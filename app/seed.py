from __future__ import annotations

from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from .models import Advertiser, Campaign, UserEngagement


def seed_data(db: Session) -> None:
    if db.query(Advertiser).count() > 0:
        return

    advertisers = [
        Advertiser(id=1, name='Acme Corp'),
        Advertiser(id=2, name='Globex'),
    ]
    db.add_all(advertisers)
    db.flush()

    campaigns = [
        Campaign(id=101, advertiser_id=1, name='Spring Sale', clicks=1200, impressions=40000, ad_spend=850.50),
        Campaign(id=102, advertiser_id=1, name='Retargeting Push', clicks=650, impressions=15000, ad_spend=420.75),
        Campaign(id=201, advertiser_id=2, name='Brand Awareness', clicks=2100, impressions=90000, ad_spend=1600.00),
    ]
    db.add_all(campaigns)
    db.flush()

    engagements = [
        UserEngagement(user_id=1, campaign_id=101, ad_id='AD-1001', engagement_type='click', engaged_at=datetime.utcnow() - timedelta(minutes=5)),
        UserEngagement(user_id=1, campaign_id=102, ad_id='AD-1002', engagement_type='view', engaged_at=datetime.utcnow() - timedelta(minutes=3)),
        UserEngagement(user_id=2, campaign_id=201, ad_id='AD-2001', engagement_type='click', engaged_at=datetime.utcnow() - timedelta(minutes=7)),
        UserEngagement(user_id=1, campaign_id=101, ad_id='AD-1003', engagement_type='purchase', engaged_at=datetime.utcnow() - timedelta(minutes=1)),
    ]
    db.add_all(engagements)
    db.commit()
