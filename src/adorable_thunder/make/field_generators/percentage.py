import numpy as np

# Common VAT/GST/sales tax rates used globally, with rough frequency weights
_TAX_RATES = np.array([0.00, 0.05, 0.07, 0.08, 0.10, 0.13, 0.15, 0.18, 0.20, 0.21, 0.25])
_TAX_WEIGHTS = np.array([0.05, 0.07, 0.05, 0.06, 0.12, 0.05, 0.08, 0.20, 0.20, 0.07, 0.05])


def generate_tax_rates(n_samples: int) -> np.ndarray:
    return np.random.choice(_TAX_RATES, p=_TAX_WEIGHTS, size=n_samples)


def generate_discount_rates(n_samples: int, max_rate: float = 0.30) -> np.ndarray:
    """Beta(1, 5) distribution — most records have zero or small discounts."""
    return np.round(np.random.beta(a=1, b=5, size=n_samples) * max_rate, 4)


def generate_gross_margin_rates(
    n_samples: int, mean: float = 0.35, std: float = 0.12
) -> np.ndarray:
    return np.round(np.clip(np.random.normal(loc=mean, scale=std, size=n_samples), 0.0, 1.0), 4)


def generate_budget_variance_rates(n_samples: int) -> np.ndarray:
    """Centered near 0; occasional large swings in either direction."""
    return np.round(np.clip(np.random.normal(loc=0.0, scale=0.08, size=n_samples), -0.50, 0.50), 4)
