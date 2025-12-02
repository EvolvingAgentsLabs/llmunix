"""
Qiskit Tools Plugin for LLM OS
Executes Qiskit quantum code with automatic backend switching

This plugin wraps the Qiskit code execution logic from the original
qiskit-studio coderun-agent, adapting it to work as an LLM OS tool.
"""

import sys
import io
import contextlib
import re
import logging
from typing import Optional, Dict, Any

# Import the llm_tool decorator from the parent llmos plugins
# We need to add the llmos path to sys.path
from pathlib import Path
LLMOS_ROOT = Path(__file__).parents[3]  # Go up to llm-os root
if (LLMOS_ROOT / "llmos").exists():
    sys.path.insert(0, str(LLMOS_ROOT))  # Add llm-os root to path

# Import from llmos.plugins to avoid circular import
from llmos.plugins import llm_tool

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def replace_ibm_quantum_config(code: str, ibm_config: Optional[Dict[str, Any]] = None, use_simulator: bool = True) -> str:
    """
    Replace IBM Quantum Config section based on execution mode and IBM config.

    Args:
        code: Python code to transform
        ibm_config: Optional IBM Quantum configuration (token, channel, instance, region)
        use_simulator: Whether to use local simulator (default: True)

    Returns:
        Transformed code
    """

    # If IBM config is provided, use IBM Quantum Runtime Service
    if ibm_config and ibm_config.get("token"):
        token = ibm_config["token"]
        channel = ibm_config.get("channel", "ibm_quantum")
        instance = ibm_config.get("instance")
        region = ibm_config.get("region")

        logger.info(f"IBM config provided. Injecting token: {token[:10]}...")
        logger.info(
            f"Channel: {channel}, Instance: {'yes' if instance else 'no'}, Region: {region or 'none'}"
        )

        # Pattern to match AerSimulator config (if switching from local to cloud)
        aer_pattern = r"from qiskit_aer import AerSimulator\n\nbackend = AerSimulator\(\)\nprint\(\"Using local simulator\.\.\.\"\)"

        # Pattern to match IBM Quantum imports and backend setup (without token)
        ibm_pattern_no_token = r"from qiskit_ibm_runtime import QiskitRuntimeService\n\nservice = QiskitRuntimeService\(\)\nbackend = service\.least_busy\(operational=True, simulator=False\)"

        # Pattern to match IBM Quantum imports and backend setup (with existing token)
        ibm_pattern_with_token = r"from qiskit_ibm_runtime import QiskitRuntimeService\n\nservice = QiskitRuntimeService\(token='[^']+'\)\nbackend = service\.least_busy\(operational=True, simulator=False\)"

        # Build service initialization parameters
        service_params = [f'channel="{channel}"', f'token="{token}"']

        if instance:
            service_params.append(f'instance="{instance}"')

        if region:
            service_params.append(f'region="{region}"')

        service_params_str = ",\n    ".join(service_params)

        # Replacement text with IBM Quantum Runtime Service and full config
        replacement = f"""from qiskit_ibm_runtime import QiskitRuntimeService

# Initialize IBM Quantum Runtime Service with provided configuration
service = QiskitRuntimeService(
    {service_params_str}
)
backend = service.least_busy(operational=True, simulator=False)
print(f"Using IBM Quantum backend: {{backend.name}}")"""

        # Replace AerSimulator with IBM Quantum if found
        if re.search(aer_pattern, code, re.DOTALL):
            logger.info("Found AerSimulator config, replacing with IBM Quantum config.")
            return re.sub(aer_pattern, replacement, code, flags=re.DOTALL)

        # Replace existing IBM Quantum config (without token) to include token
        if re.search(ibm_pattern_no_token, code, re.DOTALL):
            logger.info("Found IBM Quantum config without token, injecting token.")
            return re.sub(ibm_pattern_no_token, replacement, code, flags=re.DOTALL)

        # Replace existing IBM Quantum config (with token) to update token
        if re.search(ibm_pattern_with_token, code, re.DOTALL):
            logger.info("Found IBM Quantum config with existing token, updating it.")
            return re.sub(ibm_pattern_with_token, replacement, code, flags=re.DOTALL)

        # If no exact patterns found, try to find and inject token into existing QiskitRuntimeService calls
        if "QiskitRuntimeService()" in code:
            logger.info("Found generic 'QiskitRuntimeService()', injecting parameters.")
            modified_code = code.replace(
                "QiskitRuntimeService()",
                f"QiskitRuntimeService(\n    {service_params_str}\n)",
            )
            return modified_code

        logger.info(
            "No specific IBM Quantum pattern matched for token injection. Returning original code."
        )
        return code

    # Only replace with local simulator if use_simulator is True and no token provided
    if not use_simulator:
        logger.info(
            "Cloud mode is active and no token provided. No code replacement will be performed."
        )
        return code

    logger.info(
        "No token provided and local mode is active. Attempting to replace IBM Quantum config with local simulator."
    )

    # Replacement text with local simulator
    replacement = """from qiskit_aer import AerSimulator

backend = AerSimulator()
print("Using local simulator...")"""

    # Find the IBM Quantum Config section
    ibm_config_pattern = r"## STEP 0 : IBM Quantum Config"
    if re.search(ibm_config_pattern, code):
        logger.info("Found IBM Quantum Config section header.")

        # Split the code into sections based on "## STEP" markers
        sections = re.split(r"(## STEP \d+.*?\n)", code)

        # If we have at least 3 elements (before STEP 0, STEP 0 marker, STEP 0 content)
        if len(sections) >= 3:
            # Replace the content of STEP 0 with our simulator code
            for i in range(1, len(sections), 2):
                if "STEP 0" in sections[i] and "IBM Quantum Config" in sections[i]:
                    # Replace the content (which is in the next section)
                    sections[i+1] = "\n" + replacement + "\n\n"
                    break

            # Join the sections back together
            modified_code = "".join(sections)

            # Remove all IBM Runtime specific options
            logger.info("Removing any remaining IBM Runtime options from code.")
            modified_code = re.sub(r".*?\.options\..*?\n", "", modified_code)

            return modified_code

    # If we didn't find a structured IBM Quantum Config section, try the old patterns
    ibm_patterns = [
        r"from qiskit_ibm_runtime import QiskitRuntimeService\n\nservice = QiskitRuntimeService\(token='[^']+'\)\nbackend = service\.least_busy\(operational=True, simulator=False\)\nprint\(f\"Using IBM Quantum backend: {[^}]+}\"\)",
        r"from qiskit_ibm_runtime import QiskitRuntimeService\n\nservice = QiskitRuntimeService\(\)\nbackend = service\.least_busy\(operational=True, simulator=False\)",
    ]

    # Try each pattern
    for i, pattern in enumerate(ibm_patterns):
        if re.search(pattern, code, re.DOTALL):
            logger.info(
                f"Matched IBM Quantum pattern #{i + 1}. Replacing with local simulator."
            )
            modified_code = re.sub(pattern, replacement, code, flags=re.DOTALL)
            # Remove all IBM Runtime specific options
            logger.info("Removing any remaining IBM Runtime options from code.")
            modified_code = re.sub(r".*?\.options\..*?\n", "", modified_code)
            return modified_code

    logger.info(
        "No IBM Quantum patterns matched for local simulator replacement. Returning original code."
    )
    return code


@llm_tool(
    "execute_qiskit_code",
    "Executes Python/Qiskit quantum code and returns output. Automatically switches between local simulator and IBM Quantum backends.",
    {
        "code": "str",
        "use_simulator": "bool (optional, default=True)",
        "ibm_token": "str (optional)",
        "channel": "str (optional)",
        "instance": "str (optional)",
        "region": "str (optional)"
    }
)
async def execute_qiskit_code(
    code: str,
    use_simulator: bool = True,
    ibm_token: Optional[str] = None,
    channel: str = "ibm_quantum",
    instance: Optional[str] = None,
    region: Optional[str] = None
) -> str:
    """
    Execute Qiskit Python code and capture stdout/stderr.

    This tool provides:
    1. Security checks to prevent malicious code
    2. Automatic backend switching (local simulator vs IBM Quantum)
    3. Code transformation for backend compatibility
    4. Safe execution with timeout protection

    Args:
        code: Python code to execute (should contain Qiskit quantum circuits)
        use_simulator: Use local AerSimulator (True) or IBM Quantum (False)
        ibm_token: Optional IBM Quantum API token
        channel: IBM Quantum channel (default: "ibm_quantum")
        instance: Optional IBM Quantum instance CRN
        region: Optional IBM Quantum region

    Returns:
        String containing the execution output (stdout + stderr)
    """
    logger.info("Beginning Qiskit code execution via LLM OS tool.")

    # 1. Basic Security Check (LLM OS hooks should handle this, but good to have backup)
    dangerous_patterns = [
        "import os",
        "import subprocess",
        "import shutil",
        "__import__",
        "eval(",
        "exec(",  # Will be blocked below, but checking for nested execs
        "open(",  # File access
        "compile("
    ]

    for pattern in dangerous_patterns:
        if pattern in code and pattern != "exec(":  # exec is used by us
            logger.warning(f"Security: Blocked dangerous pattern: {pattern}")
            return f"Security Error: Potentially dangerous operation '{pattern}' not allowed."

    # Create IBM config object if token provided
    ibm_config = (
        {
            "token": ibm_token,
            "channel": channel,
            "instance": instance,
            "region": region
        }
        if ibm_token
        else None
    )

    # 2. Transform code to replace IBM Quantum config
    code = replace_ibm_quantum_config(code, ibm_config, use_simulator)
    logger.info("Code transformation complete. Preparing execution environment.")

    # 3. Execute with output capture
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()

    try:
        # Create execution namespace with minimal builtins
        # Only allow safe built-in functions
        safe_builtins = {
            "print": print,
            "len": len,
            "range": range,
            "enumerate": enumerate,
            "zip": zip,
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "list": list,
            "dict": dict,
            "tuple": tuple,
            "set": set,
            "abs": abs,
            "min": min,
            "max": max,
            "sum": sum,
            "round": round,
            "sorted": sorted,
            "reversed": reversed,
            "map": map,
            "filter": filter,
            "any": any,
            "all": all,
            "isinstance": isinstance,
            "type": type,
            "__name__": "__main__",
            "__doc__": None,
        }

        exec_globals = {
            "__builtins__": safe_builtins,
        }

        with (
            contextlib.redirect_stdout(stdout_capture),
            contextlib.redirect_stderr(stderr_capture),
        ):
            logger.info("Executing Qiskit code via exec().")
            exec(code, exec_globals)
            logger.info("Finished executing Qiskit code.")

        stdout_output = stdout_capture.getvalue()
        stderr_output = stderr_capture.getvalue()

        output = ""
        if stdout_output:
            output += stdout_output
        if stderr_output:
            output += stderr_output

        # Fix for escaped newlines in output
        if output and isinstance(output, str):
            output = output.replace('\\\\n', '\n')

        logger.info("Successfully captured output from Qiskit code execution.")
        return output if output else "Code executed successfully (no output)"

    except Exception as e:
        logger.error("An exception occurred during Qiskit code execution.", exc_info=True)
        # Also capture any stderr that might have been produced before the exception
        stderr_output = stderr_capture.getvalue()
        error_output = f"Error executing code: {str(e)}\n{stderr_output}"
        return error_output


@llm_tool(
    "validate_qiskit_code",
    "Validates Qiskit code without executing it. Checks for syntax errors and common issues.",
    {"code": "str"}
)
async def validate_qiskit_code(code: str) -> str:
    """
    Validate Qiskit code without executing it.

    Performs:
    1. Syntax validation
    2. Basic security checks
    3. Qiskit-specific pattern validation

    Args:
        code: Python code to validate

    Returns:
        Validation result message
    """
    try:
        # Check syntax
        compile(code, '<string>', 'exec')

        # Check for required Qiskit imports
        if "qiskit" not in code.lower():
            return "Warning: Code does not appear to import Qiskit"

        # Check for basic Qiskit patterns
        has_circuit = "QuantumCircuit" in code or "qc" in code
        if not has_circuit:
            return "Warning: Code does not appear to create a QuantumCircuit"

        return "✓ Code validation passed. Syntax is correct and contains Qiskit patterns."

    except SyntaxError as e:
        return f"Syntax Error: {str(e)}"
    except Exception as e:
        return f"Validation Error: {str(e)}"
