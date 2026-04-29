import numpy as np
import pandas as pd

from adorable_thunder.make.common.math import round_weights_and_rebalance
from adorable_thunder.make.field_generators.currency import TOP_CURRENCIES
from adorable_thunder.make.field_generators.identifiers import generate_n_random_uuids
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql, PgColumn

# App-store price points dominate IAP datasets; uniform amounts would be unrealistic.
_PRICE_POINTS = np.array([0.99, 1.99, 2.99, 4.99, 9.99, 19.99, 49.99, 99.99])
_PRICE_WEIGHTS = np.array([0.25, 0.15, 0.20, 0.15, 0.12, 0.08, 0.04, 0.01])

# amount_usd stays canonical; currency_code reflects the user's locale at purchase.
# USD dominant globally because Apple/Google bill many regions in USD; the rest is
# weighted by currency market cap so EUR/CNY/JPY appear most among non-USD locales.
_USD_SHARE = 0.65
_NON_USD = [c for c in TOP_CURRENCIES if c.code != "USD"]
_NON_USD_CODES = np.array([c.code for c in _NON_USD])
_NON_USD_CAPS = np.array([c.market_cap_trillions for c in _NON_USD])
_NON_USD_WEIGHTS = round_weights_and_rebalance(_NON_USD_CAPS / _NON_USD_CAPS.sum(), precision=4)

IAP_PURCHASES_TABLE_NAME = "iap_purchases"


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=IAP_PURCHASES_TABLE_NAME,
        llm_description=(
            "In-app purchases made by retained users. Generated only for installs that reach "
            "day-7 retention and convert to paying. Amounts cluster on standard app-store price "
            "points. store=app_store implies platform=iOS; store=google_play implies "
            "platform=Android."
        ),
        pg_columns=[
            PgColumn(
                name="iap_id",
                data_type="UUID",
                modifiers="PRIMARY KEY",
                llm_description="Unique identifier for the in-app purchase.",
                llm_example_values="'e5f6a7b8-c9d0-1234-efab-567890123456'",
            ),
            PgColumn(
                name="install_id",
                data_type="UUID",
                modifiers="NOT NULL",
                llm_description="Foreign key to the install that made the purchase.",
                llm_example_values="'a1b2c3d4-e5f6-7890-abcd-ef1234567890'",
            ),
            PgColumn(
                name="product_sku",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description=(
                    "App-defined product identifier. Encoded with the price point in cents."
                ),
                llm_example_values="'iap_0099', 'iap_0499', 'iap_9999'",
            ),
            PgColumn(
                name="amount_usd",
                data_type="NUMERIC(18, 2)",
                modifiers="NOT NULL",
                llm_description=(
                    "Purchase amount in USD. Drawn from standard price points: $0.99, $1.99, "
                    "$2.99, $4.99, $9.99, $19.99, $49.99, $99.99."
                ),
                llm_example_values="'0.99', '4.99', '99.99'",
            ),
            PgColumn(
                name="currency_code",
                data_type="VARCHAR(3)",
                modifiers="NOT NULL",
                llm_description=(
                    "ISO 4217 currency the user paid in. ~65% USD; the rest follows the "
                    "user's locale (EUR, CNY, JPY, etc.). amount_usd stays canonical."
                ),
                llm_example_values="'USD', 'EUR', 'JPY', 'CNY'",
            ),
            PgColumn(
                name="store",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description=(
                    "App store of origin. Must align with platform: app_store for iOS, "
                    "google_play for Android."
                ),
                llm_example_values="'app_store', 'google_play'",
            ),
            PgColumn(
                name="purchased_at",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description=(
                    "Date of the purchase. Between 1 and 90 days after first_open_at."
                ),
                llm_example_values="'2024-02-15', '2025-08-30'",
            ),
        ],
    )


def generate_iap_purchases(installs: pd.DataFrame, dataset_end: str) -> pd.DataFrame:
    payers = installs[installs["_is_payer"]].reset_index(drop=True)
    n_payers = len(payers)
    if n_payers == 0:
        return pd.DataFrame(
            columns=[
                "iap_id",
                "install_id",
                "product_sku",
                "amount_usd",
                "currency_code",
                "store",
                "purchased_at",
            ]
        )

    # Lognormal purchase counts give a realistic long-tail of whales without flat distribution.
    n_purchases_per = np.clip(
        np.round(np.random.lognormal(mean=0.5, sigma=0.7, size=n_payers)), 1, 10
    ).astype(int)

    dataset_end_ts = pd.Timestamp(dataset_end)
    rows: list[dict[str, object]] = []

    install_ids = payers["install_id"].to_numpy()
    first_opens = pd.to_datetime(payers["first_open_at"])
    platforms = payers["platform"].to_numpy()

    for i in range(n_payers):
        first_open = first_opens.iloc[i]
        store = "app_store" if platforms[i] == "iOS" else "google_play"
        for _ in range(int(n_purchases_per[i])):
            offset = int(np.random.randint(1, 91))
            purchased_at = first_open + pd.Timedelta(days=offset)
            if purchased_at > dataset_end_ts:
                continue
            amount = float(np.random.choice(_PRICE_POINTS, p=_PRICE_WEIGHTS))
            sku = f"iap_{int(round(amount * 100)):04d}"
            currency_code = (
                "USD"
                if np.random.random() < _USD_SHARE
                else str(np.random.choice(_NON_USD_CODES, p=_NON_USD_WEIGHTS))
            )
            rows.append(
                {
                    "install_id": install_ids[i],
                    "product_sku": sku,
                    "amount_usd": amount,
                    "currency_code": currency_code,
                    "store": store,
                    "purchased_at": purchased_at,
                }
            )

    if not rows:
        return pd.DataFrame(
            columns=[
                "iap_id",
                "install_id",
                "product_sku",
                "amount_usd",
                "currency_code",
                "store",
                "purchased_at",
            ]
        )

    df = pd.DataFrame(rows)
    df.insert(0, "iap_id", generate_n_random_uuids(len(df)))
    return df[
        [
            "iap_id",
            "install_id",
            "product_sku",
            "amount_usd",
            "currency_code",
            "store",
            "purchased_at",
        ]
    ]
