from typing import ClassVar

import numpy as np
import pandas as pd

from adorable_thunder.make.record_generators.schemas import BaseGeneratorConfig

from .forecasts import FORECASTS_TABLE_NAME, generate_forecasts
from .inventory_positions import (
    INVENTORY_POSITIONS_TABLE_NAME,
    generate_inventory_positions,
)
from .replenishment_orders import (
    REPLENISHMENT_ORDERS_TABLE_NAME,
    generate_replenishment_orders,
)
from .stock_parameters import STOCK_PARAMETERS_TABLE_NAME, generate_stock_parameters

FLOW_NAME = "forecast_to_stock"


def _suppress_overlapping_triggers(
    triggered: pd.DataFrame, lead_time_days: pd.Series
) -> pd.DataFrame:
    # Keep only triggered snapshots whose date is strictly after the previous
    # surviving trigger's expected_receipt — so each (sku, location) never has
    # two open replenishment orders simultaneously. This keeps trigger logic
    # consistent with the post-hoc on_order_qty derivation in the caller.
    sorted_df = triggered.assign(_lead_time=lead_time_days.to_numpy()).sort_values(
        ["sku", "location", "as_of_date"]
    )
    sorted_df["_exp_recv"] = sorted_df["as_of_date"] + pd.to_timedelta(
        sorted_df["_lead_time"], unit="D"
    )

    keep = np.zeros(len(sorted_df), dtype=bool)
    last_exp_by_pair: dict[tuple[str, str], pd.Timestamp] = {}
    pairs = list(zip(sorted_df["sku"].to_numpy(), sorted_df["location"].to_numpy()))
    as_of = sorted_df["as_of_date"].to_numpy()
    exp_recv = sorted_df["_exp_recv"].to_numpy()
    for i, pair in enumerate(pairs):
        last = last_exp_by_pair.get(pair)
        if last is None or as_of[i] > last:
            keep[i] = True
            last_exp_by_pair[pair] = exp_recv[i]
    return sorted_df[keep].drop(columns=["_lead_time", "_exp_recv"]).reset_index(drop=True)


def _derive_on_order_from_open_orders(
    inventory_positions: pd.DataFrame, replenishment_orders: pd.DataFrame
) -> pd.DataFrame:
    open_orders = replenishment_orders[replenishment_orders["status"] != "cancelled"][
        ["sku", "location", "trigger_date", "expected_receipt_date", "order_qty"]
    ]
    ip_idx = inventory_positions.reset_index(drop=True).reset_index(names="_ip_idx")
    merged = ip_idx.merge(open_orders, on=["sku", "location"], how="left")
    is_open = (merged["trigger_date"] < merged["as_of_date"]) & (
        merged["as_of_date"] < merged["expected_receipt_date"]
    )
    merged["_contrib"] = merged["order_qty"].where(is_open, 0).fillna(0)
    summed = merged.groupby("_ip_idx", sort=True)["_contrib"].sum()

    out = inventory_positions.reset_index(drop=True).copy()
    out["on_order_qty"] = summed.reindex(range(len(out)), fill_value=0).astype(int).to_numpy()
    out["available_qty"] = (
        out["on_hand_qty"] + out["on_order_qty"] - out["committed_qty"]
    ).astype(int)
    return out


class GeneratorConfig(BaseGeneratorConfig):
    name: ClassVar[str] = FLOW_NAME
    start_date: str = "2024-01-01"
    end_date: str = "2025-12-31"

    def make(self) -> dict[str, pd.DataFrame]:
        stock_parameters = generate_stock_parameters(self.n_samples)

        forecasts = generate_forecasts(
            skus=stock_parameters["sku"].to_numpy(),
            avg_daily_demand=stock_parameters["avg_daily_demand"].to_numpy(),
            start_date=self.start_date,
            end_date=self.end_date,
        )

        inventory_positions = generate_inventory_positions(
            skus=stock_parameters["sku"].to_numpy(),
            locations=stock_parameters["location"].to_numpy(),
            reorder_points=stock_parameters["reorder_point"].to_numpy(),
            avg_daily_demand=stock_parameters["avg_daily_demand"].to_numpy(),
            start_date=self.start_date,
            end_date=self.end_date,
        )

        params_by_sku = stock_parameters.set_index("sku")
        triggered_mask = inventory_positions["available_qty"] <= (
            inventory_positions["sku"].map(params_by_sku["reorder_point"]).to_numpy()
        )
        triggered = inventory_positions[triggered_mask].reset_index(drop=True)

        lead_time = triggered["sku"].map(params_by_sku["lead_time_days"])
        triggered = _suppress_overlapping_triggers(triggered, lead_time)

        replenishment_orders = generate_replenishment_orders(
            skus=triggered["sku"].to_numpy(),
            locations=triggered["location"].to_numpy(),
            trigger_dates=triggered["as_of_date"],
            on_hand_qty=triggered["on_hand_qty"].to_numpy(),
            reorder_points=triggered["sku"].map(params_by_sku["reorder_point"]).to_numpy(),
            safety_stock_qty=triggered["sku"].map(params_by_sku["safety_stock_qty"]).to_numpy(),
            economic_order_qty=triggered["sku"]
            .map(params_by_sku["economic_order_qty"])
            .to_numpy(),
            lead_time_days=triggered["sku"].map(params_by_sku["lead_time_days"]).to_numpy(),
        )

        inventory_positions = _derive_on_order_from_open_orders(
            inventory_positions, replenishment_orders
        )

        return {
            STOCK_PARAMETERS_TABLE_NAME: stock_parameters,
            FORECASTS_TABLE_NAME: forecasts,
            INVENTORY_POSITIONS_TABLE_NAME: inventory_positions,
            REPLENISHMENT_ORDERS_TABLE_NAME: replenishment_orders,
        }
