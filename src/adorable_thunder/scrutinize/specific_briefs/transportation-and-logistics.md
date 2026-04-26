# Transportation & Logistics (TL) — Scrutiny Brief

**Date chain** (high severity): `booking_date < departure_date < arrival_date < pod_date`. Arrivals before departures or PODs before arrivals are hard bugs.

**Mode-appropriate transit times**: road domestic 1–5 days; ocean 14–45 days; air 1–5 days; rail 5–15 days. Ocean shipments with 2-day transit, or road shipments taking 60 days, are unrealistic.

**Freight audit math**: `total_amount = base_freight + fuel_surcharge + accessorials`. Verify arithmetic. Accessorials should be 10–20% of base freight — if they're 0% on every shipment, the generator is skipping a realistic cost component.

**Customs records**: every cross-border shipment (origin country ≠ destination country) should have a corresponding customs declaration. Domestic shipments should not.

**Duty math**: `duty_amount = declared_value × duty_rate`. Verify arithmetic on a sample.

**Multi-leg logic**: ocean shipments should typically have truck legs at origin and destination (drayage). A dataset where all ocean shipments have a single leg is unrealistic.

**Tracking event sequencing**: events for a shipment should be in strict chronological order and logically sequenced — a `DEPARTED` event cannot follow a `DELIVERED` event at the same location; an `ARRIVED` must precede any `CUSTOMS_CLEARED` or `OUT_FOR_DELIVERY` event. Out-of-order events are a generator sequencing bug.

**Freight as % of goods value**: road 2–5%; ocean 1–3%; air 10–20%. If `total_amount / declared_value` consistently exceeds 30% for road or ocean, the freight amounts are miscalibrated relative to cargo value.

**Incoterms-customs alignment**: `DDP` (Delivered Duty Paid) means the seller bears all customs costs — a customs record on a DDP shipment should show duty paid by the seller, not the buyer. `EXW` (Ex Works) transfers all responsibility to the buyer. Mismatches between incoterms and the party recorded as paying duty indicate a generator wiring error.
