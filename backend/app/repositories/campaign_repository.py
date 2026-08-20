from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.campaign import Campaign


class CampaignRepository:
    def create(self, db: Session, campaign: Campaign) -> Campaign:
        db.add(campaign)
        db.commit()
        db.refresh(campaign)
        return campaign

    def get_by_id(self, db: Session, campaign_id: str) -> Optional[Campaign]:
        return db.query(Campaign).filter(Campaign.id == campaign_id).first()

    def update(self, db: Session, campaign: Campaign) -> Campaign:
        db.commit()
        db.refresh(campaign)
        return campaign

    def list_all(self, db: Session, limit: int = 100, offset: int = 0) -> list[Campaign]:
        return (
            db.query(Campaign)
            .order_by(Campaign.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def delete(self, db: Session, campaign: Campaign) -> None:
        db.delete(campaign)
        db.commit()
