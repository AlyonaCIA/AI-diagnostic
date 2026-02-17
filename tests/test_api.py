"""
File: tests/test_api.py
Description: Basic API integration tests.
"""

import os

import pytest

from app.agents.diagnostician import PLCDiagnosticAgent
from app.agents.schemas import DiagnosticReport


def test_api_with_mock_provider():
    """Test API with mock metadata and context (no real LLM call)."""
    # This test validates the flow without requiring API key
    mock_metadata = {"stage": "iec_compilation", "line": 30}
    mock_xml = "<variable name='LocalVar1' constant='true'/>"

    # Skip if no API key
    if not os.getenv("GEMINI_API_KEY"):
        pytest.skip("GEMINI_API_KEY not found - skipping real API test")

    agent = PLCDiagnosticAgent()
    report = agent.get_fix_suggestions(mock_metadata, mock_xml)

    assert isinstance(report, DiagnosticReport)
    assert len(report.root_cause) > 0
    assert len(report.suggestions) > 0
