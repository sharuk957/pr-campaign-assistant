import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, String, Text

from app.db.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String(255), nullable=False)
    company_name = Column(String(255), nullable=False)
    product_description = Column(Text, nullable=False)
    campaign_description = Column(Text, nullable=False)
    target_audience = Column(Text, nullable=False)
    key_topics = Column(Text, nullable=False)
    desired_outcome = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
