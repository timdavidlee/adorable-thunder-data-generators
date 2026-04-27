import numpy as np
import pandas as pd

from adorable_thunder.make.field_generators.company import generate_company_names
from adorable_thunder.make.field_generators.dates import generate_random_dates
from adorable_thunder.make.field_generators.identifiers import (
    generate_n_random_uuids,
    generate_serial_numbers_with_prefix,
)
from adorable_thunder.make.field_generators.person import generate_first_names, generate_last_names
from adorable_thunder.make.field_generators.phone import generate_phone_numbers
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql, PgColumn

_SOURCES = np.array(
    [
        "WEB_FORM",
        "PAID_SEARCH",
        "CONTENT_DOWNLOAD",
        "REFERRAL",
        "TRADE_SHOW",
        "COLD_OUTREACH",
        "PARTNER",
        "WEBINAR",
    ]
)
_SOURCE_WEIGHTS = np.array([0.20, 0.15, 0.15, 0.15, 0.10, 0.10, 0.10, 0.05])

LEADS_TABLE_NAME = "leads"


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=LEADS_TABLE_NAME,
        llm_description="Raw inbound leads from acquisition channels. ~20% become contacts; the rest are disqualified or stall. Source distribution should span all channels — single-source dominance (>60%) is unrealistic.",
        pg_columns=[
            PgColumn(
                name="lead_id",
                data_type="UUID",
                modifiers="PRIMARY KEY",
                llm_description="Unique identifier for the lead.",
                llm_example_values="'a1b2c3d4-e5f6-7890-abcd-ef1234567890'",
            ),
            PgColumn(
                name="lead_number",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Human-readable sequential lead reference.",
                llm_example_values="'LDR-000001', 'LDR-009999'",
            ),
            PgColumn(
                name="first_name",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="First name of the lead contact.",
                llm_example_values="'James', 'Maria', 'Chen'",
            ),
            PgColumn(
                name="last_name",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Last name of the lead contact.",
                llm_example_values="'Smith', 'Garcia', 'Wang'",
            ),
            PgColumn(
                name="email",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Lead's business email, derived from name and company domain.",
                llm_example_values="'james.smith@acmecorp.com', 'maria.garcia@globaltech.com'",
            ),
            PgColumn(
                name="phone",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Lead's phone number in E.164 format.",
                llm_example_values="'+14155551234', '+447911123456'",
            ),
            PgColumn(
                name="company",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Company the lead works for.",
                llm_example_values="'Acme Corp', 'Global Tech Solutions'",
            ),
            PgColumn(
                name="source",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Acquisition channel. Mix: WEB_FORM ~20%, PAID_SEARCH ~15%, CONTENT_DOWNLOAD ~15%, REFERRAL ~15%, TRADE_SHOW ~10%, COLD_OUTREACH ~10%, PARTNER ~10%, WEBINAR ~5%.",
                llm_example_values="'WEB_FORM', 'REFERRAL', 'TRADE_SHOW', 'WEBINAR'",
            ),
            PgColumn(
                name="created_date",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description="Date the lead was captured. Must be ≤ any downstream contact or opportunity date.",
                llm_example_values="'2024-01-15', '2024-09-01'",
            ),
            PgColumn(
                name="status",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Lead lifecycle status. ~20% converted, ~10% qualified (still being worked), ~35% disqualified, ~35% new.",
                llm_example_values="'new', 'qualified', 'disqualified', 'converted'",
            ),
        ],
    )


def generate_leads(
    n_samples: int,
    start_date: str = "2024-01-01",
    end_date: str = "2025-12-31",
    n_converted: int | None = None,
) -> pd.DataFrame:
    first_names = generate_first_names(n_samples)
    last_names = generate_last_names(n_samples)
    companies = generate_company_names(n_samples)

    company_domains = np.array(
        [
            c.lower().replace(" ", "").replace(",", "").replace(".", "")[:12] + ".com"
            for c in companies
        ]
    )
    emails = np.array(
        [f"{f.lower()}.{ln.lower()}@{d}" for f, ln, d in zip(first_names, last_names, company_domains)]
    )

    n_conv = n_converted if n_converted is not None else int(n_samples * 0.20)
    n_conv = min(n_conv, n_samples)

    statuses = np.full(n_samples, "new", dtype=object)
    perm = np.random.permutation(n_samples)
    statuses[perm[:n_conv]] = "converted"
    remaining = perm[n_conv:]
    n_qual = int(len(remaining) * 0.10)
    n_disq = int(len(remaining) * 0.44)
    statuses[remaining[:n_qual]] = "qualified"
    statuses[remaining[n_qual : n_qual + n_disq]] = "disqualified"

    return pd.DataFrame(
        {
            "lead_id": generate_n_random_uuids(n_samples),
            "lead_number": generate_serial_numbers_with_prefix(
                n_samples, prefix="LDR-", total_length=11
            ),
            "first_name": first_names,
            "last_name": last_names,
            "email": emails,
            "phone": generate_phone_numbers(n_samples),
            "company": companies,
            "source": np.random.choice(_SOURCES, p=_SOURCE_WEIGHTS, size=n_samples),
            "created_date": generate_random_dates(start_date, end_date, n_samples),
            "status": statuses,
        }
    )
