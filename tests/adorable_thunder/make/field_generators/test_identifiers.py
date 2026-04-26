import uuid

import pytest

from adorable_thunder.make.field_generators.identifiers import (
    generate_n_random_uuids,
    generate_serial_numbers_with_prefix,
)


def test_generate_uuids_returns_correct_length():
    result = generate_n_random_uuids(15)
    assert len(result) == 15


def test_generate_uuids_are_valid():
    result = generate_n_random_uuids(10)
    for s in result:
        uuid.UUID(s)  # raises ValueError if invalid


def test_generate_serial_numbers_returns_correct_length():
    result = generate_serial_numbers_with_prefix(20)
    assert len(result) == 20


def test_generate_serial_numbers_have_correct_total_length():
    result = generate_serial_numbers_with_prefix(10, prefix="REQ", total_length=12)
    assert all(len(s) == 12 for s in result)


def test_generate_serial_numbers_start_with_prefix():
    result = generate_serial_numbers_with_prefix(10, prefix="INV", total_length=10)
    assert all(s.startswith("INV") for s in result)


def test_generate_serial_numbers_raises_when_prefix_too_long():
    with pytest.raises(ValueError, match="Prefix length must be less than total length"):
        generate_serial_numbers_with_prefix(5, prefix="ABCDE", total_length=5)
