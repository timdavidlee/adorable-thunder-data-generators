import re

from adorable_thunder.make.field_generators.product_code import (
    generate_product_codes,
    generate_sku_codes,
)

_KNOWN_PREFIXES = {"PROD", "SKU", "MAT", "COMP", "ITEM", "PKG", "SVC", "LIC"}


def test_generate_product_codes_returns_correct_length():
    result = generate_product_codes(20)
    assert len(result) == 20


def test_generate_product_codes_default_prefix_format():
    result = generate_product_codes(20)
    assert all(re.match(r"^PROD-\d{7}$", code) for code in result)


def test_generate_product_codes_custom_prefix():
    result = generate_product_codes(10, prefix="MAT")
    assert all(code.startswith("MAT-") for code in result)


def test_generate_sku_codes_returns_correct_length():
    result = generate_sku_codes(25)
    assert len(result) == 25


def test_generate_sku_codes_format():
    result = generate_sku_codes(20)
    for code in result:
        prefix, digits = code.split("-")
        assert prefix in _KNOWN_PREFIXES
        assert re.match(r"^\d{7}$", digits)
