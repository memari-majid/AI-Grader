# Rubric Format (JSON)

Use this schema to import a custom rubric for the AI Grader.

```
{
  "name": "Course/Assignment Name",
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
    }
  ]
}
```

Notes:
- `scale` is optional; defaults to 0–3 with standard labels if omitted.
- Criterion `levels` may be partial; AI will infer but complete descriptors improve feedback quality.
- Additional fields (e.g., `weight`, `examples`) are allowed and ignored by default UI.
