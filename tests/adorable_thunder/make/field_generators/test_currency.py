import pytest

from adorable_thunder.make.field_generators.currency import (
    TOP_CURRENCIES,
    USD_RATES,
    generate_currency_entries,
    usd_to,
)

_VALID_CODES = {c.code for c in TOP_CURRENCIES}


def test_usd_to_converts_known_currency():
    result = usd_to(100.0, "EUR")
    assert result == pytest.approx(100.0 * USD_RATES["EUR"], abs=0.01)  # type: ignore[reportUnknownMemberType]


def test_usd_to_rounds_to_two_decimal_places():
    result = usd_to(1.0, "JPY")
    assert result is not None
    assert result == round(result, 2)


def test_usd_to_returns_none_for_unknown_currency():
    result = usd_to(100.0, "XYZ")
    assert result is None


def test_generate_currency_entries_returns_correct_length():
    result = generate_currency_entries(40)
    assert len(result) == 40


def test_generate_currency_entries_from_reference_pool():
    result = generate_currency_entries(100)
    assert all(code in _VALID_CODES for code in result)
