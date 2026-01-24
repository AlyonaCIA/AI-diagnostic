"""
File: tests/test_agent_integration.py
Description: End-to-end integration test for the AI Agent.
"""
import os
import pytest
from app.agents.diagnostician import PLCDiagnosticAgent
from app.agents.schemas import DiagnosticReport

def test_agent_connection():
    # Skip if no API key
    if not os.getenv("GEMINI_API_KEY"):
        pytest.skip("GEMINI_API_KEY not found - skipping real Gemini API test")
    
    # Arrange
    agent = PLCDiagnosticAgent()
    mock_metadata = {"stage": "iec_compilation", "line": 30}
    mock_context = "LocalVar1 := LocalVar0; (* LocalVar1 is a CONSTANT *)"

    # Act
    # This will make a real call to the Gemini API
    report = agent.get_fix_suggestions(mock_metadata, mock_context)

    # Assert
    assert isinstance(report, DiagnosticReport)
    assert len(report.suggestions) > 0
    print(f"\n AI Root Cause: {report.root_cause}")
