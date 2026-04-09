import numpy as np

from adorable_thunder.common.math import round_weights_and_rebalance


def generate_amounts(
    n_samples: int,
    min_amount: float = 1000.0,
    max_amount: float = 100_000.0,
    mu: float = 10.0,
    sigma: float = 1.5,
) -> np.ndarray:
    """
    Tune mu and sigma by sector:

    Sector	mu	sigma	Median
    Office supplies	6.0	1.2	~$400
    Manufacturing inputs	9.0	1.5	~$8,000
    Enterprise software	10.5	1.3	~$36,000
    Raw materials	11.0	1.8	~$60,000

    """
    amount = np.random.lognormal(mean=mu, sigma=sigma, size=n_samples)
    amount = np.clip(amount, min_amount, max_amount)
    amount = np.round(amount, 2)
    return amount
