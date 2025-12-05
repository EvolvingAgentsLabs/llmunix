"""
Cron Interaction Handler - Chat with your UserCron.

Enables interactive communication between users and their personal cron.
Only the owner can interact with their cron - others have read-only access.
"""

from typing import Dict, Any, Optional, List, Callable, Awaitable
from dataclasses import dataclass, field
from datetime import datetime
import asyncio


@dataclass
class ChatMessage:
    """A message in the cron chat"""
    role: str  # "user" or "cron"
    content: str
    timestamp: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InteractionSession:
    """Active interaction session with a cron"""
    cron_id: str
    user_id: str
    messages: List[ChatMessage] = field(default_factory=list)
    started_at: str = ""
    is_active: bool = True

    def __post_init__(self):
        if not self.started_at:
            self.started_at = datetime.now().isoformat()


class CronInteraction:
    """
    Handles interactive chat with UserCron.

    The interaction system allows users to:
    - Ask their cron for suggestions
    - Request specific analysis
    - Approve or reject cron proposals
    - Guide cron behavior with preferences
    """

    def __init__(
        self,
        current_user_id: str,
        cron_callback: Optional[Callable[[str, str], Awaitable[str]]] = None
    ):
        """
        Initialize the interaction handler.

        Args:
            current_user_id: ID of the current user
            cron_callback: Async function to get cron responses
                          Takes (cron_id, user_message) -> cron_response
        """
        self.current_user_id = current_user_id
        self.cron_callback = cron_callback
        self.sessions: Dict[str, InteractionSession] = {}
        self.input_buffer: str = ""

    def can_interact(self, cron_id: str) -> bool:
        """
        Check if the user can interact with a cron.

        Only the owner of a UserCron can interact with it.
        SystemCron and TeamCrons are read-only for everyone.
        """
        if ":" not in cron_id:
            return False  # System cron - no interaction

        cron_type, owner_id = cron_id.split(":", 1)

        if cron_type == "user":
            return owner_id == self.current_user_id

        return False  # Team crons are read-only

    def get_or_create_session(self, cron_id: str) -> Optional[InteractionSession]:
        """Get existing session or create new one"""
        if not self.can_interact(cron_id):
            return None

        if cron_id not in self.sessions:
            self.sessions[cron_id] = InteractionSession(
                cron_id=cron_id,
                user_id=self.current_user_id
            )

        return self.sessions[cron_id]

    def add_user_message(self, cron_id: str, content: str) -> bool:
        """Add a user message to the session"""
        session = self.get_or_create_session(cron_id)
        if not session:
            return False

        session.messages.append(ChatMessage(
            role="user",
            content=content,
            timestamp=datetime.now().isoformat()
        ))
        return True

    def add_cron_response(self, cron_id: str, content: str, metadata: Optional[Dict] = None) -> bool:
        """Add a cron response to the session"""
        session = self.get_or_create_session(cron_id)
        if not session:
            return False

        session.messages.append(ChatMessage(
            role="cron",
            content=content,
            timestamp=datetime.now().isoformat(),
            metadata=metadata or {}
        ))
        return True

    async def send_message(self, cron_id: str, message: str) -> Optional[str]:
        """
        Send a message to the cron and get response.

        Args:
            cron_id: ID of the cron to message
            message: User's message

        Returns:
            Cron's response or None if interaction not allowed
        """
        if not self.can_interact(cron_id):
            return None

        # Add user message
        self.add_user_message(cron_id, message)

        # Get cron response
        if self.cron_callback:
            response = await self.cron_callback(cron_id, message)
        else:
            # Default response when no callback is configured
            response = self._generate_default_response(message)

        # Add cron response
        self.add_cron_response(cron_id, response)

        return response

    def _generate_default_response(self, message: str) -> str:
        """Generate a default response when no callback is configured"""
        message_lower = message.lower()

        if any(word in message_lower for word in ["suggest", "what should", "next"]):
            return "💡 Based on your recent activity, I suggest reviewing the pending proposals in your queue."

        if any(word in message_lower for word in ["analyze", "look at", "check"]):
            return "🔍 I'll analyze that for you. Give me a moment to review the relevant traces..."

        if any(word in message_lower for word in ["help", "how"]):
            return "🤖 I can help you with:\n  • Suggesting next steps\n  • Analyzing your traces\n  • Reviewing proposals\n  • Finding patterns in your work"

        return "🤔 I'm processing your request. What specific aspect would you like me to focus on?"

    def get_chat_history(self, cron_id: str, limit: int = 10) -> List[Dict[str, str]]:
        """Get recent chat history for display"""
        session = self.sessions.get(cron_id)
        if not session:
            return []

        messages = session.messages[-limit:]
        return [{"role": m.role, "content": m.content} for m in messages]

    def handle_input(self, char: str) -> Optional[str]:
        """
        Handle keyboard input for chat.

        Args:
            char: Input character

        Returns:
            Complete message if Enter pressed, None otherwise
        """
        if char == "\n" or char == "\r":
            # Enter pressed - return complete message
            message = self.input_buffer.strip()
            self.input_buffer = ""
            return message if message else None

        elif char == "\x7f" or char == "\b":
            # Backspace
            self.input_buffer = self.input_buffer[:-1]

        elif char.isprintable():
            # Regular character
            self.input_buffer += char

        return None

    def get_input_buffer(self) -> str:
        """Get current input buffer for display"""
        return self.input_buffer

    def clear_input(self):
        """Clear the input buffer"""
        self.input_buffer = ""

    def close_session(self, cron_id: str):
        """Close an interaction session"""
        if cron_id in self.sessions:
            self.sessions[cron_id].is_active = False

    def render_chat_input(self, width: int = 40) -> List[str]:
        """Render the chat input area"""
        lines = []

        # Input prompt
        cursor = "_" if len(self.input_buffer) < width - 5 else ""
        display_text = self.input_buffer[-(width - 5):] if self.input_buffer else ""
        lines.append(f"> {display_text}{cursor}")

        return lines

    def get_quick_actions(self) -> List[Dict[str, str]]:
        """Get quick action suggestions for the user"""
        return [
            {"key": "s", "label": "Suggest next steps"},
            {"key": "a", "label": "Analyze recent work"},
            {"key": "p", "label": "Show proposals"},
            {"key": "h", "label": "Help"}
        ]

    def render_quick_actions(self, width: int = 40) -> List[str]:
        """Render quick action buttons"""
        actions = self.get_quick_actions()
        lines = []

        lines.append("Quick actions:")
        for action in actions:
            lines.append(f"  [{action['key']}] {action['label']}")

        return lines
