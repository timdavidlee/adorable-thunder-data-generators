import numpy as np

from adorable_thunder.make.reference_data.person_names import FIRST_NAMES, LAST_NAMES


def generate_first_names(n_samples: int) -> np.ndarray:
    return np.random.choice(FIRST_NAMES, size=n_samples, replace=True)


def generate_last_names(n_samples: int) -> np.ndarray:
    return np.random.choice(LAST_NAMES, size=n_samples, replace=True)


def generate_full_names(n_samples: int) -> np.ndarray:
    first = generate_first_names(n_samples)
    last = generate_last_names(n_samples)
    return np.array([f"{f} {ln}" for f, ln in zip(first, last)])
