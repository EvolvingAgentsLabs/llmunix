# News Web Fetch Tool

**Tool Name:** news-web-fetch-tool
**Tool Type:** web-content-retrieval
**Project:** Project_tech_news_intelligence_briefing
**Maps To:** Claude Code WebFetch tool

---

## Purpose
Fetch live web content from tech news sources with intelligent content extraction and error handling.

## Parameters
- **url** (required): The news source URL to fetch
- **prompt** (required): Instructions for content extraction and summarization

## Capabilities
- Fetch live HTML content from any accessible URL
- Convert HTML to markdown for easier processing
- Extract specific content based on prompt instructions
- Handle redirects, timeouts, and errors gracefully
- Cache results for 15 minutes to optimize repeated requests

## Claude Code Integration
```
TOOL_CALL: WebFetch
{
  "url": "https://techcrunch.com",
  "prompt": "Extract all article headlines, publication dates, and brief summaries from the main page. Focus on technology news and trending topics. Format as structured list."
}
```

## Usage Pattern
```markdown
To fetch TechCrunch content:
- URL: https://techcrunch.com
- Prompt: "Extract article headlines and summaries focusing on AI, cloud computing, startups, and emerging tech"

To fetch Ars Technica:
- URL: https://arstechnica.com
- Prompt: "Extract article headlines and summaries with emphasis on technical depth and analysis"
```

## Error Handling
- **HTTP errors**: Retry with exponential backoff
- **Redirects**: Follow and document redirect chain
- **Timeouts**: Log timeout and attempt with simplified prompt
- **Content extraction failures**: Return raw content for manual processing

## Performance
- Average latency: 2-5 seconds per fetch
- Supports parallel execution for multiple sources
- Automatic caching reduces repeated fetch costs

## Output Format
Structured markdown with:
- Source URL and fetch timestamp
- Extracted headlines and summaries
- Article metadata (dates, authors, categories)
- Status indicators and any warnings
