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
- OpenAI API (default model: gpt-5-nano for cost optimization, configurable via `OPENAI_MODEL`)
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
OPENAI_MODEL=gpt-5-nano
```

## 📊 Research Focus

- Inter-rater reliability: AI vs TA/Professor
- Delta analysis: human revisions vs AI suggestions
- Feedback quality: rubric-aligned, specific, constructive

## 🧩 Custom Rubrics (General AI Grader)

- Use the "CS Programming (UVU)" type for Python code or the "Custom Rubric" type to upload a rubric JSON.
- JSON schema: see `docs/RUBRIC_FORMAT.md` (criteria with ids, titles, and per-level descriptors).
- The AI will generate criterion-level feedback and suggested scores based on the rubric, submission, and optional context.

## 🚀 Easy Deployment

Start the app with ngrok tunnel in one command:

```bash
./start_app.sh
```

This automatically:
- Starts Streamlit on port 8501
- Creates ngrok tunnel at https://csaigrader.ngrok.app
- Uses GPT-5-nano for cost-effective department-wide usage

## 💰 Cost-Effective AI for UVU CS Department

Instead of individual ChatGPT subscriptions for each professor/TA, this centralized app provides:
- **Automated grading** with rubric-aligned feedback
- **Student email generation** with personalized feedback
- **Batch grading summaries** for class performance analysis
- **Plagiarism detection** between submissions
- **Custom rubric generation** for new assignments
- **Improvement suggestions** tailored to student code

All powered by GPT-5-nano to minimize API costs while serving the entire department.

## License
See LICENSE. 
