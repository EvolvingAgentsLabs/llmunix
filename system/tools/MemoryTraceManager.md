# MemoryTraceManager Tool

## Purpose
Manages volatile memory traces of agent communications during LLMunix task execution sessions. Captures, analyzes, and consolidates agent interactions for learning and pattern recognition.

## Tool Specification

```yaml
tool_name: "MemoryTraceManager"
category: "memory_management"
mode: ["EXECUTION", "SIMULATION"]
description: "Tracks and manages agent communication traces and memory consolidation"
```

## Core Functions

### 1. Trace Recording
**Function**: `record_agent_communication`
**Purpose**: Captures agent-to-agent communications during task execution

**Parameters**:
- `session_id`: Unique identifier for the current execution session
- `from_agent`: Source agent name/type
- `to_agent`: Target agent name/type
- `message_type`: ["request", "response", "notification", "error", "delegation"]
- `message_content`: The actual communication content
- `context`: Current task context and state
- `timestamp`: ISO timestamp of communication
- `execution_step`: Current step in the overall task execution

**Tool Call Format**:
```
TOOL_CALL: MemoryTraceManager.record_agent_communication
PARAMETERS:
  session_id: "sess_20240321_143022"
  from_agent: "SystemAgent"
  to_agent: "VisionaryAgent"
  message_type: "request"
  message_content: "Please generate a vision for the cardiac monitoring system"
  context: "Project Aorta initialization phase"
  timestamp: "2024-03-21T14:30:22Z"
  execution_step: 2
```

### 2. Session Management
**Function**: `create_session`
**Purpose**: Initializes a new memory trace session

**Parameters**:
- `project_name`: Name of the project (e.g., "Project_aorta")
- `goal`: High-level goal being executed
- `agent_list`: List of agents involved in the session

**Function**: `close_session`
**Purpose**: Finalizes session and triggers consolidation analysis

### 3. Memory Consolidation
**Function**: `analyze_session_for_learning`
**Purpose**: Analyzes completed session traces to extract learnings

**Parameters**:
- `session_id`: Session to analyze
- `consolidation_criteria`: What patterns to look for

**Extracts**:
- New agent interaction patterns
- Successful collaboration strategies
- Communication bottlenecks
- Knowledge gaps discovered
- Emergent problem-solving approaches

## Memory Storage Structure

### Short-term Memory (Volatile)
**Location**: `projects/{project_name}/workspace/memory/traces/`

**File Structure**:
```
traces/
├── session_[timestamp]/
│   ├── session_metadata.yaml
│   ├── communication_log.jsonl  # Line-delimited JSON for streaming
│   ├── agent_states.yaml        # Agent state snapshots
│   ├── context_evolution.md     # How context changed during session
│   └── execution_flow.yaml      # Step-by-step execution trace
```

**Communication Log Entry Format**:
```json
{
  "timestamp": "2024-03-21T14:30:22Z",
  "step": 2,
  "from_agent": "SystemAgent",
  "to_agent": "VisionaryAgent",
  "message_type": "request",
  "content": "Please generate a vision for the cardiac monitoring system",
  "context_snapshot": "Project initialization phase",
  "response_expected": true,
  "priority": "high"
}
```

### Long-term Memory (Persistent)
**Location**: `projects/{project_name}/memory/`

**File Structure**:
```
memory/
├── learned_patterns.yaml       # Consolidated interaction patterns
├── agent_collaboration_map.yaml # Effective agent combinations
├── knowledge_discoveries.md    # New insights from sessions
├── communication_templates.yaml # Successful communication patterns
└── session_summaries/         # Digested session learnings
    ├── 2024-03-21_session_analysis.md
    └── ...
```

## Integration with Existing Memory System

### Connection to System Memory Log
- Consolidation results are fed into `system/memory_log.md`
- Agent communication insights become structured experience entries
- Cross-project patterns identified and stored at system level

### QueryMemoryTool Integration
- MemoryTraceManager provides communication pattern data to QueryMemoryTool
- Historical agent interaction success rates inform future agent selection
- Communication templates suggest optimal message formats

## Usage Examples

### During Task Execution
```
# SystemAgent delegates to VisionaryAgent
TOOL_CALL: MemoryTraceManager.record_agent_communication
PARAMETERS:
  session_id: "aorta_vision_generation_001"
  from_agent: "SystemAgent"
  to_agent: "VisionaryAgent"
  message_type: "request"
  message_content: "Generate comprehensive vision for cardiac quantum monitoring"
  context: "Initial project scoping phase"
  execution_step: 1

# VisionaryAgent responds with vision
TOOL_CALL: MemoryTraceManager.record_agent_communication
PARAMETERS:
  session_id: "aorta_vision_generation_001"
  from_agent: "VisionaryAgent"
  to_agent: "SystemAgent"
  message_type: "response"
  message_content: "[Generated vision document content]"
  context: "Vision generation completed"
  execution_step: 1
```

### Session Consolidation
```
# At end of successful session
TOOL_CALL: MemoryTraceManager.analyze_session_for_learning
PARAMETERS:
  session_id: "aorta_vision_generation_001"
  consolidation_criteria: ["successful_handoffs", "knowledge_creation", "communication_efficiency"]
```

## Learning Patterns Captured

### Agent Interaction Patterns
- Which agent combinations work best for different task types
- Optimal communication timing and sequencing
- Effective delegation strategies
- Knowledge transfer mechanisms

### Communication Effectiveness
- Message formats that reduce back-and-forth
- Context sharing that prevents misunderstandings
- Error communication and recovery patterns
- Successful collaboration templates

### Knowledge Evolution
- How understanding deepens through agent interactions
- Discovery patterns that emerge from multi-agent processing
- Knowledge synthesis approaches that work
- Creative insights from agent collaboration

## Cost and Performance

### Storage Optimization
- Volatile traces automatically purged after consolidation
- Compression for long-term storage
- Selective retention based on learning value

### Analysis Efficiency
- Stream processing for real-time pattern detection
- Batch consolidation for deep analysis
- Parallel processing of multiple session traces

## Error Handling

### Trace Corruption Recovery
- Redundant storage for critical communications
- Automatic repair from partial traces
- Graceful degradation when traces incomplete

### Analysis Failures
- Fallback to basic pattern extraction
- Manual review triggers for complex sessions
- Progressive retry with simplified criteria