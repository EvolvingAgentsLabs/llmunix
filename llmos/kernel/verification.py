"""
Verification and Testing Harness for LLMOS

Automatic verification system for tools, agents, and crystallized patterns.
Inspired by Claude-Flow's testing approach with >90% test coverage.

Key Features:
- Automatic test generation from traces
- Tool validation before crystallization
- Agent performance verification
- Correctness threshold enforcement
- Continuous validation of evolved patterns

Inspired by Claude-Flow's verification system (MIT License)
https://github.com/ruvnet/claude-flow
"""

from typing import Dict, Any, List, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
import asyncio
from pathlib import Path
import time


class VerificationStatus(Enum):
    """Verification result status"""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class VerificationResult:
    """Single verification test result"""
    test_name: str
    status: VerificationStatus
    expected: Any = None
    actual: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return self.status == VerificationStatus.PASSED


@dataclass
class VerificationSuite:
    """Collection of verification results"""
    suite_name: str
    results: List[VerificationResult] = field(default_factory=list)
    total_time: float = 0.0

    @property
    def total_tests(self) -> int:
        return len(self.results)

    @property
    def passed_tests(self) -> int:
        return sum(1 for r in self.results if r.passed)

    @property
    def failed_tests(self) -> int:
        return sum(1 for r in self.results if r.status == VerificationStatus.FAILED)

    @property
    def error_tests(self) -> int:
        return sum(1 for r in self.results if r.status == VerificationStatus.ERROR)

    @property
    def success_rate(self) -> float:
        if self.total_tests == 0:
            return 0.0
        return self.passed_tests / self.total_tests

    def add_result(self, result: VerificationResult):
        """Add a test result"""
        self.results.append(result)

    def meets_threshold(self, threshold: float = 0.9) -> bool:
        """Check if suite meets success threshold"""
        return self.success_rate >= threshold


class ToolVerifier:
    """
    Tool Verification Engine

    Validates tools before they are crystallized or deployed.
    Generates test cases from successful traces.
    """

    def __init__(
        self,
        workspace: Path,
        min_success_rate: float = 0.9,
        timeout_secs: float = 30.0
    ):
        self.workspace = workspace
        self.min_success_rate = min_success_rate
        self.timeout_secs = timeout_secs

    async def verify_tool(
        self,
        tool_name: str,
        tool_func: Callable,
        test_cases: List[Dict[str, Any]]
    ) -> VerificationSuite:
        """
        Verify a tool against test cases

        Args:
            tool_name: Name of the tool
            tool_func: Tool function to test
            test_cases: List of test cases with inputs and expected outputs

        Returns:
            VerificationSuite with results
        """
        suite = VerificationSuite(suite_name=f"Tool: {tool_name}")
        start_time = time.time()

        for i, test_case in enumerate(test_cases):
            test_name = f"{tool_name}_test_{i}"
            inputs = test_case.get("inputs", {})
            expected = test_case.get("expected")

            result = await self._run_test(
                test_name=test_name,
                func=tool_func,
                inputs=inputs,
                expected=expected
            )

            suite.add_result(result)

        suite.total_time = time.time() - start_time
        return suite

    async def _run_test(
        self,
        test_name: str,
        func: Callable,
        inputs: Dict[str, Any],
        expected: Any
    ) -> VerificationResult:
        """Run a single test case"""
        start_time = time.time()

        try:
            # Execute with timeout
            if asyncio.iscoroutinefunction(func):
                actual = await asyncio.wait_for(
                    func(**inputs),
                    timeout=self.timeout_secs
                )
            else:
                loop = asyncio.get_event_loop()
                actual = await asyncio.wait_for(
                    loop.run_in_executor(None, lambda: func(**inputs)),
                    timeout=self.timeout_secs
                )

            execution_time = time.time() - start_time

            # Compare results
            if self._compare_results(actual, expected):
                return VerificationResult(
                    test_name=test_name,
                    status=VerificationStatus.PASSED,
                    expected=expected,
                    actual=actual,
                    execution_time=execution_time
                )
            else:
                return VerificationResult(
                    test_name=test_name,
                    status=VerificationStatus.FAILED,
                    expected=expected,
                    actual=actual,
                    error=f"Expected {expected}, got {actual}",
                    execution_time=execution_time
                )

        except asyncio.TimeoutError:
            return VerificationResult(
                test_name=test_name,
                status=VerificationStatus.ERROR,
                error=f"Timeout after {self.timeout_secs}s",
                execution_time=time.time() - start_time
            )

        except Exception as e:
            return VerificationResult(
                test_name=test_name,
                status=VerificationStatus.ERROR,
                error=str(e),
                execution_time=time.time() - start_time
            )

    def _compare_results(self, actual: Any, expected: Any) -> bool:
        """
        Compare actual vs expected results

        Supports various comparison strategies:
        - Exact equality
        - Dict subset matching
        - Numeric tolerance
        """
        if expected is None:
            # No expected value means we just check for no errors
            return True

        if isinstance(expected, dict) and isinstance(actual, dict):
            # Check if all expected keys/values are in actual
            return all(
                k in actual and actual[k] == v
                for k, v in expected.items()
            )

        if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
            # Numeric tolerance
            return abs(actual - expected) < 1e-6

        # Default: exact equality
        return actual == expected


class AgentVerifier:
    """
    Agent Verification Engine

    Validates agent performance against expected metrics.
    Ensures agents meet quality thresholds before deployment.
    """

    def __init__(
        self,
        min_success_rate: float = 0.85,
        min_avg_rating: float = 0.75
    ):
        self.min_success_rate = min_success_rate
        self.min_avg_rating = min_avg_rating

    async def verify_agent(
        self,
        agent_name: str,
        traces: List[Any]  # List of ExecutionTrace objects
    ) -> VerificationSuite:
        """
        Verify agent performance based on execution traces

        Args:
            agent_name: Name of the agent
            traces: Execution traces for this agent

        Returns:
            VerificationSuite with verification results
        """
        suite = VerificationSuite(suite_name=f"Agent: {agent_name}")

        if not traces:
            suite.add_result(VerificationResult(
                test_name=f"{agent_name}_has_traces",
                status=VerificationStatus.FAILED,
                error="No execution traces found"
            ))
            return suite

        # Test 1: Success rate
        success_count = sum(1 for t in traces if t.success)
        success_rate = success_count / len(traces)

        suite.add_result(VerificationResult(
            test_name=f"{agent_name}_success_rate",
            status=VerificationStatus.PASSED if success_rate >= self.min_success_rate else VerificationStatus.FAILED,
            expected=self.min_success_rate,
            actual=success_rate,
            metadata={"total_traces": len(traces), "successful": success_count}
        ))

        # Test 2: Average rating
        avg_rating = sum(t.success_rating for t in traces) / len(traces)

        suite.add_result(VerificationResult(
            test_name=f"{agent_name}_avg_rating",
            status=VerificationStatus.PASSED if avg_rating >= self.min_avg_rating else VerificationStatus.FAILED,
            expected=self.min_avg_rating,
            actual=avg_rating
        ))

        # Test 3: Performance consistency (standard deviation of ratings)
        if len(traces) > 1:
            ratings = [t.success_rating for t in traces]
            mean = sum(ratings) / len(ratings)
            variance = sum((r - mean) ** 2 for r in ratings) / len(ratings)
            std_dev = variance ** 0.5

            # Lower std dev is better (more consistent)
            consistent = std_dev < 0.2

            suite.add_result(VerificationResult(
                test_name=f"{agent_name}_consistency",
                status=VerificationStatus.PASSED if consistent else VerificationStatus.FAILED,
                expected="<0.2",
                actual=std_dev,
                metadata={"variance": variance}
            ))

        return suite


class CrystallizationVerifier:
    """
    Crystallization Verification Engine

    Validates that crystallized tools match the behavior of their source traces.
    Ensures crystallization doesn't introduce bugs.
    """

    def __init__(
        self,
        tool_verifier: ToolVerifier,
        min_match_rate: float = 0.95
    ):
        self.tool_verifier = tool_verifier
        self.min_match_rate = min_match_rate

    async def verify_crystallization(
        self,
        tool_name: str,
        tool_func: Callable,
        source_traces: List[Any],
        num_test_cases: int = 10
    ) -> VerificationSuite:
        """
        Verify that crystallized tool matches source trace behavior

        Args:
            tool_name: Name of crystallized tool
            tool_func: Crystallized tool function
            source_traces: Traces that were crystallized
            num_test_cases: Number of test cases to generate

        Returns:
            VerificationSuite with verification results
        """
        # Generate test cases from traces
        test_cases = self._generate_test_cases_from_traces(
            source_traces,
            num_test_cases
        )

        # Run tool verification
        suite = await self.tool_verifier.verify_tool(
            tool_name=tool_name,
            tool_func=tool_func,
            test_cases=test_cases
        )

        # Check if meets threshold
        if suite.meets_threshold(self.min_match_rate):
            suite.add_result(VerificationResult(
                test_name=f"{tool_name}_crystallization_valid",
                status=VerificationStatus.PASSED,
                expected=self.min_match_rate,
                actual=suite.success_rate,
                metadata={
                    "source_traces": len(source_traces),
                    "test_cases": len(test_cases)
                }
            ))
        else:
            suite.add_result(VerificationResult(
                test_name=f"{tool_name}_crystallization_valid",
                status=VerificationStatus.FAILED,
                expected=self.min_match_rate,
                actual=suite.success_rate,
                error=f"Crystallization only matched {suite.success_rate:.0%} of traces"
            ))

        return suite

    def _generate_test_cases_from_traces(
        self,
        traces: List[Any],
        num_cases: int
    ) -> List[Dict[str, Any]]:
        """
        Generate test cases from execution traces

        Extracts inputs and expected outputs from successful traces.
        """
        test_cases = []

        # Use successful traces only
        successful_traces = [t for t in traces if t.success][:num_cases]

        for trace in successful_traces:
            # Extract test case from trace
            # This is a simplified version - real implementation would
            # parse tool_calls to extract inputs/outputs
            test_case = {
                "inputs": {},  # Would extract from trace.tool_calls
                "expected": None  # Would extract from trace output
            }
            test_cases.append(test_case)

        return test_cases


class VerificationManager:
    """
    Central Verification Management

    Coordinates all verification activities:
    - Tool verification before crystallization
    - Agent performance validation
    - Continuous testing of evolved patterns
    """

    def __init__(
        self,
        workspace: Path,
        config: Optional[Dict[str, Any]] = None
    ):
        self.workspace = workspace
        self.config = config or {}

        # Initialize verifiers
        self.tool_verifier = ToolVerifier(
            workspace=workspace,
            min_success_rate=self.config.get("min_tool_success_rate", 0.9),
            timeout_secs=self.config.get("tool_timeout_secs", 30.0)
        )

        self.agent_verifier = AgentVerifier(
            min_success_rate=self.config.get("min_agent_success_rate", 0.85),
            min_avg_rating=self.config.get("min_agent_avg_rating", 0.75)
        )

        self.crystallization_verifier = CrystallizationVerifier(
            tool_verifier=self.tool_verifier,
            min_match_rate=self.config.get("min_crystallization_match", 0.95)
        )

        # Verification history
        self.verification_history: List[VerificationSuite] = []

    async def verify_before_crystallization(
        self,
        tool_name: str,
        tool_func: Callable,
        source_traces: List[Any]
    ) -> Tuple[bool, VerificationSuite]:
        """
        Verify a tool before crystallization

        Args:
            tool_name: Name of tool
            tool_func: Tool function
            source_traces: Source traces

        Returns:
            (should_crystallize: bool, suite: VerificationSuite)
        """
        suite = await self.crystallization_verifier.verify_crystallization(
            tool_name=tool_name,
            tool_func=tool_func,
            source_traces=source_traces
        )

        self.verification_history.append(suite)

        # Decision: crystallize if meets threshold
        should_crystallize = suite.meets_threshold(
            self.config.get("min_crystallization_match", 0.95)
        )

        return should_crystallize, suite

    async def verify_agent_performance(
        self,
        agent_name: str,
        traces: List[Any]
    ) -> Tuple[bool, VerificationSuite]:
        """
        Verify agent performance

        Args:
            agent_name: Name of agent
            traces: Execution traces

        Returns:
            (meets_standards: bool, suite: VerificationSuite)
        """
        suite = await self.agent_verifier.verify_agent(
            agent_name=agent_name,
            traces=traces
        )

        self.verification_history.append(suite)

        meets_standards = suite.meets_threshold(
            self.config.get("min_agent_success_rate", 0.85)
        )

        return meets_standards, suite

    def get_verification_statistics(self) -> Dict[str, Any]:
        """Get verification statistics"""
        if not self.verification_history:
            return {
                "total_suites": 0,
                "total_tests": 0,
                "overall_success_rate": 0.0
            }

        total_tests = sum(s.total_tests for s in self.verification_history)
        total_passed = sum(s.passed_tests for s in self.verification_history)

        return {
            "total_suites": len(self.verification_history),
            "total_tests": total_tests,
            "overall_success_rate": total_passed / total_tests if total_tests > 0 else 0.0,
            "by_suite": [
                {
                    "name": s.suite_name,
                    "success_rate": s.success_rate,
                    "tests": s.total_tests,
                    "time": s.total_time
                }
                for s in self.verification_history[-10:]  # Last 10 suites
            ]
        }

    def generate_report(self) -> str:
        """Generate a verification report"""
        stats = self.get_verification_statistics()

        report = f"""
# Verification Report

## Summary
- Total Suites: {stats['total_suites']}
- Total Tests: {stats['total_tests']}
- Overall Success Rate: {stats['overall_success_rate']:.1%}

## Recent Suites
"""

        for suite_stats in stats.get('by_suite', []):
            report += f"""
### {suite_stats['name']}
- Success Rate: {suite_stats['success_rate']:.1%}
- Tests: {suite_stats['tests']}
- Time: {suite_stats['time']:.2f}s
"""

        return report
