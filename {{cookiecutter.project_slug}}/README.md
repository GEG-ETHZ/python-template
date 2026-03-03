# {{ cookiecutter.project_name }}

{{ cookiecutter.project_short_description }}


## Prerequisites
- Python version specified in `.python-version`
- uv (if not installed - see below)

### Installation
1. [install uv](https://docs.astral.sh/uv/getting-started/installation/) <!--NOTE: link to Wiki for uv--> 
2. run `uv sync` to install dependencies. Re-run whenever dependencies in `pyproject.toml` change
3. execute a script via: `uv run some_script.py`


## Project Structure
This section should be deleted when creating a specific project from this template.
```
└── {{ cookiecutter.project_slug }}
    ├── README.md
    ├── pyproject.toml
    ├── .gitignore
    ├── .python-version
    ├── src
    │   └── {{ cookiecutter.project_slug }}
    │       └── __init__.py
    ├── tests
    │   └── __init__.py
    │   └── test_demo.py
    └── uv.lock
```

**Tip:** To regenerate this tree, run:
`tree -I '__pycache__|.venv|*.egg-info|.git'`
(If tree isn't installed run: `brew install tree`)


## Branching Strategy
Explained [here](./CONTRIBUTING.md#branching-strategy).

## Running
- **Tests:** `uv run pytest`
- **Linting:** `uv run ruff check .`
- **Formatting:** `uv run ruff format .`
- **Type checking:** `uv run mypy src/`
