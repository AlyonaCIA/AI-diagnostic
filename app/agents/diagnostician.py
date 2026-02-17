"""
File: app/agents/diagnostician.py
Description: AI Agent that generates actionable fix suggestions for PLC errors
using deterministic metadata and XML context.
Uses configurable LLM providers (Gemini by default, extensible to OpenAI/Anthropic).
"""

import os
from typing import Any, Dict

from loguru import logger

from app.agents.llm_provider import GeminiProvider, LLMProvider
from app.agents.schemas import DiagnosticReport


class PLCDiagnosticAgent:
    """
    Expert AI Agent specializing in IEC 61131-3 and industrial automation.
    Uses configurable LLM providers for flexibility and extensibility.
    """

    def __init__(self, provider: LLMProvider = None):
        """
        Initialize the diagnostic agent.

        Args:
            provider: LLM provider instance. If None, uses Gemini (default).
                     If GEMINI_API_KEY is not set and provider is None,
                     provider will be None (useful for testing).
        """
        if provider is None:
            # Try to initialize default Gemini provider
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                self.provider = GeminiProvider(api_key)
            else:
                # Don't raise error here - allow instantiation for tests
                # Error will occur when actually calling get_fix_suggestions
                logger.warning(
                    "GEMINI_API_KEY not found - LLM provider not initialized"
                )
                self.provider = None
        else:
            self.provider = provider

    def get_fix_suggestions(
        self, metadata: Dict[str, Any], xml_context: str
    ) -> DiagnosticReport:
        """
        Generate fix suggestions using the configured LLM provider.

        Args:
            metadata: Parsed error metadata
            xml_context: Relevant XML code snippet

        Returns:
            DiagnosticReport with classification and suggestions

        Raises:
            ValueError: If no provider is available
        """
        if self.provider is None:
            raise ValueError(
                "LLM provider not initialized. Set GEMINI_API_KEY environment variable."
            )
        return self.provider.get_fix_suggestions(metadata, xml_context)
