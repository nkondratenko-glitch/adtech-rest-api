from __future__ import annotations

from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Advertiser(Base):
    __tablename__ = 'advertisers'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    campaigns: Mapped[list['Campaign']] = relationship(back_populates='advertiser')


class Campaign(Base):
    __tablename__ = 'campaigns'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    advertiser_id: Mapped[int] = mapped_column(ForeignKey('advertisers.id'), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    clicks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    impressions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    ad_spend: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)

    advertiser: Mapped['Advertiser'] = relationship(back_populates='campaigns')
    engagements: Mapped[list['UserEngagement']] = relationship(back_populates='campaign')


class UserEngagement(Base):
    __tablename__ = 'user_engagements'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey('campaigns.id'), nullable=False, index=True)
    ad_id: Mapped[str] = mapped_column(String(50), nullable=False)
    engagement_type: Mapped[str] = mapped_column(String(32), nullable=False)
    engaged_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    campaign: Mapped['Campaign'] = relationship(back_populates='engagements')
