"""
Cron Terminal - Interactive Dashboard for LLM OS

This module provides a two-panel terminal interface for monitoring
and interacting with Sentience Crons.

Features:
- Left Panel: Tree view of all cron processes with live status
- Right Panel: Detailed view of selected cron
- Interactive Mode: Chat with YOUR UserCron
- Read-Only Mode: View other crons' activity

Usage:
    python llmos/boot.py terminal --user alice --team engineering
"""

from .ui import CronTerminal
from .tree import CronTreeView
from .detail import CronDetailPanel
from .interaction import CronInteraction

__all__ = [
    "CronTerminal",
    "CronTreeView",
    "CronDetailPanel",
    "CronInteraction"
]
