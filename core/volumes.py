"""
Git-Integrated Volume System for LLMos-Lite

Volumes are Git repositories containing Skills and Memory (traces).
This enables:
- Version control of all artifacts
- Pull requests for promoting User → Team → System
- Distributed collaboration on skills
- Rollback capabilities

Volume Hierarchy:
- SystemVolume: /volumes/system (read-only for users)
- TeamVolume: /volumes/teams/{team_id} (shared by team members)
- UserVolume: /volumes/users/{user_id} (private workspace)
"""

from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum
import json
import subprocess


class VolumeType(Enum):
    """Types of volumes"""
    SYSTEM = "system"
    TEAM = "team"
    USER = "user"


class ArtifactType(Enum):
    """Types of artifacts in volumes"""
    SKILL = "skill"
    TRACE = "trace"
    MEMORY = "memory"


class GitVolume:
    """
    A Git-backed volume for storing skills and traces.

    Structure:
    /volume_root/
        skills/           # Markdown skill definitions
        traces/           # Execution history
        memory/           # Consolidated memory/context
        .git/             # Git repository
        metadata.json     # Volume metadata
    """

    def __init__(
        self,
        volume_type: VolumeType,
        base_path: Path,
        owner_id: str,
        readonly: bool = False
    ):
        self.volume_type = volume_type
        self.base_path = Path(base_path)
        self.owner_id = owner_id
        self.readonly = readonly

        # Subdirectories
        self.skills_path = self.base_path / "skills"
        self.traces_path = self.base_path / "traces"
        self.memory_path = self.base_path / "memory"
        self.metadata_path = self.base_path / "metadata.json"

        # Initialize
        self._ensure_structure()
        self._init_git_if_needed()

    def _ensure_structure(self):
        """Create directory structure"""
        for path in [self.skills_path, self.traces_path, self.memory_path]:
            path.mkdir(parents=True, exist_ok=True)

        # Create metadata if not exists
        if not self.metadata_path.exists():
            self._save_metadata({
                "volume_type": self.volume_type.value,
                "owner_id": self.owner_id,
                "created_at": datetime.now().isoformat(),
                "version": "1.0"
            })

    def _init_git_if_needed(self):
        """Initialize Git repository if not exists"""
        git_dir = self.base_path / ".git"

        if not git_dir.exists():
            try:
                subprocess.run(
                    ["git", "init"],
                    cwd=self.base_path,
                    capture_output=True,
                    check=True
                )
                subprocess.run(
                    ["git", "add", "."],
                    cwd=self.base_path,
                    capture_output=True,
                    check=True
                )
                subprocess.run(
                    ["git", "commit", "-m", "Initial volume"],
                    cwd=self.base_path,
                    capture_output=True,
                    check=True
                )
                print(f"✓ Git repository initialized: {self.base_path}")
            except subprocess.CalledProcessError as e:
                print(f"Warning: Could not initialize Git: {e}")

    def _save_metadata(self, data: Dict):
        """Save metadata to JSON"""
        with open(self.metadata_path, 'w') as f:
            json.dump(data, f, indent=2)

    def _load_metadata(self) -> Dict:
        """Load metadata from JSON"""
        if self.metadata_path.exists():
            with open(self.metadata_path, 'r') as f:
                return json.load(f)
        return {}

    # =========================================================================
    # SKILL OPERATIONS
    # =========================================================================

    def list_skills(self) -> List[str]:
        """List all skill IDs (filenames without .md)"""
        return [f.stem for f in self.skills_path.glob("*.md")]

    def read_skill(self, skill_id: str) -> Optional[str]:
        """Read a skill's content"""
        skill_file = self.skills_path / f"{skill_id}.md"
        if skill_file.exists():
            return skill_file.read_text()
        return None

    def write_skill(self, skill_id: str, content: str, commit_message: str = None) -> bool:
        """Write a skill and optionally commit"""
        if self.readonly:
            return False

        skill_file = self.skills_path / f"{skill_id}.md"
        skill_file.write_text(content)

        # Auto-commit if message provided
        if commit_message:
            self.commit_changes(commit_message, f"{self.owner_id}-cron")

        return True

    def delete_skill(self, skill_id: str, commit_message: str = None) -> bool:
        """Delete a skill"""
        if self.readonly:
            return False

        skill_file = self.skills_path / f"{skill_id}.md"
        if skill_file.exists():
            skill_file.unlink()

            if commit_message:
                self.commit_changes(commit_message, f"{self.owner_id}-cron")

            return True
        return False

    # =========================================================================
    # TRACE OPERATIONS
    # =========================================================================

    def list_traces(self, limit: Optional[int] = None) -> List[str]:
        """List all trace IDs, sorted by modification time"""
        traces = sorted(
            self.traces_path.glob("*.md"),
            key=lambda f: f.stat().st_mtime,
            reverse=True
        )

        if limit:
            traces = traces[:limit]

        return [f.stem for f in traces]

    def read_trace(self, trace_id: str) -> Optional[str]:
        """Read a trace's content"""
        trace_file = self.traces_path / f"{trace_id}.md"
        if trace_file.exists():
            return trace_file.read_text()
        return None

    def write_trace(self, trace_id: str, content: str) -> bool:
        """Write a trace (no auto-commit for performance)"""
        if self.readonly:
            return False

        trace_file = self.traces_path / f"{trace_id}.md"
        trace_file.write_text(content)
        return True

    def delete_trace(self, trace_id: str) -> bool:
        """Delete a trace"""
        if self.readonly:
            return False

        trace_file = self.traces_path / f"{trace_id}.md"
        if trace_file.exists():
            trace_file.unlink()
            return True
        return False

    # =========================================================================
    # GIT OPERATIONS
    # =========================================================================

    def commit_changes(self, message: str, author: str):
        """Commit all changes to Git"""
        if self.readonly:
            return

        try:
            subprocess.run(
                ["git", "add", "."],
                cwd=self.base_path,
                capture_output=True,
                check=True
            )
            subprocess.run(
                ["git", "commit", "-m", message, f"--author={author} <{author}@llmos>"],
                cwd=self.base_path,
                capture_output=True,
                check=True
            )
            print(f"✓ Committed: {message}")
        except subprocess.CalledProcessError:
            # No changes to commit (OK)
            pass

    def get_git_log(self, limit: int = 10) -> List[Dict]:
        """Get recent Git commits"""
        try:
            result = subprocess.run(
                ["git", "log", f"-{limit}", "--pretty=format:%H|%an|%at|%s"],
                cwd=self.base_path,
                capture_output=True,
                text=True,
                check=True
            )

            commits = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    hash_val, author, timestamp, message = line.split('|', 3)
                    commits.append({
                        "hash": hash_val,
                        "author": author,
                        "timestamp": int(timestamp),
                        "message": message
                    })

            return commits
        except subprocess.CalledProcessError:
            return []

    def create_branch(self, branch_name: str) -> bool:
        """Create a new Git branch"""
        try:
            subprocess.run(
                ["git", "checkout", "-b", branch_name],
                cwd=self.base_path,
                capture_output=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError:
            return False

    # =========================================================================
    # STATISTICS
    # =========================================================================

    def get_stats(self) -> Dict:
        """Get volume statistics"""
        return {
            "volume_type": self.volume_type.value,
            "owner_id": self.owner_id,
            "skill_count": len(self.list_skills()),
            "trace_count": len(self.list_traces()),
            "readonly": self.readonly,
            "recent_commits": len(self.get_git_log(limit=10))
        }


class VolumeManager:
    """
    Manages all volumes in the system.

    Provides access control:
    - User can read/write own volume, read team + system
    - Team crons can read/write team volume, read system
    - System cron can read/write all volumes
    """

    def __init__(self, base_path: Path):
        self.base_path = Path(base_path)
        self._volumes: Dict[str, GitVolume] = {}

        # Ensure structure
        (self.base_path / "system").mkdir(parents=True, exist_ok=True)
        (self.base_path / "teams").mkdir(parents=True, exist_ok=True)
        (self.base_path / "users").mkdir(parents=True, exist_ok=True)

    def get_system_volume(self, readonly: bool = True) -> GitVolume:
        """Get the system-wide volume"""
        key = "system"
        if key not in self._volumes:
            self._volumes[key] = GitVolume(
                volume_type=VolumeType.SYSTEM,
                base_path=self.base_path / "system",
                owner_id="system",
                readonly=readonly
            )
        return self._volumes[key]

    def get_team_volume(self, team_id: str, readonly: bool = True) -> GitVolume:
        """Get a team's volume"""
        key = f"team:{team_id}"
        if key not in self._volumes:
            self._volumes[key] = GitVolume(
                volume_type=VolumeType.TEAM,
                base_path=self.base_path / "teams" / team_id,
                owner_id=team_id,
                readonly=readonly
            )
        return self._volumes[key]

    def get_user_volume(self, user_id: str, readonly: bool = False) -> GitVolume:
        """Get a user's volume"""
        key = f"user:{user_id}"
        if key not in self._volumes:
            self._volumes[key] = GitVolume(
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

    def promote_skill(
        self,
        skill_id: str,
        from_volume: GitVolume,
        to_volume: GitVolume,
        reason: str
    ) -> bool:
        """
        Promote a skill from one volume to another.

        This is like a "Pull Request":
        - Read skill from source
        - Write to target
        - Commit with reason
        """
        content = from_volume.read_skill(skill_id)
        if not content:
            return False

        success = to_volume.write_skill(
            skill_id,
            content,
            commit_message=f"Promote '{skill_id}' from {from_volume.volume_type.value}: {reason}"
        )

        return success
