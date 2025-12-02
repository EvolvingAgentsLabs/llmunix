#!/usr/bin/env python3
"""
Qiskit Studio Backend - LLM OS Edition (v3.4.0)

This FastAPI server acts as a bridge between the Qiskit Studio frontend
and the LLM OS backend, replacing the original Maestro-based microservices
(chat-agent, codegen-agent, coderun-agent) with a unified LLM OS implementation.

Key features:
- Drop-in replacement for qiskit-studio API endpoints
- Advanced Tool Use integration (PTC, Tool Search, Tool Examples)
- Sentience Layer (valence, homeostatic dynamics, cognitive kernel)
- Five execution modes: CRYSTALLIZED, FOLLOWER, MIXED, LEARNER, ORCHESTRATOR
- 90%+ token savings via Programmatic Tool Calling (PTC)
- Adaptive behavior based on internal state
- Built-in security hooks
- Unified memory management

API Endpoints (matching original qiskit-studio):
- POST /chat          - Chat agent (port 8000 in original)
- POST /chat/stream   - Streaming chat (SSE)
- POST /run           - Code execution (port 8002 in original)
- GET  /stats         - Enhanced stats with Execution Layer and Sentience metrics
- GET  /sentience     - NEW: View current internal state (v3.4.0)
"""

import asyncio
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pathlib import Path
import sys
import logging
import json
import re
from typing import Optional, Dict, Any, List, AsyncGenerator

# Add llmos to path - support both standalone and in-tree execution
LLMOS_ROOT = Path(__file__).parents[2]  # Go up to llm-os root
if (LLMOS_ROOT / "llmos").exists():
    sys.path.insert(0, str(LLMOS_ROOT))  # Add llm-os root to path
else:
    # Fallback: assume llmos is already in path or installed
    pass

from boot import LLMOS
from kernel.component_registry import ComponentRegistry
from kernel.agent_loader import AgentLoader

# Import configuration with LLMOSConfig support
sys.path.insert(0, str(Path(__file__).parent))
from config import Config
from plugins.qiskit_tools import execute_qiskit_code, validate_qiskit_code

# Agents directory path (Markdown agents)
AGENTS_DIR = Path(__file__).parent / "workspace" / "agents"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Qiskit Studio Backend - LLM OS Edition",
    description="Drop-in replacement for qiskit-studio backend using LLM OS v3.4.0 with Advanced Tool Use and Sentience Layer",
    version="3.4.0"
)

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global LLM OS instance (initialized on startup)
os_instance: Optional[LLMOS] = None
session_memory: Dict[str, List[Dict[str, str]]] = {}  # Session-based chat history

# Sentience components (initialized on startup)
sentience_manager = None
cognitive_kernel = None


def analyze_intent(user_input: str, conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Analyze user intent to determine routing strategy.

    Returns:
        Dict with:
        - agent: "quantum-architect" or "quantum-tutor"
        - mode: "LEARNER", "FOLLOWER", or "AUTO"
        - is_coding_task: bool
    """
    user_input_lower = user_input.lower()

    # Coding indicators
    coding_keywords = [
        "code", "circuit", "implement", "create", "generate", "write",
        "build", "program", "qubits", "gates", "measure", "execute",
        "bell state", "ghz", "grover", "shor", "vqe", "qaoa"
    ]

    # Question indicators
    question_keywords = [
        "what", "how", "why", "when", "where", "explain", "describe",
        "tell me", "difference", "compare", "teach", "help me understand"
    ]

    # Check for coding task
    is_coding = any(keyword in user_input_lower for keyword in coding_keywords)
    is_question = any(keyword in user_input_lower for keyword in question_keywords)

    # Determine agent
    if is_coding and not is_question:
        agent = "quantum-architect"
        # Check if it's a repeated pattern (FOLLOWER candidate)
        # In a real implementation, this would check memory for similar tasks
        mode = "AUTO"  # Let LLM OS dispatcher decide
    elif is_question and not is_coding:
        agent = "quantum-tutor"
        mode = "ORCHESTRATOR"  # Tutor uses orchestration for knowledge retrieval
    elif is_coding and is_question:
        # "How do I create a Bell state?" - hybrid
        agent = "quantum-architect"  # Architect can explain + provide code
        mode = "AUTO"
    else:
        # Default to tutor for general queries
        agent = "quantum-tutor"
        mode = "ORCHESTRATOR"

    logger.info(f"Intent analysis: agent={agent}, mode={mode}, is_coding={is_coding}")

    return {
        "agent": agent,
        "mode": mode,
        "is_coding_task": is_coding
    }


@app.on_event("startup")
async def startup():
    """Initialize LLM OS on server startup with Advanced Tool Use and Sentience Layer"""
    global os_instance, sentience_manager, cognitive_kernel

    logger.info("="*60)
    logger.info("Starting Qiskit Studio Backend (LLM OS v3.4.0)")
    logger.info("Advanced Tool Use: PTC, Tool Search, Tool Examples")
    logger.info("Sentience Layer: Valence, Homeostatic Dynamics, Cognitive Kernel")
    logger.info("="*60)

    # Get LLMOSConfig with Execution Layer and Sentience settings
    llmos_config = Config.get_llmos_config()

    # Log Execution Layer configuration
    logger.info(f"Execution Layer Configuration:")
    logger.info(f"  - PTC (Programmatic Tool Calling): {llmos_config.execution.enable_ptc}")
    logger.info(f"  - Tool Search: {llmos_config.execution.enable_tool_search}")
    logger.info(f"  - Tool Examples: {llmos_config.execution.enable_tool_examples}")
    logger.info(f"  - Use Embeddings: {llmos_config.execution.tool_search_use_embeddings}")
    logger.info(f"  - Auto-Crystallization: {llmos_config.dispatcher.auto_crystallization}")

    # Log Sentience Layer configuration
    logger.info(f"Sentience Layer Configuration:")
    logger.info(f"  - Enabled: {llmos_config.sentience.enable_sentience}")
    logger.info(f"  - Inject Internal State: {llmos_config.sentience.inject_internal_state}")
    logger.info(f"  - Auto-Improvement: {llmos_config.sentience.enable_auto_improvement}")
    logger.info(f"  - Safety Setpoint: {llmos_config.sentience.safety_setpoint}")
    logger.info(f"  - Curiosity Setpoint: {llmos_config.sentience.curiosity_setpoint}")

    # Initialize LLM OS with full configuration
    os_instance = LLMOS(config=llmos_config)

    # Initialize Sentience Layer if enabled
    if llmos_config.sentience.enable_sentience:
        try:
            from kernel.sentience import SentienceManager
            from kernel.cognitive_kernel import CognitiveKernel

            state_path = Path(__file__).parent / llmos_config.sentience.state_file
            state_path.parent.mkdir(parents=True, exist_ok=True)

            sentience_manager = SentienceManager(
                state_path=state_path,
                auto_persist=llmos_config.sentience.auto_persist
            )
            cognitive_kernel = CognitiveKernel(sentience_manager)

            logger.info(f"Sentience Layer initialized")
            logger.info(f"  - Current latent mode: {sentience_manager.get_state().latent_mode.value}")
            logger.info(f"  - Homeostatic cost: {sentience_manager.get_state().valence.homeostatic_cost():.4f}")
        except ImportError as e:
            logger.warning(f"Sentience Layer not available: {e}")
            sentience_manager = None
            cognitive_kernel = None

    # Register our custom Qiskit tools with the dispatcher for Execution Layer support
    logger.info("Registering Qiskit tools with Execution Layer...")
    os_instance.component_registry.register_tool(execute_qiskit_code)
    os_instance.component_registry.register_tool(validate_qiskit_code)

    # Also register with dispatcher for PTC/Tool Search support
    if hasattr(os_instance, 'dispatcher') and os_instance.dispatcher:
        os_instance.dispatcher.register_tool(execute_qiskit_code)
        os_instance.dispatcher.register_tool(validate_qiskit_code)

    # Load agents from Markdown files (Hybrid Architecture approach)
    logger.info("Loading specialized quantum agents from Markdown...")
    agent_loader = AgentLoader(agents_dir=str(AGENTS_DIR))

    # Load all agent definitions from Markdown files
    for agent_name in agent_loader.list_agents():
        agent_def = agent_loader.load_agent(agent_name)
        if agent_def:
            logger.info(f"  - Loaded agent: {agent_def.name}")
            # Convert AgentDefinition to AgentSpec for registry
            from kernel.agent_factory import AgentSpec
            spec = AgentSpec(
                name=agent_def.name,
                agent_type=agent_def.metadata.get("agent_type", "specialized"),
                category=agent_def.metadata.get("category", "quantum_computing"),
                description=agent_def.description,
                tools=agent_def.tools,
                system_prompt=agent_def.system_prompt,
                capabilities=agent_def.metadata.get("capabilities", []),
                version=agent_def.metadata.get("version", "1.0")
            )
            os_instance.component_registry.register_agent(spec)

    # Boot the OS
    await os_instance.boot()

    # Pre-load any quantum computing knowledge into L4 memory
    # This would normally load Qiskit documentation, but we'll skip for now
    agents_list = agent_loader.list_agents()
    logger.info("Backend initialization complete!")
    logger.info(f"Loaded {len(agents_list)} Markdown agents from {AGENTS_DIR}")
    logger.info("="*60)
    print()


@app.on_event("shutdown")
async def shutdown():
    """Shutdown LLM OS gracefully including Execution Layer"""
    global os_instance

    if os_instance:
        logger.info("Shutting down LLM OS...")

        # Shutdown dispatcher (cleans up PTC containers)
        if hasattr(os_instance, 'dispatcher') and os_instance.dispatcher:
            if hasattr(os_instance.dispatcher, 'shutdown'):
                await os_instance.dispatcher.shutdown()
                logger.info("Dispatcher and Execution Layer shut down")

        await os_instance.shutdown()


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Qiskit Studio Backend - LLM OS Edition",
        "version": "1.0.0",
        "llm_os_running": os_instance is not None and os_instance._running
    }


def extract_user_message(data: Dict[str, Any]) -> str:
    """
    Extract user message from various request formats.

    Supports:
    - messages: [{role: "user", content: "..."}]
    - input_value: "..."
    - prompt: "..."
    """
    # Check for messages array (standard format)
    messages = data.get("messages", [])
    if messages:
        return messages[-1].get("content", "")

    # Check for input_value (Maestro format)
    if data.get("input_value"):
        return data["input_value"]

    # Check for prompt (alternative format)
    if data.get("prompt"):
        return data["prompt"]

    return ""


def is_code_update_request(user_message: str) -> bool:
    """
    Detect if this is a code update/parameter change request (from codegen-agent).

    These requests have a specific format:
    ###[Node Label]
    ```
    code here
    ```
    NEW PARAMETERS:
    parameter: value
    """
    return user_message.strip().startswith("###[") and "NEW PARAMETERS:" in user_message


def extract_code_from_request(user_message: str) -> tuple[str, str, Dict[str, Any]]:
    """
    Extract node label, code, and parameters from a code update request.

    Returns:
        tuple: (node_label, current_code, parameters_dict)
    """
    # Extract node label
    label_match = re.search(r"###\[([^\]]+)\]", user_message)
    node_label = label_match.group(1) if label_match else "Unknown"

    # Extract code block
    code_match = re.search(r"```(?:python)?\s*(.*?)```", user_message, re.DOTALL)
    current_code = code_match.group(1).strip() if code_match else ""

    # Extract parameters
    params = {}
    params_section = user_message.split("NEW PARAMETERS:")
    if len(params_section) > 1:
        params_text = params_section[1].strip()
        # Parse key: value pairs
        for line in params_text.split("\n"):
            line = line.strip()
            if ":" in line and not line.startswith("#"):
                key, value = line.split(":", 1)
                params[key.strip()] = value.strip()

    return node_label, current_code, params


@app.post("/chat")
async def chat_endpoint(request: Request):
    """
    Chat endpoint - handles both conversational and code generation requests.

    This is the drop-in replacement for:
    - Original chat-agent (RAG-based Q&A) - port 8000
    - Original codegen-agent (code generation) - port 8001

    Request formats supported:
    1. Standard: {"messages": [{"role": "user", "content": "..."}]}
    2. Maestro: {"input_value": "...", "prompt": "..."}

    Response format (Maestro-compatible):
    {
        "response": "{\"final_prompt\": \"...\"}",
        "output": "..."
    }
    """
    if not os_instance:
        raise HTTPException(status_code=503, detail="LLM OS not initialized")

    try:
        data = await request.json()
        session_id = data.get("session_id", "default")

        # Extract user message from various formats
        user_message = extract_user_message(data)

        if not user_message:
            raise HTTPException(status_code=400, detail="No message provided")

        # Get or create session history
        if session_id not in session_memory:
            session_memory[session_id] = []

        conversation_history = session_memory[session_id]

        # Check if this is a code update request (codegen-agent style)
        if is_code_update_request(user_message):
            logger.info("Detected code update request (codegen-agent style)")
            node_label, current_code, params = extract_code_from_request(user_message)

            # Build a prompt for code modification
            enhanced_prompt = f"""You are an expert Qiskit programmer. Update the following code for the {node_label} node.

Current code:
```python
{current_code}
```

Apply these parameter changes:
{json.dumps(params, indent=2)}

Return ONLY the updated Python code. Do not include markdown formatting or explanations."""

            intent = {"agent": "quantum-architect", "mode": "AUTO", "is_coding_task": True}
        else:
            # Regular chat/Q&A request
            intent = analyze_intent(user_message, conversation_history)

            # Build enhanced prompt with conversation context
            if conversation_history:
                context = "\n".join([
                    f"{msg['role']}: {msg['content']}"
                    for msg in conversation_history[-5:]  # Last 5 messages
                ])
                enhanced_prompt = f"""Previous conversation:
{context}

Current request: {user_message}"""
            else:
                enhanced_prompt = user_message

        logger.info(f"Processing chat request: {user_message[:100]}...")
        logger.info(f"Routing to agent: {intent['agent']}, mode: {intent['mode']}")

        # Execute through LLM OS
        result = await os_instance.execute(
            goal=enhanced_prompt,
            mode=intent["mode"],
            max_cost_usd=2.0  # Max $2 per request
        )

        # Extract response
        response_text = result.get("output", "")
        cost = result.get("cost", 0.0)
        mode_used = result.get("mode", intent["mode"])
        cached = cost == 0.0  # If cost is 0, it was cached (FOLLOWER mode)

        # Update session memory
        conversation_history.append({"role": "user", "content": user_message})
        conversation_history.append({"role": "assistant", "content": response_text})
        session_memory[session_id] = conversation_history

        # Determine if PTC was used (FOLLOWER mode with zero/near-zero cost)
        ptc_used = mode_used == "FOLLOWER" and cost < 0.01
        tokens_saved = result.get("tokens_saved", 0)

        # Update sentience state based on task outcome
        if cognitive_kernel:
            try:
                success = not result.get("error", False)
                cognitive_kernel.on_task_complete(
                    success=success,
                    cost=cost,
                    mode=mode_used,
                    goal=user_message[:100]  # Truncate for tracking
                )

                # Check if this is a novel task (triggers curiosity)
                if mode_used == "LEARNER":
                    cognitive_kernel.on_novel_task(user_message[:100])

                # Log latent mode for debugging
                state = sentience_manager.get_state()
                logger.info(f"[Sentience] Latent mode: {state.latent_mode.value}, "
                           f"Safety: {state.valence.safety:.2f}, "
                           f"Curiosity: {state.valence.curiosity:.2f}")
            except Exception as e:
                logger.warning(f"Sentience tracking error: {e}")

        # Log interesting stats
        if ptc_used:
            logger.info("✨ PTC activated - Tool sequence replayed outside context (90%+ savings!)")
        elif cached:
            logger.info("✨ FOLLOWER mode activated - Request served from cache")
        else:
            logger.info(f"💰 Request cost: ${cost:.4f}")

        # Get sentience state for response metadata
        sentience_metadata = {}
        if sentience_manager:
            state = sentience_manager.get_state()
            sentience_metadata = {
                "latent_mode": state.latent_mode.value,
                "valence": {
                    "safety": round(state.valence.safety, 3),
                    "curiosity": round(state.valence.curiosity, 3),
                    "energy": round(state.valence.energy, 3),
                    "self_confidence": round(state.valence.self_confidence, 3)
                },
                "homeostatic_cost": round(state.valence.homeostatic_cost(), 4)
            }

        # Return response in Maestro-compatible format for frontend
        # The frontend expects either:
        # - {response: "{final_prompt: ...}"} for Maestro
        # - {output: "..."} for simple responses
        response_json = {
            "final_prompt": response_text,
            "agent": intent["agent"],
            "mode": mode_used,
            "cost": cost,
            "cached": cached,
            # v3.3.0 Execution Layer metadata
            "ptc_used": ptc_used,
            "tokens_saved": tokens_saved,
            "execution_layer": {
                "ptc_enabled": Config.LLMOS_ENABLE_PTC,
                "tool_search_enabled": Config.LLMOS_ENABLE_TOOL_SEARCH,
                "tool_examples_enabled": Config.LLMOS_ENABLE_TOOL_EXAMPLES
            },
            # v3.4.0 Sentience Layer metadata
            "sentience": sentience_metadata
        }

        return {
            "response": json.dumps(response_json),
            "output": response_text,
            # Also include metadata at top level for easy access
            "metadata": {
                "agent": intent["agent"],
                "mode": mode_used,
                "cost": cost,
                "cached": cached,
                "ptc_used": ptc_used,
                "tokens_saved": tokens_saved,
                # v3.4.0 Sentience metadata
                "sentience": sentience_metadata
            }
        }

    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/stream")
async def chat_stream_endpoint(request: Request):
    """
    Streaming chat endpoint - returns Server-Sent Events (SSE).

    This is the drop-in replacement for the streaming endpoint used by the frontend.

    Response format (SSE):
    data: {"step_name": "llm_step", "step_result": "..."}
    data: [DONE]
    """
    if not os_instance:
        raise HTTPException(status_code=503, detail="LLM OS not initialized")

    try:
        data = await request.json()
        session_id = data.get("session_id", "default")
        user_message = extract_user_message(data)

        if not user_message:
            raise HTTPException(status_code=400, detail="No message provided")

        # Get or create session history
        if session_id not in session_memory:
            session_memory[session_id] = []

        conversation_history = session_memory[session_id]
        intent = analyze_intent(user_message, conversation_history)

        # Build enhanced prompt
        if conversation_history:
            context = "\n".join([
                f"{msg['role']}: {msg['content']}"
                for msg in conversation_history[-5:]
            ])
            enhanced_prompt = f"""Previous conversation:
{context}

Current request: {user_message}"""
        else:
            enhanced_prompt = user_message

        logger.info(f"Processing streaming chat request: {user_message[:100]}...")

        async def generate_stream() -> AsyncGenerator[str, None]:
            """Generate SSE stream."""
            try:
                # Execute through LLM OS
                result = await os_instance.execute(
                    goal=enhanced_prompt,
                    mode=intent["mode"],
                    max_cost_usd=2.0
                )

                response_text = result.get("output", "")

                # Update session memory
                conversation_history.append({"role": "user", "content": user_message})
                conversation_history.append({"role": "assistant", "content": response_text})
                session_memory[session_id] = conversation_history

                # Send the result as SSE in the format expected by frontend
                sse_data = {
                    "step_name": "llm_step",
                    "step_result": response_text
                }
                yield f"data: {json.dumps(sse_data)}\n\n"

                # Send done marker
                yield "data: [DONE]\n\n"

            except Exception as e:
                logger.error(f"Error in stream generation: {str(e)}", exc_info=True)
                error_data = {
                    "step_name": "error",
                    "step_result": str(e)
                }
                yield f"data: {json.dumps(error_data)}\n\n"
                yield "data: [DONE]\n\n"

        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )

    except Exception as e:
        logger.error(f"Error in streaming chat endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/run")
async def run_endpoint(request: Request):
    """
    Direct code execution endpoint.

    This is the drop-in replacement for the original coderun-agent.

    Instead of a separate microservice, we use the LLM OS Somatic Layer
    (execute_qiskit_code tool) with built-in security hooks.

    Request format:
    {
        "input_value": "python code here",
        "ibm_token": "optional-ibm-quantum-token",
        "channel": "ibm_quantum",
        "instance": "optional-crn",
        "region": "optional-region"
    }

    Response format:
    {
        "output": "execution output here"
    }
    """
    if not os_instance:
        raise HTTPException(status_code=503, detail="LLM OS not initialized")

    try:
        data = await request.json()
        code = data.get("input_value", "")

        if not code:
            raise HTTPException(status_code=400, detail="No code provided")

        # Extract IBM Quantum config (optional)
        ibm_token = data.get("ibm_token")
        channel = data.get("channel", "ibm_quantum")
        instance = data.get("instance")
        region = data.get("region")

        logger.info(f"Executing Qiskit code ({len(code)} chars)...")

        # Execute using the Somatic Layer tool
        # This goes through LLM OS security hooks automatically
        use_simulator = not bool(ibm_token)  # Use simulator if no token

        output = await execute_qiskit_code(
            code=code,
            use_simulator=use_simulator,
            ibm_token=ibm_token,
            channel=channel,
            instance=instance,
            region=region
        )

        logger.info("Code execution completed successfully")

        return JSONResponse({"output": output})

    except Exception as e:
        logger.error(f"Error in run endpoint: {str(e)}", exc_info=True)
        error_output = f"Error executing code: {str(e)}"
        return JSONResponse({"output": error_output})


@app.get("/stats")
async def stats_endpoint():
    """
    Statistics endpoint - shows LLM OS performance metrics.

    This endpoint showcases LLM OS v3.4.0 capabilities including:
    - Execution Layer (PTC, Tool Search, Tool Examples) statistics
    - Sentience Layer (valence, latent mode, homeostatic cost) statistics
    """
    if not os_instance:
        raise HTTPException(status_code=503, detail="LLM OS not initialized")

    # Get memory statistics
    mem_stats = os_instance.memory_query.get_memory_statistics()

    # Get token economy stats
    total_spent = sum(log["cost"] for log in os_instance.token_economy.spend_log)
    balance = os_instance.token_economy.balance

    # Get Execution Layer stats if available
    execution_layer_stats = {}
    if hasattr(os_instance, 'dispatcher') and os_instance.dispatcher:
        if hasattr(os_instance.dispatcher, 'get_execution_layer_stats'):
            execution_layer_stats = os_instance.dispatcher.get_execution_layer_stats()

    # Get Sentience Layer stats
    sentience_stats = {"enabled": False}
    if sentience_manager:
        state = sentience_manager.get_state()
        policy = cognitive_kernel.derive_policy() if cognitive_kernel else None

        sentience_stats = {
            "enabled": True,
            "latent_mode": state.latent_mode.value,
            "valence": {
                "safety": round(state.valence.safety, 3),
                "curiosity": round(state.valence.curiosity, 3),
                "energy": round(state.valence.energy, 3),
                "self_confidence": round(state.valence.self_confidence, 3)
            },
            "setpoints": {
                "safety": round(state.valence.safety_setpoint, 3),
                "curiosity": round(state.valence.curiosity_setpoint, 3),
                "energy": round(state.valence.energy_setpoint, 3),
                "self_confidence": round(state.valence.self_confidence_setpoint, 3)
            },
            "homeostatic_cost": round(state.valence.homeostatic_cost(), 4),
            "last_trigger": state.last_trigger.value if state.last_trigger else None,
            "last_trigger_reason": state.last_trigger_reason,
            "policy": {
                "prefer_cheap_modes": policy.prefer_cheap_modes if policy else False,
                "prefer_safe_modes": policy.prefer_safe_modes if policy else False,
                "allow_exploration": policy.allow_exploration if policy else True,
                "enable_auto_improvement": policy.enable_auto_improvement if policy else False
            } if policy else {}
        }

        # Check for self-improvement opportunities
        if cognitive_kernel:
            suggestions = cognitive_kernel.detect_improvement_opportunities()
            if suggestions:
                sentience_stats["improvement_suggestions"] = [
                    {"type": s.type.value, "description": s.description, "priority": s.priority}
                    for s in suggestions[:3]  # Top 3 suggestions
                ]

    return {
        "version": "3.4.0",
        "token_economy": {
            "budget_usd": Config.LLMOS_BUDGET_USD,
            "spent_usd": total_spent,
            "remaining_usd": balance,
            "transactions": len(os_instance.token_economy.spend_log)
        },
        "memory": {
            "total_traces": mem_stats.get("total_traces", 0),
            "high_confidence_traces": mem_stats.get("high_confidence_count", 0),
            "facts": mem_stats.get("facts_count", 0),
            "traces_with_tool_calls": mem_stats.get("traces_with_tool_calls", 0)  # For PTC
        },
        "agents": {
            "registered": len(os_instance.component_registry.list_agents()),
            "available": [
                agent["name"]
                for agent in os_instance.component_registry.list_agents()
            ]
        },
        "sessions": {
            "active": len(session_memory),
            "total_messages": sum(len(history) for history in session_memory.values())
        },
        # New v3.3.0 Execution Layer statistics
        "execution_layer": {
            "enabled": Config.LLMOS_ENABLE_PTC or Config.LLMOS_ENABLE_TOOL_SEARCH,
            "ptc": {
                "enabled": Config.LLMOS_ENABLE_PTC,
                "active_containers": execution_layer_stats.get("ptc_active_containers", 0),
                "total_executions": execution_layer_stats.get("ptc_total_executions", 0),
                "tokens_saved": execution_layer_stats.get("ptc_tokens_saved", 0)
            },
            "tool_search": {
                "enabled": Config.LLMOS_ENABLE_TOOL_SEARCH,
                "use_embeddings": Config.LLMOS_USE_EMBEDDINGS,
                "registered_tools": execution_layer_stats.get("tool_search_registered", 0),
                "total_searches": execution_layer_stats.get("tool_search_total", 0)
            },
            "tool_examples": {
                "enabled": Config.LLMOS_ENABLE_TOOL_EXAMPLES,
                "generated_examples": execution_layer_stats.get("tool_examples_generated", 0)
            }
        },
        # Mode distribution
        "mode_distribution": {
            "crystallized": execution_layer_stats.get("mode_crystallized", 0),
            "follower": execution_layer_stats.get("mode_follower", 0),
            "mixed": execution_layer_stats.get("mode_mixed", 0),
            "learner": execution_layer_stats.get("mode_learner", 0),
            "orchestrator": execution_layer_stats.get("mode_orchestrator", 0)
        },
        # v3.4.0 Sentience Layer statistics
        "sentience": sentience_stats
    }


@app.get("/sentience")
async def sentience_endpoint():
    """
    Sentience Layer endpoint - view and understand internal state.

    NEW in v3.4.0: This endpoint provides detailed access to the
    Sentience Layer state including valence, latent mode, and
    behavioral policy.
    """
    if not sentience_manager:
        return {
            "enabled": False,
            "message": "Sentience Layer is not enabled"
        }

    state = sentience_manager.get_state()
    policy = cognitive_kernel.derive_policy() if cognitive_kernel else None

    response = {
        "enabled": True,
        "latent_mode": {
            "current": state.latent_mode.value,
            "description": _get_latent_mode_description(state.latent_mode.value)
        },
        "valence": {
            "safety": {
                "value": round(state.valence.safety, 3),
                "setpoint": round(state.valence.safety_setpoint, 3),
                "deviation": round(state.valence.safety - state.valence.safety_setpoint, 3)
            },
            "curiosity": {
                "value": round(state.valence.curiosity, 3),
                "setpoint": round(state.valence.curiosity_setpoint, 3),
                "deviation": round(state.valence.curiosity - state.valence.curiosity_setpoint, 3)
            },
            "energy": {
                "value": round(state.valence.energy, 3),
                "setpoint": round(state.valence.energy_setpoint, 3),
                "deviation": round(state.valence.energy - state.valence.energy_setpoint, 3)
            },
            "self_confidence": {
                "value": round(state.valence.self_confidence, 3),
                "setpoint": round(state.valence.self_confidence_setpoint, 3),
                "deviation": round(state.valence.self_confidence - state.valence.self_confidence_setpoint, 3)
            }
        },
        "homeostatic_cost": round(state.valence.homeostatic_cost(), 4),
        "last_trigger": {
            "type": state.last_trigger.value if state.last_trigger else None,
            "reason": state.last_trigger_reason
        },
        "behavioral_guidance": state.to_behavioral_guidance(),
        "policy": {
            "prefer_cheap_modes": policy.prefer_cheap_modes if policy else False,
            "prefer_safe_modes": policy.prefer_safe_modes if policy else False,
            "allow_exploration": policy.allow_exploration if policy else True,
            "exploration_budget_multiplier": policy.exploration_budget_multiplier if policy else 1.0,
            "enable_auto_improvement": policy.enable_auto_improvement if policy else False
        } if policy else {}
    }

    # Add self-improvement suggestions if available
    if cognitive_kernel:
        suggestions = cognitive_kernel.detect_improvement_opportunities()
        if suggestions:
            response["improvement_suggestions"] = [
                {
                    "type": s.type.value,
                    "description": s.description,
                    "priority": s.priority,
                    "trigger_reason": s.trigger_reason
                }
                for s in suggestions
            ]

    return response


def _get_latent_mode_description(mode: str) -> str:
    """Get human-readable description for latent mode."""
    descriptions = {
        "auto_creative": "High curiosity and confidence - exploring new approaches and solutions",
        "auto_contained": "Low curiosity - focused on efficient task completion",
        "balanced": "Normal operating state - balanced between exploration and efficiency",
        "recovery": "Low energy or safety - preferring cheap, safe modes",
        "cautious": "Low safety - requiring extra verification and confirmation"
    }
    return descriptions.get(mode, "Unknown mode")


@app.post("/clear_session")
async def clear_session_endpoint(request: Request):
    """
    Clear a chat session's history.

    Request format:
    {
        "session_id": "session-id-to-clear"
    }
    """
    data = await request.json()
    session_id = data.get("session_id", "default")

    if session_id in session_memory:
        del session_memory[session_id]
        logger.info(f"Cleared session: {session_id}")

    return {"status": "ok", "session_id": session_id}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Run Qiskit Studio Backend powered by LLM OS"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to run the server on (default: 8000)"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )

    args = parser.parse_args()

    logger.info(f"Starting server on {args.host}:{args.port}")

    uvicorn.run(
        "server:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )
