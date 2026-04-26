import numpy as np

from adorable_thunder.make.reference_data.payment_terms import PAYMENT_TERMS

from adorable_thunder.make.field_generators.payment_terms import generate_payment_terms

_VALID_LABELS = {t[1] for t in PAYMENT_TERMS}


def test_generate_payment_terms_returns_correct_length():
    result = generate_payment_terms(40)
    assert len(result) == 40


def test_generate_payment_terms_values_from_reference_pool():
    result = generate_payment_terms(100)
    assert all(label in _VALID_LABELS for label in result)
