"""
Workflow Engine for LLMos-Lite

Enables treating Skills as executable Nodes in a computational graph.
Supports WebAssembly execution in the browser for:
- Python (Pyodide) - Quantum computing, data science
- JavaScript - 3D graphics, animations
- SPICE (Ngspice.js) - Electronic circuits

Architecture:
- Skills become Nodes with inputs/outputs
- Workflows are DAGs (Directed Acyclic Graphs)
- Execution happens in browser via Wasm
- Results feed back into Memory for learning

Node Types:
- PythonNode: Runs Python code via Pyodide
- JavaScriptNode: Runs JS directly
- SPICENode: Simulates circuits via Ngspice.js
- ThreeJSNode: Renders 3D scenes
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import json
import re


class NodeType(Enum):
    """Types of executable nodes"""
    PYTHON_WASM = "python-wasm"        # Pyodide
    JAVASCRIPT = "javascript"          # Native JS
    SPICE = "spice"                    # Circuit simulation
    THREEJS = "threejs"                # 3D rendering
    QISKIT = "qiskit"                  # Quantum (Pyodide + micro-qiskit)


class ExecutionMode(Enum):
    """Where the node executes"""
    BROWSER_WASM = "browser-wasm"      # Client-side Wasm
    SERVER_PYTHON = "server-python"    # Server fallback (for heavy compute)
    HYBRID = "hybrid"                  # Start in browser, escalate if needed


@dataclass
class NodeInput:
    """Input parameter for a node"""
    name: str
    type: str  # "number", "string", "array", "object", "image"
    description: str
    default: Any = None
    required: bool = True


@dataclass
class NodeOutput:
    """Output from a node"""
    name: str
    type: str
    description: str


@dataclass
class ExecutableSkill:
    """
    A skill that can be executed as a node in a workflow.

    This extends the basic Skill format with executable code and I/O spec.
    """
    skill_id: str
    name: str
    description: str
    node_type: NodeType
    execution_mode: ExecutionMode

    # I/O Specification
    inputs: List[NodeInput]
    outputs: List[NodeOutput]

    # Executable code
    code: str

    # Metadata
    category: str = "general"
    tags: List[str] = field(default_factory=list)
    version: str = "1.0.0"
    author: str = "system"

    # Performance hints
    estimated_time_ms: int = 100
    memory_mb: int = 10

    def to_markdown(self) -> str:
        """
        Convert to Markdown format for storage.

        Format:
        ---
        name: Node Name
        type: python-wasm
        execution_mode: browser-wasm
        category: quantum
        inputs:
          - name: iterations
            type: number
            default: 100
        outputs:
          - name: result
            type: number
        ---

        # Code

        ```python
        def execute(inputs):
            # Node logic
            return {"result": 42}
        ```
        """
        # Build frontmatter
        inputs_yaml = "\n".join([
            f"  - name: {inp.name}\n"
            f"    type: {inp.type}\n"
            f"    description: {inp.description}\n"
            f"    default: {json.dumps(inp.default)}\n"
            f"    required: {inp.required}"
            for inp in self.inputs
        ])

        outputs_yaml = "\n".join([
            f"  - name: {out.name}\n"
            f"    type: {out.type}\n"
            f"    description: {out.description}"
            for out in self.outputs
        ])

        tags_yaml = json.dumps(self.tags)

        # Determine code fence language
        lang_map = {
            NodeType.PYTHON_WASM: "python",
            NodeType.QISKIT: "python",
            NodeType.JAVASCRIPT: "javascript",
            NodeType.THREEJS: "javascript",
            NodeType.SPICE: "spice"
        }
        lang = lang_map.get(self.node_type, "python")

        return f"""---
skill_id: {self.skill_id}
name: {self.name}
description: {self.description}
type: {self.node_type.value}
execution_mode: {self.execution_mode.value}
category: {self.category}
tags: {tags_yaml}
version: {self.version}
author: {self.author}
estimated_time_ms: {self.estimated_time_ms}
memory_mb: {self.memory_mb}
inputs:
{inputs_yaml}
outputs:
{outputs_yaml}
---

# {self.name}

{self.description}

## Inputs
{chr(10).join([f"- **{inp.name}** ({inp.type}): {inp.description}" for inp in self.inputs])}

## Outputs
{chr(10).join([f"- **{out.name}** ({out.type}): {out.description}" for out in self.outputs])}

## Code

```{lang}
{self.code}
```

## Usage Notes

This node executes in {self.execution_mode.value}.
Estimated execution time: {self.estimated_time_ms}ms
Memory usage: ~{self.memory_mb}MB
"""

    def to_browser_payload(self) -> Dict[str, Any]:
        """
        Convert to JSON payload for browser execution.

        Returns:
            Dict ready to send to browser for Wasm execution
        """
        return {
            "nodeId": self.skill_id,
            "name": self.name,
            "type": self.node_type.value,
            "executionMode": self.execution_mode.value,
            "inputs": [
                {
                    "name": inp.name,
                    "type": inp.type,
                    "description": inp.description,
                    "default": inp.default,
                    "required": inp.required
                }
                for inp in self.inputs
            ],
            "outputs": [
                {
                    "name": out.name,
                    "type": out.type,
                    "description": out.description
                }
                for out in self.outputs
            ],
            "code": self.code,
            "metadata": {
                "category": self.category,
                "tags": self.tags,
                "version": self.version,
                "estimatedTimeMs": self.estimated_time_ms,
                "memoryMb": self.memory_mb
            }
        }


@dataclass
class WorkflowNode:
    """A node instance in a workflow"""
    node_id: str
    skill_id: str  # Reference to ExecutableSkill
    position: Dict[str, float]  # {"x": 100, "y": 200}
    input_values: Dict[str, Any] = field(default_factory=dict)  # User-set inputs

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodeId": self.node_id,
            "skillId": self.skill_id,
            "position": self.position,
            "inputValues": self.input_values
        }


@dataclass
class WorkflowEdge:
    """Connection between nodes"""
    edge_id: str
    source_node_id: str
    source_output: str
    target_node_id: str
    target_input: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "edgeId": self.edge_id,
            "source": self.source_node_id,
            "sourceOutput": self.source_output,
            "target": self.target_node_id,
            "targetInput": self.target_input
        }


@dataclass
class Workflow:
    """
    A workflow (computational graph) composed of executable skills.

    Workflows are DAGs where:
    - Nodes are ExecutableSkills
    - Edges pass data between node outputs and inputs
    - Execution happens topologically (respecting dependencies)
    """
    workflow_id: str
    name: str
    description: str
    nodes: List[WorkflowNode]
    edges: List[WorkflowEdge]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict"""
        return {
            "workflowId": self.workflow_id,
            "name": self.name,
            "description": self.description,
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
            "metadata": self.metadata
        }

    def to_markdown(self) -> str:
        """
        Convert workflow to Markdown for storage in Git.

        Format:
        ---
        workflow_id: my-workflow
        name: My Workflow
        description: Does something cool
        ---

        # Workflow: My Workflow

        ## Nodes
        - node_1: VQE Simulation
        - node_2: Plot Results

        ## Connections
        - node_1.eigenvalue → node_2.data

        ## Configuration
        ```json
        {full workflow JSON}
        ```
        """
        nodes_list = "\n".join([
            f"- **{node.node_id}**: {node.skill_id}"
            for node in self.nodes
        ])

        edges_list = "\n".join([
            f"- {edge.source_node_id}.{edge.source_output} → "
            f"{edge.target_node_id}.{edge.target_input}"
            for edge in self.edges
        ])

        config_json = json.dumps(self.to_dict(), indent=2)

        return f"""---
workflow_id: {self.workflow_id}
name: {self.name}
description: {self.description}
---

# Workflow: {self.name}

{self.description}

## Nodes

{nodes_list}

## Connections

{edges_list}

## Configuration

```json
{config_json}
```
"""


class ExecutableSkillParser:
    """
    Parses Markdown files into ExecutableSkill objects.

    Handles the extended skill format with inputs/outputs and executable code.
    """

    @staticmethod
    def parse(content: str) -> Optional[ExecutableSkill]:
        """Parse Markdown content into ExecutableSkill"""

        # Check for frontmatter
        if not content.startswith('---'):
            return None

        parts = content.split('---', 2)
        if len(parts) < 3:
            return None

        frontmatter = parts[1].strip()
        body = parts[2].strip()

        # Parse frontmatter (simplified YAML parsing)
        metadata = {}
        current_key = None
        current_list = []

        for line in frontmatter.split('\n'):
            line = line.rstrip()

            # Handle list items
            if line.startswith('  - ') and current_key:
                current_list.append(line[4:])
            # Handle key-value pairs
            elif ':' in line and not line.startswith('  '):
                if current_key and current_list:
                    metadata[current_key] = current_list
                    current_list = []

                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()

                # Check if this starts a list
                if not value:
                    current_key = key
                else:
                    metadata[key] = value
                    current_key = None

        # Handle last list
        if current_key and current_list:
            metadata[current_key] = current_list

        # Extract code block
        code_match = re.search(r'```(?:python|javascript|spice)\n(.*?)\n```', body, re.DOTALL)
        code = code_match.group(1) if code_match else ""

        # Parse inputs (from frontmatter list)
        inputs = []
        if 'inputs' in metadata and isinstance(metadata['inputs'], list):
            # Parse input items (simplified)
            current_input = {}
            for item in metadata['inputs']:
                if item.startswith('name:'):
                    if current_input:
                        inputs.append(NodeInput(**current_input))
                    current_input = {'name': item.split(':', 1)[1].strip()}
                elif item.startswith('type:'):
                    current_input['type'] = item.split(':', 1)[1].strip()
                elif item.startswith('description:'):
                    current_input['description'] = item.split(':', 1)[1].strip()
                elif item.startswith('default:'):
                    try:
                        current_input['default'] = json.loads(item.split(':', 1)[1].strip())
                    except:
                        current_input['default'] = None
                elif item.startswith('required:'):
                    current_input['required'] = item.split(':', 1)[1].strip().lower() == 'true'

            if current_input:
                inputs.append(NodeInput(**current_input))

        # Parse outputs (similar to inputs)
        outputs = []
        if 'outputs' in metadata and isinstance(metadata['outputs'], list):
            current_output = {}
            for item in metadata['outputs']:
                if item.startswith('name:'):
                    if current_output:
                        outputs.append(NodeOutput(**current_output))
                    current_output = {'name': item.split(':', 1)[1].strip()}
                elif item.startswith('type:'):
                    current_output['type'] = item.split(':', 1)[1].strip()
                elif item.startswith('description:'):
                    current_output['description'] = item.split(':', 1)[1].strip()

            if current_output:
                outputs.append(NodeOutput(**current_output))

        # Parse tags
        tags = []
        if 'tags' in metadata:
            try:
                tags = json.loads(metadata['tags'])
            except:
                tags = []

        # Create ExecutableSkill
        try:
            return ExecutableSkill(
                skill_id=metadata.get('skill_id', 'unknown'),
                name=metadata.get('name', 'Unnamed Skill'),
                description=metadata.get('description', ''),
                node_type=NodeType(metadata.get('type', 'python-wasm')),
                execution_mode=ExecutionMode(metadata.get('execution_mode', 'browser-wasm')),
                inputs=inputs,
                outputs=outputs,
                code=code,
                category=metadata.get('category', 'general'),
                tags=tags,
                version=metadata.get('version', '1.0.0'),
                author=metadata.get('author', 'system'),
                estimated_time_ms=int(metadata.get('estimated_time_ms', 100)),
                memory_mb=int(metadata.get('memory_mb', 10))
            )
        except Exception as e:
            print(f"Error parsing executable skill: {e}")
            return None


class WorkflowEngine:
    """
    Manages workflow execution and skill library.

    This is the backend component that:
    - Stores ExecutableSkills
    - Manages Workflows
    - Prepares payloads for browser execution
    - Captures execution traces
    """

    def __init__(self, volume_manager):
        self.volume_manager = volume_manager
        self._skills_cache: Dict[str, ExecutableSkill] = {}

    def load_executable_skills(
        self,
        user_id: str,
        team_id: str
    ) -> List[ExecutableSkill]:
        """
        Load all executable skills from volumes.

        Only returns skills that have the executable format (inputs/outputs/code).
        """
        skills = []

        # Load from system volume
        sys_vol = self.volume_manager.get_system_volume(readonly=True)
        skills.extend(self._load_skills_from_volume(sys_vol))

        # Load from team volume
        team_vol = self.volume_manager.get_team_volume(team_id, readonly=True)
        skills.extend(self._load_skills_from_volume(team_vol))

        # Load from user volume
        user_vol = self.volume_manager.get_user_volume(user_id, readonly=False)
        skills.extend(self._load_skills_from_volume(user_vol))

        return skills

    def _load_skills_from_volume(self, volume) -> List[ExecutableSkill]:
        """Load executable skills from a volume"""
        skills = []
        skill_ids = volume.list_skills()

        for skill_id in skill_ids:
            content = volume.read_skill(skill_id)
            if content:
                skill = ExecutableSkillParser.parse(content)
                if skill:
                    skills.append(skill)
                    self._skills_cache[skill.skill_id] = skill

        return skills

    def get_skill(self, skill_id: str) -> Optional[ExecutableSkill]:
        """Get a cached executable skill by ID"""
        return self._skills_cache.get(skill_id)

    def save_workflow(
        self,
        user_id: str,
        workflow: Workflow
    ) -> bool:
        """Save a workflow to user's volume"""
        user_vol = self.volume_manager.get_user_volume(user_id)

        # Save as markdown in workflows/ subdirectory
        # (We'd need to extend GitVolume to support workflows)
        content = workflow.to_markdown()

        # For now, save in traces/ (would create workflows/ directory in production)
        return user_vol.write_trace(
            f"workflow_{workflow.workflow_id}",
            content
        )

    def prepare_for_browser(
        self,
        workflow: Workflow
    ) -> Dict[str, Any]:
        """
        Prepare workflow for browser execution.

        Returns JSON payload with all skill code and workflow structure.
        """
        # Resolve all skills
        skills_payload = {}
        for node in workflow.nodes:
            skill = self.get_skill(node.skill_id)
            if skill:
                skills_payload[skill.skill_id] = skill.to_browser_payload()

        return {
            "workflow": workflow.to_dict(),
            "skills": skills_payload
        }
