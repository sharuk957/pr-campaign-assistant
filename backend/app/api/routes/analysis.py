from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.analysis import AnalysisResponse, CampaignAnalysisRunResult
from app.services.analysis_service import AnalysisService

router = APIRouter(prefix="/campaigns/{campaign_id}/analysis", tags=["analysis"])

_analysis_service = AnalysisService()


def get_analysis_service() -> AnalysisService:
    return _analysis_service


@router.post(
    "",
    response_model=CampaignAnalysisRunResult,
    summary="Run AI relevance analysis for every journalist in a campaign",
)
def run_analysis(
    campaign_id: str,
    db: Session = Depends(get_db),
    service: AnalysisService = Depends(get_analysis_service),
) -> CampaignAnalysisRunResult:
    return service.run_campaign_analysis(db, campaign_id)


@router.get(
    "",
    response_model=list[AnalysisResponse],
    summary="List stored analyses for a campaign, ranked by relevance score",
)
def list_analyses(
    campaign_id: str,
    db: Session = Depends(get_db),
    service: AnalysisService = Depends(get_analysis_service),
) -> list[AnalysisResponse]:
    analyses = service.list_analyses(db, campaign_id)
    return [AnalysisResponse.model_validate(a) for a in analyses]


@router.get(
    "/{journalist_id}",
    response_model=AnalysisResponse,
    summary="Get the stored analysis for one journalist",
)
def get_analysis_for_journalist(
    campaign_id: str,
    journalist_id: str,
    db: Session = Depends(get_db),
    service: AnalysisService = Depends(get_analysis_service),
) -> AnalysisResponse:
    analysis = service.get_analysis_for_journalist(db, campaign_id, journalist_id)
    return AnalysisResponse.model_validate(analysis)
