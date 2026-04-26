import numpy as np
from adorable_thunder.make.reference_data.cost_centers import COST_CENTERS


def generate_cost_center_names(n_samples: int) -> np.ndarray:
    return np.random.choice(COST_CENTERS, size=n_samples, replace=True)
