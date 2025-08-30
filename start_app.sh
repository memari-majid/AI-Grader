#!/bin/bash
# Startup script for CS AI Grader with ngrok
# Automatically starts the app and exposes it via ngrok

cd /home/majid/Downloads/AI-Grader

# Activate virtual environment
source venv/bin/activate

# Kill any existing processes
pkill -f streamlit 2>/dev/null
pkill -f ngrok 2>/dev/null

echo "🚀 Starting CS AI Grader..."

# Start Streamlit in background
streamlit run app_simple.py --server.port 8501 --server.address 0.0.0.0 &
STREAMLIT_PID=$!

# Wait for Streamlit to start
sleep 5

# Start ngrok tunnel
echo "🌐 Starting ngrok tunnel..."
ngrok http --url=csaigrader.ngrok.app 8501 &
NGROK_PID=$!

# Wait for ngrok to connect
sleep 3

echo "✅ CS AI Grader is live!"
echo "🌐 Access at: https://csaigrader.ngrok.app"
echo "🏠 Local access: http://localhost:8501"
echo ""
echo "💰 Cost-effective AI grading for UVU CS Department"
echo "📊 Centralized GPT-5-mini usage instead of individual ChatGPT subscriptions"
echo ""
echo "Press Ctrl+C to stop both services"

# Wait for user interrupt
trap 'echo "🛑 Stopping services..."; kill $STREAMLIT_PID $NGROK_PID 2>/dev/null; exit 0' INT
wait
