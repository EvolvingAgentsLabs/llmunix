# LLMunix Dual-Mode Deployment Guide

## Overview

LLMunix now operates with an advanced **Learner-Follower** architecture that enables:

1. **Learning Phase**: Use Claude Sonnet 4.5 to solve novel problems and create execution traces
2. **Execution Phase**: Deploy traces to edge devices running small, efficient models
3. **Continuous Improvement**: Traces evolve based on real-world execution feedback

This architecture reduces operational costs by **20-80x** and execution time by **3-10x** for repetitive tasks.

## Architecture Components

### Cloud Infrastructure (Learner Mode)

**Purpose**: Problem-solving, learning, and trace generation

**Components**:
- **Claude Code**: Runtime environment
- **Claude Sonnet 4.5**: Powerful reasoning model
- **SystemAgent**: Orchestration and mode selection
- **Memory System**: Pure markdown files with bold text metadata for structured queries
- **MemoryConsolidationAgent**: Generates execution traces

**When Used**:
- Novel problems with no execution history
- Complex tasks requiring creative problem-solving
- Low-confidence or failed trace recovery
- First-time workflows

### Edge Infrastructure (Follower Mode)

**Purpose**: Fast, cheap, reliable execution of learned workflows

**Components**:
- **Standalone Python Runtime**: No Claude Code dependency
- **Small Language Models**: Granite Nano 4B, Llama 3.1 8B, Mistral 7B
- **Local Tool Library**: Read, Write, Bash implementations
- **Execution Traces**: Pre-validated instruction sets

**When Used**:
- Repetitive tasks with proven traces (confidence >= 0.9)
- Resource-constrained environments
- Offline/air-gapped operations
- Cost and speed optimization priorities

## Setup Guide

### Phase 1: Cloud Learning Environment

#### Prerequisites

```bash
# Python 3.9+
python --version

# Claude Code installed
claude --version

# Install dependencies
cd llmunix
pip install -r requirements.txt
```

#### Verify Installation

```bash
# Check that core directories exist
ls -lh system/
ls -lh projects/

# Verify memory log is present
ls -lh system/memory_log.md

# LLMunix is ready - zero dependencies!
# Memory is stored in pure markdown files (no parsing needed)
```

### Phase 2: Edge Deployment Environment

#### Edge Device Requirements

**Minimum Specifications**:
- **CPU**: 4-core ARM or x86
- **RAM**: 2GB available
- **Storage**: 5GB for model + dependencies
- **OS**: Linux (Raspberry Pi OS, Ubuntu), Windows, macOS

**Recommended**:
- 8GB RAM for larger models
- SSD storage for faster model loading
- Edge AI accelerator (optional)

#### Setup Edge Runtime

```bash
# On edge device
git clone <llmunix-repository>
cd llmunix/edge_runtime

# Install minimal dependencies
pip install -r requirements.txt

# Test installation
./run_follower.py --help
```

#### Optional: Install Local LLM (for enhanced error handling)

```bash
# Option 1: Ollama (easiest)
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull granite:4b

# Option 2: Direct model download
# Download quantized model to edge_runtime/models/
```

## Usage Workflows

### Workflow 1: Learning a New Task (Cloud)

```bash
# Start LLMunix with Claude Code
cd llmunix

# Execute a novel task (Learner mode activates automatically)
# Example: Create a research analysis workflow
llmunix execute: "Research AI trends from TechCrunch and ArXiv, synthesize findings, generate report"

# SystemAgent will:
# 1. Detect no existing execution trace
# 2. Use Learner mode (Claude Sonnet 4.5)
# 3. Orchestrate multi-agent workflow
# 4. Generate execution trace upon success
# 5. Index trace in memory system

# Check that trace was created
ls -lh projects/Project_ai_research/memory/long_term/execution_trace_*.md
```

### Workflow 2: Deploying Trace to Edge (Transfer)

```bash
# On cloud machine
# Export the successful trace
cp projects/Project_ai_research/memory/long_term/execution_trace_research_v1.0.md \
   /tmp/research_trace.md

# Transfer to edge device
scp /tmp/research_trace.md edge-device:/home/user/llmunix/edge_runtime/traces/

# Alternative: Use Git for trace distribution
cd projects/Project_ai_research
git add memory/long_term/execution_trace_research_v1.0.md
git commit -m "Add research analysis trace"
git push origin main

# On edge device
git pull origin main
```

### Workflow 3: Executing Trace on Edge (Offline)

```bash
# On edge device
cd llmunix/edge_runtime

# Execute the trace
./run_follower.py \
    --trace traces/execution_trace_research_v1.0.md \
    --base-dir /home/user/llmunix \
    --output reports/execution_report.json

# Monitor execution
# The follower will:
# 1. Load and validate the trace
# 2. Check preconditions
# 3. Execute steps sequentially
# 4. Validate after each step
# 5. Generate execution report

# View results
cat projects/Project_ai_research/output/ai_trends_report.md

# Check execution report
cat reports/execution_report.json
```

### Workflow 4: Automatic Mode Selection (Cloud)

```bash
# When executing a task that has a high-confidence trace
llmunix execute: "Research AI trends from TechCrunch and ArXiv, synthesize findings, generate report"

# SystemAgent will:
# 1. Query memory for matching trace
# 2. Find execution_trace_research_v1.0.md (confidence: 0.95)
# 3. Decide: Use Follower mode
# 4. Delegate to granite-follower-agent
# 5. Execute trace deterministically
# 6. Update trace metadata (usage_count, success_rate, confidence)

# Result:
# - 20-80x cost reduction
# - 3-10x speed improvement
# - Same quality output
```

## Memory Management

### Pure Markdown Architecture

LLMunix uses a pure markdown-based memory system:

```
system/
├── memory_log.md              # Centralized experience log (Source of truth)
└── agents/                    # System-level agents
    └── MemoryAnalysisAgent.md # Analyzes memory patterns

projects/
└── [ProjectName]/
    └── memory/
        ├── short_term/        # Agent interactions and context
        └── long_term/         # Consolidated insights and traces
            ├── experiences/   # Individual experience logs
            └── traces/        # Execution traces
```

**Benefits**:
- **100% human-readable**: All memory in pure markdown (no parsing needed)
- **Git-versionable**: Full version control and collaboration
- **Zero dependencies**: No installation, no parsing libraries, no overhead
- **Fully portable**: Clone and run anywhere with standard Unix tools
- **Fast**: Grep-based queries typically <200ms for hundreds of experiences

### Querying Memory

LLMunix uses native tools for memory queries:

```bash
# Find successful experiences
grep -A 50 "**Outcome:** success" system/memory_log.md

# Find experiences by task type
grep -A 50 "**Task Type:** research" system/memory_log.md

# Find high-confidence traces
find projects -name "execution_trace_*.md" -exec grep -l "**Confidence:** 0.9" {} \;

# Agents use Claude Code tools:
# - Glob: Find files matching patterns
# - Grep: Search content using pure markdown patterns
# - Read: Extract metadata from bold text fields
```

### Memory Structure

Each experience in `system/memory_log.md` uses pure markdown with bold text metadata:

```markdown
## Experience: exp_20250103_143022_ai_research

**Experience ID:** exp_20250103_143022_ai_research
**Timestamp:** 2025-01-03T14:30:22Z
**Project Name:** Project_ai_trends_analysis
**Goal Description:** Research AI trends and generate report
**Outcome:** success
**Task Type:** research
**Confidence Score:** 0.95
**Tags:** research, ai_trends, multi_source
**Trace Generated:** yes
**Trace ID:** research_ai_trends_v1.0

---

### Summary
Successfully researched AI trends from three sources...

### Learnings
- Multi-source research pattern is highly effective
- Parallel fetching reduces execution time
...
```

## Execution Trace Management

### Trace Structure

```markdown
# Execution Trace: research-ai-trends-v1.0

**Trace ID:** research-ai-trends-v1.0
**Goal Signature:** research AI trends and generate report
**Confidence:** 0.95
**Estimated Cost:** 0.15
**Estimated Time (seconds):** 120
**Success Rate:** 0.94
**Usage Count:** 17

---

## Step 1: Fetch AI news from TechCrunch

**Description:** Fetch AI news from TechCrunch

**Tool Call:**
- **Tool:** WebFetch
- **Parameters:**
  - **URL:** https://techcrunch.com/category/artificial-intelligence/
  - **Prompt:** Extract top 5 AI trends

**Validation:**
- **Check:** Response contains AI topics
- **Type:** content_contains
- **Parameters:**
  - **Substring:** AI
```

### Trace Evolution

Traces improve over time based on execution feedback:

```markdown
**Confidence Evolution:**
- Initial creation: 0.75
- After 5 successes: 0.82
- After 10 successes: 0.89
- After 20 successes: 0.95

**After a failure:**
- Confidence drops: 0.95 → 0.67
- SystemAgent falls back to Learner mode
- New improved trace generated: v1.1
```

### Versioning Strategy

```bash
# Semantic versioning for traces
execution_trace_research_v1.0.md  # Initial version
execution_trace_research_v1.1.md  # Bug fix (failed step corrected)
execution_trace_research_v1.2.md  # Optimization (steps reordered)
execution_trace_research_v2.0.md  # Breaking change (new tools added)
```

## Advanced Configurations

### Offline Edge Deployment

For completely air-gapped environments:

```bash
# 1. Prepare offline package on cloud
tar -czf llmunix-edge-offline.tar.gz \
    edge_runtime/ \
    projects/Project_*/memory/long_term/execution_trace_*.md

# 2. Transfer via USB or physical media
cp llmunix-edge-offline.tar.gz /media/usb/

# 3. On air-gapped edge device
tar -xzf llmunix-edge-offline.tar.gz
cd edge_runtime

# 4. Execute traces offline
./run_follower.py --trace traces/execution_trace_research_v1.0.md
```

### Multi-Device Edge Fleet

Deploy traces to multiple edge devices:

```bash
# Central trace repository
git clone <trace-repository>
cd trace-repository/traces/

# Automated deployment script
for device in edge-01 edge-02 edge-03; do
    scp execution_trace_*.md $device:/home/user/llmunix/edge_runtime/traces/
    ssh $device "cd llmunix/edge_runtime && ./run_follower.py --trace traces/execution_trace_research_v1.0.md"
done
```

### Trace Quality Monitoring

```bash
# Aggregate execution reports
cd edge_runtime/reports/

# Analyze success rates
jq '.status' *.json | sort | uniq -c

# Calculate average execution time
jq '.execution_time_secs' *.json | awk '{sum+=$1; count++} END {print sum/count}'

# Identify failing steps
jq 'select(.status=="failed") | .failed_step' *.json | sort | uniq -c
```

## Troubleshooting

### Issue: Trace Execution Fails on Edge

```bash
# Check trace validation
./run_follower.py --trace traces/failing_trace.md --output debug.json
cat debug.json | jq '.step_results[] | select(.status=="failed")'

# Common causes:
# 1. Missing files: Check file paths in trace
# 2. Network required: Some traces need internet
# 3. Permissions: Check file write permissions
```

### Issue: Memory Query Slow

```bash
# For large memory logs (>500 experiences), consider:
# 1. Split memory into project-specific logs
# 2. Use more specific Grep patterns
# 3. Archive old experiences to separate files

# Typical query performance:
# - <100 experiences: <500ms
# - 100-500 experiences: <2s
# - >500 experiences: Consider archiving
```

### Issue: Low Trace Confidence

```bash
# Find low-confidence traces
find projects -name "execution_trace_*.md" -exec grep -H "**Confidence:** 0\.[0-8]" {} \;

# Analyze failures
grep -r "**Outcome:** failure" projects/*/memory/long_term/*.md

# Solution: Let SystemAgent re-learn the task in Learner mode
# The system will generate an improved trace after successful execution
```

## Performance Benchmarks

### Cost Comparison

| Mode | Model | Cost per Task | Speed | Best For |
|------|-------|---------------|-------|----------|
| Learner | Claude Sonnet 4.5 | $0.50-2.00 | Slow | Novel problems |
| Follower (Cloud) | Granite Nano 4B | $0.025-0.05 | Fast | Proven workflows |
| Follower (Edge) | Local Granite Nano | ~$0.001 (electricity) | Fast | Offline repetition |

### Execution Time Comparison

```
Research Task (10 steps):
- Learner mode: 180-300 seconds
- Follower mode: 30-60 seconds
- Speedup: 3-10x

Analysis Task (5 steps):
- Learner mode: 90-150 seconds
- Follower mode: 15-30 seconds
- Speedup: 6x
```

## Best Practices

### 1. Trace Creation

- Let Claude solve the problem naturally first
- Review generated traces before deployment
- Test traces in safe environment before production
- Add comprehensive validation checks
- Include retry logic for network-dependent steps

### 2. Memory Management

- Index memory after each significant execution
- Keep memory logs human-readable (don't over-structure)
- Archive old experiences periodically
- Use tags effectively for filtering

### 3. Edge Deployment

- Start with high-confidence traces only (>= 0.9)
- Monitor execution reports regularly
- Update traces when failure rate increases
- Keep traces in version control
- Test offline operation before field deployment

### 4. Security

- Validate trace sources before execution
- Restrict file system access on edge devices
- Review bash commands in traces
- Use sandboxing for high-risk operations
- Encrypt traces containing sensitive information

## Roadmap and Future Enhancements

### Planned Features

1. **Automatic Trace Optimization**: AI-driven trace refinement based on execution data
2. **Distributed Trace Repository**: Central hub for sharing verified traces
3. **Real-time Trace Sync**: Automatic trace updates pushed to edge devices
4. **Advanced Sandboxing**: Container-based execution for enhanced security
5. **Trace Composition**: Combine multiple traces into complex workflows
6. **Visual Trace Editor**: GUI for creating and editing traces
7. **Performance Profiling**: Detailed execution analysis and bottleneck identification
8. **Multi-Model Support**: Support for more edge models (Phi-3, Mistral, etc.)

## Support and Community

- **Documentation**: `doc/` directory in repository
- **Issues**: GitHub Issues for bug reports
- **Discussions**: GitHub Discussions for questions
- **Examples**: `scenarios/` directory for reference implementations

## Conclusion

The Dual-Mode architecture transforms LLMunix from a pure cloud-based reasoning system into a **hybrid intelligence platform**:

1. **Learn** complex tasks with powerful cloud models
2. **Compile** successful workflows into efficient traces
3. **Deploy** traces to edge devices for fast, cheap execution
4. **Evolve** traces based on real-world performance

This creates a **continuous improvement loop** where every successful execution makes the system smarter, faster, and more cost-effective.

Start with Learner mode for novel problems. Graduate to Follower mode for repetitive tasks. Deploy to edge devices for maximum efficiency. Your AI agents learn once and execute repeatedly at minimal cost.

**Welcome to the future of adaptive, deployable AI systems.**
