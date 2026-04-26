import numpy as np

from adorable_thunder.make.field_generators._random_state import get_random_state


def generate_fiscal_periods(
    n_samples: int,
    start_year: int = 2022,
    end_year: int = 2026,
    granularity: str = "quarter",
) -> np.ndarray:
    """Generate fiscal period strings.
    granularity='quarter' → 'FY2025-Q2'
    granularity='month'   → 'FY2025-P03'
    """
    years = get_random_state().randint(start_year, end_year + 1, size=n_samples)
    if granularity == "quarter":
        periods = get_random_state().randint(1, 5, size=n_samples)
        return np.array([f"FY{y}-Q{p}" for y, p in zip(years, periods)])
    elif granularity == "month":
        periods = get_random_state().randint(1, 13, size=n_samples)
        return np.array([f"FY{y}-P{p:02d}" for y, p in zip(years, periods)])
    else:
        raise ValueError(f"granularity must be 'quarter' or 'month', got {granularity!r}")
