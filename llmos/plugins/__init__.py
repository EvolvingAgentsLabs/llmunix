"""
Plugin System - Extensible tool packs for domain-specific capabilities
"""

from typing import Dict, Any, Callable
from pathlib import Path
import importlib.util
import inspect
import sys


class PluginLoader:
    """
    Plugin loader for dynamic tool registration
    Allows domain-specific tools without hardcoding

    Supports hot-reload for HOPE (Self-Modifying Kernel) architecture,
    enabling runtime loading of crystallized tools.
    """

    def __init__(self, plugin_dir: Path):
        self.plugin_dir = Path(plugin_dir)
        self.plugin_dir.mkdir(parents=True, exist_ok=True)

        self.tools: Dict[str, Callable] = {}

        # Track loaded modules for hot-reload
        self._loaded_modules: Dict[str, Any] = {}

    def load_plugins(self):
        """Scan plugin directory and load all Python modules"""
        for plugin_file in self.plugin_dir.glob("*.py"):
            if plugin_file.name.startswith("_"):
                continue  # Skip __init__.py and private files

            self._load_plugin(plugin_file)

    def _load_plugin(self, plugin_file: Path):
        """Load a single plugin file"""
        # Import the module
        spec = importlib.util.spec_from_file_location(
            plugin_file.stem,
            plugin_file
        )
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Track module for hot-reload
            self._loaded_modules[plugin_file.stem] = module

            # Find all functions decorated with @llm_tool
            for name, obj in inspect.getmembers(module):
                if hasattr(obj, '_is_llm_tool'):
                    self.tools[obj._tool_name] = obj
                    print(f"  ✓ Loaded tool: {obj._tool_name}")

    def get_tool(self, name: str) -> Callable:
        """Get a tool by name"""
        return self.tools.get(name)

    def list_tools(self) -> list:
        """List all available tools"""
        return list(self.tools.keys())

    def load_plugin_dynamically(self, file_path: Path) -> bool:
        """
        Hot-load a specific plugin file into the running kernel.

        This implements the HOPE (Self-Modifying Kernel) architecture,
        allowing the system to load newly crystallized tools at runtime
        without restarting.

        Args:
            file_path: Path to the plugin file to load

        Returns:
            True if loaded successfully, False otherwise
        """
        if not file_path.exists():
            print(f"[ERROR] Plugin file not found: {file_path}")
            return False

        module_name = file_path.stem
        spec = importlib.util.spec_from_file_location(module_name, file_path)

        if spec and spec.loader:
            try:
                # Load module
                module = importlib.util.module_from_spec(spec)

                # Register in sys.modules for proper import handling
                sys.modules[module_name] = module

                # Execute module code
                spec.loader.exec_module(module)

                # Track module
                self._loaded_modules[module_name] = module

                # Scan for tools in the new module
                new_tools = []
                for name, obj in inspect.getmembers(module):
                    if hasattr(obj, '_is_llm_tool'):
                        self.tools[obj._tool_name] = obj
                        new_tools.append(obj._tool_name)

                if new_tools:
                    print(f"🔥 Hot-loaded {len(new_tools)} tool(s) from {module_name}:")
                    for tool_name in new_tools:
                        print(f"   💎 {tool_name}")
                    return True
                else:
                    print(f"[WARNING] No tools found in {module_name}")
                    return False

            except Exception as e:
                print(f"[ERROR] Failed to hot-load plugin {module_name}: {e}")
                import traceback
                traceback.print_exc()
                return False

        return False

    def reload_plugin(self, module_name: str) -> bool:
        """
        Reload an existing plugin module.

        Useful for updating crystallized tools without restarting.

        Args:
            module_name: Name of the module to reload

        Returns:
            True if reloaded successfully
        """
        if module_name not in self._loaded_modules:
            print(f"[ERROR] Module {module_name} not loaded")
            return False

        # Find the original file
        plugin_file = self.plugin_dir / f"{module_name}.py"

        if not plugin_file.exists():
            # Check generated subdirectory
            generated_dir = self.plugin_dir / "generated"
            plugin_file = generated_dir / f"{module_name}.py"

        if not plugin_file.exists():
            print(f"[ERROR] Plugin file not found: {module_name}.py")
            return False

        # Remove old tools from this module
        old_module = self._loaded_modules[module_name]
        tools_to_remove = []
        for tool_name, tool_func in self.tools.items():
            if hasattr(tool_func, '__module__') and tool_func.__module__ == module_name:
                tools_to_remove.append(tool_name)

        for tool_name in tools_to_remove:
            del self.tools[tool_name]

        # Reload
        return self.load_plugin_dynamically(plugin_file)


def llm_tool(name: str, description: str, schema: Dict[str, Any]):
    """
    Decorator to mark a function as an LLM tool

    Args:
        name: Tool name
        description: Tool description
        schema: JSON schema for tool parameters

    Example:
        @llm_tool("calculate", "Perform calculations", {"expression": str})
        async def calculate(expression: str):
            return eval(expression)
    """
    def decorator(func):
        func._is_llm_tool = True
        func._tool_name = name
        func._tool_description = description
        func._tool_schema = schema
        return func

    return decorator
