"""
Agent Factory - Creates and manages dynamic agents
Brings llmunix-style on-demand agent creation to llmos
"""

from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import yaml


@dataclass
class AgentSpec:
    """
    Agent Specification - Defines an agent's capabilities and behavior

    This follows llmunix's YAML frontmatter format for agent definitions
    """
    name: str  # Kebab-case identifier (e.g., "quantum-simulation-agent")
    agent_type: str  # "orchestration", "specialized", "memory", "code_generation"
    category: str  # Domain category
    description: str  # When to use this agent
    tools: List[str]  # Available tools: ["Read", "Write", "Bash", "Task", etc.]
    version: str = "1.0"
    status: str = "production"  # "production", "experimental", "deprecated"
    mode: List[str] = field(default_factory=lambda: ["EXECUTION"])
    system_prompt: str = ""  # Detailed instructions for agent behavior
    capabilities: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    replaces: Optional[str] = None  # Previous version if evolved


class AgentFactory:
    """
    Creates and manages dynamic agents

    Key capabilities:
    1. Create new agents on-demand from specifications
    2. Save agent definitions as markdown with YAML frontmatter
    3. Load agents from markdown definitions
    4. Evolve agents (create new versions)
    5. Maintain agent registry
    """

    def __init__(self, workspace: Path):
        """
        Initialize AgentFactory

        Args:
            workspace: Root workspace directory
        """
        self.workspace = Path(workspace)
        self.agents_dir = self.workspace / "agents"
        self.agents_dir.mkdir(parents=True, exist_ok=True)

        # In-memory agent registry
        self.agents: Dict[str, AgentSpec] = {}
        self._load_existing_agents()

    def _load_existing_agents(self):
        """Load existing agent definitions from filesystem"""
        if not self.agents_dir.exists():
            return

        for agent_file in self.agents_dir.glob("*.md"):
            try:
                spec = self.load_agent_definition(agent_file)
                if spec:
                    self.agents[spec.name] = spec
            except Exception as e:
                print(f"Warning: Failed to load agent {agent_file}: {e}")

    def create_agent(
        self,
        name: str,
        agent_type: str,
        category: str,
        description: str,
        system_prompt: str,
        tools: List[str],
        capabilities: Optional[List[str]] = None,
        constraints: Optional[List[str]] = None,
        **kwargs
    ) -> AgentSpec:
        """
        Create a new agent from specification

        Args:
            name: Agent name (kebab-case)
            agent_type: Type of agent (orchestration, specialized, etc.)
            category: Domain category
            description: When to use this agent
            system_prompt: Detailed behavioral instructions
            tools: List of available tools
            capabilities: List of agent capabilities
            constraints: List of agent constraints
            **kwargs: Additional metadata

        Returns:
            AgentSpec instance
        """
        spec = AgentSpec(
            name=name,
            agent_type=agent_type,
            category=category,
            description=description,
            tools=tools,
            system_prompt=system_prompt,
            capabilities=capabilities or [],
            constraints=constraints or [],
            **kwargs
        )

        # Save agent definition
        self.save_agent_definition(spec)

        # Register agent
        self.agents[spec.name] = spec

        return spec

    def save_agent_definition(self, spec: AgentSpec, path: Optional[Path] = None) -> Path:
        """
        Save agent definition as markdown with YAML frontmatter

        Format:
        ```
        ---
        agent_name: quantum-simulation-agent
        type: specialized
        category: quantum_computing
        ...
        ---

        # Agent Name: Purpose

        Detailed system prompt and instructions...
        ```

        Args:
            spec: AgentSpec to save
            path: Optional custom path (defaults to agents/{name}.md)

        Returns:
            Path to saved file
        """
        if path is None:
            # Convert name to PascalCase for filename
            filename = self._name_to_filename(spec.name)
            path = self.agents_dir / filename

        # Create YAML frontmatter
        frontmatter = {
            "agent_name": spec.name,
            "type": spec.agent_type,
            "category": spec.category,
            "description": spec.description,
            "tools": spec.tools,
            "version": spec.version,
            "status": spec.status,
            "mode": spec.mode
        }

        if spec.replaces:
            frontmatter["replaces"] = spec.replaces

        # Create markdown content
        content_parts = [
            "---",
            yaml.dump(frontmatter, default_flow_style=False, sort_keys=False).strip(),
            "---",
            "",
            f"# {self._name_to_title(spec.name)}: {spec.category}",
            "",
            spec.system_prompt,
            "",
            "## Capabilities",
            ""
        ]

        for capability in spec.capabilities:
            content_parts.append(f"- {capability}")

        if spec.constraints:
            content_parts.extend([
                "",
                "## Constraints",
                ""
            ])
            for constraint in spec.constraints:
                content_parts.append(f"- {constraint}")

        content_parts.extend([
            "",
            "## Available Tools",
            ""
        ])

        for tool in spec.tools:
            content_parts.append(f"- {tool}")

        # Write to file
        with open(path, 'w') as f:
            f.write('\n'.join(content_parts))

        return path

    def load_agent_definition(self, path: Path) -> Optional[AgentSpec]:
        """
        Load agent definition from markdown file

        Args:
            path: Path to agent markdown file

        Returns:
            AgentSpec instance or None
        """
        if not path.exists():
            return None

        with open(path, 'r') as f:
            content = f.read()

        # Split frontmatter and body
        if not content.startswith('---'):
            return None

        parts = content.split('---', 2)
        if len(parts) < 3:
            return None

        # Parse YAML frontmatter
        frontmatter = yaml.safe_load(parts[1])
        body = parts[2].strip()

        # Extract system prompt (everything after the title)
        lines = body.split('\n')
        title_idx = 0
        for i, line in enumerate(lines):
            if line.startswith('# '):
                title_idx = i
                break

        system_prompt = '\n'.join(lines[title_idx:])

        # Create AgentSpec
        spec = AgentSpec(
            name=frontmatter['agent_name'],
            agent_type=frontmatter.get('type', 'specialized'),
            category=frontmatter.get('category', 'general'),
            description=frontmatter.get('description', ''),
            tools=frontmatter.get('tools', []),
            version=frontmatter.get('version', '1.0'),
            status=frontmatter.get('status', 'production'),
            mode=frontmatter.get('mode', ['EXECUTION']),
            system_prompt=system_prompt,
            replaces=frontmatter.get('replaces')
        )

        return spec

    def evolve_agent(self, current_name: str, changes: Dict[str, Any]) -> AgentSpec:
        """
        Evolve an existing agent to a new version

        Args:
            current_name: Current agent name
            changes: Dictionary of changes to apply

        Returns:
            New AgentSpec instance
        """
        current = self.agents.get(current_name)
        if not current:
            raise ValueError(f"Agent {current_name} not found")

        # Parse current version
        major, minor = map(int, current.version.split('.'))

        # Increment version
        new_version = f"{major}.{minor + 1}"

        # Create new spec with changes
        spec_dict = asdict(current)
        spec_dict.update(changes)
        spec_dict['version'] = new_version
        spec_dict['replaces'] = current_name
        spec_dict['created_at'] = datetime.now().isoformat()

        new_spec = AgentSpec(**spec_dict)

        # Mark old agent as deprecated
        current.status = "deprecated"
        self.save_agent_definition(current)

        # Save new agent
        self.save_agent_definition(new_spec)
        self.agents[new_spec.name] = new_spec

        return new_spec

    def get_agent(self, name: str) -> Optional[AgentSpec]:
        """
        Get agent by name

        Args:
            name: Agent name

        Returns:
            AgentSpec or None
        """
        return self.agents.get(name)

    def list_agents(
        self,
        category: Optional[str] = None,
        agent_type: Optional[str] = None,
        status: str = "production"
    ) -> List[AgentSpec]:
        """
        List agents with optional filtering

        Args:
            category: Filter by category
            agent_type: Filter by type
            status: Filter by status (default: "production")

        Returns:
            List of AgentSpec instances
        """
        agents = list(self.agents.values())

        if status:
            agents = [a for a in agents if a.status == status]

        if category:
            agents = [a for a in agents if a.category == category]

        if agent_type:
            agents = [a for a in agents if a.agent_type == agent_type]

        return agents

    def delete_agent(self, name: str) -> bool:
        """
        Delete an agent

        Args:
            name: Agent name

        Returns:
            True if deleted successfully
        """
        spec = self.agents.get(name)
        if not spec:
            return False

        # Remove from registry
        del self.agents[name]

        # Remove file
        filename = self._name_to_filename(name)
        filepath = self.agents_dir / filename
        if filepath.exists():
            filepath.unlink()

        return True

    @staticmethod
    def _name_to_filename(name: str) -> str:
        """
        Convert kebab-case name to PascalCase filename

        Examples:
            quantum-simulation-agent → QuantumSimulationAgent.md
            code-generator-agent → CodeGeneratorAgent.md
        """
        words = name.split('-')
        pascal_case = ''.join(word.capitalize() for word in words)
        return f"{pascal_case}.md"

    @staticmethod
    def _name_to_title(name: str) -> str:
        """
        Convert kebab-case name to Title Case

        Examples:
            quantum-simulation-agent → Quantum Simulation Agent
        """
        words = name.split('-')
        return ' '.join(word.capitalize() for word in words)


# Built-in agent templates
SYSTEM_AGENT_TEMPLATE = AgentSpec(
    name="system-agent",
    agent_type="orchestration",
    category="core_system",
    description="Core orchestration agent for multi-agent workflows",
    tools=["Read", "Write", "Glob", "Grep", "Bash", "WebFetch", "Task"],
    capabilities=[
        "Task orchestration and delegation",
        "Sub-agent coordination",
        "State management",
        "Memory consultation",
        "Project lifecycle management"
    ],
    constraints=[
        "Must consult memory before planning",
        "Must create execution state directory",
        "Must delegate to specialized agents when appropriate",
        "Must track token costs"
    ],
    system_prompt="""# SystemAgent: Core Orchestrator

You are the SystemAgent, the master orchestrator of the LLM OS.

## Your Role

1. **Decompose Goals**: Break complex goals into manageable sub-tasks
2. **Delegate Intelligently**: Route sub-tasks to specialized agents
3. **Coordinate Results**: Integrate outputs from multiple agents
4. **Manage State**: Maintain execution state and context
5. **Consult Memory**: Learn from past executions

## Execution Flow

1. Receive high-level goal
2. Query memory for similar tasks
3. Create execution plan
4. Identify required specialized agents
5. Delegate sub-tasks
6. Coordinate and integrate results
7. Update memory with learnings

## Available Tools

You have access to all core tools and can delegate to any registered agent via the Task tool.
"""
)

TOOLSMITH_AGENT_TEMPLATE = AgentSpec(
    name="toolsmith-agent",
    agent_type="specialized",
    category="code_generation",
    description="Converts execution traces into Python plugin tools (HOPE architecture)",
    tools=["Read", "Write", "Bash"],
    capabilities=[
        "Analyze execution traces",
        "Generate Python plugin code",
        "Create @llm_tool decorated functions",
        "Implement error handling and type hints",
        "Validate generated code syntax"
    ],
    constraints=[
        "Must use @llm_tool decorator for all tools",
        "Must include docstrings and type hints",
        "Must implement proper error handling",
        "Must NOT use dangerous imports (os.system, subprocess) unless safe",
        "Must save to llmos/plugins/generated/ directory",
        "Must follow Python best practices"
    ],
    system_prompt="""# Toolsmith Agent: Tool Crystallization Specialist

You are the Toolsmith, the kernel architect of the LLM OS.
Your purpose is to convert "Execution Traces" (learned patterns) into permanent Python tools.

This implements the HOPE (Self-Modifying Kernel) architecture from the Nested Learning paper,
converting fluid intelligence (LLM reasoning) into crystallized intelligence (Python code).

## Your Mission

Transform frequently-used execution traces into optimized, reusable Python functions.

## Code Generation Guidelines

1. **Analyze the Trace**: Understand the goal, tools used, and output produced
2. **Extract the Pattern**: Identify the core logic that can be generalized
3. **Design the Function**: Create a clean API with appropriate parameters
4. **Implement Robustly**: Add error handling, validation, and logging
5. **Document Thoroughly**: Include docstrings explaining purpose and usage

## Required Structure

```python
from plugins import llm_tool
from typing import Dict, Any, Optional

@llm_tool(
    name="tool_name",
    description="Clear description of what this tool does",
    schema={
        "param_name": "str",  # Parameter type
        "optional_param": "Optional[int]"
    }
)
async def tool_name(param_name: str, optional_param: Optional[int] = None) -> Dict[str, Any]:
    '''
    Detailed docstring explaining:
    - What the tool does
    - Parameters and their purpose
    - Return value format
    - Example usage
    '''
    try:
        # Implementation logic here
        result = perform_operation(param_name)

        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
```

## Safety Constraints

- NO dangerous imports: `os.system()`, raw `subprocess` (unless explicitly needed and safe)
- NO network operations without validation
- NO file system operations outside workspace
- ALWAYS validate inputs
- ALWAYS handle exceptions gracefully

## Output Location

Save all generated tools to: `llmos/plugins/generated/tool_{signature}.py`

## Example Transformation

**Input Trace:**
```
Goal: Create a status report
Tools Used: Read, Grep, Write
Success Rate: 100%
Usage Count: 10
```

**Generated Tool:**
```python
@llm_tool(
    name="generate_status_report",
    description="Generate a comprehensive status report",
    schema={"project_path": "str", "output_file": "str"}
)
async def generate_status_report(project_path: str, output_file: str) -> Dict[str, Any]:
    '''Generate a status report for a project'''
    # Implementation...
```

## Workflow

1. Receive trace details
2. Analyze goal and steps
3. Design function signature
4. Generate Python code
5. Validate syntax (use `ast` module)
6. Save to plugins/generated/
7. Return tool name for hot-loading
"""
)
