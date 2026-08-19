from typing import Optional
from sqlalchemy.orm import Session

from app.ai.schemas import PitchResult
from app.models.pitch import Pitch


class PitchRepository:
    def upsert(self, db: Session, campaign_id: str, journalist_id: str, result: PitchResult) -> Pitch:
        existing = self.get_by_journalist_id(db, journalist_id)

        if existing:
            existing.subject = result.subject
            existing.body = result.body
            db.commit()
            db.refresh(existing)
            return existing

        pitch = Pitch(
            campaign_id=campaign_id,
            journalist_id=journalist_id,
            subject=result.subject,
            body=result.body,
        )
        db.add(pitch)
        db.commit()
        db.refresh(pitch)
        return pitch

    def get_by_journalist_id(self, db: Session, journalist_id: str) -> Optional[Pitch]:
        return db.query(Pitch).filter(Pitch.journalist_id == journalist_id).first()
