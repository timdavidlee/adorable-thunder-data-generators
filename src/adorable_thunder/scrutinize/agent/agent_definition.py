import logging
from typing import Any

from deepagents import create_deep_agent  # type: ignore[reportUnknownVariableType]
from langchain_core.messages import AIMessage, ToolMessage

from adorable_thunder.scrutinize.agent.schemas import ScrutinyReport
from adorable_thunder.scrutinize.tools import (
    get_flow_brief,
    get_table_llm_annotations,
    list_tables,
    run_sql,
)

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """\
You are a data quality critic for enterprise procurement and finance datasets.

Your job is to evaluate whether generated records in a PostgreSQL database look realistic
for a mid-to-large enterprise (500–10,000 employees) — one with diverse suppliers,
multi-currency spend, layered approval hierarchies, and dedicated procurement/finance teams.

## Evaluation approach

1. Call `get_flow_brief` with the flow name to load domain-specific business rules and
   realism benchmarks.
2. Call `get_table_llm_annotations` with the flow name to load per-column descriptions,
   expected data types, and representative example values for every table in the flow.
3. Call `list_tables` to discover the available schemas and tables.
4. Call `run_sql` to profile distributions, sample rows, check date chains, and validate
   cross-field consistency. Run as many queries as needed.
4. Reason over your findings against the brief. Flag what looks wrong.

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

If no issues are found, return a ScrutinyReport with an empty findings list and a summary
that explicitly confirms the data looks realistic (e.g. "No issues found — data looks
realistic for a mid-to-large enterprise <flow> dataset.").
"""

agent = create_deep_agent(
    system_prompt=_SYSTEM_PROMPT,
    tools=[get_flow_brief, get_table_llm_annotations, list_tables, run_sql],
    response_format=ScrutinyReport,
)


async def scrutinize(flow: str) -> ScrutinyReport:
    """Evaluate generated records in the database for realism.

    Args:
        flow: Enterprise flow name (e.g. "procure-to-pay", "order-to-cash").

    Returns:
        A ScrutinyReport with structured findings and a summary.
    """
    prompt = f"Evaluate the {flow} data in the database for realism."
    seen = 0
    final_state: dict[str, Any] | None = None
    async for state in agent.astream(  # type: ignore[reportUnknownMemberType]
        {"messages": [{"role": "user", "content": prompt}]},
        stream_mode="values",
    ):
        new_messages = state["messages"][seen:]
        seen = len(state["messages"])
        for msg in new_messages:
            if isinstance(msg, AIMessage):
                content = msg.content
                text = (
                    content
                    if isinstance(content, str)
                    else next(
                        (
                            b["text"]
                            for b in content
                            if isinstance(b, dict) and b.get("type") == "text" and b.get("text")
                        ),
                        None,
                    )
                )
                if text:
                    logger.info("Agent: %s", text)
                for tool_call in getattr(msg, "tool_calls", []):
                    logger.info(
                        "Calling tool: %s(%s)", tool_call["name"], tool_call.get("args", {})
                    )
            elif isinstance(msg, ToolMessage):
                logger.debug("Tool result [%s]: %.200s", msg.name, msg.content)
        final_state = state

    assert final_state is not None
    return final_state["structured_response"]
