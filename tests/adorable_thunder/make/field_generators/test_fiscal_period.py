import re

import pytest

from adorable_thunder.make.field_generators.fiscal_period import generate_fiscal_periods


def test_generate_fiscal_periods_returns_correct_length():
    result = generate_fiscal_periods(30)
    assert len(result) == 30


@pytest.mark.parametrize(
    "granularity, pattern",
    [
        ("quarter", r"^FY\d{4}-Q[1-4]$"),
        ("month", r"^FY\d{4}-P\d{2}$"),
    ],
)
def test_generate_fiscal_periods_format(granularity: str, pattern: str):  # type: ignore[reportUnknownParameterType, reportMissingParameterType]
    result = generate_fiscal_periods(20, granularity=granularity)
    assert all(re.match(pattern, s) for s in result)


def test_generate_fiscal_periods_years_within_range():
    result = generate_fiscal_periods(100, start_year=2020, end_year=2024)
    years = [int(s[2:6]) for s in result]
    assert all(2020 <= y <= 2024 for y in years)


def test_generate_fiscal_periods_raises_on_invalid_granularity():
    with pytest.raises(ValueError, match="granularity"):
        generate_fiscal_periods(10, granularity="week")
