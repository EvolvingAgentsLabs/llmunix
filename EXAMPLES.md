# LLMunix Examples: Autonomous, Adaptive, and Evolvable Workflows

This document showcases the power of the LLMunix framework when run by manifest-aware interpreters like Claude Code or Gemini CLI. These examples demonstrate how the system autonomously plans, adapts, and executes complex tasks through pure markdown definitions.

## What Makes LLMunix Unique

* **Pure Markdown Architecture**: Everything is defined in markdown - agents, tools, and workflows
* **Runtime Flexibility**: Works seamlessly with both Claude Code and Gemini CLI
* **Self-Improving System**: Creates new tools and agents as needed during execution
* **Memory-Driven Intelligence**: Learns from past executions to improve future performance
* **Adaptive Workflow**: Automatically adjusts execution based on constraints and requirements
* **Native Sub-Agent Architecture**: In Claude Code, leverages isolated context windows for specialized tasks

## 🚀 Using LLMunix with Your Preferred Runtime

All examples can be run with either Claude Code or Gemini CLI following these simple workflows. Choose the runtime that best fits your needs - both provide the full power of LLMunix's pure markdown architecture:

### Claude Code Workflow

**1. Boot the System**

```bash
# From the llmunix project root:
boot llmunix
```

This prepares the environment and makes all sub-agents discoverable to Claude Code.

**2. Execute a Goal**

```bash
# Direct execution - for single tasks
llmunix execute: "Your high-level goal here..."

# Interactive mode - for conversational workflows
llmunix execute: "Your goal here..." -i

# Simulation mode - for training data generation
llmunix simulate: "Your goal here..."
```

### Gemini CLI Workflow

**1. Boot the System (Run Once per Session)**

```bash
# From the llmunix project root:
./llmunix-boot
```

**2. Execute a Goal**

```bash
# Start Gemini CLI
gemini

# At the prompt, enter your goal
> Your high-level goal here...
```

Both runtimes provide similar capabilities through different interfaces. All examples below work with either runtime, with implementation differences noted.

---

## 🎯 Core Capability Examples

### Autonomous Research & Analysis

This demonstrates the system's ability to plan a multi-step research task, use tools to gather information, and synthesize a report.

#### Claude Code Example

```bash
llmunix execute: "Monitor 5 tech news sources (TechCrunch, Ars Technica, Hacker News, MIT Tech Review, Wired), extract trending topics in AI, and generate an intelligence briefing summarizing the key themes."
```

#### Gemini CLI Example

```
> Monitor 5 tech news sources (e.g., TechCrunch, Ars Technica), extract trending topics in AI, and generate an intelligence briefing summarizing the key themes.
```

**Expected Behavior:**

1. **PLAN:** 
   - The system creates a detailed execution plan
   - **Claude Code:** Uses Write tool to create `workspace/state/plan.md`
   - **Gemini CLI:** Uses `write_file` to create the plan
   - Plan outlines steps: identify sources, fetch content, analyze, and generate the briefing

2. **EXECUTE (Loop):** 
   - **Claude Code:** Uses WebFetch tool to get content from each source
   - **Gemini CLI:** Uses `web_fetch` tool for each source
   - Saves fetched content to `workspace/fetched_content/`
   - Processes text to identify trending AI topics

3. **COMPLETE:** 
   - Writes the final `intelligence_briefing.md` to `workspace/outputs/`
   - Provides summary of key themes identified across sources
   - Notifies user of task completion

### Dynamic Capability Evolution (Self-Improvement)

This example shows the system creating a new sub-agent it needs to complete a task.

#### Claude Code Example

```bash
llmunix execute: "Analyze the sentiment of the latest 5 articles on TechCrunch AI and tell me if the overall tone is positive or negative."
```

#### Gemini CLI Example

```
> Analyze the sentiment of the latest 5 articles on TechCrunch AI and tell me if the overall tone is positive or negative.
```

**Expected Behavior:**

1. **PLAN & GAP ANALYSIS:** 
   - System determines it lacks a specialized "sentiment analysis" capability
   - Identifies this as a critical gap for completing the task
   - Plans to create a new component before proceeding

2. **EVOLVE:** 
   - **Claude Code:** Creates `sentiment-analyzer-agent.md` with YAML frontmatter:
   ```markdown
   ---
   name: sentiment-analyzer-agent
   description: Analyzes text content to determine sentiment polarity (positive, negative, neutral) with scoring and evidence extraction.
   tools: Read, Write, WebFetch
   ---
   # System Prompt: SentimentAnalyzerAgent
   ...
   ```
   - **Gemini CLI:** Uses `write_file` to create the agent definition
   - The runtime automatically detects this new component
   - Agent includes scoring methodology and sentiment classification rules

3. **EXECUTE:** 
   - Fetches articles from TechCrunch AI section
   - **Claude Code:** Uses Task tool to invoke the new sentiment-analyzer-agent
   - **Gemini CLI:** Uses `run_agent` to invoke the new agent
   - Assigns sentiment scores using consistent methodology

4. **COMPLETE:** 
   - Synthesizes individual scores into an overall sentiment evaluation
   - Provides evidence-based assessment of tech industry sentiment
   - Saves both component scores and final analysis

**Runtime-Specific Implementation:**
- **Claude Code:** Uses Write tool to create the sub-agent file with YAML frontmatter, WebFetch for articles, and Task tool to invoke the sub-agent in an isolated context
- **Gemini CLI:** Uses `write_file` tool to create the agent file, `web_fetch` for articles, and `run_agent` tool for execution

### Hierarchical Agent Delegation

This showcases a high-level orchestration of specialized sub-agents.

#### Claude Code Example

```bash
llmunix execute: "Create a full marketing campaign for a new product called 'SynthWave AI', an AI music tool. I need ad copy, a target audience profile, and a blog post outline."
```

#### Gemini CLI Example

```
> Create a full marketing campaign for a new product called 'SynthWave AI', an AI music tool. I need ad copy, a target audience profile, and a blog post outline.
```

**Expected Behavior:**

1. **ORCHESTRATE:** 
   - Creates a high-level plan for the marketing campaign
   - Divides work into specialized domains: audience analysis, ad copy, blog content
   - Establishes coordination workflow and deliverable format

2. **DELEGATE:** 
   - **Claude Code:** Uses Task tool with appropriate sub-agent types:
   ```
   Task(
     description="Create target audience profile",
     prompt="Analyze the market for SynthWave AI music tool and create a detailed target audience profile...",
     subagent_type="market-analyst-agent"
   )
   ```
   - **Gemini CLI:** Uses `run_agent` for each specialized component
   - Invokes specialized agents (e.g., `ad-copy-generator-agent`, `market-analyst-agent`)
   - Creates any missing agents using the Evolve pattern when needed

3. **SYNTHESIZE:** 
   - Collects outputs from all specialist sub-agents
   - Ensures consistency across all campaign elements
   - **Claude Code:** Uses Write tool to create final `campaign_brief.md` 
   - **Gemini CLI:** Uses `write_file` for the final deliverable
   - Provides a cohesive marketing strategy incorporating all components

**Runtime-Specific Implementation:**
- **Claude Code:** Uses Task tool for sub-agent delegation with isolated contexts and Write tool for file operations
- **Gemini CLI:** Uses `run_agent` tool for delegation and `write_file` for file operations

## 🔄 Sub-Agent Architecture in Claude Code

Claude Code's native sub-agent architecture provides significant advantages for LLMunix:

### Context Isolation

Each sub-agent operates in its own isolated context window, which provides several benefits:

1. **Clean Slate Processing**: Sub-agents start with a fresh context for each task, preventing contamination from prior tasks
2. **Specialized Focus**: Each sub-agent can focus exclusively on its domain without unrelated information
3. **Parallel Processing**: Multiple sub-agents can work simultaneously on different aspects of a complex task

```bash
# Example: Run multiple specialized agents in parallel
llmunix execute: "Research the AI market, draft a business plan, and create a pitch deck for a new AI startup."
```

In this example, the system-agent delegates to three specialized sub-agents that work in parallel:
- research-analyst-agent gathers market data
- business-planner-agent creates the business plan
- presentation-designer-agent builds the pitch deck

Each works with a clean context specifically tailored to its task.

### Tool Access Control

Sub-agents can be granted access to specific tools based on their function:

```markdown
---
name: security-auditor-agent
description: Performs security audits of code repositories and identifies potential vulnerabilities
tools: Read, Grep, Glob, Bash
---
```

This security-focused agent has read-only tools and can't modify files, while:

```markdown
---
name: code-fixer-agent
description: Implements fixes for identified security vulnerabilities in code
tools: Read, Write, Edit, MultiEdit, Grep, Glob
---
```

This agent has write access to implement fixes. The SystemAgent can coordinate between them for a secure workflow.

### Dynamic Discovery

One of the most powerful features is the ability to create new sub-agents during execution:

```bash
llmunix execute: "I need a specialized agent for analyzing healthcare data. Create one and use it to analyze patient treatment outcomes."
```

The system-agent will:
1. Create a new healthcare-analyst-agent.md file with appropriate YAML frontmatter
2. Write it to the .claude/agents/ directory
3. The sub-agent becomes immediately available for use
4. Invoke it through the Task tool to analyze the healthcare data

### Memory Integration with Sub-Agents

The SystemAgent acts as the memory manager for sub-agents:

1. **Before Delegation**:
   ```
   # SystemAgent queries memory for relevant context
   [Reads from memory_log.md to find insights about healthcare data analysis]
   
   # Then includes this context when invoking the sub-agent
   Task(
     description="Analyze healthcare data",
     prompt="Based on our previous analysis methods that were successful (summarized here: [context from memory]), analyze this patient treatment data...",
     subagent_type="healthcare-analyst-agent"
   )
   ```

2. **After Sub-Agent Execution**:
   ```
   # SystemAgent captures the sub-agent's insights and stores them in memory
   [Takes results from healthcare-analyst-agent and writes key findings to memory_log.md]
   ```

This memory orchestration ensures that knowledge is preserved across sub-agent executions, even though each sub-agent operates in its own isolated context.

### External LLM Integration (Multi-Model Workflows)

This example demonstrates using local LLMs alongside the primary model for specialized tasks.

#### Claude Code Example

```bash
llmunix execute: "Please analyze the following code snippet 'function example(a, b) { return a + b / 2; }' for potential bugs. First, get a second opinion from the llama3.2 model running on my local Ollama, then provide your final analysis."
```

#### Gemini CLI Example

```
> Please analyze the following code snippet `function example(a, b) { return a + b / 2; }` for potential bugs. 
> First, get a second opinion from the llama3.2 model, then provide your final analysis. 
> Use the Ollama that is running in my local machine
```

**Expected Behavior:**

1. **CAPABILITY CHECK:** 
   - System finds the `LocalLLMTool.md` in `components/tools/`
   - Verifies Ollama is running and accessible
   - Confirms llama3.2 model is available

2. **TOOL EXECUTION:** 
   - **Claude Code**: Uses Bash tool to call the local Ollama API
   - **Gemini CLI**: Uses `run_tool` with `LocalLLMTool.md` and parameters:
   ```json
   {
     "model": "llama3.2",
     "prompt": "Please analyze this code for bugs: function example(a, b) { return a + b / 2; }"
   }
   ```

3. **LLM RESPONSE:** The llama3.2 model identifies several issues:
   - **Operator precedence**: Division happens before addition (b/2 is calculated first)
   - **No input validation**: Missing type checks for parameters
   - **Division by zero**: No check if b could be zero
   - **Floating point precision**: Potential rounding errors

4. **SYNTHESIS:** 
   - Primary model combines llama3.2's analysis with its own insights
   - Provides a comprehensive review of the code
   - Prioritizes issues by severity and likelihood
   - Suggests specific code improvements

**Key Benefits:**
- **Model specialization**: Use models optimized for specific tasks
- **Local processing**: Keep sensitive code on-premise
- **Cost optimization**: Use smaller models for routine tasks
- **Consensus building**: Get multiple perspectives on critical decisions

### Memory-Driven Learning System

This example shows how agents use the multi-tier memory system during campaign execution.

#### Claude Code Example

```bash
llmunix execute: "Create a comprehensive marketing campaign for 'EcoFlow Pro' - a new sustainable water purification device. Include market research, targeting strategy, and creative assets."
```

#### Gemini CLI Example

```
> Create a comprehensive marketing campaign for "EcoFlow Pro" - a new sustainable water purification device.
```

**Multi-Tier Memory Architecture:**

Both Claude Code and Gemini CLI implement the same memory hierarchy:

```
workspace/memory/
├── volatile/       # Cleared each session - temporary data
├── task/          # Persists for current goal - working context
└── permanent/     # Located in system/memory/permanent/ - long-term learning
```

This consistent memory structure enables seamless runtime switching while preserving learning continuity.

**Memory Operations During Campaign Execution:**

1. **Initial Planning**: 
   - SystemAgent stores the comprehensive execution plan
   - **Claude Code**: Uses Write tool to create `workspace/state/plan.md`
   - **Gemini CLI**: Uses `write_file` tool with similar parameters
   - Both include metadata like estimated completion time and resource needs

2. **Market Research Phase**: 
   - **Claude Code Example**:
   ```bash
   # Using Task tool to store volatile memory
   "Store market research results for temporary use"
   ```
   
   - **Gemini CLI Example**:
   ```
   # Volatile memory for temporary search results
   memory_store(type="volatile", key="brita_competitor_data", value="Market share: 35%...")
   
   # Task memory for campaign-specific insights
   memory_store(type="task", key="ecoflow_target_audience", value="Eco-conscious millennials...")
   ```

3. **Permanent Learning**: 
   - Key market insights preserved for future use
   - **Claude Code**: Uses Write tool to create files in system/memory/permanent/
   - **Gemini CLI**: Uses memory API:
   ```
   # Permanent memory creation
   memory_store(type="permanent", 
                key="SustainableWaterMarket_Trends_2025_07_05", 
                value="Key trends: decentralization, smart systems (AI/IoT)...")
   
   memory_store(type="permanent", 
                key="SustainableWaterMarket_Competitors_2025_07_05",
                value="Major players: Brita, LifeStraw, Soma...")
   ```

4. **Memory Retrieval**: 
   - For future campaigns, agents access this knowledge
   - **Claude Code**: Uses Read tool to access memory files
   - **Gemini CLI**: Uses memory API:
   ```
   # Search across memory tiers
   memory_search(pattern="water purification market")
   
   # Recall specific competitor analysis
   memory_recall(type="permanent", key="SustainableWaterMarket_Competitors_2025_07_05")
   ```

**Key Benefits:**
- **Knowledge Accumulation**: Market insights persist beyond single execution
- **Contextual Awareness**: Agents reference past analyses for better decisions
- **Continuous Improvement**: Each campaign builds on previous learnings
- **Reduced Redundancy**: Avoid repeating research on subsequent tasks

## 🔬 Advanced Scenarios

These examples demonstrate the system's more sophisticated adaptive capabilities. Each scenario showcases how LLMunix can intelligently respond to complex requirements, learn from past experiences, and dynamically evolve its toolset to meet challenges.

### Adaptive Execution & Constraint Management

#### Claude Code Example

```bash
llmunix execute: "URGENT: Analyze this 50-page legal document for risks in under 10 minutes. Focus only on liability and termination clauses."
```

#### Gemini CLI Example

```
> URGENT: Analyze this 50-page legal document for risks in under 10 minutes. Focus only on liability and termination clauses.
```

**Expected Behavior:**

1. **Constraint Detection**: The system parses the "URGENT" and "10 minutes" cues from the prompt.

2. **Constraint Update**: 
   - **Claude Code**: Uses Write tool to update `workspace/state/constraints.md` with new rules
   - **Gemini CLI**: Uses `write_file` to update constraints
   - New constraints include: `priority: speed_and_clarity` and `max_execution_time: 600`

3. **Adaptive Planning**:
   - Creates a highly focused execution plan
   - Prioritizes speed over comprehensive analysis
   - Limits scope to only liability and termination clauses

4. **Execution Adaptation**:
   - **Claude Code**: Uses more concise prompts with WebFetch and Task tools
   - **Gemini CLI**: Uses focused prompts for `summarize` tool calls
   - Skips formatting and visualization steps that would take extra time
   - Implements parallel processing where possible

### Memory-Driven Task Improvement

#### Claude Code Example

```bash
llmunix execute: "Research the latest advancements in quantum computing."
```

#### Gemini CLI Example

```
> Research the latest advancements in quantum computing.
```
*(After a previous run where the agent used slow or unreliable sources...)*

**Expected Behavior:**

1. **Memory Consultation**:
   - **Claude Code**: Uses Read tool to check `system/memory_log.md`
   - **Gemini CLI**: Uses `read_file` to review past experiences
   - Looks specifically for entries tagged with "quantum computing"

2. **Memory Analysis**:
   - Finds log entries with valuable insights such as:
     - "Fetching from `slow-science-journal.com` timed out. `fast-arxiv.com` was more reliable."
     - "Google Scholar provided more relevant results than general search."
     - "Papers from last 6 months contained most significant breakthroughs."

3. **Adaptive Planning**:
   - Creates research plan that incorporates these learnings
   - Intelligently prioritizes `fast-arxiv.com` over slower sources
   - Focuses on papers from the last 6 months
   - Uses Google Scholar as primary search tool

4. **Execution Improvement**:
   - Completes research 40% faster than previous run
   - Discovers more relevant information
   - Updates memory with new reliable sources for future reference

### Complex Tool Orchestration

This example shows how virtual tools can work together in sophisticated workflows.

#### Claude Code Example

```bash
llmunix execute: "Create a comprehensive competitor analysis for our new AI music app. Use web search for public info, consult llama3.2 for market insights, and generate visualizations of the competitive landscape."
```

#### Gemini CLI Example

```
> Create a comprehensive competitor analysis for our new AI music app. 
> Use web search for public info, consult llama3.2 for market insights, 
> and generate visualizations of the competitive landscape.
```

**Expected Behavior:**

1. **MULTI-TOOL PLANNING:** 
   - Creates a plan involving multiple specialized tools
   - **Claude Code**: Uses multiple tool calls in parallel
   - **Gemini CLI**: Uses various virtual tools defined in markdown:
     - `web_fetch` for competitor websites
     - `google_search` for market data
     - `LocalLLMTool` for analysis via llama3.2
     - A newly created `VisualizationAgent` for charts

2. **PARALLEL EXECUTION:** 
   - Runs multiple tools concurrently when possible
   - Coordinates tool execution for maximum efficiency
   - Manages dependencies between tool operations

3. **DATA FLOW:** 
   - Passes outputs between tools systematically
   - Creates pipelines: web data → llama3.2 → visualization
   - Handles data transformations between tool handoffs

4. **ERROR RESILIENCE:** 
   - If one tool fails (e.g., web fetch quota), adapts by using alternatives
   - Implements retry logic with exponential backoff
   - Provides graceful degradation when tools are unavailable

### Virtual Tool Creation On-Demand

This demonstrates the system creating new tools during execution.

#### Claude Code Example

```bash
llmunix execute: "I need to analyze 100 CSV files for anomalies. Create whatever tools you need to process them efficiently."
```

#### Gemini CLI Example

```
> I need to analyze 100 CSV files for anomalies. Create whatever tools you need to process them efficiently.
```

**Expected Behavior:**

1. **CAPABILITY GAP:** 
   - System analyzes the task and available tools
   - Realizes no CSV processing tool exists in current library
   - Determines requirements for efficient CSV analysis

2. **TOOL GENERATION:** 
   - **Claude Code**: Creates a new sub-agent using Write tool:
   ```markdown
   ---
   name: csv-analyzer-agent
   description: Specialized agent for processing and analyzing CSV files to detect anomalies and patterns
   tools: Read, Write, Bash
   ---
   # System Prompt: CSVAnalyzerAgent
   ...
   ```
   - **Gemini CLI**: Creates `CSVAnalyzer.md` with tool implementation
   - Registers new tool/agent in component registry
   - Tool includes anomaly detection algorithms

3. **BATCH PROCESSING:** 
   - Uses the new tool to process all 100 CSV files
   - Implements batching strategy for efficiency
   - Tracks progress and aggregates results

4. **OPTIMIZATION:** 
   - May create additional tools for parallel processing
   - Implements worker pool for distributed processing
   - Adds results aggregation and visualization tools

## Key Insights

These examples illustrate the transformative power of the manifest-driven virtual tool system:

1. **Immediate Extensibility**: New capabilities can be added by writing Markdown
2. **Tool Composition**: Complex workflows emerge from simple tool combinations  
3. **Runtime Evolution**: The system adapts its toolset during execution
4. **Security & Transparency**: All tool logic is auditable and sandboxed
5. **Multi-Model Orchestration**: Seamlessly integrate external AI services
6. **Context Isolation**: Sub-agents work in dedicated contexts for optimal performance

### 🏢 Virtual Company Demo

For a comprehensive demonstration of memory and messaging in action, see the **Virtual Company Demo** at `examples/virtual_company_demo.md`. This showcase features:

- **Four Specialized Agents**: CEO, Market Analyst, Content Writer, and QA Reviewer
- **Complete Marketing Campaign**: From market research to final deliverables
- **Memory Evolution**: Watch how agents learn and improve
- **Message Choreography**: See real-time agent coordination
- **Business Value**: Produces professional-quality outputs

Run the demo with:
```bash
./llmunix-boot
gemini
> Create a comprehensive marketing campaign for "EcoFlow Pro" - a new sustainable water purification device.
```

## 📊 Case Study: EcoFlow Pro Campaign Analysis

The EcoFlow Pro marketing campaign execution provides valuable insights into the framework's capabilities and current limitations:

### Execution Flow Analysis

1. **Initial Planning**: SystemAgent created a comprehensive 4-phase plan stored in `workspace/state/plan.md`
   - Phase 1: Research & Analysis (Market Analyst, Trending Topic Extractor)
   - Phase 2: Strategy & Positioning (Intelligence Briefing)
   - Phase 3: Content Creation (Ad Copy Generator, Content Writer)
   - Phase 4: Review & Finalization (QA Review, Research Report)

2. **Agent Delegation Challenges**:
   - **Tool Registration**: Each agent execution registered virtual tools, causing warnings about duplicates
   - **Output Consistency**: Agents didn't consistently save outputs to expected file locations
   - **SystemAgent Intervention**: Required manual intervention to correct file paths and consolidate outputs

3. **Memory System Usage**:
   - **Permanent Memory**: Market trends and competitor analysis were stored for future use
   - **Task Memory**: Plan and intermediate results were maintained throughout execution
   - **Volatile Memory**: Temporary data was used for processing but not preserved

4. **Communication System Issues**:
   - **Message Delivery**: The `check_messages` tool encountered errors with directory handling
   - **Agent Coordination**: Agents attempted to communicate but messaging was unreliable
   - **Fallback Behavior**: SystemAgent had to manually coordinate instead of relying on messages

### Key Observations

**Strengths Demonstrated**:
- **Resilience**: SystemAgent successfully completed the task despite tool failures
- **Adaptability**: When agents failed to save outputs correctly, SystemAgent intervened
- **Quality Output**: Final deliverables were professional and comprehensive
- **Memory Persistence**: Market insights were preserved for future campaigns

**Areas for Improvement**:
- **Tool Reliability**: Virtual tool execution needs better error handling
- **Output Standardization**: Agents need clearer contracts for file outputs
- **Message System**: The messaging infrastructure requires debugging
- **Agent Autonomy**: Reduce need for SystemAgent manual interventions

### Technical Insights

1. **Virtual Tool Architecture**:
   - Tools are registered dynamically from `GEMINI.md` manifest
   - Each agent execution creates a new Gemini subprocess
   - Tool registration happens per-subprocess, causing duplicate warnings

2. **File System Challenges**:
   - Relative vs absolute path confusion in agent implementations
   - Inconsistent output file naming conventions
   - Need for better workspace organization standards

3. **Communication Patterns**:
   - Agents attempted peer-to-peer communication
   - Broadcast messages for system-wide coordination
   - Priority-based message handling for urgent tasks

### Recommendations for Future Development

1. **Standardize Agent Contracts**: Define clear input/output specifications
2. **Improve Error Handling**: Add retry logic and fallback strategies
3. **Fix Messaging System**: Debug the `check_messages` implementation
4. **Enhance Tool Registry**: Prevent duplicate registrations across subprocesses
5. **Add Monitoring**: Implement execution tracing and performance metrics

The manifest-driven architecture provides a flexible and powerful foundation for creating truly autonomous, adaptive, and self-improving AI systems that can leverage the best tools and models for each task.