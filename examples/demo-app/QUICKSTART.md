# Quick Start Guide - LLM OS Demo App (Phase 2.5+)

Get up and running with the LLM OS demo application in 5 minutes.

**NEW: Featuring Nested Learning with Semantic Trace Matching!**

## Prerequisites

```bash
# 1. Check Python version (need 3.11+)
python --version

# 2. Have your Anthropic API key ready
# Get one at: https://console.anthropic.com/
```

## Installation (2 minutes)

```bash
# 1. Navigate to demo-app directory
cd demo-app

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set your API key
export ANTHROPIC_API_KEY="your-key-here"
```

## Run Your First Demo (1 minute)

```bash
# Start interactive demo
python demo_main.py
```

You'll see:
```
╔══════════════════════════════════════════════════════════════╗
║    LLM OS - Demo Application (Phase 2.5)                     ║
╚══════════════════════════════════════════════════════════════╝

Select a demo scenario:
1. Data Processing Pipeline
2. Code Generation Workflow
...
```

## Recommended First Demo

**Choose option 1**: 🧬 Nested Learning Demo (NEW!)

This demo showcases the cutting-edge Nested Learning implementation:
1. **Initial trace creation** (LEARNER mode: ~2,500 tokens)
2. **Exact match replay** (FOLLOWER mode: 0 tokens - 100% savings)
3. **Semantic match** (FOLLOWER/MIXED mode: 0-1,000 tokens - semantic understanding!)
4. **Related task** (MIXED mode: ~1,000 tokens - trace-guided execution)
5. **Unrelated task** (LEARNER mode: ~2,500 tokens - new learning)

**Key Innovation**: The LLM analyzes semantic similarity, not just exact text matching!

### Alternative First Demo

**Option 2**: Code Generation Workflow

Shows the classic Learner → Follower pattern:
1. First run: Learner mode (~2,500 tokens) - learns the pattern
2. Second run: Follower mode (0 tokens) - replays for free
3. **Savings: 100%**

Expected output:
```
First run tokens: ~2,500
Mode: LEARNER

Second run tokens: 0
Mode: FOLLOWER

💰 Savings: 100% (2,500 → 0 tokens)
```

## What's Happening?

1. **First execution**: LLM OS uses Claude to solve the problem, records every step
2. **Execution trace created**: Pattern saved to `workspace/memories/traces/`
3. **Second execution**: Replays the trace with pure Python - no LLM needed!
4. **Result**: Same output, zero tokens

## Next Steps

### Try Other Scenarios

```bash
# Nested Learning (semantic matching)
python demo_main.py --scenario nested-learning

# Token optimization (see dramatic savings)
python demo_main.py --scenario cost-optimization

# Multi-agent orchestration
python demo_main.py --scenario data-pipeline

# SDK hooks (security and token control)
python demo_main.py --scenario hooks

# Run everything
python demo_main.py --all
```

### Explore the Code

```bash
# View main demo implementation
cat demo_main.py

# Check helper functions
cat utils/demo_helpers.py

# Read comprehensive analysis
cat ANALYSIS.md
```

### View Generated Files

```bash
# After running demos, explore outputs
ls output/projects/      # Project directories
ls output/reports/       # Generated reports
ls output/traces/        # Execution traces
```

## Understanding the Output

### Scenario Completion

```
╔══════════════════════════════════════════════════════════════╗
║ 📊 Code Generation Results                                   ║
╠══════════════════════════════════════════════════════════════╣
║ ✅ Success                                                   ║
║                                                              ║
║ Mode: FOLLOWER                                               ║
║ Tokens: 0                                                    ║
║ Steps: 3/3                                                   ║
║ Time: 0.5s                                                   ║
╚══════════════════════════════════════════════════════════════╝
```

**What this means**:
- ✅ Success: Execution completed successfully
- FOLLOWER mode: Used free trace replay
- 0 tokens: No LLM tokens consumed
- 3/3 steps: All steps executed
- 0.5s: Near-instant execution

### Token Summary

After running multiple scenarios:
```
╔══════════════════════════════════════════════════════════════╗
║ Token Summary                                                ║
╠══════════════════════════════════════════════════════════════╣
║ Scenario                    Tokens                           ║
║ ────────────────────────────────────────────────────────     ║
║ Data Pipeline               ~5,000                           ║
║ Code Generation             ~2,500                           ║
║ Research Assistant          ~8,000                           ║
║ ────────────────────────────────────────────────────────     ║
║ Total                       ~15,500                          ║
╚══════════════════════════════════════════════════════════════╝
```

## Troubleshooting

### "Claude Agent SDK not installed"

```bash
pip install claude-agent-sdk
```

### "ANTHROPIC_API_KEY not found"

```bash
# Make sure you exported the key
export ANTHROPIC_API_KEY="sk-ant-..."

# Or add to your .bashrc/.zshrc
echo 'export ANTHROPIC_API_KEY="sk-ant-..."' >> ~/.bashrc
```

### "Low battery error"

The token budget is exhausted. The system tracks token usage to prevent runaway consumption.

### Permission errors

```bash
chmod +x demo_main.py
chmod -R 755 ../llmos/workspace/
```

### "Delegation timed out after 300.0s"

This is a known issue with the Research Assistant scenario (option 3):
- Some agent delegations timeout after 5 minutes
- System continues and may generate partial results
- Not a critical error

**Recommendation**: Try the Data Pipeline scenario (option 1) instead for reliable multi-agent orchestration.

### "No messages for 60s - stopping delegation"

This warning may appear in the Research scenario. It's informational - the system is handling slow agent responses and will continue execution.

## Key Concepts (Quick Reference)

### Four Execution Modes

| Mode | Tokens | Description |
|------|--------|-------------|
| **Learner** | ~2,500 | First time, uses LLM, creates trace |
| **Follower** | 0 | Repeat, replays trace, no LLM |
| **MIXED** | ~1,000 | Similar task, trace-guided LLM execution |
| **Orchestrator** | Variable | Complex, coordinates multiple agents |

**The Game Changer**: MIXED mode uses traces as few-shot guidance when the task is similar but not identical!

### Memory Hierarchy

- **L1**: Context window (in LLM)
- **L2**: Session logs (short-term)
- **L3**: Execution traces (Markdown) - **KEY INNOVATION**
- **L4**: Facts and insights (long-term)

### SDK Hooks (Phase 2.5)

Automatically enabled in Learner mode:
- 🔒 **Security**: Blocks dangerous commands
- 📝 **Trace**: Captures execution for Follower mode
- 🧠 **Memory**: Injects context from past runs
- 📊 **Tokens**: Tracks token consumption

## Help & Documentation

- **Full README**: `cat README.md`
- **Detailed Analysis**: `cat ANALYSIS.md`
- **Main llmos docs**: `cat ../llmos/README.md`
- **Architecture**: `cat ../llmos/ARCHITECTURE.md`

## Interactive Menu Options

```
1. 🧬 Nested Learning Demo      - NEW! Semantic matching         🌟 RECOMMENDED
2. Code Generation Workflow     - Learn-once, execute-free        ✅ Working
3. Token Optimization Demo      - Dramatic savings                ✅ Working
4. Data Processing Pipeline     - Multi-agent coordination        ✅ Working
5. DevOps Automation           - Security hooks                  ✅ Working
6. Cross-Project Learning      - Pattern detection               ✅ Working
7. SDK Hooks Demo              - All Phase 2.5 features          ✅ Working
8. Run All Scenarios           - Complete demonstration          ✅ Working
9. View System Stats           - Traces, agents, memory          ✅ Working
0. Exit                        - Quit demo
```

**Note**: Research Assistant (option 3) has known timeout issues. Use Data Pipeline (option 1) for reliable multi-agent demonstration.

## Example Session

```bash
$ python demo_main.py

# Select option 2 (Code Generation)
Choice (0-9): 2

🚀 Booting LLM OS...
✅ LLM OS ready!

First execution (Learner mode)...
[... Claude generates code ...]
First run tokens: ~2,500
Mode: LEARNER

Second execution (Follower mode expected)...
[... Replays trace instantly ...]
Second run tokens: 0
Mode: FOLLOWER

💰 Savings: 100% (2,500 → 0 tokens)

Press Enter to continue...
```

## What Makes This Special?

**Traditional Approach**:
- Every execution uses ~2,500 tokens
- 10 executions = 25,000 tokens
- 100 executions = 250,000 tokens

**LLM OS Approach**:
- First execution: ~2,500 tokens (learns)
- Next 99 executions: 0 tokens (replays)
- Total for 100: ~2,500 tokens

**Savings**: 247,500 tokens (99% reduction)

## Ready to Build?

After exploring the demo, check out:
- Real llmos usage: `../llmos/examples/multi_agent_example.py`
- Create custom agents: `../llmos/kernel/agent_factory.py`
- Add plugins: `../llmos/plugins/example_tools.py`

## Need Help?

1. Read the full README: `cat README.md`
2. Check architecture docs: `cat ../llmos/ARCHITECTURE.md`
3. View examples: `ls ../llmos/examples/`
4. Read comprehensive analysis: `cat ANALYSIS.md`

---

**You're ready!** Run `python demo_main.py` and start exploring.
