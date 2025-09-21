---
name: quantum-computing-tool
description: A specialized tool for managing quantum computing environments, installing dependencies, and executing quantum workflows
tools: Bash, Write, Read
---

# QuantumComputingTool
This tool provides comprehensive support for quantum computing workflows, including dependency management, environment setup, and quantum circuit execution using Qiskit.

## Capabilities

### Environment Setup
- Install and manage Qiskit and quantum computing dependencies
- Set up Python virtual environments for quantum projects
- Verify quantum computing library installations

### Quantum Circuit Execution
- Execute Qiskit circuits on simulators
- Manage quantum backend connections
- Handle quantum job submission and result retrieval

### Dependency Management
- Install required packages: qiskit, qiskit-aer, numpy, matplotlib
- Manage version compatibility
- Set up development environments

## Usage Patterns

### Install Quantum Dependencies
```bash
pip install 'qiskit[visualization]' qiskit-aer numpy matplotlib scipy
```

### Create Quantum Development Environment
```bash
python -m venv quantum_env
source quantum_env/bin/activate  # On Unix/Linux/Mac
pip install --upgrade pip
pip install qiskit qiskit-aer jupyter notebook
```

### Execute Quantum Code
```python
import subprocess
import sys

def run_quantum_script(script_path):
    """Execute a quantum Python script and return results"""
    result = subprocess.run([sys.executable, script_path], 
                          capture_output=True, text=True)
    return result.stdout, result.stderr, result.returncode
```

## Error Handling

### Common Issues
- Import errors for quantum libraries
- Circuit execution timeouts
- Simulator memory limitations
- Backend connectivity issues

### Resolution Strategies
- Automatic dependency installation
- Fallback to different simulators
- Memory optimization for large circuits
- Retry logic for network operations

## Integration with LLMunix

This tool integrates with the Project Aorta workflow by:
1. Setting up quantum environments for the QuantumEngineerAgent
2. Executing generated Qiskit code safely
3. Managing quantum simulation resources
4. Providing error recovery for quantum workflows

## Cost and Performance

- **Setup Cost**: Medium (requires package installation)
- **Execution Cost**: Variable (depends on circuit complexity)
- **Latency**: 
  - Environment setup: 30-300 seconds
  - Simple circuit execution: 1-10 seconds
  - Complex circuits: 10-300 seconds

## Security Considerations

- Sandboxed execution of quantum code
- Dependency verification
- Resource usage monitoring
- Safe handling of quantum circuit outputs