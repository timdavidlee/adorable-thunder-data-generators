# Transportation & Logistics (TL)

**Flow:** Load Planning → Booking → Shipment Execution → Tracking Events → Proof of Delivery → Freight Audit → Payment

TL covers the movement of goods between locations — inbound from suppliers, outbound to customers, and inter-facility transfers.

## Records

| Record | Key Fields |
|---|---|
| **Shipment** | shipment_id, mode, carrier_scac, origin, destination, incoterms, status, weight_kg, volume_cbm |
| **Shipment Leg** | leg_id, shipment_id, origin, destination, carrier, departure_date, arrival_date, status |
| **Tracking Event** | event_id, shipment_id, event_type, location, event_date, description |
| **Freight Invoice** | invoice_id, shipment_id, carrier, base_freight, fuel_surcharge, accessorials, total_amount, currency |
| **Customs Declaration** | declaration_id, shipment_id, country, hs_code, declared_value, duty_rate, duty_amount, status |

## Transport Mode Benchmarks

| Mode | Typical Transit | Cost per kg |
|---|---|---|
| Road (domestic) | 1–5 days | $0.10–$0.50 |
| Ocean (FCL) | 14–45 days | $0.05–$0.20 |
| Air freight | 1–5 days | $2.00–$8.00 |
| Rail | 5–15 days | $0.08–$0.25 |
| Parcel / express | 1–3 days | $5.00–$20.00 |

## Business Rules

- **Date chain**: booking_date < departure_date < arrival_date < pod_date
- **Incoterms determine risk/cost split**: EXW = all buyer responsibility; DDP = all seller
- **Freight audit**: carrier_invoice vs. contracted_rate × weight/volume; dispute if variance >$50 or >5%
- **Customs**: required for all cross-border shipments; duty = declared_value × duty_rate
- **Multi-leg**: ocean shipments often have a truck leg at origin and destination (drayage)

## Realism Benchmarks

- **On-time delivery**: 92–96% domestic road; 85–90% international ocean
- **Freight as % of goods value**: road 2–5%; ocean 1–3%; air 10–20%
- **Accessorial charges**: 10–20% of base freight (fuel surcharge, detention, liftgate, residential)
- **Customs clearance time**: 1–3 days for routine shipments; 7–14 days for inspected or complex declarations
- **Weight vs. volume billing**: carriers charge the greater of actual weight vs. dimensional weight (typically L×W×H / 5,000 cm³)

## Field Generators

`carrier`, `incoterms`, `dates`, `amounts`, `identifiers`, `country`, `address`, `product_code`, `unit_of_measure`, `currency`
