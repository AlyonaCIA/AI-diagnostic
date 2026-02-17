"""
File: tests/test_evaluation.py
Description: Evaluation test suite - runs generated test cases through the system
and generates performance metrics.
"""

import json
import time

import pytest

from app.agents.diagnostician import PLCDiagnosticAgent
from app.core.parser import PLCParser
from app.utils.error_generator import ErrorGenerator
from app.utils.evaluator import Evaluator
from app.utils.xml_manager import XMLContextExtractor


class TestErrorGeneratorAndEvaluation:
    """Test suite for synthetic error generation and evaluation."""

    @pytest.fixture
    def parser(self):
        """Initialize parser."""
        return PLCParser()

    @pytest.fixture
    def agent(self):
        """Initialize LLM agent (requires GEMINI_API_KEY env var)."""
        return PLCDiagnosticAgent()

    def test_constant_error_generation(self):
        """Test that constant error variations are generated correctly."""
        errors = ErrorGenerator.generate_constant_errors(count=5)

        assert len(errors) == 5
        for error in errors:
            assert error.error_type == "constant_error"
            assert error.expected_stage == "iec_compilation"
            assert error.expected_severity == "blocking"
            assert error.expected_complexity == "trivial"
            assert (
                "Assignment to CONSTANT" in error.log_text
                or "iec_compilation" in error.log_text
            )

    def test_code_generation_error_generation(self):
        """Test that code generation error variations are generated correctly."""
        errors = ErrorGenerator.generate_code_generation_errors(count=5)

        assert len(errors) == 5
        for error in errors:
            assert error.error_type == "code_generation"
            assert error.expected_stage == "code_generation"
            assert error.expected_severity == "blocking"
            assert error.expected_complexity == "trivial"
            assert "AttributeError" in error.log_text or "NoneType" in error.log_text

    def test_all_test_cases_generation(self):
        """Test generation of full test suite."""
        all_cases = ErrorGenerator.generate_all_test_cases(
            constant_error_count=10, code_gen_count=10
        )

        assert len(all_cases) == 20

        constant_count = sum(1 for c in all_cases if c.error_type == "constant_error")
        code_gen_count = sum(1 for c in all_cases if c.error_type == "code_generation")

        assert constant_count == 10
        assert code_gen_count == 10

    def test_parser_on_generated_errors(self, parser):
        """Test that parser correctly handles generated error variations."""
        constant_errors = ErrorGenerator.generate_constant_errors(count=5)
        code_gen_errors = ErrorGenerator.generate_code_generation_errors(count=5)

        for error in constant_errors:
            metadata = parser.get_metadata(error.log_text)
            assert metadata["stage"] == "iec_compilation"
            assert metadata["line"] is not None
            assert metadata["severity"] == "blocking"

        for error in code_gen_errors:
            metadata = parser.get_metadata(error.log_text)
            assert metadata["stage"] == "code_generation"
            assert metadata["severity"] == "blocking"

    def test_xml_extraction_on_generated_errors(self):
        """Test that XML extraction works on generated errors."""
        constant_errors = ErrorGenerator.generate_constant_errors(count=3)

        for error in constant_errors:
            xml_extractor = XMLContextExtractor(error.xml_content)
            context = xml_extractor.get_pou_context("program0")

            assert context is not None
            assert "program0" in context
            assert len(context) > 0

    @pytest.mark.skip(reason="Requires real Gemini API - run manually for evaluation")
    def test_full_pipeline_on_generated_errors(self, parser, agent):
        """
        Full end-to-end test of the diagnostic pipeline on generated errors.
        This test is skipped by default as it requires API calls and takes time.
        Run with: pytest -v tests/test_evaluation.py::TestErrorGeneratorAndEvaluation::test_full_pipeline_on_generated_errors -s
        """
        constant_errors = ErrorGenerator.generate_constant_errors(count=3)
        test_results = []

        for error in constant_errors:
            start = time.time()

            metadata = parser.get_metadata(error.log_text)

            try:
                xml_extractor = XMLContextExtractor(error.xml_content)
                context = xml_extractor.get_pou_context("program0")
            except Exception:
                context = "Context missing"

            report = agent.get_fix_suggestions(metadata, context)

            response_time = time.time() - start

            test_results.append(
                {
                    "error_type": error.error_type,
                    "expected_stage": error.expected_stage,
                    "expected_severity": error.expected_severity,
                    "expected_complexity": error.expected_complexity,
                    "predicted": {
                        "stage": report.stage,
                        "severity": report.severity,
                        "complexity": report.complexity,
                        "suggestions": [
                            {
                                "confidence": s.confidence,
                                "explanation": s.explanation[:50] + "...",
                            }
                            for s in report.suggestions
                        ],
                    },
                    "response_time": response_time,
                }
            )

        # Generate report
        evaluation_report = Evaluator.generate_report(test_results)
        Evaluator.print_report(evaluation_report)

        # Assertions
        assert evaluation_report.total_cases == 3
        assert evaluation_report.avg_stage_accuracy > 0
        assert evaluation_report.avg_severity_accuracy > 0


class TestEvaluationMetrics:
    """Test evaluation metrics and reporting."""

    def test_classification_metrics_calculation(self):
        """Test that metrics are calculated correctly."""
        predicted = {
            "stage": "iec_compilation",
            "severity": "blocking",
            "complexity": "trivial",
            "suggestions": [
                {"confidence": 1.0},
                {"confidence": 0.9},
            ],
        }

        metrics = Evaluator.evaluate_classification(
            predicted, "iec_compilation", "blocking", "trivial", response_time=5.2
        )

        assert metrics.correct_stage is True
        assert metrics.correct_severity is True
        assert metrics.correct_complexity is True
        assert metrics.has_suggestions is True
        assert metrics.suggestion_confidence_avg == 0.95
        assert metrics.response_time_seconds == 5.2

    def test_metrics_with_mismatches(self):
        """Test metrics when predictions are incorrect."""
        predicted = {
            "stage": "code_generation",  # Wrong
            "severity": "warning",  # Wrong
            "complexity": "moderate",  # Wrong
            "suggestions": [],
        }

        metrics = Evaluator.evaluate_classification(
            predicted, "iec_compilation", "blocking", "trivial", response_time=2.1
        )

        assert metrics.correct_stage is False
        assert metrics.correct_severity is False
        assert metrics.correct_complexity is False
        assert metrics.has_suggestions is False

    def test_report_generation(self):
        """Test that reports are generated correctly."""
        test_cases = [
            {
                "error_type": "constant_error",
                "expected_stage": "iec_compilation",
                "expected_severity": "blocking",
                "expected_complexity": "trivial",
                "predicted": {
                    "stage": "iec_compilation",
                    "severity": "blocking",
                    "complexity": "trivial",
                    "suggestions": [{"confidence": 1.0}],
                },
                "response_time": 5.0,
            },
            {
                "error_type": "code_generation",
                "expected_stage": "code_generation",
                "expected_severity": "blocking",
                "expected_complexity": "trivial",
                "predicted": {
                    "stage": "code_generation",
                    "severity": "blocking",
                    "complexity": "trivial",
                    "suggestions": [{"confidence": 0.95}],
                },
                "response_time": 6.0,
            },
        ]

        report = Evaluator.generate_report(test_cases)

        assert report.total_cases == 2
        assert report.correct_stage == 2
        assert report.correct_severity == 2
        assert report.correct_complexity == 2
        assert report.avg_stage_accuracy == 100.0
        assert report.avg_severity_accuracy == 100.0
        assert report.avg_complexity_accuracy == 100.0
        assert report.avg_response_time == 5.5

    def test_report_by_error_type(self):
        """Test that reports aggregate metrics by error type."""
        test_cases = [
            {
                "error_type": "constant_error",
                "expected_stage": "iec_compilation",
                "expected_severity": "blocking",
                "expected_complexity": "trivial",
                "predicted": {
                    "stage": "iec_compilation",
                    "severity": "blocking",
                    "complexity": "trivial",
                    "suggestions": [{"confidence": 1.0}],
                },
                "response_time": 4.0,
            },
            {
                "error_type": "code_generation",
                "expected_stage": "code_generation",
                "expected_severity": "blocking",
                "expected_complexity": "trivial",
                "predicted": {
                    "stage": "code_generation",
                    "severity": "blocking",
                    "complexity": "trivial",
                    "suggestions": [{"confidence": 0.8}],
                },
                "response_time": 6.0,
            },
        ]

        report = Evaluator.generate_report(test_cases)

        assert "constant_error" in report.results_by_error_type
        assert "code_generation" in report.results_by_error_type
        assert report.results_by_error_type["constant_error"]["count"] == 1
        assert report.results_by_error_type["code_generation"]["count"] == 1
