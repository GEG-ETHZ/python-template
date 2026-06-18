# {{ cookiecutter.project_name }}

{{ cookiecutter.project_short_description }}

> **Built on the GEG Python template.** This project entails [`uv`](https://docs.astral.sh/uv/) for dependencies and environments, [`ruff`](https://docs.astral.sh/ruff/) for linting and formatting, [`mypy`](https://mypy-lang.org/) for type checks, [`pre-commit`](https://pre-commit.com/) hooks, and a working GitLab CI pipeline. A new contributor only needs `uv sync` to be productive, and every GEG repo looks the same to reviewers. See [About](#about) for the exact generation command.
>
> **First time on a template-generated project?** Read the rest of this README end-to-end — it documents our conventions.

## Table of contents

- [Quick Start](#quick-start)
- [Getting Started](#getting-started)
- [Repository Setup](#repository-setup)
- [Project Structure](#project-structure)
{% if cookiecutter.repo_type == 'data_project' %}
- [Data Pipeline (DVC)](#data-pipeline-dvc)
{% endif %}
- [Developers](#developers)

<a id="about"></a>
<details>
<summary><strong>About</strong></summary>

This project was generated from the [GEG Python template](https://gitlab.ethz.ch/geg/templates/python-template) by running:

```bash
uvx --from cookiecutter cookiecutter git@gitlab.ethz.ch:geg/templates/python-template.git
```
</details>

## Quick Start

```bash
cd {{ cookiecutter.project_slug }}
just setup # 'just' is a modern command runner (like 'make' but works for both macOS/Linux AND Windows)
```

That is enough to install dependencies and git hooks so you can work locally.
More information: Don't have `just` → [Getting Started](#getting-started). GitLab remote and first push → [Repository Setup](#repository-setup).


<a id="getting-started"></a>
<details>
<summary><strong>Getting Started</strong></summary>

### 1. Install required tools

[**uv**](https://docs.astral.sh/uv/getting-started/installation/) — manages dependencies and your Python environment.

### 2. Install optional tools (recommended)

[**just**](https://just.systems/man/en/packages.html) — wraps the setup steps into a single `just setup` command. Without it, run the steps manually (see below).
- macOS: `brew install just`
- Linux: see [just installation docs](https://just.systems/man/en/packages.html)
- Windows: `winget install Casey.Just` or `scoop install just`

[**direnv**](https://direnv.net) *(macOS/Linux only)* — auto-activates your environment on `cd` so you never need to run `source .venv/bin/activate` manually. Without it, activate the environment yourself each session (`source .venv/bin/activate` / `.venv\Scripts\Activate.ps1`).
- Install via your package manager (`brew install direnv` / `sudo apt install direnv`)
- Add the shell hook to your rc file: `eval "$(direnv hook zsh)"` or `eval "$(direnv hook bash)"`
- See [direnv hook docs](https://direnv.net/docs/hook.html) for other shells

### 3. Run setup

**With just:**
```bash
just setup
```
Runs `uv sync`, approves `.envrc` if direnv is installed (macOS/Linux), and installs git hooks.

**Without just:**
```bash
uv sync
direnv allow .   # macOS/Linux with direnv only
uv run prek install --hook-type pre-commit --hook-type pre-push --hook-type post-checkout --overwrite
```

> **Windows note:** prek hooks run as shell scripts — [Git for Windows](https://git-scm.com/download/win) (which includes Git Bash) must be installed.

</details>

<a id="repository-setup"></a>
<details>
<summary><strong>Repository Setup</strong></summary>

**Note: One-time action. This section can be deleted after initial setup.**

If you just generated this project from the template, you need to connect it to a remote repository:
1. **Create the remote repository:** Create a new project in
   [GitLab](https://gitlab.ethz.ch/geg) (unless it is already known that the
   project will be released publicly via [GitHub](https://github.com/GEG-ETHZ/)).
   - **Uncheck "Initialize repository with a README"** — the repository must be
     empty so the local history can be pushed without conflicts.
   - *Note: If you run into permissions issues creating the repository, please
      contact the Software Team (e.g., Chad Baker, Anton Kulik).*
1. **Link your local repository:** Follow the [Syncing with Multiple Repos](https://gitlab.ethz.ch/geg/computing-guide/-/wikis/git#syncing-with-multiple-repos) guide to set up your git remotes.
   - *Example:* `git remote add origin git@gitlab.ethz.ch:geg/your-project.git`
1. **Push the initial commit immediately** — before making any deliberate commits.
   This verifies the generated baseline passes CI before you build on top of it.
   ```
   git push -u --no-verify origin main
   ```
   - `--no-verify` skips local pre-push hooks (mypy/pytest) for this push only — **do not use it again.**
   - **If branch protection blocks the push:** first request Owner role from an admin
     (e.g. Chad Baker or Anton Kulik) — this alone may resolve it. If it still blocks,
     temporarily unprotect main in GitLab → Your Project → Settings → Repository →
     Protected Branches, push, then re-enable protection.
1. **GitLab Runner:** The GEG group runner handles CI automatically — no per-project setup needed.
1. **Auto-tagging token:** The CI pipeline tags branches on merge (`bak/<branch-name>`) — this needs a one-time token.
   Create a Project Access Token under **Settings → Access Tokens → Add new token**:
   - **Token name**: `GITLAB_PUSH_TOKEN`
   - **Description**: `allows gitlab runner to tag branches`
   - **Expiration date**: leave blank (no expiration)
   - **Role**: Developer
   - **Scope**: `write_repository`

   GitLab shows the token value only once — copy it immediately and add it as a CI/CD variable under **Settings → CI/CD → Variables**:
   - **Key**: `GITLAB_PUSH_TOKEN`
   - **Value**: paste the token here
   - **Visibility**: Masked
   - **Protect variable**: unchecked (protected variables are not injected into unprotected MR branches)

</details>

## Project Structure
Layout of the generated repo.
**Note: This section should be deleted when creating a specific project from this template.**
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
{% endif %}
    └── uv.lock
```

> **Note on Repository Type:** You generated a `{{ cookiecutter.repo_type }}` repository.
> This layout contains both a standardized data analysis environment (`data`, `outputs`, `scripts`, `tests`) and an installable Python library in `src/`.
{% if cookiecutter.repo_type == 'data_project' %}> As a **data_project**, your `pyproject.toml` also includes a placeholder dependency linking to a GEG Gitlab data package that you should configure.
{% endif %}> If you find you do not need the data science folders, you may safely delete them.

**Tip:** To regenerate this tree, run:
`tree -I '__pycache__|.venv|*.egg-info|.git'`
(If tree isn't installed run: `brew install tree`)

{% if cookiecutter.repo_type == 'data_project' %}

<a id="data-pipeline-dvc"></a>
<details>
<summary><strong>Data Pipeline (DVC)</strong></summary>

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

</details>
{% endif %}

<a id="developers"></a>
<details>
<summary><strong>Developers</strong></summary>

### Branching Strategy
Explained [here](./CONTRIBUTING.md#branching-strategy).

### Running Checks
- **Tests:** `uv run pytest -v`
- **Linting:** `uv run ruff check .`
- **Formatting:** `uv run ruff format .` (use `--check` to verify without modifying)
- **Type checking:** `uv run mypy src/`
</details>
