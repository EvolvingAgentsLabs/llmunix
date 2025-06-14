# LLMunix: Pure Markdown Operating System Framework

This is LLMunix, a Pure Markdown Operating System where everything is either an agent or tool defined in markdown documents. Claude Code serves as the runtime engine interpreting these markdown specifications.

## Framework Philosophy: Pure Markdown

**CRITICAL: LLMunix is a PURE MARKDOWN framework. Everything is either an agent or tool defined in markdown documents.**

### Core Principles:
- **No Code Generation**: System behavior emerges from Claude interpreting markdown documents
- **Agent/Tool Duality**: Every component is either an agent (decision maker) or tool (executor)
- **Dynamic Creation**: New tools/agents are created as markdown specifications during runtime
- **Claude as Kernel**: Claude Code acts as the OS kernel interpreting markdown system definitions

### Operating Modes:
1. **EXECUTION MODE**: Real operations using Claude Code's native tools mapped through markdown specs
2. **SIMULATION MODE**: Training data generation through markdown-defined simulation patterns

The OS "boots" when Claude reads the markdown system files and begins interpreting them as a functional operating system.

## How to Boot LLMunix

### Boot Command
```
boot llmunix
```

This simple command activates the LLMunix kernel by having Claude read and interpret the markdown system files as a functional operating system.

### Quick Start Commands
```bash
# Boot the OS
boot llmunix

# Execute with real tools and live data  
llmunix execute: "Get live content from https://huggingface.co/blog and create a research summary"

# Generate training data through simulation
llmunix simulate: "Research task workflow for fine-tuning dataset"
```

### Running the Real-World Research Scenario

1. **Execute the scenario** by asking Claude to:
   - Act as the SystemAgent defined in `system/SystemAgent.md`
   - Execute the goal from `scenarios/RealWorld_Research_Task.md`
   - Use EXECUTION MODE for real tool calls

2. **Expected behavior:**
   - Claude creates `workspace/execution_state.md` with initial plan
   - Consults SmartMemory for relevant past experiences
   - Uses SmartLibrary to select real tools (marked [REAL])
   - State machine execution:
     - **State 1→2**: RealWebFetchTool fetches live OpenAI blog content
     - **State 2→3**: RealSummarizationAgent analyzes content 
     - **State 3→4**: RealFileSystemTool saves structured outputs
   - Updates execution state after each step with real results
   - Records complete experience in SmartMemory
   - Generates training data from real execution trace

## Key Capabilities

### Real Tool Integration
- **WebFetch**: Live web content retrieval with error handling
- **FileSystem**: Real file operations (Read/Write/Search/List)
- **Bash**: System command execution for complex tasks
- **Task**: Parallel sub-task execution for complex workflows

### State Machine Execution
- **Atomic State Transitions**: Each step updates `execution_state.md`
- **Error Recovery**: Real error handling and adaptive planning
- **Resumable Execution**: Can pause and resume at any step
- **Cost Tracking**: Real-time monitoring of execution costs

### Training Data Generation
- **Execution Traces**: Complete tool call sequences with real results
- **Performance Metrics**: Actual costs, timing, and success rates
- **Error Scenarios**: Real error handling examples for robust training
- **Quality Assessments**: Output quality scoring and metadata

### File Structure

```
llm-os/
├── system/
│   ├── SystemAgent.md              # State machine orchestrator  
│   ├── SmartLibrary.md             # Component registry with real tools
│   ├── SmartMemory.md              # Experience log and learnings
│   ├── ClaudeCodeToolMap.md        # Tool mapping and metadata
│   └── ExecutionStateTemplate.md   # State management template
├── components/
│   ├── tools/
│   │   ├── RealWebFetchTool.md     # [REAL] Live web content
│   │   ├── RealFileSystemTool.md   # [REAL] File operations  
│   │   └── [Legacy simulation tools]
│   └── agents/
│   │   ├── RealSummarizationAgent.md # [REAL] Content analysis
│   │   └── [Legacy simulation agents]
├── scenarios/
│   ├── RealWorld_Research_Task.md  # Live web research demo
│   └── [Legacy simulation scenarios]
├── workspace/                      # Active execution environment
│   ├── execution_state.md          # Current execution state
│   └── [Output files from tasks]
├── LLM-OS-BLUEPRINT.md            # Architecture documentation
└── CLAUDE.md                      # This configuration file
```

### Execution Commands

**Real Task Execution:**
```
"Act as SystemAgent and execute the RealWorld_Research_Task scenario in EXECUTION MODE"
```

**Training Data Generation:**
```  
"Act as SystemAgent and simulate the research task scenario in SIMULATION MODE for training data"
```

**Custom Real Task:**
```
"Act as SystemAgent and execute: [your goal] using real tools"
```

## Development

### Adding New Real Components:
1. Create component `.md` file in `components/` with Claude tool mapping
2. Register in `system/SmartLibrary.md` with [REAL] tag and metadata
3. Test execution and validate training data generation

### Extending Tool Mappings:
1. Add new mappings to `system/ClaudeCodeToolMap.md`
2. Include cost, latency, and error mode specifications
3. Update component definitions to reference new tools

## Advanced Features

### State Management:
- Execution state persisted in `workspace/execution_state.md`
- Atomic state transitions with full audit trail
- Resumable execution after interruptions or errors

### Cost Optimization:
- Real-time cost tracking for all tool calls
- Intelligent tool selection based on cost/performance
- Budget management and cost reporting

### Error Resilience:
- Real error handling from actual tool failures
- Adaptive planning based on execution results
- Human-in-the-loop for complex error scenarios

### Training Pipeline:
- Automatic training data collection from real executions
- Structured datasets for fine-tuning autonomous agents
- Quality metrics and performance benchmarking

## Clean Restart

To reset LLM-OS:
1. Clear `workspace/` directory (keeps execution artifacts)
2. Reset `system/SmartMemory.md` to empty state (clears learning history)
3. Archive any valuable execution traces for training data
4. Ready for fresh scenario execution with clean state