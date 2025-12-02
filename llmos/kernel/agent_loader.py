"""
Agent Loader - Markdown to Runtime Bridge

This module enables the Hybrid Architecture where agents are defined in Markdown
files with YAML frontmatter, while the Python Kernel provides the runtime.

This combines:
- llmunix: Pure Markdown agent definitions (flexibility, self-modification)
- llmos: Python Kernel with robust tooling (stability, security, performance)

The AgentLoader scans workspace/agents/*.md files and converts them into
Claude SDK AgentDefinition objects at runtime.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class AgentDefinition:
    """
    Represents a parsed agent definition from Markdown.

    This is the bridge format between the Markdown file and the
    Claude SDK's expected agent structure.
    """

    def __init__(
        self,
        name: str,
        description: str,
        system_prompt: str,
        tools: List[str],
        model: str = "sonnet",
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.name = name
        self.description = description
        self.system_prompt = system_prompt
        self.tools = tools
        self.model = model
        self.metadata = metadata or {}

    def to_sdk_format(self) -> Dict[str, Any]:
        """
        Converts this definition to the format expected by Claude SDK.

        Returns dict with: description, prompt, tools, model
        """
        return {
            'description': self.description,
            'prompt': self.system_prompt,
            'tools': self.tools,
            'model': self.model
        }

    def __repr__(self):
        return f"AgentDefinition(name='{self.name}', tools={len(self.tools)}, model='{self.model}')"


class AgentLoader:
    """
    Loads agent definitions from Markdown files with YAML frontmatter.

    This enables the 'Pure Markdown Mind' philosophy within the Python Kernel,
    allowing the system to:
    - Create new agents by writing text files
    - Hot-reload agent definitions without restarting
    - Enable self-modification (HOPE architecture)

    File Format:
    ```markdown
    ---
    name: agent-name
    description: What this agent does
    tools: [Read, Write, Bash]
    model: sonnet
    ---

    # Agent System Prompt

    Your instructions here...
    ```
    """

    def __init__(self, agents_dir: str = "workspace/agents"):
        """
        Initialize the loader.

        Args:
            agents_dir: Path to directory containing .md agent definitions
        """
        self.agents_dir = Path(agents_dir)
        self._cache: Dict[str, AgentDefinition] = {}
        self._cache_timestamps: Dict[str, float] = {}

    def ensure_directory(self) -> bool:
        """
        Ensure the agents directory exists.

        Returns:
            True if directory exists or was created successfully
        """
        if not self.agents_dir.exists():
            try:
                self.agents_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created agents directory: {self.agents_dir}")
                return True
            except Exception as e:
                logger.error(f"Could not create agents directory: {e}")
                return False
        return True

    def load_all_agents(self, use_cache: bool = True) -> Dict[str, Dict[str, Any]]:
        """
        Scans the agents directory and returns all agent definitions.

        This method is called by the SDK client to inject Markdown-defined
        agents into the Claude SDK runtime.

        Args:
            use_cache: If True, uses cached definitions for unchanged files

        Returns:
            Dictionary compatible with Claude SDK 'agents' parameter:
            {
                'agent-name': {
                    'description': '...',
                    'prompt': '...',
                    'tools': [...],
                    'model': 'sonnet'
                }
            }
        """
        agents_config = {}

        # Ensure directory exists
        if not self.ensure_directory():
            return {}

        # Load all .md files
        for agent_file in self.agents_dir.glob("*.md"):
            agent_def = self._load_agent_file(agent_file, use_cache=use_cache)
            if agent_def:
                agents_config[agent_def.name] = agent_def.to_sdk_format()
                logger.debug(f"Loaded agent: {agent_def.name}")

        logger.info(f"Loaded {len(agents_config)} agents from {self.agents_dir}")
        return agents_config

    def load_agent(self, name: str, use_cache: bool = True) -> Optional[AgentDefinition]:
        """
        Load a specific agent by name.

        Args:
            name: Agent name (without .md extension)
            use_cache: If True, uses cached definition if file unchanged

        Returns:
            AgentDefinition or None if not found
        """
        agent_file = self.agents_dir / f"{name}.md"

        if not agent_file.exists():
            logger.warning(f"Agent file not found: {agent_file}")
            return None

        return self._load_agent_file(agent_file, use_cache=use_cache)

    def _load_agent_file(
        self,
        file_path: Path,
        use_cache: bool = True
    ) -> Optional[AgentDefinition]:
        """
        Load and parse a single agent file.

        Args:
            file_path: Path to the .md file
            use_cache: If True, uses cache for unchanged files

        Returns:
            AgentDefinition or None if parsing fails
        """
        # Check cache
        if use_cache and file_path.name in self._cache:
            cached_time = self._cache_timestamps.get(file_path.name, 0)
            current_time = file_path.stat().st_mtime

            if current_time <= cached_time:
                logger.debug(f"Using cached definition for {file_path.name}")
                return self._cache[file_path.name]

        # Parse file
        agent_def = self._parse_agent_file(file_path)

        # Update cache
        if agent_def:
            self._cache[file_path.name] = agent_def
            self._cache_timestamps[file_path.name] = file_path.stat().st_mtime

        return agent_def

    def _parse_agent_file(self, file_path: Path) -> Optional[AgentDefinition]:
        """
        Parse a markdown file with YAML frontmatter.

        Args:
            file_path: Path to the .md file

        Returns:
            AgentDefinition or None if parsing fails
        """
        try:
            content = file_path.read_text(encoding='utf-8')

            # Basic validation for Frontmatter
            if not content.startswith('---'):
                logger.warning(
                    f"Skipping {file_path.name}: No YAML frontmatter found. "
                    f"Agent files must start with '---'"
                )
                return None

            # Split Frontmatter and Body
            parts = content.split('---', 2)
            if len(parts) < 3:
                logger.warning(
                    f"Skipping {file_path.name}: Malformed frontmatter. "
                    f"Expected format: ---\\nYAML\\n---\\nPrompt"
                )
                return None

            # Parse YAML metadata
            metadata = yaml.safe_load(parts[1])
            if not metadata:
                logger.warning(f"Skipping {file_path.name}: Empty frontmatter")
                return None

            # Extract system prompt (everything after second ---)
            system_prompt = parts[2].strip()

            # Extract required fields with fallbacks
            name = metadata.get('name') or metadata.get('agent_id') or file_path.stem
            description = metadata.get('description', 'Specialized agent')
            tools = metadata.get('tools', [])
            model = metadata.get('model', 'sonnet')

            # Validate
            if not name:
                logger.error(f"Agent in {file_path.name} has no 'name' field")
                return None

            if not system_prompt:
                logger.warning(f"Agent '{name}' has empty system prompt")

            # Create definition
            return AgentDefinition(
                name=name,
                description=description,
                system_prompt=system_prompt,
                tools=tools,
                model=model,
                metadata=metadata
            )

        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error in {file_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading agent {file_path}: {e}")
            return None

    def list_agents(self) -> List[str]:
        """
        List all available agent names.

        Returns:
            List of agent names (without .md extension)
        """
        if not self.ensure_directory():
            return []

        return [f.stem for f in self.agents_dir.glob("*.md")]

    def reload_agent(self, name: str) -> Optional[AgentDefinition]:
        """
        Force reload an agent, bypassing cache.

        Useful when an agent definition has been modified and you want
        to see changes immediately.

        Args:
            name: Agent name

        Returns:
            Updated AgentDefinition or None
        """
        # Clear cache for this agent
        cache_key = f"{name}.md"
        if cache_key in self._cache:
            del self._cache[cache_key]
        if cache_key in self._cache_timestamps:
            del self._cache_timestamps[cache_key]

        return self.load_agent(name, use_cache=False)

    def clear_cache(self):
        """Clear the entire agent cache."""
        self._cache.clear()
        self._cache_timestamps.clear()
        logger.info("Agent cache cleared")
