import numpy as np
import pandas as pd

from adorable_thunder.generators.currency import USD_RATES


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


def generate_local_currency_amounts(
    amounts: np.ndarray,
    currency_codes: np.ndarray,
) -> pd.DataFrame:
    """
    Convert amounts to local currency using broad fixed exchange rates.

    Returns a DataFrame with columns: currency_code, rate, amount_usd, amount_local.
    """
    local_amounts_df = pd.DataFrame({"currency_code": currency_codes})
    local_amounts_df["rate"] = local_amounts_df["currency_code"].map(USD_RATES)
    local_amounts_df["amount_usd"] = amounts
    local_amounts_df["amount_local"] = (
        local_amounts_df["amount_usd"] * local_amounts_df["rate"]
    ).round(2)

    return local_amounts_df
