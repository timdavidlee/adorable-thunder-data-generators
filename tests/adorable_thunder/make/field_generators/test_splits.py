import numpy as np

from adorable_thunder.make.field_generators.splits import (
    assign_split_weights_within_original_record,
)


def test_output_length_matches_input():
    splits = np.array([0, 0, 1, 1, 1, 2])

    result = assign_split_weights_within_original_record(splits)

    assert len(result) == len(splits)


def test_returns_dataframe_with_expected_columns():
    splits = np.array([0, 0, 1])

    result = assign_split_weights_within_original_record(splits)

    assert list(result.columns) == ["splits", "split_weight"]


def test_weights_sum_to_one_per_group():
    splits = np.array([0, 0, 1, 1, 1, 2])

    result = assign_split_weights_within_original_record(splits)

    sums = result.groupby("splits")["split_weight"].sum()
    assert sums.eq(1.0).all()


def test_all_weights_are_positive():
    splits = np.array([0, 0, 1, 1, 1])

    result = assign_split_weights_within_original_record(splits)

    assert (result["split_weight"] > 0).all()


def test_single_element_group_has_weight_one():
    splits = np.array([0, 1, 1])

    result = assign_split_weights_within_original_record(splits)

    solo_weight = result.loc[result["splits"] == 0, "split_weight"].iloc[0]
    assert solo_weight == 1.0


def test_weights_respect_default_precision():
    splits = np.array([0, 0, 0, 1, 1])

    result = assign_split_weights_within_original_record(splits)

    assert (result["split_weight"].round(4) == result["split_weight"]).all()


def test_weights_respect_custom_precision():
    splits = np.array([0, 0, 0, 1, 1])

    result = assign_split_weights_within_original_record(splits, precision=2)

    assert (result["split_weight"].round(2) == result["split_weight"]).all()
