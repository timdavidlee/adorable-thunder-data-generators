import numpy as np
import pandas as pd

from adorable_thunder.make.common.math import round_weights_and_rebalance
from adorable_thunder.make.field_generators.amounts import generate_amounts
from adorable_thunder.make.field_generators.company import generate_company_names
from adorable_thunder.make.field_generators.cost_center import (
    generate_cost_center_names,
)
from adorable_thunder.make.field_generators.currency import TOP_CURRENCIES
from adorable_thunder.make.field_generators.dates import generate_random_dates
from adorable_thunder.make.field_generators.identifiers import (
    generate_n_random_uuids,
    generate_serial_numbers_with_prefix,
)
from adorable_thunder.make.field_generators.users import generate_user_emails
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql, PgColumn

_REQUEST_STATUSES = np.array(["approved", "initiated", "pending", "rejected"])
_REQUEST_STATUS_WEIGHTS = np.array([0.55, 0.20, 0.15, 0.10])

SPEND_CATEGORIES = np.array(
    [
        "IT",
        "PROFESSIONAL_SERVICES",
        "MATERIALS",
        "LOGISTICS",
        "MARKETING",
        "FACILITIES",
        "TRAVEL",
        "OTHER",
    ]
)
_SPEND_CATEGORY_WEIGHTS = np.array([0.25, 0.20, 0.20, 0.10, 0.10, 0.08, 0.05, 0.02])

_NON_USD = [c for c in TOP_CURRENCIES if c.code != "USD"]
_NON_USD_CODES = np.array([c.code for c in _NON_USD])
_NON_USD_CAPS = np.array([c.market_cap_trillions for c in _NON_USD])
_NON_USD_WEIGHTS = round_weights_and_rebalance(_NON_USD_CAPS / _NON_USD_CAPS.sum(), precision=4)


REQUESTS_TABLE_NAME = "requests"


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=REQUESTS_TABLE_NAME,
        llm_description="Purchase requests submitted by employees to initiate a procurement. Each record represents a single spend request that, if approved, triggers the creation of a Purchase Order.",
        pg_columns=[
            PgColumn(
                name="request_id",
                data_type="UUID",
                modifiers="PRIMARY KEY",
                llm_description="Unique identifier for the purchase request.",
                llm_example_values="'a1b2c3d4-e5f6-7890-abcd-ef1234567890'",
            ),
            PgColumn(
                name="document_number",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Human-readable reference number assigned sequentially at submission.",
                llm_example_values="'REQ-00001234', 'REQ-00009999'",
            ),
            PgColumn(
                name="request_date",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description="Date the purchase request was submitted. Must be ≤ po_date on the linked PO.",
                llm_example_values="'2024-03-15', '2025-01-08'",
            ),
            PgColumn(
                name="requester_email",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Corporate email of the employee who submitted the request.",
                llm_example_values="'john.smith@acme.com', 'sarah.jones@acme.com'",
            ),
            PgColumn(
                name="owner_email",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Email of the budget owner or approver responsible for authorising the spend.",
                llm_example_values="'manager.doe@acme.com', 'vp.finance@acme.com'",
            ),
            PgColumn(
                name="supplier_name",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Legal or trading name of the vendor being requested.",
                llm_example_values="'Acme Supplies Ltd', 'Global Tech Solutions Inc'",
            ),
            PgColumn(
                name="amount_usd",
                data_type="NUMERIC(18, 2)",
                modifiers="NOT NULL",
                llm_description="Requested spend amount in USD. Range $1k–$100k (lognormal); enterprise requests can reach $500k+.",
                llm_example_values="'12500.00', '4875.50', '87320.00'",
            ),
            PgColumn(
                name="currency_code",
                data_type="VARCHAR(3)",
                modifiers="NOT NULL",
                llm_description="ISO 4217 currency of the original request. ~70% USD; ~30% non-USD per P2P brief.",
                llm_example_values="'USD', 'EUR', 'GBP', 'JPY'",
            ),
            PgColumn(
                name="cost_center",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Internal cost centre the spend is allocated to. >95% of requests must have a non-null value.",
                llm_example_values="'CC-1001-ENGINEERING', 'CC-2003-MARKETING', 'CC-4010-FINANCE'",
            ),
            PgColumn(
                name="status",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Request lifecycle status. Expected mix: approved ~55%, initiated ~20%, pending ~15%, rejected ~10%.",
                llm_example_values="'approved', 'pending', 'rejected', 'initiated'",
            ),
            PgColumn(
                name="spend_category",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description=(
                    "High-level spend category for the request. Drives category-spend "
                    "analytics and propagates to the PO as supplier_category. Expected "
                    "mix: IT ~25%, PROFESSIONAL_SERVICES ~20%, MATERIALS ~20%, "
                    "LOGISTICS ~10%, MARKETING ~10%, FACILITIES ~8%, TRAVEL ~5%, "
                    "OTHER ~2%."
                ),
                llm_example_values=(
                    "'IT', 'PROFESSIONAL_SERVICES', 'MATERIALS', 'LOGISTICS', "
                    "'MARKETING', 'FACILITIES', 'TRAVEL', 'OTHER'"
                ),
            ),
        ],
    )


def generate_requests(
    n_samples: int,
    start_date: str = "2024-01-01",
    end_date: str = "2025-12-31",
) -> pd.DataFrame:
    amounts_usd = generate_amounts(
        n_samples,
        min_amount=1_000.0,
        max_amount=500_000.0,
        mu=10.0,
        sigma=1.5,
    )

    is_non_usd = np.random.random(n_samples) < 0.30
    currency_codes = np.where(
        is_non_usd,
        np.random.choice(_NON_USD_CODES, p=_NON_USD_WEIGHTS, size=n_samples),
        "USD",
    )

    requester_emails = np.array(generate_user_emails(n_samples))
    owner_emails = np.array(generate_user_emails(n_samples))
    # No self-approval: requester and approver must be different people
    clash = requester_emails == owner_emails
    while clash.any():
        owner_emails[clash] = np.array(generate_user_emails(int(clash.sum())))
        clash = requester_emails == owner_emails

    return pd.DataFrame(
        {
            "request_id": generate_n_random_uuids(n_samples),
            "document_number": generate_serial_numbers_with_prefix(
                n_samples, prefix="REQ-", total_length=12
            ),
            "request_date": generate_random_dates(start_date, end_date, n_samples),
            "requester_email": requester_emails,
            "owner_email": owner_emails,
            "supplier_name": generate_company_names(n_samples),
            "amount_usd": amounts_usd,
            "currency_code": currency_codes,
            "cost_center": generate_cost_center_names(n_samples),
            "status": np.random.choice(
                _REQUEST_STATUSES, p=_REQUEST_STATUS_WEIGHTS, size=n_samples
            ),
            "spend_category": np.random.choice(
                SPEND_CATEGORIES, p=_SPEND_CATEGORY_WEIGHTS, size=n_samples
            ),
        }
    )
