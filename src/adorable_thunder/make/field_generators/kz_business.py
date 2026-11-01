from datetime import date

import numpy as np

from adorable_thunder.make.field_generators._random_state import get_random_state

_SURNAMES = np.array(
    [
        "Abenov", "Akhmetova", "Baimukhanov", "Bekova", "Dzhaksybekov", "Ermekova", "Iskakov",
        "Kassymova", "Kim", "Li", "Mukanov", "Nurlanova", "Omarov", "Petrova", "Sadykova",
        "Seitkali", "Smagulov", "Tulegenova", "Utepov", "Zhumabayeva", "Ivanov", "Karimov",
    ]
)  # fmt: skip
_INITIALS = np.array(list("ABDEGKMNRSTZ"))
_STEMS = np.array(
    [
        "Altyn", "Aqsu", "Arman", "Baiterek", "Dala", "Kok Tobe", "Nur", "Orda", "Samal",
        "Saryarka", "Shanyrak", "Steppe", "Tau", "Tulpar", "Zhuldyz", "Alatau", "Ertis", "Kerey",
    ]
)  # fmt: skip
_SECTOR_WORDS: dict[str, list[str]] = {
    "retail_trade": ["Market", "Trade", "Shop"],
    "wholesale_import": ["Import", "Distribution", "Trading"],
    "food_service": ["Food", "Cafe", "Catering"],
    "construction": ["Build", "Stroy", "Construction"],
    "transport_logistics": ["Logistics", "Trans", "Cargo"],
    "agriculture": ["Agro", "Farm", "Grain"],
    "professional_services": ["Consulting", "Audit", "Partners"],
    "manufacturing": ["Plant", "Industries", "Manufacturing"],
    "it_services": ["Tech", "Soft", "Digital"],
    "beauty_health": ["Med", "Beauty", "Clinic"],
}
BANK_CODE = "999"  # not assigned to any real Kazakh bank


def generate_kz_legal_names(
    n_samples: int, legal_forms: np.ndarray, industries: np.ndarray
) -> np.ndarray:
    """IE clients get 'IE Surname X.'; LLP clients get '<Stem> <Sector word> LLP'."""
    rng = get_random_state()
    surnames = rng.choice(_SURNAMES, size=n_samples)
    initials = rng.choice(_INITIALS, size=n_samples)
    stems = rng.choice(_STEMS, size=n_samples)
    names: list[str] = []
    for i in range(n_samples):
        if legal_forms[i] == "IE":
            names.append(f"IE {surnames[i]} {initials[i]}.")
        else:
            word = str(rng.choice(_SECTOR_WORDS[str(industries[i])]))
            names.append(f"{stems[i]} {word} LLP")
    return np.array(names)


def generate_kz_bins(
    n_samples: int, registered_on: list[date], legal_forms: np.ndarray
) -> np.ndarray:
    """12-digit business IDs: YYMM of registration, entity-type digit, then a unique serial."""
    serials = get_random_state().permutation(n_samples)
    return np.array(
        [
            f"{d:%y%m}{4 if form == 'LLP' else 6}0{int(s):06d}"
            for d, form, s in zip(registered_on, legal_forms, serials, strict=True)
        ]
    )


def generate_kz_ibans(n_samples: int) -> np.ndarray:
    """KZ-format IBANs (20 chars) under a fictional bank code; unique within the call."""
    check_digits = get_random_state().randint(10, 100, size=n_samples)
    serials = get_random_state().permutation(n_samples) + 1_000_000
    return np.array(
        [f"KZ{c}{BANK_CODE}{int(s):013d}" for c, s in zip(check_digits, serials, strict=True)]
    )
