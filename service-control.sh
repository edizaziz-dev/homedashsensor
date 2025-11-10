#!/bin/bash
# HomeDashSensor Service Control Script
# Usage: ./service-control.sh {start|stop|restart|status|install|uninstall|logs}

SERVICE_NAME="homedashsensor"
SERVICE_FILE="/home/pi/apps/homedashsensor/homedashsensor.service"
INSTALL_PATH="/etc/systemd/system/homedashsensor.service"

case "$1" in
    install)
        echo "🔧 Installing HomeDashSensor service..."
        
        # Copy service file to systemd directory
        sudo cp "$SERVICE_FILE" "$INSTALL_PATH"
        
        # Reload systemd and enable service
        sudo systemctl daemon-reload
        sudo systemctl enable homedashsensor
        
        echo "✅ Service installed and enabled for startup"
        echo "   Use './service-control.sh start' to start the service"
        ;;
        
    uninstall)
        echo "🗑️ Uninstalling HomeDashSensor service..."
        
        # Stop and disable service
        sudo systemctl stop homedashsensor 2>/dev/null || true
        sudo systemctl disable homedashsensor 2>/dev/null || true
        
        # Remove service file
        sudo rm -f "$INSTALL_PATH"
        sudo systemctl daemon-reload
        
        echo "✅ Service uninstalled"
        ;;
        
    start)
        echo "🚀 Starting HomeDashSensor service..."
        sudo systemctl start homedashsensor
        
        if sudo systemctl is-active --quiet homedashsensor; then
            echo "✅ Service started successfully"
        else
            echo "❌ Failed to start service"
            echo "   Check logs with './service-control.sh logs'"
        fi
        ;;
        
    stop)
        echo "🛑 Stopping HomeDashSensor service..."
        sudo systemctl stop homedashsensor
        echo "✅ Service stopped"
        ;;
        
    restart)
        echo "🔄 Restarting HomeDashSensor service..."
        sudo systemctl restart homedashsensor
        
        if sudo systemctl is-active --quiet homedashsensor; then
            echo "✅ Service restarted successfully"
        else
            echo "❌ Failed to restart service"
            echo "   Check logs with './service-control.sh logs'"
        fi
        ;;
        
    status)
        echo "📊 HomeDashSensor service status:"
        sudo systemctl status homedashsensor --no-pager -l
        ;;
        
    logs)
        echo "📋 HomeDashSensor service logs (last 50 lines):"
        echo "   Press Ctrl+C to exit, or use 'journalctl -f -u homedashsensor' for live logs"
        sudo journalctl -u homedashsensor -n 50 --no-pager
        ;;
        
    logs-live)
        echo "📋 Live HomeDashSensor service logs:"
        echo "   Press Ctrl+C to exit"
        sudo journalctl -f -u homedashsensor
        ;;
        
    *)
        echo "HomeDashSensor Service Control"
        echo "Usage: $0 {install|uninstall|start|stop|restart|status|logs|logs-live}"
        echo ""
        echo "Commands:"
        echo "  install     Install service for automatic startup"
        echo "  uninstall   Remove service from system"
        echo "  start       Start the service"
        echo "  stop        Stop the service"
        echo "  restart     Restart the service"
        echo "  status      Show service status"
        echo "  logs        Show recent logs"
        echo "  logs-live   Show live logs (follow mode)"
        exit 1
        ;;
esac

exit 0