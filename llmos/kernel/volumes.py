"""
Volume Architecture for LLM OS

Volumes are the organizational units for artifacts in the system. Each volume
contains traces, tools, and agents that belong to a specific scope:

- **UserVolume**: Personal artifacts for a single user
- **TeamVolume**: Shared artifacts for a team of users
- **SystemVolume**: Global artifacts available to all

Access Control:
- User Cron: read/write UserVolume, read TeamVolume
- Team Cron: read/write TeamVolume, read UserVolume (aggregated)
- System Cron: read/write all volumes, controls other crons

Artifacts in each volume:
- Traces: Execution histories (can be summarized/consolidated)
- Tools: Crystallized capabilities (can evolve)
- Agents: Markdown agent definitions (can be refined)
- Insights: Summarized learnings from analysis
- Suggestions: Opportunities for improvement
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Set
from pathlib import Path
from enum import Enum
from datetime import datetime
import json
import hashlib


class VolumeType(Enum):
    """Types of volumes in the system"""
    USER = "user"
    TEAM = "team"
    SYSTEM = "system"


class ArtifactType(Enum):
    """Types of artifacts stored in volumes"""
    TRACE = "trace"
    TOOL = "tool"
    AGENT = "agent"
    INSIGHT = "insight"
    SUGGESTION = "suggestion"


class ArtifactAction(Enum):
    """Actions that can be performed on artifacts"""
    CREATED = "created"
    EVOLVED = "evolved"
    SUMMARIZED = "summarized"
    PROMOTED = "promoted"  # User -> Team or Team -> System
    DEPRECATED = "deprecated"
    DELETED = "deleted"


@dataclass
class ArtifactChange:
    """Record of a change to an artifact"""
    artifact_id: str
    artifact_type: ArtifactType
    action: ArtifactAction
    timestamp: str
    source_volume: VolumeType
    target_volume: Optional[VolumeType]  # For promotions
    reason: str
    cron_level: str  # "user", "team", or "system"
    details: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "artifact_type": self.artifact_type.value,
            "action": self.action.value,
            "timestamp": self.timestamp,
            "source_volume": self.source_volume.value,
            "target_volume": self.target_volume.value if self.target_volume else None,
            "reason": self.reason,
            "cron_level": self.cron_level,
            "details": self.details
        }


@dataclass
class VolumeStats:
    """Statistics about a volume's contents"""
    trace_count: int = 0
    tool_count: int = 0
    agent_count: int = 0
    insight_count: int = 0
    suggestion_count: int = 0
    total_size_bytes: int = 0
    last_modified: Optional[str] = None

    def as_dict(self) -> Dict[str, Any]:
        return {
            "trace_count": self.trace_count,
            "tool_count": self.tool_count,
            "agent_count": self.agent_count,
            "insight_count": self.insight_count,
            "suggestion_count": self.suggestion_count,
            "total_size_bytes": self.total_size_bytes,
            "last_modified": self.last_modified
        }


class Volume:
    """
    A volume containing artifacts (traces, tools, agents, insights, suggestions).

    Volumes are file-based storage units that can be read and written
    according to access control rules.
    """

    def __init__(
        self,
        volume_type: VolumeType,
        base_path: Path,
        owner_id: str,  # user_id, team_id, or "system"
        readonly: bool = False
    ):
        self.volume_type = volume_type
        self.base_path = base_path
        self.owner_id = owner_id
        self.readonly = readonly

        # Artifact subdirectories
        self.traces_path = base_path / "traces"
        self.tools_path = base_path / "tools"
        self.agents_path = base_path / "agents"
        self.insights_path = base_path / "insights"
        self.suggestions_path = base_path / "suggestions"

        # Change log
        self.changelog_path = base_path / "changelog.json"
        self._changes: List[ArtifactChange] = []

        # Ensure directories exist
        self._ensure_directories()
        self._load_changelog()

    def _ensure_directories(self):
        """Create volume directories if they don't exist"""
        for path in [self.traces_path, self.tools_path, self.agents_path,
                     self.insights_path, self.suggestions_path]:
            path.mkdir(parents=True, exist_ok=True)

    def _load_changelog(self):
        """Load change history from disk"""
        if self.changelog_path.exists():
            try:
                with open(self.changelog_path, 'r') as f:
                    data = json.load(f)
                    self._changes = [
                        ArtifactChange(
                            artifact_id=c["artifact_id"],
                            artifact_type=ArtifactType(c["artifact_type"]),
                            action=ArtifactAction(c["action"]),
                            timestamp=c["timestamp"],
                            source_volume=VolumeType(c["source_volume"]),
                            target_volume=VolumeType(c["target_volume"]) if c.get("target_volume") else None,
                            reason=c["reason"],
                            cron_level=c["cron_level"],
                            details=c.get("details", {})
                        )
                        for c in data
                    ]
            except Exception:
                self._changes = []

    def _save_changelog(self):
        """Save change history to disk"""
        if not self.readonly:
            with open(self.changelog_path, 'w') as f:
                json.dump([c.as_dict() for c in self._changes[-1000:]], f, indent=2)

    def _get_path_for_type(self, artifact_type: ArtifactType) -> Path:
        """Get the directory path for an artifact type"""
        mapping = {
            ArtifactType.TRACE: self.traces_path,
            ArtifactType.TOOL: self.tools_path,
            ArtifactType.AGENT: self.agents_path,
            ArtifactType.INSIGHT: self.insights_path,
            ArtifactType.SUGGESTION: self.suggestions_path
        }
        return mapping[artifact_type]

    def record_change(
        self,
        artifact_id: str,
        artifact_type: ArtifactType,
        action: ArtifactAction,
        reason: str,
        cron_level: str,
        target_volume: Optional[VolumeType] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Record a change to an artifact"""
        change = ArtifactChange(
            artifact_id=artifact_id,
            artifact_type=artifact_type,
            action=action,
            timestamp=datetime.now().isoformat(),
            source_volume=self.volume_type,
            target_volume=target_volume,
            reason=reason,
            cron_level=cron_level,
            details=details or {}
        )
        self._changes.append(change)
        self._save_changelog()
        return change

    # =========================================================================
    # READ OPERATIONS
    # =========================================================================

    def list_artifacts(self, artifact_type: ArtifactType) -> List[str]:
        """List all artifact IDs of a given type"""
        path = self._get_path_for_type(artifact_type)

        if artifact_type in [ArtifactType.TRACE, ArtifactType.INSIGHT, ArtifactType.SUGGESTION]:
            # Markdown files
            return [f.stem for f in path.glob("*.md")]
        elif artifact_type == ArtifactType.TOOL:
            # Python files
            return [f.stem for f in path.glob("*.py")]
        elif artifact_type == ArtifactType.AGENT:
            # Markdown files
            return [f.stem for f in path.glob("*.md")]
        return []

    def read_artifact(self, artifact_type: ArtifactType, artifact_id: str) -> Optional[str]:
        """Read an artifact's content"""
        path = self._get_path_for_type(artifact_type)

        if artifact_type in [ArtifactType.TRACE, ArtifactType.INSIGHT,
                             ArtifactType.SUGGESTION, ArtifactType.AGENT]:
            file_path = path / f"{artifact_id}.md"
        elif artifact_type == ArtifactType.TOOL:
            file_path = path / f"{artifact_id}.py"
        else:
            return None

        if file_path.exists():
            return file_path.read_text()
        return None

    def get_stats(self) -> VolumeStats:
        """Get statistics about the volume"""
        stats = VolumeStats()

        stats.trace_count = len(self.list_artifacts(ArtifactType.TRACE))
        stats.tool_count = len(self.list_artifacts(ArtifactType.TOOL))
        stats.agent_count = len(self.list_artifacts(ArtifactType.AGENT))
        stats.insight_count = len(self.list_artifacts(ArtifactType.INSIGHT))
        stats.suggestion_count = len(self.list_artifacts(ArtifactType.SUGGESTION))

        # Calculate total size
        total_size = 0
        for path in [self.traces_path, self.tools_path, self.agents_path,
                     self.insights_path, self.suggestions_path]:
            for f in path.iterdir():
                if f.is_file():
                    total_size += f.stat().st_size
        stats.total_size_bytes = total_size

        # Get last modified
        if self._changes:
            stats.last_modified = self._changes[-1].timestamp

        return stats

    def get_recent_changes(self, limit: int = 50) -> List[ArtifactChange]:
        """Get recent changes to the volume"""
        return self._changes[-limit:]

    # =========================================================================
    # WRITE OPERATIONS
    # =========================================================================

    def write_artifact(
        self,
        artifact_type: ArtifactType,
        artifact_id: str,
        content: str,
        reason: str,
        cron_level: str,
        is_new: bool = True
    ) -> bool:
        """Write an artifact to the volume"""
        if self.readonly:
            return False

        path = self._get_path_for_type(artifact_type)

        if artifact_type in [ArtifactType.TRACE, ArtifactType.INSIGHT,
                             ArtifactType.SUGGESTION, ArtifactType.AGENT]:
            file_path = path / f"{artifact_id}.md"
        elif artifact_type == ArtifactType.TOOL:
            file_path = path / f"{artifact_id}.py"
        else:
            return False

        file_path.write_text(content)

        # Record the change
        action = ArtifactAction.CREATED if is_new else ArtifactAction.EVOLVED
        self.record_change(
            artifact_id=artifact_id,
            artifact_type=artifact_type,
            action=action,
            reason=reason,
            cron_level=cron_level
        )

        return True

    def delete_artifact(
        self,
        artifact_type: ArtifactType,
        artifact_id: str,
        reason: str,
        cron_level: str
    ) -> bool:
        """Delete an artifact from the volume"""
        if self.readonly:
            return False

        path = self._get_path_for_type(artifact_type)

        if artifact_type in [ArtifactType.TRACE, ArtifactType.INSIGHT,
                             ArtifactType.SUGGESTION, ArtifactType.AGENT]:
            file_path = path / f"{artifact_id}.md"
        elif artifact_type == ArtifactType.TOOL:
            file_path = path / f"{artifact_id}.py"
        else:
            return False

        if file_path.exists():
            file_path.unlink()
            self.record_change(
                artifact_id=artifact_id,
                artifact_type=artifact_type,
                action=ArtifactAction.DELETED,
                reason=reason,
                cron_level=cron_level
            )
            return True
        return False


class VolumeManager:
    """
    Manages access to User, Team, and System volumes.

    Provides access control based on cron level:
    - user: read/write user volume, read team volume
    - team: read/write team volume, read all user volumes (aggregated)
    - system: read/write all volumes
    """

    def __init__(self, base_path: Path):
        self.base_path = base_path
        self._volumes: Dict[str, Volume] = {}

        # Ensure base structure exists
        (base_path / "system").mkdir(parents=True, exist_ok=True)
        (base_path / "teams").mkdir(parents=True, exist_ok=True)
        (base_path / "users").mkdir(parents=True, exist_ok=True)

    def get_system_volume(self, readonly: bool = False) -> Volume:
        """Get the system-wide volume"""
        key = "system"
        if key not in self._volumes:
            self._volumes[key] = Volume(
                volume_type=VolumeType.SYSTEM,
                base_path=self.base_path / "system",
                owner_id="system",
                readonly=readonly
            )
        return self._volumes[key]

    def get_team_volume(self, team_id: str, readonly: bool = False) -> Volume:
        """Get a team's volume"""
        key = f"team:{team_id}"
        if key not in self._volumes:
            self._volumes[key] = Volume(
                volume_type=VolumeType.TEAM,
                base_path=self.base_path / "teams" / team_id,
                owner_id=team_id,
                readonly=readonly
            )
        return self._volumes[key]

    def get_user_volume(self, user_id: str, readonly: bool = False) -> Volume:
        """Get a user's volume"""
        key = f"user:{user_id}"
        if key not in self._volumes:
            self._volumes[key] = Volume(
                volume_type=VolumeType.USER,
                base_path=self.base_path / "users" / user_id,
                owner_id=user_id,
                readonly=readonly
            )
        return self._volumes[key]

    def list_teams(self) -> List[str]:
        """List all team IDs"""
        teams_path = self.base_path / "teams"
        if teams_path.exists():
            return [d.name for d in teams_path.iterdir() if d.is_dir()]
        return []

    def list_users(self) -> List[str]:
        """List all user IDs"""
        users_path = self.base_path / "users"
        if users_path.exists():
            return [d.name for d in users_path.iterdir() if d.is_dir()]
        return []

    def get_volumes_for_cron(
        self,
        cron_level: str,
        user_id: Optional[str] = None,
        team_id: Optional[str] = None
    ) -> Dict[str, Volume]:
        """
        Get volumes accessible to a cron based on its level.

        Returns dict with keys: 'user', 'team', 'system' (where applicable)
        """
        volumes = {}

        if cron_level == "user":
            # User cron: read/write user, read team
            if user_id:
                volumes["user"] = self.get_user_volume(user_id, readonly=False)
            if team_id:
                volumes["team"] = self.get_team_volume(team_id, readonly=True)

        elif cron_level == "team":
            # Team cron: read/write team, read system
            if team_id:
                volumes["team"] = self.get_team_volume(team_id, readonly=False)
            volumes["system"] = self.get_system_volume(readonly=True)

        elif cron_level == "system":
            # System cron: read/write everything
            volumes["system"] = self.get_system_volume(readonly=False)
            for team_id in self.list_teams():
                volumes[f"team:{team_id}"] = self.get_team_volume(team_id, readonly=False)
            for user_id in self.list_users():
                volumes[f"user:{user_id}"] = self.get_user_volume(user_id, readonly=False)

        return volumes

    def promote_artifact(
        self,
        artifact_type: ArtifactType,
        artifact_id: str,
        from_volume: Volume,
        to_volume: Volume,
        reason: str,
        cron_level: str
    ) -> bool:
        """
        Promote an artifact from one volume to another.

        For example: User trace -> Team trace, or Team tool -> System tool
        """
        content = from_volume.read_artifact(artifact_type, artifact_id)
        if content is None:
            return False

        # Write to target volume
        success = to_volume.write_artifact(
            artifact_type=artifact_type,
            artifact_id=artifact_id,
            content=content,
            reason=f"Promoted from {from_volume.volume_type.value}: {reason}",
            cron_level=cron_level,
            is_new=True
        )

        if success:
            # Record promotion in source volume
            from_volume.record_change(
                artifact_id=artifact_id,
                artifact_type=artifact_type,
                action=ArtifactAction.PROMOTED,
                reason=reason,
                cron_level=cron_level,
                target_volume=to_volume.volume_type
            )

        return success
