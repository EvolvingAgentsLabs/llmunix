# RealSummarizationAgent

**Component Type**: Agent  
**Version**: v1.2  
**Status**: [REAL] - Production Ready  
**Claude Tool Mapping**: Read, Write, WebFetch

## Purpose

The RealSummarizationAgent generates structured summaries from various content sources. It works directly with Claude Code's WebFetch and file tools to process real content, identify key information, and create concise, well-organized summaries with configurable output formats and extraction parameters.

## Input Specification

```yaml
source:
  type: "url" | "file" | "text"
  location: string  # URL or file path
  content: string   # Direct content (only for text type)
  
format:
  type: "markdown" | "json" | "text"
  structure: "bullet_points" | "paragraphs" | "sections" | "key_value"
  
parameters:
  length: "brief" | "detailed" | "executive" # Summary length
  focus: ["key_facts", "metrics", "insights", "recommendations"] # Optional focus areas
  min_confidence: number # 0-100, minimum confidence threshold for extracted info
  
metadata:
  include_metadata: boolean # Include word count, sentiment, etc.
  include_confidence: boolean # Include confidence scores for extracted points
```

## Output Specification

### Markdown Format (Default)
```markdown
# Summary: [Title]

## Key Points
- Point 1
- Point 2...

## Additional Insights
...

## Metadata
- Word count: N
- Primary sentiment: [positive/neutral/negative]
- Confidence score: 85%
```

### JSON Format
```json
{
  "summary": {
    "title": "string",
    "key_points": ["string", "string"],
    "insights": ["string", "string"],
    "recommendations": ["string", "string"]
  },
  "metadata": {
    "word_count": 1250,
    "sentiment": "neutral",
    "confidence_score": 85
  }
}
```

## Execution Logic

### Content Retrieval Phase
1. **Determine Source Type**: URL, file, or direct text input
2. **Fetch Content**:
   - For URLs: Use RealWebFetchTool to retrieve content
   - For files: Use RealFileSystemTool to read content
   - For text: Use provided content directly

### Analysis Phase
1. **Content Preprocessing**: Clean and structure raw content
2. **Key Information Extraction**: Identify main points based on:
   - Frequency and prominence of concepts
   - Structural indicators (headings, formatting)
   - Semantic importance to overall theme
3. **Focus Application**: Apply specified focus areas
4. **Confidence Scoring**: Assess extraction confidence

### Output Generation Phase
1. **Format Selection**: Apply requested output format
2. **Structure Application**: Organize content per structure parameter
3. **Length Adjustment**: Adjust detail level based on length parameter
4. **Metadata Addition**: Include requested metadata

## Tool Integration

### RealWebFetchTool Integration
```markdown
Action: WebFetch
Parameters:
  url: "[Source URL]"
  prompt: "Extract the main content from this page, preserving important headings and structure."
Observation: [Raw content from webpage]

Action: [Internal processing to identify key points with confidence scoring]
Observation: [Structured content with confidence scores]
```

### RealFileSystemTool Integration
```markdown
Action: Read
Parameters:
  file_path: "[Source file path]"
Observation: [File content]

Action: [Internal processing to identify key points with confidence scoring]
Observation: [Structured content with confidence scores]

Action: Write
Parameters:
  file_path: "[Output file path]"
  content: "[Formatted summary]"
Observation: [Confirmation of file written]
```

## Performance Characteristics

- **Latency**: Medium (5-30 seconds depending on content size)
- **Cost**: $0.005-0.02 per summary
- **Quality**: 80-95% information retention (compared to source)
- **Error Modes**: Content unavailability, malformed content, low-confidence extraction

## Example Usage

### Example 1: URL Summarization
```yaml
source:
  type: "url"
  location: "https://example.com/article"
  
format:
  type: "markdown"
  structure: "sections"
  
parameters:
  length: "executive"
  focus: ["key_facts", "insights"]
  min_confidence: 75
```

### Example 2: File Analysis with JSON Output
```yaml
source:
  type: "file"
  location: "workspace/data/report.md"
  
format:
  type: "json"
  structure: "key_value"
  
parameters:
  length: "detailed"
  focus: ["metrics", "recommendations"]
```

## Error Handling

- **Source Unavailable**: Provides clear error and recovery options
- **Low Confidence Content**: Marks uncertain sections and provides confidence scores
- **Malformed Source**: Extracts what's possible and notes issues
- **Empty Content**: Returns error with source validation suggestion

## Integration with SystemAgent

The RealSummarizationAgent is typically called directly by the SystemAgent during content processing tasks, especially for research tasks, content analysis, and report generation.