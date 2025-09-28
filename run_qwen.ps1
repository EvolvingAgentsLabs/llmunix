# Quick start script for Qwen Runtime (PowerShell version)

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "     LLMunix Qwen Runtime Launcher      " -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Check if .env exists
if (-not (Test-Path .env)) {
    if (Test-Path .env.example) {
        Write-Host "No .env file found. Creating from .env.example..." -ForegroundColor Yellow
        Copy-Item .env.example .env
        Write-Host "Please edit .env and add your OpenRouter API key" -ForegroundColor Yellow
        Write-Host "Get a free key at: https://openrouter.ai/keys" -ForegroundColor Green
        exit 1
    } else {
        Write-Host "Error: No .env or .env.example file found" -ForegroundColor Red
        exit 1
    }
}

# Check if API key is set
$envContent = Get-Content .env -Raw
if ($envContent -match "your-api-key-here") {
    Write-Host "Please update your OpenRouter API key in .env" -ForegroundColor Yellow
    Write-Host "Get a free key at: https://openrouter.ai/keys" -ForegroundColor Green
    exit 1
}

# Install dependencies if needed
Write-Host "Checking dependencies..." -ForegroundColor Cyan
pip install -q openai python-dotenv requests 2>$null

# Run the runtime based on parameter
switch ($args[0]) {
    "test" {
        Write-Host "Running test suite..." -ForegroundColor Green
        python test_qwen_runtime.py
    }
    "interactive" {
        Write-Host "Starting interactive mode..." -ForegroundColor Green
        python qwen_runtime.py interactive
    }
    default {
        Write-Host "Running default Project Aorta scenario..." -ForegroundColor Green
        Write-Host "Use '.\run_qwen.ps1 interactive' for interactive mode" -ForegroundColor Gray
        Write-Host "Use '.\run_qwen.ps1 test' to run tests" -ForegroundColor Gray
        Write-Host ""
        python qwen_runtime.py
    }
}