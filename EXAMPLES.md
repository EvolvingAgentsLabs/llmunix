# LLMunix Examples: Autonomous, Adaptive, and Evolvable Workflows

This document showcases the power of the LLMunix framework when run by manifest-aware interpreters like Claude Code or an enhanced Gemini CLI. These examples demonstrate how the system autonomously plans, evolves, and executes complex tasks.

## 🚀 Using LLMunix with Your Preferred Runtime

All examples can be run with either Claude Code or Gemini CLI following these simple workflows:

### Claude Code Workflow

**1. Boot the System**

```bash
# From the llmunix project root:
boot llmunix
```

**2. Execute a Goal**

```bash
# Direct execution
llmunix execute: "Your high-level goal here..."

# Interactive mode
llmunix execute: "Your goal here..." -i

# Simulation mode (for training data generation)
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
1.  **PLAN:** The system creates a `plan.md` using `write_file` or Claude's Write tool to outline the steps: identify sources, fetch content, analyze, and generate the briefing.
2.  **EXECUTE (Loop):** It uses `web_fetch` or Claude's WebFetch tool to get content, saves it to `workspace/fetched_content/`, and processes the text.
3.  **COMPLETE:** It writes the final `intelligence_briefing.md` to `workspace/outputs/` and notifies the user.

### Dynamic Capability Evolution (Self-Improvement)

This example shows the system creating a new tool it needs to complete a task.

#### Claude Code Example

```bash
llmunix execute: "Analyze the sentiment of the latest 5 articles on TechCrunch AI and tell me if the overall tone is positive or negative."
```

#### Gemini CLI Example

```
> Analyze the sentiment of the latest 5 articles on TechCrunch AI and tell me if the overall tone is positive or negative.
```

**Expected Behavior:**
1.  **PLAN & GAP ANALYSIS:** The system determines it lacks a specialized "sentiment analysis" capability.
2.  **EVOLVE:** It autonomously generates the Markdown definition for a new `SentimentAnalysisAgent.md` and saves it to `components/agents/`. The runtime automatically detects this new component.
3.  **EXECUTE:** After fetching the articles, it invokes its newly created agent to get the sentiment scores for each article.
4.  **COMPLETE:** It synthesizes the scores and provides a final answer.

**Runtime-Specific Implementation:**
- **Claude Code:** Uses Write tool to create the agent file, WebFetch for articles, and Task to execute the agent logic
- **Gemini CLI:** Uses `write_file` tool to create the agent file, `web_fetch` for articles, and `run_agent` tool for execution

### Hierarchical Agent Delegation

This showcases a high-level orchestration of specialized agents.

#### Claude Code Example

```bash
llmunix execute: "Create a full marketing campaign for a new product called 'SynthWave AI', an AI music tool. I need ad copy, a target audience profile, and a blog post outline."
```

#### Gemini CLI Example

```
> Create a full marketing campaign for a new product called 'SynthWave AI', an AI music tool. I need ad copy, a target audience profile, and a blog post outline.
```

**Expected Behavior:**
1.  **ORCHESTRATE:** The system creates a high-level plan (define audience, generate copy, create outline).
2.  **DELEGATE:** For each sub-task, it invokes a specialized agent (e.g., `AdCopyGeneratorAgent`, `MarketingPersonaAgent`). If a required agent doesn't exist, it creates it first using the Evolve pattern.
3.  **SYNTHESIZE:** It combines the outputs from all the specialist agents into a final `campaign_brief.md` file.

**Runtime-Specific Implementation:**
- **Claude Code:** Uses Task tool for agent delegation and Write tool for file operations
- **Gemini CLI:** Uses `run_agent` tool for delegation and `write_file` for file operations

---

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
1. **CAPABILITY CHECK:** The system finds the `LocalLLMTool.md` in `components/tools/`.
2. **TOOL EXECUTION:** Calls the appropriate tool to interact with the local Ollama instance.
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
4. **SYNTHESIS:** The primary model combines llama3.2's analysis with its own insights, providing a comprehensive review.

**Actual Output Example:**
```
✦ The llama3.2 model has provided a good initial analysis. Here's my final analysis of the code snippet function example(a, b) { return a + b / 2; }:

Potential Bugs and Considerations:

1. **Operator Precedence**: The most immediate and common issue with this snippet is operator precedence. Division (/) has higher precedence than addition (+). This means b / 2 will be calculated first, and then the result will be added to a.
   * Example: If a = 10 and b = 4, the function will return 10 + (4 / 2) = 10 + 2 = 12.
   * If the intent was `(a + b) / 2`: The code should be return (a + b) / 2; to ensure the sum of a and b is divided by 2.

2. **Input Validation / Type Coercion**: JavaScript is dynamically typed, so a and b can be of any type.
   * If a or b are not numbers, JavaScript will attempt type coercion.
   * Example: If a = "hello" and b = 4, b / 2 is 2, but "hello" + 2 results in "hello2" (string concatenation).

3. **Division by Zero**: If b is 0, the expression b / 2 will result in 0. This is generally not an error in JavaScript.

4. **Floating-Point Precision**: As with any language using standard floating-point representation (IEEE 754), arithmetic operations can sometimes lead to small precision errors.
```

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

Both runtimes implement the same memory hierarchy:

```
workspace/memory/
├── volatile/       # Cleared each session - temporary data
├── task/          # Persists for current goal - working context
└── permanent/     # Located in system/memory/permanent/ - long-term learning
```

**Memory Operations During Campaign Execution:**

1. **Initial Planning**: SystemAgent stores the execution plan:
   - **Claude Code**: Uses Write tool to create `workspace/state/plan.md`
   - **Gemini CLI**: Uses `write_file` tool with similar parameters

2. **Market Research Phase**: Memory tier usage example:
   ```
   # Volatile memory for temporary search results
   memory_store(type="volatile", key="brita_competitor_data", value="Market share: 35%...")
   
   # Task memory for campaign-specific insights
   memory_store(type="task", key="ecoflow_target_audience", value="Eco-conscious millennials...")
   ```

3. **Permanent Learning**: Key market insights preserved for future use:
   ```
   # Permanent memory creation
   memory_store(type="permanent", 
                key="SustainableWaterMarket_Trends_2025_07_05", 
                value="Key trends: decentralization, smart systems (AI/IoT)...")
   
   memory_store(type="permanent", 
                key="SustainableWaterMarket_Competitors_2025_07_05",
                value="Major players: Brita, LifeStraw, Soma...")
   ```

4. **Memory Retrieval**: For future campaigns, agents can access this knowledge:
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

### Inter-Agent Collaboration via Messaging

This demonstrates complex multi-agent workflows using the messaging system.

#### Claude Code Example

```bash
llmunix execute: "Our competitor just announced a major product update. I need a rapid response strategy within 2 hours."
```

#### Gemini CLI Example

```
> Our competitor just announced a major product update. 
> I need a rapid response strategy within 2 hours.
```

**Expected Behavior:**
1. **Crisis Alert**: SystemAgent broadcasts urgent message:
   ```
   broadcast_message(
     message="URGENT: Competitor announcement requires immediate response. All agents standby.",
     topic="crisis_response"
   )
   ```
2. **Parallel Execution**: Multiple agents work simultaneously:
   - MarketAnalyst fetches competitor details
   - ContentWriter drafts response options
   - CEO reviews and decides strategy
3. **Message Flow**:
   ```
   # Analyst to CEO
   send_message(
     to="CEOAgent",
     message="Competitor analysis complete. They're targeting our core market with 20% lower pricing.",
     priority="urgent"
   )
   
   # CEO to Writer
   send_message(
     to="ContentWriterAgent", 
     message="Draft announcement emphasizing our superior quality and support. Due in 30 mins.",
     priority="urgent"
   )
   ```
4. **Coordination**: Agents check messages frequently during crisis:
   ```
   check_messages(agent="ContentWriterAgent", priority="urgent")
   ```

## 🔬 Advanced Scenarios

These examples demonstrate the system's more sophisticated adaptive capabilities.

### Adaptive Execution & Constraint Management

```
> URGENT: Analyze this 50-page legal document for risks in under 10 minutes. Focus only on liability and termination clauses.
```

**Expected Behavior:**
*   The system parses the "URGENT" and "10 minutes" cues from the prompt.
*   It immediately calls `write_file` to update `workspace/state/constraints.md` with new rules like `priority: speed_and_clarity` and `max_execution_time: 600`.
*   It then proceeds with the task, altering its plan to prioritize speed over comprehensive analysis, for example by using a more focused prompt for its `summarize` tool calls.

### Memory-Driven Task Improvement

```
> Research the latest advancements in quantum computing.
```
*(After a previous run where the agent used slow or unreliable sources...)*

**Expected Behavior:**
*   The system's first action is to call `read_file` on `system/memory_log.md` to review past experiences tagged with "quantum computing".
*   It finds a log entry noting: "Fetching from `slow-science-journal.com` timed out. `fast-arxiv.com` was more reliable."
*   In its new plan, it intelligently prioritizes `fast-arxiv.com` and avoids the previously problematic source, demonstrating learning from experience.

### Complex Tool Orchestration

This example shows how virtual tools can work together in sophisticated workflows.

```
> Create a comprehensive competitor analysis for our new AI music app. 
> Use web search for public info, consult llama3.2 for market insights, 
> and generate visualizations of the competitive landscape.
```

**Expected Behavior:**
1. **MULTI-TOOL PLANNING:** Creates a plan involving multiple tools:
   - `web_fetch` for competitor websites
   - `google_search` for market data
   - `LocalLLMTool` for analysis via llama3.2
   - A newly created `VisualizationAgent` for charts
2. **PARALLEL EXECUTION:** Runs multiple tools concurrently when possible
3. **DATA FLOW:** Passes outputs between tools, e.g., web data → llama3.2 → visualization
4. **ERROR RESILIENCE:** If one tool fails (e.g., web fetch quota), adapts by using alternatives

### Virtual Tool Creation On-Demand

This demonstrates the system creating new tools during execution.

```
> I need to analyze 100 CSV files for anomalies. Create whatever tools you need to process them efficiently.
```

**Expected Behavior:**
1. **CAPABILITY GAP:** Realizes no CSV processing tool exists
2. **TOOL GENERATION:** Creates `CSVAnalyzer.md` with:
   ```markdown
   #### analyze_csv
   `sh`
   ```sh
   #!/bin/bash
   FILE_PATH=$(echo "$GEMINI_TOOL_ARGS" | jq -r .path)
   # Use awk/sed for CSV processing
   # Detect anomalies based on statistical analysis
   ```
   ```
3. **BATCH PROCESSING:** Uses the new tool to process all files
4. **OPTIMIZATION:** May create additional tools for parallel processing

## Key Insights

These examples illustrate the transformative power of the manifest-driven virtual tool system:

1. **Immediate Extensibility**: New capabilities can be added by writing Markdown
2. **Tool Composition**: Complex workflows emerge from simple tool combinations  
3. **Runtime Evolution**: The system adapts its toolset during execution
4. **Security & Transparency**: All tool logic is auditable and sandboxed
5. **Multi-Model Orchestration**: Seamlessly integrate external AI services

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