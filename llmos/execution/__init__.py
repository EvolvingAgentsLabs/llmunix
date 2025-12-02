"""
Execution Layer - Anthropic Advanced Tool Use Integration

This layer handles EFFICIENT EXECUTION of decisions made by the Learning Layer.

Architecture:
- Learning Layer (TraceManager, ModeStrategies) decides WHAT to do
- Execution Layer (this module) decides HOW to do it efficiently

Components:
- PTC (Programmatic Tool Calling): Execute tool sequences outside context
- Tool Search: On-demand tool discovery for novel scenarios
- Tool Examples: Auto-generated examples from successful traces

Beta Header: advanced-tool-use-2025-11-20
"""

# Lazy imports to avoid circular dependencies
def get_ptc_executor():
    from execution.ptc import PTCExecutor
    return PTCExecutor

def get_tool_search_engine():
    from execution.tool_search import ToolSearchEngine
    return ToolSearchEngine

def get_tool_example_generator():
    from execution.tool_examples import ToolExampleGenerator
    return ToolExampleGenerator

__all__ = [
    'get_ptc_executor',
    'get_tool_search_engine',
    'get_tool_example_generator'
]
