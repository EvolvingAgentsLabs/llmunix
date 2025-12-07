"""
Cron Terminal - Interactive Dashboard for LLM OS

This module provides a two-panel terminal interface for monitoring
and interacting with Sentience Crons.

Features:
- Left Panel: Tree view of all cron processes with live status
- Right Panel: Detailed view of selected cron
- Interactive Mode: Chat with YOUR UserCron
- Read-Only Mode: View other crons' activity

Two UI Modes:
- Legacy: Basic ANSI terminal (no dependencies)
- Textual: Midnight Commander-style TUI (requires textual)

Usage:
    # Textual UI (recommended)
    python llmos/boot.py terminal --user alice --team engineering --ui textual

    # Legacy UI
    python llmos/boot.py terminal --user alice --team engineering --ui legacy
"""

# Legacy UI components
from .ui import CronTerminal, TerminalConfig, start_terminal
from .tree import CronTreeView
from .detail import CronDetailPanel
from .interaction import CronInteraction
from .input_handler import InputHandler, Key
from .llmos_data_provider import LLMOSDataProvider

# Textual UI (with lazy import for optional dependency)
def get_textual_app():
    """Get the Textual app class (lazy import)."""
    try:
        from .app import CronTerminalApp, run_terminal
        return CronTerminalApp, run_terminal
    except ImportError:
        raise ImportError(
            "Textual UI requires the 'textual' package. "
            "Install it with: pip install textual"
        )

__all__ = [
    # Legacy UI
    "CronTerminal",
    "TerminalConfig",
    "CronTreeView",
    "CronDetailPanel",
    "CronInteraction",
    "InputHandler",
    "Key",
    "LLMOSDataProvider",
    "start_terminal",
    # Textual UI
    "get_textual_app",
]
