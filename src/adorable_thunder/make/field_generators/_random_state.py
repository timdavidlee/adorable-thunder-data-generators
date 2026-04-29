import numpy as np

# Single seeded stream shared by every generator. Determinism depends on call
# order — never call np.random.* directly; route through get_random_state().
RANDOM_SEED = 42
_NP_RANDOM_STATE = np.random.RandomState(RANDOM_SEED)


def get_random_state() -> np.random.RandomState:
    return _NP_RANDOM_STATE


def reset_random_state(seed: int = RANDOM_SEED) -> None:
    _NP_RANDOM_STATE.seed(seed)
