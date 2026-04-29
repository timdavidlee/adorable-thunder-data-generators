import numpy as np
import pandas as pd

from adorable_thunder.make.field_generators.identifiers import generate_n_random_uuids
from adorable_thunder.make.record_generators.schemas import CreatePgTableSql, PgColumn

ACTIVATION_EVENTS_TABLE_NAME = "activation_events"

_PROFILE_SETUP_RATE_AMONG_ACCOUNTS = 0.80


def create_pg_sql_table_schema(pg_schema: str) -> CreatePgTableSql:
    return CreatePgTableSql(
        pg_schema=pg_schema,
        pg_table=ACTIVATION_EVENTS_TABLE_NAME,
        llm_description=(
            "Discrete activation milestones logged for installs that opened the app. One row "
            "per (install, event_name) — events are not repeated. Event sequence: "
            "ACCOUNT_CREATED → PROFILE_SETUP → TUTORIAL_COMPLETED → FIRST_MEANINGFUL_ACTION. "
            "TUTORIAL_COMPLETED implies a preceding ACCOUNT_CREATED event for the same install. "
            "FIRST_MEANINGFUL_ACTION implies a preceding TUTORIAL_COMPLETED event."
        ),
        pg_columns=[
            PgColumn(
                name="event_id",
                data_type="UUID",
                modifiers="PRIMARY KEY",
                llm_description="Unique identifier for the event.",
                llm_example_values="'d4e5f6a7-b8c9-0123-defa-456789012345'",
            ),
            PgColumn(
                name="install_id",
                data_type="UUID",
                modifiers="NOT NULL",
                llm_description="Foreign key to the install that produced the event.",
                llm_example_values="'a1b2c3d4-e5f6-7890-abcd-ef1234567890'",
            ),
            PgColumn(
                name="event_name",
                data_type="TEXT",
                modifiers="NOT NULL",
                llm_description=(
                    "Activation milestone. ACCOUNT_CREATED for installs that registered. "
                    "PROFILE_SETUP follows account creation in ~80% of accounts. "
                    "TUTORIAL_COMPLETED requires an account; ~85% of accounts complete it. "
                    "FIRST_MEANINGFUL_ACTION requires tutorial completion and is logged for "
                    "the subset of completers retained at day 1."
                ),
                llm_example_values=(
                    "'ACCOUNT_CREATED', 'PROFILE_SETUP', 'TUTORIAL_COMPLETED', "
                    "'FIRST_MEANINGFUL_ACTION'"
                ),
            ),
            PgColumn(
                name="occurred_at",
                data_type="DATE",
                modifiers="NOT NULL",
                llm_description=(
                    "Date the event occurred. Strictly non-decreasing along the milestone "
                    "chain for any given install: account ≤ profile/tutorial ≤ FMA."
                ),
                llm_example_values="'2024-02-01', '2025-06-16'",
            ),
        ],
    )


def _emit_event_rows(
    install_ids: np.ndarray,
    event_dates: pd.Series,
    event_name: str,
) -> list[dict[str, object]]:
    return [
        {
            "install_id": install_ids[i],
            "event_name": event_name,
            "occurred_at": event_dates.iloc[i],
        }
        for i in range(len(install_ids))
    ]


def generate_activation_events(installs: pd.DataFrame) -> pd.DataFrame:
    opened = installs[installs["_has_first_open"]].reset_index(drop=True)
    if len(opened) == 0:
        return pd.DataFrame(columns=["event_id", "install_id", "event_name", "occurred_at"])

    n = len(opened)
    first_open = pd.to_datetime(opened["first_open_at"])
    install_ids = opened["install_id"].to_numpy()
    has_account = opened["_has_account"].to_numpy()
    tutorial_completed = opened["_tutorial_completed"].to_numpy()
    retained_d1 = opened["_retained_d1"].to_numpy()

    # Offsets are sampled per install with cumulative jitter so the event chain stays
    # monotonic: account ≤ profile/tutorial ≤ FMA. Using one shared offset per install
    # for each milestone (rather than independent draws per event type) prevents
    # tutorial-before-account inversions.
    account_offset = np.random.randint(0, 3, size=n)
    profile_offset = account_offset + np.random.randint(0, 3, size=n)
    tutorial_offset = account_offset + np.random.randint(0, 3, size=n)
    fma_offset = tutorial_offset + np.random.randint(0, 4, size=n)
    profile_drawn = np.random.random(n) < _PROFILE_SETUP_RATE_AMONG_ACCOUNTS

    rows: list[dict[str, object]] = []

    if has_account.any():
        idx = np.where(has_account)[0]
        dates = first_open.iloc[idx].reset_index(drop=True) + pd.to_timedelta(
            account_offset[idx], unit="D"
        )
        rows.extend(_emit_event_rows(install_ids[idx], dates, "ACCOUNT_CREATED"))

    profile_mask = has_account & profile_drawn
    if profile_mask.any():
        idx = np.where(profile_mask)[0]
        dates = first_open.iloc[idx].reset_index(drop=True) + pd.to_timedelta(
            profile_offset[idx], unit="D"
        )
        rows.extend(_emit_event_rows(install_ids[idx], dates, "PROFILE_SETUP"))

    if tutorial_completed.any():
        idx = np.where(tutorial_completed)[0]
        dates = first_open.iloc[idx].reset_index(drop=True) + pd.to_timedelta(
            tutorial_offset[idx], unit="D"
        )
        rows.extend(_emit_event_rows(install_ids[idx], dates, "TUTORIAL_COMPLETED"))

    fma_mask = tutorial_completed & retained_d1
    if fma_mask.any():
        idx = np.where(fma_mask)[0]
        dates = first_open.iloc[idx].reset_index(drop=True) + pd.to_timedelta(
            fma_offset[idx], unit="D"
        )
        rows.extend(_emit_event_rows(install_ids[idx], dates, "FIRST_MEANINGFUL_ACTION"))

    if not rows:
        return pd.DataFrame(columns=["event_id", "install_id", "event_name", "occurred_at"])

    df = pd.DataFrame(rows)
    df.insert(0, "event_id", generate_n_random_uuids(len(df)))
    return df[["event_id", "install_id", "event_name", "occurred_at"]]
