import numpy as np

from adorable_thunder.make.field_generators._random_state import get_random_state
from adorable_thunder.make.reference_data.company_users import COMPANY_USER_EMAILS


def generate_user_emails(n_samples: int) -> np.ndarray:
    return get_random_state().choice(COMPANY_USER_EMAILS, size=n_samples, replace=True)
