"""
Cron Tree View - Left panel of the terminal.

Displays the hierarchy of all crons with live status indicators.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from .models import CronTreeNode, CronState


class CronTreeView:
    """
    Renders and manages the cron hierarchy tree.

    The tree shows:
    - SystemCron at the root
    - TeamCrons as children
    - UserCrons under their respective teams
    """

    def __init__(
        self,
        current_user_id: str,
        current_team_id: Optional[str] = None
    ):
        self.current_user_id = current_user_id
        self.current_team_id = current_team_id
        self.expanded_nodes: List[str] = ["system"]  # Expand system by default
        self.selected_cron_id: Optional[str] = None

    def build_tree(self, system_cron_status: Dict[str, Any]) -> CronTreeNode:
        """
        Build the tree structure from system cron status.

        Args:
            system_cron_status: Status dict from SystemCron.get_global_status()

        Returns:
            Root CronTreeNode
        """
        # Create system node
        system_node = CronTreeNode(
            cron_id="system",
            cron_type="system",
            owner_id="system",
            display_name="🧠 SystemCron",
            state=self._parse_state(system_cron_status.get("system", {}).get("status", "idle")),
            last_activity=system_cron_status.get("system", {}).get("last_run"),
            pending_notifications=0
        )

        # Add team crons
        teams = system_cron_status.get("teams", {})
        for team_id, team_status in teams.items():
            team_node = CronTreeNode(
                cron_id=f"team:{team_id}",
                cron_type="team",
                owner_id=team_id,
                display_name=f"👥 TeamCron:{team_id}",
                state=self._parse_state(team_status.get("status", "idle")),
                last_activity=team_status.get("last_run"),
                pending_notifications=team_status.get("pending_notifications", 0)
            )
            system_node.children.append(team_node)

            # Add user crons under this team
            users = team_status.get("users", {})
            for user_id, user_status in users.items():
                is_current = user_id == self.current_user_id
                user_node = CronTreeNode(
                    cron_id=f"user:{user_id}",
                    cron_type="user",
                    owner_id=user_id,
                    display_name=f"👤 UserCron:{user_id}" + (" [YOU]" if is_current else ""),
                    state=self._parse_state(user_status.get("status", "idle")),
                    last_activity=user_status.get("last_run"),
                    pending_notifications=user_status.get("pending_notifications", 0),
                    current_task=user_status.get("current_task"),
                    is_current_user=is_current
                )
                team_node.children.append(user_node)

        # Expand current user's team by default
        if self.current_team_id:
            self.expanded_nodes.append(f"team:{self.current_team_id}")

        return system_node

    def _parse_state(self, state_str: str) -> CronState:
        """Parse state string to CronState enum"""
        state_map = {
            "idle": CronState.IDLE,
            "thinking": CronState.THINKING,
            "analyzing": CronState.ANALYZING,
            "proposing": CronState.PROPOSING,
            "running": CronState.THINKING,
            "error": CronState.ERROR,
            "stopped": CronState.STOPPED
        }
        return state_map.get(state_str.lower(), CronState.IDLE)

    def render(self, root: CronTreeNode, width: int = 35) -> List[str]:
        """
        Render the tree as a list of strings.

        Args:
            root: Root node of the tree
            width: Width of the panel

        Returns:
            List of formatted lines
        """
        lines = []
        lines.append("🤖 CRON PROCESSES")
        lines.append("─" * (width - 2))
        lines.append("")

        self._render_node(root, lines, prefix="", is_last=True, width=width)

        lines.append("")
        lines.append("─" * (width - 2))
        lines.append("[↑↓] Navigate  [Enter] Select")
        lines.append("[←→] Expand/Collapse  [r] Refresh")

        return lines

    def _render_node(
        self,
        node: CronTreeNode,
        lines: List[str],
        prefix: str,
        is_last: bool,
        width: int
    ):
        """Recursively render a node and its children"""
        # Determine connector
        connector = "└─" if is_last else "├─"

        # Expand/collapse indicator
        if node.children:
            is_expanded = node.cron_id in self.expanded_nodes
            expand_char = "▼" if is_expanded else "▶"
        else:
            expand_char = " "

        # Selection indicator
        is_selected = node.cron_id == self.selected_cron_id
        select_marker = "◄" if is_selected else " "

        # State indicator
        state_icons = {
            CronState.IDLE: "✅",
            CronState.THINKING: "💭",
            CronState.ANALYZING: "🔍",
            CronState.PROPOSING: "📝",
            CronState.ERROR: "❌",
            CronState.STOPPED: "⏹️"
        }
        state_icon = state_icons.get(node.state, "❓")

        # Build the line
        if prefix == "":
            # Root node
            line = f"{expand_char} {node.display_name} {select_marker}"
        else:
            line = f"{prefix}{connector}{expand_char} {node.display_name} {select_marker}"

        lines.append(line[:width - 2])

        # Add status line
        status_prefix = prefix + ("   " if is_last else "│  ")
        status_parts = []

        if node.current_task:
            status_parts.append(f"{state_icon} {node.current_task[:20]}...")
        else:
            status_parts.append(f"{state_icon} {node.state.value}")

        if node.pending_notifications > 0:
            status_parts.append(f"🔔 {node.pending_notifications}")

        status_line = f"{status_prefix}  {' | '.join(status_parts)}"
        lines.append(status_line[:width - 2])

        # Render children if expanded
        if node.children and node.cron_id in self.expanded_nodes:
            child_prefix = prefix + ("   " if is_last else "│  ")
            for i, child in enumerate(node.children):
                is_child_last = (i == len(node.children) - 1)
                self._render_node(child, lines, child_prefix, is_child_last, width)

    def toggle_expand(self, cron_id: str):
        """Toggle expansion of a node"""
        if cron_id in self.expanded_nodes:
            self.expanded_nodes.remove(cron_id)
        else:
            self.expanded_nodes.append(cron_id)

    def select(self, cron_id: str):
        """Select a cron for detail view"""
        self.selected_cron_id = cron_id

    def navigate_up(self, root: CronTreeNode) -> Optional[str]:
        """Navigate to previous visible node"""
        visible = self._get_visible_nodes(root)
        if not visible:
            return None

        if self.selected_cron_id is None:
            return visible[-1].cron_id

        for i, node in enumerate(visible):
            if node.cron_id == self.selected_cron_id:
                if i > 0:
                    return visible[i - 1].cron_id
                return None

        return None

    def navigate_down(self, root: CronTreeNode) -> Optional[str]:
        """Navigate to next visible node"""
        visible = self._get_visible_nodes(root)
        if not visible:
            return None

        if self.selected_cron_id is None:
            return visible[0].cron_id

        for i, node in enumerate(visible):
            if node.cron_id == self.selected_cron_id:
                if i < len(visible) - 1:
                    return visible[i + 1].cron_id
                return None

        return None

    def _get_visible_nodes(self, node: CronTreeNode) -> List[CronTreeNode]:
        """Get list of visible nodes in order"""
        result = [node]

        if node.cron_id in self.expanded_nodes:
            for child in node.children:
                result.extend(self._get_visible_nodes(child))

        return result
