"""openbis_setup_schema.py

OPTIONAL: One-time setup of the openBIS metadata schema for this project.
Only needed if you are registering results in openBIS. See the README for
the files-vs-properties design rationale.

Run once after openBIS starts up, and again after any schema changes — all
operations are idempotent (safe to re-run; existing objects are skipped).

Creates:
  - Space:       GEG  (institutional space — change if your group uses a different code)
  - Project:     {{ cookiecutter.project_slug | upper | replace("-", "_") }}
  - Experiment:  {{ cookiecutter.project_slug | upper | replace("-", "_") }}/EXP-1
  - Property types assigned to RAW_DATA datasets:
      SOURCE_FILE   — original result filename
      GIT_REPO_URL  — URL of the git repository (HYPERLINK, clickable in UI)
      GIT_COMMIT    — exact git commit hash pinning the code state
      + any domain-specific properties you add below (see TODO)

Usage:
    uv add pybis   # one-time: install pybis if not already in pyproject.toml
    uv run python scripts/openbis_setup_schema.py

Prerequisites:
    openBIS must be running. For local development, start it with:
        cd openbis && docker compose up -d
    Then poll until ready:
        until docker exec openbis-app curl -so /dev/null -w '%{http_code}' http://localhost:8080/openbis/webapp/eln-lims/version.txt 2>/dev/null | grep -q 200; do echo $(date +%H:%M:%S) still starting...; sleep 20; done && echo Ready!
"""

import argparse
import sys


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    p = argparse.ArgumentParser()
    p.add_argument("--host", default="https://localhost.openbis.net")
    p.add_argument("--user", default="admin")
    p.add_argument("--password", default=None)
    return p.parse_args()


def clean_error(e: Exception) -> str:
    """Strip the raw JSON request body that pybis appends to error messages."""
    msg = str(e)
    return msg.split("\n{")[0].strip()


def setup(args: argparse.Namespace) -> None:
    """Create the openBIS space, project, experiment, and property types."""
    try:
        import pybis  # type: ignore[import-untyped]
    except ImportError:
        print("pybis not installed. Run: uv add pybis")
        sys.exit(1)

    import getpass
    import os

    # Password resolution order:
    #   1. --password flag (avoid in scripts; prefer env var or prompt)
    #   2. OPENBIS_PASSWORD environment variable (set in .zshrc or a gitignored .env)
    #   3. Interactive prompt (safest default — never stored in shell history)
    # After first login, pybis saves a session token so the password is not
    # needed again until the token expires.
    password = (
        args.password
        or os.environ.get("OPENBIS_PASSWORD")
        or getpass.getpass(f"openBIS password for {args.user}: ")
    )

    o = pybis.Openbis(args.host, verify_certificates=False)
    o.login(args.user, password, save_token=True)
    print("Connected to openBIS.")

    # --- Space ---
    # TODO: change "GEG" to your group's institutional space code if different
    space_code = "GEG"
    try:
        space = o.new_space(code=space_code, description="Geothermal Energy Group")
        space.save()
        print(f"Created space: {space_code}")
    except Exception as e:
        print(f"Space {space_code} already exists or error: {clean_error(e)}")

    # --- Project ---
    project_code = "{{ cookiecutter.project_slug | upper | replace('-', '_') }}"
    try:
        proj = o.new_project(
            space=space_code,
            code=project_code,
            description="{{ cookiecutter.project_short_description }}",
        )
        proj.save()
        print(f"Created project: {space_code}/{project_code}")
    except Exception as e:
        print(f"Project already exists or error: {clean_error(e)}")

    # --- Experiment ---
    # TODO: change "EXP-1" or add more experiments to match your study design
    experiment_code = "EXP-1"
    try:
        exp = o.new_experiment(
            type="UNKNOWN",
            project=f"/{space_code}/{project_code}",
            code=experiment_code,
        )
        exp.save()
        print(f"Created experiment: /{space_code}/{project_code}/{experiment_code}")
    except Exception as e:
        print(f"Experiment already exists or error: {clean_error(e)}")

    # --- Property types ---
    # HYPERLINK renders as a clickable link in the openBIS UI — used for git repo URL.
    # VARCHAR is plain text — used for all other string properties.
    #
    # Properties are for small, human-readable, searchable values. Large files
    # (dvc.lock, dvc.yaml, uv.lock, pyproject.toml) are attached as dataset
    # files by register_in_openbis.py — not stored as properties — so they
    # are downloadable without cluttering the UI.
    #
    # SOURCE_FILE, GIT_REPO_URL, and GIT_COMMIT are universal across projects.
    # TODO: add domain-specific properties below (e.g. sample ID, instrument,
    # selected scenario) following the same pattern, then add them to the
    # registration call in register_in_openbis.py.
    prop_defs = [
        ("SOURCE_FILE",  "VARCHAR",   "Original result filename"),
        ("GIT_REPO_URL", "HYPERLINK", "Git repository URL"),
        ("GIT_COMMIT",   "VARCHAR",   "Git commit hash pinning the exact code state"),
        # TODO: add project-specific properties here, e.g.:
        # ("SAMPLE_ID",   "VARCHAR",   "Sample identifier"),
        # ("ANALYST",     "VARCHAR",   "Analyst who performed the review step"),
    ]
    for code, dtype, label in prop_defs:
        try:
            pt = o.new_property_type(code=code, label=label, description=label, dataType=dtype)
            pt.save()
            print(f"Created property type: {code}")
        except Exception as e:
            print(f"Property type {code} already exists or error: {clean_error(e)}")

    # --- Assign custom properties to RAW_DATA dataset type ---
    # Property types must be explicitly assigned to an entity type before they
    # can be set on instances of that type.
    try:
        raw_data_type = o.get_dataset_type("RAW_DATA")
        existing = {a.code for a in raw_data_type.get_property_assignments()}
        for code, _, _ in prop_defs:
            if code not in existing:
                raw_data_type.assign_property(code)
                print(f"Assigned {code} to RAW_DATA")
            else:
                print(f"{code} already assigned to RAW_DATA")
    except Exception as e:
        print(f"Error assigning properties to RAW_DATA: {clean_error(e)}")

    print("\nSchema setup complete.")
    print("openBIS is ready for use.")
    o.logout()


if __name__ == "__main__":
    args = parse_args()
    setup(args)
