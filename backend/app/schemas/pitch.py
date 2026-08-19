from datetime import datetime
from pydantic import BaseModel, ConfigDict


class PitchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    campaign_id: str
    journalist_id: str
    subject: str
    body: str
    created_at: datetime
