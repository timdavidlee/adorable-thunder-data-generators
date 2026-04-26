from typing import NamedTuple


class Country(NamedTuple):
    iso2_code: str
    country_name: str
    gdp_usd_trillions: float


# Ordered by GDP descending; gdp_usd_trillions used for weighted sampling in field generators
COUNTRIES: list[Country] = [
    Country("US", "United States", 27.4),
    Country("CN", "China", 17.7),
    Country("DE", "Germany", 4.5),
    Country("JP", "Japan", 4.2),
    Country("IN", "India", 3.7),
    Country("GB", "United Kingdom", 3.1),
    Country("FR", "France", 3.0),
    Country("BR", "Brazil", 2.1),
    Country("IT", "Italy", 2.1),
    Country("CA", "Canada", 2.1),
    Country("RU", "Russia", 1.9),
    Country("MX", "Mexico", 1.8),
    Country("KR", "South Korea", 1.7),
    Country("AU", "Australia", 1.7),
    Country("ES", "Spain", 1.6),
    Country("ID", "Indonesia", 1.4),
    Country("NL", "Netherlands", 1.1),
    Country("TR", "Turkey", 1.1),
    Country("SA", "Saudi Arabia", 1.1),
    Country("CH", "Switzerland", 0.9),
    Country("PL", "Poland", 0.8),
    Country("BE", "Belgium", 0.6),
    Country("SE", "Sweden", 0.6),
    Country("AR", "Argentina", 0.6),
    Country("NO", "Norway", 0.6),
    Country("AT", "Austria", 0.5),
    Country("AE", "United Arab Emirates", 0.5),
    Country("SG", "Singapore", 0.5),
    Country("IL", "Israel", 0.5),
    Country("NG", "Nigeria", 0.5),
    Country("TH", "Thailand", 0.5),
    Country("ZA", "South Africa", 0.4),
    Country("MY", "Malaysia", 0.4),
    Country("DK", "Denmark", 0.4),
    Country("PH", "Philippines", 0.4),
    Country("VN", "Vietnam", 0.4),
    Country("EG", "Egypt", 0.4),
    Country("CL", "Chile", 0.3),
    Country("CZ", "Czech Republic", 0.3),
    Country("CO", "Colombia", 0.3),
    Country("FI", "Finland", 0.3),
    Country("PT", "Portugal", 0.3),
    Country("RO", "Romania", 0.3),
    Country("PK", "Pakistan", 0.3),
    Country("HU", "Hungary", 0.2),
    Country("NZ", "New Zealand", 0.2),
    Country("KE", "Kenya", 0.1),
]
