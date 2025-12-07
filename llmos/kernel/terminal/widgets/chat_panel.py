"""
ChatPanel - Interactive chat widget for communicating with UserCron.

Provides a chat interface for users to interact with their personal cron.
"""

from typing import List, Dict, Optional, Callable, Awaitable
from datetime import datetime

from textual.widgets import Static, Input, RichLog
from textual.containers import Vertical, Horizontal
from textual.message import Message
from textual.binding import Binding
from rich.text import Text
from rich.panel import Panel


class ChatPanel(Vertical):
    """
    Interactive chat panel for cron communication.

    Features:
    - Message history display
    - Input field with send on Enter
    - User/Assistant message styling
    - Typing indicator
    - Auto-scroll to latest
    """

    DEFAULT_CSS = """
    ChatPanel {
        height: 100%;
        layout: vertical;
    }

    #chat-history {
        height: 1fr;
        border: solid $primary-darken-1;
        padding: 1;
        overflow-y: auto;
    }

    #chat-input-area {
        height: auto;
        dock: bottom;
        padding: 1;
        background: $surface-darken-1;
        border-top: solid $primary;
    }

    #chat-input {
        width: 100%;
    }

    .chat-message {
        margin-bottom: 1;
    }

    .chat-message-user {
        text-align: right;
    }

    .chat-message-assistant {
        text-align: left;
    }
    """

    BINDINGS = [
        Binding("escape", "blur_input", "Cancel"),
    ]

    class MessageSent(Message):
        """Message sent when user sends a chat message."""
        def __init__(self, content: str, cron_id: str) -> None:
            self.content = content
            self.cron_id = cron_id
            super().__init__()

    def __init__(
        self,
        cron_id: str,
        is_interactive: bool = True,
        send_callback: Optional[Callable[[str, str], Awaitable[str]]] = None,
        *args,
        **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.cron_id = cron_id
        self.is_interactive = is_interactive
        self.send_callback = send_callback
        self._history: List[Dict[str, str]] = []
        self._is_typing = False

    def compose(self):
        """Compose the chat panel."""
        yield RichLog(id="chat-history", highlight=True, markup=True)

        if self.is_interactive:
            with Horizontal(id="chat-input-area"):
                yield Input(
                    placeholder="Type a message... (Enter to send)",
                    id="chat-input"
                )
        else:
            yield Static(
                "[dim][READ-ONLY] You can view but not interact with this cron[/dim]",
                id="chat-readonly-notice"
            )

    def on_mount(self) -> None:
        """Initialize the chat display."""
        self._render_history()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle message submission."""
        if not event.value.strip():
            return

        message = event.value.strip()
        event.input.value = ""

        # Add user message
        self.add_message("user", message)

        # Post message for handling
        self.post_message(self.MessageSent(message, self.cron_id))

        # Show typing indicator
        self._show_typing()

    async def send_and_receive(self, message: str) -> Optional[str]:
        """
        Send a message and get response via callback.

        Args:
            message: Message to send

        Returns:
            Response from cron, or None if failed
        """
        if not self.send_callback:
            return None

        try:
            response = await self.send_callback(self.cron_id, message)
            self.add_message("assistant", response)
            return response
        except Exception as e:
            self.add_message("system", f"Error: {e}")
            return None
        finally:
            self._hide_typing()

    def add_message(self, role: str, content: str) -> None:
        """
        Add a message to the chat history.

        Args:
            role: "user", "assistant", or "system"
            content: Message content
        """
        self._history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        })
        self._write_message(role, content)

    def _write_message(self, role: str, content: str) -> None:
        """Write a single message to the log."""
        log = self.query_one("#chat-history", RichLog)

        text = Text()

        if role == "user":
            text.append("You: ", style="bold cyan")
            text.append(content)
        elif role == "assistant":
            text.append("Cron: ", style="bold green")
            text.append(content)
        else:  # system
            text.append("[", style="dim")
            text.append(content, style="yellow")
            text.append("]", style="dim")

        log.write(text)

    def _show_typing(self) -> None:
        """Show typing indicator."""
        if self._is_typing:
            return
        self._is_typing = True
        log = self.query_one("#chat-history", RichLog)
        log.write(Text("Cron is thinking...", style="dim italic"))

    def _hide_typing(self) -> None:
        """Hide typing indicator."""
        self._is_typing = False
        # Note: RichLog doesn't support removing lines, so we just continue

    def _render_history(self) -> None:
        """Render existing chat history."""
        for msg in self._history:
            self._write_message(msg["role"], msg["content"])

    def load_history(self, history: List[Dict[str, str]]) -> None:
        """
        Load chat history.

        Args:
            history: List of message dicts with role and content
        """
        self._history = history
        log = self.query_one("#chat-history", RichLog)
        log.clear()
        self._render_history()

    def clear_history(self) -> None:
        """Clear chat history."""
        self._history.clear()
        log = self.query_one("#chat-history", RichLog)
        log.clear()

    def action_blur_input(self) -> None:
        """Blur the input field."""
        try:
            input_widget = self.query_one("#chat-input", Input)
            input_widget.blur()
        except Exception:
            pass


class ReadOnlyChatPanel(Static):
    """
    Read-only panel shown for non-interactive crons.
    """

    DEFAULT_CSS = """
    ReadOnlyChatPanel {
        height: 100%;
        content-align: center middle;
        padding: 2;
    }
    """

    def __init__(self, cron_id: str, owner_name: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.cron_id = cron_id
        self.owner_name = owner_name

    def compose(self):
        """Compose the read-only notice."""
        panel = Panel(
            f"[dim]This is [bold]{self.owner_name}[/bold]'s cron.\n\n"
            "You can view activity but cannot interact.\n\n"
            "Select [bold]your[/bold] UserCron to chat.[/dim]",
            title="[yellow]Read-Only View[/yellow]",
            border_style="yellow",
        )
        yield Static(panel)
