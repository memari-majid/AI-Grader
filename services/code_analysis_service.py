"""
Code analysis service for CS programming assignments.
Computes basic static metrics and style issues for Python code.
"""

from typing import Dict, Any, List, Tuple
import ast
import io
import tempfile
import contextlib


def _count_docstrings(node: ast.AST) -> Tuple[int, int]:
    """Return (num_defs, num_with_docstring) for functions and classes."""
    total = 0
    with_doc = 0
    for n in ast.walk(node):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            total += 1
            if ast.get_docstring(n):
                with_doc += 1
    return total, with_doc


def analyze_python_code(code_text: str) -> Dict[str, Any]:
    """Analyze Python code and return static metrics and linting summary.

    Returns keys:
      - lines, non_empty_lines
      - functions, classes
      - docstring_coverage (0.0-1.0)
      - maintainability_index, avg_cyclomatic_complexity, max_cyclomatic_complexity
      - flake8_issues_count, flake8_top_issues (list[str])
    """
    metrics: Dict[str, Any] = {}

    # Basic line metrics
    lines = code_text.splitlines()
    metrics["lines"] = len(lines)
    metrics["non_empty_lines"] = sum(1 for l in lines if l.strip())

    # AST-based metrics
    try:
        tree = ast.parse(code_text)
        functions = sum(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) for n in ast.walk(tree))
        classes = sum(isinstance(n, ast.ClassDef) for n in ast.walk(tree))
        metrics["functions"] = int(functions)
        metrics["classes"] = int(classes)
        total_defs, with_doc = _count_docstrings(tree)
        metrics["docstring_coverage"] = (with_doc / total_defs) if total_defs else 0.0
    except SyntaxError:
        metrics["functions"] = 0
        metrics["classes"] = 0
        metrics["docstring_coverage"] = 0.0

    # Radon metrics (optional; if unavailable, leave None)
    mi_val = None
    avg_cc = None
    max_cc = None
    try:
        from radon.metrics import mi_visit
        from radon.complexity import cc_visit

        mi_val = float(mi_visit(code_text, multi=True))
        blocks = cc_visit(code_text)
        if blocks:
            complexities = [b.complexity for b in blocks]
            avg_cc = sum(complexities) / len(complexities)
            max_cc = max(complexities)
        else:
            avg_cc = 0.0
            max_cc = 0.0
    except Exception:
        pass

    metrics["maintainability_index"] = mi_val
    metrics["avg_cyclomatic_complexity"] = avg_cc
    metrics["max_cyclomatic_complexity"] = max_cc

    # Flake8 linting summary
    flake8_issues: List[str] = []
    try:
        from flake8.api import legacy as flake8
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=True) as tmp:
            tmp.write(code_text)
            tmp.flush()
            style_guide = flake8.get_style_guide(ignore=["E501"], quiet=2)
            report = style_guide.check_files([tmp.name])
            # Re-run to capture messages by redirecting stdout (flake8 legacy API prints)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                style_guide = flake8.get_style_guide(ignore=["E501"], quiet=0)
                style_guide.check_files([tmp.name])
            output = buf.getvalue().splitlines()
            # Filter lines that look like issue lines
            for line in output:
                if ":" in line and tmp.name in line:
                    # Trim filename prefix
                    flake8_issues.append(line.split(tmp.name)[-1].lstrip(": "))
            metrics["flake8_issues_count"] = int(getattr(report, "total_errors", 0))
            metrics["flake8_top_issues"] = flake8_issues[:10]
    except Exception:
        metrics["flake8_issues_count"] = None
        metrics["flake8_top_issues"] = []

    return metrics


