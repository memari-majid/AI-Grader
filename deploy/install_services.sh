#!/bin/bash
# Install CS AI Grader as systemd services for permanent background operation

echo "🚀 Installing CS AI Grader as system services..."

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run with sudo: sudo ./deploy/install_services.sh"
    exit 1
fi

# Copy service files
echo "📋 Installing service files..."
cp deploy/cs-ai-grader.service /etc/systemd/system/
cp deploy/ngrok.service /etc/systemd/system/

# Set permissions
chmod 644 /etc/systemd/system/cs-ai-grader.service
chmod 644 /etc/systemd/system/ngrok.service

# Reload systemd
echo "🔄 Reloading systemd..."
systemctl daemon-reload

# Enable services
echo "✅ Enabling services..."
systemctl enable cs-ai-grader.service
systemctl enable ngrok.service

# Start services
echo "🚀 Starting services..."
systemctl start cs-ai-grader.service
sleep 5
systemctl start ngrok.service

# Check status
echo "📊 Service status:"
systemctl status cs-ai-grader.service --no-pager -l
echo ""
systemctl status ngrok.service --no-pager -l

echo ""
echo "✅ CS AI Grader installed as system services!"
echo "🌐 App will be available at: https://csaigrader.ngrok.app"
echo ""
echo "📋 Management commands:"
echo "  sudo systemctl status cs-ai-grader    # Check app status"
echo "  sudo systemctl status ngrok           # Check tunnel status"
echo "  sudo systemctl restart cs-ai-grader   # Restart app"
echo "  sudo systemctl stop cs-ai-grader      # Stop app"
echo "  sudo journalctl -u cs-ai-grader -f    # View app logs"
echo ""
echo "🔄 Services will automatically restart on boot and if they crash."
