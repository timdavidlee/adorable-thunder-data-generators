from adorable_thunder.make.reference_data.cost_centers import COST_CENTERS

from adorable_thunder.make.field_generators.cost_center import generate_cost_center_names


def test_generate_cost_center_names_returns_correct_length():
    result = generate_cost_center_names(25)
    assert len(result) == 25


def test_generate_cost_center_names_from_reference_pool():
    result = generate_cost_center_names(50)
    assert all(name in COST_CENTERS for name in result)
