"""
Component Registry - Central registry for agents and tools
Brings llmunix's SmartLibrary concept to llmos
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Any
from kernel.agent_factory import AgentSpec


@dataclass
class ToolSpec:
    """Tool specification"""
    name: str
    description: str
    category: str
    version: str = "1.0"
    status: str = "production"


class ComponentRegistry:
    """
    Central registry for all system and project components

    Equivalent to llmunix's SmartLibrary - provides:
    - Agent registry and discovery
    - Tool registry and discovery
    - Capability-based agent selection
    - Component metadata and versioning
    """

    def __init__(self):
        """Initialize component registry"""
        self.agents: Dict[str, AgentSpec] = {}
        self.tools: Dict[str, ToolSpec] = {}

    def register_agent(self, agent: AgentSpec):
        """
        Register an agent in the registry

        Args:
            agent: AgentSpec to register
        """
        self.agents[agent.name] = agent

    def register_tool(self, tool: ToolSpec):
        """
        Register a tool in the registry

        Args:
            tool: ToolSpec to register
        """
        self.tools[tool.name] = tool

    def get_agent(self, name: str) -> Optional[AgentSpec]:
        """
        Get agent by name

        Args:
            name: Agent name

        Returns:
            AgentSpec or None
        """
        return self.agents.get(name)

    def get_tool(self, name: str) -> Optional[ToolSpec]:
        """
        Get tool by name

        Args:
            name: Tool name

        Returns:
            ToolSpec or None
        """
        return self.tools.get(name)

    def find_agent_for_capability(self, capability: str) -> Optional[AgentSpec]:
        """
        Find an agent with a specific capability

        Args:
            capability: Capability description

        Returns:
            Best matching AgentSpec or None
        """
        # Simple keyword matching for now
        # TODO: Implement semantic matching
        capability_lower = capability.lower()

        for agent in self.agents.values():
            if agent.status == "deprecated":
                continue

            # Check in capabilities list
            for agent_capability in agent.capabilities:
                if capability_lower in agent_capability.lower():
                    return agent

            # Check in description
            if capability_lower in agent.description.lower():
                return agent

        return None

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
            status: Filter by status

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

    def list_tools(
        self,
        category: Optional[str] = None,
        status: str = "production"
    ) -> List[ToolSpec]:
        """
        List tools with optional filtering

        Args:
            category: Filter by category
            status: Filter by status

        Returns:
            List of ToolSpec instances
        """
        tools = list(self.tools.values())

        if status:
            tools = [t for t in tools if t.status == status]

        if category:
            tools = [t for t in tools if t.category == category]

        return tools

    def get_agent_selection_guidance(self, goal: str) -> List[AgentSpec]:
        """
        Get recommended agents for a goal

        Args:
            goal: Natural language goal

        Returns:
            List of recommended agents (ordered by relevance)
        """
        # TODO: Implement semantic matching
        # For now, simple keyword matching

        goal_lower = goal.lower()
        scored_agents = []

        for agent in self.agents.values():
            if agent.status == "deprecated":
                continue

            score = 0

            # Check description
            if any(word in agent.description.lower() for word in goal_lower.split()):
                score += 2

            # Check category
            if agent.category.lower() in goal_lower:
                score += 3

            # Check capabilities
            for capability in agent.capabilities:
                if any(word in capability.lower() for word in goal_lower.split()):
                    score += 1

            if score > 0:
                scored_agents.append((score, agent))

        # Sort by score descending
        scored_agents.sort(key=lambda x: x[0], reverse=True)

        return [agent for _, agent in scored_agents]

    def export_registry(self) -> Dict[str, Any]:
        """
        Export registry as dictionary

        Returns:
            Dictionary representation of registry
        """
        return {
            "agents": {
                name: {
                    "name": agent.name,
                    "type": agent.agent_type,
                    "category": agent.category,
                    "description": agent.description,
                    "version": agent.version,
                    "status": agent.status,
                    "tools": agent.tools,
                    "capabilities": agent.capabilities
                }
                for name, agent in self.agents.items()
            },
            "tools": {
                name: {
                    "name": tool.name,
                    "description": tool.description,
                    "category": tool.category,
                    "version": tool.version,
                    "status": tool.status
                }
                for name, tool in self.tools.items()
            }
        }
