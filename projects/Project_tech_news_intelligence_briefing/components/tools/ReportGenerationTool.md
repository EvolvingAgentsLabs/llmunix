# Report Generation Tool

**Tool Name:** report-generation-tool
**Tool Type:** document-creation
**Project:** Project_tech_news_intelligence_briefing
**Maps To:** Claude Code Write tool

---

## Purpose
Generate structured, professional intelligence briefings and reports from analyzed data with consistent formatting and organization.

## Parameters
- **file_path** (required): Destination path for generated report
- **content** (required): Report content in markdown format
- **template** (optional): Report template to use

## Capabilities
- Create well-structured markdown documents
- Apply consistent formatting and styling
- Generate executive summaries
- Create data visualizations (tables, lists, rankings)
- Include citations and references
- Support multiple report formats

## Claude Code Integration
```
TOOL_CALL: Write
{
  "file_path": "/home/user/llmunix/projects/Project_tech_news_intelligence_briefing/output/intelligence_briefing_2025-11-04.md",
  "content": "[FORMATTED_REPORT_CONTENT]"
}
```

## Report Templates

**Intelligence Briefing Template:**
```markdown
# Tech News Intelligence Briefing
**Week of [Date Range]**

## Executive Summary
[Key developments in 200-300 words]

## Top Trending Topics
[Ranked analysis of 10-15 topics]

## Emerging Patterns
[Cross-source pattern analysis]

## Source Intelligence
[Per-source coverage breakdown]

## Strategic Implications
[Actionable insights]

## Methodology
[Sources and approach]
```

**Topic Analysis Template:**
```markdown
# Topic: [Topic Name]

**Category:** [Technology/Business/Policy/etc.]
**Prevalence:** [X sources, Y mentions]
**Trend:** [Rising/Stable/Declining]

## Overview
[Topic description and context]

## Key Developments
[Bullet points of major developments]

## Source Coverage
[How each source covered this topic]

## Strategic Significance
[Why this matters and what to do]
```

## Formatting Features
- Hierarchical structure with sections and subsections
- Bold and italic emphasis
- Bullet and numbered lists
- Tables for data presentation
- Blockquotes for important callouts
- Code blocks for technical content

## Quality Checks
- Verify markdown syntax correctness
- Ensure consistent heading hierarchy
- Check for broken links or references
- Validate table formatting
- Confirm file path accessibility

## Output Standards
- Clear, executive-level language
- Logical information flow
- Visual hierarchy for scannability
- Comprehensive yet concise
- Actionable insights highlighted

## Performance
- Generation time: < 1 second
- Supports large documents (100+ KB)
- UTF-8 encoding for international content
