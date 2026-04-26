from adorable_thunder.make.reference_data.units_of_measure import UNITS_OF_MEASURE

from adorable_thunder.make.field_generators.unit_of_measure import generate_uom_codes

_ALL_CODES = {u[0] for u in UNITS_OF_MEASURE}
_WEIGHT_CODES = {u[0] for u in UNITS_OF_MEASURE if u[2] == "weight"}


def test_generate_uom_codes_returns_correct_length():
    result = generate_uom_codes(25)
    assert len(result) == 25


def test_generate_uom_codes_values_from_reference_pool():
    result = generate_uom_codes(50)
    assert all(code in _ALL_CODES for code in result)


def test_generate_uom_codes_category_filter_restricts_output():
    result = generate_uom_codes(30, category="weight")
    assert all(code in _WEIGHT_CODES for code in result)
