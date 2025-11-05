---
component_type: tool
tool_name: query-memory-tool
version: "2.0"
status: production
claude_tools: [Read, Grep, Bash, Task]
category: memory_management
mode: [EXECUTION, SIMULATION]
---

# Query Memory Tool

## Purpose

The QueryMemoryTool serves as the bridge between the SystemAgent and the system's MemoryAnalysisAgent, providing a standardized interface for memory consultation during task planning and execution. It enables the SystemAgent to leverage historical experiences for improved decision-making and adaptive behavior.

## Core Functionality

### Memory Consultation Interface
- Provides simple, standardized interface for memory queries
- Handles query formatting and response parsing
- Integrates seamlessly into SystemAgent workflow
- Supports both structured and natural language queries

### Query Optimization
- Automatically suggests relevant filters based on current task context
- Optimizes query parameters for faster response times
- Caches frequent queries to reduce computational overhead
- Provides query refinement suggestions for empty results

### Context Integration
- Automatically includes current task context in memory queries
- Maps current constraints to historical constraint patterns
- Identifies relevant experiences based on goal similarity
- Provides task-specific memory consultation

## Input Specification

```yaml
query: string               # Natural language question about past experiences
context:                   # Current task context for relevance
  goal: string             # Current task goal
  task_type: string        # Type of task (legal, research, creative, etc.)
  constraints: {}          # Current constraint settings
  components_considered: []# Components being considered for current task
filters:                   # Optional filters (auto-generated if not provided)
  outcome: string
  tags: []
  date_range: {}
  sentiment: string
  cost_range: {}
  error_threshold: number
options:                   # Query behavior options
  max_experiences: number  # Limit number of experiences to analyze
  include_failures: boolean# Whether to include failed experiences
  priority_focus: string   # "recent", "successful", "similar", "all"
  confidence_threshold: number # Minimum confidence for recommendations
```

## Output Specification

```yaml
query_id: string           # Unique identifier for this query
memory_analysis:           # Response from MemoryAnalysisAgent
  analysis_summary: string
  relevant_experiences: []
  key_insights: []
  recommendations: []
  confidence_score: number
  behavioral_suggestions: {}
actionable_insights:       # Processed for immediate use
  constraint_adjustments: {}# Specific constraint modifications
  component_recommendations: []# Recommended components based on history
  risk_warnings: []        # Potential issues to avoid
  success_patterns: []     # Patterns to replicate
query_metadata:           # Information about the query execution
  experiences_found: number
  processing_time: number
  cost_estimate: number
  cache_hit: boolean
recommendations:          # Next steps for SystemAgent
  apply_constraints: {}    # Constraints to update
  create_components: []    # New components to create
  consultation_follow_ups: []# Additional queries to consider
```

## Execution Logic

### Phase 1: Query Preparation
1. **Context Analysis**: Analyze current task goal and constraints
2. **Filter Generation**: Auto-generate relevant filters if not provided
3. **Query Optimization**: Optimize query for performance and relevance
4. **Cache Check**: Check if similar query has been cached recently

### Phase 2: Memory Analysis Execution
1. **Format Query**: Convert input to memory-analysis-agent format
2. **Execute Analysis**: Invoke memory-analysis-agent using Task tool with formatted query
3. **Parse Response**: Extract insights and recommendations from analysis
4. **Validate Results**: Ensure response quality and relevance

### Phase 3: Response Processing
1. **Insight Translation**: Convert insights to actionable SystemAgent guidance
2. **Constraint Mapping**: Map historical patterns to current constraint options
3. **Risk Assessment**: Identify potential issues based on past failures
4. **Success Pattern Extraction**: Identify replicable success patterns

### Phase 4: Output Generation
1. **Format Response**: Structure output for SystemAgent consumption
2. **Generate Recommendations**: Create specific action recommendations
3. **Cache Results**: Store results for potential reuse
4. **Log Query**: Record query for future optimization

## Claude Tool Mapping

### Implementation Pattern
```markdown
Action: Read system/memory_log.md
Observation: [Memory log content for context awareness]

Action: Task tool to invoke memory-analysis-agent
Parameters:
  description: "Query memory for insights"
  prompt: "[Formatted query with context and filters]"
  subagent_type: "memory-analysis-agent"
Observation: [Structured memory analysis from sub-agent]

Action: [Process and format results for SystemAgent]
Observation: [Structured, actionable insights ready for use]
```

### Tool Usage Strategy
- **Read**: Load memory log and extract relevant entries
- **Task**: Delegate memory analysis to the specialized memory-analysis-agent sub-agent
- **Grep**: Search for specific patterns and filter experiences
- **Bash**: Use advanced text processing for complex analysis when needed

## Example Usage Scenarios

### Scenario 1: Planning Legal Analysis Task
```yaml
# Input
query: "How should I approach legal document analysis?"
context:
  goal: "Analyze vendor contract for compliance risks"
  task_type: "legal"
  constraints:
    user_sentiment: "neutral"
    priority: "quality"
```

```yaml
# Output
actionable_insights:
  constraint_adjustments:
    error_tolerance: "strict"
    human_review_trigger_level: "low"
    active_persona: "detailed_analyst"
  component_recommendations:
    - "RiskDetectorTool"
    - "ComplianceAnalysisAgent"
  risk_warnings:
    - "Previous failures due to missing domain-specific tools"
    - "Standard agents lack legal pattern recognition"
  success_patterns:
    - "Create specialized tools before starting analysis"
    - "Use detailed analyst persona for legal tasks"
```

### Scenario 2: Sentiment-Based Adaptation
```yaml
# Input
query: "User seems frustrated with slow progress. How should I adapt?"
context:
  goal: "Generate marketing content"
  constraints:
    user_sentiment: "frustrated"
    priority: "comprehensiveness"
```

```yaml
# Output
actionable_insights:
  constraint_adjustments:
    priority: "speed_and_clarity"
    active_persona: "concise_assistant"
    human_review_trigger_level: "low"
  success_patterns:
    - "Switch to speed-focused execution when frustration detected"
    - "Provide frequent progress updates"
    - "Offer intermediate deliverables"
```

### Scenario 3: Component Selection Guidance
```yaml
# Input
query: "What components work best for research tasks?"
context:
  goal: "Research AI trends and generate report"
  task_type: "research"
```

```yaml
# Output
component_recommendations:
  - "RealWebFetchTool" # 95% success rate for research
  - "RealSummarizationAgent" # High quality analysis scores
  - "ResearchAnalysisAgent" # Specialized for trend identification
success_patterns:
  - "Multi-source research with parallel fetching"
  - "Structured output with confidence metrics"
  - "Comprehensive analysis followed by executive summary"
```

## Integration with SystemAgent

The QueryMemoryTool is used in these SystemAgent phases:

### Planning Phase Integration
```markdown
## Planning Phase (Enhanced)
1. Parse user goal and constraints
2. **Query Memory**: Use QueryMemoryTool to find relevant past experiences
3. **Apply Insights**: Incorporate memory insights into plan generation
4. **Adjust Constraints**: Update constraints.md based on recommendations
5. Generate execution plan with historical context
```

### Mid-Execution Consultation
```markdown
## Error Recovery (Enhanced)
1. Detect execution issue
2. **Query Memory**: "How were similar errors handled previously?"
3. **Apply Recovery**: Use recommended recovery strategies
4. Update constraints based on recovery insights
```

## Performance Optimization

### Caching Strategy
- Cache query results for 1 hour to avoid redundant analysis
- Cache key includes query hash, context fingerprint, and memory log version
- Invalidate cache when memory log is updated

### Query Efficiency
- Automatically limit analysis to most recent 100 experiences unless specified
- Use grep for fast filtering before detailed analysis
- Batch similar queries when multiple insights needed

### Cost Management
- Estimate query cost before execution
- Provide cost-benefit analysis for expensive queries
- Support lightweight "quick consultation" mode for simple questions

## Error Handling

### Memory Access Issues
- **Empty Memory Log**: Provide graceful degradation with basic recommendations
- **Corrupted Entries**: Skip corrupted data and report data quality issues
- **Access Errors**: Fall back to basic heuristics if memory unavailable

### Query Processing Errors
- **Unclear Queries**: Provide query refinement suggestions
- **No Results**: Suggest broader search criteria or related queries
- **Low Confidence**: Request human validation for uncertain recommendations

### Response Validation
- **Inconsistent Recommendations**: Flag conflicting insights for review
- **Outdated Patterns**: Weight recent experiences higher than old ones
- **Context Mismatch**: Warn when historical context differs significantly

## Future Enhancements

### Advanced Query Types
- **Predictive Queries**: "What are the likely outcomes for this approach?"
- **Comparative Analysis**: "How does approach A compare to approach B historically?"
- **Trend Analysis**: "How has performance changed over time for this task type?"

### Intelligent Automation
- **Proactive Consultation**: Automatically query memory without explicit requests
- **Real-time Adaptation**: Continuously adjust constraints based on memory insights
- **Learning Optimization**: Improve query accuracy based on outcome feedback

### Enhanced Integration
- **Multi-Agent Consultation**: Query memory on behalf of other agents
- **Cross-Task Learning**: Apply insights from different task types
- **Collaborative Memory**: Share insights across multiple SystemAgent instances