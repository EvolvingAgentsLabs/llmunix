"""
Configuration module for Qiskit Studio Backend

Loads environment variables and provides configuration settings.
Integrates with LLM OS v3.4.0 features including:
- Advanced Tool Use (PTC, Tool Search, Tool Examples)
- Sentience Layer (valence, homeostatic dynamics, cognitive kernel)
"""

import os
import sys
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    load_dotenv(env_file)

# Add llmos to path for imports
LLMOS_ROOT = Path(__file__).parents[2]
if (LLMOS_ROOT / "llmos").exists():
    sys.path.insert(0, str(LLMOS_ROOT))


class Config:
    """Configuration settings for Qiskit Studio Backend"""

    # Anthropic API
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")

    # IBM Quantum (optional)
    IBM_QUANTUM_TOKEN: Optional[str] = os.getenv("IBM_QUANTUM_TOKEN")
    IBM_QUANTUM_CHANNEL: str = os.getenv("IBM_QUANTUM_CHANNEL", "ibm_quantum")
    IBM_QUANTUM_INSTANCE: Optional[str] = os.getenv("IBM_QUANTUM_INSTANCE")
    IBM_QUANTUM_REGION: Optional[str] = os.getenv("IBM_QUANTUM_REGION")

    # Server settings
    SERVER_HOST: str = os.getenv("SERVER_HOST", "0.0.0.0")
    SERVER_PORT: int = int(os.getenv("SERVER_PORT", "8000"))

    # LLM OS settings
    LLMOS_BUDGET_USD: float = float(os.getenv("LLMOS_BUDGET_USD", "50.0"))
    LLMOS_PROJECT_NAME: str = os.getenv("LLMOS_PROJECT_NAME", "qiskit_studio_session")

    # LLM OS Execution Layer settings (v3.3.0)
    LLMOS_ENABLE_PTC: bool = os.getenv("LLMOS_ENABLE_PTC", "true").lower() == "true"
    LLMOS_ENABLE_TOOL_SEARCH: bool = os.getenv("LLMOS_ENABLE_TOOL_SEARCH", "true").lower() == "true"
    LLMOS_ENABLE_TOOL_EXAMPLES: bool = os.getenv("LLMOS_ENABLE_TOOL_EXAMPLES", "true").lower() == "true"
    LLMOS_USE_EMBEDDINGS: bool = os.getenv("LLMOS_USE_EMBEDDINGS", "false").lower() == "true"

    # LLM OS Sentience Layer settings (v3.4.0)
    LLMOS_ENABLE_SENTIENCE: bool = os.getenv("LLMOS_ENABLE_SENTIENCE", "true").lower() == "true"
    LLMOS_INJECT_INTERNAL_STATE: bool = os.getenv("LLMOS_INJECT_INTERNAL_STATE", "true").lower() == "true"
    LLMOS_ENABLE_AUTO_IMPROVEMENT: bool = os.getenv("LLMOS_ENABLE_AUTO_IMPROVEMENT", "true").lower() == "true"

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        if not cls.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is required. Please set it in .env file")
        return True

    @classmethod
    def get_llmos_config(cls):
        """
        Build LLMOSConfig with Execution Layer and Sentience Layer settings.

        Returns an LLMOSConfig instance configured for Qiskit Studio with:
        - Advanced Tool Use features (PTC, Tool Search, Tool Examples)
        - Sentience Layer (valence, homeostatic dynamics, cognitive kernel)
        """
        from kernel.config import (
            LLMOSConfig,
            KernelConfig,
            MemoryConfig,
            SDKConfig,
            DispatcherConfig,
            ExecutionLayerConfig,
            SentienceConfig
        )

        workspace = Path(__file__).parent / "workspace"

        return LLMOSConfig(
            workspace=workspace,
            kernel=KernelConfig(
                budget_usd=cls.LLMOS_BUDGET_USD,
                enable_scheduling=True,
                enable_watchdog=True
            ),
            memory=MemoryConfig(
                enable_llm_matching=True,
                trace_confidence_threshold=0.9,
                mixed_mode_threshold=0.75,
                follower_mode_threshold=0.92,
                enable_cross_project_learning=True
            ),
            sdk=SDKConfig(
                model="claude-sonnet-4-5-20250929",
                enable_streaming=False,  # Server uses its own streaming
                enable_hooks=True
            ),
            dispatcher=DispatcherConfig(
                complexity_threshold=2,
                auto_crystallization=True,  # Enable for quantum patterns
                crystallization_min_usage=3,  # Lower for demo purposes
                crystallization_min_success=0.9
            ),
            execution=ExecutionLayerConfig(
                # Enable Advanced Tool Use (beta)
                enable_advanced_tool_use=True,
                beta_header="advanced-tool-use-2025-11-20",

                # PTC (Programmatic Tool Calling) - for FOLLOWER mode
                enable_ptc=cls.LLMOS_ENABLE_PTC,
                ptc_container_timeout_secs=120.0,
                ptc_max_containers=5,

                # Tool Search - for discovering tools on-demand
                enable_tool_search=cls.LLMOS_ENABLE_TOOL_SEARCH,
                tool_search_use_embeddings=cls.LLMOS_USE_EMBEDDINGS,
                tool_search_top_k=5,
                defer_tools_by_default=True,

                # Tool Examples - auto-generated from traces
                enable_tool_examples=cls.LLMOS_ENABLE_TOOL_EXAMPLES,
                tool_examples_min_success_rate=0.9,
                tool_examples_max_per_tool=3
            ),
            sentience=SentienceConfig(
                # Enable Sentience Layer for adaptive behavior
                enable_sentience=cls.LLMOS_ENABLE_SENTIENCE,

                # Valence set-points tuned for quantum computing tasks
                # Higher safety for code execution, moderate curiosity for exploration
                safety_setpoint=0.6,  # Higher for code execution safety
                curiosity_setpoint=0.1,  # Moderate exploration for learning new algorithms
                energy_setpoint=0.7,
                self_confidence_setpoint=0.4,  # Higher confidence for specialized domain

                # Context injection - agents see their internal state
                inject_internal_state=cls.LLMOS_INJECT_INTERNAL_STATE,
                inject_behavioral_guidance=True,

                # Self-improvement for detecting repetitive patterns
                enable_auto_improvement=cls.LLMOS_ENABLE_AUTO_IMPROVEMENT,
                boredom_threshold=-0.3,  # Trigger improvement earlier for quantum tasks

                # Persistence across sessions
                auto_persist=True,
                state_file="state/qiskit_sentience.json"
            ),
            project_name=cls.LLMOS_PROJECT_NAME
        )


# Validate configuration on import
try:
    Config.validate()
except ValueError as e:
    print(f"Warning: Configuration issue: {e}")
    print("   Create a .env file from .env.template and add your API key")
