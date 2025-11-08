# Project: Habit Tracker Demo

## Purpose

This project demonstrates LLMunix's mobile app generation capabilities. It shows how LLMunix:
1. Executes a primary CLI workflow (habit tracking analysis)
2. Optionally generates a mobile app from the results
3. Classifies the app as deterministic (no LLM needed)
4. Bundles a complete React Native deployment package

## User Goal

> "Create a mobile app that tracks daily habits and shows progress over time"

## Workflow

### Phase 1: Primary CLI Execution (Default LLMunix Behavior)

**SystemAgent orchestrates:**
1. Analyze habit tracking requirements
2. Design data model and features
3. Generate CLI outputs (analysis, design docs)
4. Results stored in `output/` directory

**CLI Outputs:**
- `output/requirements.md` - Detailed requirements analysis
- `output/data_model.md` - Habit tracking data structures
- `output/features.md` - Feature list and priorities

### Phase 2: Mobile App Generation (Optional)

**Triggered by "mobile app" keyword in user goal**

**SystemAgent detects and delegates:**
1. Invokes `CodeGeneratorAgent` with project context
2. CodeGeneratorAgent reads `output/` files
3. Generates complete React Native codebase
4. Invokes `MobileAppAnalyzer` for classification
5. Invokes `MobileAppBuilder` for bundling

**Mobile App Classification:**
- **Type**: Deterministic (no LLM required)
- **Reason**: All logic is CRUD operations and data visualization
- **Size**: ~15MB (code + assets only)

**Mobile App Outputs:**
- `mobile_app/manifest.json` - App metadata
- `mobile_app/src/` - React Native source code
- `mobile_app/package.json` - Dependencies
- `mobile_app/README.md` - Setup instructions

## Project Structure

```
projects/Project_habit_tracker_demo/
├── README.md                    # This file
├── input/                       # User requirements (optional)
│   └── user_requirements.md
├── output/                      # Primary CLI results
│   ├── requirements.md
│   ├── data_model.md
│   └── features.md
├── mobile_app/                  # Optional mobile app output
│   ├── manifest.json
│   ├── package.json
│   ├── src/
│   │   ├── screens/
│   │   ├── components/
│   │   └── services/
│   └── README.md
├── components/                  # Project-specific components (if needed)
│   ├── agents/
│   └── tools/
├── memory/                      # Learning and history
│   ├── short_term/
│   └── long_term/
└── workspace/                   # Execution state
    └── state/
```

## How to Run This Example

### Option 1: Using llmunix Command

```bash
llmunix execute: "Create a mobile app that tracks daily habits and shows progress over time"
```

**Expected Behavior:**
1. SystemAgent creates/verifies project structure
2. Executes primary workflow (requirements analysis)
3. Detects "mobile app" keyword
4. Generates React Native app
5. Outputs both CLI results and mobile app

### Option 2: Manual Invocation

```bash
# 1. Boot LLMunix
boot llmunix

# 2. Execute via SystemAgent
"Invoke system-agent to execute: Create a mobile app that tracks daily habits and shows progress over time"
```

## Expected Outputs

### CLI Results (Primary)

**output/requirements.md** (~200 lines):
- User requirements analysis
- Feature breakdown
- Data model design
- UI/UX considerations

**output/data_model.md** (~100 lines):
- Habit entity schema
- Progress tracking model
- Reminder system design

**output/features.md** (~150 lines):
- Feature list with priorities
- Implementation complexity
- User stories

### Mobile App (Optional)

**mobile_app/** (~47 files, 15MB):
- Complete React Native codebase
- TypeScript types
- Navigation setup
- CRUD services
- Progress charts
- Dark mode support

## Classification Details

**MobileAppAnalyzer Output:**

```yaml
classification: deterministic
confidence: 0.95
reason: "All logic is CRUD operations and data visualization, no AI reasoning needed"

features_deterministic:
  - Add/edit/delete habits
  - Mark habits as complete
  - Calculate streaks and statistics
  - Display progress charts
  - Set reminders

features_requiring_llm: []

llm_recommended: none

app_size_estimate:
  code_and_assets_mb: 12
  llm_model_mb: 0
  total_mb: 12

performance_estimate:
  response_time_ms: 50
  offline_capable: true
```

## Comparison: Deterministic vs Agentic

**This Example (Deterministic):**
- App size: 15MB
- No LLM required
- Instant responses
- Rule-based logic
- CRUD operations

**Agentic Alternative (Hypothetical):**
```
User Goal: "Create a mobile personal trainer app that adapts workouts to my progress"
- App size: 635MB (15MB code + 600MB Qwen3-0.6B)
- LLM required for workout generation
- 1-2s response time for AI features
- Adaptive behavior
- Natural language understanding
```

## Key Learnings

### LLMunix Philosophy Preserved

✅ **Primary output**: CLI results in `output/`
✅ **Optional output**: Mobile app in `mobile_app/`
✅ **Agent creation**: Project-specific agents created on-demand
✅ **Memory learning**: All interactions logged to `memory/`
✅ **Project organization**: Clean structure maintained

### Mobile App Generation Benefits

✅ **No code required**: User just describes goal
✅ **Production-ready**: Complete React Native app
✅ **Intelligent classification**: 90% deterministic (small), 10% agentic (large)
✅ **Model selection**: Qwen3-0.6B or Granite 4.0 H-1B based on needs
✅ **Deployment package**: Ready to run on iOS/Android

### Workflow Insights

1. **Detection**: "mobile app" keyword triggers optional generation
2. **Context**: Project outputs inform app design
3. **Classification**: Analyzer prevents unnecessary LLM bundling
4. **Optimization**: Deterministic apps stay lightweight (<20MB)
5. **Flexibility**: Agentic apps get appropriate model (600MB-1.5GB)

## Next Steps

After reviewing this example:

1. **Test**: Run the workflow and verify outputs
2. **Deploy**: Follow `mobile_app/README.md` to run the app
3. **Extend**: Try agentic example (personal trainer, study assistant)
4. **Learn**: Review `memory/long_term/` for learnings

## Related Documentation

- **SystemAgent**: `system/agents/SystemAgent.md` - Orchestration details
- **CodeGeneratorAgent**: `system/agents/CodeGeneratorAgent.md` - App generation process
- **MobileAppAnalyzer**: `system/tools/MobileAppAnalyzer.md` - Classification logic
- **MobileAppBuilder**: `system/tools/MobileAppBuilder.md` - Bundling process
- **SmartLibrary**: `system/SmartLibrary.md` - Complete component registry

## Analysis Reference

Full research and design documents:
- `projects/Project_on_device_wabi_analysis/output/granite_qwen_comparison.md` - Model selection research
- `projects/Project_on_device_wabi_analysis/output/CODE_GENERATION_ARCHITECTURE.md` - Architecture design
- `projects/Project_on_device_wabi_analysis/output/EXECUTIVE_SUMMARY.md` - Complete analysis

---

**Project Type**: Example / Demo
**Status**: Ready to Execute
**Complexity**: Medium (4 screens, deterministic)
**Expected Execution Time**: 2-3 minutes
**Expected Output**: CLI results + Mobile app (~15MB)
