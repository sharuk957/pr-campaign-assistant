from typing import Optional
from sqlalchemy.orm import Session

from app.ai.schemas import AnalysisResult
from app.models.analysis import Analysis


class AnalysisRepository:
    def upsert(
        self, db: Session, campaign_id: str, journalist_id: str, result: AnalysisResult
    ) -> Analysis:
        existing = self.get_by_journalist_id(db, journalist_id)

        if existing:
            existing.score = result.score
            existing.priority = result.priority
            existing.reasons = result.reasons
            existing.supporting_evidence = result.supporting_evidence
            existing.concerns = result.concerns
            db.commit()
            db.refresh(existing)
            return existing

        analysis = Analysis(
            campaign_id=campaign_id,
            journalist_id=journalist_id,
            score=result.score,
            priority=result.priority,
            reasons=result.reasons,
            supporting_evidence=result.supporting_evidence,
            concerns=result.concerns,
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        return analysis

    def get_by_journalist_id(self, db: Session, journalist_id: str) -> Optional[Analysis]:
        return db.query(Analysis).filter(Analysis.journalist_id == journalist_id).first()

    def list_by_campaign(self, db: Session, campaign_id: str) -> list[Analysis]:
        return (
            db.query(Analysis)
            .filter(Analysis.campaign_id == campaign_id)
            .order_by(Analysis.score.desc())
            .all()
        )
