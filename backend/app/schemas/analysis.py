from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field


class AnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    campaign_id: str
    journalist_id: str
    score: int = Field(..., ge=0, le=100)
    priority: Literal["high", "medium", "low"]
    reasons: list[str]
    supporting_evidence: list[str]
    concerns: list[str]
    created_at: datetime


class JournalistAnalysisOutcome(BaseModel):
    """The outcome of analyzing a single journalist within a campaign-wide run."""

    journalist_id: str
    journalist_name: str
    status: Literal["success", "failed"]
    analysis: Optional[AnalysisResponse] = None
    error: Optional[str] = None


class CampaignAnalysisRunResult(BaseModel):
    campaign_id: str
    total_journalists: int
    succeeded: int
    failed: int
    results: list[JournalistAnalysisOutcome]
