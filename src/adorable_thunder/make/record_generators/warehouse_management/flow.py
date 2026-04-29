from typing import ClassVar

import pandas as pd

from adorable_thunder.make.record_generators.schemas import BaseGeneratorConfig

from .cycle_counts import CYCLE_COUNTS_TABLE_NAME, generate_cycle_counts
from .inbound_shipments import INBOUND_SHIPMENTS_TABLE_NAME, generate_inbound_shipments
from .outbound_shipments import OUTBOUND_SHIPMENTS_TABLE_NAME, generate_outbound_shipments
from .pick_lists import PICK_LISTS_TABLE_NAME, generate_pick_lists
from .receipt_lines import RECEIPT_LINES_TABLE_NAME, generate_receipt_lines
from .storage_locations import STORAGE_LOCATIONS_TABLE_NAME, generate_storage_locations

FLOW_NAME = "warehouse_management"


class GeneratorConfig(BaseGeneratorConfig):
    name: ClassVar[str] = FLOW_NAME
    start_date: str = "2024-01-01"
    end_date: str = "2025-12-31"

    def make(self) -> dict[str, pd.DataFrame]:
        storage_locations = generate_storage_locations(self.n_samples)

        inbound_shipments = generate_inbound_shipments(
            self.n_samples, start_date=self.start_date, end_date=self.end_date
        )
        receipt_lines = generate_receipt_lines(
            shipment_ids=inbound_shipments["shipment_id"].to_numpy(),
            shipment_actual_dates=inbound_shipments["actual_date"],
            shipment_statuses=inbound_shipments["status"].to_numpy(),
            storage_locations=storage_locations,
        )

        pick_lists = generate_pick_lists(
            n_orders=self.n_samples,
            storage_locations=storage_locations,
            start_date=self.start_date,
            end_date=self.end_date,
        )
        outbound_shipments = generate_outbound_shipments(pick_lists)

        cycle_counts = generate_cycle_counts(
            n_samples=self.n_samples,
            storage_locations=storage_locations,
            start_date=self.start_date,
            end_date=self.end_date,
        )

        return {
            STORAGE_LOCATIONS_TABLE_NAME: storage_locations,
            INBOUND_SHIPMENTS_TABLE_NAME: inbound_shipments,
            RECEIPT_LINES_TABLE_NAME: receipt_lines,
            PICK_LISTS_TABLE_NAME: pick_lists,
            OUTBOUND_SHIPMENTS_TABLE_NAME: outbound_shipments,
            CYCLE_COUNTS_TABLE_NAME: cycle_counts,
        }
