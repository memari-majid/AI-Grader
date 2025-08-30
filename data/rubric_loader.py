"""
Generic rubric loader and helpers for AI-Grader

Schema (JSON) expected for custom rubrics:

{
  "name": "Intro to Programming - Assignment 1",
  "version": "1.0",
  "scale": {
    "min": 0,
    "max": 3,
    "labels": {"0": "Does not meet", "1": "Approaching", "2": "Meets", "3": "Exceeds"}
  },
  "criteria": [
    {
      "id": "CORR",
      "code": "CORR",
      "title": "Correctness",
      "category": "Program Quality",
      "description": "Program produces correct outputs across specified cases.",
      "levels": {"0": "Fails most tests", "1": "Passes some tests", "2": "Passes most tests", "3": "Passes all tests incl. edge cases"}
    },
    ...
  ]
}
"""

from typing import Dict, Any, List
import json


def parse_rubric_json(json_text: str) -> Dict[str, Any]:
    """Parse rubric JSON text into a dictionary with basic validation."""
    rubric = json.loads(json_text)

    # Minimal validation and defaults
    rubric.setdefault("name", "Custom Rubric")
    rubric.setdefault("version", "1.0")
    scale = rubric.get("scale") or {"min": 0, "max": 3, "labels": {"0": "Does not meet", "1": "Approaching", "2": "Meets", "3": "Exceeds"}}
    rubric["scale"] = scale

    criteria: List[Dict[str, Any]] = rubric.get("criteria", [])
    if not isinstance(criteria, list) or not criteria:
        raise ValueError("Rubric must include a non-empty 'criteria' list")

    # Normalize each criterion
    normalized: List[Dict[str, Any]] = []
    for idx, c in enumerate(criteria):
        crit = dict(c)
        crit.setdefault("id", crit.get("code") or f"C{idx+1}")
        crit.setdefault("code", crit["id"])
        crit.setdefault("title", crit.get("name", f"Criterion {idx+1}"))
        crit.setdefault("category", crit.get("competency_area", ""))
        levels = crit.get("levels")
        if not isinstance(levels, dict):
            # If levels are missing, synthesize generic 0-3 labels
            levels = {"0": "Does not meet", "1": "Approaching", "2": "Meets", "3": "Exceeds"}
        # Ensure keys are strings
        crit["levels"] = {str(k): v for k, v in levels.items()}
        normalized.append(crit)

    rubric["criteria"] = normalized
    return rubric


def rubric_to_items(rubric: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Convert rubric dict to app 'items' structure used in evaluation UI."""
    items: List[Dict[str, Any]] = []
    for crit in rubric.get("criteria", []):
        items.append({
            "id": crit["id"],
            "code": crit.get("code", crit["id"]),
            "title": crit.get("title", crit["id"]),
            "context": crit.get("context", "Submission"),
            "competency_area": crit.get("category", ""),
            "type": crit.get("type", "Criterion"),
            "levels": crit["levels"],
        })
    return items


def get_sample_cs_rubric() -> Dict[str, Any]:
    """Built-in sample rubric for CS programming assignments (0-3 scale)."""
    return {
        "name": "CS Programming Assignment - General Rubric",
        "version": "1.0",
        "scale": {
            "min": 0,
            "max": 3,
            "labels": {"0": "Does not meet", "1": "Approaching", "2": "Meets", "3": "Exceeds"}
        },
        "criteria": [
            {
                "id": "CORR",
                "code": "CORR",
                "title": "Correctness",
                "category": "Program Quality",
                "description": "Program produces correct outputs across representative and edge cases.",
                "levels": {
                    "0": "Fails most tests; frequent runtime errors.",
                    "1": "Passes some tests; noticeable logic bugs.",
                    "2": "Passes most tests; minor issues on edge cases.",
                    "3": "Passes all specified tests including edge cases."
                }
            },
            {
                "id": "STYLE",
                "code": "STYLE",
                "title": "Code Style and Readability",
                "category": "Code Quality",
                "description": "Consistent style, meaningful names, modularity, and comments/docstrings as appropriate.",
                "levels": {
                    "0": "Inconsistent style; very hard to read.",
                    "1": "Some conventions followed; readability issues remain.",
                    "2": "Generally consistent style and readable structure.",
                    "3": "Exemplary style; highly readable and idiomatic."
                }
            },
            {
                "id": "EFF",
                "code": "EFF",
                "title": "Efficiency and Complexity",
                "category": "Performance",
                "description": "Appropriate algorithms/data structures; avoids unnecessary overhead.",
                "levels": {
                    "0": "Inefficient approach; severe performance issues.",
                    "1": "Suboptimal approach; noticeable inefficiencies.",
                    "2": "Reasonable efficiency for problem constraints.",
                    "3": "Efficient, well-chosen algorithms and structures."
                }
            },
            {
                "id": "DOC",
                "code": "DOC",
                "title": "Documentation and Testing",
                "category": "Process",
                "description": "Clear docstrings/comments and evidence of tests (cases, edge cases).",
                "levels": {
                    "0": "No meaningful documentation or tests.",
                    "1": "Minimal docs; ad-hoc tests only.",
                    "2": "Adequate docs and basic tests.",
                    "3": "Comprehensive docs and thorough tests incl. edge cases."
                }
            }
        ]
    }


