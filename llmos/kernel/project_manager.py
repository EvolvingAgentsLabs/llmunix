"""
Project Manager - Manages project lifecycle and structure
Brings llmunix-style project organization to llmos
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import json


@dataclass
class Project:
    """
    A Project in the LLM OS
    Projects provide isolation and organization for related work
    """
    name: str
    root_path: Path
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    description: str = ""
    metadata: Dict = field(default_factory=dict)

    @property
    def components_path(self) -> Path:
        """Path to components directory"""
        return self.root_path / "components"

    @property
    def agents_path(self) -> Path:
        """Path to project-specific agents"""
        return self.components_path / "agents"

    @property
    def tools_path(self) -> Path:
        """Path to project-specific tools"""
        return self.components_path / "tools"

    @property
    def input_path(self) -> Path:
        """Path to input directory"""
        return self.root_path / "input"

    @property
    def output_path(self) -> Path:
        """Path to output directory"""
        return self.root_path / "output"

    @property
    def memory_path(self) -> Path:
        """Path to memory directory"""
        return self.root_path / "memory"

    @property
    def short_term_memory_path(self) -> Path:
        """Path to short-term memory"""
        return self.memory_path / "short_term"

    @property
    def long_term_memory_path(self) -> Path:
        """Path to long-term memory (traces, learnings)"""
        return self.memory_path / "long_term"

    @property
    def state_path(self) -> Path:
        """Path to execution state"""
        return self.root_path / "state"


class ProjectManager:
    """
    Manages project lifecycle and structure

    Brings llmunix-style project organization to llmos:
    - Auto-creates project directory structure
    - Manages project isolation
    - Tracks project-specific agents and tools
    - Handles project-scoped memory
    """

    def __init__(self, workspace: Path):
        """
        Initialize ProjectManager

        Args:
            workspace: Root workspace directory
        """
        self.workspace = Path(workspace)
        self.projects_root = self.workspace / "projects"
        self.projects_root.mkdir(parents=True, exist_ok=True)

        # In-memory project registry
        self.projects: Dict[str, Project] = {}
        self._load_existing_projects()

    def _load_existing_projects(self):
        """Load existing projects from filesystem"""
        if not self.projects_root.exists():
            return

        for project_dir in self.projects_root.iterdir():
            if project_dir.is_dir() and not project_dir.name.startswith('.'):
                manifest_path = project_dir / "project.json"
                if manifest_path.exists():
                    with open(manifest_path, 'r') as f:
                        data = json.load(f)

                    project = Project(
                        name=data['name'],
                        root_path=project_dir,
                        created_at=data.get('created_at', ''),
                        description=data.get('description', ''),
                        metadata=data.get('metadata', {})
                    )
                    self.projects[project.name] = project

    def create_project(
        self,
        name: str,
        description: str = "",
        metadata: Optional[Dict] = None
    ) -> Project:
        """
        Create a new project with standard llmunix-style structure

        Creates:
        - projects/{name}/
        - projects/{name}/components/agents/
        - projects/{name}/components/tools/
        - projects/{name}/input/
        - projects/{name}/output/
        - projects/{name}/memory/short_term/
        - projects/{name}/memory/long_term/
        - projects/{name}/state/
        - projects/{name}/project.json (manifest)

        Args:
            name: Project name (will be converted to Project_{name})
            description: Project description
            metadata: Additional project metadata

        Returns:
            Project instance
        """
        # Normalize project name
        if not name.startswith("Project_"):
            project_name = f"Project_{name}"
        else:
            project_name = name

        # Check if project already exists
        if project_name in self.projects:
            return self.projects[project_name]

        # Create project root
        project_root = self.projects_root / project_name
        project_root.mkdir(parents=True, exist_ok=True)

        # Create standard directory structure
        directories = [
            "components/agents",
            "components/tools",
            "input",
            "output",
            "memory/short_term",
            "memory/long_term",
            "state"
        ]

        for dir_path in directories:
            (project_root / dir_path).mkdir(parents=True, exist_ok=True)

        # Create project instance
        project = Project(
            name=project_name,
            root_path=project_root,
            description=description,
            metadata=metadata or {}
        )

        # Save project manifest
        self._save_project_manifest(project)

        # Create README
        self._create_project_readme(project)

        # Register project
        self.projects[project_name] = project

        return project

    def _save_project_manifest(self, project: Project):
        """Save project manifest to project.json"""
        manifest = {
            "name": project.name,
            "created_at": project.created_at,
            "description": project.description,
            "metadata": project.metadata
        }

        manifest_path = project.root_path / "project.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)

    def _create_project_readme(self, project: Project):
        """Create project README"""
        readme_content = f"""# {project.name}

{project.description}

## Project Structure

```
{project.name}/
├── components/
│   ├── agents/      # Project-specific agents
│   └── tools/       # Project-specific tools
├── input/           # Input documents/data
├── output/          # Generated results
├── memory/
│   ├── short_term/  # Session logs
│   └── long_term/   # Execution traces, learnings
├── state/           # Execution state machine
└── project.json     # Project manifest
```

## Created

{project.created_at}

## Metadata

```json
{json.dumps(project.metadata, indent=2)}
```
"""

        readme_path = project.root_path / "README.md"
        with open(readme_path, 'w') as f:
            f.write(readme_content)

    def get_project(self, name: str) -> Optional[Project]:
        """
        Get project by name

        Args:
            name: Project name

        Returns:
            Project instance or None
        """
        # Normalize name
        if not name.startswith("Project_"):
            name = f"Project_{name}"

        return self.projects.get(name)

    def list_projects(self) -> List[Project]:
        """
        List all projects

        Returns:
            List of Project instances
        """
        return list(self.projects.values())

    def delete_project(self, name: str) -> bool:
        """
        Delete a project

        Args:
            name: Project name

        Returns:
            True if deleted successfully
        """
        # Normalize name
        if not name.startswith("Project_"):
            name = f"Project_{name}"

        project = self.projects.get(name)
        if not project:
            return False

        # Remove from registry
        del self.projects[name]

        # Note: We don't delete the directory for safety
        # User can manually delete if needed

        return True

    def get_project_agents(self, project: Project) -> List[Path]:
        """
        Get all agent definition files for a project

        Includes:
        - System agents from llmos/agents/
        - Project-specific agents from project/components/agents/

        Args:
            project: Project instance

        Returns:
            List of agent definition file paths
        """
        agents = []

        # System agents
        system_agents_path = self.workspace / "agents"
        if system_agents_path.exists():
            agents.extend(system_agents_path.glob("*.md"))

        # Project-specific agents
        if project.agents_path.exists():
            agents.extend(project.agents_path.glob("*.md"))

        return agents

    def get_project_tools(self, project: Project) -> List[Path]:
        """
        Get all tool definition files for a project

        Args:
            project: Project instance

        Returns:
            List of tool definition file paths
        """
        tools = []

        # System tools
        system_tools_path = self.workspace / "tools"
        if system_tools_path.exists():
            tools.extend(system_tools_path.glob("*.md"))

        # Project-specific tools
        if project.tools_path.exists():
            tools.extend(project.tools_path.glob("*.md"))

        return tools
