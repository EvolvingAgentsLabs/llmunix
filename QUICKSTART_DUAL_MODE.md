# LLMunix Dual-Mode Quick Start

Get started with the advanced Learner-Follower architecture in 5 minutes.

## 🚀 Quick Setup

### 1. Install Dependencies

```bash
cd llmunix
pip install -r requirements.txt
```

### 2. Initialize Memory System

```bash
# Create memory indexes
python system/infrastructure/memory_indexer.py --index-all

# Verify installation
ls -lh system/memory_index.sqlite
ls -lh system/chroma_db/
```

### 3. Run Your First Learning Task

```bash
# Example: Research and analysis task
# SystemAgent will automatically use Learner mode (Claude Sonnet 4.5)

llmunix execute: "Research recent developments in quantum computing from ArXiv, summarize key findings"

# What happens:
# 1. SystemAgent checks for existing execution trace
# 2. Finds none → activates Learner mode
# 3. Uses Claude Sonnet 4.5 to solve problem creatively
# 4. Generates execution trace from successful workflow
# 5. Indexes trace in memory for future use

# Check the generated trace
ls projects/Project_quantum_research/memory/long_term/execution_trace_*.yaml
```

### 4. Re-run the Same Task (Follower Mode)

```bash
# Run the exact same task again
llmunix execute: "Research recent developments in quantum computing from ArXiv, summarize key findings"

# What happens NOW:
# 1. SystemAgent finds high-confidence trace (>= 0.9)
# 2. Activates Follower mode → 20-80x cheaper!
# 3. Executes trace deterministically via GraniteFollowerAgent
# 4. Completes in 3-10x less time
# 5. Updates trace metadata (usage_count, success_rate)
```

## 📊 See the Difference

### First Execution (Learner)
```
Mode: LEARNER
Model: Claude Sonnet 4.5
Cost: ~$1.20
Time: 240 seconds
Output: ✅ Comprehensive quantum research report
Side Effect: Created execution_trace_quantum_v1.0.yaml
```

### Second Execution (Follower)
```
Mode: FOLLOWER
Model: Uses trace (no heavy LLM needed)
Cost: ~$0.05
Time: 45 seconds
Output: ✅ Same quality report
Improvement: 24x cheaper, 5x faster!
```

## 🖥️ Deploy to Edge Device (Optional)

### 1. Setup Edge Runtime

```bash
# On your Raspberry Pi or edge computer
git clone <repository>
cd llmunix/edge_runtime
pip install -r requirements.txt
```

### 2. Transfer Trace

```bash
# From cloud machine
scp projects/Project_quantum_research/memory/long_term/execution_trace_quantum_v1.0.yaml \
    edge-device:/home/user/llmunix/edge_runtime/traces/
```

### 3. Execute on Edge (Offline!)

```bash
# On edge device - works completely offline
./run_follower.py \
    --trace traces/execution_trace_quantum_v1.0.yaml \
    --base-dir /home/user/llmunix

# Cost: ~$0.001 (just electricity)
# No internet needed
# Same reliable output
```

## 🔍 Query Memory Intelligence

```bash
# Find similar past experiences
python system/infrastructure/memory_indexer.py \
    --query "research tasks with web fetching"

# Results show:
# - experience_id
# - similarity score
# - goal description
# - file path to full context
```

## 🎯 Use Cases

### Perfect for Learner-Follower Pattern

✅ **Research & Analysis**: Fetch, analyze, summarize
✅ **Data Processing**: Extract, transform, load (ETL)
✅ **Report Generation**: Gather data, format, publish
✅ **Testing Workflows**: Setup, execute, validate
✅ **Deployment Pipelines**: Build, test, deploy

### Stay in Learner Mode

⚠️ **Truly Novel Problems**: One-off creative tasks
⚠️ **Highly Dynamic**: Tasks with constantly changing requirements
⚠️ **Complex Decision Trees**: Unpredictable branching logic

## 📈 Monitor Performance

### Check Trace Status

```bash
# View trace metadata
sqlite3 system/memory_index.sqlite \
    "SELECT trace_id, confidence, success_rate, usage_count
     FROM execution_traces
     ORDER BY confidence DESC"
```

### View Execution Reports

```bash
# On edge devices
cat edge_runtime/reports/execution_report.json | jq '.status, .execution_time_secs'
```

## 🛠️ Troubleshooting

### Trace Not Found
```bash
# Reindex memory
python system/infrastructure/memory_indexer.py --index-all
```

### Edge Execution Fails
```bash
# Check dependencies
./run_follower.py --trace traces/test_trace.yaml --output debug.json
cat debug.json | jq '.step_results[] | select(.status=="failed")'
```

### Low Confidence Score
```bash
# Let system re-learn the task
# Confidence will improve with successful executions
```

## 📚 Learn More

- **Full Guide**: `doc/DUAL_MODE_DEPLOYMENT_GUIDE.md`
- **Trace Schema**: `system/infrastructure/execution_trace_schema.md`
- **Architecture**: `CLAUDE.md`

## 💡 Pro Tips

1. **Let it Learn First**: Run new tasks in Learner mode at least once
2. **Trust the Confidence**: Traces >= 0.9 are production-ready
3. **Monitor Edge Devices**: Aggregate execution reports regularly
4. **Version Control Traces**: Keep traces in Git for easy distribution
5. **Start Simple**: Begin with read-only or low-risk tasks on edge

## 🎉 You're Ready!

You now have a **self-evolving AI system** that:
- Learns from experience
- Optimizes costs automatically
- Deploys to edge devices
- Improves with every execution

**Learn once. Execute repeatedly. Deploy anywhere.**
