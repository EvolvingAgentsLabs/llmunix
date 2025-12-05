"""
Data models for the Cron Terminal.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime


class CronState(Enum):
    """State of a cron process"""
    IDLE = "idle"
    THINKING = "thinking"
    ANALYZING = "analyzing"
    PROPOSING = "proposing"
    ERROR = "error"
    STOPPED = "stopped"


class SuggestionType(Enum):
    """Types of suggestions a cron can make"""
    IMMEDIATE = "immediate"         # What to do right now
    RECOMMENDATION = "recommendation"  # General advice
    PREDICTION = "prediction"       # Predicted next steps
    CREATIVE = "creative"           # Novel approaches


@dataclass
class CronTreeNode:
    """A node in the cron hierarchy tree"""
    cron_id: str
    cron_type: str  # "system", "team", "user"
    owner_id: str
    display_name: str
    state: CronState
    last_activity: Optional[str] = None
    pending_notifications: int = 0
    current_task: Optional[str] = None
    children: List["CronTreeNode"] = field(default_factory=list)
    is_current_user: bool = False  # [YOU] marker

    def as_dict(self) -> Dict[str, Any]:
        return {
            "cron_id": self.cron_id,
            "cron_type": self.cron_type,
            "owner_id": self.owner_id,
            "display_name": self.display_name,
            "state": self.state.value,
            "last_activity": self.last_activity,
            "pending_notifications": self.pending_notifications,
            "current_task": self.current_task,
            "children": [c.as_dict() for c in self.children],
            "is_current_user": self.is_current_user
        }


@dataclass
class ThinkingProcess:
    """Current cognitive state of a cron"""
    current_action: str
    analyzed_items: List[str] = field(default_factory=list)
    found_patterns: List[Dict[str, Any]] = field(default_factory=list)
    considering: List[str] = field(default_factory=list)
    cross_references: List[str] = field(default_factory=list)

    def format(self) -> str:
        """Format for display"""
        lines = [f"💭 {self.current_action}"]

        if self.found_patterns:
            lines.append("")
            lines.append("Found patterns:")
            for pattern in self.found_patterns:
                name = pattern.get("name", "Unknown")
                count = pattern.get("count", 0)
                lines.append(f"  • \"{name}\" - {count} traces")

        if self.considering:
            lines.append("")
            lines.append("Considering:")
            for item in self.considering:
                lines.append(f"  → {item}")

        if self.cross_references:
            lines.append("")
            lines.append("Cross-referencing:")
            for ref in self.cross_references:
                lines.append(f"  🔗 {ref}")

        return "\n".join(lines)


@dataclass
class Suggestion:
    """A suggestion from a cron"""
    suggestion_type: SuggestionType
    title: str
    description: str
    confidence: float = 0.0
    source: Optional[str] = None  # Where this suggestion came from
    action_id: Optional[str] = None  # ID for executing this suggestion

    def format(self) -> str:
        """Format for display"""
        icons = {
            SuggestionType.IMMEDIATE: "🎯 IMMEDIATE",
            SuggestionType.RECOMMENDATION: "💡 RECOMMENDATION",
            SuggestionType.PREDICTION: "🔮 PREDICTION",
            SuggestionType.CREATIVE: "🎨 CREATIVE APPROACH"
        }

        lines = [icons.get(self.suggestion_type, "📝")]
        lines.append(f"   {self.title}")

        if self.confidence > 0:
            lines.append(f"   Confidence: {self.confidence:.0%}")

        if self.source:
            lines.append(f"   \"{self.source}\"")

        return "\n".join(lines)


@dataclass
class ActivityEntry:
    """An entry in the activity log"""
    timestamp: str
    icon: str
    message: str
    event_id: Optional[str] = None

    def format(self) -> str:
        """Format for display"""
        time_part = self.timestamp.split("T")[1][:8] if "T" in self.timestamp else self.timestamp
        return f"[{time_part}] {self.icon} {self.message}"


@dataclass
class CronDetailView:
    """Complete detail view for a cron"""
    cron_id: str
    cron_type: str
    display_name: str
    is_interactive: bool  # Can the user interact with this cron?

    thinking: Optional[ThinkingProcess] = None
    suggestions: List[Suggestion] = field(default_factory=list)
    activity_log: List[ActivityEntry] = field(default_factory=list)

    # For interactive mode
    chat_history: List[Dict[str, str]] = field(default_factory=list)


@dataclass
class TerminalState:
    """State of the terminal UI"""
    current_user_id: str
    current_team_id: Optional[str]

    # Tree state
    tree_root: Optional[CronTreeNode] = None
    selected_cron_id: Optional[str] = None
    expanded_nodes: List[str] = field(default_factory=list)

    # Detail state
    detail_view: Optional[CronDetailView] = None

    # UI state
    active_panel: str = "tree"  # "tree" or "detail"
    scroll_position: int = 0

    # Refresh
    last_refresh: Optional[str] = None
    auto_refresh: bool = True
    refresh_interval: float = 5.0  # seconds
