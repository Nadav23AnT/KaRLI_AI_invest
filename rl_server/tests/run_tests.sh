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

# Check if the server is running
if ! curl -s http://localhost:5001/portfolio > /dev/null; then
    log "Starting the server..."
    python main.py > logs/server.log 2>&1 &
    SERVER_PID=$!
    
    # Wait for server to start
    for i in {1..30}; do
        if curl -s http://localhost:5001/portfolio > /dev/null; then
            log "Server started successfully!"
            break
        fi
        sleep 1
    done
fi

# Run tests
log "Running tests..."
python -m unittest tests/test_system.py -v

# Cleanup
if [ ! -z "$SERVER_PID" ]; then
    log "Stopping the server..."
    kill $SERVER_PID
fi

# Deactivate virtual environment
deactivate

log "Tests completed!" 