import uuid
from datetime import datetime, timezone
from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String

from app.db.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    campaign_id = Column(String(36), ForeignKey("campaigns.id"), nullable=False, index=True)
    journalist_id = Column(
        String(36), ForeignKey("journalists.id"), nullable=False, unique=True, index=True
    )
    score = Column(Integer, nullable=False)
    priority = Column(String(20), nullable=False)
    reasons = Column(JSON, nullable=False, default=list)
    supporting_evidence = Column(JSON, nullable=False, default=list)
    concerns = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime, default=utc_now, nullable=False)
