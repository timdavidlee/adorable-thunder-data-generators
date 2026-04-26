import numpy as np
import pandas as pd

from adorable_thunder.make.reference_data.cities import CITIES
from adorable_thunder.make.reference_data.street_names import STREET_NAMES


def generate_addresses(n_samples: int, country_code: str | None = None) -> pd.DataFrame:
    """Returns street_address, city, state_province, country_code, postal_code.
    Pass country_code to restrict to cities in a specific country."""
    pool = [c for c in CITIES if c.country_code == country_code] if country_code else CITIES
    if not pool:
        pool = CITIES
    indices: list[int] = np.random.randint(0, len(pool), size=n_samples).tolist()
    sampled = [pool[i] for i in indices]

    street_numbers = np.random.randint(1, 9999, size=n_samples)
    street_names = np.random.choice(STREET_NAMES, size=n_samples, replace=True)
    street_addresses = [f"{num} {name}" for num, name in zip(street_numbers, street_names)]

    df = pd.DataFrame(sampled, columns=["city", "state_province", "country_code", "postal_code"])
    df.insert(0, "street_address", street_addresses)
    return df
