"""
Minimal FastAPI app for Vercel detection.

This file exists only to satisfy Vercel's requirement for a FastAPI entrypoint.
The actual API functionality is in individual endpoint files:
- chat.py - Chat with LLM
- skills.py - Skills management
- sessions.py - Session management
- workflows.py - Workflow execution
- cron/* - Evolution cron jobs
"""
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

app = FastAPI(
    title="LLMos-Lite API",
    description="Git-backed, Skills-driven LLM Operating System",
    version="1.0.0"
)


@app.get("/api")
async def api_root():
    """API root - redirect to main app"""
    return RedirectResponse(url="/")


@app.get("/api/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "llmos-lite",
        "version": "1.0.0"
    }


# Vercel expects this export
handler = app
