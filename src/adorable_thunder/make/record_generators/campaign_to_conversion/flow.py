from typing import ClassVar

import numpy as np
import pandas as pd

from adorable_thunder.make.record_generators.schemas import BaseGeneratorConfig

from .campaigns import CAMPAIGNS_TABLE_NAME, generate_campaigns
from .conversions import CONVERSIONS_TABLE_NAME, generate_conversions
from .engagement_events import ENGAGEMENT_EVENTS_TABLE_NAME, generate_engagement_events
from .impressions import IMPRESSIONS_TABLE_NAME, generate_impressions
from .lead_captures import LEAD_CAPTURES_TABLE_NAME, generate_lead_captures

FLOW_NAME = "campaign_to_conversion"

# Channel-specific engagement rates per the C2C brief
_CHANNEL_ENGAGEMENT_RATE: dict[str, float] = {
    "Email": 0.275,  # 20–35% open rate, midpoint
    "Paid Search": 0.05,  # 2–8% CTR, midpoint
    "Paid Social": 0.0125,  # 0.5–2% CTR, midpoint
    "Organic Search": 0.035,  # 2–5% CTR, midpoint
    "Display": 0.002,  # 0.1–0.3% CTR, midpoint
    "Events": 0.40,  # 30–50% attendance, midpoint
}
_ENGAGEMENT_TO_LEAD_RATE = 0.15  # ~15% click-to-lead form completion
_LEAD_TO_CONVERSION_RATE = 0.05  # ~5% lead-to-customer

# CPM rates derived from brief CPL midpoints × impression-to-lead rate (0.03 CTR × 0.15 = 0.0045)
# CPM = CPL_midpoint × 0.0045 × 1000
_CHANNEL_CPM: dict[str, float] = {
    "Email": 56.25,
    "Paid Search": 517.50,
    "Paid Social": 270.00,
    "Organic Search": 78.75,
    "Display": 135.00,
    "Events": 787.50,
}


class GeneratorConfig(BaseGeneratorConfig):
    name: ClassVar[str] = FLOW_NAME
    start_date: str = "2024-01-01"
    end_date: str = "2025-12-31"

    def make(self) -> dict[str, pd.DataFrame]:
        # n_samples controls campaign count; downstream stages are derived via funnel rates
        campaigns = generate_campaigns(self.n_samples, self.start_date, self.end_date)
        # Build a lookup so downstream stages can clip their dates to the campaign window
        campaign_end = campaigns.set_index("campaign_id")["end_date"]

        # Impressions per campaign = budget / channel_CPM * 1000, floored at 5
        cpm = campaigns["channel"].map(_CHANNEL_CPM)
        impressions_per_campaign = (
            (campaigns["budget_usd"] / cpm * 1000).round().clip(lower=5).astype(int)
        )

        # Expand campaign arrays to one row per impression, then generate
        camp_idx = np.repeat(np.arange(len(campaigns)), impressions_per_campaign.to_numpy())
        impressions = generate_impressions(
            campaign_ids=campaigns["campaign_id"].to_numpy()[camp_idx],
            campaign_channels=campaigns["channel"].to_numpy()[camp_idx],
            campaign_starts=campaigns["start_date"].iloc[camp_idx].reset_index(drop=True),
            campaign_ends=campaigns["end_date"].iloc[camp_idx].reset_index(drop=True),
        )
        # Engagements: sample per channel using channel-specific CTR/open-rate
        imp_channels = impressions["channel"].to_numpy()
        eng_parts: list[np.ndarray] = []
        for channel, rate in _CHANNEL_ENGAGEMENT_RATE.items():
            ch_indices = np.where(imp_channels == channel)[0]
            n_eng = min(int(len(ch_indices) * rate), len(ch_indices))
            if n_eng > 0:
                eng_parts.append(np.random.choice(ch_indices, size=n_eng, replace=False))
        eng_idx = np.concatenate(eng_parts) if eng_parts else np.array([], dtype=int)
        n_engagements = len(eng_idx)
        engagements = generate_engagement_events(
            n_engagements,
            impression_ids=impressions["impression_id"].to_numpy()[eng_idx],
            campaign_ids=impressions["campaign_id"].to_numpy()[eng_idx],
            contact_ids=impressions["contact_id"].to_numpy()[eng_idx],
            impression_dates=impressions["impression_date"].iloc[eng_idx].reset_index(drop=True),
        )
        eng_campaign_ends = pd.to_datetime(engagements["campaign_id"].map(campaign_end))
        engagements["engagement_date"] = pd.to_datetime(engagements["engagement_date"]).clip(
            upper=eng_campaign_ends
        )

        # Leads: ~15% of engagements — deduplicate contact+campaign pairs
        n_leads_raw = max(1, int(n_engagements * _ENGAGEMENT_TO_LEAD_RATE))
        lead_idx = np.random.choice(n_engagements, size=n_leads_raw, replace=False)
        lead_df = (
            pd.DataFrame(
                {
                    "campaign_id": engagements["campaign_id"].to_numpy()[lead_idx],
                    "contact_id": engagements["contact_id"].to_numpy()[lead_idx],
                    "engagement_date": engagements["engagement_date"]
                    .iloc[lead_idx]
                    .reset_index(drop=True),
                }
            )
            .drop_duplicates(subset=["campaign_id", "contact_id"])
            .reset_index(drop=True)
        )

        leads = generate_lead_captures(
            len(lead_df),
            campaign_ids=lead_df["campaign_id"].to_numpy(),
            contact_ids=lead_df["contact_id"].to_numpy(),
            engagement_dates=lead_df["engagement_date"],
        )
        lead_campaign_ends = pd.to_datetime(leads["campaign_id"].map(campaign_end))
        leads["captured_date"] = pd.to_datetime(leads["captured_date"]).clip(
            upper=lead_campaign_ends
        )

        # Conversions: ~5% of leads
        n_conversions = max(1, int(len(leads) * _LEAD_TO_CONVERSION_RATE))
        conv_idx = np.random.choice(len(leads), size=n_conversions, replace=False)
        conversions = generate_conversions(
            n_conversions,
            lead_ids=leads["lead_id"].to_numpy()[conv_idx],
            campaign_ids=leads["campaign_id"].to_numpy()[conv_idx],
            captured_dates=leads["captured_date"].iloc[conv_idx].reset_index(drop=True),
        )
        conv_campaign_ends = pd.to_datetime(conversions["campaign_id"].map(campaign_end))
        conversions["conversion_date"] = pd.to_datetime(conversions["conversion_date"]).clip(
            upper=conv_campaign_ends
        )

        return {
            CAMPAIGNS_TABLE_NAME: campaigns,
            IMPRESSIONS_TABLE_NAME: impressions,
            ENGAGEMENT_EVENTS_TABLE_NAME: engagements,
            LEAD_CAPTURES_TABLE_NAME: leads,
            CONVERSIONS_TABLE_NAME: conversions,
        }
