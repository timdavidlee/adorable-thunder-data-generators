import numpy as np

from adorable_thunder.make.field_generators.amounts import (
    generate_amounts,
    generate_local_currency_amounts,
)


def test_generate_amounts_returns_correct_length():
    result = generate_amounts(30)
    assert len(result) == 30


def test_generate_amounts_within_default_bounds():
    result = generate_amounts(200)
    assert (result >= 1000.0).all() and (result <= 100_000.0).all()


def test_generate_amounts_respects_custom_bounds():
    result = generate_amounts(200, min_amount=500.0, max_amount=5_000.0)
    assert (result >= 500.0).all() and (result <= 5_000.0).all()


def test_generate_amounts_rounded_to_two_decimals():
    result = generate_amounts(50)
    assert (result.round(2) == result).all()


def test_generate_local_currency_amounts_has_expected_columns():
    amounts = generate_amounts(10)
    currency_codes = np.array(["USD", "EUR", "JPY", "GBP", "CAD"] * 2)
    result = generate_local_currency_amounts(amounts, currency_codes)
    assert list(result.columns) == ["currency_code", "rate", "amount_usd", "amount_local"]


def test_generate_local_currency_amounts_usd_rate_is_one():
    amounts = np.array([100.0, 200.0])
    currency_codes = np.array(["USD", "USD"])
    result = generate_local_currency_amounts(amounts, currency_codes)
    assert (result["amount_local"] == result["amount_usd"]).all()
