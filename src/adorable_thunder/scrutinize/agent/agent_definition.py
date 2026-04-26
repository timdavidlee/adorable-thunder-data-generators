import json
from typing import Any

from deepagents import create_deep_agent  # type: ignore[reportUnknownVariableType]

from adorable_thunder.scrutinize.agent.schemas import ScrutinyReport
from adorable_thunder.scrutinize.tools import get_flow_brief, profile_dataset

_SYSTEM_PROMPT = """\
You are a data quality critic for enterprise procurement and finance datasets.

Your job is to evaluate whether a sample of generated records looks realistic for a
mid-to-large enterprise (500–10,000 employees) — one with diverse suppliers, multi-currency
spend, layered approval hierarchies, and dedicated procurement/finance teams.

## Evaluation approach

1. Call `get_flow_brief` with the flow name to load domain-specific business rules and
   realism benchmarks.
2. Call `profile_dataset` with the JSON-encoded records to get a statistical profile.
3. Reason over the profile against the brief. Flag what looks wrong.

## What to flag

- Amount distributions that are too uniform or violate expected tiers
- Status distributions that are too clean (e.g. 90% approved)
- Date chain violations (e.g. payment before invoice)
- Cross-field inconsistencies (currency vs. supplier region, requester = approver)
- Sparse required fields (cost_center, currency_code, etc.) at >5% null
- Identifier formats that don't follow realistic conventions
- Supplier/product pairings from mismatched industries
- Arithmetic errors (e.g. gain/loss = proceeds − book_value)

## Output

Produce a ScrutinyReport. Each Finding must be specific and actionable:
- `field`: the column or field being flagged (use "multi-field" for cross-field issues)
- `issue`: what is wrong and why it's unrealistic
- `suggestion`: a concrete change the generator should make
- `severity`: low / medium / high
"""

agent = create_deep_agent(
    system_prompt=_SYSTEM_PROMPT,
    tools=[get_flow_brief, profile_dataset],
    response_format=ScrutinyReport,
)


def scrutinize(records: list[dict[str, Any]], flow: str) -> ScrutinyReport:
    """Evaluate a sample of generated records for realism.

    Args:
        records: 50–200 representative records from the generator.
        flow: Enterprise flow name (e.g. "procure-to-pay", "order-to-cash").

    Returns:
        A ScrutinyReport with structured findings and a summary.
    """
    prompt = (
        f"Evaluate this {flow} dataset sample for realism. "
        f"Flow: {flow}\n\n"
        f"Records (JSON):\n{json.dumps(records)}"
    )
    result: dict[str, Any] = agent.invoke(  # type: ignore[reportUnknownMemberType]
        {"messages": [{"role": "user", "content": prompt}]}
    )
    return result["structured_response"]
