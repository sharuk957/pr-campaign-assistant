from typing import Literal
from pydantic import BaseModel, Field


class CampaignContext(BaseModel):
    """Campaign information supplied to the AI as grounding context."""

    name: str
    company_name: str
    product_description: str
    campaign_description: str
    target_audience: str
    key_topics: str
    desired_outcome: str


class JournalistContext(BaseModel):
    """Journalist information supplied to the AI as grounding context."""

    name: str
    publication: str
    role: str
    topics: str
    bio: str
    recent_articles: str


class AnalysisResult(BaseModel):
    """Structured result of analyzing a journalist's relevance to a campaign."""

    score: int = Field(..., ge=0, le=100)
    priority: Literal["high", "medium", "low"]
    reasons: list[str]
    supporting_evidence: list[str]
    concerns: list[str] = Field(default_factory=list)


class PitchResult(BaseModel):
    """Structured result of a generated outreach pitch."""

    subject: str
    body: str
