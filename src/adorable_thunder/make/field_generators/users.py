from adorable_thunder.make.reference_data.company_users import COMPANY_USER_EMAILS
import numpy as np


def generate_user_emails(n_samples: int) -> np.ndarray:
    return np.random.choice(COMPANY_USER_EMAILS, size=n_samples, replace=True)
