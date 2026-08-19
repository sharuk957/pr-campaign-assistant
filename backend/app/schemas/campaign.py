from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class CampaignCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Campaign name")
    company_name: str = Field(..., min_length=1, max_length=255, description="Company name")
    product_description: str = Field(
        ..., min_length=1, description="Description of the product or service"
    )
    campaign_description: str = Field(
        ..., min_length=1, description="Description of the campaign or story angle"
    )
    target_audience: str = Field(
        ..., min_length=1, description="Target audience for the campaign"
    )
    key_topics: str = Field(
        ..., min_length=1, description="Key topics separated by commas or semicolons"
    )
    desired_outcome: str = Field(
        ..., min_length=1, description="Desired outcome or goal of the campaign"
    )


class CampaignResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    company_name: str
    product_description: str
    campaign_description: str
    target_audience: str
    key_topics: str
    desired_outcome: str
    created_at: datetime
