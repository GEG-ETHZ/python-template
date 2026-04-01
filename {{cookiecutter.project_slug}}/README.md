# {{ cookiecutter.project_name }}

{{ cookiecutter.project_short_description }}


## Prerequisites
- Python version specified in `.python-version`
- uv (if not installed - see below)

### Installation
1. [install uv](https://docs.astral.sh/uv/getting-started/installation/) <!--NOTE: link to Wiki for uv-->
1. run `uv sync` to install dependencies. Re-run whenever dependencies in `pyproject.toml` change
1. execute a script via: `uv run some_script.py`

## Repository Setup
**Note**: this section can be deleted after initial setup.

If you just generated this project from the template, you need to connect it to a remote repository:
1. **Create the remote repository:** Create a new project in
   [GitLab](https://gitlab.ethz.ch/geg) (unless it is already known that the
   project will be released publicly via [GitHub](https://github.com/GEG-ETHZ/)).
   - *Note: If you run into permissions issues creating the repository, please
      contact the Software Team (e.g., Chad Baker, Anton Kulik).*
1. **Link your local repository:** Follow the [Syncing with Multiple
   Repos](https://gitlab.ethz.ch/geg/computing-guide/-/wikis/git#syncing-with-multi
   ple-repos) guide to set up your git remotes.
   - *Example:* `git remote add origin git@gitlab.ethz.ch:geg/your-project.git`
   - *Then push your initial commit:* `git push -u --no-verify origin main`
      -- you will need to use `--no-verify` for the first push because `main` is
      protected.  After that, **DO NOT** use `--no-verify`.
1. **Set up a GitLab Runner:** If you have not previously done so,
   [set up a GitLab runner](https://gitlab.ethz.ch/geg/computing-guide/-/wikis/git#setting-up-a-gitlab-runner-on-user-laptop)

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
{% if cookiecutter.repo_type == 'data_project' %}    ├── pipeline/    # DVC-managed data pipeline
    │   ├── dvc.yaml         # pipeline stage definitions
    │   ├── dvc.lock         # exact hashes of inputs/outputs at last run (commit this)
    │   ├── config/          # parameter files tracked as DVC dependencies
    │   ├── data/raw/        # input data (DVC-tracked, gitignored)
    │   ├── outputs/         # generated outputs (DVC-tracked, gitignored)
    │   └── scripts/         # pipeline stage scripts
{% endif %}    └── uv.lock
```

> **Note on Repository Type:** You generated a `{{ cookiecutter.repo_type }}` repository.
> This layout contains both a standardized data analysis environment (`data`, `outputs`, `scripts`, `tests`) and an installable Python library in `src/`.
{% if cookiecutter.repo_type == 'data_project' %}> As a **data_project**, your `pyproject.toml` also includes a placeholder dependency linking to a GEG Gitlab data package that you should configure.
{% endif %}> If you find you do not need the data science folders, you may safely delete them.

**Tip:** To regenerate this tree, run:
`tree -I '__pycache__|.venv|*.egg-info|.git'`
(If tree isn't installed run: `brew install tree`)

{% if cookiecutter.repo_type == 'data_project' %}
## Data Pipeline (DVC)

The `pipeline/` directory is managed with [DVC](https://dvc.org). DVC was initialised as a subdirectory repo (`.dvc/` lives inside `pipeline/`, not the project root).

> **Working directory:** all DVC commands and pipeline scripts must be run from `pipeline/`, where `dvc.yaml` lives.

```bash
cd pipeline
uv run dvc repro       # run (or re-run) all pipeline stages
uv run dvc status      # check whether any output is stale relative to current inputs
uv run dvc dag         # visualise the dependency graph
```

### What goes where: git vs. DVC

| Content                           | Tracked by         | Why                                                                         |
|-----------------------------------|--------------------|-----------------------------------------------------------------------------|
| Scripts, config, `dvc.yaml`       | git                | Line-by-line history; diffs show exactly what changed                       |
| `dvc.lock`, `*.dvc` pointer files | git                | Lightweight metadata linking git history to data history                    |
| `pyproject.toml`, `uv.lock`       | git                | Fully reproducible environment — `uv sync` gives everyone the same packages |
| Raw input data, generated outputs | DVC cache + remote | Content-addressed storage; keeps git history clean                          |

`dvc.lock` is a **bill of materials** for a pipeline run — it records the exact hash of every input, script, config value, and output. Committing it to git means any historical result can be reproduced or verified.

### Sharing data: DVC remote storage

`git push` does **not** push DVC-tracked data files — those live in `.dvc/cache/` locally. To share data with collaborators, configure a remote and push:

```bash
# one-time setup (from pipeline/)
uv run dvc remote add -d myremote ssh://nas.example.com/path/to/dvc-store
uv run dvc remote modify myremote user <username>

# push data after a run
uv run dvc push

# collaborators fetch data after cloning and uv sync
uv run dvc pull
```

Without a remote, collaborators can still reproduce all outputs from scratch by running `dvc repro`, provided they have (or can generate) the raw input data.

### Reproducing a past result

```bash
git checkout <commit>   # restore scripts, config, and dvc.lock to that point in history
uv run dvc checkout     # restore DVC-tracked data files to match
uv run dvc status       # confirm everything is consistent
```

{% endif %}
## Developers
### Branching Strategy
Explained [here](./CONTRIBUTING.md#branching-strategy).

### Running Checks
- **Tests:** `uv run pytest -v`
- **Linting:** `uv run ruff check .`
- **Formatting:** `uv run ruff format .` (use `--check` to verify without modifying)
- **Type checking:** `uv run mypy src/`
