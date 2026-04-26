import json
from typing import Any

import pandas as pd
from langchain_core.tools import tool  # type: ignore[reportUnknownVariableType]


@tool
def profile_dataset(records_json: str) -> str:
    """Compute a statistical profile of a dataset sample.

    Accepts a JSON-encoded list of record dicts. Returns per-column stats:
    null rate, unique count, numeric distributions (min/max/mean/median/std),
    and top value frequencies for categoricals.

    Use this to identify sparse fields, implausible distributions, and
    suspicious uniformity before writing findings.
    """
    records: list[dict[str, Any]] = json.loads(records_json)
    df = pd.DataFrame(records)

    lines = [f"Shape: {len(df)} rows × {len(df.columns)} columns", ""]

    for col in df.columns:
        series = df[col]
        null_pct = series.isna().mean() * 100
        unique_count = series.nunique(dropna=False)
        lines.append(f"[{col}]")
        lines.append(f"  null: {null_pct:.1f}%  unique: {unique_count}")

        if pd.api.types.is_numeric_dtype(series) and not series.isna().all():
            desc = series.describe()
            lines.append(
                f"  min={desc['min']:.4g}  max={desc['max']:.4g}"
                f"  mean={desc['mean']:.4g}  median={series.median():.4g}"
                f"  std={desc['std']:.4g}"
            )
            # flag suspiciously low variance
            if desc["std"] == 0:
                lines.append("  WARNING: zero variance — all values identical")
        else:
            top = series.value_counts(dropna=False).head(8)
            samples = "  |  ".join(f"{str(v)!r}: {n}" for v, n in top.items())
            lines.append(f"  top: {samples}")

        lines.append("")

    return "\n".join(lines)
