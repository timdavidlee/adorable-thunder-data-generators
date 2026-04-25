---
paths:
  - "**/*.py"
---

# Python Style Guide

**Naming**
- `snake_case` for variables, functions, modules; `PascalCase` for classes; `UPPER_SNAKE` for module-level constants
- Names should read like prose: `get_user_by_id`, not `fetch_usr`, not `retrieve_the_user_from_the_database`
- Avoid single-letter names except loop indices (`i`, `j`) and math (`x`, `y`)

**Formatting**
- Follow PEP 8; use a formatter (black/ruff) — don't debate whitespace
- Max line length: 100 chars
- One blank line between methods; two between top-level definitions

**Imports**
- stdlib → third-party → local, separated by blank lines
- No wildcard imports (`from x import *`)
- Import the module when the call site is clearer: `os.path.join(...)` beats `from os.path import join`

**Type hints**
- Annotate public function signatures; skip for obvious one-liners
- Use `X | None` over `Optional[X]` (Python 3.10+)
- Don't annotate internal variables unless the type is non-obvious

**Comments**
- Write zero comments by default
- Add one only when the *why* is non-obvious: a hidden constraint, a workaround, a subtle invariant
- Never explain what the code does — names do that

**Error handling**
- Only handle errors that can actually happen at your system boundary (user input, external APIs)
- Don't catch broad exceptions to swallow noise; let unexpected failures raise
- Prefer returning `None` or raising a domain exception over returning sentinel values

**Docstrings**
- Skip for private/internal functions
- One-line max for simple public functions; only add multi-section format (`Args`, `Returns`) for complex public APIs
