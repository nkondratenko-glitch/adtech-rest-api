from __future__ import annotations

import os
import time
from decimal import Decimal

from fastapi import Depends, FastAPI, HTTPException, Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .cache import get_cache_client, read_through_cache
from .database import Base, SessionLocal, engine, get_db
from .models import Campaign, UserEngagement
from .schemas import (
    AdvertiserSpendingResponse,
    CampaignPerformanceResponse,
    UserEngagementItem,
    UserEngagementsResponse,
)
from .seed import seed_data

DB_SIMULATED_DELAY_MS = int(os.getenv('DB_SIMULATED_DELAY_MS', '20'))

app = FastAPI(title='AdTech Performance API', version='1.0.0')


@app.on_event('startup')
def startup() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_data(db)
    try:
        get_cache_client().ping()
    except Exception:
        # Redis may be unavailable in local/dev mode; endpoints will fail only if cache is actually required.
        pass


def add_benchmark_headers(response: Response, started_at: float, source: str) -> None:
    duration_ms = (time.perf_counter() - started_at) * 1000
    response.headers['X-Response-Time-ms'] = f'{duration_ms:.2f}'
    response.headers['X-Data-Source'] = source


def simulate_db_latency() -> None:
    if DB_SIMULATED_DELAY_MS > 0:
        time.sleep(DB_SIMULATED_DELAY_MS / 1000)


@app.get('/health')
def healthcheck() -> dict[str, str]:
    return {'status': 'ok'}


@app.get('/campaign/{campaign_id}/performance', response_model=CampaignPerformanceResponse)
def get_campaign_performance(campaign_id: int, response: Response, db: Session = Depends(get_db)):
    started = time.perf_counter()

    def loader():
        simulate_db_latency()
        campaign = db.get(Campaign, campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail='Campaign not found')
        ctr = round((campaign.clicks / campaign.impressions) * 100, 4) if campaign.impressions else 0.0
        return {
            'campaign_id': campaign.id,
            'ctr': ctr,
            'clicks': campaign.clicks,
            'impressions': campaign.impressions,
            'ad_spend': float(campaign.ad_spend),
        }

    payload, source = read_through_cache(f'campaign:{campaign_id}:performance', 30, loader)
    add_benchmark_headers(response, started, source)
    return payload


@app.get('/advertiser/{advertiser_id}/spending', response_model=AdvertiserSpendingResponse)
def get_advertiser_spending(advertiser_id: int, response: Response, db: Session = Depends(get_db)):
    started = time.perf_counter()

    def loader():
        simulate_db_latency()
        total_spend = db.scalar(
            select(func.coalesce(func.sum(Campaign.ad_spend), 0)).where(Campaign.advertiser_id == advertiser_id)
        )
        if total_spend is None:
            total_spend = Decimal('0')
        return {
            'advertiser_id': advertiser_id,
            'total_ad_spend': float(total_spend),
        }

    payload, source = read_through_cache(f'advertiser:{advertiser_id}:spending', 300, loader)
    add_benchmark_headers(response, started, source)
    return payload


@app.get('/user/{user_id}/engagements', response_model=UserEngagementsResponse)
def get_user_engagements(user_id: int, response: Response, db: Session = Depends(get_db)):
    started = time.perf_counter()
    simulate_db_latency()
    rows = db.execute(
        select(UserEngagement, Campaign.name)
        .join(Campaign, Campaign.id == UserEngagement.campaign_id)
        .where(UserEngagement.user_id == user_id)
        .order_by(UserEngagement.engaged_at.desc())
    ).all()

    engagements = [
        UserEngagementItem(
            campaign_id=row[0].campaign_id,
            campaign_name=row[1],
            ad_id=row[0].ad_id,
            engagement_type=row[0].engagement_type,
            engaged_at=row[0].engaged_at,
        )
        for row in rows
    ]
    add_benchmark_headers(response, started, 'db')
    return {'user_id': user_id, 'engagements': engagements}
