from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class JournalistCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Journalist name")
    email: str = Field(..., min_length=1, max_length=255, description="Journalist email address")
    publication: str = Field(..., min_length=1, max_length=255, description="Publication or outlet")
    role: str = Field(..., min_length=1, max_length=255, description="Role or title at the publication")
    topics: str = Field(default="", description="Topics covered, separated by commas or semicolons")
    bio: str = Field(default="", description="Short biography")
    recent_articles: str = Field(default="", description="Recent articles, separated by commas or semicolons")


class JournalistResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    campaign_id: str
    name: str
    email: str
    publication: str
    role: str
    topics: str
    bio: str
    recent_articles: str
    created_at: datetime


class JournalistImportRowError(BaseModel):
    row: int = Field(..., description="1-indexed CSV row number, including the header row")
    message: str


class JournalistImportResult(BaseModel):
    imported_count: int
    total_rows: int
    errors: list[JournalistImportRowError]
    journalists: list[JournalistResponse]
