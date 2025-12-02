"""
Claude SDK Memory Tool Wrapper
Implements SDK's memory commands for file-based memory management

Based on Claude Agent SDK's Memory Tool features:
- view: Read memory file contents
- create: Create new memory file
- str_replace: Replace string in memory file
- insert: Insert content at line number
- delete: Delete memory file
- rename: Rename memory file

Uses /memories directory structure for persistent storage.
"""

from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import re


@dataclass
class MemoryFile:
    """Represents a memory file"""
    path: Path
    name: str
    content: str
    created_at: datetime
    modified_at: datetime
    size: int


class SDKMemoryTool:
    """
    Claude SDK Memory Tool Wrapper

    Provides file-based memory management aligned with Claude Agent SDK
    conventions. All memory files are stored in /memories directory.
    """

    def __init__(self, memories_dir: Path):
        """
        Initialize SDK Memory Tool

        Args:
            memories_dir: Root /memories directory
        """
        self.memories_dir = Path(memories_dir)
        self.memories_dir.mkdir(parents=True, exist_ok=True)

    def view(self, file_path: str) -> str:
        """
        View contents of a memory file

        Args:
            file_path: Relative path from /memories directory

        Returns:
            File contents as string
        """
        full_path = self.memories_dir / file_path

        if not full_path.exists():
            raise FileNotFoundError(f"Memory file not found: {file_path}")

        return full_path.read_text(encoding='utf-8')

    def create(self, file_path: str, content: str) -> bool:
        """
        Create a new memory file

        Args:
            file_path: Relative path from /memories directory
            content: File content

        Returns:
            True if created successfully
        """
        full_path = self.memories_dir / file_path

        # Create parent directories if needed
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Don't overwrite existing files
        if full_path.exists():
            raise FileExistsError(f"Memory file already exists: {file_path}")

        full_path.write_text(content, encoding='utf-8')
        return True

    def str_replace(
        self,
        file_path: str,
        old_str: str,
        new_str: str,
        count: int = -1
    ) -> bool:
        """
        Replace string in memory file

        Args:
            file_path: Relative path from /memories directory
            old_str: String to replace
            new_str: Replacement string
            count: Max replacements (-1 for all)

        Returns:
            True if replacement successful
        """
        full_path = self.memories_dir / file_path

        if not full_path.exists():
            raise FileNotFoundError(f"Memory file not found: {file_path}")

        content = full_path.read_text(encoding='utf-8')

        if old_str not in content:
            raise ValueError(f"String not found in file: {old_str}")

        new_content = content.replace(old_str, new_str, count)
        full_path.write_text(new_content, encoding='utf-8')

        return True

    def insert(self, file_path: str, line_number: int, content: str) -> bool:
        """
        Insert content at specific line number

        Args:
            file_path: Relative path from /memories directory
            line_number: Line number (1-indexed)
            content: Content to insert

        Returns:
            True if insertion successful
        """
        full_path = self.memories_dir / file_path

        if not full_path.exists():
            raise FileNotFoundError(f"Memory file not found: {file_path}")

        lines = full_path.read_text(encoding='utf-8').splitlines(keepends=True)

        # Convert to 0-indexed
        idx = line_number - 1

        if idx < 0 or idx > len(lines):
            raise ValueError(f"Invalid line number: {line_number}")

        # Insert content
        lines.insert(idx, content + '\n')

        full_path.write_text(''.join(lines), encoding='utf-8')
        return True

    def delete(self, file_path: str) -> bool:
        """
        Delete a memory file

        Args:
            file_path: Relative path from /memories directory

        Returns:
            True if deletion successful
        """
        full_path = self.memories_dir / file_path

        if not full_path.exists():
            raise FileNotFoundError(f"Memory file not found: {file_path}")

        full_path.unlink()
        return True

    def rename(self, old_path: str, new_path: str) -> bool:
        """
        Rename a memory file

        Args:
            old_path: Current relative path
            new_path: New relative path

        Returns:
            True if rename successful
        """
        old_full = self.memories_dir / old_path
        new_full = self.memories_dir / new_path

        if not old_full.exists():
            raise FileNotFoundError(f"Memory file not found: {old_path}")

        if new_full.exists():
            raise FileExistsError(f"Target file already exists: {new_path}")

        # Create parent directories for new path
        new_full.parent.mkdir(parents=True, exist_ok=True)

        old_full.rename(new_full)
        return True

    def list_files(self, directory: str = "", pattern: str = "*.md") -> List[MemoryFile]:
        """
        List memory files in a directory

        Args:
            directory: Subdirectory to search (relative to /memories)
            pattern: Glob pattern for matching files

        Returns:
            List of MemoryFile instances
        """
        search_dir = self.memories_dir / directory if directory else self.memories_dir

        if not search_dir.exists():
            return []

        files = []
        for path in search_dir.glob(pattern):
            if path.is_file():
                stat = path.stat()
                files.append(MemoryFile(
                    path=path,
                    name=path.name,
                    content=path.read_text(encoding='utf-8'),
                    created_at=datetime.fromtimestamp(stat.st_ctime),
                    modified_at=datetime.fromtimestamp(stat.st_mtime),
                    size=stat.st_size
                ))

        return files

    def search(self, query: str, directory: str = "") -> List[MemoryFile]:
        """
        Search memory files by content

        Args:
            query: Search query (supports keywords)
            directory: Subdirectory to search

        Returns:
            List of matching MemoryFile instances
        """
        all_files = self.list_files(directory, pattern="*.md")

        query_lower = query.lower()
        query_words = set(query_lower.split())

        results = []
        for file in all_files:
            content_lower = file.content.lower()

            # Score by keyword matches
            matches = sum(1 for word in query_words if word in content_lower)

            if matches > 0:
                results.append((matches, file))

        # Sort by match count
        results.sort(key=lambda x: x[0], reverse=True)

        return [file for _, file in results]

    def exists(self, file_path: str) -> bool:
        """
        Check if memory file exists

        Args:
            file_path: Relative path from /memories directory

        Returns:
            True if file exists
        """
        full_path = self.memories_dir / file_path
        return full_path.exists()

    def get_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Get metadata for a memory file

        Args:
            file_path: Relative path from /memories directory

        Returns:
            Dictionary with file metadata
        """
        full_path = self.memories_dir / file_path

        if not full_path.exists():
            raise FileNotFoundError(f"Memory file not found: {file_path}")

        stat = full_path.stat()

        return {
            "path": file_path,
            "name": full_path.name,
            "size": stat.st_size,
            "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "lines": len(full_path.read_text(encoding='utf-8').splitlines())
        }


class MemorySession:
    """
    Memory Session Manager

    Manages within-session context and cross-session persistence
    using Claude SDK conventions.
    """

    def __init__(self, memories_dir: Path, session_id: Optional[str] = None):
        """
        Initialize memory session

        Args:
            memories_dir: Root /memories directory
            session_id: Optional session identifier
        """
        self.memories_dir = Path(memories_dir)
        self.session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")

        # Initialize SDK Memory Tool
        self.memory_tool = SDKMemoryTool(self.memories_dir)

        # Session-specific directory
        self.session_dir = self.memories_dir / "sessions" / self.session_id
        self.session_dir.mkdir(parents=True, exist_ok=True)

        # Session context (in-memory)
        self.context: Dict[str, Any] = {}

    def save_session_context(self):
        """Save current session context to file"""
        context_file = self.session_dir / "context.md"

        content_lines = [
            f"# Session Context: {self.session_id}",
            f"Created: {datetime.now().isoformat()}",
            "",
            "## Context Variables",
            ""
        ]

        for key, value in self.context.items():
            content_lines.append(f"- **{key}**: {value}")

        content = "\n".join(content_lines)

        if context_file.exists():
            self.memory_tool.str_replace(
                f"sessions/{self.session_id}/context.md",
                context_file.read_text(),
                content
            )
        else:
            self.memory_tool.create(
                f"sessions/{self.session_id}/context.md",
                content
            )

    def load_session_context(self, session_id: str) -> Dict[str, Any]:
        """
        Load context from previous session

        Args:
            session_id: Session to load from

        Returns:
            Context dictionary
        """
        context_file = f"sessions/{session_id}/context.md"

        if not self.memory_tool.exists(context_file):
            return {}

        content = self.memory_tool.view(context_file)

        # Parse context variables (simple parsing)
        context = {}
        for line in content.splitlines():
            if line.startswith("- **"):
                match = re.match(r"- \*\*(.+?)\*\*: (.+)", line)
                if match:
                    key, value = match.groups()
                    context[key] = value

        return context

    def add_observation(self, observation: str):
        """
        Add observation to session memory

        Args:
            observation: Observation text
        """
        obs_file = f"sessions/{self.session_id}/observations.md"

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"\n## {timestamp}\n\n{observation}\n"

        if self.memory_tool.exists(obs_file):
            # Append to existing file
            content = self.memory_tool.view(obs_file)
            self.memory_tool.str_replace(obs_file, content, content + entry)
        else:
            # Create new file
            self.memory_tool.create(
                obs_file,
                f"# Session Observations: {self.session_id}\n{entry}"
            )

    def get_recent_sessions(self, limit: int = 5) -> List[str]:
        """
        Get recent session IDs

        Args:
            limit: Maximum number of sessions

        Returns:
            List of session IDs
        """
        sessions_dir = self.memories_dir / "sessions"

        if not sessions_dir.exists():
            return []

        # Get all session directories sorted by modification time
        sessions = []
        for session_path in sessions_dir.iterdir():
            if session_path.is_dir():
                sessions.append((session_path.stat().st_mtime, session_path.name))

        sessions.sort(reverse=True)

        return [name for _, name in sessions[:limit]]
