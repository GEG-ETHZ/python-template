# Code Quality and Linting

- **Adhere to Code Quality Standards:** Ensure all modifications comply with both general and language-specific linting rules.
- For Markdown files, ensure:
  - Fenced code blocks have language specified
  - Emphasis uses asterisks (`*text*`) not underscores (`_text_`)
  - Headers follow proper hierarchy
  - Links are properly formatted
- For code files, follow language-specific linting rules
- Use `read_lints` tool or IDE linter integration to check for issues

## Python

- **Avoid `_` prefixes on module-level helpers.** A single leading underscore is
  a convention signalling "internal", but it has no enforcement effect — it only
  suppresses `from module import *` export, which is irrelevant in scripts. Do
  not add it unless there is a concrete reason worth explaining.

- **Use `__` (name mangling) only inside class bodies, and only when subclass
  collision is a real concern.** Inside a class, `__name` is rewritten by the
  interpreter to `_ClassName__name`, preventing accidental override in
  subclasses. This is a real mechanical effect. Outside a class (module level),
  `__name` has no special behaviour — it is just a name with underscores. When
  name mangling is intentionally used, explain why in the docstring so the
  reason is not lost.
