# Project Aorta: Quantum Biomedical Signal Processing

**Quantum Biomedical Signal Processing with Three-Agent Cognitive Architecture**

This project demonstrates a specialized "Cognitive Trinity" agent architecture for complex biomedical problem-solving through autonomous AI agents. **Project Aorta** recreates a university bioengineering project using quantum homomorphic analysis for arterial navigation.

> 🌐 **Part of [Evolving Agents Labs](https://evolvingagentslabs.github.io)** | 🔬 [View All Experiments](https://evolvingagentslabs.github.io#experiments) | 📖 [Project Details](https://evolvingagentslabs.github.io/experiments/llmunix.html)

## 🧬 Project Overview: Revolutionary Medical Navigation

Project Aorta recreates a university Electronics 4 bioengineering project that aimed to navigate arterial systems without X-ray radiation by analyzing pressure wave echoes from arterial bifurcations. This implementation enhances the original concept using quantum computing techniques.

### The Medical Innovation

**Problem**: Current catheter navigation relies on X-ray imaging, exposing patients and medical staff to radiation during procedures like angioplasty and stent placement.

**Solution**: A radiation-free navigation system using:
- **Catheter length measurement** and insertion point tracking
- **Pressure wave echo analysis** from arterial bifurcations
- **Homomorphic signal processing** to detect echo delays
- **Anatomical mapping** to correlate echoes with vascular geometry
- **Real-time stenosis detection** for diagnostic capabilities

### Quantum Enhancement

The original classical cepstral analysis is enhanced with quantum computing:
- **Quantum Fourier Transform (QFT)** for enhanced frequency resolution
- **Quantum homomorphic processing** for superior echo separation
- **Parallel processing** of multiple reflection components
- **Noise resilience** through quantum error correction

## 🧠 Project-Specific: Three-Agent Cognitive Architecture

Project Aorta implements a specialized "Cognitive Trinity" architecture designed for complex biomedical research workflows:

### 1. VisionaryAgent 🎯
**Role**: Transforms high-level ideas into detailed scientific narratives
- Creates comprehensive project descriptions with medical context
- Explains real-world applications and clinical significance
- Provides compelling scientific storytelling

### 2. MathematicianAgent 🔬
**Role**: Develops rigorous mathematical frameworks
- Converts narratives into formal mathematical models
- Defines signal equations: `s(t) = p(t) + α·p(t-τ)`
- Formulates quantum operations: QFT → Log Operator → IQFT

### 3. QuantumEngineerAgent ⚛️
**Role**: Implements executable quantum computing solutions
- Translates mathematical frameworks into working Qiskit code
- Creates quantum circuits for homomorphic analysis
- Validates results against classical baselines

## 🚀 Quick Start Guide

### Prerequisites

- **[Claude Code](https://anthropic.com/claude-code)** installed on your system
- **Git** for repository cloning
- **LLMunix framework** initialized (run `setup_agents.sh/ps1` from main directory)
- **Note**: This project uses LLMunix's flexible architecture with a custom three-agent pipeline

### Running Project Aorta

From the main LLMunix directory:

```bash
# Boot LLMunix
claude --dangerously-skip-permissions --verbose "boot llmunix"

# Execute Project Aorta
claude --dangerously-skip-permissions --verbose "llmunix execute: 'Run the Project Aorta scenario to recreate my university bioengineering project using quantum homomorphic analysis of arterial pressure wave echoes. Use the three-agent cognitive pipeline: visionary-agent creates the project description, mathematician-agent develops the formal framework, and quantum-engineer-agent implements the Qiskit solution. Execute the final quantum implementation and validate results.'"
```

## 🧪 Example Executions

### Example 1: Validate Project Aorta & Generate Qiskit Code

This example demonstrates the complete three-agent pipeline and generates working quantum code:

#### Expected Execution Flow:

1. **SystemAgent Orchestration**:
   - Creates `workspace/project_aorta/` directory
   - Initializes state tracking and memory consultation

2. **Stage 1 - Vision (VisionaryAgent)**:
   - Generates comprehensive project description
   - Output: `workspace/project_aorta/project_vision.md`
   - Includes medical context, problem significance, and solution approach

3. **Stage 2 - Theory (MathematicianAgent)**:
   - Transforms vision into rigorous mathematics
   - Output: `workspace/project_aorta/mathematical_framework.md`
   - Defines signal models and quantum operations

4. **Stage 3 - Implementation (QuantumEngineerAgent)**:
   - Creates executable Qiskit implementation
   - Output: `workspace/project_aorta/quantum_aorta_implementation.py`
   - Includes quantum circuit construction and validation

5. **Validation & Execution**:
   - Runs the generated Python/Qiskit code
   - Compares quantum vs classical echo detection
   - Generates performance analysis report

#### Expected Output Files:

```
workspace/project_aorta/
├── project_vision.md              # Scientific narrative and context
├── mathematical_framework.md      # Formal mathematical model
├── quantum_aorta_implementation.py # Complete Qiskit code
├── classical_baseline.py          # Classical comparison
├── validation_results.md          # Performance analysis
├── execution_report.md            # Complete pipeline summary
└── state/                         # Execution state tracking
```

### Example 2: Generate LinkedIn Article

```bash
claude --dangerously-skip-permissions --verbose "llmunix execute: 'Create a compelling LinkedIn article about the Project Aorta experiment. Explain how I recreated my university bioengineering project using AI agents and quantum computing. The article should highlight the innovation of using quantum homomorphic analysis for arterial navigation, the three-agent cognitive architecture (Vision → Theory → Implementation), and the potential medical impact of radiation-free catheter navigation. Include technical details about pressure wave echo analysis and quantum advantages. Make it engaging for both technical and non-technical audiences. Target length: 800-1000 words. Include a call-to-action to visit the GitHub repository.'"
```

## 🧬 Scientific Foundation

### Cardiovascular Physics

**Echo Formation**: Pressure waves reflect at arterial bifurcations due to impedance mismatches
- Geometric changes (one vessel → two vessels)
- Vessel wall property differences
- Flow dynamics alterations

**Signal Model**: `s(t) = p(t) + α * p(t - τ)`
- `p(t)`: Primary cardiac pressure pulse (~1-2 Hz)
- `α`: Attenuation factor (0 < α < 1)
- `τ`: Echo delay time (proportional to distance)

### Quantum Advantages

**Enhanced Resolution**: QFT provides superior frequency analysis for overlapping echoes
**Parallel Processing**: Quantum superposition enables simultaneous analysis
**Noise Resilience**: Quantum error correction improves signal-to-noise ratio
**Real-time Performance**: Faster processing for time-critical medical procedures

## 🎯 Expected Results

### Technical Outcomes

- **Working Qiskit Implementation**: Complete quantum circuit for homomorphic analysis
- **Validation Results**: Comparison showing quantum vs classical echo detection accuracy
- **Performance Metrics**: Processing time, accuracy, and resource utilization
- **Medical Relevance**: Demonstration of radiation-free navigation feasibility

### Content Outcomes

- **Professional Article**: LinkedIn-ready content highlighting innovation and impact
- **Technical Documentation**: Complete mathematical and implementation details
- **Execution Reports**: Detailed analysis of three-agent cognitive pipeline

## 📁 Project Structure

```
projects/Project_aorta/
├── README.md                    # This file
├── input/                       # Input documentation and instructions
├── output/                      # Generated outputs and results
└── workspace/                   # Active workspace during execution
```

## 🌟 About This Project

This project demonstrates the potential of autonomous AI systems for scientific research and innovation. Project Aorta showcases how AI can enhance and reimagine existing research using cutting-edge quantum computing techniques.

**Key Innovation**: The three-agent cognitive architecture (Vision → Theory → Implementation) mirrors human scientific problem-solving while leveraging AI's computational advantages.

---

*Original Concept: Matias Molinas and Ismael Faro - Evolving Agents Labs*