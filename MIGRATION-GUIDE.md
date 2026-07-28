# Migration Guide

This file supports two audiences:

1. **AI tools** working on an existing project: a complete inventory of what this template provides, which files each feature touches, and how to retrofit it into a project that was not generated from the template.
2. **Developers** evaluating what to adopt selectively: a compact index of every practice baked in, with pointers to the detailed docs that live in each generated project's `CONTRIBUTING.md` and `README.md`.

Features marked **`data_project` only** are included only when `repo_type = data_project` is selected during generation.

---

## Dependency & Environment Management

### `uv` — dependency management
Manages dependencies, virtual environments, and script execution. Replaces pip, venv, and pip-tools.

**Files:** `pyproject.toml`, `uv.lock`

**To add:** Install `uv`, convert `pyproject.toml` to use `[dependency-groups]` instead of `[project.optional-dependencies]`, run `uv sync`. Replace `pip install` calls with `uv add`.

### `src/` layout + hatchling build backend
The installable package lives under `src/<slug>/` rather than the repo root. Prevents accidental imports of the development tree and is required for the package to be pip-installable.

**Files:** `src/<slug>/__init__.py`, `src/<slug>/py.typed`, `pyproject.toml` (`[build-system]`, `[tool.hatch.build]`)

**To add:** Move your package directory under `src/`, update `pyproject.toml` to use hatchling as the build backend, and add `[tool.hatch.build] sources = ["src"]`.

### `.python-version`
Pins the Python version used by `uv` and pyenv-compatible tools. Ensures the same interpreter across machines.

**Files:** `.python-version`

**To add:** Create `.python-version` containing the version string (e.g. `3.11`).

### `direnv` + `.envrc` (macOS/Linux)
Auto-runs `uv sync` and activates the venv when you `cd` into the project. Eliminates manual environment activation. The `just setup` recipe handles first-time approval. See [README.md — Getting Started]({{cookiecutter.project_slug}}/README.md#getting-started) for full setup instructions including the Windows (no-direnv) path.

**Files:** `.envrc`, `justfile` (`setup` recipe)

**To add:** Create `.envrc` containing `uv sync` and `source .venv/bin/activate`. Copy the [`justfile`](https://gitlab.ethz.ch/geg/templates/python-template/-/blob/main/{{cookiecutter.project_slug}}/justfile?ref_type=heads) from the blueprint for the full pattern including direnv shell-hook detection and Windows support. Run `direnv allow .` once.

---

## Code Quality & Tooling

### `just` — task runner
Cross-platform task runner (replaces `make`). Provides a `setup` recipe that works identically on macOS, Linux, and Windows — running `direnv allow` on Unix and skipping it gracefully on Windows. Also provides quality check recipes (`fmt`, `lint`, `typecheck`, `test`) and a composite `check` recipe that runs all four in CI order.

The same checks run across three surfaces at different moments:

| Check | `just` recipe | prek stage | CI job |
|---|---|---|---|
| ruff format | `just fmt` | pre-commit | `lint_code` |
| ruff lint | `just lint` | pre-commit | `lint_code` |
| mypy | `just typecheck` | pre-push | `mypy_check` |
| pytest | `just test` | pre-push | `pytest` |

**Files:** `justfile`

**To add:** [Install `just`](https://just.systems/man/en/packages.html) (`brew install just` on macOS, `winget install Casey.Just` or `scoop install just` on Windows). Copy the [`justfile`](https://gitlab.ethz.ch/geg/templates/python-template/-/blob/main/{{cookiecutter.project_slug}}/justfile?ref_type=heads) from the blueprint. Add `set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]` at the top for Windows compatibility.

### `ruff` — lint + format
Single tool replacing flake8, black, isort, and pyupgrade. Configured for Google-style docstrings, src layout, and a strict rule set (see `[tool.ruff]` in `pyproject.toml` for the exact selection).

**Files:** `pyproject.toml` (`[tool.ruff.*]`), `.pre-commit-config.yaml` (`ruff-check`, `ruff-format` hooks)

**To add:** `uv add --dev ruff`, copy the `[tool.ruff.*]` sections from `pyproject.toml`, add the `ruff-check` and `ruff-format` hooks to `.pre-commit-config.yaml`.

### `mypy` — strict type checking
Full strict mode (`strict = true`). Runs at pre-push (not pre-commit) to avoid slowing down commits.

**Files:** `pyproject.toml` (`[tool.mypy]`), `.pre-commit-config.yaml` (local `mypy` hook at `stages: [pre-push]`)

**To add:** `uv add --dev mypy`, copy `[tool.mypy]` from `pyproject.toml`, add the local hook entry to `.pre-commit-config.yaml`.

### `pytest`
Test suite scaffolded under `tests/`. `pyproject.toml` sets `testpaths = ["tests"]` so `uv run pytest` finds tests without needing a directory argument. Runs at pre-push alongside mypy.

**Files:** `tests/__init__.py`, `tests/test_demo.py`, `pyproject.toml` (`testpaths = ["tests"]` under `[tool.pytest.ini_options]`)

**To add:** `uv add --dev pytest`, add `[tool.pytest.ini_options]\ntestpaths = ["tests"]` to `pyproject.toml`, add the local pytest hook to `.pre-commit-config.yaml`.

---

## Git Workflow

### `prek` — git hooks
Runs hooks defined in `.pre-commit-config.yaml` at commit and push time. Reads the standard `pre-commit` config format; no config migration needed from `pre-commit`.

**Files:** `.pre-commit-config.yaml`, `pyproject.toml` (`prek` dev dep), `justfile` (`setup` recipe)

**To add:** `uv add --dev prek`, ensure `.pre-commit-config.yaml` exists, run `just setup` (all platforms).

### `no-commit-to-branch`
Blocks direct commits or pushes to `main` and `develop`, enforcing the branching strategy described in [CONTRIBUTING.md — Branching Strategy]({{cookiecutter.project_slug}}/CONTRIBUTING.md#branching-strategy).

**Files:** `.pre-commit-config.yaml` (`no-commit-to-branch` hook, `stages: [pre-commit, pre-push]`)

**To add:** Add the `no-commit-to-branch` entry to `.pre-commit-config.yaml`. Adjust the `--branch` args to match your protected branches.

### Conventional commits + gitmoji
Commit messages follow `<type>(<scope>): <emoji> <description>`. Enforced by convention, not a hook.

**Files:** None (convention only, documented in the root `CONTRIBUTING.md`)

**To add:** Adopt the convention and document it in your project's `CONTRIBUTING.md`.

### CHANGELOG (Keep a Changelog)
Structured around merge requests rather than releases. Uses a `## [In Development]` stub at the top. See [CONTRIBUTING.md — Changelog](https://unlimited.ethz.ch/spaces/GEG/pages/441418531/OPS+Code#OPS%3ACode-Changelog) for the full format, entry rules, and rationale.

**Files:** `CHANGELOG.md`

**To add:** Copy the `CHANGELOG.md` structure and adopt the MR-based entry convention documented in `CONTRIBUTING.md`.

### GitLab project settings
One-time configuration a project **Maintainer** applies after creating the repository. Covers merge rules, branch deletion, squash defaults, and branch protection. Must be done via the GitLab UI — not scripted or automated — to avoid granting agents API access to repository settings.

**Settings → General → Merge requests:**

| Setting | Value |
|---|---|
| Merge method | Merge commit |
| Squash commits | Encourage |
| ☑ Pipelines must succeed | checked |
| ☑ Delete source branch | checked |

**Settings → Repository → Protected branches:**

| Branch | Allowed to merge | Allowed to push and force push |
|---|---|---|
| `main` | Maintainers | No one |
| `develop` | Maintainers | Developers + Maintainers |

**Files:** None (UI-only configuration)

**To add:** Apply the settings above as a Maintainer once after creating the GitLab project. See [GEG Confluence Page — see GitLab project settings under Git Workflow](https://unlimited.ethz.ch/spaces/GEG/pages/441418531/OPS+Code#OPS%3ACode-GitWorkflow) for the full rationale.

---

## CI/CD

### GitLab CI pipeline
Four-stage pipeline: lint → typecheck → test → auto-tag. The `tag_branch` job creates a `bak/<branch>` tag at the end of each successful MR pipeline, preserving the branch ref before it is deleted on squash-merge (needed for `CHANGELOG.md` comparison links). Requires a `GITLAB_PUSH_TOKEN` CI variable. See [CONTRIBUTING.md — Tagging deleted branches](https://unlimited.ethz.ch/spaces/GEG/pages/441418531/OPS+Code#OPS%3ACode-Taggingdeletedbranches).

**Files:** `.gitlab-ci.yml`

**To add:** Copy `.gitlab-ci.yml`. Create a Project Access Token with `write_repository` scope and add it as `GITLAB_PUSH_TOKEN` under **Settings → CI/CD → Variables** (Masked, unprotected).

---

## AI Agent Support

### `.agent/` rules
Agent-readable rules for commit format, code quality, permissions, and file pathing. Loaded by AI assistants (e.g. Claude Code) when working in generated projects.

**Files:** `.agent/rules.md`, `.agent/rules/*.md`

**To add:** Copy the `.agent/` directory into your project root.

---

## Data Project Features

### DVC — data versioning (`data_project` only)
Initialized as a subdirectory repo inside `pipeline/` (`.dvc/` lives in `pipeline/`, not the project root). Tracks data files separately from code with `core.autostage = true`. Git hooks auto-sync DVC state on branch switch (`post-checkout`). See [README.md — Data Pipeline (DVC)]({{cookiecutter.project_slug}}/README.md#data-pipeline-dvc) for full usage, remote storage setup, and the git-vs-DVC decision guide.

**Files:** `pipeline/dvc.yaml`, `pipeline/.dvc/`, `pipeline/.dvcignore`, `.pre-commit-config.yaml` (dvc hooks), `pyproject.toml` (`dvc[webdav]` dep)

**To add:** `uv add --dev "dvc[webdav]"`, run `dvc init --subdir` from `pipeline/`, `dvc config core.autostage true`, `dvc install --use-pre-commit-tool` (writes DVC hooks into `.pre-commit-config.yaml`), then re-run `just setup` to install the updated hooks including `post-checkout`.
