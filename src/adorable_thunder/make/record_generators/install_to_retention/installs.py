import numpy as np
import pandas as pd

from adorable_thunder.make.field_generators.country import generate_country_codes
from adorable_thunder.make.field_generators.dates import generate_random_dates
from adorable_thunder.make.field_generators.identifiers import (
    generate_n_random_uuids,
    generate_serial_numbers_with_prefix,
)
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql, PgColumn

PLATFORMS = np.array(["iOS", "Android"])
_PLATFORM_WEIGHTS = np.array([0.35, 0.65])

SOURCES = np.array(
    [
        "ORGANIC_SEARCH",
        "PAID_SEARCH",
        "PAID_SOCIAL",
        "INFLUENCER",
        "REFERRAL",
        "CROSS_PROMO",
        "WEB_TO_APP",
    ]
)
_SOURCE_WEIGHTS = np.array([0.30, 0.18, 0.22, 0.06, 0.12, 0.08, 0.04])

_PAID_SOURCES = ("PAID_SEARCH", "PAID_SOCIAL", "INFLUENCER", "CROSS_PROMO")

_FIRST_OPEN_RATE_ORGANIC = 0.80
_FIRST_OPEN_RATE_PAID = 0.70
_ACCOUNT_CREATION_RATE = 0.70
# Tutorial completion is gated on having an account — the activation flow requires
# auth before onboarding can finish. 0.85 of accounts × 0.70 first-open-to-account
# rate ≈ 60% of first-opens, within the brief's 50-75% band.
_TUTORIAL_COMPLETION_AMONG_ACCOUNTS = 0.85

# Retention probabilities, conditioned on tutorial completion. Tutorial completers
# retain at 3-5x the rate of non-completers — see brief's activation gate.
_COMPLETER_D1 = 0.50
_NON_COMPLETER_D1 = 0.12
_COMPLETER_D7 = 0.22
_NON_COMPLETER_D7 = 0.05
_COMPLETER_D30 = 0.10
_NON_COMPLETER_D30 = 0.02

# Among d7-retained users, a fraction become paying — yields ~1-3% overall paying.
_PAYING_RATE_AMONG_D7_RETAINED = 0.18

INSTALLS_TABLE_NAME = "installs"


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=INSTALLS_TABLE_NAME,
        llm_description=(
            "Mobile app installs — top of the I2R funnel. Platform mix iOS ~35%, "
            "Android ~65%. First-open rate 70-90% for organic sources and 60-80% for "
            "paid sources. campaign_id is populated only for paid acquisition sources."
        ),
        pg_columns=[
            PgColumn(
                name="install_id",
                data_type="UUID",
                modifiers="PRIMARY KEY",
                llm_description="Unique identifier for the install.",
                llm_example_values="'a1b2c3d4-e5f6-7890-abcd-ef1234567890'",
            ),
            PgColumn(
                name="device_id",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Device-level fingerprint identifying a phone or tablet.",
                llm_example_values="'DVC-00012345'",
            ),
            PgColumn(
                name="platform",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="OS platform. Expected mix: iOS ~35%, Android ~65%.",
                llm_example_values="'iOS', 'Android'",
            ),
            PgColumn(
                name="source",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description=(
                    "Acquisition channel. Organic: ORGANIC_SEARCH, REFERRAL, WEB_TO_APP. "
                    "Paid: PAID_SEARCH, PAID_SOCIAL, INFLUENCER, CROSS_PROMO."
                ),
                llm_example_values="'ORGANIC_SEARCH', 'PAID_SOCIAL', 'REFERRAL'",
            ),
            PgColumn(
                name="campaign_id",
                data_type="UUID",
                modifiers="",
                llm_description=(
                    "Campaign that drove the install. Populated for paid sources, "
                    "NULL for organic and referral."
                ),
                llm_example_values="'b2c3d4e5-f6a7-8901-bcde-f23456789012', NULL",
            ),
            PgColumn(
                name="country_code",
                data_type="VARCHAR(2)",
                modifiers="NOT NULL",
                llm_description="ISO 3166-1 alpha-2 country code of the install.",
                llm_example_values="'US', 'GB', 'IN', 'BR'",
            ),
            PgColumn(
                name="installed_at",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description="Date the app was installed on the device.",
                llm_example_values="'2024-02-01', '2025-06-15'",
            ),
            PgColumn(
                name="first_open_at",
                data_type="DATE",
                modifiers="",
                llm_description=(
                    "Date of the first app launch after install. NULL when the install "
                    "never opened. ~80% open for organic, ~70% open for paid."
                ),
                llm_example_values="'2024-02-01', NULL",
            ),
        ],
    )


def generate_installs(
    n_samples: int,
    start_date: str = "2024-01-01",
    end_date: str = "2025-12-31",
) -> pd.DataFrame:
    install_ids = generate_n_random_uuids(n_samples)
    device_ids = generate_serial_numbers_with_prefix(
        n_samples, prefix="DVC-", total_length=12
    )
    platforms = np.random.choice(PLATFORMS, p=_PLATFORM_WEIGHTS, size=n_samples)
    sources = np.random.choice(SOURCES, p=_SOURCE_WEIGHTS, size=n_samples)

    is_paid = np.isin(sources, _PAID_SOURCES)
    paid_campaign_ids = generate_n_random_uuids(n_samples)
    campaign_ids: np.ndarray = np.full(n_samples, None, dtype=object)
    campaign_ids[is_paid] = paid_campaign_ids[is_paid]

    country_codes = generate_country_codes(n_samples)
    installed_at = generate_random_dates(start_date, end_date, n_samples)

    first_open_p = np.where(is_paid, _FIRST_OPEN_RATE_PAID, _FIRST_OPEN_RATE_ORGANIC)
    has_first_open = np.random.random(n_samples) < first_open_p

    first_open_offsets = np.random.randint(0, 2, size=n_samples)
    first_open_full = installed_at + pd.to_timedelta(first_open_offsets, unit="D")
    first_open_at = first_open_full.where(pd.Series(has_first_open))

    has_account = has_first_open & (np.random.random(n_samples) < _ACCOUNT_CREATION_RATE)
    tutorial_completed = has_account & (
        np.random.random(n_samples) < _TUTORIAL_COMPLETION_AMONG_ACCOUNTS
    )

    # Independent uniforms with conditional thresholds give the right marginals while
    # enforcing monotonicity: anyone retained at d30 was retained at d7 and d1.
    d1_p = np.where(tutorial_completed, _COMPLETER_D1, _NON_COMPLETER_D1)
    d7_p = np.where(tutorial_completed, _COMPLETER_D7, _NON_COMPLETER_D7)
    d30_p = np.where(tutorial_completed, _COMPLETER_D30, _NON_COMPLETER_D30)

    u1 = np.random.random(n_samples)
    u7 = np.random.random(n_samples)
    u30 = np.random.random(n_samples)

    retained_d1 = has_first_open & (u1 < d1_p)
    retained_d7 = retained_d1 & (u7 < d7_p / d1_p)
    retained_d30 = retained_d7 & (u30 < d30_p / d7_p)

    is_payer = retained_d7 & (np.random.random(n_samples) < _PAYING_RATE_AMONG_D7_RETAINED)

    return pd.DataFrame(
        {
            "install_id": install_ids,
            "device_id": device_ids,
            "platform": platforms,
            "source": sources,
            "campaign_id": campaign_ids,
            "country_code": country_codes,
            "installed_at": installed_at,
            "first_open_at": first_open_at,
            "_has_first_open": has_first_open,
            "_tutorial_completed": tutorial_completed,
            "_has_account": has_account,
            "_retained_d1": retained_d1,
            "_retained_d7": retained_d7,
            "_retained_d30": retained_d30,
            "_is_payer": is_payer,
        }
    )
