import numpy as np

from adorable_thunder.make.field_generators._random_state import get_random_state

# Common VAT/GST/sales tax rates used globally, with rough frequency weights.
# 0% weight raised to ~32% to reflect B2B exempt transactions (inter-company, export, exempt products).
# High brackets (18-25%) reduced; US (5-10%) and EU (20-21%) rates remain prominent.
_TAX_RATES = np.array([0.00, 0.05, 0.07, 0.08, 0.10, 0.13, 0.15, 0.18, 0.20, 0.21, 0.25])
_TAX_WEIGHTS = np.array([0.32, 0.08, 0.05, 0.06, 0.10, 0.05, 0.06, 0.10, 0.09, 0.06, 0.03])


def generate_tax_rates(n_samples: int) -> np.ndarray:
    return get_random_state().choice(_TAX_RATES, p=_TAX_WEIGHTS, size=n_samples)


def generate_discount_rates(n_samples: int, max_rate: float = 0.30) -> np.ndarray:
    """Beta(1, 5) base — ~25% of records get 0% discount; ~4% get strategic 25-30% discounts."""
    rng = get_random_state()
    rates = np.round(rng.beta(a=1, b=5, size=n_samples) * max_rate, 4)
    zero_mask = rng.random(n_samples) < 0.25
    rates[zero_mask] = 0.0
    high_mask = (~zero_mask) & (rng.random(n_samples) < 0.04)
    rates[high_mask] = np.round(rng.uniform(0.25, 0.30, n_samples)[high_mask], 4)
    return rates


def generate_gross_margin_rates(
    n_samples: int, mean: float = 0.35, std: float = 0.12
) -> np.ndarray:
    return np.round(
        np.clip(get_random_state().normal(loc=mean, scale=std, size=n_samples), 0.0, 1.0), 4
    )


def generate_budget_variance_rates(n_samples: int) -> np.ndarray:
    """Centered near 0; occasional large swings in either direction."""
    return np.round(
        np.clip(get_random_state().normal(loc=0.0, scale=0.08, size=n_samples), -0.50, 0.50), 4
    )
