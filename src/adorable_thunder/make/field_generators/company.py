import numpy as np
import pandas as pd
from adorable_thunder.make.reference_data.company_names import COMPANY_NAMES
from adorable_thunder.make.reference_data.company2products import COMPANY_PRODUCT_DF


def generate_company_names(n_samples: int) -> np.ndarray:
    return np.random.choice(COMPANY_NAMES, size=n_samples, replace=True)


def generate_company_and_products(n_samples: int) -> np.ndarray:
    """Generate random company-product pairs.

    generate_company_and_products(10)

    Returns:
        |    | company           | product                        |
        |---:|:------------------|:-------------------------------|
        |  0 | Silven Coatings   | Silven Anti-Corrosion Primer   |
        |  1 | Vantage Equity    | Vantage Mid-Cap Growth         |
        |  2 | Fable Interactive | Fable Fan Art Contest Platform |
        |  3 | Irongate Delivery | Irongate Reverse Logistics     |
        |  4 | Axiom DevOps      | Axiom Deployment Tracker       |
        |  5 | Cinemark Creative | Cinemark Color Grading Suite   |
        |  6 | Coda Robotics     | Coda Vision System             |
        |  7 | Vortex Industrial | Vortex HVAC Modules            |
        |  8 | Quorum Finance    | Quorum Equity Capital Markets  |
        |  9 | Pinnacle Tooling  | Pinnacle Mold Flow Analysis    |
    """
    max_id = COMPANY_PRODUCT_DF.shape[0]
    indices = np.random.randint(0, max_id, size=n_samples)
    sampled_df: pd.DataFrame = COMPANY_PRODUCT_DF.iloc[indices].reset_index(drop=True)
    two_column_array: np.ndarray = sampled_df[["company", "product"]].to_numpy()
    return two_column_array
