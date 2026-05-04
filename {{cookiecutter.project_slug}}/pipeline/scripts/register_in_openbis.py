r"""register_in_openbis.py

NOT YET USABLE: This script requires a deployed openBIS server (GCP VM +
storage bucket). No server has been provisioned yet. Keep this script for
when server setup is complete — the logic is correct, it just needs a target.

OPTIONAL: Registers DVC pipeline outputs in openBIS with full FAIR provenance,
modelling the DVC stage graph as openBIS parent/child dataset relationships.
Only needed when publishing or archiving results in openBIS.

For each stage in dvc.yaml (processed in dependency order):
  - A RAW_DATA dataset is created containing that stage's output files.
  - Its openBIS ``parents`` are set to the datasets of the stages it depends on,
    so the provenance chain is navigable in the openBIS UI.
  - Provenance files (dvc.lock, dvc.yaml, uv.lock, pyproject.toml) are attached
    to leaf stages (stages whose outputs are not consumed by another stage).

The registered record is self-contained enough for a reviewer to reproduce:
  - Git repo URL + commit hash  → find the exact code state
  - dvc.yaml                    → understand the pipeline structure (human-readable)
  - dvc.lock                    → verify outputs match inputs/scripts (machine-readable)
  - pyproject.toml              → understand declared dependencies (human-readable)
  - uv.lock                     → reproduce the exact environment (machine-readable)

Files are attached to datasets rather than stored as properties because they are
large and machine-readable. Properties are reserved for small, human-readable
values that are useful to search and display in the openBIS UI.

Usage:
    uv add pybis   # one-time: install pybis if not already in pyproject.toml
    uv run python scripts/register_in_openbis.py \
        --experiment /GEG/{{ cookiecutter.project_slug | upper | replace("-", "_") }}/EXP-1 \
        --description "Brief description of this pipeline run"

Arguments:
    --experiment    openBIS path: /Space/Project/Experiment (must already exist —
                    created by running openbis_setup_schema.py first)
    --description   Free-text label stored as the 'notes' property on leaf datasets
    --dvc-yaml      Path to dvc.yaml (default: dvc.yaml); parsed to discover stages
    --dvc-lock      Path to dvc.lock (default: dvc.lock); attached to leaf datasets
    --uv-lock       Path to uv.lock (default: ../uv.lock); attached to leaf datasets
    --pyproject     Path to pyproject.toml (default: ../pyproject.toml); attached
                    to leaf datasets
    --git-repo      Git remote URL; auto-detected from 'origin' if omitted
    --git-commit    Git commit hash; auto-detected from HEAD if omitted
    --host          openBIS server URL (default: https://localhost.openbis.net)
    --user          openBIS username (default: admin)
    --password      Omit to use OPENBIS_PASSWORD env var or be prompted interactively

Requirements:
    uv add pybis
"""

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    p = argparse.ArgumentParser()
    # Full openBIS path — must already exist (created by running openbis_setup_schema.py first)
    p.add_argument("--experiment", required=True, help="openBIS experiment path, e.g. /GEG/MY_PROJECT/EXP-1")
    # Stored as the built-in 'notes' field on leaf RAW_DATA datasets
    p.add_argument("--description", default="", help="Human-readable description of this pipeline run")
    # dvc.yaml is parsed to discover stages, deps, and outs
    p.add_argument("--dvc-yaml", default="dvc.yaml", help="Path to dvc.yaml")
    # Provenance files — attached to leaf datasets for reproducibility. A reviewer
    # downloads them to verify or reproduce the result.
    p.add_argument("--dvc-lock", default="dvc.lock", help="Path to dvc.lock")
    # uv.lock and pyproject.toml live one level up (repo root) relative to pipeline/
    p.add_argument("--uv-lock", default="../uv.lock", help="Path to uv.lock")
    p.add_argument("--pyproject", default="../pyproject.toml", help="Path to pyproject.toml")
    # Git provenance — auto-detected but overridable (e.g. when running in CI)
    p.add_argument("--git-repo", default=None, help="Git remote URL (auto-detected from 'origin')")
    p.add_argument("--git-commit", default=None, help="Git commit hash (auto-detected from HEAD)")
    # openBIS connection
    p.add_argument("--host", default="https://localhost.openbis.net", help="openBIS server URL")
    p.add_argument("--user", default="admin")
    # Password resolution order: --password flag → OPENBIS_PASSWORD env var → interactive prompt.
    # After first login pybis saves a session token, so the password is not needed again
    # until the token expires. Never hard-code passwords in scripts or commit them.
    p.add_argument("--password", default=None, help="Prompted if not provided")
    return p.parse_args()


def detect_git_info() -> tuple[str, str]:
    """Auto-detect git remote URL and HEAD commit hash.

    openBIS HYPERLINK properties only accept http/https/ftp URLs, so SSH
    remote URLs (git@host:org/repo.git) are converted to HTTPS equivalents.
    """

    def run(cmd: list[str]) -> str:
        try:
            return subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode().strip()
        except Exception:
            return ""

    repo = run(["git", "remote", "get-url", "origin"])
    commit = run(["git", "rev-parse", "HEAD"])

    # Convert SSH remote to HTTPS: git@gitlab.ethz.ch:org/repo.git → https://gitlab.ethz.ch/org/repo
    if repo.startswith("git@"):
        repo = repo.removeprefix("git@").replace(":", "/", 1).removesuffix(".git")
        repo = f"https://{repo}"

    return repo, commit


def expand_item(obj: object, item: str) -> object:
    """Recursively replace ``${item}`` in all strings within a nested structure."""
    if isinstance(obj, str):
        return obj.replace("${item}", item)
    if isinstance(obj, dict):
        return {k: expand_item(v, item) for k, v in obj.items()}
    if isinstance(obj, list):
        return [expand_item(x, item) for x in obj]
    return obj


def parse_dvc_yaml(path: Path) -> dict[str, dict]:  # type: ignore[type-arg]
    """Return the fully-expanded stages dict from dvc.yaml.

    ``foreach`` stages (e.g. ``compute: {foreach: [a, b], do: {...}}``) are
    expanded into individual named stages (``compute@a``, ``compute@b``) with
    all ``${item}`` placeholders substituted. Non-foreach stages are passed
    through unchanged.
    """
    import yaml  # provided by pybis's PyYAML dependency

    with open(path) as f:
        raw_stages: dict[str, object] = yaml.safe_load(f).get("stages", {})

    expanded: dict[str, dict] = {}  # type: ignore[type-arg]
    for name, stage in raw_stages.items():
        if not isinstance(stage, dict):
            continue
        if "foreach" in stage:
            items = stage["foreach"]
            do: dict[str, object] = stage.get("do", {})
            for item in items:
                expanded_stage = expand_item(do, str(item))
                expanded[f"{name}@{item}"] = expanded_stage  # type: ignore[assignment]
        else:
            expanded[name] = stage
    return expanded


def normalize_paths(items: list[object]) -> list[str]:
    """Extract string paths from a list that may contain strings or dicts.

    dvc.yaml outs/deps entries can be plain strings ("outputs/result.csv") or
    dicts with options ({"outputs/result.csv": {"cache": false}}). Both forms
    are normalised to plain path strings here.
    """
    result = []
    for item in items:
        if isinstance(item, str):
            result.append(item)
        elif isinstance(item, dict):
            result.extend(str(k) for k in item)
    return result


def build_parent_map(stages: dict[str, dict]) -> dict[str, list[str]]:  # type: ignore[type-arg]
    """Map each stage name to the list of stage names it directly depends on.

    A stage B depends on stage A when any output path of A appears in the
    deps list of B — i.e., A's outputs feed B's inputs.
    """
    out_to_stage: dict[str, str] = {}
    for name, stage in stages.items():
        for out in normalize_paths(stage.get("outs", [])):
            out_to_stage[out] = name

    parent_map: dict[str, list[str]] = {}
    for name, stage in stages.items():
        parents: list[str] = []
        for dep in normalize_paths(stage.get("deps", [])):
            if dep in out_to_stage:
                producer = out_to_stage[dep]
                if producer not in parents:
                    parents.append(producer)
        parent_map[name] = parents
    return parent_map


def topo_sort(stages: dict[str, dict], parent_map: dict[str, list[str]]) -> list[str]:  # type: ignore[type-arg]
    """Return stage names in topological order (all dependencies before dependents)."""
    visited: set[str] = set()
    order: list[str] = []

    def visit(name: str) -> None:
        if name in visited:
            return
        visited.add(name)
        for parent in parent_map.get(name, []):
            visit(parent)
        order.append(name)

    for name in stages:
        visit(name)
    return order


def find_leaf_stages(parent_map: dict[str, list[str]]) -> set[str]:
    """Return the set of stages that no other stage depends on (pipeline outputs)."""
    all_parents: set[str] = set()
    for parents in parent_map.values():
        all_parents.update(parents)
    return set(parent_map.keys()) - all_parents


def collect_staged_files(
    output_paths: list[str],
    is_leaf: bool,
    provenance_paths: list[Path],
    staging: str,
) -> list[str]:
    """Copy stage outputs (and provenance files for leaf stages) into staging dir.

    Returns the list of file names that were successfully staged.
    """
    staged_names: list[str] = []
    for out_path in output_paths:
        resolved = Path(out_path).resolve()
        if resolved.exists():
            shutil.copy2(resolved, staging)
            staged_names.append(resolved.name)
        else:
            print(f"  Warning: output '{out_path}' not found, skipping")
    if is_leaf:
        for prov_path in provenance_paths:
            resolved = prov_path.resolve()
            if resolved.exists():
                shutil.copy2(resolved, staging)
                staged_names.append(resolved.name)
            else:
                print(f"  Warning: provenance file '{prov_path}' not found, skipping")
    return staged_names


def build_dataset_props(
    stage_name: str,
    is_leaf: bool,
    parent_permids: list[str],
    git_repo: str,
    git_commit: str,
    description: str,
) -> dict[str, str]:
    """Assemble the openBIS property dict for a stage dataset.

    TODO: add domain-specific properties as keyword arguments to match
    whatever extra properties you defined in openbis_setup_schema.py.
    """
    props: dict[str, str] = {
        "notes": stage_name,
        "git_repo_url": git_repo,
        "git_commit": git_commit,
        "stage_name": stage_name,
    }
    if is_leaf and description:
        props["notes"] = f"{stage_name} — {description}"
    if parent_permids:
        props["parent_permids"] = ", ".join(parent_permids)
    return props


def register(args: argparse.Namespace) -> None:
    """Connect to openBIS and register all DVC pipeline stages with provenance."""
    try:
        import pybis  # type: ignore[import-not-found, import-untyped]
    except ImportError:
        print("pybis not installed. Run: uv add pybis")
        sys.exit(1)

    import getpass
    import os

    password = (
        args.password
        or os.environ.get("OPENBIS_PASSWORD")
        or getpass.getpass(f"openBIS password for {args.user}: ")
    )

    print(f"Connecting to {args.host} ...")
    o = pybis.Openbis(args.host, verify_certificates=False)
    o.login(args.user, password, save_token=True)
    print("Connected.")

    git_repo = args.git_repo
    git_commit = args.git_commit
    if not git_repo or not git_commit:
        detected_repo, detected_commit = detect_git_info()
        git_repo = git_repo or detected_repo
        git_commit = git_commit or detected_commit

    # Parse the DVC pipeline graph
    dvc_yaml_path = Path(args.dvc_yaml)
    stages = parse_dvc_yaml(dvc_yaml_path)
    if not stages:
        print("No stages found in dvc.yaml — nothing to register.")
        sys.exit(0)

    parent_map = build_parent_map(stages)
    sorted_stages = topo_sort(stages, parent_map)
    leaf_stages = find_leaf_stages(parent_map)

    print(f"\nDVC pipeline: {len(stages)} stage(s), processing in dependency order")
    print(f"  Stages : {' → '.join(sorted_stages)}")
    print(f"  Leaves : {', '.join(sorted(leaf_stages))}\n")

    # Provenance files attached to leaf datasets for full reproducibility
    provenance_paths = [
        dvc_yaml_path,
        Path(args.dvc_lock),
        Path(args.uv_lock),
        Path(args.pyproject),
    ]

    # stage_name → openBIS permId, populated as we create each dataset
    stage_to_permid: dict[str, str] = {}

    for stage_name in sorted_stages:
        stage = stages[stage_name]
        output_paths = normalize_paths(stage.get("outs", []))
        parent_permids = [stage_to_permid[p] for p in parent_map[stage_name] if p in stage_to_permid]
        is_leaf = stage_name in leaf_stages

        # pybis requires all files to share a common root directory — stage everything
        # into a temp directory to avoid "Could not process file default" on DSS.
        with tempfile.TemporaryDirectory() as staging:
            staged_names = collect_staged_files(output_paths, is_leaf, provenance_paths, staging)
            if not staged_names:
                print(f"Stage '{stage_name}': no files to upload, skipping")
                continue

            staged_files = [str(Path(staging) / name) for name in staged_names]
            props = build_dataset_props(
                stage_name, is_leaf, parent_permids, git_repo, git_commit, args.description,
            )
            # pybis 1.37.x raises if parents=None is passed; omit the kwarg entirely
            # for root stages and only include it when there are actual parent permIds.
            ds = o.new_dataset(
                type="RAW_DATA",
                experiment=args.experiment,
                files=staged_files,
                props=props,
                **({"parents": parent_permids} if parent_permids else {}),
            )
            ds.save()
            stage_to_permid[stage_name] = ds.permId

            parent_label = f" (parents: {', '.join(parent_permids)})" if parent_permids else ""
            print(f"  Registered '{stage_name}'{parent_label}")
            print(f"    permId     : {ds.permId}")
            print(f"    Files      : {', '.join(staged_names)}")

    # Second pass: wire native openBIS children relationships so they appear as
    # clickable links in the dataset hierarchy view (same as the built-in Parents column).
    # Metadata-only update — goes to AS, not DSS.
    for stage_name, permid in stage_to_permid.items():
        child_permids = [stage_to_permid[s] for s in stage_to_permid
                         if stage_name in parent_map.get(s, [])]
        if child_permids:
            ds = o.get_dataset(permid)
            ds.children = child_permids
            ds.save()
            print(f"  {stage_name}: children → {', '.join(child_permids)}")

    print("\nRegistration complete.")
    print(f"  Experiment : {args.experiment}")
    print(f"  Git repo   : {git_repo or '(not detected)'}")
    print(f"  Git commit : {git_commit or '(not detected)'}")
    print(f"\nDataset permIds (cite in publications):")
    for stage_name, permid in stage_to_permid.items():
        print(f"  {stage_name:<20} {permid}")
    o.logout()


if __name__ == "__main__":
    args = parse_args()
    register(args)
