import unicodedata

import numpy as np
import pandas as pd

from adorable_thunder.make.field_generators.country import generate_country_codes
from adorable_thunder.make.field_generators.identifiers import generate_n_random_uuids
from adorable_thunder.make.field_generators.phone import generate_phone_numbers_mixed
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql, PgColumn

_TITLES = np.array(
    [
        "VP Sales",
        "CTO",
        "CFO",
        "VP Engineering",
        "Director of Operations",
        "Head of Procurement",
        "CEO",
        "COO",
        "CRO",
        "VP Marketing",
        "Director of IT",
        "Director of Finance",
        "SVP Sales",
        "Chief Procurement Officer",
    ]
)
_TITLE_WEIGHTS = np.array(
    [0.15, 0.12, 0.10, 0.10, 0.10, 0.08, 0.08, 0.07, 0.07, 0.06, 0.03, 0.02, 0.01, 0.01]
)

CONTACTS_TABLE_NAME = "contacts"


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=CONTACTS_TABLE_NAME,
        llm_description="Qualified contacts at prospect companies, each converted from an inbound lead. Contacts are the FK anchor for opportunities. Title distribution should reflect decision-maker and influencer roles.",
        pg_columns=[
            PgColumn(
                name="contact_id",
                data_type="UUID",
                modifiers="PRIMARY KEY",
                llm_description="Unique identifier for the contact.",
                llm_example_values="'b2c3d4e5-f6a7-8901-bcde-f12345678901'",
            ),
            PgColumn(
                name="lead_id",
                data_type="UUID",
                modifiers="NOT NULL",
                llm_description="Source lead that was converted into this contact.",
                llm_example_values="'a1b2c3d4-e5f6-7890-abcd-ef1234567890'",
            ),
            PgColumn(
                name="company",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Company the contact works for, carried from the source lead.",
                llm_example_values="'Acme Corp', 'Global Tech Solutions'",
            ),
            PgColumn(
                name="first_name",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="First name of the contact.",
                llm_example_values="'James', 'Maria', 'Chen'",
            ),
            PgColumn(
                name="last_name",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Last name of the contact.",
                llm_example_values="'Smith', 'Garcia', 'Wang'",
            ),
            PgColumn(
                name="title",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Job title of the contact. Should reflect decision-maker roles: VP Sales ~15%, CTO ~12%, CFO ~10%, etc.",
                llm_example_values="'VP Sales', 'CTO', 'CFO', 'Director of Operations'",
            ),
            PgColumn(
                name="email",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Contact's business email, derived from name and company domain.",
                llm_example_values="'james.smith@acmecorp.com', 'maria.garcia@globaltech.com'",
            ),
            PgColumn(
                name="phone",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Contact's phone in E.164 format, consistent with their country.",
                llm_example_values="'+14155551234', '+447911123456'",
            ),
            PgColumn(
                name="country",
                data_type="VARCHAR(2)",
                modifiers="NOT NULL",
                llm_description="ISO-3166-1 alpha-2 country code. GDP-weighted — US, China, Germany, UK, and Japan should dominate.",
                llm_example_values="'US', 'DE', 'GB', 'JP', 'IN'",
            ),
        ],
    )


def generate_contacts(
    n_samples: int,
    lead_ids: np.ndarray,
    lead_companies: np.ndarray,
    lead_first_names: np.ndarray,
    lead_last_names: np.ndarray,
) -> pd.DataFrame:
    def _ascii(s: str) -> str:
        return (
            unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
        )

    country_codes = generate_country_codes(n_samples)

    company_domains = np.array(
        [
            _ascii(c).lower().replace(" ", "").replace(",", "").replace(".", "")[:12]
            + ".com"
            for c in lead_companies
        ]
    )
    emails = np.array(
        [
            f"{_ascii(f).lower()}.{_ascii(ln).lower()}@{d}"
            for f, ln, d in zip(lead_first_names, lead_last_names, company_domains)
        ]
    )

    return pd.DataFrame(
        {
            "contact_id": generate_n_random_uuids(n_samples),
            "lead_id": lead_ids,
            "company": lead_companies,
            "first_name": lead_first_names,
            "last_name": lead_last_names,
            "title": np.random.choice(_TITLES, p=_TITLE_WEIGHTS, size=n_samples),
            "email": emails,
            "phone": generate_phone_numbers_mixed(n_samples, country_codes),
            "country": country_codes,
        }
    )
