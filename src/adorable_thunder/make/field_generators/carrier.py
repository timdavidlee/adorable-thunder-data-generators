import numpy as np
import pandas as pd
from adorable_thunder.make.reference_data.carriers import CARRIERS

_MODES = np.array([c[2] for c in CARRIERS])


def generate_carriers(n_samples: int, mode: str | None = None) -> pd.DataFrame:
    """Returns carrier_scac, carrier_name, transport_mode columns.
    Pass mode to restrict to 'road', 'parcel', 'ocean', 'air', or 'rail'."""
    pool = [c for c in CARRIERS if c[2] == mode] if mode else CARRIERS
    if not pool:
        pool = CARRIERS
    indices = np.random.randint(0, len(pool), size=n_samples)
    return pd.DataFrame(
        [pool[i] for i in indices],
        columns=["carrier_scac", "carrier_name", "transport_mode"],
    )
