import numpy as np

# Common prefixes by goods/service category
_PREFIXES = ["PROD", "SKU", "MAT", "COMP", "ITEM", "PKG", "SVC", "LIC"]


def generate_product_codes(n_samples: int, prefix: str = "PROD") -> np.ndarray:
    digits = np.random.randint(0, 9_999_999, size=n_samples)
    return np.array([f"{prefix}-{d:07d}" for d in digits])


def generate_sku_codes(n_samples: int) -> np.ndarray:
    """Generate product codes with mixed category prefixes."""
    prefixes = np.random.choice(_PREFIXES, size=n_samples, replace=True)
    digits = np.random.randint(0, 9_999_999, size=n_samples)
    return np.array([f"{p}-{d:07d}" for p, d in zip(prefixes, digits)])
