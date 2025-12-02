"""
System Tools - Meta-Operations for Self-Modification

This module provides tools that enable the system to modify itself,
implementing the "HOPE" (Higher-Order Programming Evolution) architecture.

Key capabilities:
- create_agent: Write new agent definitions
- list_agents: Discover available agents
- reload_agent: Hot-reload modified agents

This enables the system to:
1. Create specialized agents on-demand
2. Evolve its capabilities through self-modification
3. Adapt to new tasks without human intervention
"""

import json
import os
from pathlib import Path
from typing import List, Optional
from datetime import datetime
import logging

from plugins import llm_tool

logger = logging.getLogger(__name__)


@llm_tool(
    "create_agent",
    "Creates a new specialized agent by writing a Markdown definition file. "
    "The agent becomes immediately available for delegation via the Task tool. "
    "Use this when you need capabilities that don't exist in current agents.",
    {
        "name": "str - Kebab-case unique identifier (e.g. 'quantum-researcher', 'code-optimizer')",
        "description": "str - SHORT description of when to use this agent (1-2 sentences). "
                      "This helps the system decide when to delegate to this agent.",
        "tools": "List[str] - Tool names this agent needs (e.g. ['WebFetch', 'Write', 'Bash']). "
                "Only grant tools the agent truly needs for security.",
        "system_prompt": "str - Detailed instructions for agent behavior. Include protocols, "
                        "constraints, and examples. This is the agent's 'brain'."
    }
)
async def create_agent(
    name: str,
    description: str,
    tools: List[str],
    system_prompt: str
) -> str:
    """
    Creates a new agent definition file in workspace/agents/.

    This enables the "HOPE" evolution pattern where the system can spawn
    new specialized capabilities by writing text files.

    Args:
        name: Kebab-case agent identifier (e.g. 'data-analyst')
        description: Short description for agent selection
        tools: List of tool names to grant access to
        system_prompt: Detailed agent instructions

    Returns:
        Success/error message

    Example:
        create_agent(
            name="security-auditor",
            description="Reviews code for security vulnerabilities",
            tools=["Read", "Grep", "Bash"],
            system_prompt="You are a security expert. Review code for: SQL injection, XSS..."
        )
    """
    # Validate name format
    if not name:
        return "❌ Error: Agent name cannot be empty."

    if " " in name or "_" in name:
        return (
            "❌ Error: Agent name must be kebab-case (lowercase with hyphens). "
            f"Example: 'quantum-researcher' not '{name}'"
        )

    if not name.replace("-", "").isalnum():
        return (
            "❌ Error: Agent name must contain only lowercase letters, numbers, and hyphens."
        )

    # Validate description
    if not description or len(description.strip()) < 10:
        return (
            "❌ Error: Description must be at least 10 characters. "
            "It helps the system decide when to use this agent."
        )

    # Validate tools
    if not tools:
        logger.warning(f"Creating agent '{name}' with no tools. It will have limited capabilities.")

    # Validate system prompt
    if not system_prompt or len(system_prompt.strip()) < 20:
        return (
            "❌ Error: System prompt must be at least 20 characters. "
            "Provide detailed instructions for the agent's behavior."
        )

    # Construct file path
    agents_dir = Path("workspace/agents")
    file_path = agents_dir / f"{name}.md"

    # Ensure directory exists
    try:
        agents_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        return f"❌ Error: Could not create agents directory: {e}"

    # Check if agent already exists
    if file_path.exists():
        return (
            f"❌ Error: Agent '{name}' already exists at {file_path}. "
            f"To modify it, edit the file directly or delete it first."
        )

    # Create agent definition content
    content = f"""---
agent_name: {name}
description: {description}
tools: {json.dumps(tools)}
model: sonnet
version: "1.0"
created_at: "{datetime.now().isoformat()}"
created_by: "system (self-modification)"
---

{system_prompt.strip()}
"""

    # Write file
    try:
        file_path.write_text(content, encoding='utf-8')
        logger.info(f"Created agent '{name}' at {file_path}")

        return (
            f"✅ Agent '{name}' created successfully!\n\n"
            f"📁 Location: {file_path}\n"
            f"🔧 Tools: {', '.join(tools)}\n\n"
            f"You can now use this agent by calling:\n"
            f'  Task(agent="{name}", goal="your task here")\n\n'
            f"The agent will be automatically loaded on the next Task execution."
        )

    except Exception as e:
        logger.error(f"Failed to create agent '{name}': {e}")
        return f"❌ Error: Failed to write agent file: {e}"


@llm_tool(
    "list_agents",
    "Lists all available agents (both Markdown-defined and programmatic). "
    "Use this to discover what specialized capabilities are available.",
    {}
)
async def list_agents() -> str:
    """
    Lists all available agents in the system.

    Returns:
        Formatted list of agent names and descriptions
    """
    agents_dir = Path("workspace/agents")

    if not agents_dir.exists():
        return "📂 No agents directory found. No Markdown agents available."

    # Find all .md files
    agent_files = list(agents_dir.glob("*.md"))

    if not agent_files:
        return (
            "📂 Agents directory exists but is empty.\n\n"
            "💡 You can create new agents using the create_agent tool."
        )

    # Parse basic info from each file
    agents_info = []
    for file_path in sorted(agent_files):
        try:
            content = file_path.read_text(encoding='utf-8')

            # Quick parse for name and description
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 2:
                    import yaml
                    metadata = yaml.safe_load(parts[1])
                    if metadata:
                        name = metadata.get('name', file_path.stem)
                        description = metadata.get('description', 'No description')
                        tools = metadata.get('tools', [])

                        agents_info.append({
                            'name': name,
                            'description': description,
                            'tools': tools,
                            'file': file_path.name
                        })
        except Exception as e:
            logger.warning(f"Could not parse {file_path.name}: {e}")

    if not agents_info:
        return "⚠️ Found agent files but could not parse any successfully."

    # Format output
    output = f"📋 Available Agents ({len(agents_info)}):\n\n"

    for info in agents_info:
        output += f"**{info['name']}**\n"
        output += f"  📝 {info['description']}\n"
        output += f"  🔧 Tools: {', '.join(info['tools']) if info['tools'] else 'None'}\n"
        output += f"  📁 File: {info['file']}\n\n"

    output += (
        "💡 To use an agent: Task(agent=\"agent-name\", goal=\"your task\")\n"
        "💡 To create new agent: create_agent(name=\"...\", ...)"
    )

    return output


@llm_tool(
    "modify_agent",
    "Modifies an existing agent by updating its Markdown file. "
    "Use this to improve agent instructions based on experience.",
    {
        "name": "str - Name of the agent to modify",
        "field": "str - Field to modify: 'description', 'tools', or 'prompt'",
        "value": "str or List[str] - New value for the field"
    }
)
async def modify_agent(name: str, field: str, value: any) -> str:
    """
    Modifies an existing agent definition.

    This enables the system to evolve agent capabilities based on experience.

    Args:
        name: Agent name
        field: Field to modify ('description', 'tools', 'prompt')
        value: New value

    Returns:
        Success/error message
    """
    agents_dir = Path("workspace/agents")
    file_path = agents_dir / f"{name}.md"

    if not file_path.exists():
        return (
            f"❌ Error: Agent '{name}' not found.\n"
            f"Available agents: {', '.join([f.stem for f in agents_dir.glob('*.md')])}"
        )

    try:
        content = file_path.read_text(encoding='utf-8')

        if not content.startswith('---'):
            return f"❌ Error: Agent file {file_path.name} has invalid format."

        # Split frontmatter and body
        parts = content.split('---', 2)
        if len(parts) < 3:
            return f"❌ Error: Agent file {file_path.name} has malformed frontmatter."

        import yaml
        metadata = yaml.safe_load(parts[1])
        system_prompt = parts[2].strip()

        # Modify requested field
        if field == 'description':
            metadata['description'] = value
        elif field == 'tools':
            if isinstance(value, str):
                value = json.loads(value)
            metadata['tools'] = value
        elif field == 'prompt' or field == 'system_prompt':
            system_prompt = value
        else:
            return (
                f"❌ Error: Unknown field '{field}'. "
                f"Valid fields: description, tools, prompt"
            )

        # Add modification timestamp
        metadata['modified_at'] = datetime.now().isoformat()
        metadata['modified_by'] = "system (self-improvement)"

        # Reconstruct file
        new_content = f"""---
{yaml.dump(metadata, default_flow_style=False, sort_keys=False)}---

{system_prompt}
"""

        # Write back
        file_path.write_text(new_content, encoding='utf-8')

        logger.info(f"Modified agent '{name}' field '{field}'")

        return (
            f"✅ Agent '{name}' updated successfully!\n\n"
            f"📝 Modified: {field}\n"
            f"📁 File: {file_path}\n\n"
            f"The changes will take effect on the next Task execution."
        )

    except Exception as e:
        logger.error(f"Failed to modify agent '{name}': {e}")
        return f"❌ Error: {e}"
