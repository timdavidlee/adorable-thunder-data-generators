import numpy as np
import pandas as pd

from adorable_thunder.common.math import round_weights_and_rebalance


def generate_random_dates(
    start_date: str, end_date: str, n_samples: int, dist_scaling: int | None = None
) -> pd.Series:
    """
    Generates a series of random dates between the specified start and end dates.
    Args:
        start_date: The start date in the format 'YYYY-MM-DD'
        end_date: The end date in the format 'YYYY-MM-DD'
        n_samples: The number of random dates to generate
        dist_scaling: The scaling factor for the distribution, if None, then uniform
            0.5 will result in 1/sqrt distribution,
            2 will result in 1/n^2 distribution, etc.
            Higher values will result in a more skewed distribution towards the start date.

    Returns:
        A pandas Series containing the generated random dates
    """
    days = pd.to_datetime(end_date) - pd.to_datetime(start_date)
    if dist_scaling is None:
        random_days = np.random.randint(0, days.days, n_samples)
    else:
        num_day_list = np.arange(1, days.days + 1)
        weights = 1 / np.power(num_day_list, dist_scaling)
        weights = weights / weights.sum()
        weights = round_weights_and_rebalance(weights, precision=4)
        random_days = np.random.choice(num_day_list, size=n_samples, p=weights)

    date_series = pd.Series(np.repeat(start_date, n_samples))
    random_dates = pd.to_datetime(date_series) + pd.to_timedelta(random_days, unit="D")
    return pd.Series(random_dates)


def extrapolate_off_dates(
    pd_date_series: pd.Series,
    min_days: int = -7,
    max_days: int = 14,
) -> pd.Series:
    """
    Extrapolates off dates from a series of pandas datetime objects by adding a random number of days to each date.
    Args:
        pd_date_series: A pandas Series containing datetime objects
        min_days: The minimum number of days to add (can be negative)
        max_days: The maximum number of days to add (should not be negative)
    Returns:
        A pandas Series containing the extrapolated off dates
    """
    random_days = np.random.randint(min_days, max_days + 1, size=len(pd_date_series))
    off_dates = pd_date_series + pd.to_timedelta(random_days, unit="D")
    return pd.Series(off_dates)


def choose_random_date_between_dates(
    start_dates: pd.Series, end_dates: pd.Series
) -> pd.Series:
    """
    Chooses a random date between two series of pandas datetime objects.
    Args:
        start_dates: A pandas Series containing the start datetime objects
        end_dates: A pandas Series containing the end datetime objects
    Returns:
        A pandas Series containing the randomly chosen dates between the start and end dates
    """
    random_days = np.random.randint(
        0, (end_dates - start_dates).days + 1, size=len(start_dates)
    )
    random_dates = start_dates + pd.to_timedelta(random_days, unit="D")
    return pd.Series(random_dates)
