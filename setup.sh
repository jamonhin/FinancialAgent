#!/bin/bash

# Financial Agent Server Management Script
# Usage: ./setup.sh [start|stop|restart|status|debug|install]

set -e

PROJECT_DIR="/Users/jamesmontoya/Documents/github/FinancialAgent"
SERVER_SCRIPT="app.py"
PYTHON_CMD="python"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_debug() {
    echo -e "${BLUE}[DEBUG]${NC} $1"
}

# Check if server is running
check_server() {
    if pgrep -f "$SERVER_SCRIPT" > /dev/null; then
        return 0
    else
        return 1
    fi
}

# Install dependencies (original setup functionality)
install_deps() {
    print_status "🏗️  Setting up Financial Agent with Real CrewAI Integration..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_status "📦 Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    print_status "🔄 Activating virtual environment..."
    source venv/bin/activate
    
    # Install dependencies
    print_status "⬇️  Installing dependencies..."
    pip install -r requirements.txt
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        print_status "⚙️  Creating .env file from template..."
        if [ -f ".env.example" ]; then
            cp .env.example .env
        fi
        print_status "✏️  Please edit .env file and add your API keys:"
        print_status "    - OpenAI API Key: https://platform.openai.com/api-keys"
        print_status "    - Serper API Key: https://serper.dev/"
    fi
    
    print_status "✅ Setup complete!"
    print_status ""
    print_status "Next steps:"
    print_status "1. Edit .env file with your API keys"
    print_status "2. Run: ./setup.sh start"
    print_status "3. Open: http://localhost:8050"
    print_status ""
    print_status "Note: Without valid API keys, the agents will show an error message but the UI will still work."
}

# Start the server
start_server() {
    print_status "Starting Financial Agent Server..."
    
    if check_server; then
        print_warning "Server is already running"
        return 0
    fi
    
    # Check if port 8050 is available
    if lsof -i :8050 > /dev/null 2>&1; then
        print_error "Port 8050 is already in use"
        print_status "Trying to free port 8050..."
        lsof -ti :8050 | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
    
    # Start server in background
    cd "$PROJECT_DIR"
    nohup $PYTHON_CMD $SERVER_SCRIPT > server.log 2>&1 &
    
    # Wait a moment and check if it started successfully
    sleep 3
    
    if check_server; then
        print_status "✅ Server started successfully"
        print_status "🌐 Access at: http://localhost:8050"
        print_status "📋 Logs: $PROJECT_DIR/server.log"
    else
        print_error "❌ Failed to start server"
        print_error "Check server.log for details"
        return 1
    fi
}

# Stop the server
stop_server() {
    print_status "Stopping Financial Agent Server..."
    
    if ! check_server; then
        print_warning "Server is not running"
        return 0
    fi
    
    # Try graceful shutdown first
    print_status "Attempting graceful shutdown..."
    pkill -TERM -f "$SERVER_SCRIPT" || true
    
    # Wait for graceful shutdown
    sleep 5
    
    # Force kill if still running
    if check_server; then
        print_warning "Graceful shutdown failed, forcing termination..."
        pkill -KILL -f "$SERVER_SCRIPT" || true
        sleep 2
    fi
    
    # Clean up port if needed
    if lsof -i :8050 > /dev/null 2>&1; then
        print_status "Cleaning up port 8050..."
        lsof -ti :8050 | xargs kill -9 2>/dev/null || true
    fi
    
    # Final verification
    if check_server; then
        print_error "❌ Failed to stop server completely"
        print_status "🚨 Run: python emergency_stop.py"
        return 1
    else
        print_status "✅ Server stopped successfully"
    fi
}

# Restart the server
restart_server() {
    print_status "Restarting Financial Agent Server..."
    stop_server
    sleep 2
    start_server
}

# Check server status
server_status() {
    print_status "Checking Financial Agent Server status..."
    
    if check_server; then
        PID=$(pgrep -f "$SERVER_SCRIPT")
        print_status "✅ Server is running (PID: $PID)"
        
        # Check if port is responding
        if curl -s http://localhost:8050 > /dev/null 2>&1; then
            print_status "🌐 Server is responding on port 8050"
        else
            print_warning "⚠️  Server is running but not responding on port 8050"
        fi
        
        # Show resource usage
        ps -p "$PID" -o pid,ppid,cpu,pmem,etime,cmd 2>/dev/null || true
        
    else
        print_warning "❌ Server is not running"
    fi
    
    # Check port usage
    if lsof -i :8050 > /dev/null 2>&1; then
        print_status "📊 Port 8050 usage:"
        lsof -i :8050 || true
    else
        print_status "✅ Port 8050 is free"
    fi
}

# Debug mode
debug_server() {
    print_status "Starting server in debug mode..."
    
    if check_server; then
        print_warning "Stopping existing server first..."
        stop_server
        sleep 2
    fi
    
    cd "$PROJECT_DIR"
    export DEBUG_THREADING=true
    export SIMULATE_ANALYSIS_RESULTS=true
    
    print_debug "Environment variables set:"
    print_debug "DEBUG_THREADING=true"
    print_debug "SIMULATE_ANALYSIS_RESULTS=true"
    
    print_status "Starting server in foreground with debug output..."
    print_status "Press Ctrl+C to stop"
    
    $PYTHON_CMD $SERVER_SCRIPT
}

# Show help
show_help() {
    echo "Financial Agent Server Management"
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  install   Install dependencies and setup"
    echo "  start     Start the server"
    echo "  stop      Stop the server"
    echo "  restart   Restart the server"
    echo "  status    Check server status"
    echo "  debug     Start in debug mode"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 install  # Install dependencies first"
    echo "  $0 start    # Start server in background"
    echo "  $0 debug    # Start with debug output"
    echo "  $0 status   # Check if server is running"
    echo ""
    echo "Emergency stop: python emergency_stop.py"
}

# Main script logic
case "${1:-help}" in
    install)
        install_deps
        ;;
    start)
        start_server
        ;;
    stop)
        stop_server
        ;;
    restart)
        restart_server
        ;;
    status)
        server_status
        ;;
    debug)
        debug_server
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
