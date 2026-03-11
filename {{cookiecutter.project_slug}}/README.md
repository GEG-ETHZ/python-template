# {{ cookiecutter.project_name }}

{{ cookiecutter.project_short_description }}


## Prerequisites
- Python version specified in `.python-version`
- uv (if not installed - see below)

### Installation
1. [install uv](https://docs.astral.sh/uv/getting-started/installation/) <!--NOTE: link to Wiki for uv--> 
2. run `uv sync` to install dependencies. Re-run whenever dependencies in `pyproject.toml` change
3. execute a script via: `uv run some_script.py`

## Repository Setup
**Note**: this section can be deleted after initial setup.  

If you just generated this project from the template, you need to connect it to a remote repository:
1. **Create the remote repository:** Create a new project in [GitLab](https://gitlab.ethz.ch/geg) (unless it is already known that the project will be released publicly via [GitHub](https://github.com/GEG-ETHZ/)).
   - *Note: If you run into permissions issues creating the repository, please contact the Software Team (e.g., Chad Baker, Anton Kulik).*
2. **Link your local repository:** Follow the [Syncing with Multiple Repos](https://gitlab.ethz.ch/geg/computing-guide/-/wikis/git#syncing-with-multiple-repos) guide to set up your git remotes.
   - *Example:* `git remote add origin git@gitlab.ethz.ch:geg/your-project.git`
   - *Then push your initial commit:* `git push -u origin main`

## Project Structure
This section should be deleted when creating a specific project from this template.
```text
└── {{ cookiecutter.project_slug }}
    ├── README.md
    ├── pyproject.toml
    ├── .gitignore
    ├── .python-version
    ├── data/        # Raw and processed data files (ignored by git by default)
    ├── outputs/     # Generated figures, reports, and models
    ├── scripts/     # Standalone Python scripts for data processing and analysis
    ├── src/         # Installable Python package source code and project-specific utilities
    │   └── {{ cookiecutter.project_slug }}
    │       └── __init__.py
    ├── tests/       # Unit and integration tests
    │   ├── __init__.py
    │   └── test_demo.py
    └── uv.lock
```

> **Note on Repository Type:** You generated a `{{ cookiecutter.repo_type }}` repository.
> This layout contains both a standardized data analysis environment (`data`, `outputs`, `scripts`, `tests`) and an installable Python library in `src/`.
{% if cookiecutter.repo_type == 'data_project' %}> As a **data_project**, your `pyproject.toml` also includes a placeholder dependency linking to a GEG Gitlab data package that you should configure.
{% endif %}> If you find you do not need the data science folders, you may safely delete them.

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
