#!/bin/bash

# Quick start script for Qwen Runtime

echo "========================================="
echo "     LLMunix Qwen Runtime Launcher      "
echo "========================================="

# Check if .env exists
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        echo "No .env file found. Creating from .env.example..."
        cp .env.example .env
        echo "Please edit .env and add your OpenRouter API key"
        echo "Get a free key at: https://openrouter.ai/keys"
        exit 1
    else
        echo "Error: No .env or .env.example file found"
        exit 1
    fi
fi

# Check if API key is set
if grep -q "your-api-key-here" .env; then
    echo "Please update your OpenRouter API key in .env"
    echo "Get a free key at: https://openrouter.ai/keys"
    exit 1
fi

# Install dependencies if needed
echo "Checking dependencies..."
pip install -q openai python-dotenv requests 2>/dev/null

# Run the runtime
if [ "$1" == "test" ]; then
    echo "Running test suite..."
    python test_qwen_runtime.py
elif [ "$1" == "interactive" ]; then
    echo "Starting interactive mode..."
    python qwen_runtime.py interactive
else
    echo "Running default Project Aorta scenario..."
    echo "Use './run_qwen.sh interactive' for interactive mode"
    echo "Use './run_qwen.sh test' to run tests"
    echo ""
    python qwen_runtime.py
fi