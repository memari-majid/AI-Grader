#!/usr/bin/env python3
"""
Synthetic evaluation pipeline for CS AI Grader.
Generates or loads synthetic code samples, runs code analysis + AI feedback,
computes metrics, and exits nonzero if thresholds fail.
"""

import os
import json
import random
import argparse
from typing import List, Dict, Any

from dotenv import load_dotenv
load_dotenv()

from data.rubric_loader import get_sample_cs_rubric
from services.code_analysis_service import analyze_python_code
from services.openai_service import OpenAIService


SYNTHETIC_SNIPPETS = [
    """
def add(a, b):
    """Return the sum of a and b."""
    return a + b

def main():
    print(add(2, 3))
""",
    """
def factorial(n):
    if n <= 1:
        return 1
    result = 1
    for i in range(2, n+1):
        result *= i
    return result
""",
    """
class Greeter:
    def __init__(self, name):
        self.name = name
    def greet(self):
        return f"Hello, {self.name}!"
""",
]


def sample_code() -> str:
    return random.choice(SYNTHETIC_SNIPPETS)


def compute_metrics(feedbacks: Dict[str, str], scores: Dict[str, Any], code_metrics: Dict[str, Any]) -> Dict[str, Any]:
    criteria_count = max(len(feedbacks), 1)
    coverage = sum(1 for v in feedbacks.values() if v and v.strip()) / criteria_count
    numeric_scores = [v for v in scores.values() if isinstance(v, int)]
    pass_rate = sum(1 for s in numeric_scores if s >= 2) / max(len(numeric_scores), 1)
    return {
        'coverage': coverage,
        'pass_rate': pass_rate,
        'flake8_issues': code_metrics.get('flake8_issues_count'),
        'avg_cc': code_metrics.get('avg_cyclomatic_complexity'),
        'maintainability_index': code_metrics.get('maintainability_index'),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--n', type=int, default=5, help='Number of synthetic runs')
    parser.add_argument('--rubric', type=str, default='', help='Path to rubric JSON (optional)')
    parser.add_argument('--min_coverage', type=float, default=0.9, help='Min fraction of criteria with feedback')
    parser.add_argument('--min_pass_rate', type=float, default=0.6, help='Min pass rate (scores >=2)')
    args = parser.parse_args()

    # Load rubric
    if args.rubric and os.path.exists(args.rubric):
        rubric = json.load(open(args.rubric, 'r'))
    else:
        rubric = get_sample_cs_rubric()

    openai_service = OpenAIService()
    if not openai_service.is_enabled():
        print('❌ OpenAI service not configured.')
        exit(1)

    all_metrics: List[Dict[str, Any]] = []
    for i in range(args.n):
        code = sample_code()
        code_metrics = analyze_python_code(code)
        result = openai_service.generate_code_feedback(
            rubric=rubric,
            code_text=code,
            metrics=code_metrics,
            assignment_name='Synthetic Test'
        )
        feedbacks = result.get('feedback', {})
        scores = result.get('scores', {})
        m = compute_metrics(feedbacks, scores, code_metrics)
        all_metrics.append(m)

    # Aggregate
    avg_coverage = sum(m['coverage'] for m in all_metrics) / len(all_metrics)
    avg_pass_rate = sum(m['pass_rate'] for m in all_metrics) / len(all_metrics)
    print(json.dumps({
        'runs': args.n,
        'avg_coverage': avg_coverage,
        'avg_pass_rate': avg_pass_rate
    }, indent=2))

    # Thresholds for CI
    ok = (avg_coverage >= args.min_coverage) and (avg_pass_rate >= args.min_pass_rate)
    if not ok:
        print('❌ Thresholds not met.')
        exit(2)
    print('✅ Synthetic evaluation passed thresholds.')


if __name__ == '__main__':
    main()


