---
name: scrutinize
description: >
  Runs the adorable_thunder scrutinize agent against a generated database to evaluate
  data realism for an enterprise flow. Use when the user says "scrutinize", "run scrutinize",
  "check the data", "evaluate the data", or invokes /scrutinize. Accepts an optional flow
  name argument (e.g. "procure-to-pay", "order-to-cash"); defaults to "procure-to-pay".
---

# Scrutinize

Run the scrutinize agent against the database for the given flow.

## Usage

```
uv run python -m adorable_thunder.scrutinize <flow>
```

Valid flow names: `procure-to-pay`, `order-to-cash`

Default flow: `procure-to-pay`

## Steps

1. Determine the flow from the user's message. If none specified, use `procure-to-pay`.
2. Run the command via Bash, streaming output to the user.
3. When the command finishes, the JSON report is printed to stdout. Summarise the findings:
   - How many findings total, broken down by severity (high / medium / low)
   - The top high-severity findings (issue + suggestion)
   - Overall summary sentence from the report
   - If there are no findings, confirm explicitly: "No issues found — data looks realistic for `<flow>`."
