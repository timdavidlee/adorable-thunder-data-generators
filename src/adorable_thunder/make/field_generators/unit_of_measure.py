import numpy as np

from adorable_thunder.make.field_generators._random_state import get_random_state
from adorable_thunder.make.reference_data.units_of_measure import UNITS_OF_MEASURE

_CODES = np.array([u[0] for u in UNITS_OF_MEASURE])
_CATEGORIES = np.array([u[2] for u in UNITS_OF_MEASURE])


def generate_uom_codes(n_samples: int, category: str | None = None) -> np.ndarray:
    """Sample UOM codes. Pass category to restrict to 'count', 'weight', 'volume',
    'length', 'area', 'time', 'service', or 'digital'."""
    if category is not None:
        pool = _CODES[_CATEGORIES == category]
    else:
        pool = _CODES
    return get_random_state().choice(pool, size=n_samples, replace=True)
