---
component_type: schema
schema_name: continuum-memory-schema
version: "1.0"
status: production
category: memory_management
mode: [EXECUTION, SIMULATION]
---

# Continuum Memory System Schema

## Purpose

Defines the standardized metadata schema for all memory files in LLMunix's Continuum Memory System (CMS). This schema enables frequency-aware consolidation, intelligent querying, and adaptive memory management based on Nested Learning principles.

## Memory Frequency Tiers

| Tier | Frequency | Hz Analogue | Update Rate | Retention | Location |
|------|-----------|-------------|-------------|-----------|----------|
| **High** | Gamma | 30-100 Hz | Every execution | Volatile | `workspace/state/`, `memory/short_term/` |
| **Mid** | Beta | 12-30 Hz | After success | Temporary | `memory/long_term/execution_trace_*.md` |
| **Low** | Alpha | 8-12 Hz | Periodic | Persistent | `system/memory_log.md`, `project_learnings.md` |
| **Ultra-Low** | Delta | 0.5-4 Hz | Rare | Permanent | `SmartLibrary.md`, user profiles |

## Standard YAML Frontmatter

### Required Fields

All memory files MUST include these fields in YAML frontmatter:

```yaml
---
memory_frequency: high|mid|low|ultra-low
volatility: high|medium|low
update_trigger: execution|success|consolidation|manual
retention_policy: volatile|temporary|persistent|permanent
confidence_score: 0.0-1.0  # How confident we are in this memory
---
```

### Optional Fields (Recommended)

```yaml
---
# ... required fields above ...

# Consolidation metadata
consolidation_threshold: 0.75  # Confidence needed to move to lower frequency
usage_count: 0  # How many times this memory has been accessed
success_rate: 0.0-1.0  # Success rate when this memory is applied
last_accessed: "2025-11-09T00:00:00Z"
created_at: "2025-11-09T00:00:00Z"

# Frequency transition metadata
frequency_history: ["high", "mid"]  # Progression through tiers
transition_timestamps: ["2025-11-09T00:00:00Z", "2025-11-10T00:00:00Z"]
consolidation_log: "Promoted from high to mid after 5 successful uses"

# Associative memory (for execution traces)
goal_signature: "string"  # Semantic key for this memory
task_type: "research|development|creative|analysis"
context_fingerprint: "hash"  # Context under which this memory applies

# Learning metadata
learning_source: "execution|consolidation|manual"
pattern_confidence: 0.0-1.0  # Confidence in extracted patterns
validation_count: 0  # Times validated against new data
---
```

## Memory Type Specifications

### 1. High-Frequency Memory (workspace/state/)

**Purpose**: Immediate working memory for current execution

**Files**:
- `plan.md`: Execution plan with steps
- `context.md`: Accumulated knowledge
- `variables.json`: Structured state
- `history.md`: Detailed execution log
- `constraints.md`: Behavioral modifiers

**Metadata Example**:
```yaml
---
memory_frequency: high
volatility: high
update_trigger: execution
retention_policy: volatile
confidence_score: 1.0  # Always reflects current state
created_at: "2025-11-09T00:00:00Z"
---
```

**Lifecycle**:
- Created: Start of execution
- Updated: After each tool call
- Cleared: On boot or explicit reset
- Never consolidated to lower tier

### 2. High-Frequency Memory (memory/short_term/)

**Purpose**: Raw experience logs from agent interactions

**Files**:
- `YYYY-MM-DD_HH-MM-SS_agent_interaction.md`
- `YYYY-MM-DD_execution_session.md`

**Metadata Example**:
```yaml
---
memory_frequency: high
volatility: high
update_trigger: execution
retention_policy: temporary
confidence_score: 0.8  # Based on execution success
consolidation_threshold: 0.75
usage_count: 1
success_rate: 1.0
created_at: "2025-11-09T14:30:00Z"
learning_source: execution
---
```

**Lifecycle**:
- Created: During execution
- Analyzed: By MemoryConsolidationAgent
- Promoted: To mid-frequency if successful (confidence ≥ 0.75)
- Archived: After consolidation (retention: 30 days)

### 3. Mid-Frequency Memory (memory/long_term/)

**Purpose**: Validated execution traces and patterns

**Files**:
- `execution_trace_{name}_v{version}.md`
- `pattern_{name}.md`

**Metadata Example**:
```yaml
---
memory_frequency: mid
volatility: medium
update_trigger: success
retention_policy: persistent
confidence_score: 0.85
consolidation_threshold: 0.95
usage_count: 15
success_rate: 0.93
last_accessed: "2025-11-09T16:00:00Z"
created_at: "2025-11-09T14:30:00Z"
frequency_history: ["high", "mid"]
transition_timestamps: ["2025-11-09T14:30:00Z", "2025-11-09T15:00:00Z"]
goal_signature: "research_web_content_summarize"
task_type: "research"
context_fingerprint: "abc123"
learning_source: consolidation
pattern_confidence: 0.85
validation_count: 3
---
```

**Lifecycle**:
- Created: From successful high-frequency consolidation
- Updated: After each successful use (confidence, usage_count, success_rate)
- Promoted: To low-frequency if usage_count ≥ 20 AND success_rate ≥ 0.95
- Version controlled: Incremented on significant modifications

### 4. Low-Frequency Memory (system/memory_log.md, project_learnings.md)

**Purpose**: Stable, cross-project knowledge

**Metadata Example**:
```yaml
---
memory_frequency: low
volatility: low
update_trigger: consolidation
retention_policy: persistent
confidence_score: 0.96
consolidation_threshold: 0.99
usage_count: 45
success_rate: 0.97
last_accessed: "2025-11-09T18:00:00Z"
created_at: "2025-10-01T00:00:00Z"
frequency_history: ["high", "mid", "low"]
transition_timestamps: ["2025-10-01T00:00:00Z", "2025-10-05T00:00:00Z", "2025-10-20T00:00:00Z"]
goal_signature: "multi_source_research_analysis"
task_type: "research"
learning_source: consolidation
pattern_confidence: 0.96
validation_count: 25
cross_project_validated: true
---
```

**Lifecycle**:
- Created: From highly successful mid-frequency patterns
- Updated: Rare, only when new evidence significantly changes understanding
- Promoted: To ultra-low-frequency (core system) if confidence ≥ 0.99
- Versioned: Major version changes only

### 5. Ultra-Low-Frequency Memory (SmartLibrary.md, User Profiles)

**Purpose**: Core system identity and stable user models

**Metadata Example**:
```yaml
---
memory_frequency: ultra-low
volatility: low
update_trigger: manual
retention_policy: permanent
confidence_score: 0.99
usage_count: 200
success_rate: 0.99
created_at: "2025-09-01T00:00:00Z"
frequency_history: ["high", "mid", "low", "ultra-low"]
learning_source: consolidation
pattern_confidence: 0.99
validation_count: 100
cross_project_validated: true
system_core_component: true
---
```

**Lifecycle**:
- Created: From proven low-frequency patterns with near-perfect performance
- Updated: Extremely rare, manual review required
- Never deleted: Forms system's core identity

## Consolidation Rules

### High→Mid Transition

**Trigger**: Successful execution + confidence ≥ 0.75

**Process**:
1. MemoryConsolidationAgent analyzes short-term logs
2. Extracts successful patterns
3. Creates execution_trace.md with mid-frequency metadata
4. Initial confidence based on execution quality

**Validation**:
- Must have complete tool call sequence
- Must have success indicators
- Must be reproducible

### Mid→Low Transition

**Trigger**: usage_count ≥ 20 AND success_rate ≥ 0.95

**Process**:
1. MemoryConsolidationAgent validates pattern across multiple contexts
2. Elevates to system-wide memory_log.md or project_learnings.md
3. Adds to SmartLibrary as reusable component
4. Updates frequency_history

**Validation**:
- Cross-project applicability
- Consistent success across contexts
- High validation_count

### Low→Ultra-Low Transition

**Trigger**: confidence ≥ 0.99 AND cross_project_validated

**Process**:
1. Manual review by ContinuumMemoryAgent
2. Becomes core system component in SmartLibrary
3. May become agent/tool definition
4. Permanently retained

**Validation**:
- Near-perfect success rate
- Validated across many projects
- Represents fundamental system capability

## Query Patterns

### Frequency-Based Queries

**High-Frequency Query** (Recent Context):
```
Find high-frequency memories related to {goal}
Created within last 24 hours
```

**Mid-Frequency Query** (Proven Patterns):
```
Find mid-frequency execution traces
WHERE goal_signature matches {goal}
AND confidence_score >= 0.85
ORDER BY success_rate DESC
```

**Low-Frequency Query** (Stable Knowledge):
```
Find low-frequency patterns
WHERE task_type = {type}
AND cross_project_validated = true
```

### Multi-Tier Query

QueryMemoryTool can search across tiers with priority weighting:

```yaml
query:
  goal: "Research web content and summarize"
  tier_weights:
    high: 0.1  # Prioritize recent context
    mid: 0.6   # Heavily weight proven traces
    low: 0.3   # Include stable knowledge
  filters:
    min_confidence: 0.75
    task_type: research
```

## Memory Pruning

### Retention Policies

| Policy | Tier | Max Age | Condition |
|--------|------|---------|-----------|
| Volatile | High | None | Cleared on boot |
| Temporary | High | 30 days | Archived if not consolidated |
| Persistent | Mid/Low | Indefinite | Retained while useful |
| Permanent | Ultra-Low | Never | Core system identity |

### Pruning Logic

```yaml
pruning_rules:
  high_frequency:
    action: archive
    condition: age > 30 days AND not_consolidated

  mid_frequency:
    action: downgrade
    condition: success_rate < 0.70 OR usage_count < 5 after 60 days

  low_frequency:
    action: flag_for_review
    condition: success_rate < 0.85 after validation

  ultra_low:
    action: none  # Never automatically pruned
```

## Implementation Guidelines

### For Memory-Writing Components

When creating new memory files:

1. **Always include required YAML frontmatter**
2. **Set appropriate frequency tier** based on purpose
3. **Initialize confidence_score** based on quality
4. **Set realistic consolidation_threshold**
5. **Log creation metadata** (timestamp, source)

### For Memory-Reading Components

When querying memory:

1. **Specify tier preferences** (high/mid/low/all)
2. **Filter by confidence_score** (minimum threshold)
3. **Consider volatility** (high volatility = less reliable)
4. **Weight by success_rate** for execution traces
5. **Respect retention_policy** (don't rely on volatile memory)

### For MemoryConsolidationAgent

When consolidating memory:

1. **Check consolidation_threshold** before promotion
2. **Update frequency_history** on transitions
3. **Increment usage_count** and **recalculate success_rate**
4. **Add transition_timestamps**
5. **Update consolidation_log** with reasoning

## Benefits of CMS Schema

1. **Automatic Memory Management**: System knows when to consolidate/prune
2. **Intelligent Querying**: Can prioritize based on frequency and confidence
3. **Continual Learning**: Successful patterns naturally rise to stable tiers
4. **No Catastrophic Forgetting**: Low-frequency knowledge preserved
5. **Explainability**: Full audit trail through frequency_history
6. **Scalability**: Frequency-based pruning prevents bloat
7. **Adaptability**: System improves automatically as memories consolidate

## Example: Complete Memory Lifecycle

```yaml
# Day 1: High-frequency creation
---
memory_frequency: high
volatility: high
confidence_score: 0.80
usage_count: 1
success_rate: 1.0
created_at: "2025-11-09T10:00:00Z"
---

# Day 2: Mid-frequency promotion (after successful consolidation)
---
memory_frequency: mid
volatility: medium
confidence_score: 0.85
usage_count: 5
success_rate: 0.90
frequency_history: ["high", "mid"]
transition_timestamps: ["2025-11-09T10:00:00Z", "2025-11-10T08:00:00Z"]
consolidation_log: "Promoted after successful pattern extraction"
---

# Day 30: Low-frequency promotion (after 25 successful uses)
---
memory_frequency: low
volatility: low
confidence_score: 0.96
usage_count: 25
success_rate: 0.96
frequency_history: ["high", "mid", "low"]
transition_timestamps: ["2025-11-09T10:00:00Z", "2025-11-10T08:00:00Z", "2025-12-08T12:00:00Z"]
consolidation_log: "Elevated to system-wide knowledge after 25 successful applications"
cross_project_validated: true
---
```

---

*This schema transforms LLMunix from a memory-enabled system into a true Continuum Memory System with multi-frequency learning and adaptive consolidation.*
