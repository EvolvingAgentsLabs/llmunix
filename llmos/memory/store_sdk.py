"""
Memory Store - SDK-based Implementation
Uses Claude Agent SDK's /memories directory structure

Replaces custom vector DB with file-based semantic memory.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from memory.sdk_memory import SDKMemoryTool, MemorySession


class MemoryStore:
    """
    File-based semantic memory using SDK conventions

    Structure:
    /memories/
        traces/         # Execution traces
        projects/       # Project-specific memory
        sessions/       # Session context
        facts/          # Long-term facts
        insights/       # Extracted insights
    """

    def __init__(self, workspace: Path):
        """
        Initialize memory store

        Args:
            workspace: Workspace root directory
        """
        self.workspace = Path(workspace)
        self.memories_dir = self.workspace / "memories"
        self.memories_dir.mkdir(parents=True, exist_ok=True)

        # Initialize SDK Memory Tool
        self.memory_tool = SDKMemoryTool(self.memories_dir)

        # Create standard directories
        self._init_directories()

    def _init_directories(self):
        """Initialize standard memory directories"""
        directories = [
            "traces",
            "projects",
            "sessions",
            "facts",
            "insights"
        ]

        for dir_name in directories:
            (self.memories_dir / dir_name).mkdir(exist_ok=True)

    def store_fact(self, fact: str, category: str = "general") -> bool:
        """
        Store a long-term fact

        Args:
            fact: Fact to store
            category: Fact category

        Returns:
            True if stored successfully
        """
        # Generate fact ID
        fact_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"facts/{category}_{fact_id}.md"

        content = f"""# Fact: {category}

**Stored**: {datetime.now().isoformat()}

## Content

{fact}
"""

        self.memory_tool.create(filename, content)
        return True

    def store_insight(
        self,
        insight: str,
        insight_type: str,
        evidence: List[str],
        confidence: float
    ) -> bool:
        """
        Store an extracted insight

        Args:
            insight: Insight description
            insight_type: Type of insight
            evidence: Supporting evidence
            confidence: Confidence score (0-1)

        Returns:
            True if stored successfully
        """
        insight_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"insights/{insight_type}_{insight_id}.md"

        evidence_md = "\n".join(f"- {e}" for e in evidence)

        content = f"""# Insight: {insight_type}

**Stored**: {datetime.now().isoformat()}
**Confidence**: {confidence:.0%}

## Description

{insight}

## Evidence

{evidence_md}
"""

        self.memory_tool.create(filename, content)
        return True

    def search_facts(self, query: str, limit: int = 5) -> List[str]:
        """
        Search facts by keyword

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of fact contents
        """
        files = self.memory_tool.search(query, directory="facts")

        facts = []
        for file in files[:limit]:
            # Extract content section
            lines = file.content.splitlines()
            content_start = False
            content_lines = []

            for line in lines:
                if line.startswith("## Content"):
                    content_start = True
                    continue
                if content_start and line.strip():
                    content_lines.append(line)

            if content_lines:
                facts.append("\n".join(content_lines))

        return facts

    def get_insights(
        self,
        insight_type: Optional[str] = None,
        min_confidence: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Get stored insights

        Args:
            insight_type: Optional type filter
            min_confidence: Minimum confidence

        Returns:
            List of insight dictionaries
        """
        pattern = f"{insight_type}_*.md" if insight_type else "*.md"
        files = self.memory_tool.list_files("insights", pattern=pattern)

        insights = []
        for file in files:
            # Parse insight
            lines = file.content.splitlines()
            metadata = {}
            description = ""
            evidence = []

            current_section = None
            for line in lines:
                if line.startswith("**") and "**:" in line:
                    key, value = line.split("**:", 1)
                    key = key.strip("* ")
                    metadata[key] = value.strip()
                elif line.startswith("## Description"):
                    current_section = "description"
                elif line.startswith("## Evidence"):
                    current_section = "evidence"
                elif current_section == "description" and line.strip():
                    description = line.strip()
                elif current_section == "evidence" and line.startswith("- "):
                    evidence.append(line[2:].strip())

            confidence = float(metadata.get("Confidence", "0%").rstrip('%')) / 100.0

            if confidence >= min_confidence:
                insights.append({
                    "type": insight_type or "general",
                    "description": description,
                    "evidence": evidence,
                    "confidence": confidence,
                    "stored_at": metadata.get("Stored", "")
                })

        return insights

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get memory statistics

        Returns:
            Dictionary with memory stats
        """
        facts_count = len(self.memory_tool.list_files("facts"))
        insights_count = len(self.memory_tool.list_files("insights"))
        sessions_count = len(list((self.memories_dir / "sessions").iterdir())) if (self.memories_dir / "sessions").exists() else 0

        return {
            "facts_count": facts_count,
            "insights_count": insights_count,
            "sessions_count": sessions_count,
            "total_files": facts_count + insights_count
        }

    def cleanup_old_sessions(self, days: int = 30):
        """
        Clean up old session files

        Args:
            days: Age threshold in days
        """
        sessions_dir = self.memories_dir / "sessions"

        if not sessions_dir.exists():
            return

        threshold = datetime.now().timestamp() - (days * 24 * 60 * 60)

        for session_path in sessions_dir.iterdir():
            if session_path.is_dir():
                if session_path.stat().st_mtime < threshold:
                    # Delete old session
                    for file in session_path.glob("*"):
                        file.unlink()
                    session_path.rmdir()
