import numpy as np
import pandas as pd

from adorable_thunder.make.field_generators._random_state import get_random_state
from adorable_thunder.make.reference_data.carriers import CARRIERS


def generate_carriers(n_samples: int, mode: str | None = None) -> pd.DataFrame:
    """Returns carrier_scac, carrier_name, transport_mode columns.
    Pass mode to restrict to 'road', 'parcel', 'ocean', 'air', or 'rail'."""
    pool = [c for c in CARRIERS if c.primary_mode == mode] if mode else CARRIERS
    if not pool:
        pool = CARRIERS
    indices: list[int] = get_random_state().randint(0, len(pool), size=n_samples).tolist()
    return pd.DataFrame(
        [pool[i] for i in indices],
        columns=["carrier_scac", "carrier_name", "transport_mode"],
    )
