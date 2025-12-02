"""
Tool Search Engine - On-Demand Tool Discovery

Implements Anthropic's Tool Search pattern for efficient tool loading.
Used in LEARNER and ORCHESTRATOR modes where we don't know upfront
which tools will be needed.

Key Concept:
- Instead of loading all 100+ tools into context (expensive!)
- Start with a "search_tools" meta-tool
- Claude discovers tools on-demand as needed
- 85-90% context reduction for large toolsets

Reference: https://github.com/anthropics/anthropic-cookbook/tree/main/misc/tool_search_tool
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import json


@dataclass
class ToolReference:
    """
    Lightweight reference to a tool (returned by search)

    This is what Tool Search returns - just enough info for Claude
    to decide if it wants to load the full tool definition.
    """
    name: str
    description: str
    category: str = ""
    relevance_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "relevance_score": self.relevance_score
        }


@dataclass
class ToolDefinition:
    """
    Full tool definition that can be deferred

    The `defer_loading` flag tells the system this tool should
    not be loaded into context upfront.
    """
    name: str
    description: str
    input_schema: Dict[str, Any]
    category: str = ""
    defer_loading: bool = True  # Default to deferred (efficient)
    input_examples: List[Dict] = field(default_factory=list)
    embedding: Optional[List[float]] = None  # For semantic search

    def to_api_format(self) -> Dict[str, Any]:
        """Convert to Anthropic API format"""
        tool_dict = {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema
        }

        if self.input_examples:
            tool_dict["input_examples"] = self.input_examples

        return tool_dict

    def to_reference(self, score: float = 0.0) -> ToolReference:
        """Convert to lightweight reference"""
        return ToolReference(
            name=self.name,
            description=self.description,
            category=self.category,
            relevance_score=score
        )


class ToolSearchEngine:
    """
    Semantic search engine for tools

    Implements on-demand tool discovery to reduce context window usage.
    Can use either:
    1. Simple keyword matching (fast, no dependencies)
    2. Embedding-based semantic search (better quality, requires sentence-transformers)

    Usage:
        engine = ToolSearchEngine()
        engine.register_tool(tool_def)

        # Search for relevant tools
        results = engine.search("read a file from disk")
        # Returns: [ToolReference(name="read_file", ...), ...]

        # Load full definition when needed
        full_def = engine.get_tool_definition("read_file")
    """

    def __init__(
        self,
        use_embeddings: bool = False,
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize tool search engine

        Args:
            use_embeddings: Whether to use embedding-based search
            embedding_model: Model name for sentence-transformers
        """
        self.tools: Dict[str, ToolDefinition] = {}
        self.use_embeddings = use_embeddings
        self.embedding_model = embedding_model
        self._embedder = None

        if use_embeddings:
            try:
                from sentence_transformers import SentenceTransformer
                self._embedder = SentenceTransformer(embedding_model)
                print(f"[ToolSearch] Using embedding model: {embedding_model}")
            except ImportError:
                print("[ToolSearch] sentence-transformers not installed, using keyword search")
                self.use_embeddings = False

    def register_tool(self, tool: ToolDefinition) -> None:
        """
        Register a tool for search

        Args:
            tool: ToolDefinition to register
        """
        # Generate embedding if using embeddings
        if self.use_embeddings and self._embedder and not tool.embedding:
            text = f"{tool.name} {tool.description} {tool.category}"
            tool.embedding = self._embedder.encode(text).tolist()

        self.tools[tool.name] = tool

    def register_tools_from_registry(self, registry: 'ComponentRegistry') -> None:
        """
        Register all tools from a ComponentRegistry

        Args:
            registry: ComponentRegistry with tools
        """
        for tool_spec in registry.tools.values():
            tool_def = ToolDefinition(
                name=tool_spec.name,
                description=tool_spec.description,
                input_schema={},  # Would need to be provided
                category=tool_spec.category,
                defer_loading=True
            )
            self.register_tool(tool_def)

    def search(
        self,
        query: str,
        top_k: int = 5,
        category_filter: Optional[str] = None
    ) -> List[ToolReference]:
        """
        Search for relevant tools

        Args:
            query: Natural language search query
            top_k: Maximum number of results
            category_filter: Optional category to filter by

        Returns:
            List of ToolReference sorted by relevance
        """
        if not self.tools:
            return []

        # Filter by category if specified
        candidates = self.tools.values()
        if category_filter:
            candidates = [t for t in candidates if t.category == category_filter]

        if self.use_embeddings and self._embedder:
            return self._search_embeddings(query, list(candidates), top_k)
        else:
            return self._search_keywords(query, list(candidates), top_k)

    def _search_keywords(
        self,
        query: str,
        candidates: List[ToolDefinition],
        top_k: int
    ) -> List[ToolReference]:
        """Simple keyword-based search"""
        query_lower = query.lower()
        query_words = set(query_lower.split())

        scored = []
        for tool in candidates:
            # Score based on word overlap
            tool_text = f"{tool.name} {tool.description} {tool.category}".lower()
            tool_words = set(tool_text.split())

            overlap = len(query_words & tool_words)
            if overlap > 0:
                # Boost for name match
                name_match = 1.0 if any(w in tool.name.lower() for w in query_words) else 0.0
                score = (overlap / len(query_words)) + name_match
                scored.append((score, tool))

        # Sort by score descending
        scored.sort(key=lambda x: x[0], reverse=True)

        return [
            tool.to_reference(score=score)
            for score, tool in scored[:top_k]
        ]

    def _search_embeddings(
        self,
        query: str,
        candidates: List[ToolDefinition],
        top_k: int
    ) -> List[ToolReference]:
        """Embedding-based semantic search"""
        import numpy as np

        query_embedding = self._embedder.encode(query)

        scored = []
        for tool in candidates:
            if tool.embedding:
                # Cosine similarity
                tool_emb = np.array(tool.embedding)
                query_emb = np.array(query_embedding)

                similarity = np.dot(tool_emb, query_emb) / (
                    np.linalg.norm(tool_emb) * np.linalg.norm(query_emb)
                )
                scored.append((float(similarity), tool))

        # Sort by similarity descending
        scored.sort(key=lambda x: x[0], reverse=True)

        return [
            tool.to_reference(score=score)
            for score, tool in scored[:top_k]
        ]

    def get_tool_definition(self, name: str) -> Optional[ToolDefinition]:
        """
        Get full tool definition by name

        Called after search when Claude decides it needs the full definition.

        Args:
            name: Tool name

        Returns:
            ToolDefinition or None
        """
        return self.tools.get(name)

    def get_immediate_tools(self) -> List[ToolDefinition]:
        """
        Get tools that should be loaded immediately (not deferred)

        These are core tools that are almost always needed.

        Returns:
            List of ToolDefinitions with defer_loading=False
        """
        return [t for t in self.tools.values() if not t.defer_loading]

    def get_search_tool_definition(self) -> Dict[str, Any]:
        """
        Get the "search_tools" meta-tool definition

        This tool is given to Claude so it can discover other tools.

        Returns:
            Tool definition for the search tool
        """
        # Get all categories
        categories = list(set(t.category for t in self.tools.values() if t.category))

        return {
            "name": "search_tools",
            "description": (
                "Search for available tools by description. Use this to discover "
                "tools that can help with a specific task. Returns tool names and "
                "descriptions that match your query."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language description of what you need"
                    },
                    "category": {
                        "type": "string",
                        "description": f"Optional category filter. Available: {', '.join(categories)}",
                        "enum": categories if categories else None
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results (default: 5)",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        }

    def get_load_tool_definition(self) -> Dict[str, Any]:
        """
        Get the "load_tool" meta-tool definition

        This tool lets Claude load a specific tool after finding it via search.

        Returns:
            Tool definition for the load tool
        """
        return {
            "name": "load_tool",
            "description": (
                "Load a tool's full definition after finding it via search_tools. "
                "Call this when you need to use a tool that was returned from search."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "tool_name": {
                        "type": "string",
                        "description": "Name of the tool to load"
                    }
                },
                "required": ["tool_name"]
            }
        }

    async def handle_search_tool_call(
        self,
        query: str,
        category: Optional[str] = None,
        max_results: int = 5
    ) -> Dict[str, Any]:
        """
        Handle a call to the search_tools tool

        Args:
            query: Search query
            category: Optional category filter
            max_results: Maximum results

        Returns:
            Tool search results
        """
        results = self.search(query, top_k=max_results, category_filter=category)

        return {
            "tools_found": len(results),
            "results": [r.to_dict() for r in results],
            "hint": "Use load_tool to get the full definition of any tool you want to use"
        }

    async def handle_load_tool_call(self, tool_name: str) -> Dict[str, Any]:
        """
        Handle a call to the load_tool tool

        Args:
            tool_name: Name of tool to load

        Returns:
            Full tool definition or error
        """
        tool = self.get_tool_definition(tool_name)

        if not tool:
            return {
                "error": f"Tool '{tool_name}' not found",
                "hint": "Use search_tools to find available tools"
            }

        return {
            "tool_definition": tool.to_api_format(),
            "hint": "You can now use this tool in your response"
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about registered tools"""
        deferred = sum(1 for t in self.tools.values() if t.defer_loading)
        immediate = len(self.tools) - deferred

        categories = {}
        for tool in self.tools.values():
            cat = tool.category or "uncategorized"
            categories[cat] = categories.get(cat, 0) + 1

        return {
            "total_tools": len(self.tools),
            "deferred_tools": deferred,
            "immediate_tools": immediate,
            "categories": categories,
            "using_embeddings": self.use_embeddings,
            "embedding_model": self.embedding_model if self.use_embeddings else None
        }
