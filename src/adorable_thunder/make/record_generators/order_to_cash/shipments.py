import numpy as np
import pandas as pd

from adorable_thunder.make.field_generators.address import generate_addresses
from adorable_thunder.make.field_generators.carrier import generate_carriers
from adorable_thunder.make.field_generators.dates import (
    extrapolate_off_dates,
    generate_random_dates,
)
from adorable_thunder.make.field_generators.identifiers import (
    generate_n_random_uuids,
    generate_serial_numbers_with_prefix,
)
from adorable_thunder.make.field_generators.incoterms import generate_incoterms_codes
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql

_SHIPMENT_STATUSES = np.array(["delivered", "in_transit", "pending", "cancelled"])
_SHIPMENT_STATUS_WEIGHTS = np.array([0.60, 0.25, 0.10, 0.05])


SHIPMENTS_TABLE_NAME = "shipments"


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=SHIPMENTS_TABLE_NAME,
        pg_columns=[
            "shipment_id              UUID      PRIMARY KEY",
            "order_id                 UUID      NOT NULL",
            "shipment_number          TEXT      NOT NULL",
            "ship_date                DATE      NOT NULL",
            "carrier_scac             TEXT      NOT NULL",
            "carrier_name             TEXT      NOT NULL",
            "transport_mode           TEXT      NOT NULL",
            "tracking_number          TEXT      NOT NULL",
            "incoterms                TEXT      NOT NULL",
            "origin_city              TEXT      NOT NULL",
            "origin_country_code      VARCHAR(2) NOT NULL",
            "destination_city         TEXT      NOT NULL",
            "destination_country_code VARCHAR(2) NOT NULL",
            "status                   TEXT      NOT NULL",
        ],
    )


def generate_shipments(
    n_samples: int,
    start_date: str = "2024-01-01",
    end_date: str = "2025-12-31",
    order_ids: np.ndarray | None = None,
    order_dates: pd.Series | None = None,
) -> pd.DataFrame:
    if order_ids is None:
        order_ids = generate_n_random_uuids(n_samples)

    if order_dates is not None:
        ship_dates = extrapolate_off_dates(order_dates, min_days=1, max_days=14)
    else:
        ship_dates = generate_random_dates(start_date, end_date, n_samples)

    carrier_df = generate_carriers(n_samples)
    origin_df = generate_addresses(n_samples)
    destination_df = generate_addresses(n_samples)

    return pd.DataFrame(
        {
            "shipment_id": generate_n_random_uuids(n_samples),
            "order_id": order_ids,
            "shipment_number": generate_serial_numbers_with_prefix(
                n_samples, prefix="SHP-", total_length=12
            ),
            "ship_date": ship_dates,
            "carrier_scac": carrier_df["carrier_scac"].to_numpy(),
            "carrier_name": carrier_df["carrier_name"].to_numpy(),
            "transport_mode": carrier_df["transport_mode"].to_numpy(),
            "tracking_number": generate_serial_numbers_with_prefix(
                n_samples, prefix="TRK-", total_length=15
            ),
            "incoterms": generate_incoterms_codes(n_samples),
            "origin_city": origin_df["city"].to_numpy(),
            "origin_country_code": origin_df["country_code"].to_numpy(),
            "destination_city": destination_df["city"].to_numpy(),
            "destination_country_code": destination_df["country_code"].to_numpy(),
            "status": np.random.choice(
                _SHIPMENT_STATUSES, p=_SHIPMENT_STATUS_WEIGHTS, size=n_samples
            ),
        }
    )
