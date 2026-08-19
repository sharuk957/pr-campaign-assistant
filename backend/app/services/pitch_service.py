from typing import Optional
from sqlalchemy.orm import Session

from app.ai import AIService, AIServiceError
from app.ai.schemas import AnalysisResult
from app.core.errors import AIGenerationError, BadRequestError, NotFoundError
from app.models.campaign import Campaign
from app.models.journalist import Journalist
from app.models.pitch import Pitch
from app.repositories.analysis_repository import AnalysisRepository
from app.repositories.campaign_repository import CampaignRepository
from app.repositories.journalist_repository import JournalistRepository
from app.repositories.pitch_repository import PitchRepository
from app.services.ai_context import to_campaign_context, to_journalist_context


class PitchService:
    def __init__(
        self,
        repository: Optional[PitchRepository] = None,
        campaign_repository: Optional[CampaignRepository] = None,
        journalist_repository: Optional[JournalistRepository] = None,
        analysis_repository: Optional[AnalysisRepository] = None,
        ai_service: Optional[AIService] = None,
    ):
        self.repository = repository or PitchRepository()
        self.campaign_repository = campaign_repository or CampaignRepository()
        self.journalist_repository = journalist_repository or JournalistRepository()
        self.analysis_repository = analysis_repository or AnalysisRepository()
        self.ai_service = ai_service or AIService()

    def _get_campaign_or_raise(self, db: Session, campaign_id: str) -> Campaign:
        campaign = self.campaign_repository.get_by_id(db, campaign_id)
        if not campaign:
            raise NotFoundError(message=f"Campaign with ID '{campaign_id}' not found")
        return campaign

    def _get_journalist_or_raise(self, db: Session, campaign_id: str, journalist_id: str) -> Journalist:
        journalist = self.journalist_repository.get_by_id(db, journalist_id)
        if not journalist or journalist.campaign_id != campaign_id:
            raise NotFoundError(message=f"Journalist with ID '{journalist_id}' not found")
        return journalist

    def generate_pitch(self, db: Session, campaign_id: str, journalist_id: str) -> Pitch:
        campaign = self._get_campaign_or_raise(db, campaign_id)
        journalist = self._get_journalist_or_raise(db, campaign_id, journalist_id)

        analysis = self.analysis_repository.get_by_journalist_id(db, journalist_id)
        if not analysis or analysis.campaign_id != campaign_id:
            raise BadRequestError(
                message="Run relevance analysis for this journalist before generating a pitch"
            )

        campaign_context = to_campaign_context(campaign)
        journalist_context = to_journalist_context(journalist)
        analysis_result = AnalysisResult(
            score=analysis.score,
            priority=analysis.priority,
            reasons=analysis.reasons,
            supporting_evidence=analysis.supporting_evidence,
            concerns=analysis.concerns,
        )

        try:
            pitch_result = self.ai_service.generate_pitch(
                campaign_context, journalist_context, analysis_result
            )
        except AIServiceError as exc:
            raise AIGenerationError(message=exc.message, details=exc.details) from exc

        return self.repository.upsert(db, campaign_id, journalist_id, pitch_result)

    def get_pitch(self, db: Session, campaign_id: str, journalist_id: str) -> Pitch:
        self._get_campaign_or_raise(db, campaign_id)
        self._get_journalist_or_raise(db, campaign_id, journalist_id)
        pitch = self.repository.get_by_journalist_id(db, journalist_id)
        if not pitch or pitch.campaign_id != campaign_id:
            raise NotFoundError(
                message=f"No pitch found for journalist '{journalist_id}' in this campaign"
            )
        return pitch
