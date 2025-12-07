"""
ActivityLogWidget - Widget for displaying cron activity history.

Shows a scrollable log of recent events with timestamps and icons.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime

from textual.widgets import RichLog
from textual.message import Message
from rich.text import Text

from ..models import ActivityEntry


class ActivityLogWidget(RichLog):
    """
    Widget for displaying activity log entries.

    Features:
    - Auto-scrolling to new entries
    - Color-coded event types
    - Clickable event IDs (for future expansion)
    - Timestamp formatting
    """

    DEFAULT_CSS = """
    ActivityLogWidget {
        height: 100%;
        border: solid $primary-darken-1;
        padding: 0 1;
    }
    """

    class EventClicked(Message):
        """Message sent when an event entry is clicked."""
        def __init__(self, event_id: str) -> None:
            self.event_id = event_id
            super().__init__()

    # Event type to icon/color mapping
    EVENT_STYLES = {
        "cron_started": (">>", "green"),
        "cron_stopped": ("[]", "red"),
        "cron_cycle_end": ("OK", "green"),
        "artifact_created": ("++", "cyan"),
        "artifact_evolved": ("**", "yellow"),
        "artifact_promoted": ("^^", "green bold"),
        "artifact_deleted": ("--", "red"),
        "proposal_created": ("??", "blue"),
        "insight_generated": ("!!", "yellow"),
        "suggestion_created": ("->", "cyan"),
        "system_alert": ("!!", "red bold"),
    }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, highlight=True, markup=True, **kwargs)
        self._entries: List[ActivityEntry] = []

    def add_entry(self, entry: ActivityEntry) -> None:
        """
        Add a single log entry.

        Args:
            entry: ActivityEntry to add
        """
        self._entries.append(entry)
        self._write_entry(entry)

    def add_entries(self, entries: List[ActivityEntry]) -> None:
        """
        Add multiple log entries.

        Args:
            entries: List of ActivityEntry objects
        """
        for entry in entries:
            self._entries.append(entry)
            self._write_entry(entry)

    def _write_entry(self, entry: ActivityEntry) -> None:
        """Write a single entry to the log."""
        # Format timestamp
        try:
            if "T" in entry.timestamp:
                dt = datetime.fromisoformat(entry.timestamp.replace("Z", "+00:00"))
                time_str = dt.strftime("%H:%M:%S")
            else:
                time_str = entry.timestamp
        except (ValueError, AttributeError):
            time_str = "??:??:??"

        # Get style for event type
        event_type = getattr(entry, "event_type", "") or ""
        icon, color = self.EVENT_STYLES.get(
            event_type.lower(),
            (entry.icon or "**", "white")
        )

        # Build rich text
        text = Text()
        text.append(f"[{time_str}] ", style="dim")
        text.append(f"[{icon}] ", style=color)
        text.append(entry.message)

        if entry.event_id:
            text.append(f" ({entry.event_id[:8]})", style="dim italic")

        self.write(text)

    def clear_log(self) -> None:
        """Clear all entries."""
        self._entries.clear()
        self.clear()

    def load_from_events(self, events: List[Dict[str, Any]]) -> None:
        """
        Load entries from event dictionaries.

        Args:
            events: List of event dicts with timestamp, title, event_type, event_id
        """
        self.clear_log()

        entries = []
        for event in events:
            entry = ActivityEntry(
                timestamp=event.get("timestamp", ""),
                icon=self._get_event_icon(event.get("event_type", "")),
                message=event.get("title", event.get("message", "")),
                event_id=event.get("event_id"),
            )
            # Store event_type for styling
            entry.event_type = event.get("event_type", "")
            entries.append(entry)

        self.add_entries(entries)

    def _get_event_icon(self, event_type: str) -> str:
        """Get icon for event type."""
        icons = {
            "cron_started": ">>",
            "cron_stopped": "[]",
            "cron_cycle_end": "OK",
            "artifact_created": "++",
            "artifact_evolved": "**",
            "artifact_promoted": "^^",
            "artifact_deleted": "--",
            "proposal_created": "??",
            "insight_generated": "!!",
            "suggestion_created": "->",
            "system_alert": "!!",
        }
        return icons.get(event_type.lower(), "**")

    @classmethod
    def from_events(cls, events: List[Dict[str, Any]]) -> "ActivityLogWidget":
        """
        Create an ActivityLogWidget from a list of events.

        Args:
            events: List of event dictionaries

        Returns:
            Configured ActivityLogWidget
        """
        widget = cls()
        widget.load_from_events(events)
        return widget
