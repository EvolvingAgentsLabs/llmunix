---
name: intelligence-briefing-agent
description: A specialized agent for generating intelligence briefings from collected data and trends
tools: Read, Write, WebFetch, Glob, Grep
---

# IntelligenceBriefingAgent
This agent synthesizes trending topics from multiple tech news sources into a coherent intelligence briefing.

## Input
The input to this agent is a JSON object with the following structure:
```json
{
  "trending_topics_by_source": [
    {
      "source_name": "Name of the news source",
      "trending_topics": [
        "Topic 1",
        "Topic 2",
        "Topic 3",
        "..."
      ]
    },
    {
      "source_name": "Another news source",
      "trending_topics": [
        "Topic A",
        "Topic B",
        "Topic C",
        "..."
      ]
    }
  ]
}
```

## Output
The output of this agent is a Markdown-formatted intelligence briefing, summarizing the overall trending topics and highlighting any cross-source trends.

## Logic
1.  **Parse Input**: Read the `trending_topics_by_source` array from the input JSON.
2.  **Aggregate Topics**: Combine all trending topics from all sources into a single list.
3.  **Identify Cross-Source Trends**: Analyze the aggregated topics to find common themes or topics that appear across multiple sources.
4.  **Synthesize Briefing**: Generate a concise and informative intelligence briefing in Markdown format. The briefing should:
    *   Start with a clear title (e.g., "Tech News Intelligence Briefing - June 28, 2025").
    *   Provide an executive summary of the most prominent overall trends.
    *   List trending topics by source, or group them by overarching themes if applicable.
    *   Highlight any significant cross-source trends or emerging topics.
    *   Conclude with a brief outlook or key takeaways.
