# Duplications

Some content in this repo is intentionally repeated in more than one file, because
each copy needs to be readable in a context where the "source of truth" file isn't
available (e.g. a generated project doesn't carry `MIGRATION-GUIDE.md`, and a
terminal print statement can't `include` a Markdown file). When editing one copy
below, check and update the others in the same change.

## GitLab / GitHub project settings tables

The one-time GitLab and GitHub UI settings (merge method, squash behavior, branch
protection) a Maintainer/Admin applies after creating a project's remote.

- **Source of truth:** `MIGRATION-GUIDE.md` → "GitLab project settings" and "GitHub
  repository settings" (under `## Git Workflow`)
- **Duplicated in:** `{{cookiecutter.project_slug}}/README.md` → "Repository Setup" →
  "GitLab project settings" and "GitHub repository settings" steps (full tables, since
  generated projects don't have `MIGRATION-GUIDE.md`)
- **Referenced (pointer only) from:** `hooks/post_gen_project.py` → `NEXT STEPS` print
  block, which points at the README section above rather than repeating the table in
  the terminal

## Initial push / bypass instructions

The "push main immediately, and how to bypass hooks/branch-protection for that one
push" instructions.

- **Duplicated in:**
  - `{{cookiecutter.project_slug}}/README.md` → "Repository Setup" → step 3
  - `hooks/post_gen_project.py` → `NEXT STEPS` print block

Both copies must stay word-for-word consistent in substance (exact command, the
`--no-verify` caveat, and the branch-protection escalation path), since this is
safety-critical setup guidance a user may follow from either location.

## CI configuration (GitLab ↔ GitHub)

The CI pipeline exists once per host, with the same job names and commands.

- **Blueprint:** `{{cookiecutter.project_slug}}/.gitlab-ci.yml` ↔
  `{{cookiecutter.project_slug}}/.github/workflows/ci.yml`
- **Template repo itself:** `.gitlab-ci.yml` (includes the blueprint file) ↔
  `.github/workflows/ci.yml` (a trimmed copy, since GitHub can't include a workflow from
  outside `.github/workflows/`)
