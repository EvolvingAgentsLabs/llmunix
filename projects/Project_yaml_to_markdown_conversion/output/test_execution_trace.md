---
trace_id: test-markdown-trace-v1.0
experience_id: exp_test_001
goal_signature: "test markdown execution trace parsing with simple file operations"
confidence: 1.0
estimated_cost: 0.01
estimated_time_secs: 5
success_rate: 1.0
usage_count: 0
created_at: "2025-11-05T00:00:00Z"
last_used: "2025-11-05T00:00:00Z"
version: "1.0.0"

metadata:
  task_type: "test"
  domain: "system"
  requires_internet: false
  requires_human: false
  risk_level: "low"
  learned_by: "claude-sonnet-4.5"

preconditions:
  - condition: "Output directory exists"
    validation_type: "directory_exists"
    parameters:
      path: "projects/Project_yaml_to_markdown_conversion/output"
---

# Test Markdown Execution Trace

> **Purpose**: Test that the run_follower.py parser correctly reads and executes Markdown execution traces with YAML frontmatter.

## Context

This trace was created on November 5, 2025, to verify that the Pure Markdown execution trace format works correctly with the Follower runtime. It performs simple file operations to validate parsing and execution.

## Workflow Overview

1. Write a test file with content
2. Read the test file back
3. Verify content matches

This is a **low-risk**, **offline** workflow suitable for testing.

## Execution Steps

### Step 1: Write Test File

**Purpose**: Create a simple text file to verify Write tool functionality.

**Tool Call**:
```yaml
tool: "Write"
parameters:
  file_path: "projects/Project_yaml_to_markdown_conversion/output/test_output.txt"
  content: "Hello from Pure Markdown execution trace! This verifies the parser works."
```

**Validation**:
```yaml
- check: "Output file was created"
  type: "file_exists"
  parameters:
    path: "projects/Project_yaml_to_markdown_conversion/output/test_output.txt"
- check: "File has content"
  type: "file_size_minimum"
  parameters:
    path: "projects/Project_yaml_to_markdown_conversion/output/test_output.txt"
    min_bytes: 10
```

**Error Handling**:
```yaml
on_error:
  action: "fail"
  error_message: "Failed to write test file"
```

**Dependencies**: None (first step)

---

### Step 2: Read Test File

**Purpose**: Read back the file we just created to verify Read tool and variable substitution.

**Tool Call**:
```yaml
tool: "Read"
parameters:
  file_path: "projects/Project_yaml_to_markdown_conversion/output/test_output.txt"
```

**Validation**:
```yaml
- check: "Content is not empty"
  type: "content_not_empty"
- check: "Content contains expected text"
  type: "content_contains"
  parameters:
    substring: "Pure Markdown"
```

**Error Handling**:
```yaml
on_error:
  action: "fail"
  error_message: "Failed to read test file"
```

**Dependencies**: None

---

## Post-Execution Validation

```yaml
postconditions:
  - condition: "Test file exists and contains expected content"
    validation_type: "file_exists_and_valid"
    parameters:
      path: "projects/Project_yaml_to_markdown_conversion/output/test_output.txt"
```

## Expected Outputs

```yaml
outputs:
  - name: "Test Output File"
    type: "file"
    location: "projects/Project_yaml_to_markdown_conversion/output/test_output.txt"
    description: "Simple text file created by the trace for testing purposes"
```

## Notes and Lessons Learned

### Purpose of This Trace
This trace validates that the run_follower.py parser can:
- Extract YAML frontmatter from markdown files
- Parse step definitions with tool calls, validations, and error handling
- Execute steps in the correct order
- Perform validations correctly

### What We're Testing
- ✅ YAML frontmatter extraction
- ✅ Markdown step parsing
- ✅ Tool call execution (Write, Read)
- ✅ Validation checks
- ✅ Error handling configuration
- ✅ Pure Markdown format compliance

## Version History

- **v1.0.0** (2025-11-05): Initial creation for testing Pure Markdown execution traces
