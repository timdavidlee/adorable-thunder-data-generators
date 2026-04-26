# Lead-to-Opportunity / Lead-to-Cash (L2O)

**Flow:** Lead Capture → Qualification → Opportunity → Quote → Negotiation → Contract → Close → Revenue Recognition

L2O covers the B2B sales cycle from initial prospect identification through contract execution and revenue booking.

## Records

| Record | Key Fields |
|---|---|
| **Lead** | lead_id, first_name, last_name, email, phone, company, source, created_date, status |
| **Contact** | contact_id, company_id, first_name, last_name, title, email, phone, country |
| **Opportunity** | opp_id, contact_id, company, stage, deal_value, close_date, owner_email, probability |
| **Quote** | quote_id, opp_id, line_items (sku, qty, unit_price, discount), total_amount, expiry_date |
| **Contract** | contract_id, opp_id, contract_type, start_date, end_date, total_value, payment_terms, status |

## Pipeline Stages & Probabilities

| Stage | Probability | Typical Duration |
|---|---|---|
| Prospecting | 5% | 1–4 weeks |
| Qualification | 15% | 1–3 weeks |
| Discovery | 25% | 2–4 weeks |
| Proposal | 40% | 1–3 weeks |
| Negotiation | 60% | 1–4 weeks |
| Closed Won | 100% | — |
| Closed Lost | 0% | — |

## Lead Sources

`WEB_FORM`, `PAID_SEARCH`, `CONTENT_DOWNLOAD`, `REFERRAL`, `TRADE_SHOW`, `COLD_OUTREACH`, `PARTNER`, `WEBINAR`

## Contract Types

`MSA` (Master Services Agreement), `SOW` (Statement of Work), `NDA`, `RESELLER_AGREEMENT`, `PILOT`

## Business Rules

- **Date chain**: lead_created ≤ opp_created ≤ quote_date ≤ contract_start; close_date is in the past for Closed Won/Lost
- **Probability**: monotonically increases through stages; Closed Won = 100%, Closed Lost = 0%
- **Deal value**: quote total ≈ contract total (discounts may differ); large gaps are a flag
- **Coverage ratio**: healthy pipeline = 3–4× quarterly quota in open opportunities

## Realism Benchmarks

- **Lead-to-opportunity conversion**: 2–5%
- **Opportunity win rate**: 20–30% for enterprise B2B
- **Average sales cycle**: 30–180 days depending on deal size
- **Deal sizes**: SMB $5k–$50k; mid-market $50k–$500k; enterprise $500k–$5M+
- **Stage distribution**: most open opportunities cluster in Qualification and Proposal; few in Negotiation

## Field Generators

`person`, `phone`, `company`, `country`, `address`, `amounts`, `dates`, `payment_terms`, `identifiers`, `product_code`, `percentage` (discount)
