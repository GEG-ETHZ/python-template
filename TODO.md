# Week of 2026-05-11
- [x] tweak cookiecutter generated README.md to have:
    - [x] some sort of exec summary explaining what and why
    - [x] quickstart TOC
    - [x] make most of the top level headings collapsible and collapsed by default
- [x] make sure that if a person gets a new computer and clones a
    cookikecutter-created repo that the docs explain how to re-init everything
    (perhaps with a script) -- solved by [MR 42](https://gitlab.ethz.ch/geg/templates/python-template/-/merge_requests/42)
- [x] make sure that there's a clearly defined set of features in the
    cookiecutter template to help an AI tool and/or user migrate cookiecutter
    features to an existing project -- solved by [MR 42](https://gitlab.ethz.ch/geg/templates/python-template/-/merge_requests/42)
- [ ] Migrate most of the content of [the "OPS: Code" Confluence
    Page](https://unlimited.ethz.ch/spaces/GEG/pages/441418531/OPS+Code) to this
    repo, and then link to it here from Confluence
- [ ] add a section on code review governance
- [x] make expectations clear in [OPS: Code#Summary](https://unlimited.ethz.ch/spaces/GEG/pages/441418531/OPS+Code#OPS:Code-Summary)
    - [x] env management
    - [x] things that should be in all (even prior existing) projects
- [ ] make sure that GCP env (i.e. dev/prod) is handled in cookiecutter CI/CD pipelines (e.g. zone is europe-west , ...)

# Misc.
- [x] investigate switching from [`pre-commit`](https://pre-commit.com/) to [`prek`](https://prek.j178.dev/#prek-is-faster)
- [ ] add config management to the `data_project` blueprint — `pipeline/config/` is currently an empty placeholder
  - **pipeline hyperparameters** → `params.yaml` (DVC-native: tracked by `dvc
    params diff`, experiment-aware, reproducible)
  - **environment/credential settings** → [`dynaconf`](https://www.dynaconf.com/)
    with `settings.toml` (committed defaults) + `.secrets.toml` (gitignored) for
    things like WebDAV remotes or feature flags
  - these are complementary, not alternatives — both likely belong in the
    blueprint
