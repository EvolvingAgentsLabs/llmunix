"""
Vercel KV Storage Adapter for Sessions

Provides session management using Vercel KV (Redis):
- Fast session lookups by ID
- Active session tracking per user/team
- Message history with pagination
- Trace references for cognitive commits

Key-Value Structure:
- session:{session_id} -> Session JSON
- user:{user_id}:sessions -> Set of session IDs
- team:{team_id}:sessions -> Set of session IDs
- session:{session_id}:messages -> List of messages
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict, field
import json
from enum import Enum


class SessionStatus(Enum):
    """Session status"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"


@dataclass
class Message:
    """Chat message"""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: str
    traces: Optional[List[int]] = None
    artifacts: Optional[List[str]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Session:
    """Chat session"""
    session_id: str
    name: str
    volume: str  # 'system', 'team', or 'user'
    volume_id: str  # 'system', team_id, or user_id
    status: SessionStatus
    created_at: str
    updated_at: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class VercelKVAdapter:
    """
    Adapter for Vercel KV storage to manage sessions.

    In production, this would use:
    - Vercel KV API (Redis) for fast session access
    - TTL for automatic cleanup of old sessions
    - Pub/Sub for real-time session updates
    """

    def __init__(self, kv_token: Optional[str] = None):
        """
        Initialize Vercel KV adapter.

        Args:
            kv_token: Vercel KV API token (from env: KV_REST_API_TOKEN)
        """
        self.kv_token = kv_token
        self._cache: Dict[str, Any] = {}

    # ========================================================================
    # Session Management
    # ========================================================================

    def create_session(
        self,
        session_id: str,
        name: str,
        volume: str,
        volume_id: str,
        initial_message: Optional[str] = None
    ) -> Session:
        """
        Create a new session.

        Args:
            session_id: Unique session identifier
            name: Human-readable session name
            volume: 'system', 'team', or 'user'
            volume_id: Volume identifier
            initial_message: Optional first message

        Returns:
            Session object
        """
        now = datetime.utcnow().isoformat() + "Z"

        session = Session(
            session_id=session_id,
            name=name,
            volume=volume,
            volume_id=volume_id,
            status=SessionStatus.ACTIVE,
            created_at=now,
            updated_at=now
        )

        # TODO: Save to Vercel KV
        # kv.set(f"session:{session_id}", json.dumps(asdict(session)))
        # kv.sadd(f"{volume}:{volume_id}:sessions", session_id)

        self._cache[f"session:{session_id}"] = session

        # Add initial message if provided
        if initial_message:
            self.add_message(
                session_id,
                Message(
                    role="user",
                    content=initial_message,
                    timestamp=now
                )
            )

        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Get a session by ID.

        Args:
            session_id: Session identifier

        Returns:
            Session object or None
        """
        cache_key = f"session:{session_id}"

        if cache_key in self._cache:
            return self._cache[cache_key]

        # TODO: Load from Vercel KV
        # data = kv.get(f"session:{session_id}")
        # if data:
        #     session_dict = json.loads(data)
        #     session = Session(**session_dict)

        # Mock response
        if session_id == "sess_quantum_research":
            session = Session(
                session_id=session_id,
                name="Quantum Research",
                volume="user",
                volume_id="user_alice",
                status=SessionStatus.ACTIVE,
                created_at="2025-12-13T10:00:00Z",
                updated_at="2025-12-13T10:30:00Z",
                metadata={"project": "qiskit-studio"}
            )
            self._cache[cache_key] = session
            return session

        return None

    def list_sessions(
        self,
        volume: str,
        volume_id: str,
        status: Optional[SessionStatus] = None
    ) -> List[Session]:
        """
        List sessions for a volume.

        Args:
            volume: 'system', 'team', or 'user'
            volume_id: Volume identifier
            status: Optional status filter

        Returns:
            List of sessions
        """
        # TODO: Query Vercel KV
        # session_ids = kv.smembers(f"{volume}:{volume_id}:sessions")
        # sessions = [self.get_session(sid) for sid in session_ids]

        # Mock response
        mock_sessions = [
            Session(
                session_id="sess_quantum_research",
                name="Quantum Research",
                volume=volume,
                volume_id=volume_id,
                status=SessionStatus.ACTIVE,
                created_at="2025-12-13T10:00:00Z",
                updated_at="2025-12-13T10:30:00Z"
            ),
            Session(
                session_id="sess_data_analysis",
                name="Data Analysis",
                volume=volume,
                volume_id=volume_id,
                status=SessionStatus.PAUSED,
                created_at="2025-12-12T14:00:00Z",
                updated_at="2025-12-12T16:00:00Z"
            )
        ]

        if status:
            mock_sessions = [s for s in mock_sessions if s.status == status]

        return mock_sessions

    def update_session(
        self,
        session_id: str,
        status: Optional[SessionStatus] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update session status or metadata.

        Args:
            session_id: Session identifier
            status: New status
            metadata: Metadata updates

        Returns:
            True if successful
        """
        session = self.get_session(session_id)
        if not session:
            return False

        if status:
            session.status = status

        if metadata:
            session.metadata.update(metadata)

        session.updated_at = datetime.utcnow().isoformat() + "Z"

        # TODO: Save to Vercel KV
        # kv.set(f"session:{session_id}", json.dumps(asdict(session)))

        return True

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.

        Args:
            session_id: Session identifier

        Returns:
            True if successful
        """
        session = self.get_session(session_id)
        if not session:
            return False

        # TODO: Delete from Vercel KV
        # kv.delete(f"session:{session_id}")
        # kv.delete(f"session:{session_id}:messages")
        # kv.srem(f"{session.volume}:{session.volume_id}:sessions", session_id)

        if f"session:{session_id}" in self._cache:
            del self._cache[f"session:{session_id}"]

        return True

    # ========================================================================
    # Message Management
    # ========================================================================

    def add_message(self, session_id: str, message: Message) -> bool:
        """
        Add a message to a session.

        Args:
            session_id: Session identifier
            message: Message object

        Returns:
            True if successful
        """
        session = self.get_session(session_id)
        if not session:
            return False

        # Update session timestamp
        session.updated_at = datetime.utcnow().isoformat() + "Z"

        # TODO: Add to Vercel KV
        # kv.rpush(f"session:{session_id}:messages", json.dumps(asdict(message)))
        # kv.set(f"session:{session_id}", json.dumps(asdict(session)))

        # Update cache
        cache_key = f"session:{session_id}:messages"
        if cache_key not in self._cache:
            self._cache[cache_key] = []
        self._cache[cache_key].append(message)

        return True

    def get_messages(
        self,
        session_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Message]:
        """
        Get messages for a session.

        Args:
            session_id: Session identifier
            limit: Maximum messages to return
            offset: Number of messages to skip

        Returns:
            List of messages
        """
        cache_key = f"session:{session_id}:messages"

        if cache_key in self._cache:
            messages = self._cache[cache_key]
            return messages[offset:offset + limit]

        # TODO: Load from Vercel KV
        # messages_json = kv.lrange(f"session:{session_id}:messages", offset, offset + limit - 1)
        # messages = [Message(**json.loads(m)) for m in messages_json]

        # Mock response
        if session_id == "sess_quantum_research":
            messages = [
                Message(
                    role="user",
                    content="Create a quantum circuit with 3 qubits",
                    timestamp="2025-12-13T10:00:00Z"
                ),
                Message(
                    role="assistant",
                    content="I'll create a quantum circuit with 3 qubits using Qiskit.",
                    timestamp="2025-12-13T10:00:05Z",
                    traces=[1, 2, 3],
                    artifacts=["quantum_circuit.py", "circuit_diagram.png"]
                ),
                Message(
                    role="user",
                    content="Now optimize it for better fidelity",
                    timestamp="2025-12-13T10:05:00Z"
                ),
                Message(
                    role="assistant",
                    content="I've optimized the circuit using error mitigation techniques.",
                    timestamp="2025-12-13T10:05:15Z",
                    traces=[4, 5],
                    artifacts=["optimized_circuit.py", "fidelity_report.json"]
                )
            ]
            self._cache[cache_key] = messages
            return messages[offset:offset + limit]

        return []

    def get_message_count(self, session_id: str) -> int:
        """
        Get total message count for a session.

        Args:
            session_id: Session identifier

        Returns:
            Message count
        """
        # TODO: Query Vercel KV
        # return kv.llen(f"session:{session_id}:messages")

        messages = self.get_messages(session_id)
        return len(messages)

    # ========================================================================
    # Trace Management
    # ========================================================================

    def get_traces_for_session(self, session_id: str) -> List[int]:
        """
        Get all trace IDs used in a session.

        Args:
            session_id: Session identifier

        Returns:
            List of trace IDs
        """
        messages = self.get_messages(session_id)
        traces = []

        for message in messages:
            if message.traces:
                traces.extend(message.traces)

        return traces

    def get_artifacts_for_session(self, session_id: str) -> List[str]:
        """
        Get all artifacts created in a session.

        Args:
            session_id: Session identifier

        Returns:
            List of artifact paths
        """
        messages = self.get_messages(session_id)
        artifacts = []

        for message in messages:
            if message.artifacts:
                artifacts.extend(message.artifacts)

        return artifacts

    # ========================================================================
    # Statistics
    # ========================================================================

    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """
        Get statistics for a session.

        Args:
            session_id: Session identifier

        Returns:
            Statistics dictionary
        """
        session = self.get_session(session_id)
        if not session:
            return {}

        messages = self.get_messages(session_id)
        traces = self.get_traces_for_session(session_id)
        artifacts = self.get_artifacts_for_session(session_id)

        user_messages = [m for m in messages if m.role == "user"]
        assistant_messages = [m for m in messages if m.role == "assistant"]

        return {
            "session_id": session_id,
            "name": session.name,
            "status": session.status.value,
            "message_count": len(messages),
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "trace_count": len(traces),
            "artifact_count": len(artifacts),
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "duration_hours": self._calculate_duration(session.created_at, session.updated_at)
        }

    def _calculate_duration(self, start: str, end: str) -> float:
        """Calculate duration in hours between two ISO timestamps"""
        try:
            start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
            end_dt = datetime.fromisoformat(end.replace("Z", "+00:00"))
            duration = end_dt - start_dt
            return duration.total_seconds() / 3600
        except:
            return 0.0


# ============================================================================
# Mock Usage Example
# ============================================================================

def example_usage():
    """Example of using the Vercel KV adapter"""
    adapter = VercelKVAdapter()

    # Create a new session
    session = adapter.create_session(
        session_id="sess_example",
        name="Example Session",
        volume="user",
        volume_id="user_alice",
        initial_message="Hello, let's start working on quantum circuits"
    )

    print(f"Created session: {session.session_id}")

    # Add assistant response
    adapter.add_message(
        session.session_id,
        Message(
            role="assistant",
            content="Great! I'll help you build quantum circuits.",
            timestamp=datetime.utcnow().isoformat() + "Z",
            traces=[1, 2],
            artifacts=["circuit.py"]
        )
    )

    # Get messages
    messages = adapter.get_messages(session.session_id)
    print(f"\nMessages: {len(messages)}")
    for msg in messages:
        print(f"  {msg.role}: {msg.content[:50]}...")

    # Get stats
    stats = adapter.get_session_stats(session.session_id)
    print(f"\nStats:")
    print(f"  Messages: {stats['message_count']}")
    print(f"  Traces: {stats['trace_count']}")
    print(f"  Artifacts: {stats['artifact_count']}")


if __name__ == "__main__":
    example_usage()
