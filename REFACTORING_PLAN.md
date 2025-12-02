# LLMunix Refactoring Plan: Migration to LLM-OS v3.4.0

**Created**: 2025-12-02
**Status**: COMPLETED
**Completed**: 2025-12-02
**Objective**: Transform llmunix repository to match llm-os architecture while preserving valuable unique features

---

## 1. Executive Summary

### Current State: LLMunix
- **Version**: ~1.0 (Pure Markdown OS)
- **Architecture**: Pure markdown-driven, Claude Code as runtime
- **Key Components**: 9 system agents, 5 tools, edge runtime, mobile app generation
- **Unique Features**:
  - Project-based architecture (projects/Project_name/)
  - Memory continuum system (inspired by neuroscience)
  - Edge runtime (run_follower.py, run_agentic_follower.py)
  - Mobile app generation capability
  - Pure markdown agents/tools definitions

### Target State: LLM-OS v3.4.0
- **Version**: 3.4.0 (Sentience Layer)
- **Architecture**: Hybrid (Markdown Mind + Python Kernel)
- **Key Components**: Four-layer stack (Sentience, Learning, Execution, Self-Modification)
- **Key Features**:
  - Sentience Layer (valence, homeostatic dynamics, cognitive kernel)
  - Five execution modes (CRYSTALLIZED, FOLLOWER, MIXED, LEARNER, ORCHESTRATOR)
  - PTC (Programmatic Tool Calling) - 90%+ token savings
  - Tool Search (on-demand discovery)
  - Self-modification (HOPE system)
  - SDK hooks system
  - Production-ready examples

---

## 2. Architecture Comparison

| Aspect | LLMunix (Current) | LLM-OS (Target) | Decision |
|--------|-------------------|-----------------|----------|
| **Core Engine** | Claude Code interprets markdown | Python kernel + Claude SDK | **Adopt LLM-OS** |
| **Agent Definition** | Markdown with YAML frontmatter | Markdown with YAML frontmatter | Same |
| **Execution Modes** | 3 (Learner, Deterministic, Agentic) | 5 (+ Mixed, Crystallized, Orchestrator) | **Adopt LLM-OS** |
| **Memory** | Markdown files, continuum system | Markdown traces, file-based | **Merge: Keep continuum concept** |
| **Self-Modification** | Dynamic markdown creation | HOPE (Markdown + Python crystallization) | **Adopt LLM-OS** |
| **Internal State** | Sentient State (constraints.md) | Sentience Layer (valence, cognitive kernel) | **Adopt LLM-OS** |
| **Token Optimization** | Implicit | PTC, Tool Search (explicit, 90%+ savings) | **Adopt LLM-OS** |
| **Edge Runtime** | Python (run_follower.py) | None | **KEEP from LLMunix** |
| **Mobile Generation** | React Native + on-device LLM | None | **KEEP from LLMunix** |
| **Projects Structure** | projects/Project_name/ | workspace/projects/{name}/ | **Adopt LLM-OS** |
| **Examples** | 1 scenario (Project Aorta) | 4 production examples | **Adopt LLM-OS** |

---

## 3. What to KEEP from LLMunix

### 3.1 Edge Runtime (HIGH VALUE)
**Location**: `edge_runtime/`
**Files**:
- `run_follower.py` - Deterministic execution
- `run_agentic_follower.py` - LLM-powered (Granite/Qwen)
- `requirements.txt`

**Rationale**: LLM-OS lacks offline/edge execution capability. This is a unique differentiator.

### 3.2 Mobile App Generation (MEDIUM VALUE)
**Files**:
- `system/tools/MobileAppBuilder.md`
- `system/tools/MobileAppAnalyzer.md`
- `system/agents/CodeGeneratorAgent.md`

**Rationale**: Optional output format for edge deployment. Can be integrated as examples.

### 3.3 Qwen Runtime Integration (LOW VALUE)
**Files**:
- `qwen_runtime.py`
- `.qwen/settings.json`

**Rationale**: Can be useful for local LLM execution, but may conflict with LLM-OS SDK approach.

**Decision**: Archive for now, may integrate later.

---

## 4. What to DELETE from LLMunix

### 4.1 Documentation (Replace with LLM-OS docs)
- `README.md` - Replace with LLM-OS README
- `README_ADVANCED.md` - Replace with ARCHITECTURE.md
- `IMPLEMENTATION_SUMMARY.md` - Obsolete
- `QUICKSTART_DUAL_MODE.md` - Obsolete
- `EXAMPLES.md` - Replace with examples/EXAMPLES.md
- `CLAUDE_CODE_ARCHITECTURE.md` - Obsolete
- `GEMINI.md` - Obsolete (LLM-OS uses Claude SDK)
- `QWEN.md` - Archive (may keep for edge runtime)
- `UPDATES_MARKDOWN_AND_MODEL.md` - Obsolete
- `doc/` folder - Most articles obsolete

### 4.2 System Components (Replace with LLM-OS)
- `system/agents/` - Replace with workspace/agents/
- `system/tools/` - Replace with Python plugins
- `system/infrastructure/` - Replace with llmos/kernel/
- `system/SmartLibrary.md` - Obsolete (use component registry)
- `system/SmartMemory.md` - Obsolete (use traces)
- `system/memory_log.md` - Obsolete (use workspace/memories/)
- `system/api/` - May keep for specific use cases

### 4.3 Old Structure
- `.claude/agents/` - Will be repopulated
- `scenarios/` - Replace with examples/
- `workspace/` content - Clean for fresh start
- `projects/` content - Clean for fresh start

---

## 5. Migration Steps

### Phase 1: Preparation (Current)
- [x] Analyze llmunix structure
- [x] Analyze llm-os structure
- [x] Create comparison document
- [x] Create this refactoring plan

### Phase 2: Backup & Clean
- [ ] Create backup branch of current llmunix state
- [ ] Delete old documentation files
- [ ] Delete old system/ structure
- [ ] Clean workspace/ and projects/

### Phase 3: Import LLM-OS
- [ ] Copy llmos/ Python kernel
- [ ] Copy workspace/ structure (agents, memories)
- [ ] Copy examples/ directory
- [ ] Copy ARCHITECTURE.md and README.md
- [ ] Copy .gitignore and LICENSE

### Phase 4: Integrate LLMunix Unique Features
- [ ] Add edge_runtime/ directory
- [ ] Create examples/edge-runtime/ with integration
- [ ] Archive mobile app generation for future integration

### Phase 5: Update Configuration
- [ ] Create new CLAUDE.md for LLM-OS
- [ ] Update setup scripts if needed
- [ ] Update requirements.txt

### Phase 6: Verify & Test
- [ ] Test boot process
- [ ] Test basic execution
- [ ] Test edge runtime
- [ ] Verify examples work

---

## 6. New Directory Structure (Target)

```
llmunix/                              # Renamed conceptually to LLM-OS
├── llmos/                            # Python Kernel (FROM LLM-OS)
│   ├── boot.py                       # Entry point
│   ├── kernel/                       # Core components
│   │   ├── config.py
│   │   ├── sentience.py              # NEW: Sentience Layer
│   │   ├── cognitive_kernel.py       # NEW: Cognitive Kernel
│   │   ├── mode_strategies.py
│   │   ├── agent_loader.py
│   │   ├── token_economy.py
│   │   └── ...
│   ├── memory/                       # Storage layer
│   │   ├── traces_sdk.py
│   │   ├── store_sdk.py
│   │   └── ...
│   ├── interfaces/                   # Execution interfaces
│   │   ├── dispatcher.py
│   │   ├── sdk_client.py
│   │   └── orchestrator.py
│   ├── execution/                    # NEW: Advanced Tool Use
│   │   ├── ptc.py                    # Programmatic Tool Calling
│   │   ├── tool_search.py
│   │   └── tool_examples.py
│   └── plugins/                      # Tools
│       ├── system_tools.py
│       └── generated/                # Crystallized tools (HOPE)
│
├── workspace/                        # Markdown Mind (FROM LLM-OS)
│   ├── agents/                       # Agent definitions
│   │   ├── researcher.md
│   │   ├── coder.md
│   │   └── data-analyst.md
│   ├── memories/                     # Memory storage
│   │   ├── traces/
│   │   ├── sessions/
│   │   └── facts/
│   ├── projects/                     # Project workspaces
│   └── state/                        # System state (sentience.json)
│
├── edge_runtime/                     # KEPT FROM LLMUNIX
│   ├── run_follower.py               # Deterministic execution
│   ├── run_agentic_follower.py       # LLM-powered execution
│   └── requirements.txt
│
├── examples/                         # FROM LLM-OS
│   ├── qiskit-studio/                # Quantum computing
│   ├── q-kids-studio/                # Educational
│   ├── robo-os/                      # Robot control
│   ├── demo-app/                     # Interactive showcase
│   ├── edge-runtime/                 # NEW: Edge integration example
│   └── EXAMPLES.md
│
├── ARCHITECTURE.md                   # FROM LLM-OS
├── README.md                         # FROM LLM-OS
├── CLAUDE.md                         # NEW: Adapted for LLM-OS
├── REFACTORING_PLAN.md               # This document
├── LICENSE
├── requirements.txt
└── .gitignore
```

---

## 7. CLAUDE.md Strategy

The new CLAUDE.md should:
1. Reflect LLM-OS v3.4.0 architecture (Four-Layer Stack)
2. Document the hybrid architecture (Markdown Mind + Python Kernel)
3. Include boot process for `python llmos/boot.py`
4. Document five execution modes
5. Include edge runtime documentation
6. Remove mobile app generation (archive separately)

---

## 8. Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Loss of valuable llmunix features | Medium | Backup branch, selective migration |
| Breaking existing functionality | High | Test each phase separately |
| Incomplete migration | Medium | Detailed checklist, resumable process |
| Edge runtime incompatibility | Low | Keep isolated in edge_runtime/ |

---

## 9. Success Criteria

1. **Boot Process**: `python llmos/boot.py interactive` works
2. **Execution**: Can execute goals in LEARNER and FOLLOWER modes
3. **Sentience**: Internal state persists across sessions
4. **Edge Runtime**: `python edge_runtime/run_follower.py` works
5. **Examples**: At least 2 examples (demo-app, edge-runtime) work
6. **Documentation**: README.md and ARCHITECTURE.md are accurate

---

## 10. Progress Tracking

### Phase 1: Preparation
- [x] Created REFACTORING_PLAN.md
- [x] Analyzed both codebases
- [x] Documented differences

### Phase 2: Backup & Clean
- [ ] Backup current state
- [ ] Delete old docs
- [ ] Clean directories

### Phase 3: Import
- [ ] Copy llmos/
- [ ] Copy workspace/
- [ ] Copy examples/
- [ ] Copy docs

### Phase 4: Integrate
- [ ] Keep edge_runtime/
- [ ] Create edge example

### Phase 5: Configure
- [ ] New CLAUDE.md
- [ ] Update scripts

### Phase 6: Verify
- [ ] Test all components

---

**Next Step**: Execute Phase 2 - Create backup and begin cleanup
