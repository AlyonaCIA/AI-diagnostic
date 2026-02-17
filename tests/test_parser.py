"""
File: tests/test_parser.py
Description: Unit tests for PLCParser ensuring correct stage and line detection
against real industrial build logs.
"""

# Standard Library Imports
import pytest

# Internal Imports
from app.core.parser import PLCParser
from app.utils.loader import load_fixture


@pytest.mark.parametrize(
    "log_file, expected_stage, expected_line",
    [
        ("constant_error.txt", "iec_compilation", 30),
        ("empty_project.txt", "code_generation", 43),
    ],
)
def test_parser_metadata_extraction(
    log_file: str, expected_stage: str, expected_line: int
):
    """
    Validates that the parser correctly identifies the build stage and
    extracts the precise line number from raw logs [cite: 11-12, 17].
    """
    # Arrange
    parser = PLCParser()
    log_content = load_fixture(log_file)

    # Act
    metadata = parser.get_metadata(log_content)

    # Assert
    assert metadata["stage"] == expected_stage, f"Failed for {log_file}: Stage mismatch"
    assert metadata["line"] == expected_line, f"Failed for {log_file}: Line mismatch"
    assert (
        metadata["severity"] == "blocking"
    ), "All critical build errors should be blocking"[cite:16]
