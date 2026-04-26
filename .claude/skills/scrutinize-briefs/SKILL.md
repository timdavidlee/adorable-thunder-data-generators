---
name: scrutinize-briefs
description: >
  Reviews enterprise dataflow brief markdown files in
  src/adorable_thunder/enterprise_dataflow_briefs/ for design completeness and
  benchmark quality. Use when the user says "scrutinize briefs", "review the
  briefs", "check the briefs", or invokes /scrutinize-briefs.
---

# Scrutinize Briefs

Read every `.md` file in `src/adorable_thunder/enterprise_dataflow_briefs/` (skip `CLAUDE.md`).
For each brief, grade it on two dimensions and report findings inline.

## 1 — Design Detail

A well-specified brief has all of:

- **Flow line** at the top (`**Flow:** step → step → …`)
- **Records table** with ≥ 3 record types, each with ≥ 4 key fields
- **Business Rules** with ≥ 3 rules that include at least one of:
  - Date-chain constraint (`date_A ≤ date_B`)
  - Amount-integrity rule (how totals derive from parts)
  - Status-transition definition
- **Field Generators** listing applicable generators

Flag as **thin design** if any of the above is missing or has fewer items than the minimums.
Also flag if there's no domain-specific reference section where one would be expected
(e.g., a manufacturing brief with no BOM or work-center detail, a subscription brief with no plan tiers).

## 2 — Realism Benchmarks

A useful `## Realism Benchmarks` section must have:

- ≥ 4 bullet points
- Quantitative values in each bullet (numbers, ranges, percentages — not vague prose)
- Coverage across at least two of: volume/counts, rates/percentages, timing/durations, distribution patterns

Flag as **missing benchmarks** if the section is absent entirely.
Flag as **weak benchmarks** if present but fewer than 4 bullets, or if bullets lack numbers.

## Output Format

For each brief, output a block like:

```
### {Flow Name}  [{PASS} | {ISSUES FOUND}]

Design detail: [OK | thin — <reason>]
Benchmarks:    [OK | missing | weak — <reason>]

<Any specific gaps as a tight bulleted list, only if there are issues>
```

End with a **Summary** table:

| Brief | Design | Benchmarks |
|-------|--------|------------|
| …     | OK / thin | OK / missing / weak |

Followed by a prioritized list of the top issues to fix, most impactful first.
