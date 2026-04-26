import numpy as np

from adorable_thunder.make.field_generators._random_state import get_random_state
from adorable_thunder.make.reference_data.cost_centers import COST_CENTERS


def generate_cost_center_names(n_samples: int) -> np.ndarray:
    return get_random_state().choice(COST_CENTERS, size=n_samples, replace=True)
