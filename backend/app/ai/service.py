import json
from typing import Optional, Type, TypeVar
from pydantic import BaseModel, ValidationError

from app.ai.client import GroqClient, LLMClient
from app.ai.errors import AIProviderError, AIResponseError
from app.ai.grounding import build_vocabulary, extract_journalist_coverage_claims, find_ungrounded_items
from app.ai.prompts import (
    ANALYSIS_SYSTEM_PROMPT,
    PITCH_SYSTEM_PROMPT,
    build_analysis_user_prompt,
    build_pitch_user_prompt,
)
from app.ai.schemas import AnalysisResult, CampaignContext, JournalistContext, PitchResult

ModelT = TypeVar("ModelT", bound=BaseModel)


class AIService:
    """Isolated entry point for all AI-backed operations.

    The rest of the application should depend only on this service, never on the LLM
    provider client directly, so the AI integration can be swapped or mocked freely.
    """

    def __init__(self, client: Optional[LLMClient] = None):
        self.client = client or GroqClient()

    def analyze_journalist(
        self, campaign: CampaignContext, journalist: JournalistContext
    ) -> AnalysisResult:
        user_prompt = build_analysis_user_prompt(campaign, journalist)
        raw_response = self._complete(ANALYSIS_SYSTEM_PROMPT, user_prompt)
        result = self._parse_response(raw_response, AnalysisResult)
        self._validate_analysis_grounding(result, journalist)
        return result

    def generate_pitch(
        self,
        campaign: CampaignContext,
        journalist: JournalistContext,
        analysis: AnalysisResult,
    ) -> PitchResult:
        user_prompt = build_pitch_user_prompt(campaign, journalist, analysis)
        raw_response = self._complete(PITCH_SYSTEM_PROMPT, user_prompt)
        result = self._parse_response(raw_response, PitchResult)
        self._validate_pitch_grounding(result, journalist)
        return result

    def _complete(self, system_prompt: str, user_prompt: str) -> str:
        try:
            return self.client.complete(system_prompt, user_prompt)
        except AIProviderError:
            raise
        except Exception as exc:
            raise AIProviderError(f"Unexpected error calling the AI provider: {exc}") from exc

    @staticmethod
    def _parse_response(raw_response: str, model: Type[ModelT]) -> ModelT:
        try:
            data = json.loads(raw_response)
        except (TypeError, ValueError) as exc:
            raise AIResponseError(
                f"AI response was not valid JSON: {exc}", details=raw_response
            ) from exc

        try:
            return model.model_validate(data)
        except ValidationError as exc:
            raise AIResponseError(
                "AI response did not match the expected schema", details=exc.errors()
            ) from exc

    @staticmethod
    def _validate_analysis_grounding(result: AnalysisResult, journalist: JournalistContext) -> None:
        """Reject supporting evidence that does not reference the journalist's actual information."""
        vocabulary = build_vocabulary(journalist.topics, journalist.bio, journalist.recent_articles)
        ungrounded = find_ungrounded_items(result.supporting_evidence, vocabulary)
        if ungrounded:
            raise AIResponseError(
                "AI response included supporting evidence not grounded in the journalist's information",
                details={"ungrounded_evidence": ungrounded},
            )

    @staticmethod
    def _validate_pitch_grounding(result: PitchResult, journalist: JournalistContext) -> None:
        """Reject pitches that assert journalist coverage topics not present in their actual information."""
        vocabulary = build_vocabulary(journalist.topics, journalist.bio, journalist.recent_articles)
        claims = extract_journalist_coverage_claims(result.body) + extract_journalist_coverage_claims(
            result.subject
        )
        ungrounded = find_ungrounded_items(claims, vocabulary)
        if ungrounded:
            raise AIResponseError(
                "AI response made unsupported claims about the journalist's coverage",
                details={"ungrounded_claims": ungrounded},
            )
