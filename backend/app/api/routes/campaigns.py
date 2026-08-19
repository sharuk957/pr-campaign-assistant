from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.campaign import CampaignCreate, CampaignResponse
from app.services.campaign_service import CampaignService

router = APIRouter(prefix="/campaigns", tags=["campaigns"])
campaign_service = CampaignService()


@router.post(
    "",
    response_model=CampaignResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new campaign",
)
def create_campaign(
    payload: CampaignCreate,
    db: Session = Depends(get_db),
) -> CampaignResponse:
    campaign = campaign_service.create_campaign(db, payload)
    return CampaignResponse.model_validate(campaign)


@router.get(
    "/{campaign_id}",
    response_model=CampaignResponse,
    summary="Get a campaign by ID",
)
def get_campaign(
    campaign_id: str,
    db: Session = Depends(get_db),
) -> CampaignResponse:
    campaign = campaign_service.get_campaign(db, campaign_id)
    return CampaignResponse.model_validate(campaign)


@router.get(
    "",
    response_model=list[CampaignResponse],
    summary="List all campaigns",
)
def list_campaigns(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
) -> list[CampaignResponse]:
    campaigns = campaign_service.list_campaigns(db, limit=limit, offset=offset)
    return [CampaignResponse.model_validate(c) for c in campaigns]
