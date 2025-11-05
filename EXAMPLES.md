# LLMunix Dual Mode Examples

**Purpose:** Complete scenarios to validate the Learner-Follower pattern with YAML frontmatter format.

---

## Table of Contents

1. [Quick Start: Basic Dual Mode Test](#scenario-1-basic-dual-mode-test)
2. [Scenario 2: Web Research Workflow](#scenario-2-web-research-workflow)
3. [Scenario 3: File Processing Pipeline](#scenario-3-file-processing-pipeline)
4. [Scenario 4: Multi-Agent Collaboration](#scenario-4-multi-agent-collaboration)
5. [Scenario 5: Error Recovery Pattern](#scenario-5-error-recovery-pattern)
6. [How to Run Examples](#how-to-run-examples)
7. [Validation Checklist](#validation-checklist)

---

## Scenario 1: Basic Dual Mode Test

### Overview

**Goal:** Validate that Follower can parse and execute a simple markdown trace created by Learner.

**Components:**
- Learner Mode: Claude Sonnet 4.5 (via Claude Code)
- Follower Mode: Small model (Granite Nano, Llama 3.1 8B, etc.)
- Execution Trace: Markdown with YAML frontmatter

### Step 1: Learner Creates Execution Trace

**What Learner Does:**
1. Receives novel task: "Create a greeting file and verify it"
2. Plans the workflow
3. Generates markdown execution trace with YAML frontmatter
4. Stores trace in `memory/long_term/`

**Generated Trace:** `execution_trace_greeting_v1.0.md`

```markdown
---
trace_id: greeting-workflow-v1.0
goal_signature: "create greeting file and verify content"
confidence: 0.95
estimated_cost: 0.01
estimated_time_secs: 5
version: "1.0.0"
created_at: "2025-11-05T00:00:00Z"

metadata:
  task_type: "basic_io"
  domain: "file_operations"
  requires_internet: false
  requires_human: false
  risk_level: "low"
  learned_by: "claude-sonnet-4.5"

preconditions:
  - condition: "Output directory exists"
    validation_type: "directory_exists"
    parameters:
      path: "workspace"
---

# Greeting Workflow - Basic I/O Test

> **Purpose**: Create and verify a greeting file to test basic file operations.

## Context

This is a simple two-step workflow to validate Write and Read tools work correctly
in Follower mode. Created by Learner after successful execution.

## Workflow Overview

1. Write greeting message to file
2. Read and verify the greeting

## Execution Steps

### Step 1: Create Greeting File

**Purpose**: Write a greeting message to demonstrate Write tool.

**Tool Call**:
```yaml
tool: "Write"
parameters:
  file_path: "workspace/greeting.txt"
  content: "Hello from LLMunix Dual Mode! Learner created this trace, Follower executes it."
```

**Validation**:
```yaml
- check: "Greeting file exists"
  type: "file_exists"
  parameters:
    path: "workspace/greeting.txt"
- check: "File has content"
  type: "file_size_minimum"
  parameters:
    path: "workspace/greeting.txt"
    min_bytes: 10
```

**Error Handling**:
```yaml
on_error:
  action: "fail"
  error_message: "Failed to create greeting file"
```

**Dependencies**: None

---

### Step 2: Verify Greeting

**Purpose**: Read the greeting file to verify content.

**Tool Call**:
```yaml
tool: "Read"
parameters:
  file_path: "workspace/greeting.txt"
```

**Validation**:
```yaml
- check: "Content not empty"
  type: "content_not_empty"
- check: "Contains expected greeting"
  type: "content_contains"
  parameters:
    substring: "LLMunix Dual Mode"
```

**Error Handling**:
```yaml
on_error:
  action: "fail"
  error_message: "Failed to read or verify greeting"
```

**Dependencies**: Step 1

---

## Expected Outputs

```yaml
outputs:
  - name: "Greeting File"
    type: "file"
    location: "workspace/greeting.txt"
    description: "Simple greeting message file"
```

## Version History

- **v1.0.0** (2025-11-05): Initial creation by Learner
```

### Step 2: Follower Executes Trace

**Command:**
```bash
python3 edge_runtime/run_follower.py \
  --trace memory/long_term/execution_trace_greeting_v1.0.md \
  --base-dir /home/user/llmunix
```

**Expected Output:**
```
[10:00:00] INFO: Loading execution trace: .../execution_trace_greeting_v1.0.md
[10:00:00] INFO: Loaded trace: greeting-workflow-v1.0 with 2 steps
[10:00:00] INFO: Checking preconditions...
[10:00:00] INFO: Precondition 1: PASSED

============================================================
Executing Step 1: Create Greeting File
============================================================
Tool: Write
✓ Step 1 completed successfully (0.00s)
  Validation 1: Greeting file exists - ✓ PASS
  Validation 2: File has content - ✓ PASS

============================================================
Executing Step 2: Verify Greeting
============================================================
Tool: Read
✓ Step 2 completed successfully (0.00s)
  Validation 1: Content not empty - ✓ PASS
  Validation 2: Contains expected greeting - ✓ PASS

============================================================
EXECUTION COMPLETE
Status: SUCCESS
Steps: 2/2 completed
Time: 0.01s
============================================================
```

### Step 3: Validate Results

**Check created file:**
```bash
cat workspace/greeting.txt
```

**Expected:**
```
Hello from LLMunix Dual Mode! Learner created this trace, Follower executes it.
```

### Success Criteria

- ✅ Follower parsed markdown trace with YAML frontmatter
- ✅ Both steps executed successfully
- ✅ All 4 validations passed
- ✅ Greeting file created with correct content
- ✅ Execution time < 1 second

---

## Scenario 2: Web Research Workflow

### Overview

**Goal:** Demonstrate Learner-Follower pattern for web research tasks.

**Workflow:**
1. Learner (Claude): Solves novel research task, creates trace
2. Follower (Small model): Executes trace for similar research tasks

### Step 1: Learner Creates Research Trace

**Novel Task:** "Fetch AI news from TechCrunch and create summary"

**Generated Trace:** `execution_trace_ai_research_v1.0.md`

```markdown
---
trace_id: ai-research-techcrunch-v1.0
goal_signature: "fetch ai news from techcrunch and create summary"
confidence: 0.90
estimated_cost: 0.15
estimated_time_secs: 30
version: "1.0.0"
created_at: "2025-11-05T10:00:00Z"

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
      path: "workspace/research"
---

# AI Research Workflow - TechCrunch News

> **Purpose**: Fetch latest AI news from TechCrunch and generate summary report.

## Context

This trace captures a proven workflow for gathering AI news from TechCrunch.
Created by Learner after successful execution. Optimized for Follower to
execute repeatedly for daily news monitoring.

## Workflow Overview

1. Fetch AI news from TechCrunch
2. Extract key points
3. Generate summary report

## Execution Steps

### Step 1: Fetch AI News

**Purpose**: Retrieve latest AI-related articles from TechCrunch.

**Tool Call**:
```yaml
tool: "WebFetch"
parameters:
  url: "https://techcrunch.com/category/artificial-intelligence/"
  prompt: "Extract the top 5 AI news headlines and brief summaries from this page"
```

**Validation**:
```yaml
- check: "Response not empty"
  type: "content_not_empty"
- check: "Contains AI content"
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

**Dependencies**: None

---

### Step 2: Generate Summary Report

**Purpose**: Create formatted summary report from fetched news.

**Tool Call**:
```yaml
tool: "Write"
parameters:
  file_path: "workspace/research/ai_news_summary.md"
  content: |
    # AI News Summary - {current_timestamp}

    **Source**: TechCrunch AI Section

    ## Latest Headlines

    {step_1_output}

    ---
    *Generated by LLMunix Follower Mode*
```

**Validation**:
```yaml
- check: "Summary file created"
  type: "file_exists"
  parameters:
    path: "workspace/research/ai_news_summary.md"
- check: "Summary has content"
  type: "file_size_minimum"
  parameters:
    path: "workspace/research/ai_news_summary.md"
    min_bytes: 100
```

**Error Handling**:
```yaml
on_error:
  action: "fail"
  error_message: "Failed to generate summary report"
```

**Dependencies**: Step 1 (output_variable: step_1_output)

---

## Expected Outputs

```yaml
outputs:
  - name: "AI News Summary"
    type: "file"
    location: "workspace/research/ai_news_summary.md"
    description: "Markdown report with latest AI news from TechCrunch"
```

## Notes

- TechCrunch may rate-limit requests; retry logic handles this
- Summary includes timestamp for tracking
- Can be run daily for automated monitoring

## Version History

- **v1.0.0** (2025-11-05): Initial creation by Learner
```

### Step 2: Follower Executes Daily

**Automated Daily Execution:**
```bash
#!/bin/bash
# daily_ai_news.sh - Run daily via cron

python3 edge_runtime/run_follower.py \
  --trace memory/long_term/execution_trace_ai_research_v1.0.md \
  --base-dir /home/user/llmunix \
  --output workspace/research/execution_report_$(date +%Y%m%d).json
```

**Expected Result:**
- Daily AI news summary in `workspace/research/ai_news_summary.md`
- Execution report in `workspace/research/execution_report_YYYYMMDD.json`
- Execution time: ~30 seconds
- Cost: ~$0.02 (with small model) vs $0.50 (with Claude)

### Success Criteria

- ✅ Learner creates reusable research trace once
- ✅ Follower executes trace daily automatically
- ✅ 20-25x cost reduction vs running Learner daily
- ✅ Consistent, reliable results
- ✅ Handles rate limiting with retry logic

---

## Scenario 3: File Processing Pipeline

### Overview

**Goal:** Multi-step file processing with dependencies and variable passing.

**Workflow:**
1. Read input data
2. Process data
3. Generate report
4. Validate output

### Complete Execution Trace

**File:** `execution_trace_data_pipeline_v1.0.md`

```markdown
---
trace_id: data-pipeline-v1.0
goal_signature: "read csv, process data, generate report"
confidence: 0.92
estimated_cost: 0.05
estimated_time_secs: 15
version: "1.0.0"
created_at: "2025-11-05T11:00:00Z"

metadata:
  task_type: "data_processing"
  domain: "analytics"
  requires_internet: false
  requires_human: false
  risk_level: "low"
  learned_by: "claude-sonnet-4.5"

preconditions:
  - condition: "Input file exists"
    validation_type: "file_exists"
    parameters:
      path: "workspace/data/input.csv"
  - condition: "Output directory exists"
    validation_type: "directory_exists"
    parameters:
      path: "workspace/reports"
---

# Data Processing Pipeline

> **Purpose**: Process CSV data and generate analytics report.

## Context

Standard data processing pipeline for CSV files. Reads data, analyzes patterns,
and generates formatted report. Created by Learner, optimized for Follower.

## Workflow Overview

1. Read CSV input
2. Count records
3. Analyze data patterns
4. Generate report with statistics

## Execution Steps

### Step 1: Read Input Data

**Purpose**: Load CSV data from input file.

**Tool Call**:
```yaml
tool: "Read"
parameters:
  file_path: "workspace/data/input.csv"
```

**Validation**:
```yaml
- check: "Data loaded"
  type: "content_not_empty"
- check: "Contains CSV headers"
  type: "content_contains"
  parameters:
    substring: ","
```

**Error Handling**:
```yaml
on_error:
  action: "fail"
  error_message: "Failed to read input CSV file"
```

**Dependencies**: None

---

### Step 2: Count Records

**Purpose**: Count number of data records using bash.

**Tool Call**:
```yaml
tool: "Bash"
parameters:
  command: "wc -l workspace/data/input.csv | awk '{print $1}'"
  description: "Count lines in CSV file"
```

**Validation**:
```yaml
- check: "Count returned"
  type: "content_not_empty"
- check: "Result is numeric"
  type: "command_exit_code"
  parameters:
    expected: 0
```

**Error Handling**:
```yaml
on_error:
  action: "fail"
  error_message: "Failed to count records"
```

**Dependencies**: Step 1

---

### Step 3: Generate Analytics Report

**Purpose**: Create comprehensive report with data statistics.

**Tool Call**:
```yaml
tool: "Write"
parameters:
  file_path: "workspace/reports/data_analysis_report.md"
  content: |
    # Data Analysis Report

    **Generated**: {current_timestamp}
    **Input File**: workspace/data/input.csv

    ## Statistics

    - Total Records: {step_2_output}
    - Processing Status: Complete

    ## Data Preview

    ```csv
    {step_1_output}
    ```

    ## Summary

    Data processing completed successfully. All records analyzed.

    ---
    *Generated by LLMunix Follower Mode*
```

**Validation**:
```yaml
- check: "Report file created"
  type: "file_exists"
  parameters:
    path: "workspace/reports/data_analysis_report.md"
- check: "Report has content"
  type: "file_size_minimum"
  parameters:
    path: "workspace/reports/data_analysis_report.md"
    min_bytes: 200
```

**Error Handling**:
```yaml
on_error:
  action: "fail"
  error_message: "Failed to generate analytics report"
```

**Dependencies**:
- Step 1 (output_variable: step_1_output)
- Step 2 (output_variable: step_2_output)

---

## Expected Outputs

```yaml
outputs:
  - name: "Analytics Report"
    type: "file"
    location: "workspace/reports/data_analysis_report.md"
    description: "Comprehensive data analysis report with statistics"
```

## Version History

- **v1.0.0** (2025-11-05): Initial creation by Learner
```

### Execution

**Command:**
```bash
python3 edge_runtime/run_follower.py \
  --trace memory/long_term/execution_trace_data_pipeline_v1.0.md \
  --base-dir /home/user/llmunix
```

**Expected Output:**
- Report generated at `workspace/reports/data_analysis_report.md`
- Contains record count from Step 2
- Includes data preview from Step 1
- All dependencies resolved correctly

### Success Criteria

- ✅ Multi-step workflow with dependencies
- ✅ Variable passing between steps (step_1_output, step_2_output)
- ✅ Multiple tool types (Read, Bash, Write)
- ✅ All validations pass
- ✅ Output includes data from multiple steps

---

## Scenario 4: Multi-Agent Collaboration

### Overview

**Goal:** Demonstrate Learner coordinating multiple specialized agents, then Follower executing the pattern.

**Agents Involved:**
- SystemAgent (orchestrator)
- MemoryAnalysisAgent (query historical data)
- Custom agents created dynamically

### Execution Trace with Sub-Agent Delegation

**File:** `execution_trace_multi_agent_v1.0.md`

```markdown
---
trace_id: multi-agent-research-v1.0
goal_signature: "coordinate multiple agents for comprehensive research"
confidence: 0.88
estimated_cost: 0.30
estimated_time_secs: 60
version: "1.0.0"
created_at: "2025-11-05T12:00:00Z"

metadata:
  task_type: "multi_agent_orchestration"
  domain: "research"
  requires_internet: true
  requires_human: false
  risk_level: "medium"
  learned_by: "claude-sonnet-4.5"

preconditions:
  - condition: "Agent directory accessible"
    validation_type: "directory_exists"
    parameters:
      path: ".claude/agents"
  - condition: "Memory analysis agent available"
    validation_type: "file_exists"
    parameters:
      path: ".claude/agents/MemoryAnalysisAgent.md"
---

# Multi-Agent Research Workflow

> **Purpose**: Coordinate multiple agents for comprehensive research task.

## Context

This trace demonstrates the Learner-Follower pattern with multi-agent orchestration.
Learner (Claude) coordinates agents to solve complex task, creates trace.
Follower executes the proven agent coordination pattern.

## Workflow Overview

1. Query memory for similar past research
2. Fetch web data based on memory insights
3. Analyze and synthesize findings
4. Generate comprehensive report

## Execution Steps

### Step 1: Consult Memory for Insights

**Purpose**: Query MemoryAnalysisAgent for relevant past research patterns.

**Tool Call**:
```yaml
tool: "Task"
parameters:
  subagent_type: "memory-analysis-agent"
  description: "Query memory for research patterns"
  prompt: |
    Analyze past research tasks to identify:
    1. Successful research sources
    2. Effective analysis approaches
    3. Report formats that worked well

    Query filters:
    - task_type: research
    - final_outcome: success
    - tags: [web_research, analysis]
```

**Validation**:
```yaml
- check: "Memory analysis completed"
  type: "content_not_empty"
- check: "Recommendations provided"
  type: "content_contains"
  parameters:
    substring: "recommend"
```

**Error Handling**:
```yaml
on_error:
  action: "skip"
  continue_on_skip: true
```

**Dependencies**: None

**Notes**: If memory query fails, continue with default approach

---

### Step 2: Fetch Research Data

**Purpose**: Gather research data from recommended sources.

**Tool Call**:
```yaml
tool: "WebFetch"
parameters:
  url: "https://arxiv.org/list/cs.AI/recent"
  prompt: "Extract top 3 recent AI research papers with titles and abstracts"
```

**Validation**:
```yaml
- check: "Research data fetched"
  type: "content_not_empty"
- check: "Contains research papers"
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

**Dependencies**: Step 1 (optional, uses recommendations if available)

---

### Step 3: Synthesize Findings

**Purpose**: Create comprehensive synthesis of research findings.

**Tool Call**:
```yaml
tool: "Write"
parameters:
  file_path: "workspace/research/multi_agent_research_report.md"
  content: |
    # Multi-Agent Research Report

    **Generated**: {current_timestamp}
    **Coordination**: Multi-agent pattern

    ## Memory Insights

    {step_1_output}

    ## Recent Research

    {step_2_output}

    ## Synthesis

    This research was coordinated across multiple agents:
    - MemoryAnalysisAgent provided historical context
    - WebFetch retrieved current research
    - SystemAgent orchestrated the workflow

    ## Recommendations

    Based on combined insights:
    1. Continue monitoring these research areas
    2. Apply proven analysis patterns from memory
    3. Update memory with new findings

    ---
    *Generated by LLMunix Multi-Agent Workflow*
```

**Validation**:
```yaml
- check: "Report created"
  type: "file_exists"
  parameters:
    path: "workspace/research/multi_agent_research_report.md"
- check: "Report comprehensive"
  type: "file_size_minimum"
  parameters:
    path: "workspace/research/multi_agent_research_report.md"
    min_bytes: 500
```

**Error Handling**:
```yaml
on_error:
  action: "fail"
  error_message: "Failed to create synthesis report"
```

**Dependencies**:
- Step 1 (output_variable: step_1_output)
- Step 2 (output_variable: step_2_output)

---

## Expected Outputs

```yaml
outputs:
  - name: "Multi-Agent Research Report"
    type: "file"
    location: "workspace/research/multi_agent_research_report.md"
    description: "Comprehensive report synthesizing memory insights and current research"
```

## Notes

- Memory consultation is optional (skip on error)
- Multiple agents coordinate seamlessly
- Pattern is reusable for similar research tasks

## Version History

- **v1.0.0** (2025-11-05): Initial multi-agent pattern by Learner
```

### Success Criteria

- ✅ Sub-agent delegation via Task tool
- ✅ MemoryAnalysisAgent consulted
- ✅ Error handling with skip capability
- ✅ Multi-source data synthesis
- ✅ Comprehensive report generation

---

## Scenario 5: Error Recovery Pattern

### Overview

**Goal:** Demonstrate robust error handling and recovery in Follower mode.

**Error Scenarios:**
1. Retry on transient failures
2. Skip non-critical steps
3. Fail fast on critical errors
4. Human escalation when needed

### Execution Trace with Error Handling

**File:** `execution_trace_error_recovery_v1.0.md`

```markdown
---
trace_id: error-recovery-pattern-v1.0
goal_signature: "demonstrate error recovery strategies"
confidence: 0.85
estimated_cost: 0.10
estimated_time_secs: 30
version: "1.0.0"
created_at: "2025-11-05T13:00:00Z"

metadata:
  task_type: "resilience_test"
  domain: "error_handling"
  requires_internet: true
  requires_human: false
  risk_level: "medium"
  learned_by: "claude-sonnet-4.5"
---

# Error Recovery Pattern

> **Purpose**: Demonstrate robust error handling strategies in Follower mode.

## Context

This trace tests various error recovery patterns:
- Retry for transient failures
- Skip for optional steps
- Fail for critical errors
- Graceful degradation

## Execution Steps

### Step 1: Fetch with Retry (Transient Failure)

**Purpose**: Fetch data from potentially unstable source.

**Tool Call**:
```yaml
tool: "WebFetch"
parameters:
  url: "https://api.example.com/data"
  prompt: "Fetch latest data"
```

**Validation**:
```yaml
- check: "Data received"
  type: "content_not_empty"
```

**Error Handling**:
```yaml
on_error:
  action: "retry"
  retry_count: 3
  delay_seconds: 5
```

**Dependencies**: None

**Notes**: Retries handle network timeouts or rate limiting

---

### Step 2: Optional Enhancement (Skip on Failure)

**Purpose**: Add optional data enrichment.

**Tool Call**:
```yaml
tool: "WebFetch"
parameters:
  url: "https://api.example.com/enrichment"
  prompt: "Fetch enrichment data"
```

**Validation**:
```yaml
- check: "Enrichment data present"
  type: "content_not_empty"
```

**Error Handling**:
```yaml
on_error:
  action: "skip"
  continue_on_skip: true
```

**Dependencies**: None

**Notes**: This step is optional; skip if it fails

---

### Step 3: Generate Report (Critical - Fail Fast)

**Purpose**: Generate final report (critical step).

**Tool Call**:
```yaml
tool: "Write"
parameters:
  file_path: "workspace/reports/final_report.md"
  content: |
    # Final Report

    Primary Data: {step_1_output}

    Enhancement: {step_2_output}
    (or "Not available" if Step 2 skipped)
```

**Validation**:
```yaml
- check: "Report created"
  type: "file_exists"
  parameters:
    path: "workspace/reports/final_report.md"
```

**Error Handling**:
```yaml
on_error:
  action: "fail"
  error_message: "CRITICAL: Failed to generate report. Manual intervention required."
```

**Dependencies**:
- Step 1 (required)
- Step 2 (optional)

**Notes**: This is critical; fail immediately if it doesn't work

---

## Expected Outputs

```yaml
outputs:
  - name: "Final Report"
    type: "file"
    location: "workspace/reports/final_report.md"
    description: "Report with primary data and optional enrichment"
```

## Recovery Strategies Summary

| Step | Strategy | Rationale |
|------|----------|-----------|
| 1 | Retry (3x) | Network issues are transient |
| 2 | Skip | Enhancement is optional |
| 3 | Fail | Report is critical deliverable |

## Version History

- **v1.0.0** (2025-11-05): Initial error recovery pattern
```

### Expected Behavior

**Scenario A: All steps succeed**
- Step 1: Succeeds on first try
- Step 2: Succeeds
- Step 3: Generates complete report

**Scenario B: Step 1 fails twice, then succeeds**
- Step 1: Fails, retries, retries, succeeds (3rd attempt)
- Step 2: Succeeds
- Step 3: Generates complete report
- Total time: ~15s (includes retry delays)

**Scenario C: Step 2 fails, continues**
- Step 1: Succeeds
- Step 2: Fails, skipped (optional)
- Step 3: Generates report without enrichment
- Status: SUCCESS (with degraded data)

**Scenario D: Step 3 fails**
- Step 1: Succeeds
- Step 2: Succeeds or skipped
- Step 3: Fails
- Status: FAILED
- Error message displayed

### Success Criteria

- ✅ Retry logic works for transient failures
- ✅ Skip works for optional steps
- ✅ Fail fast works for critical steps
- ✅ Execution continues after skip
- ✅ Clear error messages on failure

---

## How to Run Examples

### Prerequisites

1. **Install LLMunix:**
   ```bash
   git clone https://github.com/EvolvingAgentsLabs/llmunix.git
   cd llmunix
   ```

2. **Setup agents (one-time):**
   ```bash
   # On Unix/Linux/Mac:
   ./setup_agents.sh

   # On Windows:
   .\setup_agents.ps1
   ```

3. **Verify structure:**
   ```bash
   ls -la .claude/agents/
   # Should see: SystemAgent.md, GraniteFollowerAgent.md, etc.
   ```

### Running Scenario 1 (Basic Test)

```bash
# Create the execution trace
cat > memory/long_term/execution_trace_greeting_v1.0.md << 'EOF'
[paste Scenario 1 trace content here]
EOF

# Execute with Follower
python3 edge_runtime/run_follower.py \
  --trace memory/long_term/execution_trace_greeting_v1.0.md \
  --base-dir $(pwd)

# Verify output
cat workspace/greeting.txt
```

### Running Scenario 2 (Web Research)

```bash
# Create trace
cat > memory/long_term/execution_trace_ai_research_v1.0.md << 'EOF'
[paste Scenario 2 trace content here]
EOF

# Execute
python3 edge_runtime/run_follower.py \
  --trace memory/long_term/execution_trace_ai_research_v1.0.md \
  --base-dir $(pwd)

# View results
cat workspace/research/ai_news_summary.md
```

### Running Scenario 3 (Data Pipeline)

```bash
# Prepare test data
mkdir -p workspace/data workspace/reports
echo "id,name,value" > workspace/data/input.csv
echo "1,Test,100" >> workspace/data/input.csv
echo "2,Sample,200" >> workspace/data/input.csv

# Create trace
cat > memory/long_term/execution_trace_data_pipeline_v1.0.md << 'EOF'
[paste Scenario 3 trace content here]
EOF

# Execute
python3 edge_runtime/run_follower.py \
  --trace memory/long_term/execution_trace_data_pipeline_v1.0.md \
  --base-dir $(pwd)

# View report
cat workspace/reports/data_analysis_report.md
```

### Running All Scenarios (Test Suite)

```bash
#!/bin/bash
# run_all_examples.sh

echo "Running LLMunix Dual Mode Examples..."

# Scenario 1
echo "=== Scenario 1: Basic Dual Mode Test ==="
python3 edge_runtime/run_follower.py \
  --trace memory/long_term/execution_trace_greeting_v1.0.md \
  --base-dir $(pwd) \
  --output results/scenario1_report.json

# Scenario 2
echo "=== Scenario 2: Web Research ==="
python3 edge_runtime/run_follower.py \
  --trace memory/long_term/execution_trace_ai_research_v1.0.md \
  --base-dir $(pwd) \
  --output results/scenario2_report.json

# Scenario 3
echo "=== Scenario 3: Data Pipeline ==="
python3 edge_runtime/run_follower.py \
  --trace memory/long_term/execution_trace_data_pipeline_v1.0.md \
  --base-dir $(pwd) \
  --output results/scenario3_report.json

echo "All scenarios complete! Check results/ directory for reports."
```

---

## Validation Checklist

### Format Validation

- [ ] All traces have YAML frontmatter
- [ ] Frontmatter includes required fields:
  - [ ] trace_id
  - [ ] goal_signature
  - [ ] confidence
  - [ ] version
  - [ ] metadata block
- [ ] Steps have tool calls in YAML blocks
- [ ] Validations defined for each step
- [ ] Error handling specified

### Execution Validation

- [ ] Follower parses markdown trace successfully
- [ ] YAML frontmatter extracted correctly
- [ ] All steps execute in order
- [ ] Dependencies resolved properly
- [ ] Variables substituted (e.g., {step_1_output})
- [ ] All validations run
- [ ] Error handling works as configured

### Output Validation

- [ ] Expected files created
- [ ] File content matches expectations
- [ ] Validation checks pass
- [ ] Execution reports generated
- [ ] Timing within expected range
- [ ] No unexpected errors

### Dual Mode Pattern Validation

- [ ] Learner creates trace once (high cost, creative)
- [ ] Follower executes trace repeatedly (low cost, fast)
- [ ] Cost reduction 20-80x achieved
- [ ] Speed improvement 5-10x achieved
- [ ] Reliability maintained (>95% success rate)
- [ ] Trace confidence updates based on executions

---

## Troubleshooting

### Issue: Follower can't parse trace

**Check:**
- YAML frontmatter has `---` delimiters at start and end
- No syntax errors in YAML
- All required fields present
- File encoding is UTF-8

**Fix:**
```bash
# Validate YAML frontmatter
python3 -c "import yaml; yaml.safe_load(open('trace.md').read().split('---')[1])"
```

### Issue: Steps fail validation

**Check:**
- Validation type matches expected check
- Parameters are correct
- Files/directories exist as expected

**Fix:**
- Add debug logging: `--verbose` flag
- Check preconditions before execution
- Verify file paths are absolute or relative to base_dir

### Issue: Variable substitution doesn't work

**Check:**
- Variable format: `{step_N_output}`
- Step dependency declared in `depends_on`
- Previous step completed successfully

**Fix:**
- Review dependencies in trace
- Check step execution order
- Verify output_variable names match

---

## Performance Benchmarks

### Expected Performance

| Scenario | Steps | Time (Learner) | Time (Follower) | Speedup |
|----------|-------|----------------|-----------------|---------|
| Basic Test | 2 | 5-10s | 0.01s | 500-1000x |
| Web Research | 2 | 30-60s | 30-35s | 1-2x |
| Data Pipeline | 3 | 10-20s | 0.05s | 200-400x |
| Multi-Agent | 3 | 60-120s | 60-70s | 1-2x |
| Error Recovery | 3 | 30-60s | 15-40s | 1-2x |

**Note:** Speedup is highest for non-network operations. Network-bound tasks show less improvement.

### Cost Comparison

| Scenario | Learner Cost | Follower Cost | Savings |
|----------|--------------|---------------|---------|
| Basic Test | $0.05 | $0.001 | 50x |
| Web Research | $0.50 | $0.02 | 25x |
| Data Pipeline | $0.10 | $0.005 | 20x |
| Multi-Agent | $1.00 | $0.05 | 20x |
| Error Recovery | $0.50 | $0.03 | 17x |

**Total savings over 1000 executions:** $500-$1000+

---

## Next Steps

### After Running Examples

1. **Review Results:**
   - Check all generated files
   - Review execution reports
   - Verify all validations passed

2. **Create Your Own Traces:**
   - Use examples as templates
   - Adapt for your specific use cases
   - Test thoroughly before production

3. **Deploy to Edge:**
   - Package follower runtime
   - Deploy traces to edge devices
   - Monitor execution success rates

4. **Iterate and Improve:**
   - Update trace confidence scores
   - Add more validation checks
   - Optimize for speed/cost

### Resources

- **Documentation:** `docs/DUAL_MODE_DEPLOYMENT_GUIDE.md`
- **Trace Schema:** `system/infrastructure/execution_trace_schema.md`
- **Agent Definitions:** `.claude/agents/`
- **Memory Logs:** `system/memory_log.md`

---

## Summary

These 5 scenarios demonstrate the complete Learner-Follower pattern:

1. **Basic Test** - Simple validation of dual mode
2. **Web Research** - Real-world research workflow
3. **Data Pipeline** - Multi-step with dependencies
4. **Multi-Agent** - Complex agent coordination
5. **Error Recovery** - Robust error handling

**Key Benefits:**
- ✅ 20-80x cost reduction
- ✅ 5-10x speed improvement
- ✅ Consistent, reliable execution
- ✅ Scales to edge devices
- ✅ Proven patterns reusable

**Start with Scenario 1, then progress to more complex scenarios as you build confidence.**

---

*LLMunix Dual Mode Examples - Complete Scenarios*
*Version: 1.0.0*
*Last Updated: 2025-11-05*
