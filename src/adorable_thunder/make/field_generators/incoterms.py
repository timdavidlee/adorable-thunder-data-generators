import numpy as np
from adorable_thunder.make.reference_data.incoterms import INCOTERMS

_CODES = np.array([i[0] for i in INCOTERMS])
_MODES = np.array([i[2] for i in INCOTERMS])
# Weights reflect real-world frequency; FOB and FCA dominate international trade
_WEIGHTS = np.array([0.14, 0.16, 0.07, 0.05, 0.13, 0.04, 0.10, 0.02, 0.18, 0.03, 0.08])


def generate_incoterms_codes(
    n_samples: int, transport_mode: str | None = None
) -> np.ndarray:
    """Sample Incoterms 2020 codes. Pass transport_mode='sea' to restrict to
    sea-only rules (FAS, FOB, CFR, CIF)."""
    if transport_mode is not None:
        pool = _CODES[_MODES == transport_mode]
        return np.random.choice(pool, size=n_samples, replace=True)
    return np.random.choice(_CODES, p=_WEIGHTS, size=n_samples)
