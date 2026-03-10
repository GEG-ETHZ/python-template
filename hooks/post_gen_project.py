import os
import subprocess
import sys


def run_command(command, error_msg):
    """Run a shell command and exit if it fails."""
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: {error_msg}")
        print(f"Command output: {e.output}")
        print(f"Command stderr: {e.stderr}")
        sys.exit(1)


def init_git():
    """Initialize a git repository."""
    print("Initializing git repository...")
    run_command(["git", "init"], "Failed to initialize git repository.")


def create_initial_commit():
    """Add initial files and create the first commit."""
    print("Staging initial files...")
    
    # Add configuration files
    files_to_add = [
        ".gitignore",
        ".pre-commit-config.yaml",
        ".python-version",
        "pyproject.toml",
        "README.md",
        "CHANGELOG.md",
        "CONTRIBUTING.md"
    ]
    
    for file in files_to_add:
        if os.path.exists(file):
            run_command(["git", "add", file], f"Failed to stage {file}")
            
    # Add source code and tests directories
    # Note: adding a directory inherently adds its contents recursively
    for directory in ["src", "tests"]:
        if os.path.exists(directory):
            run_command(["git", "add", directory], f"Failed to stage directory: {directory}")

    # Note: uv.lock is intentionally excluded here as it's typically generated later 
    # when the user runs `uv sync` on their newly generated template. Wait for them
    # to run uv sync first.

    print("Creating initial commit...")
    # Using a simple message, but allowing it to fail gracefully if no git user configured
    try:
        subprocess.run(
            ["git", "commit", "-m", "chore: initialize project from cookiecutter template"], 
            check=True, 
            capture_output=True, 
            text=True
        )
    except subprocess.CalledProcessError:
        print("WARNING: Failed to create initial commit. Please check your git user config (`git config user.name`/`user.email`)")
        # Don't exit 1 here, let the generation succeed even if they haven't set up git globally


if __name__ == "__main__":
    # Cookiecutter runs these hook scripts inside the generated project directory
    init_git()
    create_initial_commit()
    print("\nProject initialized successfully!")
    print("Next steps:")
    print("Run:")
    print("  ```")
    print("  cd {{ cookiecutter.project_slug }}")
    print("  uv sync # install dependencies and generate the lockfile")
    print("  git add uv.lock && git commit -m \"chore: add uv.lock\"")
    print("  uv run pre-commit install && uv run pre-commit install --hook-type pre-push # set up git hooks")
    print("  ```")
