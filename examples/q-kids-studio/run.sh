#!/bin/bash
# Q-Kids Studio Backend Startup Script

set -e  # Exit on error

echo "🦉 Q-Kids Studio Backend Launcher"
echo "=================================="
echo ""

# Check if we're in the right directory
if [ ! -f "server.py" ]; then
    echo "❌ Error: server.py not found!"
    echo "   Please run this script from the q-kids-studio directory"
    exit 1
fi

# Check Python version
echo "🔍 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Found Python $python_version"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 No virtual environment found. Creating one..."
    python3 -m venv venv
    echo "   ✅ Virtual environment created!"
fi

# Activate virtual environment
echo ""
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
echo ""
echo "📚 Checking dependencies..."
if ! python -c "import fastapi" 2>/dev/null; then
    echo "   Installing requirements..."
    pip install -r requirements.txt
    echo "   ✅ Dependencies installed!"
else
    echo "   ✅ Dependencies already installed"
fi

# Check if qiskit is installed
if ! python -c "import qiskit" 2>/dev/null; then
    echo ""
    echo "⚠️  Qiskit not found! Installing..."
    pip install qiskit qiskit-aer
fi

# Create necessary directories
echo ""
echo "📁 Setting up directories..."
mkdir -p player_data
mkdir -p logs
echo "   ✅ Directories ready"

# Check for API keys
echo ""
echo "🔑 Checking configuration..."
if [ -z "$OPENAI_API_KEY" ] && [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "   ⚠️  WARNING: No API keys found in environment!"
    echo "   Set OPENAI_API_KEY or ANTHROPIC_API_KEY to use LLM features"
    echo ""
    read -p "   Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "   ✅ API key found"
fi

# Start the server
echo ""
echo "🚀 Starting Q-Kids Studio Backend..."
echo "=================================="
echo ""
echo "📍 Server will be available at: http://localhost:8000"
echo "📖 API docs will be at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run with uvicorn
python3 server.py

# Deactivate virtual environment on exit
deactivate
