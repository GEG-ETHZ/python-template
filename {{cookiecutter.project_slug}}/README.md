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

The `pipeline/` directory is managed with [DVC](https://dvc.org). DVC was initialised as a subdirectory repo (`.dvc/` lives inside `pipeline/`, not the project root). As part of project setup, `dvc install` was run to install git hooks that automatically sync DVC-tracked files when you switch branches or pull — so `dvc checkout` runs automatically after `git checkout` and `git merge`.

**One-time shell setup** — enable tab completion for DVC commands (run once per machine, not per project):
```bash
# zsh: save to a completion file on fpath (do NOT inline into .zshrc)
mkdir -p ~/.zsh/completions
uv run dvc completion -s zsh > ~/.zsh/completions/_dvc
# then add this line to .zshrc, before compinit:
#   fpath=(~/.zsh/completions $fpath)

# bash:
uv run dvc completion -s bash >> ~/.bashrc
```

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

> **Gotcha — large input deps are not automatically push/pull-able.** Listing a file as a `dep` in `dvc.yaml` tells DVC to watch it for staleness but does not add it to the DVC cache. If the file is small enough to commit, just track it in git as normal. If it's too large for git (gitignored), run `dvc add <file>` to create a `.dvc` pointer file — only then will it be cached and available via `dvc push`/`dvc pull`.

### Decision guide: git, DVC, or neither?

| File type | Track with | Notes |
|---|---|---|
| Scripts, config, `dvc.yaml`, `dvc.lock` | git | Always. Text files with meaningful diffs. |
| `*.dvc` pointer files | git | Always. These are small metadata files — they must be committed so collaborators can `dvc pull`. They are **not** auto-staged unless `core.autostage = true` is set. |
| Small input files (< ~1 MB) | git | Simpler than DVC; diffs are readable. |
| Large input files (gitignored) | DVC via `dvc add` | Creates a `.dvc` pointer; file becomes push/pull-able. |
| Pipeline outputs (`outs` in `dvc.yaml`) | DVC automatically | DVC caches after every `dvc repro`. No `dvc add` needed. |
| Large outputs, cheap to reproduce | DVC, `cache: false` | DVC tracks for staleness via `dvc.lock` but skips caching — saves cache space when re-running is fast. |
| Temporary intermediate files | Neither | Gitignore them and **actively clean them up**. Stale intermediates can cause hard-to-debug pipeline inconsistencies, and solver scratch files can be very large — accumulating them risks exhausting HPC storage quotas (which can freeze your account) or incurring significant storage costs. Add a dedicated `clean` stage in `dvc.yaml` that deletes them after the pipeline completes. |

> **Warning:** never `git add` and `dvc add` the same file. `dvc add` will gitignore the file, but if it was already staged in git the result is inconsistent. If this happens, run `git rm --cached <file>` to remove it from git's index, then let DVC manage it.

### Sharing data: DVC remote storage

`git push` does **not** push DVC-tracked data files — those live in `.dvc/cache/` locally. To share data with collaborators, configure a remote and push.

**Option A — Polybox (WebDAV, currently recommended):**

Polybox is ETH Zurich's ownCloud instance and is verified to work as a DVC remote. Each user has 50 GB of storage — sufficient for moderate datasets, but be disciplined about what you track: large binary files or frequent re-versioning of complex outputs will fill the quota quickly. Plan to migrate to a dedicated group storage solution (e.g. a group server or S3-compatible store) as data volumes grow.

```bash
# one-time: create a folder in Polybox via the web UI, e.g. dvc-store/<your-project>
# then install the WebDAV plugin for DVC:
uv add --dev dvc-webdav

# one-time setup (from pipeline/)
uv run dvc remote add -d polybox webdavs://polybox.ethz.ch/remote.php/webdav/dvc-store/<your-project>
uv run dvc remote modify polybox user <your-eth-username>

# store password locally only (never committed — goes into .dvc/config.local)
# get an app password from Polybox → Account → Devices & sessions → Create new app password
uv run dvc remote modify --local polybox password <your-app-password>

# push data after a run
uv run dvc push

# collaborators clone the repo, run uv sync, then set their own --local password and pull
uv run dvc pull
```

> The `dvc remote add` and `dvc remote modify` (without `--local`) commands write to `pipeline/.dvc/config` — commit that file so everyone on the team picks up the remote URL and username automatically. Each collaborator only needs to set their own `--local` password.

**Option B — mounted filesystem (NAS, network share):** *(untested — no verified working example yet)*

```bash
# one-time: create the store directory on the shared volume
mkdir -p /Volumes/<share>/<your-path>/dvc-store

# one-time setup (from pipeline/)
uv run dvc remote add -d nas /Volumes/<share>/<your-path>/dvc-store

# push data after a run
uv run dvc push

# collaborators fetch data after cloning and uv sync
uv run dvc pull
```

**Option C — SSH remote:** *(untested — no verified working example yet)*

```bash
uv run dvc remote add -d myremote ssh://<host>/path/to/dvc-store
uv run dvc remote modify myremote user <username>
```

Without a remote, collaborators can still reproduce all outputs from scratch by running `dvc repro`, provided they have (or can generate) the raw input data.

### Cleaning temporary files

Real solvers and processing tools often write large volumes of scratch data during a run — per-timestep checkpoints, solver logs, restart files. These should never be tracked by DVC or git, and should be actively cleaned up after the pipeline no longer needs them. Stale intermediates can cause hard-to-debug inconsistencies.

**When to use this pattern:** only when an external executable (a solver, licensed FEM/CFD tool, or CLI binary) writes scratch files to a fixed location that Python cannot intercept. If your stage is pure Python, use `tempfile.TemporaryDirectory()` as a context manager instead — it cleans up automatically, even on crash, with no DVC stage required.

**Pattern: add a `clean` stage to `dvc.yaml`** that depends on the final downstream output (so it only runs after the pipeline completes successfully) and runs a script that removes the temp directories:

```yaml
clean:
  cmd: python scripts/clean.py
  deps:
    - scripts/clean.py
    - outputs/final_result.yaml   # depend on the last stage's output
  # no outs — pure side-effect stage
  # DVC considers this stale whenever the dep changes, so cleanup is automatic
```

```python
# scripts/clean.py
import shutil
from pathlib import Path

for tmp_dir in [Path("outputs/tmp")]:
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
        print(f"Removed: {tmp_dir}")
```

Make sure the temp directories are gitignored. Because `outputs/` is already gitignored by default in the pipeline `.gitignore`, subdirectories like `outputs/tmp/` are covered automatically.

### Registering results in openBIS

When a result is ready to share or cite, register it in openBIS using `scripts/register_in_openbis.py` (see the GEG openBIS + DVC demo for a worked example). The registration attaches full provenance so any future reviewer can answer the four reproduction questions:

1. *Where is the code?* → `git_repo_url` property + `git_commit` property
2. *What did the pipeline do?* → `dvc.yaml` attached as a file
3. *Did the outputs match the inputs?* → `dvc.lock` attached as a file
4. *Can I reproduce the environment?* → `pyproject.toml` + `uv.lock` attached as files

#### Properties vs. attached files

An openBIS dataset record has two places to store information. Use them differently:

**Properties** — small, human-readable, searchable values displayed in the UI:
- `notes` — free-text description of the result
- `source_file` — name of the primary result file
- `git_repo_url` (HYPERLINK) — clickable link to the code repository
- `git_commit` — exact commit hash pinning the code state
- Any domain-specific identifiers (scenario, analyst, sample ID, etc.)

**Attached files** — large or machine-readable artifacts a reviewer downloads:
- The result file itself — the artifact the record is *about*
- `dvc.lock` — machine-readable bill of materials (every input/output hash)
- `dvc.yaml` — human-readable pipeline structure
- `pyproject.toml` — declared dependencies (human-readable intent)
- `uv.lock` — fully pinned environment for reproduction

**The rule:** never store a large machine-readable blob as a property — it makes the UI unusable. If it belongs in the record but a human wouldn't read it in a browser, attach it as a file.

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
