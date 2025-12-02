#!/bin/bash

# RoboOS - Automated Setup and Run Script
#
# This script:
# 1. Creates a virtual environment
# 2. Installs dependencies
# 3. Runs the interactive demo

set -e  # Exit on error

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║                     ROBO-OS SETUP                             ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed."
    echo "   Please install Python 3.10+ and try again."
    exit 1
fi

echo "✓ Python 3 found"

# Check for API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo ""
    echo "⚠️  Warning: ANTHROPIC_API_KEY environment variable not set."
    echo "   You can set it with:"
    echo "   export ANTHROPIC_API_KEY='your-key-here'"
    echo ""
    read -p "   Do you want to continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "✓ Pip upgraded"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt > /dev/null 2>&1
echo "✓ Dependencies installed"

# Install LLM OS from parent directory
echo ""
echo "Installing LLM OS..."
pip install -e ../.. > /dev/null 2>&1
echo "✓ LLM OS installed"

# Success message
echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║                   SETUP COMPLETE!                             ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "What would you like to do?"
echo ""
echo "  1. Run interactive demo (recommended)"
echo "  2. Start FastAPI server"
echo "  3. Exit (activate venv manually)"
echo ""
read -p "Choose (1-3): " choice

case $choice in
    1)
        echo ""
        echo "Starting interactive demo..."
        echo ""
        python3 demo.py
        ;;
    2)
        echo ""
        echo "Starting FastAPI server..."
        echo "  Server will be available at: http://localhost:8000"
        echo "  API docs at: http://localhost:8000/docs"
        echo ""
        python3 server.py
        ;;
    3)
        echo ""
        echo "To activate the virtual environment manually, run:"
        echo "  source venv/bin/activate"
        echo ""
        echo "Then you can run:"
        echo "  python3 demo.py    (interactive demo)"
        echo "  python3 server.py  (API server)"
        echo ""
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac
