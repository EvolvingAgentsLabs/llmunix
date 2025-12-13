"""
Vercel Function: Health check / redirect to Next.js app

This is a minimal API endpoint that doesn't require VolumeManager initialization.
The actual functionality is provided by:
- chat.py - Chat endpoint
- skills.py - Skills management
- sessions.py - Session management
- workflows.py - Workflow execution
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()


@app.get("/")
async def root():
    """Health check"""
    return JSONResponse({
        "status": "healthy",
        "service": "llmos-lite-api",
        "version": "1.0.0",
        "message": "API is running. Visit the main app at /",
        "endpoints": {
            "chat": "/api/chat",
            "skills": "/api/skills",
            "sessions": "/api/sessions",
            "workflows": "/api/workflows"
        }
    })


# Vercel expects the FastAPI app to be exported
handler = app
