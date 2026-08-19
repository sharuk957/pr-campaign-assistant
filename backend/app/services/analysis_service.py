from typing import Optional
from sqlalchemy.orm import Session

from app.ai import AIService, AIServiceError
from app.core.errors import NotFoundError
from app.models.analysis import Analysis
from app.models.campaign import Campaign
from app.repositories.analysis_repository import AnalysisRepository
from app.repositories.campaign_repository import CampaignRepository
from app.repositories.journalist_repository import JournalistRepository
from app.schemas.analysis import AnalysisResponse, CampaignAnalysisRunResult, JournalistAnalysisOutcome
from app.services.ai_context import to_campaign_context, to_journalist_context


class AnalysisService:
    def __init__(
        self,
        repository: Optional[AnalysisRepository] = None,
        campaign_repository: Optional[CampaignRepository] = None,
        journalist_repository: Optional[JournalistRepository] = None,
        ai_service: Optional[AIService] = None,
    ):
        self.repository = repository or AnalysisRepository()
        self.campaign_repository = campaign_repository or CampaignRepository()
        self.journalist_repository = journalist_repository or JournalistRepository()
        self.ai_service = ai_service or AIService()

    def _get_campaign_or_raise(self, db: Session, campaign_id: str) -> Campaign:
        campaign = self.campaign_repository.get_by_id(db, campaign_id)
        if not campaign:
            raise NotFoundError(message=f"Campaign with ID '{campaign_id}' not found")
        return campaign

    def run_campaign_analysis(self, db: Session, campaign_id: str) -> CampaignAnalysisRunResult:
        campaign = self._get_campaign_or_raise(db, campaign_id)
        journalists = self.journalist_repository.list_by_campaign(db, campaign_id, limit=1000)
        campaign_context = to_campaign_context(campaign)

        results: list[JournalistAnalysisOutcome] = []
        succeeded = 0
        failed = 0

        for journalist in journalists:
            journalist_context = to_journalist_context(journalist)

            try:
                ai_result = self.ai_service.analyze_journalist(campaign_context, journalist_context)
            except AIServiceError as exc:
                failed += 1
                results.append(
                    JournalistAnalysisOutcome(
                        journalist_id=journalist.id,
                        journalist_name=journalist.name,
                        status="failed",
                        error=exc.message,
                    )
                )
                continue

            analysis = self.repository.upsert(db, campaign_id, journalist.id, ai_result)
            succeeded += 1
            results.append(
                JournalistAnalysisOutcome(
                    journalist_id=journalist.id,
                    journalist_name=journalist.name,
                    status="success",
                    analysis=AnalysisResponse.model_validate(analysis),
                )
            )

        return CampaignAnalysisRunResult(
            campaign_id=campaign_id,
            total_journalists=len(journalists),
            succeeded=succeeded,
            failed=failed,
            results=results,
        )

    def list_analyses(self, db: Session, campaign_id: str) -> list[Analysis]:
        self._get_campaign_or_raise(db, campaign_id)
        return self.repository.list_by_campaign(db, campaign_id)

    def get_analysis_for_journalist(self, db: Session, campaign_id: str, journalist_id: str) -> Analysis:
        self._get_campaign_or_raise(db, campaign_id)
        analysis = self.repository.get_by_journalist_id(db, journalist_id)
        if not analysis or analysis.campaign_id != campaign_id:
            raise NotFoundError(
                message=f"No analysis found for journalist '{journalist_id}' in this campaign"
            )
        return analysis
