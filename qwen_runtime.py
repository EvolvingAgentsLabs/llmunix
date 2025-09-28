#!/usr/bin/env python3
"""
Unified Qwen Runtime for LLMunix - Complete Implementation
Combines all features: interactive mode, sequential execution, corrected cepstral analysis
"""

import os
import re
import json
import sys
import subprocess
from openai import OpenAI
from dotenv import load_dotenv

# Fix Windows console encoding for emojis
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load API keys and other configs from .env file
load_dotenv()

class QwenRuntime:
    def __init__(self, manifest_path="QWEN.md"):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )
        self.model = "qwen/qwen3-4b:free"  # Using Qwen3 4B free model
        self.tools = {}
        self.system_prompt = ""
        self._load_manifest(manifest_path)
        print("✅ Qwen Runtime Initialized.")

    def _load_manifest(self, path):
        """Loads the system prompt and compiles native tools from the manifest."""
        print(f"--- Loading manifest from {path} ---")
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        parts = content.split("### NATIVE TOOLS")
        self.system_prompt = parts[0].strip()

        tool_blocks = re.findall(r"<tool name=\"(.*?)\">(.*?)</tool>", parts[1], re.DOTALL)
        for name, block in tool_blocks:
            description = re.search(r"<description>(.*?)</description>", block, re.DOTALL).group(1).strip()
            code = re.search(r"<python_code>(.*?)</python_code>", block, re.DOTALL).group(1).strip()

            # Special handling for call_llm tool
            if name == "call_llm":
                self.tools[name] = self._handle_call_llm
                print(f"  - Registered special tool: {name}")
                continue

            # Special handling for delegate_to_agent tool
            if name == "delegate_to_agent":
                self.tools[name] = self._handle_delegate_to_agent
                print(f"  - Registered special tool: {name}")
                continue

            try:
                namespace = {}
                # Compile the tool function
                exec(code, globals(), namespace)
                # Find the function in the namespace
                for key, value in namespace.items():
                    if callable(value) and not key.startswith('_'):
                        self.tools[name] = value
                        print(f"  - Compiled tool: {name}")
                        break
            except Exception as e:
                print(f"!!! Error compiling tool '{name}': {e}")
        print("--- Manifest loaded successfully. ---")

    def _handle_call_llm(self, prompt: str):
        """Handles recursive calls to the LLM."""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        return self._call_llm(messages)

    def _handle_delegate_to_agent(self, agent_name: str, task_description: str, input_data: dict = None):
        """Handles delegation to specialized agents."""
        print(f"\n🎯 Delegating to agent: {agent_name}")

        # Load the agent definition
        agent_info = self.tools["load_agent"](agent_name)
        if not agent_info.get("found"):
            return f"❌ Agent '{agent_name}' not found. Available agents: {list(self.tools['list_agents']().keys())}"

        # Create agent-specific prompt using the agent's context
        agent_prompt = f"""
{agent_info['content']}

## CURRENT TASK

{task_description}

## INPUT DATA

{json.dumps(input_data or {}, indent=2)}

## INSTRUCTIONS

Execute this task according to your specialized capabilities and return the results.
Focus on generating high-quality, detailed content appropriate to your role.
Do not use tool calls - just provide your expert response directly.
"""

        print(f"   📋 Agent description: {agent_info['description']}")
        print(f"   🛠️  Available tools: {agent_info.get('tools', 'N/A')}")

        # Make LLM call with agent context
        messages = [
            {"role": "system", "content": agent_prompt},
            {"role": "user", "content": f"Execute the task: {task_description}"}
        ]

        try:
            response = self._call_llm(messages)
            print(f"   ✅ Agent {agent_name} completed task")
            print(f"   📄 Generated {len(response)} characters")
            return response
        except Exception as e:
            error_msg = f"❌ Error executing agent {agent_name}: {e}"
            print(f"   {error_msg}")
            return error_msg

    def _call_llm(self, messages):
        """A wrapper for making calls to the OpenRouter API."""
        return self.client.chat.completions.create(
            model=self.model,
            messages=messages,
        ).choices[0].message.content

    def _extract_tag_content(self, tag, text):
        match = re.search(f"<{tag}>(.*?)</{tag}>", text, re.DOTALL)
        return match.group(1).strip() if match else None

    def run_goal(self, goal, max_turns=10):
        """Execute a goal using the general workflow system."""
        print("\n" + "="*20 + " AGENT EXECUTION START " + "="*20)
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"My goal is: {goal}"}
        ]

        for i in range(max_turns):
            print(f"\n--- Turn {i+1}/{max_turns} ---")

            try:
                response = self._call_llm(messages)
            except Exception as e:
                print(f"!!! Error calling LLM: {e}")
                return f"Failed to get response from LLM: {e}"

            # Handle empty responses
            if not response or response.strip() == "":
                print("!!! Empty response from agent, retrying...")
                messages.append({
                    "role": "user",
                    "content": "Please provide a response with tool calls or a final_answer."
                })
                continue

            print(f"Agent Output:\n{response[:500]}...") if len(response) > 500 else print(f"Agent Output:\n{response}")
            messages.append({"role": "assistant", "content": response})

            # Check for tool calls in the response
            tool_calls = re.findall(r"<tool_call name=\"(.*?)\">(.*?)</tool_call>", response, re.DOTALL)

            # Process tool calls first (if any), then check for final answer
            if tool_calls:
                for tool_name, args_str in tool_calls:
                    print(f"\n--- Executing Tool: {tool_name} ---")
                    try:
                        # Parse JSON arguments
                        args = json.loads(args_str.strip())

                        if tool_name in self.tools:
                            # Execute the tool
                            if isinstance(args, dict):
                                tool_result = self.tools[tool_name](**args)
                            else:
                                tool_result = self.tools[tool_name](args)
                        else:
                            tool_result = f"Error: Tool '{tool_name}' not found. Available tools: {', '.join(self.tools.keys())}"

                        # Truncate long outputs for display
                        display_result = str(tool_result)[:500] + "..." if len(str(tool_result)) > 500 else str(tool_result)
                        print(f"Tool Result:\n{display_result}")

                        # Special handling for agent delegation results
                        if tool_name == "delegate_to_agent" and len(str(tool_result)) > 100:
                            print(f"🎉 Agent generated {len(str(tool_result))} characters of content!")

                        # Add tool result to conversation
                        messages.append({
                            "role": "user",
                            "content": f"Tool '{tool_name}' returned:\n{tool_result}"
                        })
                    except json.JSONDecodeError as e:
                        error_message = f"Error parsing arguments for tool '{tool_name}': {e}. Args: {args_str}"
                        print(f"!!! {error_message}")
                        messages.append({
                            "role": "user",
                            "content": error_message
                        })
                    except Exception as e:
                        error_message = f"Error executing tool '{tool_name}': {e}"
                        print(f"!!! {error_message}")
                        messages.append({
                            "role": "user",
                            "content": error_message
                        })

            # After processing tool calls, check for final answer
            final_answer = self._extract_tag_content("final_answer", response)
            if final_answer:
                print("\n" + "="*20 + " GOAL ACHIEVED " + "="*20)
                return final_answer

            # If no tool calls and no final answer, prompt the agent
            if not tool_calls and "final_answer" not in response.lower():
                messages.append({
                    "role": "user",
                    "content": "Please either make a tool call or provide a final_answer."
                })

        return "Agent reached maximum turns without providing a final answer."



    def interactive_mode(self):
        """Interactive REPL mode for the runtime."""
        print("\n" + "="*60)
        print("           LLMunix Qwen Runtime - Interactive Mode")
        print("="*60)
        print("Type 'help' for commands, 'exit' to quit")
        print("Or simply type your goal to execute it.")

        while True:
            try:
                user_input = input("\n🎯 llmunix> ").strip()

                if user_input.lower() in ['exit', 'quit']:
                    print("Goodbye!")
                    break

                if user_input.lower() == 'help':
                    print("""
Available Commands:
- help     : Show this help message
- status   : Show current workspace status
- clear    : Clear workspace (with confirmation)
- demo     : Run architecture demo without API calls
- exit/quit: Exit interactive session

Simply type any goal to execute it, for example:
  Create a Python calculator
  Analyze the files in my workspace
  Build a REST API with FastAPI
  Execute Project Aorta using quantum cepstral analysis
  Research quantum computing trends and create a report
""")
                    continue

                if user_input.lower() == 'status':
                    workspace_files = self.tools['list_files']('workspace')
                    print(f"Workspace contains: {workspace_files}")
                    continue

                if user_input.lower() == 'clear':
                    confirm = input("Clear workspace? This will delete all files in workspace/ (y/n): ")
                    if confirm.lower() == 'y':
                        self.tools['execute_bash']('rm -rf workspace/*')
                        print("Workspace cleared.")
                    continue


                if user_input.lower() == 'demo':
                    print("Running architecture demo...")
                    agents = self.tools["list_agents"]()
                    print(f"✅ Found {len(agents)} agents")
                    print(f"✅ Tools loaded: {len(self.tools)}")
                    print("🎉 Architecture is ready for full execution!")
                    continue

                # Execute the goal
                if user_input:
                    result = self.run_goal(user_input)
                    print("\n" + "="*60)
                    print("                  FINAL RESULT")
                    print("="*60)
                    print(result)

            except KeyboardInterrupt:
                print("\n\nInterrupted. Type 'exit' to quit.")
            except Exception as e:
                print(f"Error: {e}")

# ===================================================
# Main Execution Block
# ===================================================
if __name__ == "__main__":
    import sys

    runtime = QwenRuntime()

    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "interactive":
            runtime.interactive_mode()
        elif command == "demo":
            print("Running architecture demo...")
            agents = runtime.tools["list_agents"]()
            print(f"✅ Found {len(agents)} agents")
            print(f"✅ Tools loaded: {len(runtime.tools)}")
            print("🎉 Architecture is ready for full execution!")
        elif command == "test":
            # Quick test mode
            print("Running quick test...")
            test_goal = "Create a simple Python script that prints 'Hello LLMunix!'"
            result = runtime.run_goal(test_goal, max_turns=3)
            print(f"\nTest result: {result}")
        else:
            # Treat unknown command as a goal to execute
            goal = " ".join(sys.argv[1:])
            print(f"Executing goal: {goal}")
            result = runtime.run_goal(goal)
            print(f"\nResult: {result}")
    else:
        # Default: Run Project Aorta using generic runtime
        project_aorta_goal = """Execute Project Aorta using quantum-enhanced cepstral analysis:

STEP 1: Use visionary-agent to create comprehensive project vision
- Focus on arterial navigation using CEPSTRAL ANALYSIS (not encryption)
- Emphasize homomorphic transforms and quantum Fourier Transform
- Save to workspace/project_vision.md

STEP 2: Use mathematician-agent to develop mathematical framework
- Create rigorous framework for cepstral analysis using QFT
- Include echo separation and filtering equations
- Save to workspace/mathematical_framework.md

STEP 3: Use quantum-engineer-agent to create Qiskit implementation
- Build complete quantum circuit for cepstral analysis
- Include echo detection and classical validation
- Save to workspace/quantum_poc.py

Process agents sequentially and save outputs immediately."""

        result = runtime.run_goal(project_aorta_goal)
        print(f"\n🎉 Project Aorta execution result: {result}")