from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class CampaignPerformanceResponse(BaseModel):
    campaign_id: int
    ctr: float = Field(..., description='Click-through rate as a percentage')
    clicks: int
    impressions: int
    ad_spend: float
    source: str


class AdvertiserSpendingResponse(BaseModel):
    advertiser_id: int
    total_ad_spend: float
    source: str


class UserEngagementItem(BaseModel):
    campaign_id: int
    campaign_name: str
    ad_id: str
    engagement_type: str
    engaged_at: datetime


class UserEngagementsResponse(BaseModel):
    user_id: int
    engagements: list[UserEngagementItem]
