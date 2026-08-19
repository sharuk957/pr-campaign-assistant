from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.core.errors import BadRequestError
from app.db.session import get_db
from app.schemas.journalist import JournalistCreate, JournalistImportResult, JournalistResponse
from app.services.journalist_service import JournalistService

router = APIRouter(prefix="/campaigns/{campaign_id}/journalists", tags=["journalists"])
journalist_service = JournalistService()


@router.post(
    "",
    response_model=JournalistResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a journalist for a campaign",
)
def create_journalist(
    campaign_id: str,
    payload: JournalistCreate,
    db: Session = Depends(get_db),
) -> JournalistResponse:
    journalist = journalist_service.create_journalist(db, campaign_id, payload)
    return JournalistResponse.model_validate(journalist)


@router.get(
    "",
    response_model=list[JournalistResponse],
    summary="List journalists for a campaign",
)
def list_journalists(
    campaign_id: str,
    limit: int = 200,
    offset: int = 0,
    db: Session = Depends(get_db),
) -> list[JournalistResponse]:
    journalists = journalist_service.list_journalists(db, campaign_id, limit=limit, offset=offset)
    return [JournalistResponse.model_validate(j) for j in journalists]


@router.post(
    "/import",
    response_model=JournalistImportResult,
    summary="Import journalists for a campaign from a CSV file",
)
async def import_journalists(
    campaign_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> JournalistImportResult:
    filename = (file.filename or "").lower()
    if not filename.endswith(".csv"):
        raise BadRequestError(message="Only .csv files are supported")

    contents = await file.read()
    return journalist_service.import_csv(db, campaign_id, contents)


@router.get(
    "/{journalist_id}",
    response_model=JournalistResponse,
    summary="Get a journalist by ID",
)
def get_journalist(
    campaign_id: str,
    journalist_id: str,
    db: Session = Depends(get_db),
) -> JournalistResponse:
    journalist = journalist_service.get_journalist(db, campaign_id, journalist_id)
    return JournalistResponse.model_validate(journalist)
