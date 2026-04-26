import pandas as pd

from adorable_thunder.make.field_generators.dates import (
    choose_random_date_between_dates,
    extrapolate_off_dates,
    generate_random_dates,
)


def test_generate_random_dates():
    start_date = "2025-01-01"
    end_date = "2025-12-31"
    n_samples = 1000
    dates = generate_random_dates(start_date, end_date, n_samples)
    assert len(dates) == n_samples
    assert dates.min() >= pd.to_datetime(start_date)
    assert dates.max() <= pd.to_datetime(end_date)


def test_generate_random_dates_with_dist_scaling():
    start_date = "2025-01-01"
    end_date = "2025-12-31"
    n_samples = 1000
    dist_scaling = 5
    dates = generate_random_dates(start_date, end_date, n_samples, dist_scaling)
    midpoint = (
        pd.to_datetime(start_date) + (pd.to_datetime(end_date) - pd.to_datetime(start_date)) / 2
    )

    first_half_count = (dates < midpoint).sum()
    second_half_count = (dates >= midpoint).sum()

    # With 1/n^2 weighting, the first half should have significantly more samples
    assert first_half_count > second_half_count * 1.5


def test_extrapolate_off_dates():
    base_dates = pd.Series(pd.to_datetime(["2025-01-01", "2025-06-01", "2025-12-01"]))
    off_dates = extrapolate_off_dates(base_dates, min_days=2, max_days=14)
    assert len(off_dates) == len(base_dates)
    for base_date, off_date in zip(base_dates, off_dates):
        assert base_date - pd.Timedelta(days=2) <= off_date <= base_date + pd.Timedelta(days=14)


def test_choose_random_date_between_dates():
    start_dates = pd.Series(pd.to_datetime(["2025-01-01", "2025-06-01", "2025-12-01"]))
    end_dates = pd.Series(pd.to_datetime(["2025-01-10", "2025-06-10", "2025-12-10"]))
    random_dates = choose_random_date_between_dates(start_dates, end_dates)

    random_dates_after_start = random_dates >= start_dates
    random_dates_before_end = random_dates <= end_dates

    assert pd.concat([random_dates_after_start, random_dates_before_end], axis=1).all(axis=1).all()
