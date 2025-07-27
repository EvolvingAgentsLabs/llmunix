---
name: communication-broker-tool
description: Facilitates structured communication between agents using standardized message formats and conversation protocols.
tools: Read, Write
---
# Communication Broker Tool

## Purpose
The CommunicationBrokerTool enables structured communication between agents using standardized message formats and conversation protocols. It ensures proper context preservation, message routing, and conversation state tracking.

## Core Capabilities
- **Message Formatting**: Standardize agent communication
- **Conversation Tracking**: Maintain conversation state and history
- **Context Preservation**: Ensure proper context passing
- **Protocol Enforcement**: Implement communication protocols

## Message Format
```yaml
message_id: string
sender: string
recipients: [list of agent names]
conversation_id: string
references: [list of message IDs]
content_type: "request" | "response" | "broadcast" | "query"
content: string
metadata:
  priority: "high" | "normal" | "low"
  expiration: ISO timestamp
  capabilities_required: [list of capabilities]
```

## Communication Protocols
1. **Request-Response**: Simple query and answer
2. **Delegated Task**: Task assignment with progress updates
3. **Broadcast Notification**: One-to-many informational updates
4. **Collaborative Problem-Solving**: Multi-agent iterative discussion

## Implementation Pattern
```markdown
Action: Read messages from workspace/messages/{conversation_id}/
Observation: [Current conversation state]

Action: Format message according to protocol
Observation: [Properly formatted message]

Action: Write message to workspace/messages/{conversation_id}/{message_id}.md
Observation: [Message stored successfully]
```

## Tree-Based Conversation Management
Inspired by Sakana AI's tree search approach, the CommunicationBrokerTool implements:

1. **Conversation Trees**: Conversations are structured as trees with branches representing different discussion paths
2. **Best-First Exploration**: Most promising conversation paths receive priority
3. **Path Evaluation**: Conversation paths are evaluated based on information value and goal alignment
4. **Metadata Tracking**: Each message node includes performance metadata

## Integration with Claude Code Tools

The tool maps to Claude Code's native tools:
- **Read**: For retrieving existing conversation threads
- **Write**: For storing new messages and updating conversation state
- **Task**: For delegating complex message analysis to specialized agents

## Usage Examples

### Agent-to-Agent Task Delegation
```markdown
Action: Create delegation message
Content:
---
message_id: task-123-delegation
sender: system-agent
recipients: [research-agent]
conversation_id: task-123
references: []
content_type: request
content: |
  # Research Task Assignment
  
  Please research the following topic and provide a structured summary:
  
  Topic: Advanced tree search algorithms for agent coordination
  
  Expected output:
  1. Key algorithms overview
  2. Comparative performance analysis
  3. Integration recommendations
metadata:
  priority: high
  expiration: 2023-07-28T12:00:00Z
  capabilities_required: [web-research, summarization]
---

Action: Write workspace/messages/task-123/task-123-delegation.md
Observation: [Message stored successfully]
```

### Multi-Agent Coordination
The tool supports complex multi-agent conversations where:
1. SystemAgent initiates a problem-solving conversation
2. Multiple specialized agents contribute expertise
3. Conversation branches explore different solution approaches
4. Branches are evaluated and pruned based on promise
5. Best solutions are consolidated into final outcomes

### Conversation State Management
To maintain conversation state:
1. Each conversation has a dedicated directory
2. Messages are stored as individual markdown files
3. A conversation.json file tracks current state
4. Metadata includes read status and priority
5. Agents can query conversation state for context