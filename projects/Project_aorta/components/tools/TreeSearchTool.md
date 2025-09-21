---
name: tree-search-tool
description: Implements tree-based exploration of solution spaces with systematic evaluation and optimization.
tools: Read, Write, Task
---
# Tree Search Tool

## Purpose
The TreeSearchTool enables structured exploration of solution spaces using tree-based search algorithms. It systematically evaluates different approaches, tracks performance metrics, and prioritizes promising paths.

## Core Capabilities
- **Tree Construction**: Build exploration trees with nodes representing approaches
- **Node Evaluation**: Score nodes based on performance metrics
- **Search Algorithms**: Implement various tree search strategies
- **Path Optimization**: Identify and prioritize promising solution paths

## Tree Structure
```yaml
tree_id: string
root_node: node_id
nodes:
  node_id:
    parent_id: string | null
    children: [list of node IDs]
    content: string
    metadata:
      score: number
      evaluated: boolean
      execution_time: number
      resource_usage: number
      status: "pending" | "in_progress" | "completed" | "failed"
```

## Search Algorithms
1. **Best-First Search**: Prioritize nodes with highest scores
2. **Breadth-First Search**: Explore all nodes at current depth
3. **Depth-First Search**: Follow single path to completion
4. **Monte Carlo Tree Search**: Use sampling to estimate node values

## Implementation Pattern
```markdown
Action: Initialize tree with root node
Observation: [Tree created]

Action: Expand promising nodes using selected algorithm
Observation: [New nodes created]

Action: Evaluate node performance
Observation: [Node scores updated]

Action: Select next nodes for expansion
Observation: [Priority nodes identified]

Action: Execute selected nodes
Observation: [Node results recorded]

Action: Update tree state in workspace/state/trees/{tree_id}.md
Observation: [Tree state updated]
```

## Inspired by Sakana AI Scientist-v2
This tool is directly inspired by the Sakana AI Scientist-v2's tree search approach and implements:

1. **Best-First Tree Search (BFTS)**: Systematically explores solution paths based on performance metrics
2. **Node Evaluation**: Comprehensive scoring of execution results
3. **Performance Tracking**: Detailed metadata on execution performance
4. **Multi-path Exploration**: Concurrent investigation of multiple approaches

## Integration with LLMunix

### Pure Markdown Implementation
The TreeSearchTool maintains LLMunix's pure markdown philosophy by:
1. Representing trees as structured markdown documents
2. Storing nodes with YAML frontmatter for metadata
3. Using markdown links to establish node relationships
4. Implementing algorithms through markdown-defined patterns

### System Integration
The tool integrates with LLMunix through:
1. **State Management**: Trees stored in workspace/state/trees/
2. **Agent Collaboration**: Specialized agents evaluate nodes
3. **Memory System**: Successful patterns stored in memory
4. **Execution Flow**: SystemAgent orchestrates tree exploration

## Specialized Use Cases

### Solution Exploration
```markdown
Action: Create solution tree for problem X
Observation: [Tree initialized with problem statement]

Action: Generate candidate approaches
Observation: [First-level child nodes created]

Action: Evaluate initial approaches
Observation: [Nodes scored based on analysis]

Action: Expand most promising approaches
Observation: [Second-level nodes created]

Action: Execute and evaluate expanded approaches
Observation: [Performance data collected]

Action: Select optimal solution path
Observation: [Best-performing path identified]
```

### Parallel Evaluation
The TreeSearchTool supports parallel evaluation by:
1. Identifying independent nodes for concurrent execution
2. Delegating evaluation to specialized agents
3. Aggregating results from parallel evaluations
4. Updating tree state with consolidated findings

### Adaptive Exploration
The tool implements adaptive exploration by:
1. Dynamically adjusting node expansion based on performance
2. Pruning unpromising branches early
3. Allocating more resources to high-potential paths
4. Learning from exploration patterns across multiple trees