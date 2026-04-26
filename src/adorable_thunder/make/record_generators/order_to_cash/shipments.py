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
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql, PgColumn

_SHIPMENT_STATUSES = np.array(["delivered", "in_transit", "pending", "cancelled"])
_SHIPMENT_STATUS_WEIGHTS = np.array([0.60, 0.25, 0.10, 0.05])


SHIPMENTS_TABLE_NAME = "shipments"


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=SHIPMENTS_TABLE_NAME,
        llm_description="Outbound shipments dispatched to fulfil a sales order. ship_date is order_date + 1–14 days. On-time delivery: ~60% delivered, ~25% in transit.",
        pg_columns=[
            PgColumn(
                name="shipment_id",
                data_type="UUID",
                modifiers="PRIMARY KEY",
                llm_description="Unique identifier for the shipment.",
                llm_example_values="'a7b8c9d0-e1f2-3456-abcd-567890123456'",
            ),
            PgColumn(
                name="order_id",
                data_type="UUID",
                modifiers="NOT NULL",
                llm_description="Foreign key to the sales order being fulfilled.",
                llm_example_values="'f6a7b8c9-d0e1-2345-fabc-456789012345'",
            ),
            PgColumn(
                name="shipment_number",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Human-readable shipment reference number.",
                llm_example_values="'SHP-00001234', 'SHP-00009999'",
            ),
            PgColumn(
                name="ship_date",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description="Date goods left origin. Must be ≥ order_date and ≤ invoice_date.",
                llm_example_values="'2024-02-10', '2025-03-20'",
            ),
            PgColumn(
                name="carrier_scac",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Standard Carrier Alpha Code (SCAC) identifying the carrier. 2–4 uppercase letters.",
                llm_example_values="'UPSN', 'FDEG', 'DHLG', 'MAEU'",
            ),
            PgColumn(
                name="carrier_name",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Full legal name of the freight carrier.",
                llm_example_values="'UPS', 'FedEx', 'DHL', 'Maersk'",
            ),
            PgColumn(
                name="transport_mode",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Mode of transport used for this shipment.",
                llm_example_values="'road', 'ocean', 'air', 'rail', 'parcel'",
            ),
            PgColumn(
                name="tracking_number",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Carrier-assigned tracking reference for the shipment.",
                llm_example_values="'TRK-00001234567', 'TRK-00009876543'",
            ),
            PgColumn(
                name="incoterms",
                data_type="TEXT",
                modifiers="",
                llm_description="ICC Incoterms 2020 code defining risk and cost split between buyer and seller. NULL for domestic shipments (same origin and destination country).",
                llm_example_values="'EXW', 'FOB', 'CIF', 'DAP', 'DDP', NULL",
            ),
            PgColumn(
                name="origin_city",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="City from which the shipment departed.",
                llm_example_values="'Chicago', 'Rotterdam', 'Shanghai'",
            ),
            PgColumn(
                name="origin_country_code",
                data_type="VARCHAR(2)",
                modifiers="NOT NULL",
                llm_description="ISO 3166-1 alpha-2 country code of the shipment origin.",
                llm_example_values="'US', 'NL', 'CN', 'DE'",
            ),
            PgColumn(
                name="destination_city",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="City to which the shipment is consigned.",
                llm_example_values="'New York', 'London', 'Singapore'",
            ),
            PgColumn(
                name="destination_country_code",
                data_type="VARCHAR(2)",
                modifiers="NOT NULL",
                llm_description="ISO 3166-1 alpha-2 country code of the shipment destination.",
                llm_example_values="'US', 'GB', 'SG', 'FR'",
            ),
            PgColumn(
                name="status",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description="Shipment lifecycle status. Expected mix: delivered ~60%, in_transit ~25%, pending ~10%, cancelled ~5%.",
                llm_example_values="'delivered', 'in_transit', 'pending', 'cancelled'",
            ),
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

    origin_country = origin_df["country_code"].to_numpy()
    destination_country = destination_df["country_code"].to_numpy()
    incoterms_codes = generate_incoterms_codes(n_samples).astype(object)
    # Incoterms are an international trade convention; domestic shipments carry none
    incoterms_codes[origin_country == destination_country] = None

    # CIF and CFR are maritime-only (ICC Incoterms 2020); replace them on non-ocean modes
    transport_mode_arr = carrier_df["transport_mode"].to_numpy()
    replace_mask = np.isin(incoterms_codes, ["CIF", "CFR"]) & (transport_mode_arr != "ocean")
    if replace_mask.any():
        incoterms_codes[replace_mask] = np.random.choice(
            np.array(["CIP", "CPT", "DAP", "DDP"]), size=int(replace_mask.sum())
        )

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
            "incoterms": incoterms_codes,
            "origin_city": origin_df["city"].to_numpy(),
            "origin_country_code": origin_country,
            "destination_city": destination_df["city"].to_numpy(),
            "destination_country_code": destination_country,
            "status": np.random.choice(
                _SHIPMENT_STATUSES, p=_SHIPMENT_STATUS_WEIGHTS, size=n_samples
            ),
        }
    )
