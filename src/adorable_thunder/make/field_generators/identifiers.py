from uuid import uuid4

import numpy as np


def generate_n_random_uuids(n: int) -> np.ndarray:
    """Generates n random UUIDs.
    Args:
        n: The number of random UUIDs to generate
    Returns:
        A numpy array containing n random UUIDs as strings
    """
    return np.array([str(uuid4()) for _ in range(n)])


def generate_serial_numbers_with_prefix(
    n: int, prefix: str = "SN", total_length: int = 12
) -> np.ndarray:
    """Generates n serial numbers with a specified prefix and total length.
    Args:
        n: The number of serial numbers to generate
        prefix: The prefix for each serial number
        total_length: The total length of each serial number, including the prefix
    Returns:
        A numpy array containing n serial numbers as strings
    """
    if len(prefix) >= total_length:
        raise ValueError("Prefix length must be less than total length")
    num_digits = total_length - len(prefix)
    max_number = 10**num_digits - 1
    random_numbers = np.random.randint(0, max_number + 1, size=n)
    serial_numbers = [f"{prefix}{str(num).zfill(num_digits)}" for num in random_numbers]
    return np.array(serial_numbers)
