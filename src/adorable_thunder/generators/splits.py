import numpy as np
import pandas as pd


def assign_random_splits(
    n_samples: int,
    min_splits: int = 1,
    max_splits: int = 5,
    dist_scaling: int | None = None,
) -> np.ndarray:
    """
    Generates a series of random splits between the specified minimum and maximum splits.
    Args:
        n_samples: The number of random splits to generate
        min_splits: The minimum number of splits to generate (should be at least 1)
        max_splits: The maximum number of splits to generate (should be greater than or equal to min_splits)
        dist_scaling: The scaling factor for the distribution, if None, then uniform
            0.5 will result in 1/sqrt distribution,
            2 will result in 1/n^2 distribution, etc.
            Higher values will result in a more skewed distribution towards the minimum number of splits.
    Returns:
        A numpy array containing the generated random splits
    """
    if dist_scaling is None:
        splits = np.random.randint(min_splits, max_splits + 1, size=n_samples)
    else:
        num_split_list = np.arange(min_splits, max_splits + 1)
        weights = 1 / np.power(num_split_list, dist_scaling)
        weights = weights / weights.sum()
        splits = np.random.choice(num_split_list, size=n_samples, p=weights)
    return splits


def split_multiple_records(records: np.ndarray, splits: np.ndarray) -> np.ndarray:
    """
    Splits multiple records into multiple records based on the specified splits.
    Args:
        records: A numpy array containing the records to split
        splits: A numpy array containing the number of splits for each record. Must be the same length as records.
    Returns:
        A numpy array containing the split records
    """
    return np.repeat(records, splits, axis=0)


def _round_and_rebalance(x: pd.Series, precision: int) -> pd.Series:
    """Round weights to precision and rebalance using the largest remainder method."""
    unit = 10**-precision
    rounded = x.round(precision)
    n_adjust = round((1.0 - rounded.sum()) / unit)
    if n_adjust > 0:
        idx = (x / unit % 1).nlargest(n_adjust).index
        rounded.loc[idx] = (rounded.loc[idx] + unit).round(precision)
    elif n_adjust < 0:
        idx = (x / unit % 1).nsmallest(-n_adjust).index
        rounded.loc[idx] = (rounded.loc[idx] - unit).round(precision)
    return rounded


def assign_split_weights_within_original_record(
    splits: np.ndarray, precision: int = 4
) -> pd.DataFrame:
    """
    Assigns random weights to each split record, ensuring that the weights for each original record sum to 1.
    Args:
        splits: A numpy array containing the number of splits for each original record. Must be the same length as the number of original records.
        precision: Number of decimal places to round split weights to.
    Returns:
        A numpy array containing the weights for each split record, where the weights for each original record sum to 1.
    """

    df = pd.DataFrame({"splits": splits})
    df["split_weight"] = np.random.rand(len(df))
    df["weight_rank"] = df.groupby("splits")["split_weight"].rank(method="first")
    df["split_weight"] = df.groupby("splits")["split_weight"].transform(
        lambda x: _round_and_rebalance(x / x.sum(), precision)
    )

    assert (
        df.groupby("splits")["split_weight"].sum().eq(1).all()
    ), "Weights for each original record must sum to 1"
    return df.drop(columns=["weight_rank"])


def generate_split_weights_for_records(
    records: np.ndarray,
    min_splits: int = 1,
    max_splits: int = 5,
    dist_scaling: int | None = None,
) -> pd.DataFrame:
    """
    Generates random splits and corresponding weights for each record.
    Args:
        records: A numpy array containing the records to split
        min_splits: The minimum number of splits to generate (should be at least 1)
        max_splits: The maximum number of splits to generate (should be greater than or equal to min_splits)
        dist_scaling: The scaling factor for the distribution, if None, then uniform
            0.5 will result in 1/sqrt distribution,
            2 will result in 1/n^2 distribution, etc.
            Higher values will result in a more skewed distribution towards the minimum number of splits.
    Returns:
        A pandas DataFrame containing the split records and their corresponding weights, where the weights for each original record sum to 1.
    """
    splits = assign_random_splits(
        n_samples=len(records),
        min_splits=min_splits,
        max_splits=max_splits,
        dist_scaling=dist_scaling,
    )
    split_records = split_multiple_records(records, splits)
    split_weights_df = assign_split_weights_within_original_record(split_records)
    return split_weights_df
