# Smart Library - Component Registry

This file maintains a complete registry of all agents and tools available in the LLMunix system. Components are organized by category and include metadata for intelligent selection and delegation.

## System Agents

### Core Orchestration

#### SystemAgent
- **File**: `system/agents/SystemAgent.md`
- **Type**: Orchestration
- **Version**: 2.0
- **Status**: Production
- **Capabilities**: Task orchestration, sub-agent delegation, state management, learner-follower pattern, mobile app workflow
- **Tools**: Read, Write, Glob, Grep, Bash, WebFetch, Task
- **Use Cases**: All complex multi-step tasks, project execution, mobile app generation coordination
- **Mode**: EXECUTION, SIMULATION

#### GraniteFollowerAgent
- **File**: `system/agents/GraniteFollowerAgent.md`
- **Type**: Execution
- **Version**: 1.0
- **Status**: Production
- **Capabilities**: Execute high-confidence execution traces deterministically
- **Tools**: Read, Write, Bash, Task
- **Use Cases**: Repetitive tasks with proven execution traces (>0.9 confidence)
- **Mode**: EXECUTION only
- **Cost**: 20-80x cheaper than learner mode

### Memory and Learning

#### MemoryAnalysisAgent
- **File**: `system/agents/MemoryAnalysisAgent.md`
- **Type**: Specialized
- **Version**: 1.0
- **Status**: Production
- **Capabilities**: Cross-project pattern recognition, behavioral learning extraction, error recovery strategies
- **Tools**: Read, Grep, Write
- **Use Cases**: Memory consultation, pattern extraction, learning consolidation
- **Mode**: EXECUTION

#### MemoryConsolidationAgent
- **File**: `system/agents/MemoryConsolidationAgent.md`
- **Type**: Specialized
- **Version**: 1.0
- **Status**: Production
- **Capabilities**: Consolidate short-term memories into long-term insights
- **Tools**: Read, Write, Grep
- **Use Cases**: Post-execution learning consolidation, insight extraction
- **Mode**: EXECUTION

### User and Personalization

#### UserMemoryAgent
- **File**: `system/agents/UserMemoryAgent.md`
- **Type**: Specialized
- **Version**: 1.0
- **Status**: Production
- **Capabilities**: User profile management, habit inference, personalization data
- **Tools**: Read, Write, Edit
- **Use Cases**: User personalization, preference tracking, habit analysis
- **Mode**: EXECUTION
- **Related**: UI generation, mobile app personalization

### Mobile App Generation

#### CodeGeneratorAgent
- **File**: `system/agents/CodeGeneratorAgent.md`
- **Type**: Specialized
- **Category**: Mobile Generation
- **Version**: 1.0
- **Status**: Production
- **Capabilities**: React Native app generation, agentic vs deterministic classification, LLM integration
- **Tools**: Read, Write, Glob, Bash, Task
- **Use Cases**: Generate mobile apps from project outputs, create React Native codebases
- **Mode**: EXECUTION
- **Output**: Complete React Native app with optional on-device LLM
- **Delegation**: Invokes MobileAppAnalyzer and MobileAppBuilder

#### UIGeneratorAgent
- **File**: `system/agents/UIGeneratorAgent.md`
- **Type**: Specialized
- **Version**: 1.0
- **Status**: Production (Legacy - superseded by CodeGeneratorAgent for full app generation)
- **Capabilities**: UI-MD generation, component composition, personalization
- **Tools**: Task, Write, Read, Edit
- **Use Cases**: Generate UI-MD definitions for Wabi POC
- **Mode**: EXECUTION
- **Note**: Kept for UI-MD approach, CodeGeneratorAgent handles full code generation

## System Tools

### Core Tooling

#### ClaudeCodeToolMap
- **File**: `system/tools/ClaudeCodeToolMap.md`
- **Type**: Tool Mapping
- **Version**: 1.0
- **Status**: Production
- **Purpose**: Maps LLMunix markdown tools to Claude Code native tools
- **Provides**: Read, Write, Edit, Glob, Grep, Bash, WebFetch, Task mappings
- **Use**: Reference for all tool implementations

#### QueryMemoryTool
- **File**: `system/tools/QueryMemoryTool.md`
- **Type**: Memory Interface
- **Version**: 1.0
- **Status**: Production
- **Purpose**: Standardized interface for memory consultation
- **Delegation**: Invokes MemoryAnalysisAgent as sub-agent
- **Use Cases**: Planning, error recovery, strategy selection
- **Returns**: Historical patterns, recommendations, success/failure examples

#### MemoryTraceManager
- **File**: `system/tools/MemoryTraceManager.md`
- **Type**: Trace Management
- **Version**: 1.0
- **Status**: Production
- **Purpose**: Manage execution traces for follower mode
- **Capabilities**: Trace generation, indexing, retrieval, evolution
- **Use Cases**: Create execution traces from learner runs, retrieve for follower mode
- **Storage**: SQLite index + markdown traces

### Mobile App Generation Tools

#### MobileAppAnalyzer
- **File**: `system/tools/MobileAppAnalyzer.md`
- **Type**: Classification Tool
- **Category**: Mobile Generation
- **Version**: 1.0
- **Status**: Production
- **Purpose**: Classify mobile apps as agentic (LLM required) vs deterministic (code-only)
- **Claude Tools**: Read, Grep
- **Use Cases**: Determine if app needs on-device LLM, recommend model (Qwen vs Granite)
- **Output**: Classification, model recommendation, size estimates
- **Accuracy**: 90% deterministic, 10% agentic detection
- **Model Selection**: Qwen3-0.6B (general), Granite 4.0 H-1B (code generation)

#### MobileAppBuilder
- **File**: `system/tools/MobileAppBuilder.md`
- **Type**: Bundling Tool
- **Category**: Mobile Generation
- **Version**: 1.0
- **Status**: Production
- **Purpose**: Bundle complete React Native apps with optional LLM models
- **Claude Tools**: Write, Bash, Read
- **Capabilities**: Dependency management, config generation, LLM bundling, validation
- **Output**: Deployment-ready mobile app package
- **Formats**: package.json, tsconfig.json, manifest.json, README.md
- **LLM Models**: Qwen3-0.6B-INT4 (600MB), Granite 4.0 H-1B-INT4 (1.5GB)

## Component Selection Guidelines

### When to Use SystemAgent
- **All project execution**: SystemAgent orchestrates all multi-step workflows
- **Mobile app requests**: Detects mobile keywords and delegates to CodeGeneratorAgent
- **Complex tasks**: Requires sub-agent coordination
- **State management**: Needs workspace/state/ directory management

### When to Use GraniteFollowerAgent
- **High-confidence traces**: Execution trace confidence >= 0.9
- **Cost optimization**: 20-80x cheaper than learner mode
- **Speed priority**: Deterministic execution is faster
- **Repetitive tasks**: Same workflow executed multiple times

### When to Use CodeGeneratorAgent
- **Mobile app generation**: User requests "mobile app", "generate app", etc.
- **After primary execution**: CLI results exist in project/output/
- **React Native apps**: Full codebase generation needed
- **Agentic apps**: Apps requiring on-device LLM integration

### When to Use MobileAppAnalyzer
- **App classification**: Before bundling, determine if LLM is needed
- **Model selection**: Choose between Qwen3-0.6B and Granite 4.0 H-1B
- **Size estimation**: Calculate total app size with/without LLM

### When to Use MobileAppBuilder
- **Final bundling**: After code generation and classification
- **Deployment package**: Create complete, production-ready app
- **Configuration**: Generate all required config files

### When to Use Memory Tools
- **Planning phase**: QueryMemoryTool for historical patterns
- **Post-execution**: MemoryConsolidationAgent for learning extraction
- **Error recovery**: QueryMemoryTool for failure patterns

## Mobile App Generation Workflow

Complete workflow for mobile app generation:

```
User Request: "Create a mobile app for habit tracking"
    ↓
1. SystemAgent detects "mobile app" keyword
    ↓
2. SystemAgent executes primary task (habit tracking analysis)
    ↓
3. SystemAgent invokes CodeGeneratorAgent
    ↓
4. CodeGeneratorAgent reads project outputs
    ↓
5. CodeGeneratorAgent generates React Native code
    ↓
6. CodeGeneratorAgent invokes MobileAppAnalyzer
    ↓
7. MobileAppAnalyzer classifies: "deterministic" (no LLM)
    ↓
8. CodeGeneratorAgent invokes MobileAppBuilder
    ↓
9. MobileAppBuilder creates deployment package
    ↓
10. Output: projects/Project_habit_tracker/mobile_app/ (15MB)
```

**With Agentic App (Personal Trainer):**

```
User Request: "Create a mobile personal trainer app that adapts workouts"
    ↓
... steps 1-6 same ...
    ↓
7. MobileAppAnalyzer classifies: "agentic" (LLM required)
    ↓
8. MobileAppAnalyzer recommends: Qwen3-0.6B (600MB)
    ↓
9. CodeGeneratorAgent generates LLM integration code
    ↓
10. MobileAppBuilder bundles app + Qwen3-0.6B model
    ↓
11. Output: projects/Project_personal_trainer/mobile_app/ (635MB)
```

## Model Selection Matrix

Based on comprehensive Granite 4 Nano vs Qwen 3 analysis:

### Qwen3-0.6B-INT4 (Primary)
- **Use When**: General agentic apps, conversational AI, multilingual support
- **Size**: 600MB
- **Quality**: 52.81 MMLU
- **Speed**: 50-150 tokens/sec (CPU), 200-500 tokens/sec (NPU)
- **Languages**: 100+ languages
- **Strengths**: Proven ecosystem, broad language support, balanced quality/size
- **License**: Apache 2.0

### Granite 4.0 H-1B-INT4 (Alternative)
- **Use When**: Code generation, structured output, instruction following
- **Size**: 1.5GB
- **Quality**: 73.0 HumanEval, 82.37 IFEval
- **Speed**: 30-80 tokens/sec (CPU), 100-300 tokens/sec (NPU)
- **Strengths**: Superior coding (HumanEval 73.0), instruction following (IFEval 82.37)
- **License**: Apache 2.0

### None (Deterministic)
- **Use When**: 90% of apps (rule-based logic, no NLU/NLG)
- **Size**: 0MB (code only)
- **Speed**: Instant
- **Strengths**: Minimal size, maximum speed, works offline

## Version History

### v1.0 (Current)
- SystemAgent with mobile app generation support
- CodeGeneratorAgent for React Native generation
- MobileAppAnalyzer for agentic vs deterministic classification
- MobileAppBuilder for deployment bundling
- Qwen3-0.6B and Granite 4.0 H-1B model support
- Learner-follower pattern with execution traces

## Future Components

### Planned Agents
- **WebAppGeneratorAgent**: Next.js/React web app generation
- **DesktopAppGeneratorAgent**: Electron desktop app generation
- **CodeOptimizerAgent**: AI-powered code optimization

### Planned Tools
- **ModelDownloader**: On-demand LLM model downloading
- **AppAnalyticsTool**: Usage analytics integration
- **A/BTesting Tool**: Generate variant apps for testing

## Related Documentation

- **CLAUDE.md**: Overall LLMunix system configuration and workflows
- **SystemAgent.md**: Core orchestration agent details
- **Mobile App Analysis**: `projects/Project_on_device_wabi_analysis/output/`
  - `granite_qwen_comparison.md`: Model selection research
  - `CODE_GENERATION_ARCHITECTURE.md`: Architecture design
  - `EXECUTIVE_SUMMARY.md`: Complete analysis summary

## Component Discovery

All agents in `system/agents/` are automatically copied to `.claude/agents/` for Claude Code discovery:

- `SystemAgent.md` → `.claude/agents/SystemAgent.md`
- `CodeGeneratorAgent.md` → `.claude/agents/CodeGeneratorAgent.md`
- `MemoryAnalysisAgent.md` → `.claude/agents/MemoryAnalysisAgent.md`
- etc.

Project-specific agents are copied with project prefix:
- `projects/Project_aorta/components/agents/VisionaryAgent.md` → `.claude/agents/Project_aorta_VisionaryAgent.md`

## Usage Example

```yaml
# SystemAgent orchestrates mobile app generation
user_request: "Create a mobile app for habit tracking"

system_agent:
  detects: mobile_app_keyword
  executes: primary_workflow (habit analysis)
  delegates:
    - agent: code-generator-agent
      purpose: Generate React Native app
      input: projects/Project_habit_tracker/output/

code_generator_agent:
  reads: project_outputs
  generates: React Native codebase
  delegates:
    - tool: mobile-app-analyzer
      purpose: Classify app type
    - tool: mobile-app-builder
      purpose: Bundle deployment package

mobile_app_analyzer:
  analyzes: app_requirements
  classification: deterministic
  llm_required: false

mobile_app_builder:
  bundles: React Native code + dependencies
  output: projects/Project_habit_tracker/mobile_app/
  size: 15MB
  status: ready_for_deployment
```

---

**Last Updated**: 2025-11-08
**Total Agents**: 7
**Total Tools**: 5
**Mobile Generation**: Enabled
**Status**: Production Ready
