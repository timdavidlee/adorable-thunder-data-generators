from adorable_thunder.make.reference_data.countries import COUNTRIES

from adorable_thunder.make.field_generators.country import (
    generate_country_codes,
    generate_country_names,
)

_VALID_CODES = {c[0] for c in COUNTRIES}
_VALID_NAMES = {c[1] for c in COUNTRIES}


def test_generate_country_codes_returns_correct_length():
    result = generate_country_codes(30)
    assert len(result) == 30


def test_generate_country_codes_are_two_char_strings():
    result = generate_country_codes(50)
    assert all(len(code) == 2 for code in result)


def test_generate_country_codes_from_reference_pool():
    result = generate_country_codes(50)
    assert all(code in _VALID_CODES for code in result)


def test_generate_country_names_returns_correct_length():
    result = generate_country_names(30)
    assert len(result) == 30


def test_generate_country_names_from_reference_pool():
    result = generate_country_names(50)
    assert all(name in _VALID_NAMES for name in result)
