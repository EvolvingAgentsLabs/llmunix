#!/bin/bash
# Run script for Qiskit Studio Backend - LLM OS Edition

set -e  # Exit on error

echo "🚀 Starting Qiskit Studio Backend (LLM OS Edition)"
echo "================================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found"
    echo "   Creating from template..."
    cp .env.template .env
    echo "   ✅ Created .env file"
    echo "   ⚠️  Please edit .env and add your ANTHROPIC_API_KEY"
    echo ""
    read -p "Press Enter after setting your API key in .env..."
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "   ✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "   ✅ Dependencies installed"
echo ""

# Run the server
echo "🌐 Starting server..."
echo "   Host: ${SERVER_HOST:-0.0.0.0}"
echo "   Port: ${SERVER_PORT:-8000}"
echo ""
echo "   API Endpoints:"
echo "   - POST http://localhost:8000/chat (Chat & Code Generation)"
echo "   - POST http://localhost:8000/run (Code Execution)"
echo "   - GET  http://localhost:8000/stats (Statistics)"
echo ""
echo "   Press Ctrl+C to stop"
echo "================================================="
echo ""

python server.py "$@"
