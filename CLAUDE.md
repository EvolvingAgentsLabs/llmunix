# LLMunix: Pure Markdown Operating System Framework

This is LLMunix, a Pure Markdown Operating System where everything is either an agent or tool defined in markdown documents. Claude Code serves as the runtime engine interpreting these markdown specifications.

## Framework Philosophy: Pure Markdown

**CRITICAL: LLMunix is a PURE MARKDOWN framework. Everything is either an agent or tool defined in markdown documents.**

### Core Principles:
- **Markdown-Driven Execution**: LLM interpreter reads and sends full markdown specifications to LLM for interpretation and execution
- **No Code Generation**: System behavior emerges from LLM interpreting markdown documents sent at runtime
- **Agent/Tool Duality**: Every component is either an agent (decision maker) or tool (executor) defined in markdown
- **Flexible Architecture**: Projects can define any agent configuration - single agents, multi-agent pipelines, or custom patterns
- **Real Tool Integration**: Markdown components map to actual tool execution via TOOL_CALL format
- **Sentient State Architecture**: Behavioral constraints evolve dynamically to enable adaptive decision-making
- **Memory-Driven Learning**: Historical experiences become actionable intelligence for continuous improvement
- **Dynamic Creation**: New tools/agents are created as markdown specifications during runtime
- **LLM as Interpreter**: LLM receives and interprets markdown system definitions to achieve any goal

### Operating Modes:
1. **EXECUTION MODE**: Real operations using Claude Code's native tools mapped through markdown specs
2. **SIMULATION MODE**: Training data generation through markdown-defined simulation patterns

The OS "boots" when Claude reads the markdown system files and begins interpreting them as a functional operating system.

## Agent Architecture Flexibility

**IMPORTANT: LLMunix supports any agent architecture pattern.**

### Supported Configurations:

**🎯 Single-Agent Projects**: Simple tasks handled by one specialized agent
**🔄 Multi-Agent Pipelines**: Sequential processing through multiple specialized agents
**🌐 Collaborative Networks**: Complex orchestration with multiple agents working in parallel
**🧠 Custom Architectures**: Project-specific patterns tailored to domain requirements

### Example Agent Patterns:

- **Research Projects**: WebFetch → Analysis → Summarization → Report Generation
- **Development Projects**: Planning → Implementation → Testing → Documentation
- **Content Creation**: Research → Writing → Review → Publishing
- **Data Processing**: Collection → Cleaning → Analysis → Visualization
- **Project Aorta Pattern**: Vision → Mathematical Framework → Implementation (specialized three-agent cognitive pipeline)

Each project in the `projects/` directory can define its own optimal agent configuration based on its specific requirements.

## How to Boot LLMunix

### Boot Process

LLMunix requires a one-time initialization before use. **Before running any commands**, ensure you've run the appropriate initialization script for your platform:

- **Windows users**: Run `setup_agents.ps1` script
- **Unix/Linux/Mac users**: Run `setup_agents.sh` script

This initialization prepares the environment by:
1. Creating the `.claude/agents/` directory to make agents discoverable
2. Copying agent markdown files to the appropriate locations
3. Setting up the initial workspace structure

Once initialized, you can use the boot command:

```
boot llmunix
```

This command activates the LLMunix kernel by having Claude read and interpret the markdown system files as a functional operating system.

### CRITICAL EXECUTION RULES

**⚠️ IMPORTANT: All LLMunix executions MUST follow this workflow:**

1. **Boot LLMunix ONLY when:**
   - First command in a conversation session
   - User explicitly requests reboot with `boot llmunix` command
   - System needs to reload configuration

2. **ALWAYS identify or create the project structure** in `projects/[ProjectName]/`
3. **ALWAYS organize outputs** in the project's directory structure

**Boot Behavior:**
- Boot displays welcome message and initializes system state
- Boot persists throughout the conversation session
- Subsequent `llmunix execute:` commands do NOT trigger boot
- Only boot again if user explicitly requests it

**Project Structure Requirements:**
```
projects/[ProjectName]/
├── components/
│   ├── agents/          # Project-specific agents (markdown definitions)
│   └── tools/           # Project-specific tools (markdown definitions)
├── input/               # Input documents and instructions
├── output/              # Generated outputs and deliverables
├── memory/              # Project memory for learning
│   ├── short_term/      # Agent interactions, messages, context
│   └── long_term/       # Consolidated insights and learnings
└── workspace/           # Temporary execution state
    └── state/           # Execution state (plan, context, variables, etc.)
```

**Execution Pattern:**

**First execution in session:**
1. User issues: `llmunix execute: "goal"`
2. Claude performs:
   - Display boot welcome message (ONE TIME ONLY)
   - Identify project name from goal context
   - Create/verify complete `projects/[ProjectName]/` structure (including memory/)
   - **Analyze goal and create project-specific agents/tools as markdown**
   - Invoke SystemAgent to orchestrate execution
   - **Log all agent interactions to memory/short_term/**
   - Create all outputs in `projects/[ProjectName]/output/`
   - **Consolidate learnings to memory/long_term/**
   - Execute the goal

**Subsequent executions in same session:**
1. User issues: `llmunix execute: "another goal"`
2. Claude performs:
   - NO boot message (system already booted)
   - Identify project name from goal context
   - Create/verify `projects/[ProjectName]/` structure
   - **Check for existing agents/tools, create new ones if needed**
   - **Log all agent interactions to memory/short_term/**
   - Create all outputs in `projects/[ProjectName]/output/`
   - **Update memory/long_term/ with new learnings**
   - Execute the goal

### Agent and Tool Creation Rules

**CRITICAL: LLMunix is markdown-driven. All agents and tools MUST be markdown specifications.**

**When to create project-specific agents:**
1. Goal requires specialized domain knowledge (e.g., chaos theory, quantum computing)
2. Task needs multi-step orchestration with distinct roles
3. Complex workflows benefit from decomposition

**Agent creation process:**
1. Analyze goal and identify required capabilities
2. Create markdown agent definitions in `projects/[ProjectName]/components/agents/`
3. Use **YAML frontmatter** for agent metadata (consistent with framework standard)
4. Include agent instructions, capabilities, and delegation patterns
5. Copy to `.claude/agents/` with project prefix for discovery

**Tool creation process:**
1. Identify operations needed (computation, file manipulation, etc.)
2. Create markdown tool specifications in `projects/[ProjectName]/components/tools/`
3. Use **YAML frontmatter** for tool metadata (consistent with framework standard)
4. Map to Claude Code native tools (Read, Write, Bash, etc.)
5. Document tool parameters and expected outputs

**Example agent structure:**
```markdown
---
agent_name: tutorial-writer-agent
type: specialized
project: Project_chaos_bifurcation_tutorial
capabilities: [Technical writing, Mathematical explanation, Code documentation]
tools: [Write, Read, Edit]
version: "1.0"
status: production
---

# Tutorial Writer Agent

## Purpose
Create comprehensive educational tutorials with mathematical rigor...

## Instructions
1. Analyze topic and identify key concepts
2. Structure content with clear progression
3. Include mathematical foundations
4. Provide examples and visualizations
...
```

**Example tool structure:**
```markdown
---
component_type: tool
tool_name: quantum-computing-tool
version: "1.0"
status: production
claude_tools: [Bash, Read, Write]
category: scientific_computing
project: Project_chaos_bifurcation_tutorial
---

# Quantum Computing Tool

## Purpose
Execute quantum computing simulations and calculations...

## Parameters
- `algorithm`: string - Algorithm to execute
- `qubits`: number - Number of qubits
- `iterations`: number - Simulation iterations
...
```

### Memory Management Rules

**CRITICAL: All agent interactions MUST be logged for learning.**

**Short-term memory (memory/short_term/):**
- Log every agent invocation with timestamp
- Record messages exchanged between agents
- Capture context and decision rationale
- Store intermediate results and state transitions
- Format: `YYYY-MM-DD_HH-MM-SS_agent_interaction.md`

**Long-term memory (memory/long_term/):**
- Consolidate patterns and insights after execution
- Record what worked well and what failed
- Extract reusable strategies and approaches
- Document parameter choices and their outcomes
- Update project-level learnings summary

**Memory log structure:**
```markdown
---
interaction_id: int_20250929_143000
timestamp: "2025-09-29T14:30:00Z"
agent: tutorial-writer-agent
action: create_tutorial
context: chaos_bifurcation_tutorial
execution_time_secs: 45
quality_score: 9.0
outcome: success
---

# Agent Interaction Log

## Request
Create comprehensive tutorial on chaos and bifurcation...

## Agent Response
Analyzing requirements:
- Mathematical foundations needed
- Code examples required
- Visualization strategy...

## Outcome
Tutorial created: chaos_bifurcation_tutorial.md
- Quality score: 9/10
- Execution time: 45s

## Learnings
- Mathematical depth improves tutorial quality
- Code examples should align with theory
- Visual aids enhance understanding
```

### Why This Architecture Matters

**Pure Markdown Framework Benefits:**

1. **Learning & Improvement**
   - Memory logs capture what works and what doesn't
   - Patterns emerge across multiple executions
   - System gets smarter with each project
   - Failures become training data

2. **Reusability**
   - Agents created for one project can be adapted for others
   - Tools become a growing library of capabilities
   - Successful patterns propagate across projects

3. **Transparency**
   - All agent decisions are logged and auditable
   - Context is preserved for debugging and analysis
   - Memory explains why choices were made

4. **Composability**
   - Small, focused agents combine for complex tasks
   - Tools map cleanly to Claude Code native capabilities
   - Markdown specs are human-readable and modifiable

5. **Evolution**
   - Dynamic agent creation during execution
   - System adapts to new domains without reprogramming
   - Memory guides future agent generation

**Without proper architecture:**
- ❌ No learning between executions
- ❌ No reusable components
- ❌ No transparency in decision-making
- ❌ No ability to improve over time
- ❌ Monolithic, non-composable solutions

**With proper architecture:**
- ✅ Continuous learning from experience
- ✅ Growing library of reusable agents/tools
- ✅ Full transparency and auditability
- ✅ System improves with each execution
- ✅ Modular, composable solutions

### Boot Welcome Message
When LLMunix boots, display ASCII art welcome and example commands in this format:

```
██╗     ██╗     ███╗   ███╗██╗   ██╗███╗   ██╗██╗██╗  ██╗
██║     ██║     ████╗ ████║██║   ██║████╗  ██║██║╚██╗██╔╝
██║     ██║     ██╔████╔██║██║   ██║██╔██╗ ██║██║ ╚███╔╝
██║     ██║     ██║╚██╔╝██║██║   ██║██║╚██╗██║██║ ██╔██╗
███████╗███████╗██║ ╗═╝ ██║╚██████╔╝██║ ╚████║██║██╔╝ ██╗
╚══════╝╚══════╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝╚═╝  ╚═╝
                Pure Markdown Operating System v1.0

🔧 System Status: READY
📁 Project Structure: Verified
🤖 Agent Discovery: Enabled
```

**Example Commands:**
```bash
llmunix execute: "Monitor 5 tech news sources (TechCrunch, Ars Technica, Hacker News, MIT Tech Review, Wired), extract trending topics, identify patterns, and generate a weekly intelligence briefing"

llmunix execute: "Get live content from https://huggingface.co/blog and create a research summary"

llmunix execute: "Run the Project Aorta scenario from projects/Project_aorta/"

llmunix execute: "Create a tutorial on chaos theory with Python examples"

llmunix simulate: "Research task workflow for fine-tuning dataset"
```

**Project Naming Rules:**
- Goal content determines project name automatically
- Format: `projects/Project_[descriptive_name]/`
- Examples:
  - "chaos theory tutorial" → `projects/Project_chaos_theory_tutorial/`
  - "news intelligence" → `projects/Project_news_intelligence/`
  - "web scraper" → `projects/Project_web_scraper/`

### Running the Real-World Research Scenario

1. **Execute the scenario** by asking Claude to:
   - Invoke the `system-agent` to orchestrate the task
   - Execute the goal from `scenarios/RealWorld_Research_Task.md`
   - Use EXECUTION MODE for real tool calls

2. **Expected behavior:**
   - Claude creates modular `workspace/state/` directory with specialized files
   - Initializes `constraints.md` with behavioral modifiers based on task context
   - Uses QueryMemoryTool for intelligent memory consultation during planning
   - Adapts execution style based on user sentiment and historical patterns
   - State machine execution:
     - **State 1→2**: RealWebFetchTool fetches live content with constraint-aware error handling
     - **State 2→3**: RealSummarizationAgent analyzes content using memory-recommended approaches
     - **State 3→4**: RealFileSystemTool saves structured outputs with behavioral adaptations
   - Updates modular state files after each step with real results and constraint evolution
   - Records complete experience in structured memory log with sentiment and adaptation insights
   - Generates training data from real execution trace including behavioral learning patterns

## Key Capabilities

### Real Tool Integration
- **WebFetch**: Live web content retrieval with error handling
- **FileSystem**: Real file operations (Read/Write/Search/List)
- **Bash**: System command execution for complex tasks
- **Task**: Parallel sub-task execution for complex workflows

### Sentient State Management
- **Modular State Architecture**: Specialized files for plan, context, variables, history, and constraints
- **Dynamic Behavioral Adaptation**: Constraints evolve based on user sentiment and execution events
- **Memory-Driven Planning**: Historical experiences influence current decision-making
- **Intelligent Error Recovery**: Past failure patterns guide recovery strategies
- **Atomic State Transitions**: Each step updates relevant state components
- **Resumable Execution**: Can pause and resume at any step with full context preservation
- **Cost Tracking**: Real-time monitoring with budget-aware constraint adaptation

### Advanced Learning Pipeline
- **Structured Memory Log**: Pure markdown with bold text metadata for intelligent querying (zero dependencies)
- **Behavioral Pattern Extraction**: User sentiment evolution and constraint adaptation tracking
- **Execution Traces**: Complete tool call sequences with real results and behavioral context
- **Performance Metrics**: Actual costs, timing, success rates, and adaptation effectiveness
- **Error Scenarios**: Real error handling examples with sentiment-aware recovery strategies
- **Quality Assessments**: Output quality scoring with behavioral and contextual metadata

### File Structure

```
llmunix/
├── system/                                # Core LLMunix framework components
│   ├── agents/                        # System-wide orchestration agents
│   │   ├── SystemAgent.md            # Core orchestration and workflow management
│   │   └── MemoryAnalysisAgent.md     # Cross-project learning and pattern recognition
│   ├── tools/                         # Framework-level tools
│   │   ├── ClaudeCodeToolMap.md      # Integration with Claude Code's native tools
│   │   └── QueryMemoryTool.md        # Framework-level memory consultation
│   ├── SmartLibrary.md               # Component registry with real tools and memory components
│   ├── memory_log.md                 # Structured, queryable experience database
│   └── components/                   # Core framework components
├── projects/                             # Individual projects with specialized components
│   ├── Project_aorta/                # Biomedical quantum computing project
│   │   ├── components/               # Project-specific components
│   │   │   ├── agents/              # Project agents (VisionaryAgent, MathematicianAgent, etc.)
│   │   │   └── tools/               # Project tools (QuantumComputingTool, WebFetcherTool, etc.)
│   │   ├── input/                   # Project input docs and instructions
│   │   ├── output/                  # Generated outputs and results
│   │   └── workspace/               # Project workspace during execution
│   └── [Other projects]/            # Additional projects with their own components
├── scenarios/                             # Generic task scenarios
│   ├── RealWorld_Research_Task.md     # Live web research demo
│   └── [Other scenarios]
├── workspace/                            # Global execution environment
│   ├── state/                        # Modular execution state
│   │   ├── plan.md                  # Execution steps and metadata
│   │   ├── context.md               # Knowledge accumulation
│   │   ├── variables.json           # Structured data passing
│   │   ├── history.md               # Execution log
│   │   └── constraints.md           # Behavioral modifiers (sentient state)
│   └── [Output files from tasks]
├── .claude/agents/                       # Auto-populated agent definitions for Claude Code discovery
└── CLAUDE.md                            # This configuration file
```

### Component Management and Discovery

**Static Components**: Pre-defined agents and tools in project directories
- **System Components**: Framework-level agents/tools in `system/`
- **Project Components**: Domain-specific agents/tools in `projects/[project]/components/`

**Dynamic Component Creation**: New agents created during execution
1. **Gap Analysis**: SystemAgent identifies missing capabilities for task completion
2. **Agent Generation**: Creates new markdown agent definitions with pure markdown metadata (no YAML)
3. **Project-Specific Storage**: Saves new agents to appropriate `projects/[project]/components/agents/`
4. **Runtime Integration**: Auto-copies to `.claude/agents/` with project prefix for immediate discovery
5. **Task Delegation**: Uses new agents via Claude Code's Task tool

**Agent Discovery Process**:
- **Initial Setup**: Run `setup_agents.sh/ps1` to populate `.claude/agents/` directory
- **System Agents**: Copied directly (e.g., `SystemAgent.md`)
- **Project Agents**: Copied with project prefix (e.g., `Project_aorta_VisionaryAgent.md`)
- **Namespace Isolation**: Project prefixes prevent naming conflicts between projects
- **Auto-Discovery**: Claude Code automatically discovers agents in `.claude/agents/`

### Execution Commands

**Interactive Session (Claude Code style):**
```
./llmunix-llm interactive
```

**Execute with Interactive Mode:**
```
./llmunix-llm execute: "Create a Python calculator" -i
```

**Real Task Execution:**
```
Invoke the system-agent to execute the RealWorld_Research_Task scenario in EXECUTION MODE
```

**Training Data Generation:**
```  
Invoke the system-agent to simulate the research task scenario in SIMULATION MODE for training data
```

**Custom Real Task:**
```
Invoke the system-agent to execute: [your goal] using real tools
```

### Interactive Session Features

The interactive session provides a Claude Code-like experience:

**Available Commands:**
- `refine` - Refine and re-execute the last goal with improvements
- `status` - Show current workspace and execution status  
- `history` - Display execution history
- `clear` - Clear workspace for fresh start (with confirmation)
- `help` - Show available commands and examples
- `exit`/`quit` - Exit interactive session

**Goal Execution:**
Simply type any goal to execute it:
```
🎯 llmunix> Create a web scraper for news articles
🎯 llmunix> Build a REST API with FastAPI
🎯 llmunix> Analyze the data in my workspace
```

**Goal Refinement:**
After executing a goal, use `refine` to improve it:
```
🎯 llmunix> refine
Previous goal: Create a web scraper for news articles
How would you like to refine this goal?
🔄 refinement> Add error handling and save to JSON format
```

**Session Management:**
- Docker containers persist across multiple executions within a session
- Workspace state is maintained between commands
- Full execution history and context available throughout session
- Clean exit with proper resource cleanup

## Development

### Adding New Real Components:
1. Create component `.md` file in `components/` with Claude tool mapping
2. Register in `system/SmartLibrary.md` with [REAL] tag and metadata
3. Test execution and validate training data generation

### Extending Tool Mappings:
1. Add new mappings to `system/tools/ClaudeCodeToolMap.md`
2. Include cost, latency, and error mode specifications
3. Update component definitions to reference new tools

## Advanced Features

### Sentient State Management:
- **Modular State Architecture**: Specialized files in `workspace/state/` for focused updates
- **Behavioral Constraints**: `constraints.md` enables dynamic adaptation based on user sentiment and context
- **Memory-Driven Initialization**: Past experiences inform initial constraint settings
- **Real-time Adaptation**: Constraints evolve during execution based on user feedback and events
- **Atomic State Transitions**: Each component can be updated independently
- **Full Context Preservation**: Complete behavioral and execution context maintained
- **Resumable Execution**: Can pause and resume with full sentient state restoration

### Cost Optimization:
- Real-time cost tracking for all tool calls
- Intelligent tool selection based on cost/performance
- Budget management and cost reporting

### Intelligent Error Resilience:
- **Memory-Guided Recovery**: QueryMemoryTool leverages the memory-analysis-agent sub-agent for historical error recovery strategies
- **Sentiment-Aware Adaptation**: Error handling adapts based on user frustration levels
- **Constraint Evolution**: Failed attempts trigger behavioral modifications for future prevention
- **Real Error Learning**: Actual tool failures become training data for improved resilience
- **Adaptive Planning**: Execution strategy adjusts based on historical success patterns
- **Context-Aware Human Escalation**: Human-in-the-loop triggered based on confidence and constraint settings

### Training Pipeline:
- Automatic training data collection from real executions
- Structured datasets for fine-tuning autonomous agents
- Quality metrics and performance benchmarking

## Clean Restart

To reset LLM-OS:
1. Clear `workspace/` directory including `workspace/state/` (preserves execution artifacts)
2. Reset `system/memory_log.md` to empty state (clears learning history and behavioral patterns)
3. Archive any valuable execution traces and behavioral learning data for training
4. Ready for fresh scenario execution with clean sentient state

## File and Folder Permissions

If Claude Code lacks permissions to create folders and files, use these options:

### Running with Elevated Permissions

Use the `--dangerously-skip-permissions` flag when running Claude Code commands:
```bash
claude --dangerously-skip-permissions "your command here"
```
NOTE: Use this flag with caution as it bypasses permission prompts.

### Alternative Permission Modes

Start Claude Code with a specific permission mode:
```bash
claude --permission-mode plan "your command here"
```

### Windows-Specific Solutions

1. Run Command Prompt or PowerShell as administrator when using Claude Code
2. Check folder permissions in Windows Explorer:
   - Right-click on the project folder
   - Select Properties > Security
   - Ensure your user account has Write permissions
   - Apply changes

### Unix/Linux/Mac Solutions

1. Configure proper directory ownership:
```bash
sudo chown -R $USER:$USER /path/to/project/directory
```

2. Set appropriate permissions:
```bash
chmod -R 755 /path/to/project/directory
```

3. For npm-related permission issues, use:
```bash
mkdir -p ~/.npm-global
npm config set prefix ~/.npm-global
```
Add to your profile (e.g., ~/.profile, ~/.bash_profile):
```bash
export PATH=~/.npm-global/bin:$PATH
```
Then run `source ~/.profile` to apply changes.

## New Memory and Learning Features

### Intelligent Memory Consultation
- **QueryMemoryTool**: Standardized interface for memory-driven decision making through the memory-analysis-agent sub-agent
- **MemoryAnalysisAgent**: Advanced pattern recognition across historical executions (in system/agents/)
- **Behavioral Learning**: User sentiment patterns and constraint preferences captured
- **Adaptive Recommendations**: Memory provides actionable insights for current tasks

### Sentient State Architecture
- **Dynamic Constraints**: Behavioral modifiers that evolve based on context and feedback
- **User Sentiment Tracking**: Emotional state detection and adaptive response strategies
- **Priority Adaptation**: Execution focus adjusts based on user needs and historical patterns
- **Persona Switching**: Communication style adapts to optimize user experience
- **Error Tolerance Management**: Risk acceptance levels adjust based on task criticality and user preferences

### Advanced Execution Patterns
- **Memory-Informed Planning**: Historical success patterns guide component selection and strategy
- **Constraint-Aware Execution**: Every action considers current behavioral modifiers
- **Real-time Adaptation**: Behavioral constraints update during execution based on events
- **Sentiment-Driven Recovery**: Error handling strategies adapt to user emotional state
- **Learning Integration**: Every execution contributes to behavioral pattern database

## Theoretical Foundation: Continuum Memory System

**LLMunix implements a practical Continuum Memory System (CMS) inspired by cutting-edge research in Nested Learning.**

### Nested Learning Concepts

LLMunix's memory architecture maps directly to the theoretical framework from Google's "Nested Learning" research:

**Core Principles:**
- **Multi-Frequency Memory**: Different memory tiers update at different rates, like brain waves (gamma, beta, alpha)
- **Associative Memory**: Memory as key-value mapping (M: K→V) where keys are goal signatures and values are execution traces
- **Hierarchical Optimization**: Each memory tier has its own "context flow" and update frequency
- **Continual Learning**: System improves through experience without catastrophic forgetting

### CMS Implementation in LLMunix

| Memory Tier | Frequency | Update Rate | Purpose | Implementation |
|-------------|-----------|-------------|---------|----------------|
| **High-Frequency** | Gamma (30-100 Hz analogue) | Every execution | Immediate context, working memory | `workspace/state/` and `memory/short_term/` |
| **Mid-Frequency** | Beta (12-30 Hz analogue) | After successful runs | Validated patterns, execution traces | `memory/long_term/execution_trace_*.md` |
| **Low-Frequency** | Alpha (8-12 Hz analogue) | Periodic consolidation | Stable knowledge, best practices | `system/memory_log.md`, `project_learnings.md` |
| **Ultra-Low-Frequency** | Delta (0.5-4 Hz analogue) | Rare updates | Core patterns, system identity | `SmartLibrary.md`, user profiles |

### Memory Frequency Metadata

All memory files include frequency/volatility tags in YAML frontmatter:

```yaml
---
memory_frequency: high|mid|low|ultra-low
volatility: high|medium|low
update_trigger: execution|success|consolidation|manual
retention_policy: volatile|temporary|persistent|permanent
consolidation_threshold: 0.75  # Confidence needed to move to lower frequency
---
```

### Associative Memory: Goal→Trace Mapping

LLMunix implements associative memory through execution traces:

**Key (K)**: `goal_signature`
- Semantic embedding of user goal
- Task type classification
- Context fingerprint

**Value (V)**: `execution_trace`
- Deterministic tool call sequence
- Validation checks
- Error recovery strategies
- Performance metrics

**Learning Process**:
1. **Learner Mode**: Claude Sonnet 4.5 explores solution space, creates new trace
2. **Follower Mode**: Granite/Edge model executes proven trace deterministically
3. **Trace Evolution**: Success feedback increases confidence, failures trigger re-learning

### Memory Consolidation as "Systems Consolidation"

LLMunix's consolidation process mirrors biological memory:

**High→Mid Frequency (Short-Term→Long-Term)**:
- MemoryConsolidationAgent analyzes short-term logs
- Identifies successful patterns with confidence scores
- Creates execution traces when confidence ≥ 0.75
- Stores in `memory/long_term/`

**Mid→Low Frequency (Long-Term→Permanent)**:
- Traces used 20+ times with >95% success rate
- Patterns elevated to system-wide memory
- Added to SmartLibrary as reusable components
- Become part of LLMunix's "identity"

**Memory Flow Logic**:
```yaml
consolidation_rules:
  short_to_long_term:
    trigger: successful_execution
    confidence_threshold: 0.75
    output: execution_trace.md

  long_term_to_system:
    trigger: high_reuse (usage_count >= 20 AND success_rate >= 0.95)
    confidence_threshold: 0.95
    output: SmartLibrary.md entry

  system_to_core:
    trigger: cross_project_success
    confidence_threshold: 0.99
    output: Core agent/tool definition
```

### Deep Optimizers: Learnable Planning

SystemAgent's planning process is itself optimized through memory:

**Planning Metadata Logging**:
- Query strategy used (semantic vs. keyword)
- Components selected
- Constraints applied
- Outcome quality

**Meta-Learning**:
- MemoryAnalysisAgent analyzes planning decisions
- Identifies which planning strategies succeeded
- Recommends improved query strategies
- Guides future component selection

**Example**: If semantic similarity queries consistently outperform keyword searches for creative tasks, the system learns to prefer semantic queries for similar future tasks.

### Self-Modifying Architecture

LLMunix extends beyond creating new agents to modifying existing ones:

**Performance-Based Evolution**:
1. Track agent success rates in memory
2. Identify failure patterns (e.g., "WebFetchAgent fails on site X")
3. Automatically generate agent modifications
4. Update agent markdown with new error handling
5. Version control for agent evolution

**Example**:
```yaml
agent_modification_log:
  agent: web-fetch-agent
  version: 1.0 → 1.1
  trigger: repeated_failures (site: news.ycombinator.com)
  modification: Added rate limiting and retry logic
  confidence_improvement: 0.65 → 0.92
```

### Theoretical Advantages

**Why This Matters**:

1. **Rigorous Foundation**: Grounded in cutting-edge ML research (Nested Learning, CMS)
2. **Practical Implementation**: Theory manifests as file-based, human-readable system
3. **Continual Learning**: No catastrophic forgetting—old knowledge preserved in low-frequency tiers
4. **Explainability**: Every learning decision is auditable through markdown logs
5. **Scalability**: Frequency-based pruning prevents memory bloat
6. **Adaptability**: System improves automatically without manual tuning

**Comparison to Traditional LLMs**:
- ❌ Traditional: Context window only, no persistent learning
- ✅ LLMunix: Multi-tier memory with continual learning and adaptation

**Comparison to RAG Systems**:
- ❌ RAG: Flat memory retrieval, no hierarchy or consolidation
- ✅ LLMunix: Hierarchical CMS with frequency-aware consolidation and trace evolution

## Mobile App Generation (Optional Output Format)

**IMPORTANT: LLMunix's core identity is a CLI-based agent/tool creation OS. Mobile app generation is an OPTIONAL output format, not the primary goal.**

### Core Philosophy

- **Primary Output**: CLI results in `projects/{ProjectName}/output/` (reports, analysis, data files)
- **Optional Output**: Mobile app in `projects/{ProjectName}/mobile_app/` (React Native codebase)
- **Trigger**: User explicitly requests mobile app with keywords like "mobile app", "generate app", etc.

### Mobile App Generation Workflow

When user goal includes mobile app keywords, SystemAgent executes this workflow **AFTER** primary CLI execution:

```
User Request: "Create a mobile app for habit tracking"
    ↓
1. SystemAgent detects "mobile app" keyword
    ↓
2. SystemAgent executes primary workflow
   - Analyze habit tracking requirements
   - Design data model and features
   - Generate CLI outputs in output/
    ↓
3. SystemAgent invokes CodeGeneratorAgent
   - Reads project output/ files
   - Generates complete React Native codebase
   - Uses Claude Sonnet 4.5 for high-quality code
    ↓
4. CodeGeneratorAgent invokes MobileAppAnalyzer
   - Analyzes app requirements
   - Classifies as agentic (LLM needed) or deterministic (code-only)
   - Recommends model: Qwen3-0.6B, Granite 4.0 H-1B, or none
    ↓
5. CodeGeneratorAgent invokes MobileAppBuilder
   - Creates deployment package
   - Bundles LLM model (if agentic)
   - Generates manifest, package.json, README.md
    ↓
6. Output: Complete mobile app in mobile_app/
   - Deterministic: 5-20MB (code only)
   - Agentic: 600MB-1.5GB (code + LLM)
```

### App Classification: Agentic vs Deterministic

**Deterministic Apps (90% of cases) - No LLM Required:**
- Rule-based logic (if-then, calculations, CRUD)
- Data visualization and charts
- No natural language understanding needed
- Examples: Habit tracker, calculator, news reader, to-do list
- **Size**: 5-20MB (code + assets only)
- **Performance**: Instant responses, no LLM latency

**Agentic Apps (10% of cases) - LLM Required:**
- Natural language understanding/generation
- Adaptive behavior based on user patterns
- Content creation (text, code, recommendations)
- Examples: Personal trainer, study assistant, code helper
- **Size**: 600MB-1.5GB (code + on-device LLM)
- **Performance**: 1-2s latency for AI features

### Model Selection (For Agentic Apps)

Based on comprehensive research (see `projects/Project_on_device_wabi_analysis/output/granite_qwen_comparison.md`):

**Qwen3-0.6B-INT4 (Primary Choice):**
- **Use When**: General agentic apps, conversational AI, multilingual support
- **Size**: 600MB
- **Quality**: 52.81 MMLU
- **Speed**: 50-150 tokens/sec (CPU), 200-500 tokens/sec (NPU)
- **Strengths**: Proven ecosystem, 100+ languages, balanced quality/size
- **License**: Apache 2.0

**Granite 4.0 H-1B-INT4 (Alternative):**
- **Use When**: Code generation, structured output, instruction following
- **Size**: 1.5GB
- **Quality**: 73.0 HumanEval, 82.37 IFEval
- **Speed**: 30-80 tokens/sec (CPU), 100-300 tokens/sec (NPU)
- **Strengths**: Superior code generation, instruction following
- **License**: Apache 2.0

**None (Deterministic):**
- **Use When**: 90% of apps (rule-based logic, no AI needed)
- **Size**: 0MB (code only)
- **Speed**: Instant

### Example Commands

**CLI-Only (Default Behavior):**
```bash
llmunix execute: "Analyze trends in AI research papers from 2024"
# Output: projects/Project_ai_trends/output/analysis.md (CLI only)
```

**Mobile App Generation:**
```bash
llmunix execute: "Create a mobile app for tracking daily habits"
# Output:
#   - projects/Project_habit_tracker/output/requirements.md (CLI)
#   - projects/Project_habit_tracker/mobile_app/ (React Native app, 15MB)
```

**Agentic Mobile App:**
```bash
llmunix execute: "Build a mobile personal trainer app that adapts workouts to my progress"
# Output:
#   - projects/Project_personal_trainer/output/design.md (CLI)
#   - projects/Project_personal_trainer/mobile_app/ (React Native app + Qwen3-0.6B, 635MB)
```

### Example Usage

Generate a complete project with one command:
```bash
claude --dangerously-skip-permissions "llmunix execute: 'Create a mobile app for tracking daily habits'"
```

This creates:
1. Primary CLI workflow (requirements analysis, data model, features) in `output/`
2. Mobile app generation from CLI outputs in `mobile_app/`
3. Automatic classification (deterministic or agentic)
4. Complete React Native deployment package

### Key Components

**System Agents:**
- **SystemAgent**: Detects mobile keywords, orchestrates workflow
- **CodeGeneratorAgent**: Generates React Native code from project outputs

**System Tools:**
- **MobileAppAnalyzer**: Classifies apps as agentic vs deterministic
- **MobileAppBuilder**: Bundles deployment package with optional LLM

See `system/SmartLibrary.md` for complete component registry.

### Integration with LLMunix Philosophy

**Preserves Core Identity:**
- ✅ Mobile generation is OPTIONAL, not default
- ✅ CLI results remain primary output
- ✅ Agent/tool creation on-demand still core capability
- ✅ Memory and learning still drive improvements
- ✅ Project-based organization maintained
- ✅ Pure markdown framework (agents/tools as markdown specs)

**Enhances Capabilities:**
- ✅ Projects can now output to edge devices (mobile)
- ✅ Dual-mode learning applies (cloud generates, edge runs)
- ✅ On-device LLMs extend LLMunix to mobile runtime
- ✅ Hybrid cloud-edge architecture enabled
- ✅ 90% deterministic optimization (small apps)

### Research and Analysis

Comprehensive research documents available in:
- `projects/Project_on_device_wabi_analysis/output/granite_qwen_comparison.md` - Model selection (950 lines)
- `projects/Project_on_device_wabi_analysis/output/CODE_GENERATION_ARCHITECTURE.md` - Architecture design
- `projects/Project_on_device_wabi_analysis/output/EXECUTIVE_SUMMARY.md` - Complete analysis summary
