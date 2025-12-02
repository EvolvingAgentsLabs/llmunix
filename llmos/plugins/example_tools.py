"""
Example plugin tools
This demonstrates how to create domain-specific tools
"""

from plugins import llm_tool


@llm_tool(
    "hello_world",
    "Say hello to someone",
    {"name": str}
)
async def hello_world(name: str) -> str:
    """Say hello"""
    return f"Hello, {name}! Welcome to LLM OS."


@llm_tool(
    "calculate",
    "Perform simple calculations",
    {"expression": str}
)
async def calculate(expression: str) -> str:
    """Calculate mathematical expressions"""
    try:
        # Safe eval (in production, use a proper math parser)
        result = eval(expression, {"__builtins__": {}})
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {e}"


# Future plugins can be dropped here:
# - plugins/quantum.py - Quantum circuit tools
# - plugins/web.py - Web scraping tools
# - plugins/database.py - Database tools
# etc.
