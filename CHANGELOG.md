# Changelog

All notable changes to this Cookiecutter template are documented here.
This project does not yet follow [Semantic Versioning](https://semver.org/) — everything is
pre-release. Once the first stable release (`1.0.0`) is cut, the project will adopt SemVer strictly.

---

## [In Development] — `fix/openBIS-cleanup`

### Changed

- **openBIS scripts marked not-yet-usable** — `register_in_openbis.py` and `openbis_setup_schema.py`
  now carry a prominent `NOT YET USABLE` banner. Both scripts are correct; they require a deployed
  GCP-hosted openBIS server (VM + storage bucket) which has not yet been provisioned.
- **Removed self-hosted docker-compose** — `openbis/docker-compose.yml` dropped from the
  `data_project` blueprint. Self-hosting openBIS locally was never the real deployment model;
  openBIS enters the workflow at publication time, not during day-to-day analysis.
- **README callout** — "Registering results in openBIS" section now opens with a `> Not yet usable`
  blockquote explaining the server dependency.
- **CLAUDE.md trimmed** — openBIS section rewritten: Docker/version-pinning notes removed, design
  rationale and `~/.pybis/` stale-token gotcha retained.
- **Ruff C901 compliance** — `register_in_openbis.py` helpers extracted as module-level functions to
  bring cyclomatic complexity within limits. `_` prefix convention removed from all helpers (no
  enforcement value in scripts).
- **Agent naming rules** — `.agent/rules/code-quality.md` extended with a Python section documenting
  `_` vs `__` naming rationale.

---

## [2026-04-09] — DAG-aware openBIS registration

### Added

- **`register_in_openbis.py`** — full rewrite: parses `dvc.yaml` (including `foreach` expansion),
  topologically sorts stages, creates one `RAW_DATA` dataset per stage, and wires `parents=` from the
  DVC dependency graph so the provenance chain is navigable in the openBIS UI. `foreach` stages expand
  to `name@item` datasets with `SCENARIO_ID` auto-extracted from the stage name. Provenance files
  (`dvc.lock`, `dvc.yaml`, `uv.lock`, `pyproject.toml`) attached to leaf stages only.

### Changed

- **`openbis_setup_schema.py`** — `SOURCE_FILE` property replaced by `STAGE_NAME`; update-on-exists
  logic added for property labels.
- **`docker-compose.yml`** — upgraded openBIS image to `6.8.1` (native arm64; `platform: linux/amd64`
  override removed).

---

## [2026-04-08] — openBIS scaffolding for `data_project`

### Added

- **openBIS integration** (optional, `data_project` only):
  - `openbis/docker-compose.yml` — 3-container stack (PostgreSQL, openBIS app, HAProxy TLS ingress).
  - `pipeline/scripts/register_in_openbis.py` — registers pipeline outputs as `RAW_DATA` datasets
    with git provenance properties.
  - `pipeline/scripts/openbis_setup_schema.py` — idempotent one-time schema setup (space, project,
    experiment, property types).
- **README section** — "Registering results in openBIS" documents the properties-vs-files design
  pattern and the four reproducibility questions.

---

## [2026-04-07] — DVC docs

### Changed

- **README** — documented the DVC `deps` gotcha (paths must be relative to `dvc.yaml`, not the
  script's working directory).

---

## [2026-04-02] — DVC with remote

### Added

- **DVC remote configuration** — `data_project` blueprint pre-configured for a DVC remote; `.dvc/config`
  and remote setup instructions included.

### Changed

- **README** — DVC pipeline section expanded with remote setup and `dvc push`/`dvc pull` workflow.

---

## [2026-04-01] — DVC pipeline support

### Added

- **DVC pipeline scaffolding** (`data_project` only) — `dvc.yaml`, `params.yaml`, example stage
  script, and `data/`/`outputs/` directory structure with appropriate `.gitignore` entries.
- **README DVC section** — explains pipeline structure, running stages, and reproducing results.

---

## [2026-03-31] — CI auto-tagging

### Added

- **Auto-tagging CI job** — `.gitlab-ci.yml` pipeline step tags `main` automatically on MR merge,
  enabling release tracking without manual tagging.

---

## [2026-03-17] — `data_project` repo type & mypy fixes

### Added

- **`repo_type` cookiecutter variable** — `standard` | `data_project` choice; `data_project` enables
  the DVC/openBIS scaffolding and a commented-out placeholder git dependency in `pyproject.toml`.

### Fixed

- **`src/` package naming** — hyphen-to-underscore correction so the generated package is importable.
- **Duplicate code block** removed from blueprint `pyproject.toml`.
- **`data/` and `outputs/` tracked** in the initial generated commit (previously gitignored too
  aggressively, leaving the folders absent after generation).

---

## [2026-03-13] — GitLab CI pipeline & automated post-generation

### Added

- **`.gitlab-ci.yml` template** — lint → typecheck → test pipeline with `laptop` runner tag.
- **`CONTRIBUTING.md`** — branching strategy and pre-commit vs pre-push rationale documented.

### Changed

- **`hooks/post_gen_project.py`** — `finalize_setup` now runs automatically after generation (no
  manual step required); raises with full tracebacks on failure.

---

## [Earlier] — pre-commit hooks, agent rules, initial template

### Added

- **Pre-commit hook strategy** — split by stage: `pre-commit` (ruff lint + format), `pre-push`
  (mypy + pytest). Mirrors root and blueprint configurations.
- **`.agent/rules/`** — AI agent conventions for projects generated from this template.
- **Initial template** — src layout, hatchling build backend, pytest, mypy strict, ruff, uv.

---

<!-- Version comparison links — verify and update when cutting a release -->
[Unreleased]: https://gitlab.ethz.ch/geg/templates/python-template/-/commits/main
