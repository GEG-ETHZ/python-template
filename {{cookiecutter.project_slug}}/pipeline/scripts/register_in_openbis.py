r"""register_in_openbis.py

OPTIONAL: Registers a DVC-tracked output file in openBIS as a Dataset with
full FAIR provenance. Only needed if you are using openBIS for result
registration. See the README for the files-vs-properties design rationale.

The registered record is designed to be self-contained enough for a reviewer
to reproduce the result:

  - Git repo URL + commit hash  → find the exact code state
  - dvc.yaml                    → understand the pipeline structure (human-readable)
  - dvc.lock                    → verify outputs match inputs/scripts (machine-readable)
  - pyproject.toml              → understand declared dependencies (human-readable)
  - uv.lock                     → reproduce the exact environment (machine-readable)

Files are attached to the dataset rather than stored as properties because they
are large and machine-readable. Properties are reserved for small, human-readable
values that are useful to search and display in the openBIS UI.

Usage:
    uv add pybis   # one-time: install pybis if not already in pyproject.toml
    uv run python scripts/register_in_openbis.py \
        --file outputs/<your-result-file> \
        --experiment /GEG/{{ cookiecutter.project_slug | upper | replace("-", "_") }}/EXP-1 \
        --description "Brief description of this result"

Arguments:
    --file          DVC-tracked result file to upload
    --experiment    openBIS path: /Space/Project/Experiment (must already exist —
                    created by running openbis_setup_schema.py first)
    --description   Free-text label stored as the 'notes' property in openBIS
    --dvc-lock      Path to dvc.lock (default: dvc.lock); attached as a file
    --dvc-yaml      Path to dvc.yaml (default: dvc.yaml); attached as a file
    --uv-lock       Path to uv.lock (default: ../uv.lock); attached as a file
    --pyproject     Path to pyproject.toml (default: ../pyproject.toml); attached as a file
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
    # The DVC-tracked output file to upload as an openBIS dataset
    p.add_argument("--file", required=True, help="Path to result file to register")
    # Full openBIS path — must already exist (created by running openbis_setup_schema.py first)
    p.add_argument("--experiment", required=True, help="openBIS experiment path, e.g. /GEG/MY_PROJECT/EXP-1")
    # Stored as the built-in 'notes' field on RAW_DATA
    p.add_argument("--description", required=True, help="Human-readable description")
    # Provenance files — attached to the dataset, not stored as properties, because they
    # are large and machine-readable. A reviewer downloads them for verification/reproduction.
    p.add_argument("--dvc-lock", default="dvc.lock", help="Path to dvc.lock")
    p.add_argument("--dvc-yaml", default="dvc.yaml", help="Path to dvc.yaml")
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
    # TODO: add domain-specific arguments here, e.g.:
    # p.add_argument("--sample-id", default="", help="Sample identifier")
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


def register(args: argparse.Namespace) -> None:
    """Connect to openBIS and register the result file with full FAIR provenance."""
    try:
        import pybis  # type: ignore[import-untyped]
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

    file_path = Path(args.file)

    # pybis requires all files to share a common root directory — files from
    # different locations (e.g. pipeline/ and repo root) cause "Could not process
    # file default" on the DSS side. Stage everything into a temp directory first.
    attachment_paths = [args.dvc_lock, args.dvc_yaml, args.uv_lock, args.pyproject]
    staged_names: list[str] = []

    with tempfile.TemporaryDirectory() as staging:
        shutil.copy2(file_path.resolve(), staging)
        staged_names.append(file_path.name)

        for p in attachment_paths:
            resolved = Path(p).resolve()
            if resolved.exists():
                shutil.copy2(resolved, staging)
                staged_names.append(resolved.name)
            else:
                print(f"  Warning: {p} not found, skipping attachment")

        staged_files = [str(Path(staging) / name) for name in staged_names]

        ds = o.new_dataset(
            type="RAW_DATA",
            experiment=args.experiment,
            files=staged_files,
            props={
                "notes": args.description,
                "source_file": file_path.name,
                "git_repo_url": git_repo,
                "git_commit": git_commit,
                # TODO: add domain-specific properties here to match what you
                # defined in openbis_setup_schema.py, e.g.:
                # "sample_id": args.sample_id,
            },
        )
        ds.save()

    print("\nRegistered successfully.")
    print(f"  openBIS identifier : {ds.permId}")
    print(f"  File               : {file_path.name}")
    print(f"  Experiment         : {args.experiment}")
    print(f"  Git repo           : {git_repo or '(not detected)'}")
    print(f"  Git commit         : {git_commit or '(not detected)'}")
    print(f"  Attached files     : {', '.join(staged_names)}")
    print(f"\nPermanent reference for publications: {ds.permId}")
    o.logout()


if __name__ == "__main__":
    args = parse_args()
    register(args)
