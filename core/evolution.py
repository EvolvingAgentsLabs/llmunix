"""
Evolution Engine for LLMos-Lite

Simplified evolution system that analyzes traces and generates skills.
Removes the "Sentience" complexity from the original llmos.

The Evolution Cron:
1. Analyzes recent traces
2. Detects repeated patterns
3. Generates draft skills
4. Commits to Git

Runs at 3 levels:
- UserCron: Analyzes user's traces, creates personal skills
- TeamCron: Consolidates team patterns, promotes skills
- SystemCron: Manages global skills library
"""

from pathlib import Path
from typing import List, Dict, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
import hashlib
import re
import asyncio


@dataclass
class Pattern:
    """A detected pattern in traces"""
    signature: str  # Hash of normalized pattern
    description: str
    trace_ids: List[str]
    count: int
    success_rate: float
    example_content: str


@dataclass
class SkillDraft:
    """A draft skill generated from patterns"""
    skill_id: str
    name: str
    category: str
    description: str
    content: str
    keywords: List[str]
    source_traces: List[str]
    confidence: float


class PatternDetector:
    """
    Detects repeated patterns in execution traces.

    Uses simple heuristics:
    - Goal similarity (hash-based)
    - Tool sequence similarity
    - Success rate
    """

    def __init__(self):
        pass

    def analyze_traces(self, traces: List[tuple]) -> List[Pattern]:
        """
        Analyze traces and detect patterns.

        Args:
            traces: List of (trace_id, content) tuples

        Returns:
            List of detected patterns
        """
        # Group traces by goal signature
        goal_groups: Dict[str, List[tuple]] = {}

        for trace_id, content in traces:
            goal = self._extract_goal(content)
            if goal:
                signature = self._compute_signature(goal)

                if signature not in goal_groups:
                    goal_groups[signature] = []

                goal_groups[signature].append((trace_id, content))

        # Convert groups to patterns
        patterns = []
        for signature, group_traces in goal_groups.items():
            if len(group_traces) >= 2:  # At least 2 occurrences
                success_rate = self._calculate_success_rate(group_traces)
                pattern = Pattern(
                    signature=signature,
                    description=self._extract_goal(group_traces[0][1]) or "Unknown pattern",
                    trace_ids=[t[0] for t in group_traces],
                    count=len(group_traces),
                    success_rate=success_rate,
                    example_content=group_traces[0][1][:500]
                )
                patterns.append(pattern)

        # Sort by count (most frequent first)
        patterns.sort(key=lambda p: p.count, reverse=True)
        return patterns

    def _extract_goal(self, content: str) -> Optional[str]:
        """Extract goal from trace content"""
        # Look for title
        match = re.search(r'^# Execution Trace: (.+?)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()

        # Fallback: look for goal_text in metadata
        match = re.search(r'goal_text:\s*(.+?)(?:\n|$)', content)
        if match:
            return match.group(1).strip()

        return None

    def _compute_signature(self, text: str) -> str:
        """Compute signature for pattern matching"""
        # Normalize: lowercase, remove punctuation, collapse whitespace
        normalized = re.sub(r'[^\w\s]', '', text.lower())
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]

    def _calculate_success_rate(self, traces: List[tuple]) -> float:
        """Calculate success rate from traces"""
        successes = 0
        for _, content in traces:
            # Look for success indicators
            if 'success_rating: 0.9' in content or 'success_rating: 1' in content:
                successes += 1
            elif 'Success Rating**: 90%' in content or 'Success Rating**: 100%' in content:
                successes += 1

        return successes / len(traces) if traces else 0.0


class SkillGenerator:
    """
    Generates skills from detected patterns.

    Can work with or without LLM:
    - With LLM: Generates detailed, contextual skills
    - Without LLM: Uses templates and heuristics
    """

    def __init__(self, llm_callback: Optional[Callable] = None):
        """
        Initialize skill generator.

        Args:
            llm_callback: Optional async function(prompt) -> response
        """
        self.llm_callback = llm_callback

    async def generate_skill_from_pattern(self, pattern: Pattern) -> SkillDraft:
        """
        Generate a skill from a detected pattern.

        Args:
            pattern: Detected pattern

        Returns:
            SkillDraft
        """
        if self.llm_callback:
            return await self._llm_generate(pattern)
        else:
            return self._heuristic_generate(pattern)

    async def _llm_generate(self, pattern: Pattern) -> SkillDraft:
        """Generate skill using LLM"""
        prompt = f"""You are creating a reusable "Skill" (best practice guide) from a repeated pattern.

Pattern detected:
- Goal: {pattern.description}
- Seen {pattern.count} times
- Success rate: {pattern.success_rate:.0%}

Example trace:
{pattern.example_content}

Create a Skill in this format:

**Skill Name**: [Short, descriptive name]
**Category**: [coding|analysis|writing|data]
**Description**: [One-line description of when to use this skill]
**Keywords**: [Comma-separated keywords for search]

**Approach**:
1. [Step 1]
2. [Step 2]
...

**Example**:
[Code or example if applicable]

Generate the skill now:"""

        try:
            response = await self.llm_callback(prompt)

            # Parse LLM response
            skill_id = f"skill_{pattern.signature}"
            name = self._extract_field(response, "Skill Name") or pattern.description[:50]
            category = self._extract_field(response, "Category") or "general"
            description = self._extract_field(response, "Description") or pattern.description
            keywords_str = self._extract_field(response, "Keywords") or ""
            keywords = [k.strip() for k in keywords_str.split(',') if k.strip()]

            return SkillDraft(
                skill_id=skill_id,
                name=name,
                category=category,
                description=description,
                content=response,
                keywords=keywords,
                source_traces=pattern.trace_ids,
                confidence=pattern.success_rate
            )

        except Exception as e:
            print(f"LLM generation failed: {e}, falling back to heuristic")
            return self._heuristic_generate(pattern)

    def _heuristic_generate(self, pattern: Pattern) -> SkillDraft:
        """Generate skill using heuristics (no LLM)"""
        skill_id = f"skill_{pattern.signature}"

        # Extract category from goal
        category = "general"
        goal_lower = pattern.description.lower()
        if any(kw in goal_lower for kw in ["code", "script", "program", "python"]):
            category = "coding"
        elif any(kw in goal_lower for kw in ["analyze", "data", "statistics"]):
            category = "analysis"
        elif any(kw in goal_lower for kw in ["write", "document", "report"]):
            category = "writing"

        # Generate simple content
        content = f"""# Skill: {pattern.description}

## When to Use
Use this skill when you need to: {pattern.description.lower()}

## Approach
This pattern was successful {pattern.count} times with {pattern.success_rate:.0%} success rate.

Based on the traces, follow these steps:
1. Understand the specific requirements
2. Apply the learned approach from previous successful executions
3. Verify the outcome

## Notes
This skill was auto-generated from {pattern.count} similar traces.
Review and refine as needed.
"""

        keywords = [w.lower() for w in pattern.description.split() if len(w) > 3][:5]

        return SkillDraft(
            skill_id=skill_id,
            name=pattern.description[:50],
            category=category,
            description=f"Handle tasks like: {pattern.description}",
            content=content,
            keywords=keywords,
            source_traces=pattern.trace_ids,
            confidence=pattern.success_rate
        )

    def _extract_field(self, text: str, field_name: str) -> Optional[str]:
        """Extract a field from LLM response"""
        pattern = rf'\*\*{field_name}\*\*:\s*(.+?)(?:\n|$)'
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
        return None


class EvolutionCron:
    """
    Evolution Cron that analyzes traces and generates skills.

    This is a simplified version of the original SentienceCron,
    focused purely on pattern detection and skill generation.
    """

    def __init__(
        self,
        volume_manager,
        llm_callback: Optional[Callable] = None,
        min_pattern_count: int = 3,
        min_success_rate: float = 0.7
    ):
        """
        Initialize evolution cron.

        Args:
            volume_manager: VolumeManager instance
            llm_callback: Optional LLM function for skill generation
            min_pattern_count: Minimum occurrences to create skill
            min_success_rate: Minimum success rate to create skill
        """
        self.volume_manager = volume_manager
        self.pattern_detector = PatternDetector()
        self.skill_generator = SkillGenerator(llm_callback)
        self.min_pattern_count = min_pattern_count
        self.min_success_rate = min_success_rate

    async def run_user_evolution(self, user_id: str, team_id: str) -> Dict:
        """
        Run evolution for a user.

        Analyzes user's traces and generates draft skills.

        Args:
            user_id: User identifier
            team_id: Team identifier (for context)

        Returns:
            Dictionary with evolution results
        """
        user_vol = self.volume_manager.get_user_volume(user_id)

        # 1. Load recent traces
        trace_ids = user_vol.list_traces(limit=100)
        traces = []
        for trace_id in trace_ids:
            content = user_vol.read_trace(trace_id)
            if content:
                traces.append((trace_id, content))

        if not traces:
            return {"status": "no_traces", "skills_created": 0}

        # 2. Detect patterns
        patterns = self.pattern_detector.analyze_traces(traces)

        # 3. Filter patterns (min count + success rate)
        viable_patterns = [
            p for p in patterns
            if p.count >= self.min_pattern_count and p.success_rate >= self.min_success_rate
        ]

        # 4. Generate skills from patterns
        skills_created = 0
        for pattern in viable_patterns:
            skill_draft = await self.skill_generator.generate_skill_from_pattern(pattern)

            # Save as skill in user volume
            success = user_vol.write_skill(
                skill_draft.skill_id,
                self._format_skill(skill_draft),
                commit_message=f"Evolution: Create skill '{skill_draft.name}' from {pattern.count} traces"
            )

            if success:
                skills_created += 1

        return {
            "status": "completed",
            "traces_analyzed": len(traces),
            "patterns_detected": len(patterns),
            "viable_patterns": len(viable_patterns),
            "skills_created": skills_created
        }

    async def run_team_evolution(self, team_id: str) -> Dict:
        """
        Run evolution for a team.

        Analyzes team-level patterns and consolidates skills.

        Args:
            team_id: Team identifier

        Returns:
            Dictionary with evolution results
        """
        team_vol = self.volume_manager.get_team_volume(team_id, readonly=False)

        # Get all user volumes in team
        user_ids = self.volume_manager.list_users()

        # Collect skills from all users (simplified - would need user-team mapping)
        all_patterns = []

        # For now, just analyze team traces
        trace_ids = team_vol.list_traces(limit=200)
        traces = []
        for trace_id in trace_ids:
            content = team_vol.read_trace(trace_id)
            if content:
                traces.append((trace_id, content))

        if traces:
            patterns = self.pattern_detector.analyze_traces(traces)
            all_patterns.extend(patterns)

        # Generate team skills
        skills_created = 0
        for pattern in all_patterns:
            if pattern.count >= 5:  # Higher threshold for team skills
                skill_draft = await self.skill_generator.generate_skill_from_pattern(pattern)

                team_vol.write_skill(
                    skill_draft.skill_id,
                    self._format_skill(skill_draft),
                    commit_message=f"Team Evolution: {skill_draft.name}"
                )
                skills_created += 1

        return {
            "status": "completed",
            "team_skills_created": skills_created
        }

    def _format_skill(self, draft: SkillDraft) -> str:
        """Format skill draft as markdown with frontmatter"""
        keywords_str = "[" + ", ".join(draft.keywords) + "]"

        return f"""---
name: {draft.name}
category: {draft.category}
description: {draft.description}
keywords: {keywords_str}
source_traces: {len(draft.source_traces)}
confidence: {draft.confidence:.2f}
created_at: {datetime.now().isoformat()}
---

{draft.content}
"""
