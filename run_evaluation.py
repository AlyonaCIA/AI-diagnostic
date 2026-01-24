#!/usr/bin/env python3
"""
File: run_evaluation.py
Description: End-to-end evaluation script that generates test cases and evaluates the system.
Run with: python run_evaluation.py
"""

import time
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

from app.core.parser import PLCParser
from app.utils.xml_manager import XMLContextExtractor
from app.agents.diagnostician import PLCDiagnosticAgent
from app.utils.error_generator import ErrorGenerator
from app.utils.evaluator import Evaluator

# Load environment variables from .env file
load_dotenv()


def run_evaluation(num_constant_errors: int = 10, num_code_gen_errors: int = 10):
    """
    Run full evaluation on generated test cases.
    
    Args:
        num_constant_errors: Number of constant error test cases
        num_code_gen_errors: Number of code generation error test cases
    """
    print("\n" + "=" * 80)
    print("PLC DIAGNOSTIC SYSTEM - EVALUATION RUNNER")
    print("=" * 80)
    
    # Initialize components
    parser = PLCParser()
    agent = PLCDiagnosticAgent()
    
    # Generate test cases
    print(f"\n[1/3] Generating {num_constant_errors + num_code_gen_errors} test cases...")
    all_errors = ErrorGenerator.generate_all_test_cases(
        constant_error_count=num_constant_errors,
        code_gen_count=num_code_gen_errors
    )
    print(f"✓ Generated {len(all_errors)} test cases")
    
    # Run through pipeline
    print(f"\n[2/3] Running diagnostics on {len(all_errors)} test cases...")
    test_results = []
    
    for i, error in enumerate(all_errors, 1):
        try:
            start_time = time.time()
            
            # Parse error log
            metadata = parser.get_metadata(error.log_text)
            
            # Extract context
            try:
                xml_extractor = XMLContextExtractor(error.xml_content)
                context = xml_extractor.get_pou_context("program0")
            except Exception:
                context = "Context missing: Malformed project XML."
            
            # Get diagnostic report
            diagnostic_report = agent.get_fix_suggestions(metadata, context)
            
            response_time = time.time() - start_time
            
            test_results.append({
                "error_type": error.error_type,
                "expected_stage": error.expected_stage,
                "expected_severity": error.expected_severity,
                "expected_complexity": error.expected_complexity,
                "predicted": {
                    "stage": diagnostic_report.stage,
                    "severity": diagnostic_report.severity,
                    "complexity": diagnostic_report.complexity,
                    "root_cause": diagnostic_report.root_cause,
                    "suggestions": [
                        {
                            "confidence": s.confidence,
                            "explanation": s.explanation[:100] + "..." if len(s.explanation) > 100 else s.explanation
                        }
                        for s in diagnostic_report.suggestions
                    ]
                },
                "response_time": response_time
            })
            
            status = "✓" if (
                diagnostic_report.stage == error.expected_stage and
                diagnostic_report.severity == error.expected_severity and
                diagnostic_report.complexity == error.expected_complexity
            ) else "⚠"
            
            print(f"  [{i}/{len(all_errors)}] {status} {error.error_type} - {response_time:.2f}s")
            
        except Exception as e:
            print(f"  [{i}/{len(all_errors)}] ✗ {error.error_type} - Error: {str(e)[:50]}")
            # Still record for metrics
            test_results.append({
                "error_type": error.error_type,
                "expected_stage": error.expected_stage,
                "expected_severity": error.expected_severity,
                "expected_complexity": error.expected_complexity,
                "predicted": {
                    "stage": "unknown",
                    "severity": "info",
                    "complexity": "trivial",
                    "suggestions": []
                },
                "response_time": 0.0
            })
    
    # Generate report
    print(f"\n[3/3] Generating evaluation report...")
    evaluation_report = Evaluator.generate_report(test_results)
    
    # Print report
    Evaluator.print_report(evaluation_report)
    
    # Save report
    report_path = Path("evaluation_report.json")
    Evaluator.save_report_json(evaluation_report, str(report_path))
    
    print(f"\n✓ Evaluation complete!")
    return evaluation_report


if __name__ == "__main__":
    # Run with default 20 test cases
    num_constant = 10
    num_code_gen = 10
    
    # Allow command line arguments
    if len(sys.argv) > 1:
        try:
            num_constant = int(sys.argv[1])
            num_code_gen = int(sys.argv[2]) if len(sys.argv) > 2 else num_constant
        except ValueError:
            print("Usage: python run_evaluation.py [num_constant_errors] [num_code_gen_errors]")
            print("Default: 10 constant errors, 10 code generation errors")
    
    report = run_evaluation(num_constant, num_code_gen)
