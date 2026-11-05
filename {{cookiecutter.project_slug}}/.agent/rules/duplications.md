# Duplications

Some content in this repo is intentionally repeated in more than one file, because
each copy needs to be readable in a context where the "source of truth" file isn't
available (e.g. a generated project doesn't carry `MIGRATION-GUIDE.md`, and a
terminal print statement can't `include` a Markdown file). When editing one copy
below, check and update the others in the same change.

## GitHub repository settings tables

The one-time GitHub UI settings (merge options, branch deletion, branch rulesets) an
Admin applies after creating a project's remote.

- **Source of truth:** `MIGRATION-GUIDE.md` → "GitHub repository settings" (under
  `## Git Workflow`)
- **Duplicated in:** `{{cookiecutter.project_slug}}/README.md` → "Repository Setup" →
  "GitHub repository settings" step (full tables, since generated projects don't have
  `MIGRATION-GUIDE.md`)
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

## CI workflow (blueprint ↔ template repo)

- **Source of truth:** `{{cookiecutter.project_slug}}/.github/workflows/ci.yml`
- **Duplicated in:** the template repo's own `.github/workflows/ci.yml` — a trimmed copy
  (shared jobs only), since GitHub can't load a workflow from outside the root
  `.github/workflows/`
