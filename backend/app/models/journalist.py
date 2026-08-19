import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, String, Text

from app.db.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Journalist(Base):
    __tablename__ = "journalists"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    campaign_id = Column(String(36), ForeignKey("campaigns.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    publication = Column(String(255), nullable=False)
    role = Column(String(255), nullable=False)
    topics = Column(Text, nullable=False, default="")
    bio = Column(Text, nullable=False, default="")
    recent_articles = Column(Text, nullable=False, default="")
    created_at = Column(DateTime, default=utc_now, nullable=False)
