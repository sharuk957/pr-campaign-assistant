from app.ai.schemas import CampaignContext, JournalistContext
from app.models.campaign import Campaign
from app.models.journalist import Journalist


def to_campaign_context(campaign: Campaign) -> CampaignContext:
    return CampaignContext(
        name=campaign.name,
        company_name=campaign.company_name,
        product_description=campaign.product_description,
        campaign_description=campaign.campaign_description,
        target_audience=campaign.target_audience,
        key_topics=campaign.key_topics,
        desired_outcome=campaign.desired_outcome,
    )


def to_journalist_context(journalist: Journalist) -> JournalistContext:
    return JournalistContext(
        name=journalist.name,
        publication=journalist.publication,
        role=journalist.role,
        topics=journalist.topics,
        bio=journalist.bio,
        recent_articles=journalist.recent_articles,
    )
