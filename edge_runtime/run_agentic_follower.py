#!/usr/bin/env python3
"""
LLMunix Agentic Follower Runtime

This is an LLM-powered execution engine that uses small models (like Granite 4)
to execute agent definitions with reasoning and flexibility.

Key Difference from Deterministic Follower:
- Deterministic: Executes exact steps (no LLM)
- Agentic: Uses LLM to reason within learned agent boundaries

Architecture:
- Learner (Claude): Creates agent definitions with capabilities and constraints
- Follower (Granite): Reasons about how to accomplish goals using the definition

Benefits:
- Flexible execution (adapts to variations)
- Cost-effective (local LLM, no API costs)
- Intelligent decisions (within learned boundaries)
- Faster than Claude (smaller model)
"""

import os
import sys
import yaml
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

try:
    import ollama
except ImportError:
    print("ERROR: ollama-python not installed. Install with: pip install ollama")
    sys.exit(1)


class ToolLibrary:
    """Local implementations of tools available to agentic follower."""

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.execution_log = []

    def execute(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool and return results."""
        tool_method = getattr(self, f"tool_{tool_name.lower()}", None)
        if not tool_method:
            return {
                'success': False,
                'error': f"Tool '{tool_name}' not available"
            }

        try:
            result = tool_method(parameters)
            self.execution_log.append({
                'tool': tool_name,
                'parameters': parameters,
                'result': result,
                'timestamp': datetime.now().isoformat()
            })
            return result
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def tool_read(self, params: Dict) -> Dict:
        """Read a file from disk."""
        file_path = Path(params['file_path'])
        if not file_path.is_absolute():
            file_path = self.base_dir / file_path

        if not file_path.exists():
            return {
                'success': False,
                'error': f"File not found: {file_path}"
            }

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return {
            'success': True,
            'output': content,
            'metadata': {
                'file_path': str(file_path),
                'size_bytes': len(content)
            }
        }

    def tool_write(self, params: Dict) -> Dict:
        """Write content to a file."""
        file_path = Path(params['file_path'])
        if not file_path.is_absolute():
            file_path = self.base_dir / file_path

        content = params['content']
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return {
            'success': True,
            'output': f"Successfully wrote {len(content)} characters to {file_path}",
            'metadata': {
                'file_path': str(file_path),
                'size_bytes': len(content)
            }
        }

    def tool_bash(self, params: Dict) -> Dict:
        """Execute a bash command."""
        import subprocess

        command = params['command']
        timeout = params.get('timeout', 120)

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(self.base_dir)
            )

            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr if result.returncode != 0 else None,
                'metadata': {
                    'exit_code': result.returncode,
                    'command': command
                }
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': f"Command timed out after {timeout} seconds"
            }


class AgenticFollower:
    """
    LLM-powered follower that uses agent definitions to execute goals with reasoning.
    """

    def __init__(self, agent_definition_path: Path, base_dir: Path, model: str = "granite4:micro"):
        self.agent_def = self.load_agent_definition(agent_definition_path)
        self.base_dir = base_dir
        self.model = model
        self.tool_library = ToolLibrary(base_dir)
        self.conversation_history = []

    def load_agent_definition(self, path: Path) -> Dict:
        """Load agent definition from markdown file."""
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract YAML frontmatter
        import re
        frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n'
        match = re.match(frontmatter_pattern, content, re.DOTALL)

        if not match:
            raise ValueError(f"No YAML frontmatter found in agent definition: {path}")

        frontmatter_yaml = match.group(1)
        agent_metadata = yaml.safe_load(frontmatter_yaml)

        # Extract markdown body
        body_start = match.end()
        agent_metadata['description'] = content[body_start:].strip()

        return agent_metadata

    def build_system_prompt(self) -> str:
        """Build system prompt from agent definition."""
        agent_def = self.agent_def

        capabilities_text = yaml.dump(agent_def.get('capabilities', {}), default_flow_style=False)
        constraints_text = yaml.dump(agent_def.get('constraints', {}), default_flow_style=False)

        system_prompt = f"""You are an intelligent agent executing tasks based on a learned definition.

Agent ID: {agent_def.get('agent_id', 'unknown')}

{agent_def.get('description', '')}

AVAILABLE TOOLS:
You can call these tools by outputting exactly:
TOOL_CALL: tool_name(param1="value1", param2="value2")

Available tools:
1. Read(file_path="path") - Read file contents
2. Write(file_path="path", content="text") - Write file
3. Bash(command="cmd") - Execute shell command

CAPABILITIES:
{capabilities_text}

CONSTRAINTS:
{constraints_text}

REASONING GUIDELINES:
{agent_def.get('reasoning_guidelines', 'Use your best judgment.')}

ERROR HANDLING:
{agent_def.get('error_handling', 'Fail gracefully and report errors.')}

IMPORTANT:
- Plan your approach step by step
- Execute one tool at a time
- Wait for tool results before continuing
- When task is complete, output: TASK_COMPLETE
"""
        return system_prompt

    def extract_tool_call(self, text: str) -> Optional[Dict]:
        """Extract tool call from LLM response."""
        pattern = r'TOOL_CALL:\s*(\w+)\((.*?)\)'
        match = re.search(pattern, text)

        if not match:
            return None

        tool_name = match.group(1)
        params_str = match.group(2)

        # Parse parameters
        params = {}
        param_pattern = r'(\w+)=["\'](.*?)["\']'
        for param_match in re.finditer(param_pattern, params_str):
            param_name = param_match.group(1)
            param_value = param_match.group(2)
            params[param_name] = param_value

        return {
            'tool': tool_name,
            'params': params
        }

    def is_task_complete(self, text: str) -> bool:
        """Check if LLM indicates task completion."""
        return 'TASK_COMPLETE' in text.upper()

    def execute_goal(self, goal: str, max_iterations: int = 10) -> Dict:
        """Execute goal using LLM reasoning."""
        print(f"\n{'='*60}")
        print(f"Agentic Follower Execution")
        print(f"Agent: {self.agent_def.get('agent_id', 'unknown')}")
        print(f"Model: {self.model}")
        print(f"Goal: {goal}")
        print(f"{'='*60}\n")

        system_prompt = self.build_system_prompt()
        self.conversation_history = [
            {"role": "system", "content": system_prompt}
        ]

        user_prompt = f"""Goal: {goal}

Plan your approach and execute step by step using available tools.
After each tool execution, I will provide the result.
When you're done, output TASK_COMPLETE."""

        self.conversation_history.append({"role": "user", "content": user_prompt})

        iteration = 0
        while iteration < max_iterations:
            iteration += 1
            print(f"\n--- Iteration {iteration} ---")

            # Get LLM response
            print("Calling Granite for reasoning...")
            response = ollama.chat(
                model=self.model,
                messages=self.conversation_history
            )

            llm_response = response['message']['content']
            print(f"\nGranite Response:\n{llm_response}\n")

            self.conversation_history.append({
                "role": "assistant",
                "content": llm_response
            })

            # Check for completion
            if self.is_task_complete(llm_response):
                print("✅ Task marked as complete by Granite")
                break

            # Extract and execute tool call
            tool_call = self.extract_tool_call(llm_response)
            if tool_call:
                print(f"Executing tool: {tool_call['tool']}({tool_call['params']})")
                result = self.tool_library.execute(tool_call['tool'], tool_call['params'])

                result_text = f"Tool execution result:\n"
                if result['success']:
                    result_text += f"✅ Success\n"
                    if 'output' in result:
                        result_text += f"Output: {result['output'][:200]}"
                else:
                    result_text += f"❌ Error: {result.get('error', 'Unknown error')}"

                print(f"\n{result_text}\n")

                self.conversation_history.append({
                    "role": "user",
                    "content": result_text
                })
            else:
                # No tool call found, ask for next action
                self.conversation_history.append({
                    "role": "user",
                    "content": "What's your next step? (Use TOOL_CALL format or output TASK_COMPLETE)"
                })

        # Generate execution report
        report = {
            'agent_id': self.agent_def.get('agent_id'),
            'goal': goal,
            'model': self.model,
            'status': 'success' if iteration < max_iterations else 'max_iterations_reached',
            'iterations': iteration,
            'tools_executed': len(self.tool_library.execution_log),
            'execution_log': self.tool_library.execution_log,
            'conversation_length': len(self.conversation_history)
        }

        return report


def main():
    """CLI entry point for agentic follower."""
    import argparse

    parser = argparse.ArgumentParser(
        description="LLMunix Agentic Follower - Execute goals using LLM reasoning"
    )
    parser.add_argument(
        '--agent',
        type=str,
        required=True,
        help="Path to agent definition file (.md)"
    )
    parser.add_argument(
        '--goal',
        type=str,
        required=True,
        help="Goal to accomplish"
    )
    parser.add_argument(
        '--base-dir',
        type=str,
        default='.',
        help="Base directory for file operations"
    )
    parser.add_argument(
        '--model',
        type=str,
        default='granite4:micro',
        help="Ollama model to use (default: granite4:micro)"
    )
    parser.add_argument(
        '--output',
        type=str,
        help="Save execution report to JSON file"
    )

    args = parser.parse_args()

    # Initialize agentic follower
    base_dir = Path(args.base_dir).resolve()
    agent_path = Path(args.agent)
    if not agent_path.is_absolute():
        agent_path = base_dir / agent_path

    try:
        follower = AgenticFollower(agent_path, base_dir, model=args.model)
        report = follower.execute_goal(args.goal)

        print(f"\n{'='*60}")
        print("EXECUTION COMPLETE")
        print(f"{'='*60}")
        print(f"Status: {report['status']}")
        print(f"Iterations: {report['iterations']}")
        print(f"Tools Executed: {report['tools_executed']}")
        print(f"{'='*60}\n")

        # Save report if requested
        if args.output:
            output_path = Path(args.output)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)
            print(f"Execution report saved to: {output_path}")

        sys.exit(0 if report['status'] == 'success' else 1)

    except Exception as e:
        print(f"FATAL ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(2)


if __name__ == "__main__":
    main()
