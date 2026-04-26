import numpy as np

from adorable_thunder.make.field_generators._random_state import get_random_state
from adorable_thunder.make.common.math import round_weights_and_rebalance
from adorable_thunder.make.reference_data.countries import COUNTRIES

_CODES = np.array([c[0] for c in COUNTRIES])
_NAMES = np.array([c[1] for c in COUNTRIES])
_GDPS = np.array([c[2] for c in COUNTRIES], dtype=float)
_WEIGHTS = round_weights_and_rebalance(_GDPS / _GDPS.sum(), precision=4)


def generate_country_codes(n_samples: int) -> np.ndarray:
    return get_random_state().choice(_CODES, p=_WEIGHTS, size=n_samples)


def generate_country_names(n_samples: int) -> np.ndarray:
    return get_random_state().choice(_NAMES, p=_WEIGHTS, size=n_samples)
