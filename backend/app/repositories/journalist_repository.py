from typing import Optional
from sqlalchemy.orm import Session

from app.models.journalist import Journalist


class JournalistRepository:
    def create(self, db: Session, journalist: Journalist) -> Journalist:
        db.add(journalist)
        db.commit()
        db.refresh(journalist)
        return journalist

    def bulk_create(self, db: Session, journalists: list[Journalist]) -> list[Journalist]:
        if not journalists:
            return []
        db.add_all(journalists)
        db.commit()
        for journalist in journalists:
            db.refresh(journalist)
        return journalists

    def get_by_id(self, db: Session, journalist_id: str) -> Optional[Journalist]:
        return db.query(Journalist).filter(Journalist.id == journalist_id).first()

    def list_by_campaign(
        self, db: Session, campaign_id: str, limit: int = 200, offset: int = 0
    ) -> list[Journalist]:
        return (
            db.query(Journalist)
            .filter(Journalist.campaign_id == campaign_id)
            .order_by(Journalist.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
