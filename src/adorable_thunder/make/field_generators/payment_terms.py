import numpy as np

from adorable_thunder.make.field_generators._random_state import get_random_state
from adorable_thunder.make.reference_data.payment_terms import PAYMENT_TERMS

_LABELS = np.array([t[1] for t in PAYMENT_TERMS])
# Weights tuned to enterprise procurement frequency; order matches PAYMENT_TERMS
_WEIGHTS = np.array([0.35, 0.20, 0.15, 0.10, 0.07, 0.05, 0.03, 0.02, 0.01, 0.01, 0.005, 0.005])


def generate_payment_terms(n_samples: int) -> np.ndarray:
    return get_random_state().choice(_LABELS, p=_WEIGHTS, size=n_samples)
