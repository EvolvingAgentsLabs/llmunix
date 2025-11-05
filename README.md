# LLMunix: Pure Markdown Operating System with Agentic Edge AI

> **Transform any LLM into an intelligent operating system. Learn once with Claude, execute infinitely with Granite at zero cost.**

LLMunix is a revolutionary three-mode AI framework where intelligence is defined in markdown documents. High-powered LLMs create agent definitions, then lightweight edge models execute them with full reasoning capabilities - combining Claude's intelligence with Granite's efficiency.

## 🚀 Revolutionary Architecture

### Three Execution Modes

```
┌─────────────────────────────────────────────────────┐
│         LEARNER MODE (Claude Sonnet 4.5)           │
│  Creates: Agent definitions, execution traces      │
│  Cost: $0.05-$1 per definition (one-time)         │
│  Use: Novel tasks, complex reasoning               │
└─────────────────────────────────────────────────────┘
                        ↓
          (definitions created once)
                        ↓
    ┌──────────────────┴──────────────────┐
    │                                     │
    ▼                                     ▼
┌─────────────────────┐      ┌─────────────────────┐
│ DETERMINISTIC MODE  │      │  AGENTIC MODE       │
│ (Pure Python)       │      │  (Granite 4)        │
│                     │      │                     │
│ Executes: Fixed     │      │ Executes: Flexible  │
│ steps exactly       │      │ with reasoning      │
│                     │      │                     │
│ Speed: 0.01-0.1s    │      │ Speed: 0.5-3s       │
│ Cost: $0            │      │ Cost: $0 (local)    │
│ Adapt: None         │      │ Adapt: High         │
│                     │      │                     │
│ Use: Repetitive     │      │ Use: Variations,    │
│ tasks               │      │ conditional logic   │
└─────────────────────┘      └─────────────────────┘
```

### Why This Matters

**Traditional AI**: $0.50-$5 per execution, requires internet
**LLMunix Agentic**: $0 per execution, offline capable, adapts to variations

**1000 executions**: Save $500-$5000 with agentic mode

## 🎯 Quick Start

### Prerequisites
- Python 3.11+
- Git
- Ollama (for agentic mode)

### Installation

```bash
# Clone the repository
git clone https://github.com/EvolvingAgentsLabs/llmunix.git
cd llmunix

# Initialize the agent system
./setup_agents.sh    # Mac/Linux
# OR
powershell -ExecutionPolicy Bypass -File .\setup_agents.ps1  # Windows

# Install edge runtime dependencies
cd edge_runtime
pip install -r requirements.txt

# Install Ollama for agentic mode
# macOS/Linux: curl -fsSL https://ollama.ai/install.sh | sh
# Windows: Download from https://ollama.com

# Download Granite 4 model
ollama pull granite4:micro  # 2.1 GB - for simple tasks
# OR
ollama pull granite3.3:8b   # 4.9 GB - for complex tasks
```

## 💡 The Three Modes Explained

### Mode 1: Learner (Claude) - Create Once

**Purpose**: Design agent definitions and execution patterns

```bash
# Boot LLMunix with Claude
claude --dangerously-skip-permissions "boot llmunix"

# Create an agent definition
claude --dangerously-skip-permissions "llmunix execute: 'Create an agent for processing customer data files'"
```

**Output**: Agent definition saved to `projects/[project]/components/agents/`

**Cost**: $0.50-$1.00 one-time
**Value**: Reusable forever

---

### Mode 2: Deterministic Follower - Execute Fast

**Purpose**: Repeat identical tasks at maximum speed

```bash
# Execute pre-defined trace
python edge_runtime/run_follower.py \
  --trace memory/long_term/execution_trace_greeting_v1.0.md \
  --base-dir projects/Project_example
```

**Speed**: 0.01-0.1 seconds
**Cost**: $0
**Flexibility**: None (exact steps only)

**Best For**:
- Daily backups
- Fixed report generation
- Repetitive data processing

---

### Mode 3: Agentic Follower (Granite) - Execute Smart 🚀

**Purpose**: Adaptive execution with reasoning

```bash
# Execute with agentic reasoning
python edge_runtime/run_agentic_follower.py \
  --agent components/agents/FileProcessorAgent.md \
  --goal "Process today's sales data and create summary" \
  --base-dir projects/Project_sales \
  --model granite4:micro
```

**What Granite Does**:
1. Reads agent definition (capabilities, constraints, guidelines)
2. Interprets the goal
3. **Reasons about approach** (not hardcoded!)
4. Calls tools adaptively (Read, Write, Bash)
5. Handles variations and edge cases
6. Generates results

**Speed**: 0.5-3 seconds
**Cost**: $0 (local Ollama)
**Flexibility**: High (adapts to variations)

**Best For**:
- Files with varying formats
- Tasks requiring conditional logic
- Workflows needing error recovery
- Scenarios with edge cases

---

## 🌟 Real-World Example: Daily Sales Processing

### Traditional Approach (Expensive)
```bash
# Every day: Call Claude API
# Cost: $2 × 365 days = $730/year
claude "Process today's sales data"
```

### LLMunix Agentic Approach (Smart)

**Step 1: Create Agent Once (Learner)**
```bash
claude "Create agent for processing sales data files"
```
Output: `SalesProcessorAgent.md` with:
- Capabilities: read CSV, analyze data, generate reports
- Constraints: <10MB files, .csv/.xlsx formats
- Guidelines: "Validate → Analyze → Report"
- Error handling: retry on network errors, skip invalid records

Cost: $0.50 (one-time)

**Step 2: Execute Daily (Agentic)**
```bash
# Day 1: sales_2024_11_04.csv
python edge_runtime/run_agentic_follower.py \
  --agent SalesProcessorAgent.md \
  --goal "Process today's sales file"

# Granite reasons: "I see sales_2024_11_04.csv, I'll read it, analyze, generate report"
```

```bash
# Day 2: sales_nov_5.csv (different naming!)
# Granite adapts: "Filename changed but it's still CSV sales data, I'll process it"
```

```bash
# Day 3: sales_data.xlsx (different format!)
# Granite handles: "Excel format detected, I'll adjust my approach"
```

**Cost**: $0.50 setup + $0 × 365 executions = **$0.50/year**
**Savings**: $729.50/year vs traditional approach
**Added Value**: Adapts to file naming changes, format variations, missing data

---

## 🛠️ What Can You Build?

### Intelligent File Processing
```python
# Agent adapts to variations automatically
run_agentic_follower.py \
  --agent FileProcessorAgent.md \
  --goal "Process all customer data files in input/"

# Handles:
# - Different CSV structures
# - Missing columns
# - Varying data quality
# - Multiple formats (.csv, .xlsx, .json)
```

### Research & Analysis with Flexibility
```python
# Agent adjusts extraction based on content
run_agentic_follower.py \
  --agent ResearchAgent.md \
  --goal "Extract key findings from research papers"

# Adapts to:
# - Different paper structures
# - Various academic formats
# - Multiple languages
# - Incomplete data
```

### Conditional Workflows
```python
# Agent makes intelligent decisions
run_agentic_follower.py \
  --agent DataPipelineAgent.md \
  --goal "Process dataset with appropriate strategy"

# Reasoning:
# "File is 50MB → I'll process in chunks"
# "Data quality is poor → I'll apply extra validation"
# "Format is non-standard → I'll use flexible parsing"
```

### Error Recovery
```python
# Agent handles failures gracefully
run_agentic_follower.py \
  --agent RobustProcessorAgent.md \
  --goal "Process data files with retry logic"

# Decisions:
# "Network timeout → retry with exponential backoff"
# "Missing file → check alternative locations"
# "Invalid format → attempt format detection"
```

---

## 📊 Performance Comparison

### Cost Analysis (1000 Executions)

| Mode | Setup | Per-Run | Total | Flexibility |
|------|-------|---------|-------|-------------|
| **Cloud (Claude)** | $0 | $2.00 | **$2,000** | ⭐⭐⭐⭐⭐ |
| **Agentic (Granite)** | $0.50 | $0 | **$0.50** | ⭐⭐⭐⭐ |
| **Deterministic** | $0.50 | $0 | **$0.50** | ⭐ |

**Savings**: $1,999.50 with agentic mode!

### Speed Comparison

| Mode | Execution Time | Latency |
|------|---------------|---------|
| **Deterministic** | 0.01-0.1s | None |
| **Agentic (Granite)** | 0.5-3s | Local LLM |
| **Cloud (Claude)** | 10-30s | Network + LLM |

**Agentic is 10-60x faster than cloud while maintaining flexibility!**

---

## 🎓 Example Projects

### 1. Daily Sales Analytics (Agentic Mode)

**Agent Definition**: `SalesAnalyticsAgent.md`
```markdown
---
agent_id: sales-analytics-agent
capabilities:
  - read_files: [csv, xlsx, json]
  - data_analysis: [statistics, trends, forecasting]
  - report_generation: [markdown, charts]
constraints:
  - max_file_size_mb: 50
  - date_range: last_90_days
reasoning_guidelines: |
  1. Detect file format and adapt parsing
  2. Validate data quality (missing values, outliers)
  3. Calculate key metrics (revenue, growth, trends)
  4. If data sparse, use available data with disclaimer
  5. Generate visual charts for trends
  6. Create executive summary
---
```

**Daily Execution**:
```bash
# Handles any variation automatically
python edge_runtime/run_agentic_follower.py \
  --agent SalesAnalyticsAgent.md \
  --goal "Analyze today's sales and create report" \
  --model granite3.3:8b
```

**Granite's Reasoning**:
- Detects file: `sales_2024_11_05.csv`
- Checks format: CSV with 15 columns
- Validates: 2 missing values found (flags in report)
- Calculates: Revenue up 12% vs yesterday
- Decides: Generate trend chart for last 7 days
- Creates: Markdown report with insights

**Result**: Adaptive analytics without reprogramming

---

### 2. Multi-Format Data Pipeline (Agentic Mode)

**Challenge**: Process customer data in various formats

**Agent**: `DataPipelineAgent.md`
```markdown
reasoning_guidelines: |
  1. Identify file format (CSV, JSON, Excel, XML)
  2. Choose appropriate parser for format
  3. Normalize data to standard schema
  4. If format unknown, try multiple parsers
  5. Validate against schema requirements
  6. Transform and enrich data
  7. Load to destination
  8. Report processing statistics
```

**Execution**:
```bash
python edge_runtime/run_agentic_follower.py \
  --agent DataPipelineAgent.md \
  --goal "Process all files in data/input/"
```

**Granite Handles**:
- File 1: customers.csv → Uses CSV parser
- File 2: orders.json → Switches to JSON parser
- File 3: products.xlsx → Uses Excel parser
- File 4: inventory.xml → Detects XML, uses appropriate parser
- File 5: corrupted.csv → Detects corruption, skips with warning

**No hardcoding needed** - Granite reasons through each file!

---

### 3. Intelligent Web Scraping (Agentic Mode)

**Agent**: `WebScraperAgent.md`
```markdown
reasoning_guidelines: |
  1. Fetch webpage with retry logic
  2. Analyze HTML structure dynamically
  3. If JavaScript-heavy, note in report
  4. Extract content using flexible selectors
  5. If rate-limited, back off exponentially
  6. Validate extracted data quality
  7. If quality poor, try alternative extraction
```

**Execution**:
```bash
python edge_runtime/run_agentic_follower.py \
  --agent WebScraperAgent.md \
  --goal "Scrape tech news from various sources"
```

**Granite Adapts To**:
- Different website structures
- Rate limiting (automatically waits)
- Changed HTML layouts (finds content anyway)
- Missing elements (graceful degradation)
- Network errors (retry with backoff)

---

## 🏗️ Framework Architecture

```
llmunix/
├── system/
│   ├── agents/
│   │   ├── SystemAgent.md              # Orchestration
│   │   └── MemoryAnalysisAgent.md      # Learning
│   ├── tools/
│   │   └── ClaudeCodeToolMap.md        # Tool integration
│   └── memory_log.md                   # Experience database
│
├── edge_runtime/
│   ├── run_follower.py                 # Deterministic execution
│   ├── run_agentic_follower.py         # 🆕 LLM-powered execution
│   └── requirements.txt                # ollama, pyyaml
│
├── projects/
│   └── [ProjectName]/
│       ├── components/
│       │   ├── agents/                 # Project agents (markdown)
│       │   │   ├── FileProcessorAgent.md
│       │   │   ├── DataAnalyzerAgent.md
│       │   │   └── ReportGeneratorAgent.md
│       │   └── tools/                  # Project tools (markdown)
│       ├── memory/
│       │   ├── short_term/             # Execution logs
│       │   └── long_term/              # Execution traces & agent defs
│       ├── input/                      # Input data
│       ├── output/                     # Generated results
│       └── workspace/                  # Temp execution state
│
└── .claude/agents/                     # Auto-discovered agents
```

---

## 🤝 Creating Agentic Agents

### Step 1: Define Agent (Learner Mode)

```bash
claude "Create an agent for processing medical records with HIPAA compliance"
```

**Generated**: `MedicalRecordsAgent.md`
```markdown
---
agent_id: medical-records-processor
version: "1.0"
execution_mode: agentic_with_llm

capabilities:
  file_operations: [read_pdf, read_csv, write_encrypted]
  data_processing: [anonymize, validate_hipaa, extract_codes]
  compliance: [audit_log, encryption, access_control]

constraints:
  max_file_size_mb: 100
  allowed_formats: [pdf, csv, hl7]
  encryption_required: true
  audit_required: true

reasoning_guidelines: |
  HIPAA Compliance Priority:
  1. Verify file encryption before processing
  2. Anonymize all PII (names, SSN, addresses)
  3. Extract medical codes (ICD-10, CPT)
  4. Validate data completeness
  5. If encryption missing, reject with error
  6. Log all access to audit trail
  7. Generate compliance report

error_handling: |
  - Missing PHI: Flag and continue with available data
  - Invalid format: Attempt format detection
  - Encryption failure: HALT and alert (critical)
  - Validation errors: Log and quarantine record
---

# Medical Records Processor Agent

You are a HIPAA-compliant medical records processor...
```

### Step 2: Execute with Agentic Follower

```bash
python edge_runtime/run_agentic_follower.py \
  --agent MedicalRecordsAgent.md \
  --goal "Process today's medical records batch" \
  --model granite3.3:8b \
  --base-dir projects/Project_healthcare
```

**Granite's Reasoning**:
1. "Agent requires encryption → I'll verify encryption first"
2. "File is encrypted → Good, I'll decrypt and process"
3. "Found PII in record 15 → I'll anonymize per guidelines"
4. "Medical code format is ICD-10 → I'll extract correctly"
5. "Data quality issue in record 42 → I'll flag and continue"
6. "All records processed → I'll generate compliance report"

**Audit Trail**: Full log of all decisions and actions

---

## 📚 Mode Selection Guide

### Choose **Deterministic Mode** When:

✅ Task is **identical every time**
✅ **Maximum speed** required (sub-second)
✅ **Zero variability** acceptable
✅ Simple tool sequences

**Example**: Nightly database backup

```bash
python edge_runtime/run_follower.py \
  --trace backup_trace.md \
  --base-dir /data
```

---

### Choose **Agentic Mode (Granite)** When:

✅ Task has **variations** (file formats, structures, content)
✅ Need **conditional logic** ("if X then Y")
✅ **Error recovery** important
✅ Can afford **1-3 seconds** execution time
✅ Want **offline capability** (edge devices)

**Example**: Daily data processing with varying formats

```bash
python edge_runtime/run_agentic_follower.py \
  --agent DataProcessorAgent.md \
  --goal "Process all new files" \
  --model granite4:micro
```

---

### Choose **Learner Mode (Claude)** When:

✅ **Novel task** (never seen before)
✅ **Complex reasoning** required
✅ Creating **new agent definitions**
✅ **Quality > cost**

**Example**: Design new workflow

```bash
claude "llmunix execute: 'Create agent for processing satellite imagery'"
```

---

## 🚀 Advanced Features

### Hybrid Workflows

Combine modes for optimal results:

```bash
# 1. Learner creates definition (once)
claude "Create invoice processing agent"

# 2. Agentic mode handles variations (daily)
python run_agentic_follower.py \
  --agent InvoiceProcessorAgent.md \
  --goal "Process today's invoices"

# 3. Deterministic mode for known formats (batch)
python run_follower.py \
  --trace standard_invoice_trace.md
```

### Multi-Model Strategy

```bash
# Simple tasks: Granite 4:micro (2.1 GB, fast)
--model granite4:micro

# Complex tasks: Granite 3.3:8b (4.9 GB, smarter)
--model granite3.3:8b

# Maximum quality: Claude (cloud, expensive)
claude "llmunix execute: ..."
```

### Edge Deployment

```bash
# Package for edge device
tar -czf llmunix_edge.tar.gz \
  edge_runtime/ \
  projects/Project_myapp/components/agents/ \
  .ollama/models/granite4:micro

# Deploy to edge
scp llmunix_edge.tar.gz device:/opt/llmunix/

# Run on edge (completely offline!)
python run_agentic_follower.py \
  --agent MyAgent.md \
  --goal "Process local data"
```

---

## 💾 Installation Details

### Full Setup

```bash
# 1. Clone repository
git clone https://github.com/EvolvingAgentsLabs/llmunix.git
cd llmunix

# 2. Initialize agents
./setup_agents.sh  # or setup_agents.ps1 on Windows

# 3. Install Python dependencies
cd edge_runtime
pip install -r requirements.txt

# 4. Install Ollama
# macOS/Linux:
curl -fsSL https://ollama.ai/install.sh | sh

# Windows: Download from https://ollama.com/download

# 5. Download Granite models
ollama pull granite4:micro      # 2.1 GB - Simple tasks
ollama pull granite3.3:8b       # 4.9 GB - Complex tasks

# 6. Verify installation
python run_agentic_follower.py --help
```

### Minimal Setup (Agentic Only)

```bash
pip install ollama pyyaml
ollama pull granite4:micro
```

---

## 🔧 Configuration

### Environment Variables

```bash
# .env file
OLLAMA_HOST=http://localhost:11434   # Local Ollama
GRANITE_MODEL=granite4:micro          # Default model
BASE_DIR=/path/to/projects            # Projects directory
```

### Agent Configuration

Each agent can specify:
- **Capabilities**: What tools are available
- **Constraints**: Size limits, format restrictions
- **Reasoning Guidelines**: How to approach problems
- **Error Handling**: Recovery strategies
- **Examples**: Successful patterns

---

## 📖 Complete Examples

See `EXAMPLES.md` for comprehensive examples including:

1. **Basic Agentic Test** - File processing with Granite
2. **Adaptive Data Pipeline** - Handle format variations
3. **Intelligent Research** - Content extraction with flexibility
4. **Multi-Agent Orchestration** - Complex workflows
5. **Error Recovery Patterns** - Robust execution

---

## 🎯 Why LLMunix?

### Traditional AI Limitations
- ❌ $0.50-$5 per execution (expensive at scale)
- ❌ Requires internet connectivity
- ❌ No edge deployment
- ❌ Privacy concerns (data leaves premises)
- ❌ Can't adapt without reprogramming

### LLMunix Advantages
- ✅ **$0 per execution** (after setup)
- ✅ **Offline capable** (edge devices)
- ✅ **Adapts to variations** (agentic reasoning)
- ✅ **Privacy-preserving** (all local)
- ✅ **Learn once, execute infinitely**

### The Sweet Spot: Agentic Mode

```
Deterministic: Fast but inflexible
     ↓ (add reasoning)
Agentic: Fast AND flexible
     ↓ (add power)
Cloud: Flexible but expensive
```

**Agentic mode gives you 80% of cloud flexibility at 0% of the cost!**

---

## 🤔 Getting Help

- **Documentation**: See `EXAMPLES.md`, `CLAUDE.md`
- **Issues**: [GitHub Issues](https://github.com/EvolvingAgentsLabs/llmunix/issues)
- **Examples**: Check `projects/` folder
- **Architecture**: See validation reports in `projects/Project_*_verification/`

---

## 📄 License

Apache License 2.0 - see LICENSE file for details

---

## 🌟 Key Innovation

**LLMunix is the first framework to combine:**

1. **High-quality agent definitions** (from Claude)
2. **Low-cost flexible execution** (with Granite)
3. **Zero marginal cost** (local Ollama)
4. **True edge intelligence** (offline capable)

**Result**: Intelligent, adaptive AI at commodity hardware costs.

---

*Built with ❤️ by [Evolving Agents Labs](https://evolvingagentslabs.github.io)*

**Start building intelligent edge AI today!**
