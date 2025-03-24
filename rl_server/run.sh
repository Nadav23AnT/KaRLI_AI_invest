#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    error "Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    error "pip3 is not installed. Please install pip3 first."
    exit 1
fi

# Create and activate virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    log "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
log "Installing dependencies..."
pip install -r requirements.txt

# Check for Alpha Vantage API key
if [ -z "$ALPHA_VANTAGE_API_KEY" ]; then
    warn "ALPHA_VANTAGE_API_KEY not found in environment variables."
    read -p "Enter your Alpha Vantage API key: " api_key
    export ALPHA_VANTAGE_API_KEY=$api_key
fi

# Create necessary directories
mkdir -p saved_models
mkdir -p logs

# Function to check if the server is running
check_server() {
    if curl -s http://localhost:5001/portfolio > /dev/null; then
        return 0
    else
        return 1
    fi
}

# Function to start the server
start_server() {
    log "Starting the trading server..."
    python main.py > logs/server.log 2>&1 &
    SERVER_PID=$!
    
    # Wait for server to start
    for i in {1..30}; do
        if check_server; then
            log "Server started successfully!"
            return 0
        fi
        sleep 1
    done
    
    error "Server failed to start. Check logs/server.log for details."
    return 1
}

# Function to train the model
train_model() {
    log "Starting model training..."
    curl -X POST http://localhost:5001/train
    
    # Wait for training to complete (this is a simple check)
    while true; do
        if [ -f "saved_models/ppo_multistock.zip" ]; then
            log "Model training completed!"
            return 0
        fi
        sleep 5
    done
}

# Function to start trading
start_trading() {
    log "Starting trading bot..."
    curl -X POST http://localhost:5001/start_trading
    log "Trading bot started!"
}

# Function to stop trading
stop_trading() {
    log "Stopping trading bot..."
    curl -X POST http://localhost:5001/stop_trading
    log "Trading bot stopped!"
}

# Function to show portfolio status
show_portfolio() {
    curl http://localhost:5001/portfolio | python -m json.tool
}

# Cleanup function
cleanup() {
    log "Shutting down..."
    stop_trading
    kill $SERVER_PID 2>/dev/null
    deactivate
    exit 0
}

# Set up trap for cleanup
trap cleanup SIGINT SIGTERM

# Main execution
log "Starting KaRLI AI Investment System..."

# Start the server
start_server
if [ $? -ne 0 ]; then
    error "Failed to start server. Exiting..."
    exit 1
fi

# Train the model
train_model

# Start trading
start_trading

# Show initial portfolio status
log "Initial portfolio status:"
show_portfolio

# Keep the script running and show portfolio status every 5 minutes
while true; do
    sleep 300
    log "Current portfolio status:"
    show_portfolio
done 