import numpy as np

from adorable_thunder.make.field_generators._random_state import get_random_state

# Common prefixes by goods/service category
_PREFIXES = ["PROD", "SKU", "MAT", "COMP", "ITEM", "PKG", "SVC", "LIC"]


def generate_product_codes(n_samples: int, prefix: str = "PROD") -> np.ndarray:
    digits = get_random_state().randint(0, 9_999_999, size=n_samples)
    return np.array([f"{prefix}-{d:07d}" for d in digits])


def generate_sku_codes(n_samples: int) -> np.ndarray:
    """Generate product codes with mixed category prefixes."""
    prefixes = get_random_state().choice(_PREFIXES, size=n_samples, replace=True)
    digits = get_random_state().randint(0, 9_999_999, size=n_samples)
    return np.array([f"{p}-{d:07d}" for p, d in zip(prefixes, digits)])
