# Content Analysis Tool

**Tool Name:** content-analysis-tool
**Tool Type:** text-processing-analysis
**Project:** Project_tech_news_intelligence_briefing
**Maps To:** Claude Code Task tool with specialized agents

---

## Purpose
Perform deep content analysis, topic extraction, and pattern recognition on collected news content using specialized sub-agents.

## Parameters
- **content** (required): Text content to analyze
- **analysis_type** (required): Type of analysis (topic_extraction, pattern_recognition, sentiment_analysis)
- **context** (optional): Additional context for analysis

## Capabilities
- Extract key topics and themes from text
- Identify named entities (companies, people, technologies)
- Perform semantic clustering of related concepts
- Detect emerging trends and patterns
- Cross-reference multiple sources for validation
- Generate structured analytical outputs

## Claude Code Integration
```
TOOL_CALL: Task
{
  "subagent_type": "general-purpose",
  "description": "Analyze tech news content",
  "prompt": "Analyze the following tech news content and extract top 10 trending topics with supporting evidence:\n\n[CONTENT]\n\nFor each topic provide:\n1. Topic name and category\n2. Frequency across sources\n3. Key points and developments\n4. Strategic significance"
}
```

## Usage Patterns

**Topic Extraction:**
```markdown
Input: Collected news articles from multiple sources
Process: Identify recurring themes, technologies, companies, trends
Output: Ranked list of topics with prevalence metrics
```

**Pattern Recognition:**
```markdown
Input: Extracted topics from multiple sources
Process: Identify cross-source correlations, narratives, meta-trends
Output: Pattern analysis with consensus/divergence indicators
```

**Semantic Clustering:**
```markdown
Input: List of topics and keywords
Process: Group related concepts, build topic hierarchies
Output: Topic taxonomy with relationships
```

## Analysis Methodologies
- Keyword frequency analysis
- Named entity recognition
- Semantic similarity matching
- Cross-source correlation
- Temporal trend detection
- Sentiment and tone analysis

## Output Format
Structured markdown with:
- Analysis type and parameters
- Key findings and insights
- Supporting evidence and citations
- Confidence scores
- Recommendations for action

## Performance
- Processing time: 5-15 seconds depending on content volume
- Supports batch analysis of multiple articles
- Optimized for parallel processing
