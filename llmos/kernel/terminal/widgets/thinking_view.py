"""
ThinkingView - Widget for displaying cron's current cognitive state.

Shows what the cron is currently thinking about, patterns found,
and what it's considering doing next.
"""

from typing import Optional, List, Dict, Any

from textual.widgets import Static
from textual.containers import Vertical
from rich.text import Text
from rich.panel import Panel
from rich.console import Group

from ..models import ThinkingProcess


class ThinkingView(Static):
    """
    Widget for displaying the current thinking process of a cron.

    Displays:
    - Current action being performed
    - Items being analyzed
    - Patterns found
    - Things being considered
    - Cross-references
    """

    DEFAULT_CSS = """
    ThinkingView {
        padding: 1;
        height: auto;
        max-height: 15;
    }
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._thinking: Optional[ThinkingProcess] = None
        self._cron_state: str = "idle"

    def update_thinking(
        self,
        thinking: Optional[ThinkingProcess],
        cron_state: str = "idle"
    ) -> None:
        """
        Update the thinking display.

        Args:
            thinking: ThinkingProcess object or None if idle
            cron_state: Current state string for the header color
        """
        self._thinking = thinking
        self._cron_state = cron_state
        self._render_thinking()

    def _render_thinking(self) -> None:
        """Render the thinking process display."""
        if not self._thinking:
            self.update(self._render_idle())
            return

        # Build rich renderable
        elements = []

        # Current action with state-colored icon
        state_colors = {
            "idle": "green",
            "thinking": "yellow",
            "analyzing": "cyan",
            "proposing": "blue",
            "error": "red",
        }
        color = state_colors.get(self._cron_state, "white")

        action_text = Text()
        action_text.append(f"[{color}]ACTIVE[/{color}] ", style="bold")
        action_text.append(self._thinking.current_action)
        elements.append(action_text)
        elements.append("")

        # Analyzed items
        if self._thinking.analyzed_items:
            analyzed = Text()
            analyzed.append("Analyzed: ", style="dim")
            analyzed.append(", ".join(self._thinking.analyzed_items[:5]))
            if len(self._thinking.analyzed_items) > 5:
                analyzed.append(f" (+{len(self._thinking.analyzed_items) - 5} more)", style="dim")
            elements.append(analyzed)

        # Found patterns
        if self._thinking.found_patterns:
            elements.append("")
            elements.append(Text("Patterns Found:", style="bold green"))
            for pattern in self._thinking.found_patterns[:4]:
                name = pattern.get("name", "Unknown")
                count = pattern.get("count", 0)
                pattern_text = Text()
                pattern_text.append("  * ", style="green")
                pattern_text.append(f'"{name}"', style="italic")
                pattern_text.append(f" - {count} traces", style="dim")
                elements.append(pattern_text)

        # Considering
        if self._thinking.considering:
            elements.append("")
            elements.append(Text("Considering:", style="bold yellow"))
            for item in self._thinking.considering[:3]:
                consider_text = Text()
                consider_text.append("  -> ", style="yellow")
                consider_text.append(item)
                elements.append(consider_text)

        # Cross-references
        if self._thinking.cross_references:
            elements.append("")
            elements.append(Text("Cross-references:", style="bold cyan"))
            for ref in self._thinking.cross_references[:3]:
                ref_text = Text()
                ref_text.append("  @ ", style="cyan")
                ref_text.append(ref)
                elements.append(ref_text)

        # Create panel
        panel = Panel(
            Group(*elements),
            title="[bold]Current Thinking[/bold]",
            border_style=color,
        )

        self.update(panel)

    def _render_idle(self) -> Panel:
        """Render idle state."""
        idle_text = Text()
        idle_text.append("[green]:[/green] ", style="bold")
        idle_text.append("Idle - no active analysis")

        return Panel(
            idle_text,
            title="[bold]Current Thinking[/bold]",
            border_style="green",
        )

    @classmethod
    def from_status(cls, cron_status: Dict[str, Any]) -> "ThinkingView":
        """
        Create a ThinkingView from cron status dict.

        Args:
            cron_status: Status dict containing current_thinking

        Returns:
            Configured ThinkingView widget
        """
        widget = cls()

        thinking_data = cron_status.get("current_thinking")
        if thinking_data:
            thinking = ThinkingProcess(
                current_action=thinking_data.get("action", "Processing..."),
                analyzed_items=thinking_data.get("analyzed", []),
                found_patterns=thinking_data.get("patterns", []),
                considering=thinking_data.get("considering", []),
                cross_references=thinking_data.get("cross_refs", []),
            )
            widget.update_thinking(thinking, cron_status.get("status", "idle"))

        return widget
