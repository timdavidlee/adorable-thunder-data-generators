import numpy as np

# this is to be shared across all generators to ensure reproducibility and consistency in the generated data
RANDOM_SEED = 42
NP_RANDOM_STATE = np.random.RandomState(RANDOM_SEED)


def get_random_state(frozen: bool = False) -> np.random.RandomState:
    if frozen:
        return NP_RANDOM_STATE
    return np.random.RandomState()
