# 💻 CS AI Grader: UVU Computer Science Department

Cost-effective AI-assisted grading platform for programming assignments, replacing individual ChatGPT subscriptions with centralized GPT-5-nano access.

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com/)

## 🎯 Features

- **AI-Assisted Grading** with rubric-aligned feedback
- **Integrated Chatbot** with GPT-5-nano access
- **Document Upload** for AI context (PDFs, code files)
- **Automated Email Generation** for student feedback
- **Plagiarism Detection** between submissions
- **Batch Grading Analytics** for class performance
- **Secure Authentication** with role-based access
- **Research Data Collection** for publication

## 🛠 Technology Stack

- Streamlit + Python 3.12+
- OpenAI API (GPT-5-nano for cost optimization)
- SQLite database for secure data storage
- Ngrok for external access

## 🚀 Quick Start

### 1) Install Dependencies
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2) Configure Environment
```bash
cp env.example .env
# Add your OpenAI API key
```

### 3) Run Forever (Recommended)
```bash
./run_forever.sh forever
```

This starts the app with auto-restart monitoring at https://csaigrader.ngrok.app

### Alternative: One-time Run
```bash
./start_app.sh
```

### System Service (Production)
```bash
sudo ./deploy/install_services.sh
```

## 💰 Cost Benefits for UVU CS Department

**Instead of:** Individual ChatGPT Plus subscriptions ($20/month × faculty/TAs)

**Get:** Centralized AI platform with:
- **Automated Grading** - Consistent rubric-aligned feedback
- **Student Communication** - AI-generated emails and suggestions
- **Plagiarism Detection** - Compare submissions automatically
- **Class Analytics** - Batch performance summaries
- **Custom Rubrics** - AI-generated for new assignments
- **Integrated Chat** - GPT-5-nano access with document upload
- **Research Data** - All interactions logged for publication

## 🔐 Security Features

- **Secure Authentication** - UVU email required, role-based access
- **Data Encryption** - Student IDs hashed, sensitive data protected
- **Audit Logging** - Complete action tracking
- **Session Management** - Secure session handling with expiration
- **Research Consent** - Explicit consent for data use

## 🧪 Testing

**Quick Test:**
1. Go to https://csaigrader.ngrok.app
2. Click "Demo Mode" or register with @uvu.edu email
3. Click "Generate Test Assignment"
4. Try all AI features

**Synthetic Pipeline:**
```bash
python synthetic_eval.py --n 10
```

## 📊 Research Protocol

See `docs/RESEARCH_PROTOCOL.md` for complete study design, hypotheses, and publication plan.

## 🔧 Management Commands

```bash
./run_forever.sh status    # Check if running
./run_forever.sh restart   # Restart services
./run_forever.sh stop      # Stop services
```

## 📖 Documentation

- [Research Protocol](docs/RESEARCH_PROTOCOL.md) - Study design and publication plan
- [Rubric Format](docs/RUBRIC_FORMAT.md) - Custom rubric JSON schema

## License

See LICENSE.