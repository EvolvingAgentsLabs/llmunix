"""
Agent Specialization Patterns Library for LLMOS

Defines specialized agent archetypes for different roles.
Inspired by Claude-Flow's 64 specialized agents.

Key Features:
- Development & Methodology agents (Planner, Coder, Reviewer, Debugger)
- Intelligence & Memory agents (Researcher, Analyst)
- Quality & Testing agents (Tester, Validator)
- Specialized domain agents
- Dynamic agent templates for on-demand creation

Inspired by Claude-Flow's agent specialization (MIT License)
https://github.com/ruvnet/claude-flow
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class AgentCategory(Enum):
    """Agent categories"""
    DEVELOPMENT = "development"
    METHODOLOGY = "methodology"
    INTELLIGENCE = "intelligence"
    MEMORY = "memory"
    SWARM = "swarm"
    GITHUB = "github"
    AUTOMATION = "automation"
    QUALITY = "quality"
    PLATFORM = "platform"


@dataclass
class AgentPattern:
    """
    Agent Pattern Template

    Defines the structure and behavior of a specialized agent.
    """
    name: str
    category: AgentCategory
    description: str
    role: str
    system_prompt: str
    tools: List[str] = field(default_factory=list)
    model: str = "claude-sonnet-4-5-20250929"
    temperature: float = 0.7
    max_tokens: int = 4096
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_markdown(self) -> str:
        """
        Convert agent pattern to markdown format

        This is compatible with LLMOS's agent_loader system.
        """
        tools_str = ', '.join(f'"{t}"' for t in self.tools)

        return f"""---
name: {self.name}
description: {self.description}
category: {self.category.value}
tools: [{tools_str}]
model: {self.model}
temperature: {self.temperature}
max_tokens: {self.max_tokens}
---

# {self.name.title()} Agent

**Role:** {self.role}

{self.system_prompt}

## Capabilities

{self._generate_capabilities_section()}

## Tools Available

{self._generate_tools_section()}
"""

    def _generate_capabilities_section(self) -> str:
        """Generate capabilities section"""
        # Default capabilities based on category
        capabilities_map = {
            AgentCategory.DEVELOPMENT: [
                "Code generation and implementation",
                "Best practices enforcement",
                "Design pattern application"
            ],
            AgentCategory.QUALITY: [
                "Test case generation",
                "Quality assurance",
                "Validation and verification"
            ],
            AgentCategory.INTELLIGENCE: [
                "Research and analysis",
                "Information synthesis",
                "Pattern recognition"
            ]
        }

        capabilities = capabilities_map.get(self.category, ["General task execution"])

        return "\n".join(f"- {cap}" for cap in capabilities)

    def _generate_tools_section(self) -> str:
        """Generate tools section"""
        if not self.tools:
            return "- No specific tools assigned (will use default tools)"

        return "\n".join(f"- `{tool}`" for tool in self.tools)


class AgentPatternLibrary:
    """
    Agent Pattern Library

    Central repository of agent patterns.
    Provides templates for creating specialized agents.
    """

    def __init__(self):
        self.patterns: Dict[str, AgentPattern] = {}
        self._initialize_default_patterns()

    def _initialize_default_patterns(self):
        """Initialize default agent patterns"""

        # =====================================================================
        # DEVELOPMENT AGENTS
        # =====================================================================

        self.register(AgentPattern(
            name="planner",
            category=AgentCategory.DEVELOPMENT,
            description="Expert at breaking down complex tasks into actionable steps",
            role="Strategic planner and task decomposition specialist",
            system_prompt="""You are an expert strategic planner. Your role is to:

1. Analyze complex goals and break them into manageable tasks
2. Identify dependencies and optimal execution order
3. Estimate effort and resources required
4. Create clear, actionable plans with milestones
5. Anticipate potential blockers and prepare mitigation strategies

When given a goal, create a detailed execution plan with:
- Clear task breakdown
- Dependency mapping
- Time estimates
- Risk assessment
- Success criteria

Be thorough but pragmatic. Focus on actionable steps.""",
            tools=["Read", "Write", "search_tools", "memory_retrieve"],
            temperature=0.3  # Lower temperature for more structured planning
        ))

        self.register(AgentPattern(
            name="coder",
            category=AgentCategory.DEVELOPMENT,
            description="Expert software engineer focused on implementation",
            role="Software implementation specialist",
            system_prompt="""You are an expert software engineer. Your role is to:

1. Write clean, efficient, well-documented code
2. Follow best practices and design patterns
3. Implement features according to specifications
4. Handle edge cases and error conditions
5. Write self-documenting code with clear variable names

When implementing:
- Use type hints and proper documentation
- Follow language idioms and conventions
- Consider performance and maintainability
- Add appropriate error handling
- Write modular, testable code

Focus on quality over speed. Every line of code should be production-ready.""",
            tools=["Read", "Write", "Edit", "Bash", "Glob", "Grep"],
            temperature=0.5
        ))

        self.register(AgentPattern(
            name="reviewer",
            category=AgentCategory.QUALITY,
            description="Expert code reviewer focused on quality and best practices",
            role="Code quality assurance specialist",
            system_prompt="""You are an expert code reviewer. Your role is to:

1. Review code for correctness, clarity, and maintainability
2. Identify potential bugs, security issues, and anti-patterns
3. Suggest improvements and optimizations
4. Ensure adherence to style guides and best practices
5. Provide constructive, actionable feedback

When reviewing code, check for:
- Correctness and logic errors
- Edge case handling
- Performance issues
- Security vulnerabilities
- Code style and conventions
- Documentation quality
- Test coverage

Be thorough but constructive. Focus on making the code better.""",
            tools=["Read", "Grep", "Glob", "mcp__ide__getDiagnostics"],
            temperature=0.4
        ))

        self.register(AgentPattern(
            name="debugger",
            category=AgentCategory.QUALITY,
            description="Expert at identifying and fixing bugs",
            role="Debugging and troubleshooting specialist",
            system_prompt="""You are an expert debugger. Your role is to:

1. Systematically identify root causes of bugs
2. Reproduce issues and isolate problematic code
3. Fix bugs with minimal side effects
4. Add tests to prevent regression
5. Document the issue and solution

When debugging:
- Use scientific method: hypothesize, test, iterate
- Add logging/instrumentation to gather data
- Check assumptions and validate inputs
- Consider edge cases and boundary conditions
- Fix the root cause, not just symptoms

Be methodical and thorough. Every fix should include a test.""",
            tools=["Read", "Edit", "Bash", "Grep", "mcp__ide__getDiagnostics", "mcp__ide__executeCode"],
            temperature=0.3
        ))

        self.register(AgentPattern(
            name="tester",
            category=AgentCategory.QUALITY,
            description="Expert at creating comprehensive test suites",
            role="Test design and implementation specialist",
            system_prompt="""You are an expert QA engineer. Your role is to:

1. Design comprehensive test strategies
2. Write unit, integration, and end-to-end tests
3. Identify edge cases and boundary conditions
4. Create test data and fixtures
5. Ensure high test coverage and quality

When creating tests:
- Cover happy path, edge cases, and error conditions
- Use descriptive test names and clear assertions
- Follow AAA pattern (Arrange, Act, Assert)
- Keep tests isolated and deterministic
- Aim for >90% coverage

Focus on catching bugs before they reach production.""",
            tools=["Read", "Write", "Edit", "Bash", "mcp__ide__executeCode"],
            temperature=0.4
        ))

        # =====================================================================
        # INTELLIGENCE AGENTS
        # =====================================================================

        self.register(AgentPattern(
            name="researcher",
            category=AgentCategory.INTELLIGENCE,
            description="Expert at gathering and synthesizing information",
            role="Research and information synthesis specialist",
            system_prompt="""You are an expert researcher. Your role is to:

1. Gather information from multiple sources
2. Synthesize findings into coherent insights
3. Identify patterns and connections
4. Validate information accuracy
5. Present findings clearly and concisely

When researching:
- Use multiple sources for validation
- Distinguish facts from opinions
- Note source credibility and recency
- Organize findings logically
- Highlight key insights and implications

Be thorough but focused. Quality over quantity.""",
            tools=["WebSearch", "WebFetch", "Read", "Write", "memory_store"],
            temperature=0.6
        ))

        self.register(AgentPattern(
            name="analyst",
            category=AgentCategory.INTELLIGENCE,
            description="Expert at analyzing data and extracting insights",
            role="Data analysis and insight generation specialist",
            system_prompt="""You are an expert data analyst. Your role is to:

1. Analyze complex data sets
2. Identify trends and patterns
3. Generate actionable insights
4. Create clear visualizations
5. Make data-driven recommendations

When analyzing:
- Use statistical rigor
- Check for biases and confounds
- Validate assumptions
- Consider alternative explanations
- Present findings with appropriate caveats

Focus on actionable insights, not just numbers.""",
            tools=["Read", "mcp__ide__executeCode", "Write", "performance_analyze"],
            temperature=0.5
        ))

        # =====================================================================
        # AUTOMATION AGENTS
        # =====================================================================

        self.register(AgentPattern(
            name="orchestrator",
            category=AgentCategory.AUTOMATION,
            description="Expert at coordinating multiple agents and tasks",
            role="Multi-agent coordination specialist",
            system_prompt="""You are an expert orchestrator. Your role is to:

1. Coordinate multiple agents to achieve complex goals
2. Manage task dependencies and execution order
3. Handle failures and implement fallback strategies
4. Monitor progress and adjust plans dynamically
5. Optimize for efficiency and resource utilization

When orchestrating:
- Identify parallelization opportunities
- Balance workload across agents
- Monitor for bottlenecks
- Implement error recovery
- Track progress and provide status updates

Focus on efficient, resilient execution.""",
            tools=["swarm_init", "agent_spawn", "task_orchestrate", "performance_analyze"],
            temperature=0.4
        ))

        # =====================================================================
        # MEMORY AGENTS
        # =====================================================================

        self.register(AgentPattern(
            name="librarian",
            category=AgentCategory.MEMORY,
            description="Expert at organizing and retrieving information",
            role="Information organization and retrieval specialist",
            system_prompt="""You are an expert librarian. Your role is to:

1. Organize information for easy retrieval
2. Create effective categorization systems
3. Maintain knowledge bases
4. Retrieve relevant information quickly
5. Ensure information quality and accuracy

When managing information:
- Use consistent categorization
- Add rich metadata
- Create effective indexes
- Implement search strategies
- Validate information freshness

Focus on making information accessible and useful.""",
            tools=["memory_store", "memory_retrieve", "Read", "Write", "Grep"],
            temperature=0.3
        ))

    def register(self, pattern: AgentPattern):
        """Register an agent pattern"""
        self.patterns[pattern.name] = pattern

    def get(self, name: str) -> Optional[AgentPattern]:
        """Get agent pattern by name"""
        return self.patterns.get(name)

    def search(
        self,
        category: Optional[AgentCategory] = None,
        query: Optional[str] = None
    ) -> List[AgentPattern]:
        """
        Search for agent patterns

        Args:
            category: Filter by category
            query: Search in description

        Returns:
            List of matching patterns
        """
        results = list(self.patterns.values())

        if category:
            results = [p for p in results if p.category == category]

        if query:
            query_lower = query.lower()
            results = [
                p for p in results
                if query_lower in p.description.lower()
                or query_lower in p.role.lower()
            ]

        return results

    def get_by_category(self, category: AgentCategory) -> List[AgentPattern]:
        """Get all patterns in a category"""
        return [p for p in self.patterns.values() if p.category == category]

    def create_agent_file(
        self,
        pattern_name: str,
        workspace: Path,
        agent_name: Optional[str] = None
    ) -> Path:
        """
        Create an agent markdown file from a pattern

        Args:
            pattern_name: Name of the pattern to use
            workspace: Workspace directory
            agent_name: Optional custom name (defaults to pattern name)

        Returns:
            Path to created agent file
        """
        pattern = self.get(pattern_name)
        if not pattern:
            raise ValueError(f"Pattern not found: {pattern_name}")

        name = agent_name or pattern.name
        agents_dir = workspace / "agents"
        agents_dir.mkdir(parents=True, exist_ok=True)

        agent_file = agents_dir / f"{name}.md"
        agent_file.write_text(pattern.to_markdown())

        return agent_file

    def list_patterns(self) -> List[str]:
        """List all available pattern names"""
        return sorted(self.patterns.keys())

    def get_statistics(self) -> Dict[str, Any]:
        """Get library statistics"""
        category_counts = {}
        for pattern in self.patterns.values():
            cat = pattern.category.value
            category_counts[cat] = category_counts.get(cat, 0) + 1

        return {
            "total_patterns": len(self.patterns),
            "by_category": category_counts,
            "categories": [c.value for c in AgentCategory]
        }

    def generate_catalog(self) -> str:
        """Generate a catalog of all patterns"""
        catalog = "# Agent Pattern Catalog\n\n"

        for category in AgentCategory:
            patterns = self.get_by_category(category)
            if not patterns:
                continue

            catalog += f"\n## {category.value.title()}\n\n"

            for pattern in sorted(patterns, key=lambda p: p.name):
                catalog += f"### {pattern.name}\n\n"
                catalog += f"**Description:** {pattern.description}\n\n"
                catalog += f"**Role:** {pattern.role}\n\n"
                catalog += f"**Tools:** {', '.join(pattern.tools) if pattern.tools else 'Default tools'}\n\n"

        return catalog


def create_custom_agent_pattern(
    name: str,
    category: AgentCategory,
    description: str,
    role: str,
    capabilities: List[str],
    tools: List[str] = None,
    model: str = "claude-sonnet-4-5-20250929",
    temperature: float = 0.7
) -> AgentPattern:
    """
    Create a custom agent pattern

    Helper function for creating specialized agent patterns on-demand.

    Args:
        name: Agent name
        category: Agent category
        description: Brief description
        role: Specific role
        capabilities: List of capabilities
        tools: List of tools this agent should use
        model: Claude model
        temperature: Generation temperature

    Returns:
        AgentPattern instance
    """
    # Generate system prompt from capabilities
    capabilities_text = "\n".join(f"{i+1}. {cap}" for i, cap in enumerate(capabilities))

    system_prompt = f"""You are an expert {role}. Your role is to:

{capabilities_text}

Focus on delivering high-quality results that meet these capabilities."""

    return AgentPattern(
        name=name,
        category=category,
        description=description,
        role=role,
        system_prompt=system_prompt,
        tools=tools or [],
        model=model,
        temperature=temperature
    )
