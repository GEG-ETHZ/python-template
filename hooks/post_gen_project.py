"""Run new project finalization commands"""

import shutil
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Optional


def run_command(command: Sequence[str], error_msg: str, cwd: Optional[Path] = None) -> None:
    """Run a shell command, raising on failure with full context.

    Raises ``subprocess.SubprocessError`` with a descriptive multiline
    message and preserves the original exception via ``from e`` so the
    full chain is visible in tracebacks.
    """
    try:
        subprocess.run(command, check=True, capture_output=True, text=True, cwd=cwd)

    except FileNotFoundError as e:
        msg = (
            f"{error_msg}\n"
            f"  Command not found: {command[0]}\n"
            f"  Please ensure '{command[0]}' is installed and on your PATH."
        )
        raise subprocess.SubprocessError(msg) from e

    except subprocess.CalledProcessError as e:
        msg = (
            f"{error_msg}\n"
            f"  Command: {' '.join(command)}\n"
            f"  Exit code: {e.returncode}\n"
            f"  stdout: {e.output}\n"
            f"  stderr: {e.stderr}"
        )
        raise subprocess.SubprocessError(msg) from e


def init_git() -> None:
    """Initialize a git repository."""
    print("Initializing git repository...")
    run_command(["git", "init"], "Failed to initialize git repository.")


def create_initial_commit() -> None:
    """Add initial files and create the first commit."""
    print("Staging initial files...")

    # Add configuration files
    files_to_add = [
        ".gitignore",
        ".gitlab-ci.yml",
        ".pre-commit-config.yaml",
        ".python-version",
        "pyproject.toml",
        "README.md",
        "CHANGELOG.md",
        "CONTRIBUTING.md",
    ]

    for file in files_to_add:
        if Path(file).exists():
            run_command(["git", "add", file], f"Failed to stage {file}")

    # Note: uv.lock is intentionally excluded here as it's automatically
    # generated later.
    # Note: adding a directory inherently adds its contents recursively
    directories = ["data", "outputs", "scripts", "src", "tests", ".agent"]
{% if cookiecutter.repo_type == 'data_project' %}
    directories.append("pipeline")
{% endif %}
    for directory in directories:
        if Path(directory).exists():
            run_command(["git", "add", directory], f"Failed to stage directory: {directory}")

    print("Creating initial commit...")
    try:
        subprocess.run(
            ["git", "commit", "-m", "chore: initialize project from cookiecutter template"],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError:
        print(
            "WARNING: Failed to create initial commit. "
            "Please check your git user config "
            "(`git config user.name` / `user.email`)"
        )

{% if cookiecutter.repo_type == 'data_project' %}
def init_dvc() -> None:
    """Initialize DVC as a subdirectory repo inside pipeline/ and enable autostage."""
    pipeline_dir = Path("pipeline")
    print("Initializing DVC in pipeline/ ...")
    run_command(
        ["uv", "run", "dvc", "init", "--subdir"],
        "Failed to initialize DVC.",
        cwd=pipeline_dir,
    )
    run_command(
        ["uv", "run", "dvc", "config", "core.autostage", "true"],
        "Failed to configure DVC autostage.",
        cwd=pipeline_dir,
    )
    # Stage and commit the .dvc/ internals created by dvc init.
    # (.dvcignore was already staged in the initial commit.)
    if Path("pipeline/.dvc").exists():
        run_command(["git", "add", "pipeline/.dvc"], "Failed to stage pipeline/.dvc")
    run_command(
        ["git", "commit", "-m", "chore: initialize DVC in pipeline/"],
        "Failed to commit DVC initialization.",
    )
{% endif %}


def finalize_setup() -> None:
    """Run post-generation setup steps (uv sync, lock commit, hooks)."""
    print("\nRunning final project setup...")

    run_command(["uv", "sync"], "Failed to run `uv sync`.")

{% if cookiecutter.repo_type == 'data_project' %}
    init_dvc()
{% endif %}

    if Path("uv.lock").exists():
        run_command(["git", "add", "uv.lock"], "Failed to stage uv.lock.")
        run_command(["git", "commit", "-m", "chore: add uv.lock"], "Failed to create uv.lock commit.")

    run_command(["uv", "run", "pre-commit", "install"], "Failed to install pre-commit hooks.")
    run_command(
        ["uv", "run", "pre-commit", "install", "--hook-type", "pre-push"], "Failed to install pre-push hook."
    )


def cleanup_project(project_dir: Path) -> None:
    """Remove the generated project directory so the user can retry cleanly."""
    print(f"\nCleaning up generated project: {project_dir}")
    try:
        shutil.rmtree(project_dir)
        print("Project directory removed successfully.")
    except OSError as e:
        raise OSError(f"WARNING: Could not remove project directory: {e}")


if __name__ == "__main__":
    project_dir = Path.cwd().resolve()

{% if cookiecutter.repo_type != 'data_project' %}
    # Remove pipeline scaffold — only included for data_project type.
    shutil.rmtree(Path("pipeline"), ignore_errors=True)
{% endif %}

    try:
        init_git()
        create_initial_commit()
        finalize_setup()
    except subprocess.SubprocessError as e:
        print(f"\nERROR:\n{e}")
        cleanup_project(project_dir)
        sys.exit(1)

    print("\nSetup complete (dependencies synced, uv.lock committed, hooks installed).")
    print("Local project folder initialized successfully!")
    print("NEXT STEPS:")
    print(
        '    To setup a remote repository on GitLab or GitHub, see "Repository Setup" in '
        + f"    {project_dir.resolve()}/README.md"
    )
