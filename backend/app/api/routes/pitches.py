from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.pitch import PitchResponse
from app.services.pitch_service import PitchService

router = APIRouter(
    prefix="/campaigns/{campaign_id}/journalists/{journalist_id}/pitch", tags=["pitch"]
)

_pitch_service = PitchService()


def get_pitch_service() -> PitchService:
    return _pitch_service


@router.post(
    "",
    response_model=PitchResponse,
    summary="Generate (or regenerate) an outreach pitch for a journalist",
)
def generate_pitch(
    campaign_id: str,
    journalist_id: str,
    db: Session = Depends(get_db),
    service: PitchService = Depends(get_pitch_service),
) -> PitchResponse:
    pitch = service.generate_pitch(db, campaign_id, journalist_id)
    return PitchResponse.model_validate(pitch)


@router.get(
    "",
    response_model=PitchResponse,
    summary="Get the stored pitch for a journalist",
)
def get_pitch(
    campaign_id: str,
    journalist_id: str,
    db: Session = Depends(get_db),
    service: PitchService = Depends(get_pitch_service),
) -> PitchResponse:
    pitch = service.get_pitch(db, campaign_id, journalist_id)
    return PitchResponse.model_validate(pitch)
