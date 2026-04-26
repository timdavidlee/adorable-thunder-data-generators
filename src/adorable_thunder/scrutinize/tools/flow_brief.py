from pathlib import Path

from langchain_core.tools import tool  # type: ignore[reportUnknownVariableType]

_BRIEFS_DIR = Path(__file__).parent.parent / "specific_briefs"
_VALID_FLOWS = sorted(p.stem for p in _BRIEFS_DIR.glob("*.md") if p.stem != "CLAUDE")


@tool
async def get_flow_brief(flow: str) -> str:
    """Return the scrutiny brief for a named enterprise flow.

    Call this first to load the domain-specific business rules, realism benchmarks,
    and high-priority checks for the flow being evaluated.

    Valid flow names: acquire-to-retire, budget-to-report, campaign-to-conversion,
    forecast-to-stock, lead-to-opportunity, order-to-cash, plan-to-produce,
    procure-to-pay, quote-to-cash, record-to-report, returns-reverse-logistics,
    transportation-and-logistics, warehouse-management.
    """
    path = _BRIEFS_DIR / f"{flow}.md"
    if not path.exists():
        return f"Unknown flow '{flow}'. Valid flows: {', '.join(_VALID_FLOWS)}"
    return path.read_text()
