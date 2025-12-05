"""
Cron Terminal - Main UI Orchestration.

The terminal provides a two-panel interface for monitoring and interacting
with Sentience Crons. It combines the tree view, detail panel, and
interaction system into a cohesive dashboard.
"""

from typing import Dict, Any, Optional, List, Callable, Awaitable
from dataclasses import dataclass
import asyncio
from datetime import datetime

from .models import TerminalState, CronTreeNode, CronDetailView
from .tree import CronTreeView
from .detail import CronDetailPanel
from .interaction import CronInteraction


@dataclass
class TerminalConfig:
    """Configuration for the terminal UI"""
    width: int = 120
    height: int = 40
    tree_width: int = 40
    detail_width: int = 78
    refresh_interval: float = 5.0
    auto_refresh: bool = True


class CronTerminal:
    """
    Main terminal UI for the Cron system.

    Provides a two-panel dashboard:
    - Left: Tree view of all crons with live status
    - Right: Detail view of selected cron with interaction

    Usage:
        terminal = CronTerminal(
            user_id="alice",
            team_id="engineering",
            status_callback=get_system_status,
            events_callback=get_events,
            cron_callback=send_to_cron
        )
        await terminal.run()
    """

    def __init__(
        self,
        user_id: str,
        team_id: Optional[str] = None,
        status_callback: Optional[Callable[[], Awaitable[Dict[str, Any]]]] = None,
        events_callback: Optional[Callable[[str], Awaitable[List[Dict]]]] = None,
        suggestions_callback: Optional[Callable[[str], Awaitable[List[Dict]]]] = None,
        cron_callback: Optional[Callable[[str, str], Awaitable[str]]] = None,
        config: Optional[TerminalConfig] = None
    ):
        """
        Initialize the terminal.

        Args:
            user_id: Current user's ID
            team_id: Current user's team ID
            status_callback: Async function to get system cron status
            events_callback: Async function to get events for a cron
            suggestions_callback: Async function to get suggestions for a cron
            cron_callback: Async function to send messages to cron
            config: Terminal configuration
        """
        self.user_id = user_id
        self.team_id = team_id
        self.config = config or TerminalConfig()

        # Callbacks
        self.status_callback = status_callback
        self.events_callback = events_callback
        self.suggestions_callback = suggestions_callback

        # Components
        self.tree_view = CronTreeView(user_id, team_id)
        self.detail_panel = CronDetailPanel(user_id)
        self.interaction = CronInteraction(user_id, cron_callback)

        # State
        self.state = TerminalState(
            current_user_id=user_id,
            current_team_id=team_id
        )
        self.running = False
        self.tree_root: Optional[CronTreeNode] = None
        self.detail_view: Optional[CronDetailView] = None

    async def refresh(self) -> bool:
        """
        Refresh all data from callbacks.

        Returns:
            True if refresh successful
        """
        try:
            # Get system status
            if self.status_callback:
                status = await self.status_callback()
            else:
                status = self._get_mock_status()

            # Build tree
            self.tree_root = self.tree_view.build_tree(status)

            # Update detail if cron is selected
            if self.tree_view.selected_cron_id:
                await self._refresh_detail(self.tree_view.selected_cron_id, status)

            self.state.last_refresh = datetime.now().isoformat()
            return True

        except Exception as e:
            print(f"Refresh error: {e}")
            return False

    async def _refresh_detail(self, cron_id: str, system_status: Dict[str, Any]):
        """Refresh detail view for selected cron"""
        # Get cron-specific status
        cron_status = self._extract_cron_status(cron_id, system_status)

        # Get events
        events = []
        if self.events_callback:
            events = await self.events_callback(cron_id)

        # Get suggestions
        suggestions = []
        if self.suggestions_callback:
            suggestions = await self.suggestions_callback(cron_id)

        # Build detail view
        self.detail_view = self.detail_panel.build_detail_view(
            cron_id=cron_id,
            cron_status=cron_status,
            activity_events=events,
            suggestions=suggestions
        )

        # Add chat history if interactive
        if self.detail_view.is_interactive:
            self.detail_view.chat_history = self.interaction.get_chat_history(cron_id)

    def _extract_cron_status(self, cron_id: str, system_status: Dict[str, Any]) -> Dict[str, Any]:
        """Extract status for a specific cron from system status"""
        if cron_id == "system":
            return system_status.get("system", {})

        if ":" in cron_id:
            cron_type, owner_id = cron_id.split(":", 1)

            if cron_type == "team":
                return system_status.get("teams", {}).get(owner_id, {})

            if cron_type == "user":
                # Find user in teams
                for team_status in system_status.get("teams", {}).values():
                    users = team_status.get("users", {})
                    if owner_id in users:
                        return users[owner_id]

        return {}

    def render(self) -> str:
        """
        Render the complete terminal UI.

        Returns:
            Complete terminal output as string
        """
        lines = []

        # Header
        lines.extend(self._render_header())
        lines.append("")

        # Main content (two panels side by side)
        tree_lines = self._render_tree_panel()
        detail_lines = self._render_detail_panel()

        # Combine panels
        max_lines = max(len(tree_lines), len(detail_lines))
        for i in range(max_lines):
            tree_line = tree_lines[i] if i < len(tree_lines) else ""
            detail_line = detail_lines[i] if i < len(detail_lines) else ""

            # Pad tree line to fixed width
            tree_line = f"{tree_line:<{self.config.tree_width}}"

            lines.append(f"│{tree_line}│{detail_line}│")

        # Footer
        lines.append("")
        lines.extend(self._render_footer())

        return "\n".join(lines)

    def _render_header(self) -> List[str]:
        """Render terminal header"""
        width = self.config.width
        lines = []

        # Title bar
        title = "🧠 LLMOS CRON TERMINAL"
        user_info = f"👤 {self.user_id}"
        if self.team_id:
            user_info += f" | 👥 {self.team_id}"

        padding = width - len(title) - len(user_info) - 4
        lines.append("╔" + "═" * (width - 2) + "╗")
        lines.append(f"║ {title}{' ' * padding}{user_info} ║")
        lines.append("╠" + "═" * (self.config.tree_width) + "╦" + "═" * (self.config.detail_width) + "╣")

        return lines

    def _render_tree_panel(self) -> List[str]:
        """Render the left tree panel"""
        if self.tree_root:
            return self.tree_view.render(self.tree_root, self.config.tree_width)
        else:
            lines = ["🤖 CRON PROCESSES", "─" * (self.config.tree_width - 2), "", "Loading..."]
            return lines

    def _render_detail_panel(self) -> List[str]:
        """Render the right detail panel"""
        if self.detail_view:
            return self.detail_panel.render(
                self.detail_view,
                self.config.detail_width,
                self.config.height - 6
            )
        else:
            lines = ["📋 SELECT A CRON", "─" * (self.config.detail_width - 2), ""]
            lines.append("Use arrow keys to navigate the tree")
            lines.append("Press Enter to select a cron")
            return lines

    def _render_footer(self) -> List[str]:
        """Render terminal footer"""
        width = self.config.width
        lines = []

        lines.append("╠" + "═" * (width - 2) + "╣")

        # Status bar
        refresh_status = f"Last refresh: {self.state.last_refresh or 'Never'}"
        auto_status = "🔄 Auto" if self.state.auto_refresh else "⏸️ Paused"
        active_panel = f"Panel: {self.state.active_panel.upper()}"

        status_line = f" {refresh_status} | {auto_status} | {active_panel}"
        lines.append(f"║{status_line:<{width - 2}}║")

        # Keybindings
        keys = "[↑↓] Navigate  [←→] Expand  [Tab] Switch Panel  [r] Refresh  [q] Quit"
        lines.append(f"║ {keys:<{width - 4}} ║")

        lines.append("╚" + "═" * (width - 2) + "╝")

        return lines

    async def handle_input(self, key: str) -> bool:
        """
        Handle keyboard input.

        Args:
            key: Input key/character

        Returns:
            True if terminal should continue, False to quit
        """
        # Quit
        if key.lower() == "q":
            return False

        # Refresh
        if key.lower() == "r":
            await self.refresh()
            return True

        # Switch panels
        if key == "\t":
            self.state.active_panel = "detail" if self.state.active_panel == "tree" else "tree"
            return True

        # Toggle auto-refresh
        if key.lower() == "a":
            self.state.auto_refresh = not self.state.auto_refresh
            return True

        # Panel-specific input
        if self.state.active_panel == "tree":
            await self._handle_tree_input(key)
        else:
            await self._handle_detail_input(key)

        return True

    async def _handle_tree_input(self, key: str):
        """Handle input for tree panel"""
        if not self.tree_root:
            return

        # Navigation
        if key == "UP" or key == "k":
            new_id = self.tree_view.navigate_up(self.tree_root)
            if new_id:
                self.tree_view.select(new_id)
                await self._refresh_detail(new_id, await self._get_status())

        elif key == "DOWN" or key == "j":
            new_id = self.tree_view.navigate_down(self.tree_root)
            if new_id:
                self.tree_view.select(new_id)
                await self._refresh_detail(new_id, await self._get_status())

        # Expand/Collapse
        elif key == "LEFT" or key == "RIGHT" or key == " ":
            if self.tree_view.selected_cron_id:
                self.tree_view.toggle_expand(self.tree_view.selected_cron_id)

        # Select (Enter)
        elif key == "\n" or key == "\r":
            if self.tree_view.selected_cron_id:
                self.state.active_panel = "detail"

    async def _handle_detail_input(self, key: str):
        """Handle input for detail panel"""
        if not self.detail_view:
            return

        # Scroll
        if key == "UP" or key == "k":
            self.detail_panel.scroll_up()

        elif key == "DOWN" or key == "j":
            self.detail_panel.scroll_down(30, self.config.height - 6)

        # Interactive mode input
        elif self.detail_view.is_interactive:
            message = self.interaction.handle_input(key)
            if message:
                # Send message to cron
                response = await self.interaction.send_message(
                    self.detail_view.cron_id,
                    message
                )
                # Refresh detail to show new messages
                if response:
                    self.detail_view.chat_history = self.interaction.get_chat_history(
                        self.detail_view.cron_id
                    )

    async def _get_status(self) -> Dict[str, Any]:
        """Get current system status"""
        if self.status_callback:
            return await self.status_callback()
        return self._get_mock_status()

    def _get_mock_status(self) -> Dict[str, Any]:
        """Generate mock status for testing"""
        return {
            "system": {
                "status": "thinking",
                "last_run": datetime.now().isoformat(),
                "current_thinking": {
                    "action": "Analyzing cross-team patterns",
                    "patterns": [
                        {"name": "API optimization", "count": 12}
                    ]
                }
            },
            "teams": {
                "engineering": {
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
                                "considering": ["Suggest caching pattern"]
                            }
                        },
                        "bob": {
                            "status": "thinking",
                            "last_run": datetime.now().isoformat(),
                            "current_task": "Optimizing database queries"
                        }
                    }
                },
                "design": {
                    "status": "idle",
                    "users": {
                        "carol": {
                            "status": "idle"
                        }
                    }
                }
            }
        }

    async def run(self):
        """
        Run the terminal main loop.

        This is the entry point for running the interactive terminal.
        """
        self.running = True

        # Initial refresh
        await self.refresh()

        # Select user's cron by default
        user_cron_id = f"user:{self.user_id}"
        self.tree_view.select(user_cron_id)
        self.tree_view.expanded_nodes.append(f"team:{self.team_id}" if self.team_id else "system")

        print("\033[2J\033[H")  # Clear screen
        print(self.render())

        try:
            while self.running:
                # Auto-refresh
                if self.state.auto_refresh:
                    await asyncio.sleep(self.config.refresh_interval)
                    await self.refresh()
                    print("\033[2J\033[H")  # Clear screen
                    print(self.render())
                else:
                    await asyncio.sleep(0.1)

        except KeyboardInterrupt:
            self.running = False

        print("\n👋 Terminal closed.")

    def stop(self):
        """Stop the terminal"""
        self.running = False


# Convenience function for quick start
async def start_terminal(
    user_id: str,
    team_id: Optional[str] = None,
    **kwargs
) -> CronTerminal:
    """
    Quick start function for the terminal.

    Args:
        user_id: Current user's ID
        team_id: Current user's team ID
        **kwargs: Additional arguments for CronTerminal

    Returns:
        Running CronTerminal instance
    """
    terminal = CronTerminal(user_id, team_id, **kwargs)
    await terminal.run()
    return terminal
