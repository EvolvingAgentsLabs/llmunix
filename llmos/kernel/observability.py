"""
Observability System for LLM OS Sentience Crons

Provides visibility into:
- Cron activity (what each cron is doing, has done)
- Artifact changes (created, evolved, modified, deleted)
- Evolution proposals and their status
- System health and metrics

Users can query this system on-demand to see:
1. Activity Feed: Recent actions by all crons
2. Change Log: What artifacts have changed
3. Proposals: Pending evolution proposals
4. Insights: Generated insights and suggestions
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Callable
from pathlib import Path
from datetime import datetime, timedelta
from enum import Enum
import json
import asyncio


class EventType(Enum):
    """Types of observable events"""
    # Cron lifecycle
    CRON_STARTED = "cron_started"
    CRON_STOPPED = "cron_stopped"
    CRON_CYCLE_BEGIN = "cron_cycle_begin"
    CRON_CYCLE_END = "cron_cycle_end"

    # Task events
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"

    # Artifact events
    ARTIFACT_CREATED = "artifact_created"
    ARTIFACT_EVOLVED = "artifact_evolved"
    ARTIFACT_PROMOTED = "artifact_promoted"
    ARTIFACT_DELETED = "artifact_deleted"

    # Analysis events
    PROPOSAL_CREATED = "proposal_created"
    PROPOSAL_APPLIED = "proposal_applied"
    PROPOSAL_REJECTED = "proposal_rejected"

    # Insight events
    INSIGHT_GENERATED = "insight_generated"
    SUGGESTION_CREATED = "suggestion_created"

    # System events
    SYSTEM_ALERT = "system_alert"
    HEALTH_CHECK = "health_check"


class Severity(Enum):
    """Event severity levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ObservableEvent:
    """An observable event in the system"""
    event_id: str
    event_type: EventType
    timestamp: str
    source_cron: str  # "system", "team:xyz", "user:abc"
    severity: Severity
    title: str
    description: str
    details: Dict[str, Any] = field(default_factory=dict)

    # For artifact-related events
    artifact_type: Optional[str] = None
    artifact_id: Optional[str] = None
    volume_type: Optional[str] = None

    # For user notification
    notify_user: bool = False
    acknowledged: bool = False

    def as_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp,
            "source_cron": self.source_cron,
            "severity": self.severity.value,
            "title": self.title,
            "description": self.description,
            "details": self.details,
            "artifact_type": self.artifact_type,
            "artifact_id": self.artifact_id,
            "volume_type": self.volume_type,
            "notify_user": self.notify_user,
            "acknowledged": self.acknowledged
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ObservableEvent":
        return cls(
            event_id=data["event_id"],
            event_type=EventType(data["event_type"]),
            timestamp=data["timestamp"],
            source_cron=data["source_cron"],
            severity=Severity(data["severity"]),
            title=data["title"],
            description=data["description"],
            details=data.get("details", {}),
            artifact_type=data.get("artifact_type"),
            artifact_id=data.get("artifact_id"),
            volume_type=data.get("volume_type"),
            notify_user=data.get("notify_user", False),
            acknowledged=data.get("acknowledged", False)
        )


@dataclass
class ActivitySummary:
    """Summary of cron activity for display"""
    cron_id: str
    cron_type: str  # "system", "team", "user"
    status: str  # "running", "idle", "stopped"
    last_cycle: Optional[str]
    events_today: int
    artifacts_created: int
    artifacts_evolved: int
    proposals_pending: int
    insights_generated: int

    def as_dict(self) -> Dict[str, Any]:
        return {
            "cron_id": self.cron_id,
            "cron_type": self.cron_type,
            "status": self.status,
            "last_cycle": self.last_cycle,
            "events_today": self.events_today,
            "artifacts_created": self.artifacts_created,
            "artifacts_evolved": self.artifacts_evolved,
            "proposals_pending": self.proposals_pending,
            "insights_generated": self.insights_generated
        }


class EventStore:
    """
    Persistent storage for observable events.

    Events are stored in a JSON file and can be queried
    by type, time range, source, etc.
    """

    def __init__(self, store_path: Path):
        self.store_path = store_path
        self._events: List[ObservableEvent] = []
        self._event_counter = 0
        self._load()

    def _load(self):
        """Load events from disk"""
        if self.store_path.exists():
            try:
                with open(self.store_path, 'r') as f:
                    data = json.load(f)
                    self._events = [ObservableEvent.from_dict(e) for e in data.get("events", [])]
                    self._event_counter = data.get("counter", len(self._events))
            except Exception:
                self._events = []
                self._event_counter = 0

    def _save(self):
        """Save events to disk"""
        self.store_path.parent.mkdir(parents=True, exist_ok=True)

        # Keep only last 10000 events
        events_to_save = self._events[-10000:]

        with open(self.store_path, 'w') as f:
            json.dump({
                "events": [e.as_dict() for e in events_to_save],
                "counter": self._event_counter
            }, f, indent=2)

    def add_event(self, event: ObservableEvent) -> str:
        """Add an event to the store"""
        self._events.append(event)
        self._save()
        return event.event_id

    def create_event(
        self,
        event_type: EventType,
        source_cron: str,
        title: str,
        description: str,
        severity: Severity = Severity.INFO,
        details: Optional[Dict[str, Any]] = None,
        artifact_type: Optional[str] = None,
        artifact_id: Optional[str] = None,
        volume_type: Optional[str] = None,
        notify_user: bool = False
    ) -> ObservableEvent:
        """Create and store a new event"""
        self._event_counter += 1

        event = ObservableEvent(
            event_id=f"evt_{self._event_counter:08d}",
            event_type=event_type,
            timestamp=datetime.now().isoformat(),
            source_cron=source_cron,
            severity=severity,
            title=title,
            description=description,
            details=details or {},
            artifact_type=artifact_type,
            artifact_id=artifact_id,
            volume_type=volume_type,
            notify_user=notify_user
        )

        self.add_event(event)
        return event

    def get_events(
        self,
        event_types: Optional[List[EventType]] = None,
        source_cron: Optional[str] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        severity: Optional[Severity] = None,
        limit: int = 100,
        unacknowledged_only: bool = False
    ) -> List[ObservableEvent]:
        """Query events with filters"""
        result = []

        for event in reversed(self._events):
            # Apply filters
            if event_types and event.event_type not in event_types:
                continue
            if source_cron and event.source_cron != source_cron:
                continue
            if since:
                event_time = datetime.fromisoformat(event.timestamp)
                if event_time < since:
                    continue
            if until:
                event_time = datetime.fromisoformat(event.timestamp)
                if event_time > until:
                    continue
            if severity and event.severity != severity:
                continue
            if unacknowledged_only and event.acknowledged:
                continue

            result.append(event)

            if len(result) >= limit:
                break

        return result

    def get_notifications(self, limit: int = 50) -> List[ObservableEvent]:
        """Get events that should notify users"""
        return self.get_events(
            unacknowledged_only=True,
            limit=limit
        )

    def acknowledge_event(self, event_id: str) -> bool:
        """Mark an event as acknowledged"""
        for event in self._events:
            if event.event_id == event_id:
                event.acknowledged = True
                self._save()
                return True
        return False

    def acknowledge_all(self, source_cron: Optional[str] = None):
        """Acknowledge all events, optionally filtered by source"""
        for event in self._events:
            if source_cron is None or event.source_cron == source_cron:
                event.acknowledged = True
        self._save()


class ObservabilityHub:
    """
    Central hub for observability in the LLM OS.

    Provides a unified interface for:
    - Recording events from crons
    - Querying activity and changes
    - Generating summaries for users
    - Managing notifications
    """

    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.event_store = EventStore(base_path / "events.json")

        # Subscribers for real-time notifications
        self._subscribers: List[Callable[[ObservableEvent], None]] = []

        # Cache for activity summaries
        self._summary_cache: Dict[str, ActivitySummary] = {}
        self._cache_time: Optional[datetime] = None

    # =========================================================================
    # EVENT RECORDING
    # =========================================================================

    def record_cron_started(self, cron_id: str, cron_type: str):
        """Record that a cron has started"""
        event = self.event_store.create_event(
            event_type=EventType.CRON_STARTED,
            source_cron=cron_id,
            title=f"{cron_type.title()} Cron Started",
            description=f"The {cron_type} cron '{cron_id}' has started running.",
            severity=Severity.INFO,
            notify_user=False
        )
        self._notify_subscribers(event)

    def record_cron_stopped(self, cron_id: str, cron_type: str):
        """Record that a cron has stopped"""
        event = self.event_store.create_event(
            event_type=EventType.CRON_STOPPED,
            source_cron=cron_id,
            title=f"{cron_type.title()} Cron Stopped",
            description=f"The {cron_type} cron '{cron_id}' has stopped.",
            severity=Severity.INFO,
            notify_user=False
        )
        self._notify_subscribers(event)

    def record_cycle(self, cron_id: str, tasks_completed: int, duration_seconds: float):
        """Record completion of a cron cycle"""
        event = self.event_store.create_event(
            event_type=EventType.CRON_CYCLE_END,
            source_cron=cron_id,
            title=f"Analysis Cycle Complete",
            description=f"Completed {tasks_completed} tasks in {duration_seconds:.1f}s",
            severity=Severity.DEBUG,
            details={
                "tasks_completed": tasks_completed,
                "duration_seconds": duration_seconds
            }
        )
        self._notify_subscribers(event)

    def record_artifact_created(
        self,
        cron_id: str,
        artifact_type: str,
        artifact_id: str,
        volume_type: str,
        reason: str
    ):
        """Record creation of a new artifact"""
        event = self.event_store.create_event(
            event_type=EventType.ARTIFACT_CREATED,
            source_cron=cron_id,
            title=f"New {artifact_type.title()} Created",
            description=reason,
            severity=Severity.INFO,
            artifact_type=artifact_type,
            artifact_id=artifact_id,
            volume_type=volume_type,
            notify_user=True
        )
        self._notify_subscribers(event)

    def record_artifact_evolved(
        self,
        cron_id: str,
        artifact_type: str,
        artifact_id: str,
        volume_type: str,
        reason: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Record evolution of an artifact"""
        event = self.event_store.create_event(
            event_type=EventType.ARTIFACT_EVOLVED,
            source_cron=cron_id,
            title=f"{artifact_type.title()} Evolved",
            description=reason,
            severity=Severity.INFO,
            artifact_type=artifact_type,
            artifact_id=artifact_id,
            volume_type=volume_type,
            details=details or {},
            notify_user=True
        )
        self._notify_subscribers(event)

    def record_artifact_promoted(
        self,
        cron_id: str,
        artifact_type: str,
        artifact_id: str,
        from_volume: str,
        to_volume: str,
        reason: str
    ):
        """Record promotion of an artifact between volumes"""
        event = self.event_store.create_event(
            event_type=EventType.ARTIFACT_PROMOTED,
            source_cron=cron_id,
            title=f"{artifact_type.title()} Promoted to {to_volume.title()}",
            description=reason,
            severity=Severity.INFO,
            artifact_type=artifact_type,
            artifact_id=artifact_id,
            volume_type=to_volume,
            details={"from_volume": from_volume, "to_volume": to_volume},
            notify_user=True
        )
        self._notify_subscribers(event)

    def record_artifact_deleted(
        self,
        cron_id: str,
        artifact_type: str,
        artifact_id: str,
        volume_type: str,
        reason: str
    ):
        """Record deletion of an artifact"""
        event = self.event_store.create_event(
            event_type=EventType.ARTIFACT_DELETED,
            source_cron=cron_id,
            title=f"{artifact_type.title()} Deleted",
            description=reason,
            severity=Severity.WARNING,
            artifact_type=artifact_type,
            artifact_id=artifact_id,
            volume_type=volume_type,
            notify_user=True
        )
        self._notify_subscribers(event)

    def record_proposal(
        self,
        cron_id: str,
        proposal_type: str,
        target_artifact: str,
        description: str
    ):
        """Record creation of an evolution proposal"""
        event = self.event_store.create_event(
            event_type=EventType.PROPOSAL_CREATED,
            source_cron=cron_id,
            title=f"Evolution Proposal: {proposal_type}",
            description=description,
            severity=Severity.INFO,
            artifact_id=target_artifact,
            notify_user=False
        )
        self._notify_subscribers(event)

    def record_insight(
        self,
        cron_id: str,
        insight_title: str,
        insight_content: str,
        volume_type: str
    ):
        """Record generation of an insight"""
        event = self.event_store.create_event(
            event_type=EventType.INSIGHT_GENERATED,
            source_cron=cron_id,
            title=f"Insight: {insight_title}",
            description=insight_content[:200] + "..." if len(insight_content) > 200 else insight_content,
            severity=Severity.INFO,
            volume_type=volume_type,
            notify_user=True
        )
        self._notify_subscribers(event)

    def record_suggestion(
        self,
        cron_id: str,
        suggestion_title: str,
        suggestion_content: str,
        volume_type: str
    ):
        """Record creation of a suggestion"""
        event = self.event_store.create_event(
            event_type=EventType.SUGGESTION_CREATED,
            source_cron=cron_id,
            title=f"Suggestion: {suggestion_title}",
            description=suggestion_content[:200] + "..." if len(suggestion_content) > 200 else suggestion_content,
            severity=Severity.INFO,
            volume_type=volume_type,
            notify_user=True
        )
        self._notify_subscribers(event)

    def record_alert(
        self,
        cron_id: str,
        title: str,
        description: str,
        severity: Severity = Severity.WARNING
    ):
        """Record a system alert"""
        event = self.event_store.create_event(
            event_type=EventType.SYSTEM_ALERT,
            source_cron=cron_id,
            title=title,
            description=description,
            severity=severity,
            notify_user=severity in [Severity.WARNING, Severity.ERROR, Severity.CRITICAL]
        )
        self._notify_subscribers(event)

    # =========================================================================
    # QUERYING
    # =========================================================================

    def get_activity_feed(
        self,
        cron_id: Optional[str] = None,
        limit: int = 50,
        since_hours: int = 24
    ) -> List[Dict[str, Any]]:
        """Get recent activity feed"""
        since = datetime.now() - timedelta(hours=since_hours)

        events = self.event_store.get_events(
            source_cron=cron_id,
            since=since,
            limit=limit
        )

        return [e.as_dict() for e in events]

    def get_artifact_changes(
        self,
        volume_type: Optional[str] = None,
        artifact_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get artifact change history"""
        events = self.event_store.get_events(
            event_types=[
                EventType.ARTIFACT_CREATED,
                EventType.ARTIFACT_EVOLVED,
                EventType.ARTIFACT_PROMOTED,
                EventType.ARTIFACT_DELETED
            ],
            limit=limit
        )

        # Filter by volume and artifact type
        result = []
        for event in events:
            if volume_type and event.volume_type != volume_type:
                continue
            if artifact_type and event.artifact_type != artifact_type:
                continue
            result.append(event.as_dict())

        return result

    def get_pending_notifications(self, cron_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get unacknowledged notifications for user"""
        events = self.event_store.get_events(
            source_cron=cron_id,
            unacknowledged_only=True,
            limit=100
        )

        # Only return events that should notify user
        return [e.as_dict() for e in events if e.notify_user]

    def get_activity_summary(self, cron_id: str, cron_type: str) -> ActivitySummary:
        """Get activity summary for a cron"""
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        # Get today's events for this cron
        events = self.event_store.get_events(
            source_cron=cron_id,
            since=today,
            limit=1000
        )

        # Count by type
        artifacts_created = sum(1 for e in events if e.event_type == EventType.ARTIFACT_CREATED)
        artifacts_evolved = sum(1 for e in events if e.event_type == EventType.ARTIFACT_EVOLVED)
        proposals = sum(1 for e in events if e.event_type == EventType.PROPOSAL_CREATED)
        insights = sum(1 for e in events if e.event_type == EventType.INSIGHT_GENERATED)

        # Find last cycle
        cycle_events = [e for e in events if e.event_type == EventType.CRON_CYCLE_END]
        last_cycle = cycle_events[0].timestamp if cycle_events else None

        # Determine status
        started = any(e.event_type == EventType.CRON_STARTED for e in events)
        stopped = any(e.event_type == EventType.CRON_STOPPED for e in events)

        if stopped and not started:
            status = "stopped"
        elif started:
            status = "running"
        else:
            status = "idle"

        return ActivitySummary(
            cron_id=cron_id,
            cron_type=cron_type,
            status=status,
            last_cycle=last_cycle,
            events_today=len(events),
            artifacts_created=artifacts_created,
            artifacts_evolved=artifacts_evolved,
            proposals_pending=proposals,
            insights_generated=insights
        )

    def get_global_summary(self) -> Dict[str, Any]:
        """Get global system summary"""
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        events = self.event_store.get_events(since=today, limit=10000)

        # Aggregate stats
        by_cron_type = {"system": 0, "team": 0, "user": 0}
        for event in events:
            if event.source_cron.startswith("team:"):
                by_cron_type["team"] += 1
            elif event.source_cron.startswith("user:"):
                by_cron_type["user"] += 1
            else:
                by_cron_type["system"] += 1

        artifacts_created = sum(1 for e in events if e.event_type == EventType.ARTIFACT_CREATED)
        artifacts_evolved = sum(1 for e in events if e.event_type == EventType.ARTIFACT_EVOLVED)
        insights = sum(1 for e in events if e.event_type == EventType.INSIGHT_GENERATED)
        suggestions = sum(1 for e in events if e.event_type == EventType.SUGGESTION_CREATED)
        alerts = sum(1 for e in events if e.event_type == EventType.SYSTEM_ALERT)

        pending_notifications = len([e for e in events if e.notify_user and not e.acknowledged])

        return {
            "date": today.isoformat(),
            "total_events": len(events),
            "events_by_cron_type": by_cron_type,
            "artifacts_created": artifacts_created,
            "artifacts_evolved": artifacts_evolved,
            "insights_generated": insights,
            "suggestions_created": suggestions,
            "alerts": alerts,
            "pending_notifications": pending_notifications
        }

    # =========================================================================
    # USER INTERACTION
    # =========================================================================

    def acknowledge(self, event_id: str) -> bool:
        """Acknowledge a notification"""
        return self.event_store.acknowledge_event(event_id)

    def acknowledge_all_for_cron(self, cron_id: str):
        """Acknowledge all notifications from a cron"""
        self.event_store.acknowledge_all(source_cron=cron_id)

    def acknowledge_all(self):
        """Acknowledge all notifications"""
        self.event_store.acknowledge_all()

    # =========================================================================
    # SUBSCRIPTIONS
    # =========================================================================

    def subscribe(self, callback: Callable[[ObservableEvent], None]):
        """Subscribe to real-time events"""
        self._subscribers.append(callback)

    def unsubscribe(self, callback: Callable[[ObservableEvent], None]):
        """Unsubscribe from events"""
        if callback in self._subscribers:
            self._subscribers.remove(callback)

    def _notify_subscribers(self, event: ObservableEvent):
        """Notify all subscribers of an event"""
        for callback in self._subscribers:
            try:
                callback(event)
            except Exception:
                pass  # Don't let subscriber errors break the system

    # =========================================================================
    # DISPLAY HELPERS
    # =========================================================================

    def format_activity_feed(self, limit: int = 20) -> str:
        """Format activity feed for display"""
        events = self.event_store.get_events(limit=limit)

        if not events:
            return "No recent activity."

        lines = ["## Recent Activity\n"]

        for event in events:
            icon = self._get_event_icon(event.event_type)
            time = event.timestamp.split("T")[1][:8]
            lines.append(f"- [{time}] {icon} **{event.title}**")
            lines.append(f"  {event.description}")

        return "\n".join(lines)

    def format_notifications(self) -> str:
        """Format pending notifications for display"""
        events = self.event_store.get_notifications()

        if not events:
            return "No pending notifications."

        lines = [f"## Notifications ({len(events)} pending)\n"]

        for event in events:
            icon = self._get_severity_icon(event.severity)
            lines.append(f"### {icon} {event.title}")
            lines.append(f"*{event.timestamp}* - {event.source_cron}")
            lines.append(f"\n{event.description}\n")
            lines.append(f"ID: `{event.event_id}`")
            lines.append("---")

        return "\n".join(lines)

    def _get_event_icon(self, event_type: EventType) -> str:
        """Get icon for event type"""
        icons = {
            EventType.CRON_STARTED: "[START]",
            EventType.CRON_STOPPED: "[STOP]",
            EventType.CRON_CYCLE_END: "[CYCLE]",
            EventType.ARTIFACT_CREATED: "[+NEW]",
            EventType.ARTIFACT_EVOLVED: "[EVOLVE]",
            EventType.ARTIFACT_PROMOTED: "[PROMOTE]",
            EventType.ARTIFACT_DELETED: "[-DEL]",
            EventType.PROPOSAL_CREATED: "[PROPOSAL]",
            EventType.INSIGHT_GENERATED: "[INSIGHT]",
            EventType.SUGGESTION_CREATED: "[SUGGEST]",
            EventType.SYSTEM_ALERT: "[ALERT]"
        }
        return icons.get(event_type, "[EVENT]")

    def _get_severity_icon(self, severity: Severity) -> str:
        """Get icon for severity"""
        icons = {
            Severity.DEBUG: "[DBG]",
            Severity.INFO: "[INFO]",
            Severity.WARNING: "[WARN]",
            Severity.ERROR: "[ERR]",
            Severity.CRITICAL: "[CRIT]"
        }
        return icons.get(severity, "[?]")
