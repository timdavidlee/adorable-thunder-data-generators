# docs/generated/

Everything in this folder is written by AI. Humans read it; Claude writes it.

```
docs/generated/
  CLAUDE.md          # this file
  iter/              # one log per skill invocation
    <brief>/
      YYYY-MM-DD-HHMMSS--<skill>.md
```

## Iteration logs

Every time one of the skills below is run, write a log file to `docs/generated/iter/<brief>/YYYY-MM-DD-HHMMSS--<skill>.md` describing what changed. The log is the last step of the skill — write it after the work is done, not before.

### Which skills log

| Skill | `<brief>` | `<skill>` |
|---|---|---|
| `add-flow` | flow name (kebab-case, e.g. `record-to-report`) | `add-flow` |
| `add-brief` | flow name (kebab-case) | `add-brief` |
| `generate-and-scrutinize` | flow name (kebab-case) | `generate-and-scrutinize` |
| `generate-and-scrutinize-mcp` | flow name (kebab-case) | `generate-and-scrutinize-mcp` |
| `scrutinize` | flow name (kebab-case) | `scrutinize` |
| `insights-wishlist` | flow name (kebab-case) | `insights-wishlist` |
| `reset-schema` | flow name (kebab-case) | `reset-schema` |
| `scrutinize-briefs` | `_all` (reviews every brief) | `scrutinize-briefs` |

Skills not in this list (`caveman`, `write-a-skill`, etc.) do not log.

### Filename

Use the local time when the skill finishes:

```bash
date +%Y-%m-%d-%H%M%S
```

Example: `docs/generated/iter/order-to-cash/2026-04-28-181203--generate-and-scrutinize.md`.

Create the `<brief>/` subdirectory if it does not already exist.

### Contents

Keep logs short — a few paragraphs, not a transcript. Markdown only, no frontmatter. Cover, in this order:

1. **What ran.** One line: skill name, the flow argument, and any non-default flags.

2. **What changed.** A paragraph or two naming the files created, edited, or deleted, and the *intent* of each change (not a diff). For generator iterations, summarize the findings that drove the fix and the specific generator tweaks made.

3. **Verification.** What was checked to confirm the change worked (tests passed, schema regenerated cleanly, scrutiny findings addressed, etc.). If verification was skipped, say so and why.

4. **Follow-ups.** Anything left undone, surprising state encountered, or decisions deferred. Omit the section if there is nothing to record — do not pad.

The audience is a future Claude (or human) catching up on what this flow has been through. Optimize for skimmability: prefer file paths over prose, and bullet lists over walls of text when listing more than three items.
