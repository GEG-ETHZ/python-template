# Contributing to `python-template`

> **Note for AI Agents**: This document explains the architecture of the `python-template` meta-repository. Read this before attempting to modify or refactor the template.

This repository is a [Cookiecutter](https://cookiecutter.readthedocs.io/) template. Its primary purpose is to generate highly standardized Python project scaffolding.

## Repository Structure

The repository is divided into structural logic (how the template executes) and the blueprint content (what the generated code looks like).

```text
python-template/
├── cookiecutter.json                 # Core configuration and user prompts
├── hooks/                            # Pre/Post generation Python scripts
│   └── post_gen_project.py
└── {{cookiecutter.project_slug}}/    # The actual project blueprint
    ├── CONTRIBUTING.md
    ├── pyproject.toml
    └── src/
```

### 1. `cookiecutter.json`
This is the configuration schema. It defines the variables that Cookiecutter will prompt the user for (e.g., `project_slug`, `author_name`, `version`).
- **AI Rule**: If you need to add a new configurable parameter to the template, you must add it to `cookiecutter.json` first as a key-value pair. The key becomes the Jinja2 variable name (e.g., `"my_setting": "default" ` becomes `{{ cookiecutter.my_setting }}`).

### 2. `{{cookiecutter.project_slug}}/`
This directory is the **blueprint**. It represents the root directory of the software project that will be generated.
- **AI Rule**: Any files placed in here will be copied exactly to the target destination.
- You can heavily utilize Jinja2 templating syntax inside these files (e.g., `{{ cookiecutter.project_slug }}`) to dynamically inject the user's answers from `cookiecutter.json`.
- Do **not** execute commands (like `uv run pytest`) directly inside this blueprint folder during development, as the Jinja template tags will cause syntax errors in Python/TOML/YAML validators until they are rendered.

### 3. `hooks/`
These are Python scripts that execute **around** the generation process.
- `post_gen_project.py`: Executes *after* the template has been copied to the user's machine.
- **AI Rule**: We use `post_gen_project.py` to initialize Git, do initial `.pre-commit-config.yaml` commits, and print follow-up terminal instructions (`Next steps:`). This script is also processed by Jinja, so you can use `{{ cookiecutter.project_slug }}` inside it.
