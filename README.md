# Package Template

This repository is a [Cookiecutter](https://github.com/cookiecutter/cookiecutter) template for generating new Python packages within the ETHZ/EAPS/GEG Group.

It provides a standard structure, modern tooling (via `uv`), linting, type-checking, and pre-configured Git hooks to ensure consistency across our projects.

## Prerequisites

Before generating a new project from this template, you need to have Python and `uv` installed.

1. **Install Python**: You need Python >= 3.11 installed on your system.
   - **macOS**: `brew install python@3.11` (or latest available)
   - **Linux (Ubuntu/Debian)**: `sudo apt update && sudo apt install python3 python3-pip python3-venv`
   - **Windows**: Download the official installer from [python.org](https://www.python.org/downloads/windows/) or install via the Microsoft Store.
1. **Install `uv`**: Follow the [official uv installation guide](https://docs.astral.sh/uv/getting-started/installation/).
   - For macOS/Linux, you can run: `curl -LsSf https://astral.sh/uv/install.sh | sh`
   - For Windows, you can run: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## Generating a New Project

To generate a new project from this template, run `cookiecutter` using `uvx` (which temporarily downloads and runs the tool without installing it permanently in your global environment):

```bash
uvx --from cookiecutter cookiecutter git@gitlab.ethz.ch:geg/templates/package-template.git
```

### The Interactive Prompt

When you run the command, Cookiecutter will ask you a series of questions to configure your new project:

- `Project Name (e.g. My Awesome Package)`: The human-readable name of your project.
- `Project Slug (i.e. directory name -- lowercase, no spaces)`: The directory and package name (e.g., `my-awesome-package`). It defaults to a slugified version of your project name.
- `A short, awesome description for my project`: A brief description of what your package does.
- `Author or Organization Name`: Your name or organization (defaults to `ETHZ/EAPS/GEG Group`).
- `version`: The initial version of your package (defaults to `0.1.0`).

## What Happens Next?

Once you complete the prompts, Cookiecutter will automatically:

1. Create a new directory named after your `project_slug`.
1. Generate all the necessary files (`pyproject.toml`, `README.md`, `CONTRIBUTING.md`, etc.) with your customized variables filled in.
1. Automatically initialize a new `git` repository.
1. Set up the local `.githooks`.
1. Stage the initial project files and create an initial commit.


## Developers
See [CONTRIBUTING.md](./CONTRIBUTING.md)
