"""
Wabi App Server - LLMunix API for On-Demand Mobile App Generation

This FastAPI server acts as the backend "App Server" for the Wabi POC,
receiving user goals from mobile shell apps and returning personalized UI-MD definitions.

Architecture:
- Receives HTTP requests with user goals (e.g., "create morning briefing")
- Invokes LLMunix SystemAgent to orchestrate UI generation
- Returns UI-MD markdown documents for mobile shell rendering
- Handles user actions and UI updates
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List, Any
import json
import subprocess
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Wabi App Server",
    description="LLMunix backend for on-demand mobile app generation",
    version="1.0.0"
)

# Enable CORS for mobile app access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
LLMUNIX_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROJECT_OUTPUT_DIR = os.path.join(LLMUNIX_ROOT, "projects", "Project_wabi_poc", "output")
USER_PROFILES_DIR = os.path.join(LLMUNIX_ROOT, "system", "user_profiles")

# Ensure output directory exists
os.makedirs(PROJECT_OUTPUT_DIR, exist_ok=True)


# Request/Response Models
class AppGenerationRequest(BaseModel):
    """Request to generate a new app UI"""
    goal: str  # e.g., "Create a morning briefing app"
    user_id: str  # e.g., "user123"
    context: Optional[Dict[str, Any]] = None  # Additional context


class AppActionRequest(BaseModel):
    """Request to handle a user action in an existing app"""
    app_id: str  # e.g., "morning-briefing-user123"
    user_id: str
    action_id: str  # e.g., "refresh_weather"
    params: Optional[Dict[str, Any]] = None  # Action-specific parameters


class AppGenerationResponse(BaseModel):
    """Response containing generated UI-MD"""
    success: bool
    app_id: str
    ui_md: str  # Complete UI-MD markdown document
    metadata: Dict[str, Any]  # Generation metadata
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: str


# Helper Functions
def invoke_llmunix_agent(prompt: str, user_id: str) -> Dict[str, Any]:
    """
    Invoke LLMunix agent system to process a request.

    In a production system, this would integrate with Claude Code's Task tool.
    For the POC, we'll simulate the agent invocation and generate structured responses.
    """
    logger.info(f"Invoking LLMunix agent for user {user_id}: {prompt}")

    # For POC: Return simulated successful response
    # In real implementation, this would use Claude Code's Task tool:
    # Task("system-agent", prompt=f"Execute: {prompt} for user {user_id}")

    return {
        "success": True,
        "output": "Agent invocation simulated for POC",
        "prompt": prompt,
        "user_id": user_id
    }


def generate_app_ui_md(goal: str, user_id: str, context: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Generate UI-MD for a given goal by orchestrating LLMunix agents.

    Workflow:
    1. Invoke UserMemoryAgent to get personalization data
    2. Invoke UIGeneratorAgent to create UI-MD
    3. Save UI-MD to project output directory
    4. Return UI-MD and metadata
    """
    logger.info(f"Generating UI-MD for goal: '{goal}', user: {user_id}")

    # Generate app_id
    goal_slug = goal.lower().replace(" ", "-")[:30]
    app_id = f"{goal_slug}-{user_id}"
    timestamp = datetime.utcnow().isoformat() + "Z"

    # Step 1: Get user memory (simulation for POC)
    logger.info("Step 1: Querying UserMemoryAgent")
    user_memory = load_user_memory(user_id)

    # Step 2: Generate UI-MD (simulation for POC)
    logger.info("Step 2: Generating UI-MD via UIGeneratorAgent")

    # For POC, generate a sample Morning Briefing UI-MD
    ui_md = generate_morning_briefing_ui_md(user_id, user_memory, app_id, timestamp)

    # Step 3: Save UI-MD to output directory
    output_file = os.path.join(PROJECT_OUTPUT_DIR, f"{app_id}.md")
    with open(output_file, 'w') as f:
        f.write(ui_md)
    logger.info(f"Saved UI-MD to {output_file}")

    # Step 4: Log to user memory (in production)
    # log_app_creation(user_id, app_id, timestamp)

    return {
        "success": True,
        "app_id": app_id,
        "ui_md": ui_md,
        "metadata": {
            "generated_at": timestamp,
            "user_id": user_id,
            "goal": goal,
            "output_file": output_file,
            "personalization": {
                "location": user_memory.get("last_seen_location", "Unknown"),
                "theme": user_memory.get("preferences", {}).get("theme", "light"),
                "interests": user_memory.get("interests", [])
            }
        }
    }


def load_user_memory(user_id: str) -> Dict[str, Any]:
    """Load user memory from file"""
    memory_file = os.path.join(USER_PROFILES_DIR, user_id, "memory.md")

    if not os.path.exists(memory_file):
        logger.warning(f"User memory not found for {user_id}, using defaults")
        return {
            "user_id": user_id,
            "name": user_id,
            "last_seen_location": "San Francisco, CA",
            "preferences": {
                "theme": "light",
                "temperature_units": "Fahrenheit"
            },
            "interests": ["technology"]
        }

    # Parse YAML frontmatter (simplified for POC)
    with open(memory_file, 'r') as f:
        content = f.read()

    # Extract frontmatter (between --- markers)
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            import yaml
            try:
                memory_data = yaml.safe_load(parts[1])
                logger.info(f"Loaded memory for {user_id}: {memory_data.get('name', 'Unknown')}")
                return memory_data
            except Exception as e:
                logger.error(f"Error parsing user memory YAML: {e}")

    return {"user_id": user_id, "name": user_id}


def generate_morning_briefing_ui_md(user_id: str, user_memory: Dict, app_id: str, timestamp: str) -> str:
    """Generate a Morning Briefing UI-MD (simulated for POC)"""

    # Extract personalization data
    name = user_memory.get("name", user_id)
    location = user_memory.get("last_seen_location", "San Francisco, CA")
    theme = user_memory.get("preferences", {}).get("theme", "dark")
    interests = user_memory.get("interests", ["technology"])

    # Simulate data gathering (in production, would invoke WeatherAgent, NewsAgent, etc.)
    # For POC, use hardcoded sample data

    ui_md = f"""---
app_id: {app_id}
user_id: {user_id}
layout: vertical_stack
theme: {theme}
generated_at: "{timestamp}"
version: "1.0"
---

# Morning Briefing for {name}

<component type="Header">
  text: "Good Morning, {name}! ☀️"
  size: 24
  alignment: center
</component>

<component type="Divider">
  style: solid
</component>

<component type="Card">
  title: "{location} Weather"
  content: |
    **Now:** 65°F, Sunny
    **High:** 72°F
    **Low:** 58°F

    Perfect day for a walk!
  action:
    id: "refresh_weather"
    label: "Refresh"
    style: secondary
</component>

<component type="Card">
  title: "Today's Calendar"
  content: |
    **09:00** - Team Sync (30 min)
    **11:00** - Project Deep Dive (1 hr)
    **14:30** - Dentist Appointment

    Next meeting in 45 minutes
</component>

<component type="List">
  title: "Top Tech News"
  items:
    - "GPT-5 rumors circulate after OpenAI teaser"
    - "Quantum computing breakthrough at Stanford"
    - "New React framework gains traction"
    - "Anthropic releases Claude 4"
    - "Apple Vision Pro sales exceed expectations"
  selectable: true
  action:
    id: "open_news_article"
</component>

<component type="Button">
  label: "Customize Briefing"
  action:
    id: "customize_app"
    style: primary
</component>

<component type="Text">
  content: "Last updated: {timestamp[:10]} {timestamp[11:19]}"
  size: 12
  color: "#888888"
  alignment: center
</component>
"""
    return ui_md


def handle_app_action(app_id: str, user_id: str, action_id: str, params: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Handle a user action on an existing app.

    Actions trigger UI updates by re-generating or modifying the UI-MD.
    """
    logger.info(f"Handling action '{action_id}' for app {app_id}, user {user_id}")

    # Load existing UI-MD
    ui_md_file = os.path.join(PROJECT_OUTPUT_DIR, f"{app_id}.md")

    if not os.path.exists(ui_md_file):
        raise FileNotFoundError(f"App UI-MD not found: {app_id}")

    # Route action to appropriate handler
    if action_id == "refresh_weather":
        return handle_refresh_weather(app_id, user_id, ui_md_file)
    elif action_id == "refresh_news":
        return handle_refresh_news(app_id, user_id, ui_md_file)
    elif action_id == "customize_app":
        return handle_customize_app(app_id, user_id, params)
    elif action_id == "open_news_article":
        return handle_open_news_article(app_id, user_id, params)
    else:
        logger.warning(f"Unknown action_id: {action_id}")
        return {
            "success": False,
            "error": f"Unknown action: {action_id}"
        }


def handle_refresh_weather(app_id: str, user_id: str, ui_md_file: str) -> Dict[str, Any]:
    """Handle weather refresh action"""
    logger.info("Refreshing weather data")

    # In production: Invoke WeatherAgent to get fresh data
    # For POC: Return updated UI-MD with new timestamp

    with open(ui_md_file, 'r') as f:
        ui_md = f.read()

    # Update timestamp in UI-MD (simplified)
    new_timestamp = datetime.utcnow().isoformat() + "Z"
    # In real implementation, would regenerate weather card with fresh data

    return {
        "success": True,
        "app_id": app_id,
        "ui_md": ui_md,  # Return same UI-MD for POC
        "action": "refresh_weather",
        "timestamp": new_timestamp
    }


def handle_refresh_news(app_id: str, user_id: str, ui_md_file: str) -> Dict[str, Any]:
    """Handle news refresh action"""
    logger.info("Refreshing news data")

    # In production: Invoke NewsAgent to get fresh headlines
    # For POC: Return same UI-MD

    with open(ui_md_file, 'r') as f:
        ui_md = f.read()

    return {
        "success": True,
        "app_id": app_id,
        "ui_md": ui_md,
        "action": "refresh_news",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


def handle_customize_app(app_id: str, user_id: str, params: Optional[Dict]) -> Dict[str, Any]:
    """Handle app customization action"""
    logger.info(f"Customizing app with params: {params}")

    # In production: Generate customization UI or apply settings
    # For POC: Return success message

    return {
        "success": True,
        "app_id": app_id,
        "action": "customize_app",
        "message": "Customization interface would be generated here"
    }


def handle_open_news_article(app_id: str, user_id: str, params: Optional[Dict]) -> Dict[str, Any]:
    """Handle opening a news article"""
    logger.info(f"Opening news article with params: {params}")

    # In production: Return article content or URL
    # For POC: Return article metadata

    return {
        "success": True,
        "app_id": app_id,
        "action": "open_news_article",
        "article_url": "https://example.com/article",
        "message": "Article would be opened in browser or in-app view"
    }


# API Endpoints

@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.utcnow().isoformat() + "Z"
    )


@app.get("/health", response_model=HealthResponse)
async def health():
    """Detailed health check"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.utcnow().isoformat() + "Z"
    )


@app.post("/api/v1/generate", response_model=AppGenerationResponse)
async def generate_app(request: AppGenerationRequest, background_tasks: BackgroundTasks):
    """
    Generate a new personalized app UI based on user goal.

    Example request:
    {
        "goal": "Create a morning briefing app",
        "user_id": "user123",
        "context": {}
    }

    Returns UI-MD markdown document ready for mobile shell rendering.
    """
    try:
        logger.info(f"Received generation request: goal='{request.goal}', user={request.user_id}")

        # Generate UI-MD via LLMunix agent orchestration
        result = generate_app_ui_md(request.goal, request.user_id, request.context)

        if result["success"]:
            return AppGenerationResponse(
                success=True,
                app_id=result["app_id"],
                ui_md=result["ui_md"],
                metadata=result["metadata"]
            )
        else:
            raise HTTPException(status_code=500, detail="UI generation failed")

    except Exception as e:
        logger.error(f"Error generating app: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/action")
async def handle_action(request: AppActionRequest):
    """
    Handle a user action on an existing app.

    Example request:
    {
        "app_id": "morning-briefing-user123",
        "user_id": "user123",
        "action_id": "refresh_weather",
        "params": {}
    }

    Returns updated UI-MD or action result.
    """
    try:
        logger.info(f"Received action request: action='{request.action_id}', app={request.app_id}")

        result = handle_app_action(request.app_id, request.user_id, request.action_id, request.params)

        return result

    except FileNotFoundError as e:
        logger.error(f"App not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error handling action: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/apps/{user_id}")
async def list_user_apps(user_id: str):
    """
    List all apps created by a user.

    Returns app metadata for display in app library.
    """
    try:
        logger.info(f"Listing apps for user {user_id}")

        # Load user memory to get apps_created
        user_memory = load_user_memory(user_id)
        apps_created = user_memory.get("apps_created", [])

        return {
            "user_id": user_id,
            "apps": apps_created,
            "count": len(apps_created)
        }

    except Exception as e:
        logger.error(f"Error listing apps: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/user/{user_id}/preferences")
async def get_user_preferences(user_id: str):
    """Get user preferences for client-side customization"""
    try:
        user_memory = load_user_memory(user_id)

        return {
            "user_id": user_id,
            "name": user_memory.get("name", user_id),
            "preferences": user_memory.get("preferences", {}),
            "interests": user_memory.get("interests", []),
            "theme": user_memory.get("preferences", {}).get("theme", "light")
        }

    except Exception as e:
        logger.error(f"Error getting preferences: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Startup message
@app.on_event("startup")
async def startup_event():
    logger.info("=" * 60)
    logger.info("🚀 Wabi App Server Starting")
    logger.info("=" * 60)
    logger.info(f"LLMunix Root: {LLMUNIX_ROOT}")
    logger.info(f"Output Directory: {PROJECT_OUTPUT_DIR}")
    logger.info(f"User Profiles: {USER_PROFILES_DIR}")
    logger.info("=" * 60)
    logger.info("API Documentation: http://localhost:8000/docs")
    logger.info("Health Check: http://localhost:8000/health")
    logger.info("=" * 60)


# Run server
if __name__ == "__main__":
    import uvicorn

    print("\n" + "=" * 60)
    print("🌟 WABI APP SERVER - LLMunix POC")
    print("=" * 60)
    print("Starting FastAPI server on http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")
    print("=" * 60 + "\n")

    uvicorn.run(
        "wabi_app_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
