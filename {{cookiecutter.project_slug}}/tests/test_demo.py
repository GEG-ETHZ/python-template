"""
Module containing demo test.

This module can be deleted or renamed and used for actual tests.  Run tests with `uv run pytest` in the
project root.
"""


def test_import():
    """
    Demo test that verifies that {{ cookiecutter.project_slug.replace('-', '_') }} can be imported.
    """
    import {{ cookiecutter.project_slug.replace('-', '_') }}  # noqa: F401  # type: ignore[import]

    assert {{ cookiecutter.project_slug.replace('-', '_') }}.__version__ == "0.1.0"
