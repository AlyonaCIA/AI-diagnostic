"""
File: app/core/parser.py
Description: High-precision PLC log parser. Uses stage-specific regex patterns
to resolve line number conflicts in cascading error logs.
"""

# Standard Library Imports
import re
from typing import Any, Dict, Optional

# Third-Party Imports
from loguru import logger


class PLCParser:
    """
    Deterministic parser for PLC build pipelines.
    Implements granular extraction rules for each build stage. [cite: 11-12]
    """

    def __init__(self) -> None:
        """
        Initializes prioritized stage rules and targeted line extraction patterns.
        """
        # Priority: Code Gen (Crashes) > IEC (Compiler) > XML (Warnings) [cite: 13, 17]
        self._stage_rules = [
            (
                "code_generation",
                re.compile(r"Traceback|AttributeError|Beremiz_cli", re.I),
            ),
            ("iec_compilation", re.compile(r"iec2c|matiec|error:", re.I)),
            ("xml_validation", re.compile(r"XSD schema", re.I)),
        ]

        # Specific patterns for each tool's error format
        self._line_patterns = {
            "xml_validation": re.compile(r"at line\s+(?P<line>\d+):"),
            "iec_compilation": re.compile(r"\.st:(?P<line>\d+)"),
            # In Python crashes, we want the first line that triggered the build failure
            "code_generation": re.compile(r"at line\s+(?P<line>\d+):"),
        }

    def get_metadata(self, log_text: str) -> Dict[str, Any]:
        """
        Orchestrates stage detection and specific line extraction. [cite: 8, 11-12]
        """
        # 1. Detect Stage
        detected_stage = "unknown"
        for stage_name, pattern in self._stage_rules:
            if pattern.search(log_text):
                detected_stage = stage_name
                break

        # 2. Extract Line using the specific rule for that stage
        line = None
        if detected_stage in self._line_patterns:
            pattern = self._line_patterns[detected_stage]
            match = pattern.search(log_text)
            if match:
                line = int(match.group("line"))

        metadata = {
            "stage": detected_stage,
            "line": line,
            "severity": "blocking" if detected_stage != "unknown" else "info",
        }

        logger.debug(f"Metadata extracted: {metadata}")
        return metadata
