import numpy as np

from adorable_thunder.make.field_generators.phone import (
    generate_phone_numbers,
    generate_phone_numbers_mixed,
)


def test_generate_phone_numbers_returns_correct_length():
    result = generate_phone_numbers(50)
    assert len(result) == 50


def test_generate_phone_numbers_uses_correct_calling_code():
    result = generate_phone_numbers(20, country_code="DE")
    assert all(n.startswith("+49") for n in result)


def test_generate_phone_numbers_defaults_to_us_code_for_unknown_country():
    result = generate_phone_numbers(10, country_code="XX")
    assert all(n.startswith("+1") for n in result)


def test_generate_phone_numbers_mixed_length_matches_input():
    country_codes = np.array(["US", "DE", "JP", "FR"])
    result = generate_phone_numbers_mixed(len(country_codes), country_codes)
    assert len(result) == len(country_codes)


def test_generate_phone_numbers_mixed_uses_matching_calling_codes():
    country_codes = np.array(["US", "DE", "JP"])
    expected_prefixes = ["+1", "+49", "+81"]
    result = generate_phone_numbers_mixed(len(country_codes), country_codes)
    for number, prefix in zip(result, expected_prefixes):
        assert number.startswith(prefix)
