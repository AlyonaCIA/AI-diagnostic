"""
File: app/utils/evaluator.py
Description: Evaluation framework for measuring classification and suggestion quality.
Generates metrics and performance reports.
"""

from dataclasses import dataclass
from typing import List, Dict, Any
from collections import defaultdict
import json
from datetime import datetime


@dataclass
class ClassificationMetrics:
    """Metrics for a single classification."""
    correct_stage: bool
    correct_severity: bool
    correct_complexity: bool
    has_suggestions: bool
    suggestion_confidence_avg: float
    response_time_seconds: float


@dataclass
class PerformanceReport:
    """Overall performance report across all test cases."""
    total_cases: int
    correct_stage: int
    correct_severity: int
    correct_complexity: int
    avg_stage_accuracy: float
    avg_severity_accuracy: float
    avg_complexity_accuracy: float
    avg_suggestion_confidence: float
    avg_response_time: float
    results_by_error_type: Dict[str, Dict[str, Any]]
    timestamp: str


class Evaluator:
    """Evaluates classification and fix suggestion performance."""

    @staticmethod
    def evaluate_classification(
        predicted: Dict[str, Any],
        expected_stage: str,
        expected_severity: str,
        expected_complexity: str,
        response_time: float
    ) -> ClassificationMetrics:
        """
        Evaluate a single classification result.
        
        Args:
            predicted: The DiagnosticReport from the API
            expected_stage: Ground truth stage
            expected_severity: Ground truth severity
            expected_complexity: Ground truth complexity
            response_time: Time taken to generate response (seconds)
        
        Returns:
            ClassificationMetrics with correctness and quality scores
        """
        stage_match = predicted.get("stage") == expected_stage
        severity_match = predicted.get("severity") == expected_severity
        complexity_match = predicted.get("complexity") == expected_complexity
        
        has_suggestions = (
            "suggestions" in predicted and
            len(predicted["suggestions"]) > 0
        )
        
        suggestion_confidence_avg = 0.0
        if has_suggestions:
            confidences = [
                s.get("confidence", 0.0)
                for s in predicted["suggestions"]
            ]
            suggestion_confidence_avg = sum(confidences) / len(confidences)
        
        return ClassificationMetrics(
            correct_stage=stage_match,
            correct_severity=severity_match,
            correct_complexity=complexity_match,
            has_suggestions=has_suggestions,
            suggestion_confidence_avg=suggestion_confidence_avg,
            response_time_seconds=response_time
        )

    @staticmethod
    def generate_report(
        test_cases_with_results: List[Dict[str, Any]]
    ) -> PerformanceReport:
        """
        Generate a comprehensive performance report.
        
        Args:
            test_cases_with_results: List of dicts with:
                - error_type: str
                - expected_stage, severity, complexity: str
                - predicted: dict from API
                - response_time: float
        
        Returns:
            PerformanceReport with metrics
        """
        total = len(test_cases_with_results)
        
        metrics_by_error_type = defaultdict(list)
        stage_correct = 0
        severity_correct = 0
        complexity_correct = 0
        response_times = []
        confidences = []
        
        for result in test_cases_with_results:
            error_type = result["error_type"]
            metrics = Evaluator.evaluate_classification(
                result["predicted"],
                result["expected_stage"],
                result["expected_severity"],
                result["expected_complexity"],
                result["response_time"]
            )
            
            metrics_by_error_type[error_type].append(metrics)
            
            if metrics.correct_stage:
                stage_correct += 1
            if metrics.correct_severity:
                severity_correct += 1
            if metrics.correct_complexity:
                complexity_correct += 1
            
            response_times.append(metrics.response_time_seconds)
            confidences.append(metrics.suggestion_confidence_avg)
        
        # Aggregate by error type
        results_by_error_type = {}
        for error_type, metrics_list in metrics_by_error_type.items():
            stage_acc = sum(1 for m in metrics_list if m.correct_stage) / len(metrics_list) if metrics_list else 0
            sev_acc = sum(1 for m in metrics_list if m.correct_severity) / len(metrics_list) if metrics_list else 0
            complex_acc = sum(1 for m in metrics_list if m.correct_complexity) / len(metrics_list) if metrics_list else 0
            avg_time = sum(m.response_time_seconds for m in metrics_list) / len(metrics_list) if metrics_list else 0
            avg_conf = sum(m.suggestion_confidence_avg for m in metrics_list) / len(metrics_list) if metrics_list else 0
            has_sugg = sum(1 for m in metrics_list if m.has_suggestions) / len(metrics_list) if metrics_list else 0
            
            results_by_error_type[error_type] = {
                "count": len(metrics_list),
                "stage_accuracy": round(stage_acc * 100, 2),
                "severity_accuracy": round(sev_acc * 100, 2),
                "complexity_accuracy": round(complex_acc * 100, 2),
                "avg_suggestion_confidence": round(avg_conf, 3),
                "suggestions_generated_rate": round(has_sugg * 100, 2),
                "avg_response_time_seconds": round(avg_time, 2),
            }
        
        return PerformanceReport(
            total_cases=total,
            correct_stage=stage_correct,
            correct_severity=severity_correct,
            correct_complexity=complexity_correct,
            avg_stage_accuracy=round((stage_correct / total * 100) if total > 0 else 0, 2),
            avg_severity_accuracy=round((severity_correct / total * 100) if total > 0 else 0, 2),
            avg_complexity_accuracy=round((complexity_correct / total * 100) if total > 0 else 0, 2),
            avg_suggestion_confidence=round(sum(confidences) / len(confidences) if confidences else 0, 3),
            avg_response_time=round(sum(response_times) / len(response_times) if response_times else 0, 2),
            results_by_error_type=results_by_error_type,
            timestamp=datetime.now().isoformat()
        )

    @staticmethod
    def print_report(report: PerformanceReport) -> None:
        """Pretty-print the performance report."""
        print("\n" + "=" * 80)
        print("PLC DIAGNOSTIC SYSTEM - EVALUATION REPORT")
        print("=" * 80)
        print(f"\nTimestamp: {report.timestamp}")
        print(f"Total Test Cases: {report.total_cases}")
        
        print("\n" + "-" * 80)
        print("OVERALL ACCURACY METRICS")
        print("-" * 80)
        print(f"  Stage Classification Accuracy:       {report.avg_stage_accuracy}%")
        print(f"  Severity Classification Accuracy:    {report.avg_severity_accuracy}%")
        print(f"  Complexity Classification Accuracy:  {report.avg_complexity_accuracy}%")
        print(f"  Average Suggestion Confidence:       {report.avg_suggestion_confidence}")
        print(f"  Average Response Time:               {report.avg_response_time}s")
        
        print("\n" + "-" * 80)
        print("PERFORMANCE BY ERROR TYPE")
        print("-" * 80)
        
        for error_type, metrics in report.results_by_error_type.items():
            print(f"\n  {error_type.upper()} ({metrics['count']} cases)")
            print(f"    - Stage Accuracy:              {metrics['stage_accuracy']}%")
            print(f"    - Severity Accuracy:           {metrics['severity_accuracy']}%")
            print(f"    - Complexity Accuracy:         {metrics['complexity_accuracy']}%")
            print(f"    - Suggestion Confidence:       {metrics['avg_suggestion_confidence']}")
            print(f"    - Suggestions Generated:       {metrics['suggestions_generated_rate']}%")
            print(f"    - Avg Response Time:           {metrics['avg_response_time_seconds']}s")
        
        print("\n" + "=" * 80)

    @staticmethod
    def save_report_json(report: PerformanceReport, filepath: str) -> None:
        """Save report to JSON file."""
        report_dict = {
            "timestamp": report.timestamp,
            "total_cases": report.total_cases,
            "accuracy": {
                "stage": report.avg_stage_accuracy,
                "severity": report.avg_severity_accuracy,
                "complexity": report.avg_complexity_accuracy,
            },
            "quality": {
                "avg_suggestion_confidence": report.avg_suggestion_confidence,
                "avg_response_time_seconds": report.avg_response_time,
            },
            "by_error_type": report.results_by_error_type,
        }
        
        with open(filepath, "w") as f:
            json.dump(report_dict, f, indent=2)
        
        print(f"Report saved to: {filepath}")
