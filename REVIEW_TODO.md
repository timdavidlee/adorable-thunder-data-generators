# Code Review TODO

Findings from a full review of `src/` and `tests/` (Python 3.13, pyright strict, ruff, pytest).

**How to use this file:** work top-to-bottom (highest impact first). **Delete each item from this file as it is completed** — don't just check the box. When the file is empty, delete it.

Pyright currently passes (`0 errors`). Ruff has 148 auto-fixable lint errors. 84 tests collected, all in `field_generators/` (zero coverage on flows, database, scrutinize agent).

---

## Top priority — silent correctness bugs

- [ ] **Fix `splits.py` group-key bug + misleading API.** [splits.py:79-82](src/adorable_thunder/make/field_generators/splits.py#L79) — `assign_split_weights_within_original_record` does `groupby("splits")` but the parameter is named `splits` and the docstring says "number of splits per record." Rename to `record_ids` (or fix the grouping). [test_splits.py](tests/adorable_thunder/make/field_generators/test_splits.py) cements the buggy semantics — update tests too.
- [ ] **Fix zero-decimal currency rounding.** [amounts.py:43-46](src/adorable_thunder/make/field_generators/amounts.py#L43-L46) — `round(amount * rate, 2)` produces `12345.67 JPY`, but JPY/KRW/CLP/IDR have 0 minor units per ISO 4217. Add a per-currency decimals map.
- [ ] **Replace f-string SQL identifiers in DDL.** [schemas.py:40,45](src/adorable_thunder/make/record_generators/schemas.py#L40) — `CREATE TABLE {self.pg_schema}.{self.pg_table}` and `COPY` interpolate identifiers as raw strings. Use `psycopg.sql.Identifier(...)` so it's safe by construction.
- [ ] **Tighten `run_sql` SELECT-only check.** [run_sql.py:24](src/adorable_thunder/scrutinize/tools/run_sql.py#L24) — `query.strip().upper().startswith("SELECT")` rejects valid `WITH ... SELECT` CTEs and lets `SELECT 1; DROP …` past the gate. Drop the check, rely on `default_transaction_read_only=on` + the read-only role, and remove `sql.SQL(query)` and the `# type: ignore[arg-type]` (use `cur.execute(query)` directly).
- [ ] **Add prompt caching + pin a model in the scrutinize agent.** [agent_definition.py:78](src/adorable_thunder/scrutinize/agent/agent_definition.py#L78) — long system prompt, tool schemas, and brief content are reused across many tool turns with no caching. Configure `cache_control: {"type": "ephemeral"}` on the system prompt and tool blocks. Pin `model="claude-opus-4-7-..."` (or Sonnet 4.6 / Haiku 4.5) instead of relying on `deepagents` defaults.

---

## Other bugs

### Cross-stage invariants

- [ ] **O2C cash receipts can pre-date invoice.** [cash_receipts.py:92](src/adorable_thunder/make/record_generators/order_to_cash/cash_receipts.py#L92) — `np.random.randint(-3, 4)` for the on-time band can produce `received_date < invoice_date`. Clip lower bound to 0.
- [ ] **O2C "paid" invoices have non-zero open balance.** [order_to_cash/flow.py:60](src/adorable_thunder/make/record_generators/order_to_cash/flow.py#L60) — partial-receipt paths leave `_open_balance > 0` on rows whose status is `"paid"`. Either don't generate partials for `paid`, or use `partially_paid` status.
- [ ] **C2C engagement/conversion clipping breaks chain invariants.** [campaign_to_conversion/flow.py:82-127](src/adorable_thunder/make/record_generators/campaign_to_conversion/flow.py#L82-L127) — clipping individual stages to `campaign_end` after offsets are applied lets downstream `captured_date < engagement_date`. Re-derive each stage from the clipped predecessor.
- [ ] **Q2C `term_months * 30` drifts from monthly recurring invoices.** [subscriptions.py:218](src/adorable_thunder/make/record_generators/quote_to_cash/subscriptions.py#L218) — 30-day-month math drifts ~5–16 days from the `pd.DateOffset(months=…)` used in `recurring_invoices`; renewals fall off-cycle. Use `pd.DateOffset` row-wise.
- [ ] **Q2C `signed_date < dataset start`.** [contracts.py:107-108](src/adorable_thunder/make/record_generators/quote_to_cash/contracts.py#L107-L108) — clip lower bound to `start_date`.
- [ ] **Q2C dead branch.** [contracts.py:117](src/adorable_thunder/make/record_generators/quote_to_cash/contracts.py#L117) — `np.where(... == "paused", "active", "active")` collapses to `"active"`. Delete the conditional.
- [ ] **L2O `close_date` uses wall-clock today.** [opportunities.py:151](src/adorable_thunder/make/record_generators/lead_to_opportunity/opportunities.py#L151) — `pd.Timestamp.today()` is non-deterministic and unrelated to `start_date/end_date`. Use the configured `end_date`.
- [ ] **Forecast duplicate periods per SKU.** [forecasts.py:88-92](src/adorable_thunder/make/record_generators/forecast_to_stock/forecasts.py#L88-L92) — sample 4 *distinct* periods per SKU.
- [ ] **P2P payment currency derived from PO instead of invoice.** [procure_to_pay/flow.py:57](src/adorable_thunder/make/record_generators/procure_to_pay/flow.py#L57) — incidentally correct today (same length and order), but brittle. Read currency from `invoices`, not `approved_pos`.

### Field-generator bugs

- [ ] **Off-by-one inconsistency in `dates.py`.** [dates.py:27 vs 33](src/adorable_thunder/make/field_generators/dates.py#L27) — uniform path is end-exclusive, dist-scaling path is start-exclusive. Reconcile to `[start, end]` inclusive on both, and add a test asserting `end_date` is reachable.
- [ ] **`address.py` silent fallback for unknown country.** [address.py:11-13](src/adorable_thunder/make/field_generators/address.py#L11-L13) — passing an unknown `country_code` samples globally instead of raising.
- [ ] **`phone.py` silent fallback to `+1`.** [phone.py:60](src/adorable_thunder/make/field_generators/phone.py#L60) — unknown country code silently returns `+1`. [test_phone.py:19-21](tests/adorable_thunder/make/field_generators/test_phone.py#L19-L21) codifies this — replace with `pytest.raises`.
- [ ] **Identifier collisions; UUIDs unseedable.** [identifiers.py:33-34](src/adorable_thunder/make/field_generators/identifiers.py#L33-L34) — birthday collisions around ~1e5 samples on a 12-digit pool. [identifiers.py:8-15](src/adorable_thunder/make/field_generators/identifiers.py#L8-L15) uses `uuid4()` (OS entropy), bypassing `_random_state`. Sample without replacement up to pool size; derive UUIDs from a seeded `random.Random`.
- [ ] **`amounts.py` `np.clip` creates point-mass at bounds.** [amounts.py:25-27](src/adorable_thunder/make/field_generators/amounts.py#L25-L27) — ~7% of samples land exactly on the `max_amount`. Resample tail via rejection sampling.
- [ ] **`reference_data/person_names.py` duplicate names skew sampling.** Duplicates: `Joseph, Daniel, Isabella, Yuna, Hana, Fatima` (each x2), `Lee` x2 in last names. `np.random.choice(replace=True)` overweights them. Dedupe.
- [ ] **`reference_data/cities.py` has TW but `countries.py` doesn't.** TW will never be emitted by `generate_country_codes`, so paired (country, city) generation breaks. Add TW to `countries.py` or drop from `cities.py` and `_CALLING_CODES`.
- [ ] **`common/math.py` uses global `np.random`.** `generate_weighted_random_choice` calls `np.random.choice` directly — bypasses `_random_state`. Route through `get_random_state()`.
- [ ] **`fiscal_period.py` has stale calendar defaults.** [fiscal_period.py:8](src/adorable_thunder/make/field_generators/fiscal_period.py#L8) — `start_year=2022, end_year=2026`. Drop defaults or compute from current year.
- [ ] **`incoterms.py` weights sum to ~1.00000000000000022.** [incoterms.py:9](src/adorable_thunder/make/field_generators/incoterms.py#L9) — passes today but fragile. Route through `round_weights_and_rebalance`.
- [ ] **`splits.py` duplicates `round_weights_and_rebalance`.** [splits.py:49-60](src/adorable_thunder/make/field_generators/splits.py#L49-L60) — local `_round_and_rebalance` reimplements with a different (largest-remainder) algorithm. Pick one; move to `common/math.py`; delete the duplicate.

---

## Risks

- [ ] **`reset_schema.py` has no `--yes` guard** for `DROP SCHEMA … CASCADE`. A typo silently nukes data. Add a typed-confirm prompt or `--yes` flag.
- [ ] **Hardcoded read-only password defaults** in [database_connection.py:17](src/adorable_thunder/make/database/database_connection.py#L17) and [reset_schema.py:17](src/adorable_thunder/make/database/reset_schema.py#L17). Even matching `.env.example`, default to `None` and require env.
- [ ] **Connection per query in scrutinize tools.** [_db.py:6](src/adorable_thunder/scrutinize/tools/_db.py#L6) — every `run_sql` / `list_tables` call opens and tears down a fresh psycopg connection. Use a shared `psycopg_pool.AsyncConnectionPool`.
- [ ] **`run_sql` error path leaks DSN/role details.** [run_sql.py:34](src/adorable_thunder/scrutinize/tools/run_sql.py#L34) — `return f"Error: {e}"` exposes server hostnames and SQL fragments to the LLM. Log the full exception, return `"Error: query failed (see logs)."` plus exception class name.
- [ ] **`run_sql` row truncation.** Returns up to 200 rows but doesn't cap individual cell values — a wide JSONB row can blow context. Cap text columns at ~500 chars.
- [ ] **No retry on Anthropic 429/529/5xx.** [agent_definition.py:97](src/adorable_thunder/scrutinize/agent/agent_definition.py#L97) — wrap `astream` in `tenacity` exponential backoff on `anthropic.APIStatusError` for status >= 500 / 429.
- [ ] **`agent_definition.py:78` instantiates the agent at import time.** Importing the module spins up the LLM client and binds tools (problematic for tests). Move into `scrutinize()` or a `functools.cache`'d factory.
- [ ] **`requests.py` has an infinite-loop risk.** [procure_to_pay/requests.py:165-167](src/adorable_thunder/make/record_generators/procure_to_pay/requests.py#L165-L167) — `while clash.any(): reroll` could spin on small email pools. Cap at N retries.
- [ ] **Per-row Python loops in flows.** [iap_purchases.py:130-154](src/adorable_thunder/make/record_generators/install_to_retention/iap_purchases.py#L130-L154), [recurring_invoices.py:127-156](src/adorable_thunder/make/record_generators/quote_to_cash/recurring_invoices.py#L127-L156), [usage_records.py:135-173](src/adorable_thunder/make/record_generators/quote_to_cash/usage_records.py#L135-L173), [depreciation_runs.py:111-154](src/adorable_thunder/make/record_generators/acquire_to_retire/depreciation_runs.py#L111-L154), [phone.py:65-72](src/adorable_thunder/make/field_generators/phone.py#L65-L72) — vectorize with `np.repeat` when dataset sizes grow.
- [ ] **`n_samples` semantics differ across flows** — primary-entity count for some, multiplied/exploded for `campaign_to_conversion` and `warehouse_management`. Document expected scale per flow.

---

## Style / cleanup

- [ ] **Run `uv run ruff check --fix && uv run ruff format`.** 148 errors auto-fixable: 136 × E501 (line-too-long, >100 chars), 12 × I001 (unsorted imports). Zero risk.
- [ ] **Delete or implement empty stub files.** [central_cli.py](src/adorable_thunder/central_cli.py), [make/cli.py](src/adorable_thunder/make/cli.py), [make/database/__init__.py](src/adorable_thunder/make/database/__init__.py), [common/__init__.py](src/adorable_thunder/common/__init__.py).
- [ ] **Wire up `logging_config.yaml`** and switch `typer.echo` (used as logger) to `logger.info` for progress. Also rename the stale `logs/pregunta_ai.log` to `adorable_thunder.log` in [logging_config.yaml](logging_config.yaml).
- [ ] **Extract a `non_usd_choices()` helper in `field_generators/currency.py`.** Six near-identical `_NON_USD` blocks across record generators: [quotes.py:23-26](src/adorable_thunder/make/record_generators/order_to_cash/quotes.py#L23), [sales_orders.py:31-34](src/adorable_thunder/make/record_generators/order_to_cash/sales_orders.py#L31), [purchase_orders.py:27-30](src/adorable_thunder/make/record_generators/procure_to_pay/purchase_orders.py#L27), [payments.py:19-22](src/adorable_thunder/make/record_generators/procure_to_pay/payments.py#L19), [subscriptions.py:27-30](src/adorable_thunder/make/record_generators/quote_to_cash/subscriptions.py#L27), [iap_purchases.py:17-20](src/adorable_thunder/make/record_generators/install_to_retention/iap_purchases.py#L17), [requests.py:36-39](src/adorable_thunder/make/record_generators/procure_to_pay/requests.py#L36).
- [ ] **De-duplicate `_months_between`** across [acquire_to_retire/depreciation_runs.py:86](src/adorable_thunder/make/record_generators/acquire_to_retire/depreciation_runs.py#L86), [acquire_to_retire/disposals.py:100](src/adorable_thunder/make/record_generators/acquire_to_retire/disposals.py#L100), [quote_to_cash/recurring_invoices.py:106](src/adorable_thunder/make/record_generators/quote_to_cash/recurring_invoices.py#L106), [quote_to_cash/usage_records.py:100](src/adorable_thunder/make/record_generators/quote_to_cash/usage_records.py#L100). Lift into a shared util.
- [ ] **De-duplicate `_sku_for_zone`** across [warehouse_management/storage_locations.py:145](src/adorable_thunder/make/record_generators/warehouse_management/storage_locations.py#L145), [pick_lists.py:114](src/adorable_thunder/make/record_generators/warehouse_management/pick_lists.py#L114), [receipt_lines.py:119](src/adorable_thunder/make/record_generators/warehouse_management/receipt_lines.py#L119).
- [ ] **Standardize flow `__init__.py` exports.** Some flows export `FLOW_SCHEMAS` (list); project rule says `_FLOW_SCHEMA` (dict mapping stage name → CreatePgTableSql). Pick one, update all.
- [ ] **Parameterize numpy/psycopg generics.** `np.ndarray` in [common/math.py](src/adorable_thunder/make/common/math.py), `psycopg.AsyncConnection` and `AsyncCursor` in [database_connection.py:22,32](src/adorable_thunder/make/database/database_connection.py#L22) and [inject_into_pg.py:85,96](src/adorable_thunder/make/database/inject_into_pg.py#L85). Use `npt.NDArray[np.float64]` and `psycopg.AsyncConnection[tuple[Any, ...]]`.
- [ ] **Drop `# type: ignore` on `sql.SQL(query)`** in [run_sql.py:30](src/adorable_thunder/scrutinize/tools/run_sql.py#L30) — remove with the SELECT-check fix.
- [ ] **Use `typer.Choice` / Enum for `--flow`.** [inject_into_pg.py:145](src/adorable_thunder/make/database/inject_into_pg.py#L145) renders Python list repr in `--help`. Use `Enum` or `click_type=click.Choice(...)`.
- [ ] **Rename `run_all` to `run` / `load_flow_cli`.** [inject_into_pg.py:144](src/adorable_thunder/make/database/inject_into_pg.py#L144) — function loads a *single* flow despite the name.
- [ ] **Drop `copy_serialized_csv` dead code.** [database_connection.py:32](src/adorable_thunder/make/database/database_connection.py#L32) — defined but unused; `inject_into_pg.py` defines its own `_copy_df`.
- [ ] **Reconcile `DEFAULT_N_SAMPLES`.** [schemas.py:48](src/adorable_thunder/make/record_generators/schemas.py#L48) defaults to 10,000; [inject_into_pg.py:111](src/adorable_thunder/make/database/inject_into_pg.py#L111) defaults to 1,000. Share one constant.
- [ ] **Move `_SYSTEM_PROMPT` to a sibling `.md` file.** [agent_definition.py:17](src/adorable_thunder/scrutinize/agent/agent_definition.py#L17) — easier to diff/edit.

---

## Test gaps

The codebase has 84 tests, all in `field_generators/`. Several existing tests are smoke-only and several new categories are completely untested.

- [ ] **Add a database integration test** that calls `load_flow` against a temp schema and asserts `SELECT count(*)` per table — would catch the missing-commit bug today.
- [ ] **Add a `_copy_df` round-trip test** with a DataFrame containing `pd.NA`/`np.nan` — would catch the NULL bug.
- [ ] **Add reset_schema integration test** verifying `ai_readonly_user` can `SELECT` from a freshly created table after reset.
- [ ] **Add `_random_state.py` determinism test** — with `frozen=True`, two consecutive calls produce the same first sample.
- [ ] **Add a test for `generate_split_weights_for_records`** (the public API; current coverage is on the internal helper only).
- [ ] **Add a date-reachability test** — assert `end_date` appears in samples (catches the off-by-one).
- [ ] **Add a JPY/KRW zero-decimal currency test** for `generate_local_currency_amounts`.
- [ ] **Add an identifier collision/uniqueness test.**
- [ ] **Replace `test_phone.py:19-21`** which asserts the `+1` fallback bug — should be `pytest.raises`.
- [ ] **Add an unknown-country test for `address.py`** — should raise, not silently fall back.
- [ ] **Add a smoke test for the scrutinize agent** with a mocked Anthropic client exercising one tool call → `ScrutinyReport` round-trip.
- [ ] **Strengthen `test_users.py:9-11`** beyond `"@" in result` — parse with `email.utils.parseaddr` and check both parts.
- [ ] **Strengthen `test_person.py:23-25`** beyond `" " in name` — assert no trailing whitespace, no double-space, includes Unicode (Müller, Chloé, Pérez).
- [ ] **Move `test_company.py:22-27`** ("company first word in product") out of generator tests — it's a property of reference data, not the generator.

---

When this file is empty, delete it.
