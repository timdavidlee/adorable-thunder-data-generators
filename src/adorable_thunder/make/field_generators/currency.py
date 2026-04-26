from enum import StrEnum

import numpy as np
from pydantic import BaseModel

from adorable_thunder.make.common.math import round_weights_and_rebalance


class PopularCurrency(BaseModel):
    code: str
    name: str
    market_cap_trillions: float


TOP_CURRENCIES = [
    PopularCurrency(code="USD", name="US Dollar", market_cap_trillions=28.8),
    PopularCurrency(code="EUR", name="Euro (Eurozone)", market_cap_trillions=15.0),
    PopularCurrency(code="CNY", name="Chinese Yuan", market_cap_trillions=18.5),
    PopularCurrency(code="JPY", name="Japanese Yen", market_cap_trillions=4.1),
    PopularCurrency(code="INR", name="Indian Rupee", market_cap_trillions=3.9),
    PopularCurrency(code="GBP", name="British Pound", market_cap_trillions=3.1),
    PopularCurrency(code="BRL", name="Brazilian Real", market_cap_trillions=2.2),
    PopularCurrency(code="CAD", name="Canadian Dollar", market_cap_trillions=2.1),
    PopularCurrency(code="RUB", name="Russian Ruble", market_cap_trillions=2.0),
    PopularCurrency(code="KRW", name="South Korean Won", market_cap_trillions=1.8),
    PopularCurrency(code="AUD", name="Australian Dollar", market_cap_trillions=1.7),
    PopularCurrency(code="MXN", name="Mexican Peso", market_cap_trillions=1.8),
    PopularCurrency(code="IDR", name="Indonesian Rupiah", market_cap_trillions=1.4),
    PopularCurrency(code="SAR", name="Saudi Riyal", market_cap_trillions=1.1),
    PopularCurrency(code="TRY", name="Turkish Lira", market_cap_trillions=1.1),
    PopularCurrency(code="CHF", name="Swiss Franc", market_cap_trillions=0.9),
    PopularCurrency(code="TWD", name="Taiwan Dollar", market_cap_trillions=0.8),
    PopularCurrency(code="PLN", name="Polish Zloty", market_cap_trillions=0.8),
    PopularCurrency(code="SEK", name="Swedish Krona", market_cap_trillions=0.6),
    PopularCurrency(code="NOK", name="Norwegian Krone", market_cap_trillions=0.6),
    PopularCurrency(code="AED", name="UAE Dirham", market_cap_trillions=0.5),
    PopularCurrency(code="THB", name="Thai Baht", market_cap_trillions=0.5),
    PopularCurrency(code="ILS", name="Israeli Shekel", market_cap_trillions=0.5),
    PopularCurrency(code="ZAR", name="South African Rand", market_cap_trillions=0.4),
    PopularCurrency(code="DKK", name="Danish Krone", market_cap_trillions=0.4),
]


class CurrencyEnum(StrEnum):
    USD = "USD"
    EUR = "EUR"
    CNY = "CNY"
    JPY = "JPY"
    INR = "INR"
    GBP = "GBP"
    BRL = "BRL"
    CAD = "CAD"
    RUB = "RUB"
    KRW = "KRW"
    AUD = "AUD"
    MXN = "MXN"
    IDR = "IDR"
    SAR = "SAR"
    TRY = "TRY"
    CHF = "CHF"
    TWD = "TWD"
    PLN = "PLN"
    SEK = "SEK"
    NOK = "NOK"
    AED = "AED"
    THB = "THB"
    ILS = "ILS"
    ZAR = "ZAR"
    DKK = "DKK"


USD_RATES: dict[str, float] = {
    "USD": 1.0,
    "EUR": 0.92,
    "GBP": 0.79,
    "JPY": 149.0,
    "CAD": 1.36,
    "AUD": 1.53,
    "CHF": 0.89,
    "CNY": 7.24,
    "INR": 83.5,
    "MXN": 17.1,
    "BRL": 4.97,
    "KRW": 1325.0,
    "SGD": 1.34,
    "HKD": 7.82,
    "NOK": 10.6,
    "SEK": 10.4,
    "DKK": 6.89,
    "NZD": 1.63,
    "ZAR": 18.6,
    "TRY": 32.0,
    "AED": 3.67,
    "SAR": 3.75,
    "THB": 35.1,
    "IDR": 15700.0,
    "MYR": 4.72,
    "PHP": 56.5,
    "PKR": 278.0,
    "EGP": 30.9,
    "CZK": 23.2,
    "PLN": 4.02,
    "HUF": 357.0,
    "RUB": 85.0,
    "TWD": 30.5,
    "ILS": 3.09,
}


def usd_to(amount: float, currency_code: str) -> float | None:
    """Convert USD to another currency. Returns None if code is unknown."""
    rate = USD_RATES.get(currency_code.upper())
    if rate is None:
        return None
    return round(amount * rate, 2)


class CurrencyGenerator:
    def __init__(self) -> None:
        self.currencies = TOP_CURRENCIES
        self.currency_codes = [currency.code for currency in self.currencies]
        self.market_caps = np.array([currency.market_cap_trillions for currency in self.currencies])
        self.weights = round_weights_and_rebalance(
            self.market_caps / self.market_caps.sum(),
            precision=4,
        )

    def generate_currency_entries(self, n_samples: int = 10) -> np.ndarray:
        return np.random.choice(self.currency_codes, p=self.weights, size=n_samples)
