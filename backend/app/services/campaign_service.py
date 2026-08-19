from typing import Optional
from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.models.campaign import Campaign
from app.repositories.campaign_repository import CampaignRepository
from app.schemas.campaign import CampaignCreate


class CampaignService:
    def __init__(self, repository: Optional[CampaignRepository] = None):
        self.repository = repository or CampaignRepository()

    def create_campaign(self, db: Session, data: CampaignCreate) -> Campaign:
        campaign = Campaign(
            name=data.name.strip(),
            company_name=data.company_name.strip(),
            product_description=data.product_description.strip(),
            campaign_description=data.campaign_description.strip(),
            target_audience=data.target_audience.strip(),
            key_topics=data.key_topics.strip(),
            desired_outcome=data.desired_outcome.strip(),
        )
        return self.repository.create(db, campaign)

    def get_campaign(self, db: Session, campaign_id: str) -> Campaign:
        campaign = self.repository.get_by_id(db, campaign_id)
        if not campaign:
            raise NotFoundError(message=f"Campaign with ID '{campaign_id}' not found")
        return campaign

    def list_campaigns(self, db: Session, limit: int = 100, offset: int = 0) -> list[Campaign]:
        return self.repository.list_all(db, limit=limit, offset=offset)
