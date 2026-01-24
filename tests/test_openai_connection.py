"""
File: tests/test_gemini_connection.py
Description: Test Gemini API connection and structured output integrity.
"""

import pytest
import os
from app.agents.diagnostician import PLCDiagnosticAgent
from app.agents.schemas import DiagnosticReport


def test_gemini_structured_output_integrity():
    """
    Validates that Gemini correctly parses the PLC context into our 
    Pydantic DiagnosticReport schema.
    """
    # Skip if no API key is present to avoid CI failures
    if not os.getenv("GEMINI_API_KEY"):
        pytest.skip("Skipping: GEMINI_API_KEY not found.")

    agent = PLCDiagnosticAgent()
    
    # Mock metadata and context
    mock_metadata = {"stage": "iec_compilation", "line": 30}
    mock_context = "LocalVar1 := LocalVar0; (* LocalVar1 is CONSTANT *)"

    # Act
    report = agent.get_fix_suggestions(mock_metadata, mock_context)

    # Assert
    assert isinstance(report, DiagnosticReport)
    assert report.stage == "iec_compilation"
    assert len(report.suggestions) > 0
    assert report.suggestions[0].confidence >= 0.0
    assert all(0.0 <= s.confidence <= 1.0 for s in report.suggestions)
