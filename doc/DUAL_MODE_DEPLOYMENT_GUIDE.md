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
- **Memory Indexer**: SQLite + ChromaDB for fast retrieval
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

#### Initialize Memory Infrastructure

```bash
# Create necessary directories
mkdir -p system/chroma_db
mkdir -p system/infrastructure
mkdir -p projects

# Run initial memory indexing
python system/infrastructure/memory_indexer.py --index-all
```

#### Verify Installation

```bash
# Check that SQLite database was created
ls -lh system/memory_index.sqlite

# Check that ChromaDB was initialized
ls -lh system/chroma_db/

# Test semantic search
python system/infrastructure/memory_indexer.py --query "research task workflow"
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
ls -lh projects/Project_ai_research/memory/long_term/execution_trace_*.yaml
```

### Workflow 2: Deploying Trace to Edge (Transfer)

```bash
# On cloud machine
# Export the successful trace
cp projects/Project_ai_research/memory/long_term/execution_trace_research_v1.0.yaml \
   /tmp/research_trace.yaml

# Transfer to edge device
scp /tmp/research_trace.yaml edge-device:/home/user/llmunix/edge_runtime/traces/

# Alternative: Use Git for trace distribution
cd projects/Project_ai_research
git add memory/long_term/execution_trace_research_v1.0.yaml
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
    --trace traces/execution_trace_research_v1.0.yaml \
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
# 1. Query memory indexer for matching trace
# 2. Find execution_trace_research_v1.0.yaml (confidence: 0.95)
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

### Indexed Markdown Architecture

LLMunix uses a hybrid memory system:

```
system/
├── memory_log.md              # Source of truth (Markdown)
├── memory_index.sqlite        # Fast metadata queries
└── chroma_db/                 # Semantic similarity search
```

**Benefits**:
- Human-readable memory (Markdown)
- Fast structured queries (SQLite)
- Intelligent semantic search (ChromaDB)
- Git-versionable and portable

### Querying Memory

```python
# In Python
from system.infrastructure.memory_indexer import MemoryIndexer

indexer = MemoryIndexer()

# Hybrid query (recommended)
results = indexer.query_hybrid(
    query_text="research task with web fetching",
    filters={
        'outcome': 'success',
        'min_confidence': 0.8
    },
    n_results=5
)

# Find execution trace for a goal
trace = indexer.find_execution_trace(
    goal_signature="research AI trends",
    min_confidence=0.9
)

if trace:
    print(f"Found trace: {trace['file_path']}")
    print(f"Confidence: {trace['confidence']}")
    print(f"Estimated cost: ${trace['estimated_cost']}")
```

### Memory Indexing

```bash
# Reindex all memory after updates
python system/infrastructure/memory_indexer.py --index-all

# Index a specific file
python system/infrastructure/memory_indexer.py --file projects/Project_foo/memory/long_term/experience_001.md

# Test semantic search
python system/infrastructure/memory_indexer.py --query "legal document analysis"
```

## Execution Trace Management

### Trace Structure

```yaml
trace_id: research-ai-trends-v1.0
goal_signature: "research AI trends and generate report"
confidence: 0.95
estimated_cost: 0.15
estimated_time_secs: 120
success_rate: 0.94
usage_count: 17

steps:
  - step: 1
    description: "Fetch AI news from TechCrunch"
    tool_call:
      tool: "WebFetch"
      parameters:
        url: "https://techcrunch.com/category/artificial-intelligence/"
        prompt: "Extract top 5 AI trends"
    validation:
      - check: "Response contains AI topics"
        type: "content_contains"
        parameters:
          substring: "AI"
```

### Trace Evolution

Traces improve over time based on execution feedback:

```yaml
# Confidence evolution
Initial creation: confidence = 0.75
After 5 successes: confidence = 0.82
After 10 successes: confidence = 0.89
After 20 successes: confidence = 0.95

# After a failure
Confidence drops: 0.95 → 0.67
SystemAgent falls back to Learner mode
New improved trace generated: v1.1
```

### Versioning Strategy

```bash
# Semantic versioning for traces
execution_trace_research_v1.0.yaml  # Initial version
execution_trace_research_v1.1.yaml  # Bug fix (failed step corrected)
execution_trace_research_v1.2.yaml  # Optimization (steps reordered)
execution_trace_research_v2.0.yaml  # Breaking change (new tools added)
```

## Advanced Configurations

### Offline Edge Deployment

For completely air-gapped environments:

```bash
# 1. Prepare offline package on cloud
tar -czf llmunix-edge-offline.tar.gz \
    edge_runtime/ \
    projects/Project_*/memory/long_term/execution_trace_*.yaml

# 2. Transfer via USB or physical media
cp llmunix-edge-offline.tar.gz /media/usb/

# 3. On air-gapped edge device
tar -xzf llmunix-edge-offline.tar.gz
cd edge_runtime

# 4. Execute traces offline
./run_follower.py --trace traces/execution_trace_research_v1.0.yaml
```

### Multi-Device Edge Fleet

Deploy traces to multiple edge devices:

```bash
# Central trace repository
git clone <trace-repository>
cd trace-repository/traces/

# Automated deployment script
for device in edge-01 edge-02 edge-03; do
    scp execution_trace_*.yaml $device:/home/user/llmunix/edge_runtime/traces/
    ssh $device "cd llmunix/edge_runtime && ./run_follower.py --trace traces/execution_trace_research_v1.0.yaml"
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
./run_follower.py --trace traces/failing_trace.yaml --output debug.json
cat debug.json | jq '.step_results[] | select(.status=="failed")'

# Common causes:
# 1. Missing files: Check file paths in trace
# 2. Network required: Some traces need internet
# 3. Permissions: Check file write permissions
```

### Issue: Memory Index Out of Sync

```bash
# Rebuild memory index
rm system/memory_index.sqlite
rm -rf system/chroma_db/
python system/infrastructure/memory_indexer.py --index-all
```

### Issue: Low Trace Confidence

```bash
# Query trace metadata
sqlite3 system/memory_index.sqlite "SELECT trace_id, confidence, success_rate, usage_count FROM execution_traces WHERE confidence < 0.9"

# Analyze failures
grep -r "failed_step" projects/*/memory/long_term/*.md

# Solution: Let SystemAgent re-learn the task in Learner mode
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
