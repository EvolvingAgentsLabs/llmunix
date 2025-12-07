"""
CronTerminalApp - Main Textual application for the Cron Terminal.

Provides a Midnight Commander-style two-panel interface with
function keys, command palette, and live data updates.
"""

from typing import Optional, Dict, Any, List, Callable, Awaitable
from pathlib import Path
import asyncio

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, Static, Label
from textual.binding import Binding
from textual.timer import Timer
from textual.message import Message

from .widgets.cron_tree import CronTreeWidget
from .widgets.detail_tabs import DetailTabs
from .models import CronState


class CronTerminalApp(App):
    """
    Main Textual application for the Cron Terminal.

    Features:
    - Two-panel MC-style layout
    - Function key bindings (F1-F10)
    - Vim-style navigation
    - Command palette (Ctrl+P)
    - Auto-refresh with live updates
    - Color themes
    """

    # Load CSS from styles directory
    CSS_PATH = Path(__file__).parent / "styles" / "mc_blue.tcss"

    # Application title
    TITLE = "LLMOS Cron Terminal"
    SUB_TITLE = "Midnight Commander Style"

    # Function key bindings - MC style
    BINDINGS = [
        Binding("f1", "show_help", "Help", show=True),
        Binding("f2", "show_menu", "Menu", show=True),
        Binding("f3", "view_detail", "View", show=True),
        Binding("f4", "edit", "Edit", show=True),
        Binding("f5", "refresh", "Refresh", show=True),
        Binding("f6", "move", "Move", show=True),
        Binding("f7", "mkdir", "MkDir", show=True),
        Binding("f8", "delete", "Delete", show=True),
        Binding("f9", "pull_down", "PullDn", show=True),
        Binding("f10", "quit", "Quit", show=True, key_display="F10"),
        # Additional bindings
        Binding("ctrl+p", "command_palette", "Commands", show=False),
        Binding("ctrl+r", "refresh", "Refresh", show=False),
        Binding("tab", "switch_panel", "Switch Panel", show=False),
        Binding("q", "quit", "Quit", show=False),
        Binding("?", "show_help", "Help", show=False),
    ]

    # Commands for command palette
    COMMANDS = {
        "refresh": "Refresh all data",
        "quit": "Exit terminal",
        "help": "Show help",
        "theme": "Change theme",
        "toggle_auto_refresh": "Toggle auto-refresh",
    }

    class DataRefreshed(Message):
        """Message sent when data is refreshed."""
        pass

    def __init__(
        self,
        user_id: str,
        team_id: Optional[str] = None,
        status_callback: Optional[Callable[[], Awaitable[Dict[str, Any]]]] = None,
        events_callback: Optional[Callable[[str], Awaitable[List[Dict]]]] = None,
        suggestions_callback: Optional[Callable[[str], Awaitable[List[Dict]]]] = None,
        cron_callback: Optional[Callable[[str, str], Awaitable[str]]] = None,
        refresh_interval: float = 5.0,
        auto_refresh: bool = True,
    ) -> None:
        """
        Initialize the terminal app.

        Args:
            user_id: Current user's ID
            team_id: Current user's team ID
            status_callback: Async function to get system cron status
            events_callback: Async function to get events for a cron
            suggestions_callback: Async function to get suggestions for a cron
            cron_callback: Async function to send messages to cron
            refresh_interval: Seconds between auto-refresh
            auto_refresh: Enable auto-refresh
        """
        super().__init__()
        self.user_id = user_id
        self.team_id = team_id
        self.status_callback = status_callback
        self.events_callback = events_callback
        self.suggestions_callback = suggestions_callback
        self.cron_callback = cron_callback
        self.refresh_interval = refresh_interval
        self.auto_refresh_enabled = auto_refresh

        # State
        self.selected_cron_id: Optional[str] = None
        self.current_status: Dict[str, Any] = {}
        self._refresh_timer: Optional[Timer] = None
        self._active_panel: str = "tree"  # "tree" or "detail"

    def compose(self) -> ComposeResult:
        """Compose the app layout."""
        yield Header(show_clock=True)

        with Horizontal(id="main-container"):
            # Left panel - Cron Tree
            with Vertical(id="left-panel"):
                yield Label("CRON PROCESSES", id="left-panel-title")
                yield CronTreeWidget(
                    current_user_id=self.user_id,
                    current_team_id=self.team_id,
                    id="cron-tree"
                )

            # Right panel - Detail Tabs
            with Vertical(id="right-panel"):
                yield Label("DETAILS", id="right-panel-title")
                yield DetailTabs(
                    cron_id=f"user:{self.user_id}",
                    current_user_id=self.user_id,
                    send_callback=self.cron_callback,
                    id="detail-tabs"
                )

        yield Footer()

    async def on_mount(self) -> None:
        """Initialize on app mount."""
        # Initial data load
        await self.action_refresh()

        # Select user's cron by default
        user_cron_id = f"user:{self.user_id}"
        tree = self.query_one("#cron-tree", CronTreeWidget)
        tree.select_cron(user_cron_id)
        self.selected_cron_id = user_cron_id

        # Start auto-refresh timer
        if self.auto_refresh_enabled:
            self._refresh_timer = self.set_interval(
                self.refresh_interval,
                self._auto_refresh
            )

    async def _auto_refresh(self) -> None:
        """Auto-refresh callback."""
        if self.auto_refresh_enabled:
            await self.action_refresh()

    async def action_refresh(self) -> None:
        """Refresh all data."""
        # Get system status
        if self.status_callback:
            self.current_status = await self.status_callback()
        else:
            self.current_status = self._get_mock_status()

        # Update tree
        tree = self.query_one("#cron-tree", CronTreeWidget)
        tree.build_from_status(self.current_status)

        # Update detail if cron is selected
        if self.selected_cron_id:
            await self._update_detail(self.selected_cron_id)

        # Update title with refresh time
        self.sub_title = f"Last refresh: {self._get_time_str()}"
        self.post_message(self.DataRefreshed())

    async def _update_detail(self, cron_id: str) -> None:
        """Update the detail panel for selected cron."""
        # Get cron-specific status
        cron_status = self._extract_cron_status(cron_id)

        # Get events
        events = []
        if self.events_callback:
            try:
                events = await self.events_callback(cron_id)
            except Exception:
                pass

        # Get suggestions
        suggestions = []
        if self.suggestions_callback:
            try:
                suggestions = await self.suggestions_callback(cron_id)
            except Exception:
                pass

        # Update detail tabs
        try:
            detail_tabs = self.query_one("#detail-tabs", DetailTabs)
            detail_tabs.update_for_cron(cron_id, cron_status, events, suggestions)

            # Update panel title
            panel_title = self.query_one("#right-panel-title", Label)
            cron_type = cron_id.split(":")[0] if ":" in cron_id else "system"
            owner = cron_id.split(":")[1] if ":" in cron_id else "System"
            panel_title.update(f"DETAILS: {cron_type.upper()}:{owner}")
        except Exception:
            pass

    def _extract_cron_status(self, cron_id: str) -> Dict[str, Any]:
        """Extract status for a specific cron from system status."""
        if cron_id == "system":
            return self.current_status.get("system", {})

        if ":" in cron_id:
            cron_type, owner_id = cron_id.split(":", 1)

            if cron_type == "team":
                return self.current_status.get("teams", {}).get(owner_id, {})

            if cron_type == "user":
                for team_status in self.current_status.get("teams", {}).values():
                    users = team_status.get("users", {})
                    if owner_id in users:
                        return users[owner_id]

        return {}

    def on_cron_tree_widget_cron_selected(
        self,
        event: CronTreeWidget.CronSelected
    ) -> None:
        """Handle cron selection from tree."""
        self.selected_cron_id = event.cron_id
        asyncio.create_task(self._update_detail(event.cron_id))

    def action_switch_panel(self) -> None:
        """Switch focus between panels."""
        if self._active_panel == "tree":
            self._active_panel = "detail"
            try:
                tabs = self.query_one("#detail-tabs", DetailTabs)
                tabs.focus()
            except Exception:
                pass
        else:
            self._active_panel = "tree"
            try:
                tree = self.query_one("#cron-tree", CronTreeWidget)
                tree.focus()
            except Exception:
                pass

    def action_show_help(self) -> None:
        """Show help modal."""
        help_text = """
[bold]LLMOS Cron Terminal - Keyboard Shortcuts[/bold]

[cyan]Navigation:[/cyan]
  [bold]Tab[/bold]       Switch between panels
  [bold]j/k[/bold]       Move up/down in tree
  [bold]Enter[/bold]     Select cron
  [bold]Space[/bold]     Expand/collapse node

[cyan]Function Keys:[/cyan]
  [bold]F1[/bold]        This help
  [bold]F5[/bold]        Refresh data
  [bold]F10/q[/bold]     Quit

[cyan]Other:[/cyan]
  [bold]Ctrl+P[/bold]    Command palette
  [bold]Ctrl+R[/bold]    Refresh
        """
        self.notify(help_text, title="Help", timeout=10)

    def action_show_menu(self) -> None:
        """Show menu (placeholder)."""
        self.notify("Menu coming soon...", title="Menu")

    def action_view_detail(self) -> None:
        """Focus on detail panel."""
        self._active_panel = "detail"
        try:
            tabs = self.query_one("#detail-tabs", DetailTabs)
            tabs.focus()
        except Exception:
            pass

    def action_edit(self) -> None:
        """Edit action (placeholder)."""
        self.notify("Edit not available for crons", title="Edit")

    def action_move(self) -> None:
        """Move action (placeholder)."""
        self.notify("Move not available", title="Move")

    def action_mkdir(self) -> None:
        """Create action (placeholder)."""
        self.notify("Create cron via /cron command", title="Create")

    def action_delete(self) -> None:
        """Delete action (placeholder)."""
        self.notify("Delete not available", title="Delete")

    def action_pull_down(self) -> None:
        """Pull down menu (placeholder)."""
        self.notify("Pull-down menu coming soon...", title="Menu")

    def action_toggle_auto_refresh(self) -> None:
        """Toggle auto-refresh."""
        self.auto_refresh_enabled = not self.auto_refresh_enabled
        if self.auto_refresh_enabled and not self._refresh_timer:
            self._refresh_timer = self.set_interval(
                self.refresh_interval,
                self._auto_refresh
            )
        elif not self.auto_refresh_enabled and self._refresh_timer:
            self._refresh_timer.stop()
            self._refresh_timer = None

        status = "enabled" if self.auto_refresh_enabled else "disabled"
        self.notify(f"Auto-refresh {status}", title="Auto-refresh")

    def _get_time_str(self) -> str:
        """Get current time string."""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")

    def _get_mock_status(self) -> Dict[str, Any]:
        """Generate mock status for testing."""
        from datetime import datetime
        return {
            "system": {
                "status": "thinking",
                "last_run": datetime.now().isoformat(),
                "current_thinking": {
                    "action": "Analyzing cross-team patterns",
                    "patterns": [
                        {"name": "API optimization", "count": 12},
                        {"name": "Cache invalidation", "count": 8},
                    ],
                    "considering": ["Suggest team-wide caching strategy"],
                }
            },
            "teams": {
                self.team_id or "default": {
                    "status": "analyzing",
                    "last_run": datetime.now().isoformat(),
                    "pending_notifications": 3,
                    "users": {
                        self.user_id: {
                            "status": "idle",
                            "last_run": datetime.now().isoformat(),
                            "pending_notifications": 5,
                            "current_task": None,
                            "current_thinking": {
                                "action": "Reviewing your recent traces",
                                "analyzed": ["trace_001", "trace_002"],
                                "considering": ["Suggest caching pattern"],
                            }
                        },
                        "alice": {
                            "status": "thinking",
                            "last_run": datetime.now().isoformat(),
                            "current_task": "Optimizing database queries",
                        },
                        "bob": {
                            "status": "proposing",
                            "last_run": datetime.now().isoformat(),
                            "pending_notifications": 2,
                        }
                    }
                },
                "design": {
                    "status": "idle",
                    "users": {
                        "carol": {"status": "idle"},
                        "dan": {"status": "analyzing"},
                    }
                }
            }
        }


async def run_terminal(
    user_id: str,
    team_id: Optional[str] = None,
    status_callback: Optional[Callable[[], Awaitable[Dict[str, Any]]]] = None,
    events_callback: Optional[Callable[[str], Awaitable[List[Dict]]]] = None,
    suggestions_callback: Optional[Callable[[str], Awaitable[List[Dict]]]] = None,
    cron_callback: Optional[Callable[[str, str], Awaitable[str]]] = None,
    **kwargs
) -> None:
    """
    Run the Textual terminal app.

    Args:
        user_id: Current user's ID
        team_id: Current user's team ID
        status_callback: Async function to get system cron status
        events_callback: Async function to get events for a cron
        suggestions_callback: Async function to get suggestions for a cron
        cron_callback: Async function to send messages to cron
        **kwargs: Additional arguments for CronTerminalApp
    """
    app = CronTerminalApp(
        user_id=user_id,
        team_id=team_id,
        status_callback=status_callback,
        events_callback=events_callback,
        suggestions_callback=suggestions_callback,
        cron_callback=cron_callback,
        **kwargs
    )
    await app.run_async()


def main():
    """Entry point for running the terminal directly."""
    import sys

    user_id = sys.argv[1] if len(sys.argv) > 1 else "demo_user"
    team_id = sys.argv[2] if len(sys.argv) > 2 else "engineering"

    app = CronTerminalApp(
        user_id=user_id,
        team_id=team_id,
    )
    app.run()


if __name__ == "__main__":
    main()
