import numpy as np
import pandas as pd

from adorable_thunder.make.common.math import round_weights_and_rebalance
from adorable_thunder.make.field_generators.company import generate_company_names
from adorable_thunder.make.field_generators.currency import TOP_CURRENCIES
from adorable_thunder.make.field_generators.dates import generate_random_dates
from adorable_thunder.make.field_generators.identifiers import (
    generate_n_random_uuids,
    generate_serial_numbers_with_prefix,
)
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql, PgColumn

PLAN_TIERS = np.array(["Starter", "Professional", "Business", "Enterprise"])
_PLAN_WEIGHTS = np.array([0.25, 0.50, 0.18, 0.07])

_TIER_MRR_BOUNDS: dict[str, tuple[float, float]] = {
    "Starter": (10.0, 100.0),
    "Professional": (100.0, 2_000.0),
    "Business": (2_000.0, 10_000.0),
    "Enterprise": (10_000.0, 100_000.0),
}

_STATUSES = np.array(["active", "churned", "paused"])
_STATUS_WEIGHTS = np.array([0.75, 0.20, 0.05])

_NON_USD = [c for c in TOP_CURRENCIES if c.code != "USD"]
_NON_USD_CODES = np.array([c.code for c in _NON_USD])
_NON_USD_CAPS = np.array([c.market_cap_trillions for c in _NON_USD])
_NON_USD_WEIGHTS = round_weights_and_rebalance(_NON_USD_CAPS / _NON_USD_CAPS.sum(), precision=4)

SUBSCRIPTIONS_TABLE_NAME = "subscriptions"


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=SUBSCRIPTIONS_TABLE_NAME,
        llm_description=(
            "Recurring revenue subscriptions. MRR amount must match plan tier — Starter $10–$100, "
            "Professional $100–$2k, Business $2k–$10k, Enterprise $10k+. Annual billing for "
            "Business/Enterprise; monthly or annual for Professional; monthly for Starter."
        ),
        pg_columns=[
            PgColumn(
                name="sub_id",
                data_type="UUID",
                modifiers="PRIMARY KEY",
                llm_description="Unique identifier for the subscription.",
                llm_example_values="'a1b2c3d4-e5f6-7890-abcd-ef1234567890'",
            ),
            PgColumn(
                name="sub_number",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Human-readable subscription reference number.",
                llm_example_values="'SUB-00001234', 'SUB-00009999'",
            ),
            PgColumn(
                name="customer_name",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Legal or trading name of the subscribing customer.",
                llm_example_values="'Widgets Corp', 'Northstar Logistics LLC'",
            ),
            PgColumn(
                name="plan_tier",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description=(
                    "Subscription plan tier. Starter ~25%, Professional ~50%, "
                    "Business ~18%, Enterprise ~7%."
                ),
                llm_example_values="'Starter', 'Professional', 'Business', 'Enterprise'",
            ),
            PgColumn(
                name="billing_cycle_months",
                data_type="INTEGER",
                modifiers="NOT NULL",
                llm_description=(
                    "Length of one billing period in months. 1 = monthly, 12 = annual. "
                    "Business/Enterprise are annual; Starter is monthly; Professional is mixed."
                ),
                llm_example_values="'1', '12'",
            ),
            PgColumn(
                name="mrr_usd",
                data_type="NUMERIC(18, 2)",
                modifiers="NOT NULL",
                llm_description=(
                    "Monthly recurring revenue in USD. Must fall within the plan tier band."
                ),
                llm_example_values="'49.00', '850.00', '6500.00', '42000.00'",
            ),
            PgColumn(
                name="currency_code",
                data_type="VARCHAR(3)",
                modifiers="NOT NULL",
                llm_description="ISO 4217 currency the subscription is billed in. ~70% USD.",
                llm_example_values="'USD', 'EUR', 'GBP', 'CAD'",
            ),
            PgColumn(
                name="start_date",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description="Date the subscription was activated.",
                llm_example_values="'2024-02-01', '2025-03-10'",
            ),
            PgColumn(
                name="end_date",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description=(
                    "Date the current term ends. start_date + term_months. Renewals extend "
                    "via a new renewal record, not by mutating this field."
                ),
                llm_example_values="'2025-02-01', '2026-03-10'",
            ),
            PgColumn(
                name="churn_date",
                data_type="DATE",
                modifiers="",
                llm_description=(
                    "Date the subscription was cancelled. Populated only when status='churned'. "
                    "No invoices or renewals should exist with date > churn_date."
                ),
                llm_example_values="'2025-04-15', NULL",
            ),
            PgColumn(
                name="pause_date",
                data_type="DATE",
                modifiers="",
                llm_description=(
                    "Date the subscription was paused (billing suspended). Populated only when "
                    "status='paused'. No invoices or usage with date > pause_date."
                ),
                llm_example_values="'2025-06-15', NULL",
            ),
            PgColumn(
                name="auto_renew",
                data_type="BOOLEAN",
                modifiers="NOT NULL",
                llm_description="Whether the subscription auto-renews at end_date.",
                llm_example_values="'true', 'false'",
            ),
            PgColumn(
                name="status",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description=(
                    "Subscription lifecycle status. Expected mix: active ~75%, churned ~20%, "
                    "paused ~5%."
                ),
                llm_example_values="'active', 'churned', 'paused'",
            ),
        ],
    )


def _sample_mrr_for_tier(plan_tiers: np.ndarray) -> np.ndarray:
    n = len(plan_tiers)
    out = np.zeros(n, dtype=float)
    for tier, (lo, hi) in _TIER_MRR_BOUNDS.items():
        mask = plan_tiers == tier
        if not mask.any():
            continue
        # Lognormal within band, then clip — gives a rightward skew within each tier.
        mu = np.log((lo * hi) ** 0.5)
        sigma = 0.5
        sampled = np.random.lognormal(mean=mu, sigma=sigma, size=int(mask.sum()))
        out[mask] = np.clip(sampled, lo, hi)
    return np.round(out, 2)


def _assign_billing_cycle(plan_tiers: np.ndarray) -> np.ndarray:
    n = len(plan_tiers)
    cycles = np.full(n, 1, dtype=int)
    annual_only = np.isin(plan_tiers, ["Business", "Enterprise"])
    cycles[annual_only] = 12

    pro_mask = plan_tiers == "Professional"
    if pro_mask.any():
        # ~40% of Professional subscriptions bill annually.
        pro_cycles = np.where(np.random.random(int(pro_mask.sum())) < 0.40, 12, 1)
        cycles[pro_mask] = pro_cycles
    return cycles


def _assign_term_months(billing_cycles: np.ndarray) -> np.ndarray:
    n = len(billing_cycles)
    terms = np.full(n, 12, dtype=int)
    annual_mask = billing_cycles == 12
    if annual_mask.any():
        terms[annual_mask] = np.random.choice(
            [12, 24, 36], p=[0.65, 0.25, 0.10], size=int(annual_mask.sum())
        )
    return terms


def generate_subscriptions(
    n_samples: int,
    start_date: str = "2024-01-01",
    end_date: str = "2025-12-31",
) -> pd.DataFrame:
    plan_tiers = np.random.choice(PLAN_TIERS, p=_PLAN_WEIGHTS, size=n_samples)
    billing_cycles = _assign_billing_cycle(plan_tiers)
    term_months = _assign_term_months(billing_cycles)
    mrr_usd = _sample_mrr_for_tier(plan_tiers)

    is_non_usd = np.random.random(n_samples) < 0.30
    currency_codes = np.where(
        is_non_usd,
        np.random.choice(_NON_USD_CODES, p=_NON_USD_WEIGHTS, size=n_samples),
        "USD",
    )

    sub_start_dates = generate_random_dates(start_date, end_date, n_samples)
    sub_end_dates = pd.Series(sub_start_dates + pd.to_timedelta(term_months * 30, unit="D"))

    statuses = np.random.choice(_STATUSES, p=_STATUS_WEIGHTS, size=n_samples)
    dataset_end = pd.Timestamp(end_date)

    churn_dates = pd.Series([pd.NaT] * n_samples, dtype="datetime64[ns]")
    pause_dates = pd.Series([pd.NaT] * n_samples, dtype="datetime64[ns]")

    def _sample_stop_dates(idx: np.ndarray) -> pd.DatetimeIndex:
        starts = sub_start_dates.iloc[idx].to_numpy()
        ends = np.minimum(sub_end_dates.iloc[idx].to_numpy(), dataset_end.to_numpy())
        spans = (ends - starts).astype("timedelta64[D]").astype(int)
        spans = np.clip(spans, 1, None)
        offsets = np.array(
            [np.random.randint(1, int(s) + 1) for s in spans.tolist()], dtype=int
        )
        return pd.to_datetime(starts) + pd.to_timedelta(offsets, unit="D")

    churn_mask = statuses == "churned"
    if churn_mask.any():
        churn_idx = np.where(churn_mask)[0]
        churn_dates.iloc[churn_idx] = _sample_stop_dates(churn_idx)

    pause_mask = statuses == "paused"
    if pause_mask.any():
        pause_idx = np.where(pause_mask)[0]
        pause_dates.iloc[pause_idx] = _sample_stop_dates(pause_idx)

    auto_renew = np.random.random(n_samples) < 0.60

    return pd.DataFrame(
        {
            "sub_id": generate_n_random_uuids(n_samples),
            "sub_number": generate_serial_numbers_with_prefix(
                n_samples, prefix="SUB-", total_length=12
            ),
            "customer_name": generate_company_names(n_samples),
            "plan_tier": plan_tiers,
            "billing_cycle_months": billing_cycles,
            "mrr_usd": mrr_usd,
            "currency_code": currency_codes,
            "start_date": sub_start_dates,
            "end_date": sub_end_dates,
            "churn_date": churn_dates,
            "pause_date": pause_dates,
            "auto_renew": auto_renew,
            "status": statuses,
            "_term_months": term_months,
        }
    )
