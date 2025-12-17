#!/bin/bash

################################################################################
# IoT Smart Home Agent-Based System - Universal Setup & Run Script
# This script works on Linux, macOS, and Windows (Git Bash/WSL)
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# PID tracking
BACKEND_PID=""
MOBILE_PID=""

# Cleanup function for Ctrl+C
cleanup() {
    echo ""
    log_info "Caught interrupt signal, cleaning up..."
    stop
    exit 0
}

# Set trap for Ctrl+C
trap cleanup SIGINT SIGTERM

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✅${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}❌${NC} $1"
}

print_header() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  $1"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
}

################################################################################
# PHASE 1: Setup
################################################################################

setup() {
    print_header "🚀 IoT Smart Home Setup"
    
    log_info "Checking environment..."
    
    # Check Python
    if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
        log_error "Python is not installed. Please install Python 3.11+ first."
        exit 1
    fi
    
    # Use python3 if available, otherwise python (prefer python on Windows)
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        PYTHON_CMD="python"
    else
        PYTHON_CMD="python3"
        if ! command -v python3 &> /dev/null; then
            PYTHON_CMD="python"
        fi
    fi
    
    log_success "Python found: $($PYTHON_CMD --version)"
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js is not installed. Please install Node.js 18+ first."
        exit 1
    fi
    
    log_success "Node.js found: $(node --version)"
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        log_error "npm is not installed. Please install npm first."
        exit 1
    fi
    
    log_success "npm found: $(npm --version)"
    
    # Check for .env file
    if [ ! -f ".env" ]; then
        log_warning ".env file not found. Creating from template..."
        if [ -f ".env.example" ]; then
            cp .env.example .env
            log_warning "Please edit .env and add your OpenAI API key!"
            log_warning "OPENAI_API_KEY=sk-your-key-here"
        else
            log_error ".env.example not found!"
            exit 1
        fi
    fi
    
    # Check if OpenAI key is set
    if grep -q "sk-proj-" .env 2>/dev/null || grep -q "sk-[a-zA-Z0-9]" .env 2>/dev/null; then
        log_success "OpenAI API key found in .env"
    else
        log_warning "OpenAI API key not configured in .env"
        log_warning "Voice commands will not work without a valid API key"
    fi
    
    print_header "📦 Installing Backend Dependencies"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        log_info "Creating Python virtual environment..."
        $PYTHON_CMD -m venv venv
        log_success "Virtual environment created"
    fi
    
    # Activate virtual environment
    log_info "Activating virtual environment..."
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    
    # Install Python dependencies
    log_info "Installing Python packages..."
    pip install --upgrade pip > /dev/null 2>&1
    pip install -r requirements.txt > /dev/null 2>&1
    log_success "Backend dependencies installed"
    
    print_header "📱 Installing Mobile Dependencies"
    
    cd mobile
    log_info "Installing npm packages..."
    npm install --legacy-peer-deps > /dev/null 2>&1
    log_success "Mobile dependencies installed"
    cd ..
    
    log_success "Setup complete! 🎉"
    echo ""
}

################################################################################
# PHASE 2: Run
################################################################################

run() {
    print_header "🚀 Starting IoT Smart Home System"
    
    # Kill any existing processes
    log_info "Cleaning up existing processes..."
    
    # Kill Python processes (backend)
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        taskkill //F //IM python.exe 2>/dev/null || true
        taskkill //F //IM node.exe 2>/dev/null || true
    else
        pkill -f "backend.main" 2>/dev/null || true
        pkill -f "expo start" 2>/dev/null || true
    fi
    
    sleep 2
    
    # Activate virtual environment
    log_info "Activating virtual environment..."
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        source venv/Scripts/activate
        PYTHON_CMD="python"
    else
        source venv/bin/activate
        PYTHON_CMD="python"
    fi
    
    print_header "🔧 Starting Backend Server"
    
    # Start backend in background
    log_info "Starting backend (http://localhost:8000)..."
    
    # Different approach for Windows vs Unix
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        # Windows (Git Bash)
        $PYTHON_CMD -m backend.main > backend.log 2>&1 &
        BACKEND_PID=$!
    else
        # Linux/Mac
        nohup $PYTHON_CMD -m backend.main > backend.log 2>&1 &
        BACKEND_PID=$!
    fi
    
    log_success "Backend started (PID: $BACKEND_PID)"
    
    # Wait for backend to start
    log_info "Waiting for backend to initialize..."
    for i in {1..15}; do
        if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
            log_success "Backend is responding!"
            log_info "API: http://localhost:8000"
            log_info "Docs: http://localhost:8000/docs"
            break
        fi
        sleep 1
        if [ $i -eq 15 ]; then
            log_error "Backend failed to start. Check backend.log for errors."
            cat backend.log
            exit 1
        fi
    done
    
    print_header "📱 Starting Mobile App"
    
    log_info "Starting Expo development server..."
    log_info "Scan the QR code with Expo Go app on your phone"
    log_info "Or press 'w' to open in web browser"
    log_info "Press Ctrl+C to stop all services"
    echo ""
    
    cd mobile
    npm start
    cd ..
}

################################################################################
# PHASE 3: Stop
################################################################################

stop() {
    print_header "🛑 Stopping Services"
    
    log_info "Stopping backend..."
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        taskkill //F //IM python.exe 2>/dev/null || true
        taskkill //F //IM pythonw.exe 2>/dev/null || true
    else
        pkill -f "backend.main" 2>/dev/null || true
        [ -n "$BACKEND_PID" ] && kill $BACKEND_PID 2>/dev/null || true
    fi
    
    log_info "Stopping mobile..."
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        taskkill //F //IM node.exe 2>/dev/null || true
    else
        pkill -f "expo start" 2>/dev/null || true
        pkill -f "react-native" 2>/dev/null || true
        [ -n "$MOBILE_PID" ] && kill $MOBILE_PID 2>/dev/null || true
    fi
    
    log_success "All services stopped"
}

################################################################################
# Main
################################################################################

case "${1:-}" in
    setup)
        setup
        ;;
    run)
        run
        ;;
    stop)
        stop
        ;;
    *)
        print_header "🏠 IoT Smart Home Agent-Based System"
        echo "Usage: $0 {setup|run|stop}"
        echo ""
        echo "Commands:"
        echo "  setup  - Install all dependencies (first time only)"
        echo "  run    - Start backend and mobile app"
        echo "  stop   - Stop all running services"
        echo ""
        echo "Quick start:"
        echo "  1. $0 setup    # Install dependencies"
        echo "  2. Edit .env and add your OpenAI API key"
        echo "  3. $0 run      # Start the system"
        echo ""
        exit 1
        ;;
esac
