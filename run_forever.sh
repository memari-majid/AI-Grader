#!/bin/bash
# Run CS AI Grader in background forever (alternative to systemd)

cd /home/majid/Downloads/AI-Grader

# Function to start services
start_services() {
    echo "🚀 Starting CS AI Grader services..."
    
    # Kill any existing processes
    pkill -f "streamlit run app_simple.py" 2>/dev/null
    pkill -f "ngrok http.*8501" 2>/dev/null
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Start Streamlit in background
    echo "📱 Starting Streamlit..."
    nohup streamlit run app_simple.py --server.port 8501 --server.address 0.0.0.0 > logs/streamlit.log 2>&1 &
    STREAMLIT_PID=$!
    
    # Wait for Streamlit to start
    sleep 8
    
    # Start ngrok tunnel
    echo "🌐 Starting ngrok tunnel..."
    nohup ngrok http --url=csaigrader.ngrok.app 8501 > logs/ngrok.log 2>&1 &
    NGROK_PID=$!
    
    # Save PIDs
    echo $STREAMLIT_PID > logs/streamlit.pid
    echo $NGROK_PID > logs/ngrok.pid
    
    echo "✅ Services started!"
    echo "🌐 CS AI Grader: https://csaigrader.ngrok.app"
    echo "🏠 Local access: http://localhost:8501"
    echo "📋 PIDs saved to logs/ directory"
}

# Function to stop services
stop_services() {
    echo "🛑 Stopping CS AI Grader services..."
    
    if [ -f logs/streamlit.pid ]; then
        STREAMLIT_PID=$(cat logs/streamlit.pid)
        kill $STREAMLIT_PID 2>/dev/null
        rm logs/streamlit.pid
    fi
    
    if [ -f logs/ngrok.pid ]; then
        NGROK_PID=$(cat logs/ngrok.pid)
        kill $NGROK_PID 2>/dev/null
        rm logs/ngrok.pid
    fi
    
    pkill -f "streamlit run app_simple.py" 2>/dev/null
    pkill -f "ngrok http.*8501" 2>/dev/null
    
    echo "✅ Services stopped"
}

# Function to check status
check_status() {
    echo "📊 CS AI Grader Status:"
    echo ""
    
    if pgrep -f "streamlit run app_simple.py" > /dev/null; then
        echo "✅ Streamlit: Running"
    else
        echo "❌ Streamlit: Not running"
    fi
    
    if pgrep -f "ngrok http.*8501" > /dev/null; then
        echo "✅ Ngrok: Running"
    else
        echo "❌ Ngrok: Not running"
    fi
    
    echo ""
    echo "🌐 Should be available at: https://csaigrader.ngrok.app"
}

# Create logs directory
mkdir -p logs

# Handle command line arguments
case "$1" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        stop_services
        sleep 2
        start_services
        ;;
    status)
        check_status
        ;;
    forever)
        echo "🔄 Running CS AI Grader forever (with auto-restart)..."
        
        # Trap signals to clean shutdown
        trap 'echo "🛑 Received shutdown signal..."; stop_services; exit 0' SIGTERM SIGINT
        
        while true; do
            start_services
            
            echo "👁️ Monitoring services... (Press Ctrl+C to stop)"
            
            # Monitor loop
            while true; do
                sleep 30
                
                # Check if services are still running
                if ! pgrep -f "streamlit run app_simple.py" > /dev/null; then
                    echo "⚠️ Streamlit died, restarting..."
                    break
                fi
                
                if ! pgrep -f "ngrok http.*8501" > /dev/null; then
                    echo "⚠️ Ngrok died, restarting..."
                    break
                fi
            done
            
            echo "🔄 Restarting services in 5 seconds..."
            sleep 5
        done
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|forever}"
        echo ""
        echo "Commands:"
        echo "  start   - Start services once"
        echo "  stop    - Stop all services"
        echo "  restart - Restart services"
        echo "  status  - Check service status"
        echo "  forever - Run with auto-restart monitoring"
        echo ""
        echo "Examples:"
        echo "  ./run_forever.sh start     # Start once"
        echo "  ./run_forever.sh forever   # Run forever with monitoring"
        echo "  ./run_forever.sh status    # Check if running"
        exit 1
        ;;
esac
