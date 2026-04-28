# Request-to-Delivery (R2D)

**Flow:** Search → Browse Listings → Selection → Booking/Request → Provider Acceptance → Payment Authorization → Service Delivery

R2D covers on-demand consumer marketplaces (food delivery, ride-share, courier, home services) where a customer-facing request is matched to a provider in real time. The defining trait vs. classic e-commerce is the live two-sided match with a provider acceptance step.

## Records

| Record | Key Fields |
|---|---|
| **Search** | search_id, user_id, query, geohash, timestamp, results_count |
| **Listing Impression** | impression_id, search_id, listing_id, position, viewed_at |
| **Booking Request** | request_id, user_id, listing_id, requested_at, scheduled_for, total_estimated, status |
| **Provider Match** | match_id, request_id, provider_id, offered_at, response, responded_at |
| **Payment Authorization** | auth_id, request_id, amount_authorized, payment_method, authorized_at, captured_at |
| **Delivery / Service** | delivery_id, request_id, provider_id, started_at, completed_at, distance_km, actual_amount, rating |

## Match Responses

`ACCEPTED`, `DECLINED`, `TIMEOUT`, `PROVIDER_CANCELLED`

## Cancellation Reasons

`USER_CHANGED_MIND`, `LONG_WAIT`, `PROVIDER_NO_SHOW`, `WRONG_ADDRESS`, `PRICE_CHANGE`, `ITEM_UNAVAILABLE`

## Business Rules

- **Date chain**: search ≤ booking_request ≤ provider_accepted ≤ payment_authorized ≤ delivery_started ≤ delivery_completed
- **Match SLA**: requests must be matched within target seconds; un-matched requests time out and refund any auth
- **Payment integrity**: actual_amount may differ from estimated due to tip / upcharge / route change; capture ≤ authorized except where the platform contract permits adjustment
- **Status transitions**: request `created` → `matched` → `in_progress` → `completed` / `cancelled`
- **Tip ordering**: tips post after delivery_completed; cannot exceed N% of subtotal in most platform rules

## Realism Benchmarks

- **Search-to-booking conversion**: 5–15% (high abandonment, especially food delivery)
- **Provider match time**: median 15–60s for ride-share; 30–180s for delivery; 5–15% un-matched at peak demand
- **Cancellation rate**: 3–8% by user; 1–3% by provider; cancellation fees apply after acceptance
- **Tip share**: 60–80% of completed deliveries receive a tip; tip averages 10–20% of subtotal
- **Distance distribution**: median food delivery 2–5 km; ride-share 4–10 km; varies dramatically by metro density
- **Rating distribution**: heavily skewed — ~85% are 5-star; ratings ≤3 are rare and trigger review workflows

## Field Generators

`identifiers`, `dates`, `amounts`, `address`, `country`, `percentage` (match rate, cancel rate, tip rate), `person`
