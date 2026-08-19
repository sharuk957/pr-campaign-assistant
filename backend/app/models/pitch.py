import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, String, Text

from app.db.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Pitch(Base):
    __tablename__ = "pitches"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    campaign_id = Column(String(36), ForeignKey("campaigns.id"), nullable=False, index=True)
    journalist_id = Column(
        String(36), ForeignKey("journalists.id"), nullable=False, unique=True, index=True
    )
    subject = Column(String(500), nullable=False)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
