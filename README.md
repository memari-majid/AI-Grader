# 💻 CS AI Grader: Research Platform for AI-Assisted Grading

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com/)

A general-purpose grading research platform to study automated grading with AI using assignment context, rubrics, and human-in-the-loop feedback.

## ⭐ Initial Feature Goals

- General rubric ingestion (CSV/JSON/UI builder)
- Assignment/prompt ingestion (text, PDF)
- Evidence ingestion (student submission text; attachments roadmap)
- AI scoring suggestions per criterion
- Feedback generation aligned to rubric criteria
- Human-in-the-loop revision and acceptance
- Reliability controls and guardrails
- Research exports and analytics

## 🛠 Technology Stack

- Streamlit + Python 3.12+
- OpenAI API (default model: gpt-4o-mini, configurable via `OPENAI_MODEL`)
- Local JSON storage (SQLite planned)

## 🚀 Quick Start

### 1) Install
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2) Configure
```bash
cp env.example .env
# Add your OpenAI API key and optional model
```

### 3) Run
```bash
streamlit run app.py
```
Open http://localhost:8501 in your browser.

## 📖 Documentation

| Document | Description |
|----------|-------------|
| docs/RESEARCH_DESIGN.md | Reliability, study design, and protocols |
| docs/RUBRIC_FORMAT.md | How to define/import rubrics |
| docs/GUARDRAILS.md | Model guardrails and mitigation strategies |
| docs/ARCHITECTURE.md | System architecture and components |
| deploy/README.md | Ngrok deployment for pilots |

## 🔧 Environment Variables

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional
OPENAI_MODEL=gpt-4o-mini
```

## 📊 Research Focus

- Inter-rater reliability: AI vs TA/Professor
- Delta analysis: human revisions vs AI suggestions
- Feedback quality: rubric-aligned, specific, constructive

## 🧩 Custom Rubrics (General AI Grader)

- Use the "CS Programming (UVU)" type for Python code or the "Custom Rubric" type to upload a rubric JSON.
- JSON schema: see `docs/RUBRIC_FORMAT.md` (criteria with ids, titles, and per-level descriptors).
- The AI will generate criterion-level feedback and suggested scores based on the rubric, submission, and optional context.

## ✅ CI-style Synthetic Test Pipeline

Run a headless evaluation using synthetic code and rubric, outputting metrics:

```bash
python synthetic_eval.py --n 20 --rubric docs/examples/cs_sample_rubric.json
```

It reports:
- Coverage: percent of criteria with non-empty feedback
- Score distribution and pass-rate (≥2)
- Lint/complexity summary

Exit code is nonzero if thresholds are not met (for CI).

## License
See LICENSE. 
