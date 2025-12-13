"""
Skills System for LLMos-Lite

Skills replace the concept of "Tools" or "Agents" in the original llmos.
A Skill is simply a Markdown file that contains instructions, patterns,
or best practices that get injected into the LLM's context.

This aligns with the OpenAI/Anthropic "Skills" paradigm:
- Skills are human-readable Markdown
- Skills are version-controlled (Git)
- Skills can be shared across users/teams
- Skills are loaded on-demand based on context

Skill Format:
---
name: skill-name
category: coding|analysis|writing|data
description: What this skill helps with
keywords: [python, testing, pytest]
---

# Skill: [Name]

## When to Use
[Description of when this skill applies]

## Approach
[Step-by-step approach or best practices]

## Example
[Code or example demonstrating the skill]
"""

from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
import re


@dataclass
class Skill:
    """
    A skill loaded from a Markdown file.

    Skills are context that gets injected into the LLM to guide behavior.
    """
    name: str
    category: str
    description: str
    keywords: List[str]
    content: str  # Full markdown content
    volume: str   # "system", "team", or "user"
    file_path: Path

    def to_context_injection(self) -> str:
        """
        Convert skill to LLM context injection.

        This formats the skill for inclusion in the system prompt.
        """
        return f"""
## Available Skill: {self.name}

**Category**: {self.category}
**When to use**: {self.description}

{self.content}
"""

    def matches_keywords(self, query: str) -> bool:
        """Check if skill matches search keywords"""
        query_lower = query.lower()
        return any(kw.lower() in query_lower for kw in self.keywords)


class SkillsManager:
    """
    Manages skills across System, Team, and User volumes.

    The SkillsManager:
    - Loads skills from multiple volumes (layered)
    - Filters skills based on context/keywords
    - Injects relevant skills into LLM context
    - Supports skill creation and evolution
    """

    def __init__(self, volume_manager):
        """
        Initialize skills manager.

        Args:
            volume_manager: VolumeManager instance
        """
        self.volume_manager = volume_manager
        self._cache: Dict[str, List[Skill]] = {}

    def load_skills_for_user(
        self,
        user_id: str,
        team_id: str,
        use_cache: bool = True
    ) -> List[Skill]:
        """
        Load all skills accessible to a user.

        Hierarchy:
        1. System skills (global, read-only)
        2. Team skills (shared by team)
        3. User skills (private)

        Args:
            user_id: User identifier
            team_id: Team identifier
            use_cache: Use cached skills if available

        Returns:
            List of Skill objects
        """
        cache_key = f"{user_id}:{team_id}"

        if use_cache and cache_key in self._cache:
            return self._cache[cache_key]

        skills = []

        # 1. System skills (lowest priority, override by team/user)
        sys_vol = self.volume_manager.get_system_volume(readonly=True)
        skills.extend(self._load_from_volume(sys_vol, "system"))

        # 2. Team skills
        team_vol = self.volume_manager.get_team_volume(team_id, readonly=True)
        skills.extend(self._load_from_volume(team_vol, "team"))

        # 3. User skills (highest priority)
        user_vol = self.volume_manager.get_user_volume(user_id, readonly=False)
        skills.extend(self._load_from_volume(user_vol, "user"))

        # Cache
        self._cache[cache_key] = skills

        return skills

    def _load_from_volume(self, volume, volume_type: str) -> List[Skill]:
        """Load all skills from a volume"""
        skills = []
        skill_ids = volume.list_skills()

        for skill_id in skill_ids:
            content = volume.read_skill(skill_id)
            if content:
                skill = self._parse_skill(
                    skill_id,
                    content,
                    volume_type,
                    volume.skills_path / f"{skill_id}.md"
                )
                if skill:
                    skills.append(skill)

        return skills

    def _parse_skill(
        self,
        skill_id: str,
        content: str,
        volume_type: str,
        file_path: Path
    ) -> Optional[Skill]:
        """
        Parse a skill from Markdown with YAML frontmatter.

        Expected format:
        ---
        name: skill-name
        category: coding
        description: What it does
        keywords: [python, testing]
        ---

        [Skill content in markdown]
        """
        # Check for frontmatter
        if not content.startswith('---'):
            # No frontmatter, create default metadata
            return Skill(
                name=skill_id,
                category="general",
                description="",
                keywords=[],
                content=content,
                volume=volume_type,
                file_path=file_path
            )

        # Split frontmatter and body
        parts = content.split('---', 2)
        if len(parts) < 3:
            return None

        frontmatter = parts[1].strip()
        body = parts[2].strip()

        # Parse frontmatter (simple YAML parsing)
        metadata = {}
        for line in frontmatter.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()

                # Handle lists (simple approach)
                if value.startswith('[') and value.endswith(']'):
                    value = [v.strip().strip('"\'') for v in value[1:-1].split(',')]

                metadata[key] = value

        return Skill(
            name=metadata.get('name', skill_id),
            category=metadata.get('category', 'general'),
            description=metadata.get('description', ''),
            keywords=metadata.get('keywords', []),
            content=body,
            volume=volume_type,
            file_path=file_path
        )

    def filter_skills_by_query(
        self,
        skills: List[Skill],
        query: str,
        max_skills: int = 5
    ) -> List[Skill]:
        """
        Filter skills based on a query string.

        Uses keyword matching to find relevant skills.

        Args:
            skills: List of all available skills
            query: Search query (e.g., user message)
            max_skills: Maximum number of skills to return

        Returns:
            Filtered list of relevant skills
        """
        # Score each skill
        scored_skills = []
        for skill in skills:
            score = 0

            # Check keyword matches
            if skill.matches_keywords(query):
                score += 2

            # Check name match
            if skill.name.lower() in query.lower():
                score += 3

            # Check category match
            if skill.category.lower() in query.lower():
                score += 1

            if score > 0:
                scored_skills.append((skill, score))

        # Sort by score and return top N
        scored_skills.sort(key=lambda x: x[1], reverse=True)
        return [s[0] for s in scored_skills[:max_skills]]

    def create_skill(
        self,
        user_id: str,
        skill_id: str,
        name: str,
        category: str,
        description: str,
        content: str,
        keywords: List[str] = None
    ) -> bool:
        """
        Create a new skill in the user's volume.

        Args:
            user_id: User identifier
            skill_id: Skill identifier (filename without .md)
            name: Human-readable name
            category: Skill category
            description: What the skill does
            content: Skill content (markdown)
            keywords: Keywords for matching

        Returns:
            True if created successfully
        """
        user_vol = self.volume_manager.get_user_volume(user_id)

        # Format as markdown with frontmatter
        keywords_str = "[" + ", ".join(keywords or []) + "]"
        full_content = f"""---
name: {name}
category: {category}
description: {description}
keywords: {keywords_str}
---

{content}
"""

        return user_vol.write_skill(
            skill_id,
            full_content,
            commit_message=f"Create skill: {name}"
        )

    def get_skill(
        self,
        user_id: str,
        team_id: str,
        skill_id: str
    ) -> Optional[Skill]:
        """Get a specific skill by ID"""
        skills = self.load_skills_for_user(user_id, team_id)
        for skill in skills:
            if skill.name == skill_id or skill.file_path.stem == skill_id:
                return skill
        return None

    def build_context_for_query(
        self,
        user_id: str,
        team_id: str,
        query: str,
        max_skills: int = 5
    ) -> str:
        """
        Build LLM context injection for a query.

        This is the main method used by the chat API:
        1. Load all accessible skills
        2. Filter to most relevant
        3. Format for LLM context

        Args:
            user_id: User identifier
            team_id: Team identifier
            query: User's query/message
            max_skills: Maximum skills to include

        Returns:
            Formatted context string for LLM
        """
        # Load all skills
        all_skills = self.load_skills_for_user(user_id, team_id)

        # Filter to relevant
        relevant_skills = self.filter_skills_by_query(all_skills, query, max_skills)

        # Build context
        if not relevant_skills:
            return ""

        context_parts = [
            "# Available Skills",
            "",
            "You have access to the following skills to help solve this task:",
            ""
        ]

        for skill in relevant_skills:
            context_parts.append(skill.to_context_injection())

        return "\n".join(context_parts)

    def clear_cache(self):
        """Clear the skills cache"""
        self._cache.clear()
