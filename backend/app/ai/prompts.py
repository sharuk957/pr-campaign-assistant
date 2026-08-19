from app.ai.schemas import AnalysisResult, CampaignContext, JournalistContext

ANALYSIS_SYSTEM_PROMPT = """You are a PR strategist assistant. You evaluate how relevant a journalist \
is to a specific PR campaign, using only the campaign and journalist information you are given.

Do not invent facts about the journalist. Only reference topics, articles, or details that were \
explicitly provided. If the journalist's information does not support a strong match, reflect that \
honestly with a lower score and note it as a concern.

Respond with ONLY a JSON object in exactly this shape, with no extra commentary:
{
  "score": <integer 0-100>,
  "priority": "high" | "medium" | "low",
  "reasons": [<string>, ...],
  "supporting_evidence": [<string>, ...],
  "concerns": [<string>, ...]
}
"""

PITCH_SYSTEM_PROMPT = """You are a PR strategist assistant. You write concise, personalized outreach \
emails ("pitches") to journalists on behalf of a company running a PR campaign, using only the \
campaign, journalist, and relevance analysis information you are given.

Do not invent facts about the journalist or claim coverage areas that were not provided. Ground the \
pitch in the campaign's product, story angle, and the journalist's actual stated topics and background.

Respond with ONLY a JSON object in exactly this shape, with no extra commentary:
{
  "subject": <string>,
  "body": <string>
}
"""


def build_analysis_user_prompt(campaign: CampaignContext, journalist: JournalistContext) -> str:
    return f"""Campaign:
- Name: {campaign.name}
- Company: {campaign.company_name}
- Product/Service: {campaign.product_description}
- Campaign/Story Angle: {campaign.campaign_description}
- Target Audience: {campaign.target_audience}
- Key Topics: {campaign.key_topics}
- Desired Outcome: {campaign.desired_outcome}

Journalist:
- Name: {journalist.name}
- Publication: {journalist.publication}
- Role: {journalist.role}
- Topics Covered: {journalist.topics}
- Biography: {journalist.bio}
- Recent Articles: {journalist.recent_articles}

Evaluate how relevant this journalist is to this campaign."""


def build_pitch_user_prompt(
    campaign: CampaignContext, journalist: JournalistContext, analysis: AnalysisResult
) -> str:
    reasons = "\n".join(f"- {reason}" for reason in analysis.reasons) or "- None provided"
    evidence = "\n".join(f"- {item}" for item in analysis.supporting_evidence) or "- None provided"

    return f"""Campaign:
- Name: {campaign.name}
- Company: {campaign.company_name}
- Product/Service: {campaign.product_description}
- Campaign/Story Angle: {campaign.campaign_description}
- Target Audience: {campaign.target_audience}
- Key Topics: {campaign.key_topics}
- Desired Outcome: {campaign.desired_outcome}

Journalist:
- Name: {journalist.name}
- Publication: {journalist.publication}
- Role: {journalist.role}
- Topics Covered: {journalist.topics}
- Biography: {journalist.bio}
- Recent Articles: {journalist.recent_articles}

Relevance Analysis:
- Score: {analysis.score} ({analysis.priority} priority)
- Reasons:
{reasons}
- Supporting Evidence:
{evidence}

Write a personalized outreach pitch to this journalist for this campaign."""
