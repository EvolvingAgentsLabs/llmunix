"""
CronTreeWidget - Custom tree widget for displaying cron hierarchy.

Provides a tree view of SystemCron -> TeamCrons -> UserCrons with
live status indicators and notification badges.
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from textual.widgets import Tree
from textual.widgets.tree import TreeNode
from textual.message import Message
from rich.text import Text

from ..models import CronState


@dataclass
class CronNodeData:
    """Data associated with a tree node."""
    cron_id: str
    cron_type: str  # "system", "team", "user"
    owner_id: str
    state: CronState
    pending_notifications: int = 0
    current_task: Optional[str] = None
    is_current_user: bool = False


class CronTreeWidget(Tree[CronNodeData]):
    """
    Custom tree widget for the cron hierarchy.

    Features:
    - Status icons with colors (idle=green, thinking=yellow, etc.)
    - Notification badges
    - Current user highlighting
    - Vim-style navigation (j/k)
    """

    BINDINGS = [
        ("j", "cursor_down", "Down"),
        ("k", "cursor_up", "Up"),
        ("g", "scroll_home", "Top"),
        ("G", "scroll_end", "Bottom"),
        ("space", "toggle_node", "Expand/Collapse"),
    ]

    class CronSelected(Message):
        """Message sent when a cron is selected."""
        def __init__(self, cron_id: str, cron_type: str, owner_id: str) -> None:
            self.cron_id = cron_id
            self.cron_type = cron_type
            self.owner_id = owner_id
            super().__init__()

    def __init__(
        self,
        current_user_id: str,
        current_team_id: Optional[str] = None,
        *args,
        **kwargs
    ) -> None:
        super().__init__("CRON PROCESSES", *args, **kwargs)
        self.current_user_id = current_user_id
        self.current_team_id = current_team_id
        self.show_root = True
        self.show_guides = True
        self.guide_depth = 2

    def _get_state_icon(self, state: CronState) -> str:
        """Get status icon for a cron state."""
        icons = {
            CronState.IDLE: "[green]:[/green]",
            CronState.THINKING: "[yellow]:[/yellow]",
            CronState.ANALYZING: "[cyan]:[/cyan]",
            CronState.PROPOSING: "[blue]:[/blue]",
            CronState.ERROR: "[red]:[/red]",
            CronState.STOPPED: "[dim]:[/dim]",
        }
        return icons.get(state, "[white]:[/white]")

    def _get_type_icon(self, cron_type: str) -> str:
        """Get icon for cron type."""
        icons = {
            "system": "[bold cyan]SYS[/bold cyan]",
            "team": "[bold blue]TM[/bold blue]",
            "user": "[bold green]USR[/bold green]",
        }
        return icons.get(cron_type, "[white]?[/white]")

    def _format_node_label(self, data: CronNodeData) -> Text:
        """Format the label for a tree node with rich styling."""
        # State indicator
        state_icon = self._get_state_icon(data.state)

        # Type icon
        type_icon = self._get_type_icon(data.cron_type)

        # Name
        if data.cron_type == "system":
            name = "SystemCron"
        elif data.cron_type == "team":
            name = f"Team:{data.owner_id}"
        else:
            name = f"User:{data.owner_id}"

        # Current user marker
        user_marker = ""
        if data.is_current_user:
            user_marker = " [bold yellow][YOU][/bold yellow]"

        # Notification badge
        notif_badge = ""
        if data.pending_notifications > 0:
            notif_badge = f" [bold red on white] {data.pending_notifications} [/bold red on white]"

        # Current task preview
        task_preview = ""
        if data.current_task:
            short_task = data.current_task[:20] + "..." if len(data.current_task) > 20 else data.current_task
            task_preview = f"\n    [dim]{short_task}[/dim]"

        label = f"{state_icon} {type_icon} {name}{user_marker}{notif_badge}{task_preview}"
        return Text.from_markup(label)

    def build_from_status(self, system_status: Dict[str, Any]) -> None:
        """
        Build the tree from system cron status.

        Args:
            system_status: Status dict from SystemCron.get_global_status()
        """
        self.clear()

        # Parse system state
        system_data = system_status.get("system", {})
        system_state = self._parse_state(system_data.get("status", "idle"))

        # Create root node (SystemCron)
        root_data = CronNodeData(
            cron_id="system",
            cron_type="system",
            owner_id="system",
            state=system_state,
            pending_notifications=0,
            current_task=(system_data.get("current_thinking") or {}).get("action"),
        )
        self.root.data = root_data
        self.root.label = self._format_node_label(root_data)
        self.root.expand()

        # Add team crons
        teams = system_status.get("teams", {})
        for team_id, team_status in teams.items():
            team_state = self._parse_state(team_status.get("status", "idle"))
            team_data = CronNodeData(
                cron_id=f"team:{team_id}",
                cron_type="team",
                owner_id=team_id,
                state=team_state,
                pending_notifications=team_status.get("pending_notifications", 0),
            )

            team_node = self.root.add(
                self._format_node_label(team_data),
                data=team_data,
            )

            # Expand current user's team by default
            if team_id == self.current_team_id:
                team_node.expand()

            # Add user crons under this team
            users = team_status.get("users", {})
            for user_id, user_status in users.items():
                is_current = user_id == self.current_user_id
                user_state = self._parse_state(user_status.get("status", "idle"))
                user_data = CronNodeData(
                    cron_id=f"user:{user_id}",
                    cron_type="user",
                    owner_id=user_id,
                    state=user_state,
                    pending_notifications=user_status.get("pending_notifications", 0),
                    current_task=user_status.get("current_task"),
                    is_current_user=is_current,
                )

                team_node.add(
                    self._format_node_label(user_data),
                    data=user_data,
                )

    def _parse_state(self, state_str: str) -> CronState:
        """Parse state string to CronState enum."""
        state_map = {
            "idle": CronState.IDLE,
            "thinking": CronState.THINKING,
            "analyzing": CronState.ANALYZING,
            "proposing": CronState.PROPOSING,
            "running": CronState.THINKING,
            "error": CronState.ERROR,
            "stopped": CronState.STOPPED,
        }
        return state_map.get(state_str.lower(), CronState.IDLE)

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """Handle node selection and post message."""
        if event.node.data:
            data = event.node.data
            self.post_message(
                self.CronSelected(
                    cron_id=data.cron_id,
                    cron_type=data.cron_type,
                    owner_id=data.owner_id,
                )
            )

    def select_cron(self, cron_id: str) -> bool:
        """
        Programmatically select a cron by ID.

        Args:
            cron_id: The cron ID to select

        Returns:
            True if found and selected
        """
        def find_node(node: TreeNode, target_id: str) -> Optional[TreeNode]:
            if node.data and node.data.cron_id == target_id:
                return node
            for child in node.children:
                result = find_node(child, target_id)
                if result:
                    return result
            return None

        target_node = find_node(self.root, cron_id)
        if target_node:
            self.select_node(target_node)
            # Expand parent nodes
            parent = target_node.parent
            while parent:
                parent.expand()
                parent = parent.parent
            return True
        return False

    def refresh_node(self, cron_id: str, new_state: CronState,
                     notifications: int = 0, current_task: Optional[str] = None) -> None:
        """
        Update a specific node's display.

        Args:
            cron_id: The cron ID to update
            new_state: New state for the cron
            notifications: New notification count
            current_task: Current task description
        """
        def find_and_update(node: TreeNode) -> bool:
            if node.data and node.data.cron_id == cron_id:
                node.data.state = new_state
                node.data.pending_notifications = notifications
                node.data.current_task = current_task
                node.label = self._format_node_label(node.data)
                return True
            for child in node.children:
                if find_and_update(child):
                    return True
            return False

        find_and_update(self.root)
