# Trial-to-Membership (T2M)

**Flow:** Ad Click → Website Visit → Free Trial Pass → First Visit → Tour with Sales Rep → Price Quote → Membership Signup

T2M covers the brick-and-mortar fitness sales funnel — from paid ad through in-person tour through signed membership. Distinct from `lead-to-opportunity` (B2B sales) and `signup-to-renewal` (digital SaaS): the funnel hinges on a physical visit, and conversion is driven by an in-person tour, not a digital onboarding sequence.

## Records

| Record | Key Fields |
|---|---|
| **Ad Click** | click_id, ad_id, channel, anonymous_id, landing_page, timestamp |
| **Trial Pass** | pass_id, prospect_id, issued_date, expires_date, redeemed_date, location_id |
| **Visit** | visit_id, prospect_id, location_id, check_in_time, check_out_time, activity |
| **Tour** | tour_id, prospect_id, sales_rep, scheduled_at, completed_at, outcome |
| **Quote** | quote_id, prospect_id, plan_tier, monthly_price, initiation_fee, valid_until |
| **Membership** | membership_id, customer_id, plan_tier, signed_date, start_date, monthly_price, payment_method |
| **Membership Status Change** | change_id, membership_id, change_type, effective_date, reason_code |

## Plan Tiers

| Tier | Typical Monthly Dues | Notes |
|---|---|---|
| Basic / Single Club | $20–$50 | Largest share at budget gyms |
| Mid-Tier / Multi-Club | $50–$120 | Includes group classes |
| Premium / Boutique | $150–$300 | Specialty (HIIT, cycling, yoga, climbing) |
| Family / Corporate | Varies | Discounted per-person rate |

## Tour Outcomes

`SIGNUP_SAME_DAY`, `SIGNUP_FOLLOW_UP`, `NO_SIGNUP`, `NO_SHOW`

## Business Rules

- **Date chain**: ad_click ≤ trial_issued ≤ first_visit ≤ tour ≤ quote ≤ signup
- **Trial expiration**: passes expire 7–14 days after issuance; un-redeemed passes have <2% conversion to membership
- **Membership status transitions**: prospect `lead` → `trial` → `visited` → `toured` → `member` / `lost`; member `active` → `paused` → `cancelled`
- **Cancellation notice**: most contracts require 30-day notice; cancellations effective at next billing cycle

## Realism Benchmarks

- **Funnel conversion**: ad click → trial pass 10–25%; trial pass → first visit 40–60% (redemption); visit → tour 50–70%; tour → signup 30–55% same-day close
- **Plan mix at signup**: basic ~50%, mid-tier ~30%, premium ~15%, family / corporate ~5%
- **Avg monthly dues**: $20–$50 budget gyms; $50–$120 mid-market; $150–$300+ boutique / luxury
- **Annual churn**: 30–40% in commercial gyms; 15–25% in boutique studios with engaged communities
- **Visit frequency**: median 4–8 visits/month for active members; <2 visits/month strongly predicts churn
- **Initiation fee waivers**: 40–70% of new signups receive a waived or discounted initiation fee (promo-driven)

## Field Generators

`identifiers`, `dates`, `amounts`, `person`, `phone`, `address`, `country`, `percentage` (conversion, churn rates)
