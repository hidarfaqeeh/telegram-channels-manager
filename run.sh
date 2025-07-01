#!/bin/bash

# Telegram Channels Manager Bot - Run Script
# بوت إدارة القنوات - ملف التشغيل

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python() {
    if command_exists python3; then
        PYTHON_CMD="python3"
    elif command_exists python; then
        PYTHON_CMD="python"
    else
        print_error "Python is not installed. Please install Python 3.8 or later."
        exit 1
    fi
    
    # Check Python version
    PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    REQUIRED_VERSION="3.8"
    
    if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
        print_error "Python $REQUIRED_VERSION or later is required. Found: $PYTHON_VERSION"
        exit 1
    fi
    
    print_success "Python $PYTHON_VERSION found"
}

# Function to setup virtual environment
setup_venv() {
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        $PYTHON_CMD -m venv venv
        print_success "Virtual environment created"
    else
        print_status "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        print_success "Virtual environment activated"
    elif [ -f "venv/Scripts/activate" ]; then
        source venv/Scripts/activate
        print_success "Virtual environment activated (Windows)"
    else
        print_error "Could not find virtual environment activation script"
        exit 1
    fi
}

# Function to install dependencies
install_deps() {
    print_status "Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    print_success "Dependencies installed"
}

# Function to check configuration
check_config() {
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            print_warning ".env file not found. Copying from .env.example"
            cp .env.example .env
            print_warning "Please edit .env file with your actual configuration"
            print_warning "Required fields: API_ID, API_HASH, BOT_TOKEN, PHONE_NUMBER, CONTROL_BOT_TOKEN, ADMIN_IDS"
            exit 1
        else
            print_error ".env file not found and no .env.example available"
            exit 1
        fi
    fi
    
    print_success "Configuration file found"
}

# Function to create necessary directories
create_dirs() {
    dirs=("logs" "data" "sessions")
    
    for dir in "${dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_status "Created directory: $dir"
        fi
    done
}

# Function to show help
show_help() {
    echo "Telegram Channels Manager Bot - Run Script"
    echo "=========================================="
    echo ""
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  start, run       Start the bot (both UserBot and Control Bot)"
    echo "  userbot          Start only the UserBot"
    echo "  control          Start only the Control Bot"
    echo "  setup            Setup environment and install dependencies"
    echo "  check            Check configuration and dependencies"
    echo "  update           Update dependencies"
    echo "  clean            Clean up temporary files"
    echo "  logs             Show recent logs"
    echo "  help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 setup         # First time setup"
    echo "  $0 start         # Start the bot"
    echo "  $0 logs          # View logs"
}

# Function to setup everything
setup_bot() {
    print_status "Setting up Telegram Channels Manager Bot..."
    
    check_python
    setup_venv
    install_deps
    check_config
    create_dirs
    
    print_success "Setup completed successfully!"
    print_warning "Please edit .env file with your configuration before starting the bot"
}

# Function to check everything
check_bot() {
    print_status "Checking bot configuration..."
    
    check_python
    
    if [ ! -d "venv" ]; then
        print_error "Virtual environment not found. Run: $0 setup"
        exit 1
    fi
    
    setup_venv
    check_config
    
    # Check if required packages are installed
    python -c "import telethon, telegram, sqlalchemy" 2>/dev/null || {
        print_error "Required packages not installed. Run: $0 setup"
        exit 1
    }
    
    print_success "All checks passed!"
}

# Function to update dependencies
update_bot() {
    print_status "Updating dependencies..."
    setup_venv
    pip install --upgrade pip
    pip install -r requirements.txt --upgrade
    print_success "Dependencies updated!"
}

# Function to clean up
clean_bot() {
    print_status "Cleaning up temporary files..."
    
    # Remove Python cache
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    
    # Remove logs older than 7 days
    find logs -name "*.log" -mtime +7 -delete 2>/dev/null || true
    
    print_success "Cleanup completed!"
}

# Function to show logs
show_logs() {
    if [ -f "bot.log" ]; then
        print_status "Showing recent logs (last 50 lines):"
        echo "=================================="
        tail -n 50 bot.log
    else
        print_warning "No log file found"
    fi
}

# Function to start the bot
start_bot() {
    print_status "Starting Telegram Channels Manager Bot..."
    
    # Check everything first
    check_bot
    
    # Start the bot
    python main.py
}

# Function to start only userbot
start_userbot() {
    print_status "Starting UserBot only..."
    check_bot
    python userbot.py
}

# Function to start only control bot
start_control() {
    print_status "Starting Control Bot only..."
    check_bot
    python control_bot.py
}

# Main script logic
case "${1:-start}" in
    "start"|"run")
        start_bot
        ;;
    "userbot")
        start_userbot
        ;;
    "control")
        start_control
        ;;
    "setup")
        setup_bot
        ;;
    "check")
        check_bot
        ;;
    "update")
        update_bot
        ;;
    "clean")
        clean_bot
        ;;
    "logs")
        show_logs
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        print_error "Unknown option: $1"
        echo ""
        show_help
        exit 1
        ;;
esac