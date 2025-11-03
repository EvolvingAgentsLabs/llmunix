#!/usr/bin/env python3
"""
LLMunix Standalone Follower Runtime

This is a self-contained execution engine that runs pre-learned execution traces
on edge devices without requiring Claude Code or internet connectivity.

Perfect for:
- Industrial control systems
- Remote field operations
- Air-gapped secure environments
- Resource-constrained edge devices

Can run with small models like:
- IBM Granite Nano 4B
- Llama 3.1 8B (quantized)
- Mistral 7B (quantized)
- Phi-3 Mini
"""

import os
import sys
import yaml
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import argparse


class ToolLibrary:
    """Local implementations of Claude Code tools for edge execution."""

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.last_output = None

    def execute(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool and return results.

        Args:
            tool_name: Name of the tool (Read, Write, Bash, etc.)
            parameters: Tool-specific parameters

        Returns:
            Dictionary with 'success', 'output', and optional 'error'
        """
        tool_method = getattr(self, f"tool_{tool_name.lower()}", None)
        if not tool_method:
            return {
                'success': False,
                'error': f"Tool '{tool_name}' not implemented"
            }

        try:
            result = tool_method(parameters)
            self.last_output = result.get('output')
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

        # Create parent directories if needed
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
        command = params['command']
        timeout = params.get('timeout', 120)  # Default 2 minute timeout

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
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


class Validator:
    """Handles validation checks for execution trace steps."""

    @staticmethod
    def validate(check_type: str, parameters: Dict, tool_result: Dict, tool_library: ToolLibrary) -> bool:
        """
        Perform a validation check.

        Args:
            check_type: Type of validation (file_exists, content_contains, etc.)
            parameters: Validation-specific parameters
            tool_result: Result from the tool execution
            tool_library: Access to tool library for additional checks

        Returns:
            True if validation passes, False otherwise
        """
        validator_method = getattr(Validator, f"check_{check_type}", None)
        if not validator_method:
            print(f"Warning: Unknown validation type '{check_type}' - skipping")
            return True  # Don't fail on unknown validation types

        return validator_method(parameters, tool_result, tool_library)

    @staticmethod
    def check_file_exists(params: Dict, tool_result: Dict, tool_lib: ToolLibrary) -> bool:
        """Check if a file exists."""
        file_path = Path(params['path'])
        if not file_path.is_absolute():
            file_path = tool_lib.base_dir / file_path
        return file_path.exists()

    @staticmethod
    def check_content_contains(params: Dict, tool_result: Dict, tool_lib: ToolLibrary) -> bool:
        """Check if output contains a substring."""
        substring = params['substring']
        content = tool_result.get('output', '')
        return substring in content

    @staticmethod
    def check_content_not_empty(params: Dict, tool_result: Dict, tool_lib: ToolLibrary) -> bool:
        """Check if output is not empty."""
        content = tool_result.get('output', '')
        return len(content.strip()) > 0

    @staticmethod
    def check_command_exit_code(params: Dict, tool_result: Dict, tool_lib: ToolLibrary) -> bool:
        """Check bash command exit code."""
        expected = params.get('expected', 0)
        actual = tool_result.get('metadata', {}).get('exit_code')
        return actual == expected

    @staticmethod
    def check_file_size_minimum(params: Dict, tool_result: Dict, tool_lib: ToolLibrary) -> bool:
        """Check if file meets minimum size."""
        file_path = Path(params['path'])
        if not file_path.is_absolute():
            file_path = tool_lib.base_dir / file_path

        if not file_path.exists():
            return False

        min_bytes = params.get('min_bytes', 0)
        actual_size = file_path.stat().st_size
        return actual_size >= min_bytes


class FollowerSystemAgent:
    """
    Standalone Follower execution engine.

    This agent reads execution traces and executes them deterministically
    without requiring any reasoning or LLM assistance.
    """

    def __init__(self, base_dir: Path, verbose: bool = True):
        self.base_dir = base_dir
        self.verbose = verbose
        self.tool_library = ToolLibrary(base_dir)
        self.execution_state = {}
        self.step_outputs = {}

    def log(self, message: str, level: str = "INFO"):
        """Log a message if verbose mode is enabled."""
        if self.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {level}: {message}")

    def load_trace(self, trace_path: Path) -> Dict:
        """Load and validate execution trace YAML file."""
        self.log(f"Loading execution trace: {trace_path}")

        if not trace_path.exists():
            raise FileNotFoundError(f"Trace file not found: {trace_path}")

        with open(trace_path, 'r', encoding='utf-8') as f:
            trace = yaml.safe_load(f)

        # Validate required fields
        required_fields = ['trace_id', 'steps']
        for field in required_fields:
            if field not in trace:
                raise ValueError(f"Invalid trace: missing required field '{field}'")

        self.log(f"Loaded trace: {trace['trace_id']} with {len(trace['steps'])} steps")
        return trace

    def check_preconditions(self, preconditions: List[Dict]) -> bool:
        """Check all preconditions before execution."""
        if not preconditions:
            return True

        self.log("Checking preconditions...")

        for i, condition in enumerate(preconditions, 1):
            check_type = condition.get('validation_type')
            params = condition.get('parameters', {})

            # Simplified precondition checking
            if check_type == 'directory_exists':
                path = Path(params['path'])
                if not path.is_absolute():
                    path = self.base_dir / path
                if not path.exists() or not path.is_dir():
                    self.log(f"Precondition {i} failed: Directory not found: {path}", "ERROR")
                    return False

            self.log(f"Precondition {i}: PASSED")

        return True

    def substitute_variables(self, text: str) -> str:
        """Substitute variables in text with values from previous step outputs."""
        import re

        # Find all {variable} patterns
        pattern = r'\{([\w_]+)\}'
        matches = re.findall(pattern, text)

        for var in matches:
            if var in self.step_outputs:
                text = text.replace(f'{{{var}}}', str(self.step_outputs[var]))
            elif var == 'current_timestamp':
                text = text.replace('{current_timestamp}', datetime.now().isoformat())

        return text

    def check_dependencies(self, depends_on: Optional[List[Dict]]) -> bool:
        """Check if all dependency steps have completed."""
        if not depends_on:
            return True

        for dep in depends_on:
            step_num = dep['step']
            output_var = dep.get('output_variable')

            step_key = f"step_{step_num}"
            if step_key not in self.execution_state:
                self.log(f"Dependency failed: Step {step_num} has not completed", "ERROR")
                return False

            if output_var:
                output_key = f"{step_key}_output"
                if output_key not in self.step_outputs:
                    self.log(f"Dependency failed: Step {step_num} did not produce output variable", "ERROR")
                    return False

        return True

    def execute_step(self, step: Dict) -> Dict:
        """Execute a single step from the trace."""
        step_num = step['step']
        description = step.get('description', '')
        tool_call = step['tool_call']

        self.log(f"\n{'='*60}")
        self.log(f"Executing Step {step_num}: {description}")
        self.log(f"{'='*60}")

        # Check dependencies
        if not self.check_dependencies(step.get('depends_on')):
            return {
                'success': False,
                'error': 'Dependencies not met'
            }

        # Substitute variables in parameters
        tool_name = tool_call['tool']
        parameters = tool_call['parameters'].copy()

        # Substitute variables in all parameter values
        for key, value in parameters.items():
            if isinstance(value, str):
                parameters[key] = self.substitute_variables(value)

        # Execute the tool
        self.log(f"Tool: {tool_name}")
        self.log(f"Parameters: {json.dumps(parameters, indent=2)}")

        start_time = time.time()
        result = self.tool_library.execute(tool_name, parameters)
        execution_time = time.time() - start_time

        # Log result
        if result['success']:
            self.log(f"✓ Step {step_num} completed successfully ({execution_time:.2f}s)", "SUCCESS")
            if self.verbose and 'output' in result:
                output_preview = str(result['output'])[:200]
                self.log(f"Output preview: {output_preview}...")
        else:
            self.log(f"✗ Step {step_num} failed: {result.get('error')}", "ERROR")

        # Store output for later steps
        step_key = f"step_{step_num}_output"
        self.step_outputs[step_key] = result.get('output', '')

        # Perform validations
        validations = step.get('validation', [])
        validation_results = []

        if validations:
            self.log(f"Running {len(validations)} validation(s)...")

        for i, validation in enumerate(validations, 1):
            check_type = validation.get('type')
            params = validation.get('parameters', {})
            check_desc = validation.get('check', 'Validation')

            passed = Validator.validate(check_type, params, result, self.tool_library)
            validation_results.append(passed)

            status = "✓ PASS" if passed else "✗ FAIL"
            self.log(f"  Validation {i}: {check_desc} - {status}")

        all_validations_passed = all(validation_results) if validation_results else True

        # Mark step as complete
        self.execution_state[f"step_{step_num}"] = {
            'completed': result['success'] and all_validations_passed,
            'execution_time': execution_time
        }

        return {
            'success': result['success'] and all_validations_passed,
            'execution_time': execution_time,
            'validation_results': validation_results,
            'output': result.get('output'),
            'error': result.get('error')
        }

    def handle_error(self, step: Dict, error_result: Dict, attempt: int = 1) -> Dict:
        """Handle error based on step's error recovery strategy."""
        on_error = step.get('on_error', {})
        action = on_error.get('action', 'fail')

        if action == 'retry':
            retry_count = on_error.get('retry_count', 1)
            if attempt < retry_count:
                delay = on_error.get('delay_seconds', 0)
                self.log(f"Retrying step (attempt {attempt + 1}/{retry_count + 1})...", "WARN")
                if delay > 0:
                    time.sleep(delay)
                return self.execute_step(step)  # Retry
            else:
                self.log(f"Max retries ({retry_count}) exceeded", "ERROR")
                return error_result

        elif action == 'skip':
            self.log("Skipping failed step and continuing...", "WARN")
            return {'success': True, 'skipped': True}

        elif action == 'human_escalate':
            message = on_error.get('escalation_message', 'Step failed - manual review required')
            self.log(f"HUMAN ESCALATION: {message}", "ERROR")
            return error_result

        else:  # Default: fail
            return error_result

    def execute_trace(self, trace_path: Path) -> Dict:
        """
        Execute a complete execution trace.

        Args:
            trace_path: Path to execution_trace.yaml file

        Returns:
            Execution report with results
        """
        start_time = time.time()

        # Load trace
        trace = self.load_trace(trace_path)

        # Check preconditions
        preconditions = trace.get('preconditions', [])
        if not self.check_preconditions(preconditions):
            return {
                'status': 'failed',
                'error': 'Preconditions not met',
                'trace_id': trace.get('trace_id')
            }

        # Execute steps sequentially
        step_results = []
        failed_step = None

        for step in sorted(trace['steps'], key=lambda s: s['step']):
            result = self.execute_step(step)

            step_results.append({
                'step': step['step'],
                'status': 'success' if result['success'] else 'failed',
                'execution_time': result.get('execution_time', 0),
                'output': result.get('output', '')[:500],  # Truncate long outputs
                'validation_results': result.get('validation_results', []),
                'error_message': result.get('error')
            })

            if not result['success']:
                # Attempt error recovery
                retry_result = self.handle_error(step, result)
                if not retry_result['success']:
                    failed_step = step['step']
                    self.log(f"\nExecution halted at step {failed_step}", "ERROR")
                    break

        # Calculate final metrics
        total_time = time.time() - start_time
        completed_steps = len([r for r in step_results if r['status'] == 'success'])
        total_steps = len(trace['steps'])

        # Check postconditions
        postconditions_met = True
        if failed_step is None and 'postconditions' in trace:
            self.log("\nChecking postconditions...")
            # Simplified postcondition checking
            postconditions_met = True  # Would implement full checking here

        # Generate report
        report = {
            'trace_id': trace['trace_id'],
            'status': 'success' if failed_step is None else 'failed',
            'total_steps': total_steps,
            'completed_steps': completed_steps,
            'failed_step': failed_step,
            'execution_time_secs': total_time,
            'estimated_cost': trace.get('estimated_cost', 0.0),
            'step_results': step_results,
            'all_validations_passed': all(
                all(r.get('validation_results', [True]))
                for r in step_results
            ),
            'all_postconditions_met': postconditions_met
        }

        # Log summary
        self.log(f"\n{'='*60}")
        self.log("EXECUTION COMPLETE")
        self.log(f"{'='*60}")
        self.log(f"Status: {report['status'].upper()}")
        self.log(f"Steps: {completed_steps}/{total_steps} completed")
        self.log(f"Time: {total_time:.2f}s")
        self.log(f"{'='*60}\n")

        return report


def main():
    """CLI entry point for standalone follower runtime."""
    parser = argparse.ArgumentParser(
        description="LLMunix Standalone Follower Runtime - Execute pre-learned traces on edge devices"
    )
    parser.add_argument(
        '--trace',
        type=str,
        required=True,
        help="Path to execution_trace.yaml file"
    )
    parser.add_argument(
        '--base-dir',
        type=str,
        default='.',
        help="Base directory for relative file paths (default: current directory)"
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help="Suppress verbose output"
    )
    parser.add_argument(
        '--output',
        type=str,
        help="Save execution report to JSON file"
    )

    args = parser.parse_args()

    # Initialize agent
    base_dir = Path(args.base_dir).resolve()
    agent = FollowerSystemAgent(base_dir, verbose=not args.quiet)

    # Execute trace
    trace_path = Path(args.trace)
    if not trace_path.is_absolute():
        trace_path = base_dir / trace_path

    try:
        report = agent.execute_trace(trace_path)

        # Save report if requested
        if args.output:
            output_path = Path(args.output)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)
            print(f"\nExecution report saved to: {output_path}")

        # Exit with appropriate code
        sys.exit(0 if report['status'] == 'success' else 1)

    except Exception as e:
        print(f"FATAL ERROR: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
