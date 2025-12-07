"""
DetailTabs - Tabbed detail panel for the right side of the terminal.

Provides tabs for Info, Activity, Chat, and Config views.
"""

from typing import Optional, Dict, Any, List, Callable, Awaitable

from textual.widgets import TabbedContent, TabPane, Static, Label
from textual.containers import Vertical, ScrollableContainer
from textual.message import Message
from rich.text import Text
from rich.panel import Panel
from rich.table import Table

from .thinking_view import ThinkingView
from .activity_log import ActivityLogWidget
from .suggestion_list import SuggestionList
from .chat_panel import ChatPanel, ReadOnlyChatPanel
from ..models import CronDetailView, ThinkingProcess, Suggestion


class InfoTab(ScrollableContainer):
    """
    Info tab showing cron overview and current state.
    """

    DEFAULT_CSS = """
    InfoTab {
        height: 100%;
        padding: 1;
    }

    InfoTab .section-title {
        text-style: bold;
        margin-bottom: 1;
        color: $primary-lighten-2;
    }

    InfoTab .info-row {
        margin-bottom: 1;
    }
    """

    def __init__(self, cron_id: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.cron_id = cron_id
        self._cron_status: Dict[str, Any] = {}
        self._suggestions: List[Suggestion] = []

    def compose(self):
        """Compose the info tab."""
        yield ThinkingView(id="thinking-view")
        yield Static("", id="info-divider")
        yield Label("Suggested Actions", classes="section-title")
        yield SuggestionList(id="suggestion-list")

    def update_info(
        self,
        cron_status: Dict[str, Any],
        suggestions: List[Dict[str, Any]]
    ) -> None:
        """
        Update the info display.

        Args:
            cron_status: Current cron status dict
            suggestions: List of suggestion dicts
        """
        self._cron_status = cron_status

        # Update thinking view
        thinking_view = self.query_one("#thinking-view", ThinkingView)
        thinking_data = cron_status.get("current_thinking")
        if thinking_data:
            thinking = ThinkingProcess(
                current_action=thinking_data.get("action", "Processing..."),
                analyzed_items=thinking_data.get("analyzed", []),
                found_patterns=thinking_data.get("patterns", []),
                considering=thinking_data.get("considering", []),
                cross_references=thinking_data.get("cross_refs", []),
            )
            thinking_view.update_thinking(thinking, cron_status.get("status", "idle"))
        else:
            thinking_view.update_thinking(None)

        # Update suggestions
        suggestion_list = self.query_one("#suggestion-list", SuggestionList)
        parsed_suggestions = []
        for s in suggestions:
            stype = SuggestionList._parse_type(s.get("type", "recommendation"))
            parsed_suggestions.append(Suggestion(
                suggestion_type=stype,
                title=s.get("title", ""),
                description=s.get("description", ""),
                confidence=s.get("confidence", 0.0),
                source=s.get("source"),
                action_id=s.get("action_id"),
            ))
        suggestion_list.load_suggestions(parsed_suggestions)


class ActivityTab(Vertical):
    """Activity tab showing event log."""

    DEFAULT_CSS = """
    ActivityTab {
        height: 100%;
    }
    """

    def __init__(self, cron_id: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.cron_id = cron_id

    def compose(self):
        """Compose the activity tab."""
        yield ActivityLogWidget(id="activity-log")

    def update_activity(self, events: List[Dict[str, Any]]) -> None:
        """Update the activity log."""
        log = self.query_one("#activity-log", ActivityLogWidget)
        log.load_from_events(events)


class ChatTab(Vertical):
    """Chat tab for interactive communication."""

    DEFAULT_CSS = """
    ChatTab {
        height: 100%;
    }
    """

    def __init__(
        self,
        cron_id: str,
        is_interactive: bool,
        owner_name: str,
        send_callback: Optional[Callable[[str, str], Awaitable[str]]] = None,
        *args,
        **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.cron_id = cron_id
        self.is_interactive = is_interactive
        self.owner_name = owner_name
        self.send_callback = send_callback

    def compose(self):
        """Compose the chat tab."""
        if self.is_interactive:
            yield ChatPanel(
                cron_id=self.cron_id,
                is_interactive=True,
                send_callback=self.send_callback,
                id="chat-panel"
            )
        else:
            yield ReadOnlyChatPanel(
                cron_id=self.cron_id,
                owner_name=self.owner_name,
                id="readonly-chat"
            )


class ConfigTab(ScrollableContainer):
    """Configuration tab showing cron settings."""

    DEFAULT_CSS = """
    ConfigTab {
        height: 100%;
        padding: 1;
    }
    """

    def __init__(self, cron_id: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.cron_id = cron_id

    def compose(self):
        """Compose the config tab."""
        # Basic config display - can be expanded
        yield Static(self._render_config())

    def _render_config(self) -> Panel:
        """Render configuration panel."""
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Key", style="bold cyan")
        table.add_column("Value")

        table.add_row("Cron ID", self.cron_id)
        table.add_row("Auto-refresh", "Enabled")
        table.add_row("Refresh interval", "5.0s")
        table.add_row("Notifications", "Enabled")

        return Panel(
            table,
            title="[bold]Configuration[/bold]",
            border_style="blue",
        )


class DetailTabs(Vertical):
    """
    Main tabbed container for the detail panel.

    Tabs:
    - Info: Thinking state and suggestions
    - Activity: Event log
    - Chat: Interactive chat (if allowed)
    - Config: Settings
    """

    DEFAULT_CSS = """
    DetailTabs {
        height: 100%;
    }
    """

    def __init__(
        self,
        cron_id: str,
        current_user_id: str,
        send_callback: Optional[Callable[[str, str], Awaitable[str]]] = None,
        *args,
        **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.cron_id = cron_id
        self.current_user_id = current_user_id
        self.send_callback = send_callback

        # Determine if interactive
        self.is_interactive = self._check_interactive()
        self.owner_name = self._get_owner_name()

    def _check_interactive(self) -> bool:
        """Check if current user can interact with this cron."""
        if ":" not in self.cron_id:
            return False
        cron_type, owner_id = self.cron_id.split(":", 1)
        return cron_type == "user" and owner_id == self.current_user_id

    def _get_owner_name(self) -> str:
        """Get the owner name from cron_id."""
        if ":" in self.cron_id:
            return self.cron_id.split(":", 1)[1]
        return "System"

    def compose(self):
        """Compose all tabs using TabbedContent properly."""
        with TabbedContent(id="detail-tabbed-content"):
            with TabPane("Info", id="tab-info"):
                yield InfoTab(self.cron_id, id="info-content")

            with TabPane("Activity", id="tab-activity"):
                yield ActivityTab(self.cron_id, id="activity-content")

            with TabPane("Chat", id="tab-chat"):
                yield ChatTab(
                    cron_id=self.cron_id,
                    is_interactive=self.is_interactive,
                    owner_name=self.owner_name,
                    send_callback=self.send_callback,
                    id="chat-content"
                )

            with TabPane("Config", id="tab-config"):
                yield ConfigTab(self.cron_id, id="config-content")

    def update_for_cron(
        self,
        cron_id: str,
        cron_status: Dict[str, Any],
        events: List[Dict[str, Any]],
        suggestions: List[Dict[str, Any]]
    ) -> None:
        """
        Update all tabs for a new cron selection.

        Args:
            cron_id: Selected cron ID
            cron_status: Cron status dict
            events: Activity events
            suggestions: Suggestions list
        """
        self.cron_id = cron_id
        self.is_interactive = self._check_interactive()
        self.owner_name = self._get_owner_name()

        # Update info tab
        try:
            info_tab = self.query_one("#info-content", InfoTab)
            info_tab.update_info(cron_status, suggestions)
        except Exception:
            pass

        # Update activity tab
        try:
            activity_tab = self.query_one("#activity-content", ActivityTab)
            activity_tab.update_activity(events)
        except Exception:
            pass
