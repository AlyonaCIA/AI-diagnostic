"""
File: app/agents/llm_provider.py
Description: Abstract LLM provider interface allowing easy switching between providers.
Implementations support Gemini, OpenAI, and other LLM services.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict

from app.agents.schemas import DiagnosticReport


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def get_fix_suggestions(
        self, metadata: Dict[str, Any], xml_context: str
    ) -> DiagnosticReport:
        """
        Generate fix suggestions for a PLC error.

        Args:
            metadata: Parsed error metadata (stage, line, severity)
            xml_context: Relevant XML code snippet

        Returns:
            DiagnosticReport with classification and suggestions
        """
        pass


class GeminiProvider(LLMProvider):
    """Google Gemini 2.5 Flash provider."""

    def __init__(self, api_key: str):
        """Initialize Gemini provider."""
        from google import genai
        from google.genai.types import GenerateContentConfig

        self.api_key = api_key
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-2.5-flash-lite"
        self.GenerateContentConfig = GenerateContentConfig

    def get_fix_suggestions(
        self, metadata: Dict[str, Any], xml_context: str
    ) -> DiagnosticReport:
        """Generate fix suggestions using Gemini."""
        from loguru import logger

        system_prompt = (
            "You are a Lead Automation Engineer. Analyze PLC compilation logs and project XML. "
            "Prioritize the root cause. If it's a 'constant_error', explain that CONSTANT variables "
            "cannot be modified in Structured Text. If it's a code generation crash with no ST code, "
            "explain the POU is empty."
        )

        user_prompt = (
            f"Build Stage: {metadata['stage']}\n"
            f"Error Line: {metadata['line']}\n"
            f"XML Context Snippet: \n{xml_context}\n\n"
            "Generate a diagnostic report with 1-3 actionable suggestions."
        )

        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=user_prompt,
                config=self.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    response_schema=DiagnosticReport,
                ),
            )
            return response.parsed

        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            raise


class OpenAIProvider(LLMProvider):
    """
    OpenAI GPT-4 provider (not currently used - requires paid API key).
    Keeping as reference for future implementation.
    """

    def __init__(self, api_key: str):
        """Initialize OpenAI provider."""
        # Uncomment when ready to use OpenAI
        # from openai import OpenAI
        # self.client = OpenAI(api_key=api_key)
        # self.model_id = "gpt-4-turbo-preview"
        pass

    def get_fix_suggestions(
        self, metadata: Dict[str, Any], xml_context: str
    ) -> DiagnosticReport:
        """
        Generate fix suggestions using OpenAI.

        Example implementation:
        ```python
        system_prompt = (
            "You are a Lead Automation Engineer specializing in PLC programming..."
        )

        user_prompt = (
            f"Build Stage: {metadata['stage']}\n"
            f"Error Line: {metadata['line']}\n"
            f"XML Context: {xml_context}\n\n"
            "Generate 1-3 actionable suggestions in JSON format."
        )

        response = self.client.chat.completions.create(
            model=self.model_id,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "DiagnosticReport",
                    "schema": DiagnosticReport.model_json_schema()
                }
            }
        )

        return DiagnosticReport.model_validate_json(response.choices[0].message.content)
        ```
        """
        raise NotImplementedError(
            "OpenAI provider not yet implemented. "
            "Requires paid OpenAI API key. "
            "See docstring for implementation guide."
        )


class AnthropicProvider(LLMProvider):
    """
    Anthropic Claude provider (not currently used - future implementation).
    Keeping as reference for extensibility.
    """

    def __init__(self, api_key: str):
        """Initialize Anthropic provider."""
        # Future: from anthropic import Anthropic
        pass

    def get_fix_suggestions(
        self, metadata: Dict[str, Any], xml_context: str
    ) -> DiagnosticReport:
        """
        Generate fix suggestions using Claude.

        Implementation would be similar to OpenAI but using Claude's API.
        """
        raise NotImplementedError(
            "Anthropic provider not yet implemented. "
            "See app/agents/llm_provider.py for reference implementation."
        )
