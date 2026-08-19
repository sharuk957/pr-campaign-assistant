import csv
import io
import re
from typing import Optional
from sqlalchemy.orm import Session

from app.core.errors import BadRequestError, NotFoundError
from app.models.journalist import Journalist
from app.repositories.campaign_repository import CampaignRepository
from app.repositories.journalist_repository import JournalistRepository
from app.schemas.journalist import (
    JournalistCreate,
    JournalistImportResult,
    JournalistImportRowError,
    JournalistResponse,
)

REQUIRED_CSV_COLUMNS = ["name", "email", "publication", "role", "topics", "bio", "recent_articles"]
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MAX_CSV_SIZE_BYTES = 2 * 1024 * 1024


class JournalistService:
    def __init__(
        self,
        repository: Optional[JournalistRepository] = None,
        campaign_repository: Optional[CampaignRepository] = None,
    ):
        self.repository = repository or JournalistRepository()
        self.campaign_repository = campaign_repository or CampaignRepository()

    def _ensure_campaign_exists(self, db: Session, campaign_id: str) -> None:
        if not self.campaign_repository.get_by_id(db, campaign_id):
            raise NotFoundError(message=f"Campaign with ID '{campaign_id}' not found")

    def create_journalist(self, db: Session, campaign_id: str, data: JournalistCreate) -> Journalist:
        self._ensure_campaign_exists(db, campaign_id)
        journalist = Journalist(
            campaign_id=campaign_id,
            name=data.name.strip(),
            email=data.email.strip(),
            publication=data.publication.strip(),
            role=data.role.strip(),
            topics=data.topics.strip(),
            bio=data.bio.strip(),
            recent_articles=data.recent_articles.strip(),
        )
        return self.repository.create(db, journalist)

    def get_journalist(self, db: Session, campaign_id: str, journalist_id: str) -> Journalist:
        self._ensure_campaign_exists(db, campaign_id)
        journalist = self.repository.get_by_id(db, journalist_id)
        if not journalist or journalist.campaign_id != campaign_id:
            raise NotFoundError(message=f"Journalist with ID '{journalist_id}' not found")
        return journalist

    def list_journalists(
        self, db: Session, campaign_id: str, limit: int = 200, offset: int = 0
    ) -> list[Journalist]:
        self._ensure_campaign_exists(db, campaign_id)
        return self.repository.list_by_campaign(db, campaign_id, limit=limit, offset=offset)

    def import_csv(self, db: Session, campaign_id: str, file_bytes: bytes) -> JournalistImportResult:
        self._ensure_campaign_exists(db, campaign_id)

        if not file_bytes:
            raise BadRequestError(message="The uploaded CSV file is empty")

        if len(file_bytes) > MAX_CSV_SIZE_BYTES:
            raise BadRequestError(
                message="The uploaded CSV file exceeds the maximum allowed size of 2MB"
            )

        try:
            text = file_bytes.decode("utf-8-sig")
        except UnicodeDecodeError:
            raise BadRequestError(message="The uploaded file is not a valid UTF-8 encoded CSV")

        reader = csv.DictReader(io.StringIO(text))
        if not reader.fieldnames:
            raise BadRequestError(message="The CSV file has no header row")

        normalized_fields = {field.strip().lower() for field in reader.fieldnames if field}
        missing_columns = [column for column in REQUIRED_CSV_COLUMNS if column not in normalized_fields]
        if missing_columns:
            raise BadRequestError(
                message="The CSV file is missing required columns: " + ", ".join(missing_columns),
                details={"missing_columns": missing_columns},
            )

        errors: list[JournalistImportRowError] = []
        to_create: list[Journalist] = []
        total_rows = 0

        for row_number, row in enumerate(reader, start=2):
            total_rows += 1
            normalized_row = {
                (key.strip().lower() if key else key): (value or "").strip()
                for key, value in row.items()
            }

            name = normalized_row.get("name", "")
            email = normalized_row.get("email", "")
            publication = normalized_row.get("publication", "")
            role = normalized_row.get("role", "")
            topics = normalized_row.get("topics", "")
            bio = normalized_row.get("bio", "")
            recent_articles = normalized_row.get("recent_articles", "")

            row_errors = []
            if not name:
                row_errors.append("name is required")
            if not email:
                row_errors.append("email is required")
            elif not EMAIL_PATTERN.match(email):
                row_errors.append("email is invalid")
            if not publication:
                row_errors.append("publication is required")
            if not role:
                row_errors.append("role is required")

            if row_errors:
                errors.append(JournalistImportRowError(row=row_number, message="; ".join(row_errors)))
                continue

            to_create.append(
                Journalist(
                    campaign_id=campaign_id,
                    name=name,
                    email=email,
                    publication=publication,
                    role=role,
                    topics=topics,
                    bio=bio,
                    recent_articles=recent_articles,
                )
            )

        if total_rows == 0:
            raise BadRequestError(message="The CSV file contains no data rows")

        created = self.repository.bulk_create(db, to_create)

        return JournalistImportResult(
            imported_count=len(created),
            total_rows=total_rows,
            errors=errors,
            journalists=[JournalistResponse.model_validate(journalist) for journalist in created],
        )
