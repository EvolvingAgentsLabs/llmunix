"""
LLM-Based Trace Analyzer - Semantic trace matching using Claude Agent SDK

Replaces brittle hash-based matching with intelligent semantic analysis.
Implements "soft" associative memory as described in Nested Learning paper.
"""

import json
import asyncio
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
from dataclasses import dataclass

try:
    from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions
except ImportError:
    print("Warning: claude-agent-sdk not installed. Install with: pip install claude-agent-sdk")
    ClaudeSDKClient = None
    ClaudeAgentOptions = None


@dataclass
class TraceMatch:
    """Result of trace matching analysis"""
    trace_signature: str
    goal_text: str
    confidence: float  # 0.0 to 1.0
    reasoning: str  # Why this trace matches
    recommended_mode: str  # "FOLLOWER", "MIXED", or "LEARNER"


class TraceAnalyzer:
    """
    LLM-Based Trace Analyzer

    Uses Claude Agent SDK to perform semantic analysis of goal-to-trace matching.

    This implements "soft" associative memory:
    - Hash matching: "create file" ≠ "create a file" (fails)
    - LLM matching: "create file" ≈ "create a file" (succeeds with confidence score)

    Confidence thresholds:
    - ≥0.92: High confidence → FOLLOWER mode (direct replay)
    - 0.75-0.92: Medium confidence → MIXED mode (trace as few-shot)
    - <0.75: Low confidence → LEARNER mode (full reasoning)
    """

    def __init__(
        self,
        workspace: Path,
        model: str = "claude-sonnet-4-5-20250929"
    ):
        """
        Initialize TraceAnalyzer

        Args:
            workspace: Workspace directory
            model: Claude model to use
        """
        self.workspace = Path(workspace)
        self.model = model

        if ClaudeSDKClient is None:
            raise RuntimeError(
                "Claude Agent SDK not installed. "
                "Install with: pip install claude-agent-sdk"
            )

    async def analyze_goal_similarity(
        self,
        goal: str,
        trace_goal: str,
        trace_metadata: Dict[str, Any]
    ) -> float:
        """
        Analyze semantic similarity between goal and trace goal

        Uses Claude to understand if goals are functionally equivalent,
        even if worded differently.

        Args:
            goal: Current goal
            trace_goal: Goal from existing trace
            trace_metadata: Additional trace metadata (success rate, usage count, etc.)

        Returns:
            Confidence score (0.0 to 1.0)
        """
        analysis_prompt = f"""Analyze if these two goals are semantically similar enough to use the same execution strategy.

Current Goal:
"{goal}"

Previous Goal (from execution trace):
"{trace_goal}"

Trace Metadata:
- Success Rate: {trace_metadata.get('success_rating', 0.0):.0%}
- Times Used: {trace_metadata.get('usage_count', 0)}
- Mode: {trace_metadata.get('mode', 'UNKNOWN')}

Question: Can the execution trace from the previous goal be safely reused for the current goal?

Consider:
1. **Semantic equivalence**: Do the goals request the same logical action?
2. **Scope similarity**: Are the goals operating at the same level of complexity?
3. **Output compatibility**: Would the same execution steps work for both goals?

Respond with a JSON object:
{{
  "confidence": 0.95,  // Score from 0.0 (completely different) to 1.0 (identical intent)
  "reasoning": "Brief explanation of why they match or don't match",
  "recommended_mode": "FOLLOWER"  // One of: FOLLOWER, MIXED, LEARNER
}}

Scoring guide:
- 0.95-1.0: Virtually identical (minor wording differences only)
- 0.85-0.95: Same core task, slight parameter differences
- 0.70-0.85: Related tasks, could benefit from similar approach
- 0.50-0.70: Loosely related, different execution needed
- 0.0-0.50: Unrelated tasks

Be strict: only high scores for truly equivalent tasks.
"""

        # Configure Claude options
        options = ClaudeAgentOptions(
            model=self.model,
            cwd=str(self.workspace),
            allowed_tools=[],  # No tools needed for analysis
            permission_mode="acceptEdits",
            system_prompt={
                "type": "text",
                "text": """You are a semantic analysis expert specializing in task equivalence.
Your role is to determine if two natural language goals are functionally equivalent.

Be conservative: only assign high confidence scores when you're certain the same
execution strategy will work for both goals.

Consider edge cases:
- "Create a file" vs "Create a new file" → High confidence (same action)
- "List files" vs "Show all files" → High confidence (same action)
- "Create a Python file" vs "Create a JavaScript file" → Low confidence (different file types)
- "Read config.json" vs "Read settings.yaml" → Medium confidence (same action, different files)

Always respond with valid JSON."""
            }
        )

        result = None

        try:
            async with ClaudeSDKClient(options=options) as client:
                await client.query(analysis_prompt)

                async for msg in client.receive_response():
                    if hasattr(msg, "content"):
                        for block in msg.content:
                            if hasattr(block, "text"):
                                text = block.text
                                # Extract JSON from response
                                try:
                                    start = text.find("{")
                                    end = text.rfind("}") + 1
                                    if start != -1 and end != 0:
                                        result = json.loads(text[start:end])
                                except json.JSONDecodeError:
                                    continue

                    # Break on ResultMessage
                    if "Result" in msg.__class__.__name__:
                        break

        except Exception as e:
            print(f"[WARNING] LLM analysis failed: {e}")
            return 0.0

        if result and "confidence" in result:
            return float(result["confidence"])

        return 0.0

    async def find_best_matching_trace(
        self,
        goal: str,
        traces: List[Any],  # List[ExecutionTrace]
        min_confidence: float = 0.75
    ) -> Optional[TraceMatch]:
        """
        Find best matching trace using LLM analysis

        Analyzes all traces and returns the best semantic match.

        Args:
            goal: Goal to match
            traces: List of ExecutionTrace instances
            min_confidence: Minimum confidence threshold

        Returns:
            TraceMatch if found, None otherwise
        """
        if not traces:
            return None

        # Build analysis prompt with all traces
        traces_info = []
        for i, trace in enumerate(traces):
            traces_info.append({
                "index": i,
                "goal": trace.goal_text,
                "signature": trace.goal_signature,
                "success_rating": trace.success_rating,
                "usage_count": trace.usage_count,
                "mode": trace.mode
            })

        analysis_prompt = f"""Find the best matching execution trace for this goal.

Current Goal:
"{goal}"

Available Traces:
{json.dumps(traces_info, indent=2)}

Question: Which trace (if any) best matches the current goal?

Respond with JSON:
{{
  "best_match_index": 0,  // Index of best matching trace, or null if none match
  "confidence": 0.95,  // Confidence score (0.0-1.0)
  "reasoning": "Why this trace matches",
  "recommended_mode": "FOLLOWER"  // FOLLOWER, MIXED, or LEARNER
}}

Criteria:
1. Semantic similarity to goal
2. Success rate (prefer proven traces)
3. Usage count (prefer well-tested traces)

Confidence thresholds:
- ≥0.92: FOLLOWER mode (execute trace directly)
- 0.75-0.92: MIXED mode (use trace as guidance)
- <0.75: LEARNER mode (learn from scratch)

If no trace has confidence ≥{min_confidence}, set best_match_index to null.
"""

        options = ClaudeAgentOptions(
            model=self.model,
            cwd=str(self.workspace),
            allowed_tools=[],
            permission_mode="acceptEdits",
            system_prompt={
                "type": "text",
                "text": """You are an expert at matching tasks to execution traces.
Analyze semantic similarity while considering execution success history.

Prioritize:
1. Semantic equivalence (most important)
2. High success rate
3. Frequent usage (indicates reliability)

Be conservative with confidence scores. Always return valid JSON."""
            }
        )

        result = None

        try:
            async with ClaudeSDKClient(options=options) as client:
                await client.query(analysis_prompt)

                async for msg in client.receive_response():
                    if hasattr(msg, "content"):
                        for block in msg.content:
                            if hasattr(block, "text"):
                                text = block.text
                                try:
                                    start = text.find("{")
                                    end = text.rfind("}") + 1
                                    if start != -1 and end != 0:
                                        result = json.loads(text[start:end])
                                except json.JSONDecodeError:
                                    continue

                    if "Result" in msg.__class__.__name__:
                        break

        except Exception as e:
            print(f"[WARNING] Trace matching analysis failed: {e}")
            return None

        if not result:
            return None

        # Extract match
        match_index = result.get("best_match_index")

        if match_index is None:
            return None

        confidence = float(result.get("confidence", 0.0))

        if confidence < min_confidence:
            return None

        # Get matched trace
        matched_trace = traces[match_index]

        return TraceMatch(
            trace_signature=matched_trace.goal_signature,
            goal_text=matched_trace.goal_text,
            confidence=confidence,
            reasoning=result.get("reasoning", "LLM analysis matched this trace"),
            recommended_mode=result.get("recommended_mode", self._determine_mode(confidence))
        )

    def _determine_mode(self, confidence: float) -> str:
        """
        Determine execution mode from confidence score

        Args:
            confidence: Confidence score (0.0-1.0)

        Returns:
            Mode string: "FOLLOWER", "MIXED", or "LEARNER"
        """
        if confidence >= 0.92:
            return "FOLLOWER"
        elif confidence >= 0.75:
            return "MIXED"
        else:
            return "LEARNER"

    async def batch_analyze_traces(
        self,
        goal: str,
        traces: List[Any],
        top_k: int = 3
    ) -> List[TraceMatch]:
        """
        Analyze multiple traces and return top matches

        Useful for providing multiple execution options to the user.

        Args:
            goal: Goal to match
            traces: List of ExecutionTrace instances
            top_k: Number of top matches to return

        Returns:
            List of TraceMatch instances, sorted by confidence
        """
        # For efficiency, we'll use the batch analysis in find_best_matching_trace
        # and return the single best match
        #
        # In a production system, you could modify find_best_matching_trace
        # to return multiple matches

        best_match = await self.find_best_matching_trace(goal, traces, min_confidence=0.5)

        if best_match:
            return [best_match]

        return []
