# Execution Trace Schema (Markdown Format)

## Purpose

An Execution Trace is a deterministic, human-readable instruction set that captures a successful workflow for achieving a specific goal. It's the key artifact enabling the **Learner-Follower Pattern** in LLMunix.

**Format**: Markdown with YAML frontmatter (consistent with LLMunix's Pure Markdown philosophy)

## Architecture Context

### Learner Mode (Claude Sonnet 4.5 via Claude Code)
- Explores novel problems
- Creates execution traces from successful workflows
- Expensive, creative, intelligent
- Model: claude-sonnet-4-5 (the same model powering Claude Code)

### Follower Mode (Granite Nano or similar)
- Executes pre-defined traces
- Fast, cheap, reliable
- No reasoning required - just instruction following

## Markdown Schema Definition

### File Format: `.md` (Markdown with YAML Frontmatter)

```markdown
---
# YAML Frontmatter (Structured Metadata)
trace_id: string              # Unique identifier (format: project-task-version)
experience_id: string         # Optional link to source memory experience
goal_signature: string        # Natural language description of what this achieves
confidence: float             # 0-1, how reliable is this trace
estimated_cost: float         # USD cost estimate for execution
estimated_time_secs: float    # Time estimate in seconds
success_rate: float           # Historical success rate (0-1)
usage_count: integer          # How many times this trace has been executed
created_at: string            # ISO timestamp
last_used: string             # ISO timestamp of last execution
version: string               # Semantic version (e.g., "1.2.0")

# Metadata for context and learning
metadata:
  task_type: string           # research, analysis, development, etc.
  domain: string              # quantum, legal, creative, etc.
  requires_internet: boolean  # Whether trace needs network access
  requires_human: boolean     # Whether human review is needed
  risk_level: string          # low, medium, high
  learned_by: string          # Model that created this trace (e.g., "claude-sonnet-4.5")

# Pre-execution requirements and validations
preconditions:
  - condition: string         # Natural language or evaluable expression
    validation_type: string   # file_exists, env_var_set, etc.
---

# [Trace Title]

> **Purpose**: [Brief description of what this trace accomplishes]

## Context

[Narrative explanation of when and why this trace was created, what problem it solves, and any important context]

## Workflow Overview

[High-level description of the steps in human-readable narrative form]

## Execution Steps

### Step 1: [Step Name]

**Purpose**: [What this step accomplishes]

**Tool Call**:
```yaml
tool: string            # Tool name (Write, Read, Bash, WebFetch, Task)
parameters:             # Tool-specific parameters (must be complete)
  # Examples:
  # For Write:
  #   file_path: string
  #   content: string
  # For Bash:
  #   command: string
```

**Validation**:
```yaml
- check: string         # Description of what to validate
  type: string          # file_exists, command_exit_code, content_contains, etc.
  parameters: {}        # Check-specific parameters
```

**Error Handling**:
```yaml
on_error:
  action: string          # retry, skip, fail, human_escalate
  retry_count: integer    # For retry action
  fallback_step: integer  # Alternative step to try
```

**Dependencies**: [List of previous steps this depends on]

---

### Step 2: [Step Name]

[Repeat pattern for each step...]

---

## Post-Execution Validation

```yaml
postconditions:
  - condition: string
    validation_type: string
```

## Expected Outputs

```yaml
outputs:
  - name: string
    type: string              # file, directory, variable, metric
    location: string          # Where to find it
    description: string
```

## Notes and Lessons Learned

[Any important observations, gotchas, or learnings from using this trace]

## Version History

- **v1.0.0** (YYYY-MM-DD): Initial creation by [agent/user]
- **v1.1.0** (YYYY-MM-DD): [Description of changes]
```

## Example: Research Task Execution Trace (Markdown Format)

**File**: `execution_trace_ai_research_v1.2.md`

```markdown
---
trace_id: research-ai-trends-v1.2
experience_id: exp_045_ai_research_success
goal_signature: "research AI trends from multiple sources and generate comprehensive report"
confidence: 0.95
estimated_cost: 0.15
estimated_time_secs: 120
success_rate: 0.94
usage_count: 17
created_at: "2025-01-15T10:30:00Z"
last_used: "2025-01-20T14:22:00Z"
version: "1.2.0"

metadata:
  task_type: "research"
  domain: "technology"
  requires_internet: true
  requires_human: false
  risk_level: "low"
  learned_by: "claude-sonnet-4.5"

preconditions:
  - condition: "Internet connectivity available"
    validation_type: "network_check"
  - condition: "Output directory exists"
    validation_type: "directory_exists"
    parameters:
      path: "projects/Project_ai_research/output"
---

# AI Trends Research Workflow

> **Purpose**: Fetch latest AI developments from multiple authoritative sources, analyze patterns, and generate a comprehensive research report.

## Context

This trace was created on January 15, 2025, when Claude Sonnet 4.5 (via Claude Code) successfully completed a comprehensive AI trends research task. The workflow proved highly reliable across 17 executions with a 94% success rate.

**Why this trace exists**: Research workflows that fetch from specific trusted sources follow a predictable pattern. By capturing this pattern, subsequent research tasks can execute 24x cheaper and 5x faster using the Follower mode.

## Workflow Overview

1. Fetch current industry news from TechCrunch AI section
2. Fetch recent academic research from ArXiv
3. Synthesize findings using specialized analysis agent
4. Generate formatted markdown report

This is a **low-risk**, **internet-dependent** workflow suitable for automatic execution.

## Execution Steps

### Step 1: Fetch Industry Trends

**Purpose**: Retrieve the latest AI news and industry developments from TechCrunch.

**Tool Call**:
```yaml
tool: "WebFetch"
parameters:
  url: "https://techcrunch.com/category/artificial-intelligence/"
  prompt: "Extract the top 5 trending AI topics and key developments from this page"
```

**Validation**:
```yaml
- check: "Response contains valid content"
  type: "content_not_empty"
- check: "Response mentions AI topics"
  type: "content_contains"
  parameters:
    substring: "AI"
```

**Error Handling**:
```yaml
on_error:
  action: "retry"
  retry_count: 2
  delay_seconds: 5
```

**Dependencies**: None (first step)

**Notes**: TechCrunch occasionally rate-limits requests. The retry logic with 5-second delay handles this gracefully.

---

### Step 2: Fetch Academic Research

**Purpose**: Retrieve recent AI research papers from ArXiv to complement industry news with academic perspective.

**Tool Call**:
```yaml
tool: "WebFetch"
parameters:
  url: "https://arxiv.org/list/cs.AI/recent"
  prompt: "Extract titles and abstracts of the 5 most recent AI research papers"
```

**Validation**:
```yaml
- check: "Response contains paper titles"
  type: "content_contains"
  parameters:
    substring: "arXiv"
```

**Error Handling**:
```yaml
on_error:
  action: "retry"
  retry_count: 2
  delay_seconds: 5
```

**Dependencies**: None (can run in parallel with Step 1)

---

### Step 3: Analyze and Synthesize

**Purpose**: Use specialized analysis agent to identify patterns, common themes, and key insights across both sources.

**Tool Call**:
```yaml
tool: "Task"
parameters:
  subagent_type: "research-analysis-agent"
  prompt: |
    Analyze the following AI trends data and create a comprehensive synthesis:

    Industry Trends: {step_1_output}
    Research Papers: {step_2_output}

    Identify:
    1. Common themes across sources
    2. Emerging technologies
    3. Key research directions
    4. Industry implications
```

**Validation**:
```yaml
- check: "Analysis contains all required sections"
  type: "content_structure_check"
  parameters:
    required_sections: ["Common Themes", "Emerging Technologies", "Research Directions", "Industry Implications"]
```

**Error Handling**:
```yaml
on_error:
  action: "human_escalate"
  escalation_message: "Analysis agent failed to produce structured output. Manual review required."
```

**Dependencies**:
- Step 1 (output_variable: `step_1_output`)
- Step 2 (output_variable: `step_2_output`)

**Notes**: The analysis agent uses Claude Sonnet 4.5 for deep pattern recognition. This is the most expensive step but produces high-quality insights.

---

### Step 4: Generate Report

**Purpose**: Create final formatted markdown report with all findings, properly structured for publication.

**Tool Call**:
```yaml
tool: "Write"
parameters:
  file_path: "projects/Project_ai_research/output/ai_trends_report.md"
  content: |
    # AI Trends Research Report
    Generated: {current_timestamp}

    ## Executive Summary
    {synthesis_summary}

    ## Industry Trends
    {industry_trends_section}

    ## Research Developments
    {research_section}

    ## Analysis
    {analysis_section}

    ## Recommendations
    {recommendations_section}

    ---
    *Report generated by LLMunix using execution trace v1.2*
```

**Validation**:
```yaml
- check: "Report file was created"
  type: "file_exists"
  parameters:
    path: "projects/Project_ai_research/output/ai_trends_report.md"
- check: "Report has minimum length"
  type: "file_size_minimum"
  parameters:
    path: "projects/Project_ai_research/output/ai_trends_report.md"
    min_bytes: 5000
```

**Error Handling**:
```yaml
on_error:
  action: "fail"
  error_message: "Critical: Failed to write final report"
```

**Dependencies**:
- Step 3 (output_variable: `step_3_output`)

---

## Post-Execution Validation

```yaml
postconditions:
  - condition: "Final report exists and is complete"
    validation_type: "file_exists_and_valid"
    parameters:
      path: "projects/Project_ai_research/output/ai_trends_report.md"
  - condition: "Report contains all required sections"
    validation_type: "content_structure_check"
```

## Expected Outputs

```yaml
outputs:
  - name: "AI Trends Report"
    type: "file"
    location: "projects/Project_ai_research/output/ai_trends_report.md"
    description: "Comprehensive markdown report on current AI trends combining industry and academic perspectives"
```

## Notes and Lessons Learned

### What Works Well
- Fetching from both industry and academic sources provides comprehensive coverage
- The 5-second retry delay handles rate limiting effectively
- Analysis agent consistently produces high-quality structured output

### Potential Issues
- ArXiv occasionally changes their HTML structure (affects extraction reliability)
- Very long research papers can cause analysis agent to exceed context limits
- Report generation assumes standard markdown formatting

### Optimization Opportunities
- Could parallelize Step 1 and Step 2 for faster execution
- Consider caching source fetches for 1 hour to reduce redundant network calls
- Could add confidence scoring to synthesized findings

## Version History

- **v1.0.0** (2025-01-15): Initial creation by SystemAgent using Claude Sonnet 4.5
- **v1.1.0** (2025-01-17): Added retry logic with delays for rate limiting
- **v1.2.0** (2025-01-18): Enhanced validation checks and improved error messages
```

## Benefits of Markdown Format

### 1. Human Readability
- Engineers can understand traces at a glance
- Context and rationale are preserved
- Version history is documented inline

### 2. LLMunix Philosophy Alignment
- Consistent with agents (markdown with YAML frontmatter)
- Consistent with memory logs (markdown with YAML frontmatter)
- **Pure Markdown Operating System** - everything is markdown

### 3. Enhanced Documentation
- Each step can have detailed explanations
- Notes and lessons learned are part of the trace
- Context helps future modifications

### 4. Git-Friendly
- Clear diffs when traces evolve
- Easy to review changes in pull requests
- Collaborative editing with standard tools

### 5. Still Machine-Parseable
- YAML frontmatter is easy to parse
- Structured step definitions in YAML code blocks
- Tools can extract and execute deterministically

## Comparison: YAML vs Markdown

### Pure YAML (Old Approach)
```yaml
trace_id: research-ai-trends-v1.2
steps:
  - step: 1
    tool_call:
      tool: WebFetch
    # Hard to read, no context, no explanations
```

### Markdown with YAML (New Approach)
```markdown
---
trace_id: research-ai-trends-v1.2
---

# AI Trends Research

> Purpose: Comprehensive research workflow

## Step 1: Fetch Industry Trends

**Purpose**: Retrieve latest AI news from TechCrunch

[Clear narrative explanation]

**Tool Call**:
```yaml
tool: WebFetch
# Structured data where needed
```

**Notes**: TechCrunch occasionally rate-limits...
```

**Winner**: Markdown format provides **context + structure** while maintaining LLMunix philosophy.

## Implementation in Edge Runtime

The edge runtime (`run_follower.py`) will be updated to:
1. Read `.md` files instead of `.yaml`
2. Parse YAML frontmatter for metadata
3. Extract step definitions from markdown sections
4. Execute deterministically as before

This is a non-breaking change since the structured data is still YAML, just embedded in markdown.

## Storage Convention

```
projects/Project_name/
└── memory/
    └── long_term/
        ├── execution_trace_research_v1.2.md    # ✅ Markdown format
        ├── execution_trace_analysis_v2.0.md    # ✅ Markdown format
        └── project_learnings.md                 # (already markdown)
```

## Why This Matters

LLMunix's philosophy is **"Pure Markdown Operating System where everything is markdown"**. By using Markdown for execution traces:

- ✅ **Consistency**: Agents, tools, memory, AND traces are all markdown
- ✅ **Transparency**: Anyone can read and understand traces
- ✅ **Evolution**: Traces document their own history and rationale
- ✅ **Collaboration**: Standard markdown tools work everywhere
- ✅ **Philosophy**: Stays true to "Pure Markdown" vision

YAML was a pragmatic choice for machine readability, but **Markdown with YAML frontmatter** gives us the best of both worlds - exactly like we do for agents and memory logs.

---

*Execution traces are now fully aligned with LLMunix's Pure Markdown philosophy while maintaining complete machine parseability.*
