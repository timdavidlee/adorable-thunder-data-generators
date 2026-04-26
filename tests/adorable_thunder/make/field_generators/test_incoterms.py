from adorable_thunder.make.reference_data.incoterms import INCOTERMS

from adorable_thunder.make.field_generators.incoterms import generate_incoterms_codes

_ALL_CODES = {i[0] for i in INCOTERMS}
_SEA_CODES = {"FAS", "FOB", "CFR", "CIF"}


def test_generate_incoterms_codes_returns_correct_length():
    result = generate_incoterms_codes(30)
    assert len(result) == 30


def test_generate_incoterms_codes_values_from_reference_pool():
    result = generate_incoterms_codes(100)
    assert all(code in _ALL_CODES for code in result)


def test_generate_incoterms_codes_sea_filter_restricts_output():
    result = generate_incoterms_codes(50, transport_mode="sea")
    assert all(code in _SEA_CODES for code in result)
