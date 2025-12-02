"""
RoboOS - FastAPI Server (v3.4.0)

Production-ready REST API server for robot control via LLM OS.

This server provides:
- Natural language robot control endpoints
- Safety monitoring and reporting
- State visualization (cockpit/operator views)
- WebSocket for real-time updates
- Session management
- Sentience Layer integration for adaptive behavior
"""

import sys
import os
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from boot.llm_os import LLMOS
from boot.config import LLMOSConfig, SentienceConfig
from kernel.agent_loader import AgentLoader
from sentience.sentience import SentienceManager
from sentience.cognitive_kernel import CognitiveKernel
from plugins.robot_controller import ROBOT_CONTROLLER_TOOLS
from robot_state import get_robot_state, reset_robot_state
from safety_hook import get_safety_hook

# Agents directory path (Markdown agents)
AGENTS_DIR = Path(__file__).parent / "workspace" / "agents"


# ============================================================================
# Pydantic Models
# ============================================================================

class CommandRequest(BaseModel):
    """Request model for robot commands."""
    command: str
    session_id: Optional[str] = "default"
    agent: Optional[str] = "operator"  # or "safety_officer"


class MoveRequest(BaseModel):
    """Direct movement request."""
    x: Optional[float] = None
    y: Optional[float] = None
    z: Optional[float] = None
    theta: Optional[float] = None


class ToolRequest(BaseModel):
    """Tool activation request."""
    activate: bool


class ViewRequest(BaseModel):
    """Camera view request."""
    view_type: str = "cockpit"  # or "operator"


# ============================================================================
# FastAPI App Setup
# ============================================================================

app = FastAPI(
    title="RoboOS API",
    description="LLM OS-powered robot control system with Sentience Layer",
    version="3.4.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Global State
# ============================================================================

llmos_instance: Optional[LLMOS] = None
operator_agent = None
safety_officer_agent = None
websocket_connections: list[WebSocket] = []

# Sentience Layer components (v3.4.0)
sentience_manager: Optional[SentienceManager] = None
cognitive_kernel: Optional[CognitiveKernel] = None


# ============================================================================
# Initialization
# ============================================================================

def initialize_llmos():
    """Initialize LLM OS instance, agents, and Sentience Layer."""
    global llmos_instance, operator_agent, safety_officer_agent
    global sentience_manager, cognitive_kernel

    if llmos_instance is not None:
        return  # Already initialized

    # Configure LLM OS with robotics-focused sentience settings
    # High safety setpoint is critical for robot control
    config = LLMOSConfig(
        workspace=Path(__file__).parent / "workspace",
        sentience=SentienceConfig(
            enable_sentience=True,
            safety_setpoint=0.8,  # Very high safety for robot control
            curiosity_setpoint=0.1,  # Low curiosity - focus on precision
            energy_setpoint=0.6,  # Moderate energy for sustained operation
            self_confidence_setpoint=0.5,  # Balanced confidence
            boredom_threshold=-0.4,  # Higher threshold - routine is good for robots
            state_file="state/robo_sentience.json"
        )
    )

    # Initialize Sentience Layer
    sentience_config = config.sentience
    sentience_manager = SentienceManager(
        safety_setpoint=sentience_config.safety_setpoint,
        curiosity_setpoint=sentience_config.curiosity_setpoint,
        energy_setpoint=sentience_config.energy_setpoint,
        self_confidence_setpoint=sentience_config.self_confidence_setpoint,
        boredom_threshold=sentience_config.boredom_threshold
    )
    cognitive_kernel = CognitiveKernel(sentience_manager)
    print("✓ Sentience Layer initialized (robotics profile)")

    # Create LLM OS instance
    llmos_instance = LLMOS()

    # Register all robot controller tools
    for tool in ROBOT_CONTROLLER_TOOLS:
        llmos_instance.register_tool(
            name=tool['name'],
            func=tool['function'],
            description=tool['description']
        )

    # Register safety hook
    llmos_instance.register_hook('pre_tool_use', get_safety_hook())

    # Load agents from Markdown files
    agent_loader = AgentLoader(agents_dir=str(AGENTS_DIR))

    # Load operator agent
    operator_def = agent_loader.load_agent("operator")
    if operator_def:
        operator_agent = llmos_instance.create_agent(
            name=operator_def.name,
            mode=operator_def.metadata.get("mode", "learner"),
            system_prompt=operator_def.system_prompt,
            available_tools=operator_def.tools
        )
        print("✓ Operator agent loaded from Markdown")
    else:
        raise RuntimeError("Failed to load operator agent from workspace/agents/operator.md")

    # Load safety officer agent (only monitoring tools)
    safety_def = agent_loader.load_agent("safety-officer")
    if safety_def:
        safety_officer_agent = llmos_instance.create_agent(
            name=safety_def.name,
            mode=safety_def.metadata.get("mode", "learner"),
            system_prompt=safety_def.system_prompt,
            available_tools=safety_def.tools  # Tools restricted in markdown definition
        )
        print("✓ Safety officer agent loaded from Markdown")
    else:
        raise RuntimeError("Failed to load safety officer agent from workspace/agents/safety-officer.md")

    print("✓ LLM OS initialized")
    print("✓ Safety hook registered")


@app.on_event("startup")
async def startup_event():
    """Initialize on server startup."""
    print("\n" + "="*70)
    print("  RoboOS Server Starting...")
    print("="*70 + "\n")
    initialize_llmos()
    print("\n✓ Server ready!")
    print(f"  API docs: http://localhost:8000/docs")
    print(f"  Health: http://localhost:8000/health\n")


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with service info."""
    return {
        "service": "RoboOS API",
        "version": "3.4.0",
        "status": "operational",
        "message": "LLM OS-powered robot control system with Sentience Layer",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "state": "/state",
            "sentience": "/sentience",
            "command": "/command [POST]",
            "move": "/move [POST]",
            "tool": "/tool [POST]",
            "view": "/view [POST]",
            "safety": "/safety",
            "reset": "/reset [POST]",
            "emergency": "/emergency [POST]"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    robot_state = get_robot_state()
    return {
        "status": "healthy" if not robot_state.emergency_stop else "emergency_stop",
        "timestamp": datetime.now().isoformat(),
        "emergency_stop": robot_state.emergency_stop,
        "llmos_ready": llmos_instance is not None
    }


@app.get("/state")
async def get_state():
    """Get current robot state."""
    robot_state = get_robot_state()
    return {
        "state": robot_state.get_state(),
        "safety_limits": robot_state.safety_limits.to_dict(),
        "recent_actions": robot_state.history[-10:]
    }


@app.post("/command")
async def execute_command(request: CommandRequest):
    """
    Execute a natural language command via the operator or safety officer agent.

    Example requests:
    - {"command": "Move 30cm to the right"}
    - {"command": "Show me the cockpit view"}
    - {"command": "Check safety status", "agent": "safety_officer"}
    """
    if llmos_instance is None:
        initialize_llmos()

    # Select agent
    agent = operator_agent if request.agent == "operator" else safety_officer_agent

    if agent is None:
        raise HTTPException(status_code=500, detail="Agent not initialized")

    # Get current sentience state for adaptive behavior
    sentience_state = None
    if sentience_manager and cognitive_kernel:
        policy = cognitive_kernel.derive_policy()
        sentience_state = {
            "latent_mode": policy.latent_mode.value,
            "valence": sentience_manager.get_valence(),
            "safety_level": "high" if sentience_manager.get_valence()["safety"] > 0.6 else "normal"
        }
        # Track command as interaction
        sentience_manager.on_interaction()

    try:
        # Execute command
        response = await agent.run(request.command)

        # Track successful execution
        if sentience_manager:
            sentience_manager.on_success()

        result = {
            "success": True,
            "command": request.command,
            "agent": request.agent,
            "response": response,
            "timestamp": datetime.now().isoformat()
        }

        # Include sentience state if available
        if sentience_state:
            result["sentience"] = sentience_state

        return result

    except Exception as e:
        # Track failure
        if sentience_manager:
            sentience_manager.on_failure()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/move")
async def direct_move(request: MoveRequest):
    """
    Direct movement endpoint (bypasses natural language, uses tool directly).

    WARNING: This still goes through the safety hook!
    """
    if llmos_instance is None:
        initialize_llmos()

    try:
        robot_state = get_robot_state()
        current = robot_state.position

        # Use provided values or keep current
        x = request.x if request.x is not None else current.x
        y = request.y if request.y is not None else current.y
        z = request.z if request.z is not None else current.z
        theta = request.theta if request.theta is not None else current.theta

        # Import tool function
        from plugins.robot_controller import move_to

        # Execute move (safety hook will validate)
        result = await move_to(x, y, z, theta)

        return {
            "success": True,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tool")
async def control_tool(request: ToolRequest):
    """Activate or deactivate the robot tool."""
    if llmos_instance is None:
        initialize_llmos()

    try:
        from plugins.robot_controller import toggle_tool
        result = await toggle_tool(request.activate)

        return {
            "success": True,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/view")
async def get_view(request: ViewRequest):
    """Get camera feed view (cockpit or operator)."""
    try:
        from plugins.robot_controller import get_camera_feed
        view = await get_camera_feed(request.view_type)

        return {
            "success": True,
            "view_type": request.view_type,
            "view": view,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/safety")
async def get_safety_status():
    """Get safety status and violation history."""
    robot_state = get_robot_state()
    safety_hook = get_safety_hook()

    is_safe, reason = robot_state.safety_limits.is_position_safe(robot_state.position)

    result = {
        "current_position_safe": is_safe,
        "reason": reason,
        "emergency_stop": robot_state.emergency_stop,
        "violations": safety_hook.get_violations_summary(),
        "safety_limits": robot_state.safety_limits.to_dict()
    }

    # Include sentience safety level
    if sentience_manager:
        valence = sentience_manager.get_valence()
        result["sentience_safety"] = {
            "safety_valence": valence["safety"],
            "level": "critical" if valence["safety"] > 0.7 else "elevated" if valence["safety"] > 0.5 else "normal"
        }

    return result


@app.get("/sentience")
async def get_sentience_state():
    """
    Get current Sentience Layer state (v3.4.0).

    Returns internal valence variables and derived latent mode.
    This is used to understand the system's current behavioral profile.
    """
    if not sentience_manager or not cognitive_kernel:
        return {
            "enabled": False,
            "message": "Sentience Layer not initialized"
        }

    valence = sentience_manager.get_valence()
    policy = cognitive_kernel.derive_policy()

    # Robotics-specific mode descriptions
    mode_descriptions = {
        "auto_creative": "ADAPTIVE mode - Exploring alternative approaches (unusual for robotics)",
        "auto_contained": "PRECISION mode - Focused on exact, controlled movements",
        "balanced": "STANDARD mode - Normal operation within safety parameters",
        "recovery": "RECOVERY mode - Reduced operations, conservative movements",
        "cautious": "MAXIMUM SAFETY mode - Extra validation, minimal movements"
    }

    return {
        "enabled": True,
        "valence": valence,
        "latent_mode": policy.latent_mode.value,
        "mode_description": mode_descriptions.get(policy.latent_mode.value, "Unknown mode"),
        "policy": {
            "exploration_rate": policy.exploration_rate,
            "verbosity": policy.verbosity,
            "self_improvement_enabled": policy.self_improvement_enabled
        },
        "robotics_profile": {
            "safety_priority": "HIGH" if valence["safety"] > 0.6 else "NORMAL",
            "precision_mode": valence["curiosity"] < 0.2,  # Low curiosity = high precision
            "operational_readiness": valence["energy"] > 0.4
        },
        "timestamp": datetime.now().isoformat()
    }


@app.post("/reset")
async def reset_system():
    """Reset robot to home position and clear state."""
    reset_robot_state()
    safety_hook = get_safety_hook()
    safety_hook.reset_violations()

    return {
        "success": True,
        "message": "Robot reset to home position",
        "state": get_robot_state().get_state()
    }


@app.post("/emergency")
async def trigger_emergency():
    """Trigger emergency stop."""
    from plugins.robot_controller import emergency_stop
    result = await emergency_stop()

    # Notify WebSocket clients
    await broadcast_to_websockets({
        "type": "emergency_stop",
        "message": "EMERGENCY STOP ACTIVATED",
        "timestamp": datetime.now().isoformat()
    })

    return {
        "success": True,
        "result": result
    }


# ============================================================================
# WebSocket for Real-Time Updates
# ============================================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time robot state updates.

    Clients can connect to receive live updates when robot state changes.
    Includes sentience state in v3.4.0+.
    """
    await websocket.accept()
    websocket_connections.append(websocket)

    try:
        while True:
            # Send periodic state updates
            robot_state = get_robot_state()
            update = {
                "type": "state_update",
                "state": robot_state.get_state(),
                "timestamp": datetime.now().isoformat()
            }

            # Include sentience state in updates
            if sentience_manager and cognitive_kernel:
                policy = cognitive_kernel.derive_policy()
                update["sentience"] = {
                    "latent_mode": policy.latent_mode.value,
                    "safety_valence": sentience_manager.get_valence()["safety"],
                    "operational_readiness": sentience_manager.get_valence()["energy"] > 0.4
                }

            await websocket.send_json(update)
            await asyncio.sleep(1)  # Update every second

    except WebSocketDisconnect:
        websocket_connections.remove(websocket)


async def broadcast_to_websockets(message: Dict[str, Any]):
    """Broadcast a message to all connected WebSocket clients."""
    for connection in websocket_connections[:]:  # Copy list to avoid modification during iteration
        try:
            await connection.send_json(message)
        except Exception:
            # Remove dead connections
            websocket_connections.remove(connection)


# ============================================================================
# Server Entry Point
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
