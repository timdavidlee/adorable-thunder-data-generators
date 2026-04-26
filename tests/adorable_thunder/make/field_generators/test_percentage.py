from adorable_thunder.make.field_generators.percentage import (
    generate_budget_variance_rates,
    generate_discount_rates,
    generate_gross_margin_rates,
    generate_tax_rates,
)

_VALID_TAX_RATES = {0.00, 0.05, 0.07, 0.08, 0.10, 0.13, 0.15, 0.18, 0.20, 0.21, 0.25}


def test_generate_tax_rates_values_from_known_set():
    result = generate_tax_rates(100)
    assert all(r in _VALID_TAX_RATES for r in result)


def test_generate_discount_rates_within_default_bounds():
    result = generate_discount_rates(200)
    assert (result >= 0).all() and (result <= 0.30).all()


def test_generate_discount_rates_values_from_tiers():
    _VALID_TIERS = {0.00, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30}
    result = generate_discount_rates(200)
    assert all(float(r) in _VALID_TIERS for r in result)


def test_generate_gross_margin_rates_within_unit_interval():
    result = generate_gross_margin_rates(200)
    assert (result >= 0.0).all() and (result <= 1.0).all()


def test_generate_budget_variance_rates_within_bounds():
    result = generate_budget_variance_rates(200)
    assert (result >= -0.50).all() and (result <= 0.50).all()
