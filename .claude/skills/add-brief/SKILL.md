---
name: add-brief
description: >
  Adds a new enterprise dataflow brief markdown file in
  src/adorable_thunder/enterprise_dataflow_briefs/ and registers it in the
  briefs CLAUDE.md index. Use when the user says "add a brief", "add a new
  brief", "write a brief", "draft a brief", or invokes /add-brief. Accepts a
  flow name as an argument (e.g. "hire-to-retire", "issue-to-resolution").
  This is the lightweight counterpart to /add-flow — brief only, no generators.
---

# Add Brief

Creates a new enterprise dataflow brief and registers it for shared use by `make/` and `scrutinize/`.

Use this when the user only wants the design document (the brief). For a full implementation including the scrutiny brief, generator package, and pipeline wiring, use `/add-flow` instead.

## Naming

The flow name is used in two forms:

| Form | Example | Used for |
|---|---|---|
| kebab-case | `hire-to-retire` | Brief filename, CLAUDE.md `@`-import |
| Title Case (ABBR) | `Hire-to-Retire (H2R)` | Brief H1 heading |

## Checklist

Work through these in order. Verify each before moving to the next.

### 1. Check for an existing brief

**Before doing anything else**, check whether the brief file already exists:

```
src/adorable_thunder/enterprise_dataflow_briefs/<flow-name>.md
```

If it exists, **stop and warn the user**. Show:
- The path of the existing brief
- A one-line summary of what it covers (read the H1 and Flow line)

Then ask whether they want to:
1. **Edit the existing brief** (in which case proceed as a targeted edit, not a fresh write)
2. **Pick a different name** (the new flow may belong under a different kebab-case name)
3. **Overwrite** (only proceed after explicit confirmation — overwriting destroys prior work)

Do not proceed to step 2 until the user has chosen.

### 2. Confirm scope

Before writing, confirm with the user:
- The flow name (kebab-case) and abbreviation
- The high-level stages of the flow (the `**Flow:**` line)
- Whether any sibling brief already covers this ground (skim existing brief filenames in `src/adorable_thunder/enterprise_dataflow_briefs/` and flag overlap — e.g., a new "order-to-invoice" brief overlaps with `order-to-cash.md`)

If the user is vague, propose 2–3 candidate stage breakdowns and ask which fits.

### 3. Write the brief

Path:

```
src/adorable_thunder/enterprise_dataflow_briefs/<flow-name>.md
```

Required sections, in order:

1. **H1 heading** — `# <Flow Name> (<ABBR>)`
2. **Flow line** — `**Flow:** Stage A → Stage B → Stage C → ...` immediately under the H1
3. **One-paragraph summary** — what this flow covers and how it relates to adjacent flows
4. **`## Records`** — markdown table with ≥ 3 record types, each with ≥ 4 key fields
5. **`## Business Rules`** — ≥ 3 rules; include at least one of: date-chain constraint, amount-integrity rule, or status-transition definition
6. **`## Realism Benchmarks`** — ≥ 4 bullets, each with concrete numbers (counts, ranges, percentages, durations); cover at least two of: volume, rates/percentages, timing, distribution patterns
7. **`## Field Generators`** — comma-separated list of applicable generators (see [available generators](#available-field-generators) below)

Optional but encouraged when the domain warrants it:
- A reference table (asset classes, status transitions, channels, modes, tiers, etc.) between Records and Business Rules
- A reference values list (enum-like sets — reasons, condition codes, contract types)

See an existing brief like `procure-to-pay.md` or `acquire-to-retire.md` for shape.

### 4. Register in the briefs index

File: `src/adorable_thunder/enterprise_dataflow_briefs/CLAUDE.md`

Append an `@<flow-name>.md` line to the existing list. Order is loose — group by domain (finance, supply chain, sales/marketing) when reasonable, but appending at the end is fine.

### 5. Verify

Run the brief reviewer to confirm the new brief passes both gates:

```
/scrutinize-briefs
```

The new brief should report `Design detail: OK` and `Benchmarks: OK`. Fix any thin sections it flags.

### 6. Write iteration log

After the brief is in place, record what was done.

Path: `docs/generated/iter/<flow-name>/<timestamp>--add-brief.md`

- `<flow-name>` is the kebab-case flow name (same as the brief filename)
- `<timestamp>` is `date +%Y-%m-%d-%H%M%S` at completion

Create the `<flow-name>/` subdirectory if it does not exist. Follow the contents template in [docs/generated/CLAUDE.md](../../docs/generated/CLAUDE.md) — a few paragraphs covering what ran, what changed, verification, and follow-ups.

## Available field generators

Common generators referenced across briefs (see `src/adorable_thunder/make/field_generators/` for the full list):

`amounts`, `dates`, `identifiers`, `company`, `users`, `person`, `phone`, `cost_center`, `currency`, `payment_terms`, `percentage`, `country`, `address`, `carrier`, `incoterms`, `product_code`, `unit_of_measure`, `ledger_account`, `fiscal_period`

If the flow needs a generator that doesn't exist yet, list it anyway — it documents intent, and the implementing engineer (or `/add-flow`) will add it.

## Quality bar

A good brief is **specific and quantitative**. Bad: "amounts vary widely". Good: "$500–$500k, lognormal peak ~$10k". Numbers in the Realism Benchmarks section are what make a brief useful as ground truth for both generators and scrutiny.
