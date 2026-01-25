#!/bin/bash
# Setup script to install CSX Trading Journal as a systemd service

set -e

SERVICE_NAME="csx-trading-journal"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
PROJECT_DIR="/workspaces/csx-trading-journal"
LOCAL_SERVICE="${PROJECT_DIR}/${SERVICE_NAME}.service"

echo "📦 CSX Trading Journal - Systemd Setup"
echo "======================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
   echo "❌ Error: This script must be run as root (use sudo)"
   exit 1
fi

echo "✓ Running as root"
echo ""

# Copy service file
echo "📋 Installing service file..."
cp "$LOCAL_SERVICE" "$SERVICE_FILE"
echo "✓ Service file copied to $SERVICE_FILE"
echo ""

# Reload systemd daemon
echo "🔄 Reloading systemd daemon..."
systemctl daemon-reload
echo "✓ Systemd daemon reloaded"
echo ""

# Enable service to start on boot
echo "⚙️  Enabling service to start on boot..."
systemctl enable "$SERVICE_NAME"
echo "✓ Service enabled"
echo ""

# Start the service
echo "🚀 Starting service..."
systemctl start "$SERVICE_NAME"
echo "✓ Service started"
echo ""

# Check status
echo "📊 Service status:"
systemctl status "$SERVICE_NAME"
echo ""

echo "======================================"
echo "✅ Setup complete!"
echo ""
echo "📌 Useful commands:"
echo "   sudo systemctl status csx-trading-journal    - Check status"
echo "   sudo systemctl start csx-trading-journal     - Start service"
echo "   sudo systemctl stop csx-trading-journal      - Stop service"
echo "   sudo systemctl restart csx-trading-journal   - Restart service"
echo "   sudo systemctl log-journal-unit csx-trading-journal - View logs"
echo "   journalctl -u csx-trading-journal -f         - Follow logs in real-time"
echo ""
