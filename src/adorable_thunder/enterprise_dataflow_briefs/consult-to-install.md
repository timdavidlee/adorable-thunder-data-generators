# Consult-to-Install (C2I)

**Flow:** Lead Form → Qualification Call → In-Home Consultation → Quote → Financing Options → Contract → Permitting → Installation → Final Payment

C2I covers the home-services sales cycle (solar, HVAC, roofing, windows, remodeling) — high-ticket residential installs that hinge on an on-site visit, jurisdictional permitting, and milestone-based payment.

## Records

| Record | Key Fields |
|---|---|
| **Lead** | lead_id, source, captured_date, homeowner_name, address, phone, status |
| **Consultation** | consult_id, lead_id, scheduled_date, completed_date, sales_rep, outcome |
| **Quote** | quote_id, consult_id, system_size, base_price, options_total, total_price, valid_until |
| **Financing Application** | finance_id, quote_id, lender, amount_financed, term_months, apr, decision, decision_date |
| **Contract** | contract_id, quote_id, signed_date, deposit_amount, financed_amount, scheduled_install_date |
| **Permit** | permit_id, contract_id, jurisdiction, application_date, approval_date, status |
| **Installation** | install_id, contract_id, install_date, crew_lead, hours_on_site, status |
| **Milestone Payment** | payment_id, contract_id, milestone, amount, paid_date |

## Lead Sources

`PAID_SEARCH`, `FACEBOOK_LEAD_AD`, `WEB_FORM`, `REFERRAL`, `DOOR_KNOCK`, `EVENT`, `PARTNER` (e.g., utility programs)

## Payment Milestones

`DEPOSIT` (at signing), `PROGRESS` (material delivery / install start), `FINAL` (post-completion / inspection)

## Business Rules

- **Date chain**: lead_captured ≤ consult_date ≤ quote_date ≤ contract_signed ≤ permit_approved ≤ install_date ≤ final_payment_date
- **Amount integrity**: contract_total = quote_total; sum(milestone_payments) = contract_total
- **Permit gate**: install_date must be on or after permit_approval_date in regulated jurisdictions; un-permitted installs are a hard data flag
- **Status transitions**: lead `new` → `qualified` → `consult_scheduled` → `quoted` → `won` / `lost`; consult `scheduled` → `completed` / `no_show` / `cancelled`
- **Financing decision**: contract cannot be signed for financed deals until lender returns `approved`

## Realism Benchmarks

- **Funnel conversion**: lead → consult-scheduled 30–50%; consult → quote 70–85%; quote → close 25–40% for solar / roofing
- **Average ticket**: solar $20k–$60k; HVAC $5k–$15k; roofing $8k–$25k; windows $10k–$30k
- **Cycle time**: lead → install 30–120 days; permitting alone 14–60 days depending on jurisdiction
- **Financing attach rate**: 50–70% of solar installs are financed; cash deals trend higher-margin
- **Payment milestones**: deposit 10–25% at signing; progress 40–60% on material drop / install start; remainder on completion
- **Cancellation rate**: 5–15% of signed contracts cancel during permitting (cooling-off, re-shop, financing fall-through)

## Field Generators

`identifiers`, `dates`, `amounts`, `person`, `phone`, `address`, `country`, `percentage` (apr, attach rate, conversion), `payment_terms`
