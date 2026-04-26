import numpy as np

from adorable_thunder.make.field_generators._random_state import get_random_state

# E.164 country calling codes for countries in reference_data/countries.py
_CALLING_CODES: dict[str, str] = {
    "US": "+1",
    "CA": "+1",
    "MX": "+52",
    "BR": "+55",
    "AR": "+54",
    "CO": "+57",
    "CL": "+56",
    "GB": "+44",
    "DE": "+49",
    "FR": "+33",
    "IT": "+39",
    "ES": "+34",
    "NL": "+31",
    "CH": "+41",
    "SE": "+46",
    "PL": "+48",
    "BE": "+32",
    "NO": "+47",
    "AT": "+43",
    "DK": "+45",
    "FI": "+358",
    "PT": "+351",
    "RO": "+40",
    "HU": "+36",
    "CZ": "+420",
    "RU": "+7",
    "TR": "+90",
    "IL": "+972",
    "SA": "+966",
    "AE": "+971",
    "ZA": "+27",
    "NG": "+234",
    "EG": "+20",
    "KE": "+254",
    "IN": "+91",
    "CN": "+86",
    "JP": "+81",
    "KR": "+82",
    "AU": "+61",
    "SG": "+65",
    "MY": "+60",
    "TH": "+66",
    "ID": "+62",
    "VN": "+84",
    "PH": "+63",
    "PK": "+92",
    "NZ": "+64",
    "TW": "+886",
}


def generate_phone_numbers(n_samples: int, country_code: str = "US") -> np.ndarray:
    """Generate E.164-format phone numbers for a single country."""
    calling_code = _CALLING_CODES.get(country_code, "+1")
    numbers = get_random_state().randint(1_000_000_000, 9_999_999_999, size=n_samples)
    return np.array([f"{calling_code}{n}" for n in numbers])


def generate_phone_numbers_mixed(n_samples: int, country_codes: np.ndarray) -> np.ndarray:
    """Generate E.164-format phone numbers matching a parallel array of country codes."""
    return np.array(
        [
            f"{_CALLING_CODES.get(cc, '+1')}{get_random_state().randint(1_000_000_000, 9_999_999_999)}"
            for cc in country_codes
        ]
    )
