"""Verify that cookiecutter generation produces a working project for every `repo_type`.

Run with `uv run pytest` from the repo root. Run with `uv run pytest -v` to see progress —
each variant runs a full `uv sync`, `ruff check`, `mypy`, and `pytest` cycle and can take
a minute or more.
"""

import subprocess
from pathlib import Path

import pytest
from cookiecutter.main import cookiecutter

TEMPLATE_DIR = Path(__file__).resolve().parents[1]
SUBPROCESS_TIMEOUT = 300


def _run(command: list[str], cwd: Path) -> None:
    """Run a command in `cwd`, failing the test with full output on non-zero exit."""
    result = subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=SUBPROCESS_TIMEOUT,
    )
    assert result.returncode == 0, (
        f"`{' '.join(command)}` failed in {cwd}\n"
        f"--- stdout ---\n{result.stdout}\n"
        f"--- stderr ---\n{result.stderr}"
    )


@pytest.mark.parametrize("repo_type", ["standard", "data_project"])
def test_generated_project_passes_checks(repo_type: str, tmp_path: Path) -> None:
    """Generate a project for `repo_type` and confirm lint/typecheck/test all pass."""
    project_slug = f"sandbox-{repo_type.replace('_', '-')}"

    project_dir = Path(
        cookiecutter(
            str(TEMPLATE_DIR),
            no_input=True,
            output_dir=str(tmp_path),
            extra_context={
                "project_name": project_slug,
                "author_name": "Test Author",
                "repo_type": repo_type,
            },
        )
    )

    assert (project_dir / "pyproject.toml").exists()
    assert (project_dir / "uv.lock").exists()
    assert (project_dir / "src" / project_slug.replace("-", "_") / "__init__.py").exists()
    assert (project_dir / "tests" / "test_demo.py").exists()

    if repo_type == "data_project":
        assert (project_dir / "pipeline" / "dvc.yaml").exists()
        assert (project_dir / "pipeline" / ".dvc").is_dir()
    else:
        assert not (project_dir / "pipeline").exists()

    _run(["uv", "run", "ruff", "check", "."], cwd=project_dir)
    _run(["uv", "run", "mypy", "."], cwd=project_dir)
    _run(["uv", "run", "pytest", "-v"], cwd=project_dir)
