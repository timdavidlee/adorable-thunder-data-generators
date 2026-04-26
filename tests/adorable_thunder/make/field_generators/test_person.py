from adorable_thunder.make.field_generators.person import (
    generate_first_names,
    generate_full_names,
    generate_last_names,
)


def test_generate_first_names_returns_correct_length():
    result = generate_first_names(25)
    assert len(result) == 25


def test_generate_last_names_returns_correct_length():
    result = generate_last_names(25)
    assert len(result) == 25


def test_generate_full_names_returns_correct_length():
    result = generate_full_names(20)
    assert len(result) == 20


def test_generate_full_names_contain_space():
    result = generate_full_names(20)
    assert all(" " in name for name in result)
