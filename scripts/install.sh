#!/bin/bash

# AI Chat Agent Installation Script for macOS/Linux
# This script sets up the complete environment for the application

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

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

print_header "AI Chat Agent Installation"

# Step 1: Check Python version
print_info "Checking Python version..."
if ! command_exists python3; then
    print_error "Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info[0])')
PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info[1])')

print_info "Found Python $PYTHON_VERSION"

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 9 ]); then
    print_error "Python 3.9 or higher is required. Current version: $PYTHON_VERSION"
    exit 1
fi

print_success "Python version check passed"

# Step 2: Check and install system dependencies (if needed)
print_info "Checking system dependencies..."

# Check for required system libraries for PyQt6
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    print_info "Detected Linux system"
    if command_exists apt-get; then
        print_warning "On Debian/Ubuntu systems, you may need to install:"
        print_warning "  sudo apt-get install python3-venv libxcb-xinerama0"
    elif command_exists yum; then
        print_warning "On RedHat/CentOS systems, you may need to install:"
        print_warning "  sudo yum install python3-venv"
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    print_info "Detected macOS system"
    print_success "No additional system dependencies required for macOS"
fi

# Step 3: Create virtual environment
print_info "Creating virtual environment..."
if [ -d "venv" ]; then
    print_warning "Virtual environment already exists. Removing old environment..."
    rm -rf venv
fi

python3 -m venv venv
print_success "Virtual environment created"

# Step 4: Activate virtual environment
print_info "Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"

# Step 5: Upgrade pip
print_info "Upgrading pip to latest version..."
python -m pip install --upgrade pip
PIP_VERSION=$(pip --version | awk '{print $2}')
print_success "pip upgraded to version $PIP_VERSION"

# Step 6: Install dependencies
print_info "Installing Python dependencies..."
print_info "This may take a few minutes..."
echo ""

# Install GUI Framework
print_info "Installing PyQt6 (GUI Framework)..."
pip install "PyQt6>=6.5.0"
print_success "PyQt6 installed"

# Install LangChain Core
print_info "Installing LangChain core libraries..."
pip install "langchain>=0.1.0"
print_success "LangChain installed"

print_info "Installing LangChain OpenAI integration..."
pip install "langchain-openai>=0.0.5"
print_success "LangChain OpenAI installed"

# Install Configuration and Data libraries
print_info "Installing PyYAML (configuration management)..."
pip install "PyYAML>=6.0"
print_success "PyYAML installed"

print_info "Installing requests (HTTP library)..."
pip install "requests>=2.31.0"
print_success "requests installed"

# Install Development Tools
print_info "Installing pytest (testing framework)..."
pip install "pytest>=7.4.0"
print_success "pytest installed"

echo ""
print_success "All dependencies installed successfully"

# Step 7: Create application directory structure
print_info "Creating application directory structure..."

# Create directories if they don't exist
mkdir -p sessions
mkdir -p logs
mkdir -p docs

print_success "Directory structure created:"
print_info "  - sessions/ (for storing conversation sessions)"
print_info "  - logs/ (for application logs)"
print_info "  - docs/ (for documentation)"

# Step 8: Generate default configuration file
print_info "Generating default configuration file..."

if [ -f "config.yaml" ]; then
    print_warning "config.yaml already exists. Creating backup..."
    cp config.yaml config.yaml.backup
    print_info "Backup saved as config.yaml.backup"
fi

cat > config.yaml << 'EOF'
# AI Chat Agent Configuration File

# Active Model Configuration
active_model_id: null  # Will be set when user adds first model

# Model Configurations (OpenAPI compatible models)
models: {}

# LangChain Configuration
langchain:
  temperature: 0.7
  max_tokens: 2048
  streaming: true
  verbose: false

# Working Directory
working_directory: "."

# Session Configuration
session:
  storage_path: "./sessions"
  auto_save: true
  max_history: 100

# File Operation Configuration
file_operations:
  allowed_formats:
    - .txt
    - .md
    - .py
    - .js
    - .json
    - .yaml
    - .yml
    - .xml
    - .html
    - .css
    - .sh
    - .bat
  max_file_size: 10485760  # 10MB in bytes

# Logging Configuration
logging:
  level: "INFO"
  file: "./logs/agent.log"
  max_bytes: 10485760  # 10MB
  backup_count: 5

# UI Configuration
ui:
  theme: "light"
  window_width: 1200
  window_height: 800
EOF

print_success "Default configuration file created"

# Step 9: Set file permissions
print_info "Setting file permissions..."
chmod +x scripts/*.sh 2>/dev/null || true
chmod 644 config.yaml
print_success "File permissions set"

# Step 10: Verify installation
print_header "Verifying Installation"

print_info "Checking installed packages..."
VERIFICATION_FAILED=0

# Check critical dependencies
REQUIRED_PACKAGES=("PyQt6" "langchain" "langchain_openai" "yaml" "requests")
for package in "${REQUIRED_PACKAGES[@]}"; do
    if python -c "import $package" 2>/dev/null; then
        print_success "✓ $package installed"
    else
        print_error "✗ $package not found"
        VERIFICATION_FAILED=1
    fi
done

# Check directories
print_info "Checking directories..."
for dir in "sessions" "logs" "docs" "src"; do
    if [ -d "$dir" ]; then
        print_success "✓ $dir/ exists"
    else
        print_error "✗ $dir/ not found"
        VERIFICATION_FAILED=1
    fi
done

# Check configuration file
print_info "Checking configuration file..."
if [ -f "config.yaml" ]; then
    print_success "✓ config.yaml exists"
else
    print_error "✗ config.yaml not found"
    VERIFICATION_FAILED=1
fi

# Check main application file
if [ -f "main.py" ]; then
    print_success "✓ main.py exists"
else
    print_error "✗ main.py not found"
    VERIFICATION_FAILED=1
fi

echo ""

if [ $VERIFICATION_FAILED -eq 0 ]; then
    print_header "Installation Successful!"
    
    echo -e "${GREEN}The AI Chat Agent has been successfully installed!${NC}"
    echo ""
    echo -e "${BLUE}Next Steps:${NC}"
    echo "  1. Activate the virtual environment:"
    echo -e "     ${YELLOW}source venv/bin/activate${NC}"
    echo ""
    echo "  2. Run the application:"
    echo -e "     ${YELLOW}python main.py${NC}"
    echo ""
    echo "  3. On first launch, you'll be guided to add your first AI model configuration"
    echo "     (OpenAI, Azure OpenAI, or any OpenAPI-compatible service)"
    echo ""
    echo -e "${BLUE}Quick Start:${NC}"
    echo "  - Use the provided run script:"
    echo -e "    ${YELLOW}./scripts/run.sh${NC}"
    echo ""
    echo -e "${BLUE}Documentation:${NC}"
    echo "  - User Guide: docs/USER_GUIDE.md"
    echo "  - Developer Guide: docs/DEVELOPER_GUIDE.md"
    echo "  - API Documentation: docs/API.md"
    echo ""
    echo -e "${GREEN}Happy chatting! 🚀${NC}"
    echo ""
else
    print_header "Installation Completed with Warnings"
    print_warning "Some verification checks failed. Please review the errors above."
    print_info "You may need to manually fix these issues before running the application."
    exit 1
fi
