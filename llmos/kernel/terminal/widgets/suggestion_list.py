"""
SuggestionList - Widget for displaying cron suggestions.

Shows suggestion cards with type indicators, confidence scores,
and action buttons.
"""

from typing import List, Dict, Any, Optional

from textual.widgets import Static, ListView, ListItem
from textual.containers import Vertical
from textual.message import Message
from rich.text import Text
from rich.panel import Panel
from rich.console import Group

from ..models import Suggestion, SuggestionType


class SuggestionCard(Static):
    """A single suggestion card widget."""

    DEFAULT_CSS = """
    SuggestionCard {
        height: auto;
        margin-bottom: 1;
        padding: 1;
    }

    SuggestionCard.-immediate {
        border: tall $error;
    }

    SuggestionCard.-recommendation {
        border: tall $success;
    }

    SuggestionCard.-prediction {
        border: tall $warning;
    }

    SuggestionCard.-creative {
        border: tall $secondary;
    }
    """

    # Type styling
    TYPE_STYLES = {
        SuggestionType.IMMEDIATE: ("->", "red bold", "IMMEDIATE"),
        SuggestionType.RECOMMENDATION: ("!!", "green", "RECOMMENDATION"),
        SuggestionType.PREDICTION: ("??", "yellow", "PREDICTION"),
        SuggestionType.CREATIVE: ("**", "magenta", "CREATIVE"),
    }

    def __init__(self, suggestion: Suggestion, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.suggestion = suggestion

        # Add CSS class based on type
        type_class = suggestion.suggestion_type.value
        self.add_class(f"-{type_class}")

    def compose(self):
        """Compose the card content."""
        yield Static(self._render_card())

    def _render_card(self) -> Panel:
        """Render the suggestion as a rich Panel."""
        icon, color, label = self.TYPE_STYLES.get(
            self.suggestion.suggestion_type,
            ("**", "white", "SUGGESTION")
        )

        elements = []

        # Header with type badge
        header = Text()
        header.append(f"[{icon}] ", style=color)
        header.append(label, style=f"{color} bold")
        if self.suggestion.confidence > 0:
            conf_pct = f"{self.suggestion.confidence:.0%}"
            header.append(f"  [{conf_pct}]", style="dim")
        elements.append(header)

        # Title
        title = Text()
        title.append("\n")
        title.append(self.suggestion.title, style="bold")
        elements.append(title)

        # Description
        if self.suggestion.description:
            desc = Text()
            desc.append("\n")
            desc.append(self.suggestion.description, style="dim")
            elements.append(desc)

        # Source
        if self.suggestion.source:
            source = Text()
            source.append("\n")
            source.append('from: "', style="dim italic")
            source.append(self.suggestion.source[:50], style="italic")
            source.append('"', style="dim italic")
            elements.append(source)

        return Panel(
            Group(*elements),
            border_style=color,
            padding=(0, 1),
        )


class SuggestionList(Vertical):
    """
    Widget for displaying a list of suggestions.

    Features:
    - Type-coded cards (immediate, recommendation, prediction, creative)
    - Confidence indicators
    - Source attribution
    - Action buttons (future)
    """

    DEFAULT_CSS = """
    SuggestionList {
        height: 100%;
        padding: 1;
        overflow-y: auto;
    }
    """

    class SuggestionSelected(Message):
        """Message sent when a suggestion is selected."""
        def __init__(self, suggestion: Suggestion) -> None:
            self.suggestion = suggestion
            super().__init__()

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._suggestions: List[Suggestion] = []

    def load_suggestions(self, suggestions: List[Suggestion]) -> None:
        """
        Load suggestions into the widget.

        Args:
            suggestions: List of Suggestion objects
        """
        self._suggestions = suggestions
        self._render_suggestions()

    def _render_suggestions(self) -> None:
        """Render all suggestion cards."""
        # Remove existing children
        self.remove_children()

        if not self._suggestions:
            self.mount(Static(
                "[dim]No suggestions at this time[/dim]",
                classes="empty-message"
            ))
            return

        # Sort by type priority (immediate first)
        priority = {
            SuggestionType.IMMEDIATE: 0,
            SuggestionType.RECOMMENDATION: 1,
            SuggestionType.PREDICTION: 2,
            SuggestionType.CREATIVE: 3,
        }
        sorted_suggestions = sorted(
            self._suggestions,
            key=lambda s: (priority.get(s.suggestion_type, 99), -s.confidence)
        )

        # Add cards
        for suggestion in sorted_suggestions[:6]:  # Max 6 suggestions
            self.mount(SuggestionCard(suggestion))

    @classmethod
    def from_dicts(cls, suggestion_dicts: List[Dict[str, Any]]) -> "SuggestionList":
        """
        Create a SuggestionList from dictionaries.

        Args:
            suggestion_dicts: List of suggestion dictionaries

        Returns:
            Configured SuggestionList widget
        """
        widget = cls()

        suggestions = []
        for s in suggestion_dicts:
            stype = cls._parse_type(s.get("type", "recommendation"))
            suggestions.append(Suggestion(
                suggestion_type=stype,
                title=s.get("title", ""),
                description=s.get("description", ""),
                confidence=s.get("confidence", 0.0),
                source=s.get("source"),
                action_id=s.get("action_id"),
            ))

        widget.load_suggestions(suggestions)
        return widget

    @staticmethod
    def _parse_type(type_str: str) -> SuggestionType:
        """Parse suggestion type string."""
        type_map = {
            "immediate": SuggestionType.IMMEDIATE,
            "recommendation": SuggestionType.RECOMMENDATION,
            "prediction": SuggestionType.PREDICTION,
            "creative": SuggestionType.CREATIVE,
        }
        return type_map.get(type_str.lower(), SuggestionType.RECOMMENDATION)
