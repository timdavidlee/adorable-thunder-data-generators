import numpy as np
import pandas as pd

from adorable_thunder.make.field_generators._random_state import get_random_state
from adorable_thunder.make.field_generators.carrier import generate_carriers
from adorable_thunder.make.field_generators.dates import generate_random_dates
from adorable_thunder.make.field_generators.identifiers import (
    generate_n_random_uuids,
    generate_serial_numbers_with_prefix,
)
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql, PgColumn

INBOUND_SHIPMENTS_TABLE_NAME = "inbound_shipments"

_STATUSES = np.array(["pending", "in_transit", "received", "cancelled"])
_STATUS_WEIGHTS = np.array([0.10, 0.25, 0.60, 0.05])

_DOMESTIC_ORIGINS = np.array(["US", "CA", "MX"])
_INTL_ORIGINS = np.array(["CN", "DE", "JP", "KR", "VN", "IN", "GB", "TW"])

_INTERNATIONAL_RATE = 0.30
_DOMESTIC_DELAY_RANGE = (-3, 4)  # ±3 days inclusive
_INTL_DELAY_RANGE = (-7, 8)  # ±7 days inclusive

_DEST_WAREHOUSES = np.array(["WH1", "WH2", "WH3"])
_DEST_WEIGHTS = np.array([0.45, 0.35, 0.20])


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=INBOUND_SHIPMENTS_TABLE_NAME,
        llm_description=(
            "Shipments arriving at the warehouse from suppliers or contract manufacturers. "
            "actual_date is within ±3 days of expected_date for domestic origins and ±7 "
            "days for international origins. ~30% of shipments are international."
        ),
        pg_columns=[
            PgColumn(
                name="shipment_id",
                data_type="UUID",
                modifiers="PRIMARY KEY",
                llm_description="Unique identifier for the inbound shipment.",
                llm_example_values="'b2c3d4e5-f6a7-8901-bcde-f12345678901'",
            ),
            PgColumn(
                name="shipment_number",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Human-readable inbound shipment reference.",
                llm_example_values="'INB-000123', 'INB-009999'",
            ),
            PgColumn(
                name="carrier_scac",
                data_type="VARCHAR(4)",
                modifiers="NOT NULL",
                llm_description="Carrier SCAC code for the inbound move.",
                llm_example_values="'FDEG', 'UPSN', 'MAEU'",
            ),
            PgColumn(
                name="carrier_name",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Carrier company name.",
                llm_example_values="'FedEx Ground', 'Maersk Line'",
            ),
            PgColumn(
                name="tracking_number",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Carrier-issued tracking reference.",
                llm_example_values="'TRK-0000001234567', 'TRK-0000009876543'",
            ),
            PgColumn(
                name="origin_country",
                data_type="VARCHAR(2)",
                modifiers="NOT NULL",
                llm_description="ISO-3166-1 alpha-2 origin country code.",
                llm_example_values="'US', 'CN', 'DE'",
            ),
            PgColumn(
                name="is_international",
                data_type="BOOLEAN",
                modifiers="NOT NULL",
                llm_description=(
                    "True when origin_country is not in {US, CA, MX}. ~30% of shipments."
                ),
                llm_example_values="'true', 'false'",
            ),
            PgColumn(
                name="destination_warehouse",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Receiving warehouse identifier.",
                llm_example_values="'WH1', 'WH2', 'WH3'",
            ),
            PgColumn(
                name="expected_date",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description="Date the shipment was expected to arrive.",
                llm_example_values="'2024-06-15', '2025-09-30'",
            ),
            PgColumn(
                name="actual_date",
                data_type="DATE",
                modifiers="",
                llm_description=(
                    "Date the shipment actually arrived. NULL when status is pending or "
                    "in_transit. Within ±3 days of expected_date for domestic, ±7 for "
                    "international."
                ),
                llm_example_values="'2024-06-16', '2025-10-02', NULL",
            ),
            PgColumn(
                name="status",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description=(
                    "Lifecycle status. Mix: pending ~10%, in_transit ~25%, received ~60%, "
                    "cancelled ~5%."
                ),
                llm_example_values="'pending', 'in_transit', 'received', 'cancelled'",
            ),
        ],
    )


def generate_inbound_shipments(
    n_samples: int,
    start_date: str = "2024-01-01",
    end_date: str = "2025-12-31",
) -> pd.DataFrame:
    rng = get_random_state()

    is_international = rng.random(n_samples) < _INTERNATIONAL_RATE
    origins = np.where(
        is_international,
        rng.choice(_INTL_ORIGINS, size=n_samples),
        rng.choice(_DOMESTIC_ORIGINS, size=n_samples),
    )

    expected_date = generate_random_dates(start_date, end_date, n_samples)

    delay_days = np.where(
        is_international,
        rng.randint(_INTL_DELAY_RANGE[0], _INTL_DELAY_RANGE[1], size=n_samples),
        rng.randint(_DOMESTIC_DELAY_RANGE[0], _DOMESTIC_DELAY_RANGE[1], size=n_samples),
    )
    actual_date = expected_date + pd.to_timedelta(delay_days, unit="D")

    statuses = rng.choice(_STATUSES, p=_STATUS_WEIGHTS, size=n_samples)
    has_actual = (statuses == "received") | (statuses == "cancelled")
    actual_date_with_nulls = pd.Series(
        np.where(has_actual, actual_date.to_numpy(), np.datetime64("NaT"))
    )

    carriers = generate_carriers(n_samples)

    return pd.DataFrame(
        {
            "shipment_id": generate_n_random_uuids(n_samples),
            "shipment_number": generate_serial_numbers_with_prefix(
                n_samples, prefix="INB-", total_length=10
            ),
            "carrier_scac": carriers["carrier_scac"].to_numpy(),
            "carrier_name": carriers["carrier_name"].to_numpy(),
            "tracking_number": generate_serial_numbers_with_prefix(
                n_samples, prefix="TRK-", total_length=18
            ),
            "origin_country": origins,
            "is_international": is_international,
            "destination_warehouse": rng.choice(
                _DEST_WAREHOUSES, p=_DEST_WEIGHTS, size=n_samples
            ),
            "expected_date": expected_date,
            "actual_date": actual_date_with_nulls,
            "status": statuses,
        }
    )
