#!/bin/bash

# AI Chat Agent Run Script for macOS/Linux
# This script activates the virtual environment and starts the application

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

print_header "AI Chat Agent"

# Step 1: Check if virtual environment exists
print_info "Checking virtual environment..."
if [ ! -d "venv" ]; then
    print_error "Virtual environment not found!"
    print_info "Please run the installation script first:"
    echo -e "  ${YELLOW}./scripts/install.sh${NC}"
    exit 1
fi
print_success "Virtual environment found"

# Step 2: Activate virtual environment
print_info "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    print_error "Failed to activate virtual environment"
    exit 1
fi
print_success "Virtual environment activated"

# Step 3: Check if main.py exists
print_info "Checking application files..."
if [ ! -f "main.py" ]; then
    print_error "main.py not found!"
    print_info "Please ensure you are in the correct directory"
    exit 1
fi
print_success "Application files found"

# Step 4: Check configuration file
print_info "Checking configuration file..."
if [ ! -f "config.yaml" ]; then
    print_warning "config.yaml not found!"
    print_info "A default configuration will be created on first run"
else
    print_success "Configuration file found"
fi

# Step 5: Check required directories
print_info "Checking required directories..."
mkdir -p sessions
mkdir -p logs
print_success "Required directories ready"

# Step 6: Start the application
print_header "Starting Application"
echo ""
print_info "Launching AI Chat Agent..."
echo ""

# Run the application
python main.py

# Capture exit code
EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    print_success "Application closed successfully"
else
    print_warning "Application exited with code $EXIT_CODE"
fi

# Deactivate virtual environment
deactivate 2>/dev/null || true

exit $EXIT_CODE
