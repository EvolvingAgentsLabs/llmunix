# Component: RealWebFetchTool

- **Name**: RealWebFetchTool
- **Type**: TOOL
- **Claude Tool**: WebFetch
- **Description**: Fetches real, live content from web URLs using Claude Code's WebFetch capability.

## Inputs

- `url` (string): The URL to fetch content from
- `prompt` (string): Instructions for content extraction (default: "Extract the main text content")

## Outputs

- `content` (string): The extracted content from the webpage
- `summary` (string): Brief summary of what was fetched
- `metadata` (object): Information about the fetch operation

## Real Tool Mapping

```yaml
claude_tool: WebFetch
parameters:
  url: {{url}}
  prompt: {{prompt}}
cost: low ($0.001-0.01 per call)
latency: medium (2-10 seconds)
side_effects: "Network request to external server"
error_modes: ["timeout", "404", "403", "rate_limit", "connection_error"]
```

## Logic

### EXECUTION MODE (Claude Code Runtime):
1. Use Claude Code's WebFetch tool with provided URL and prompt
2. Capture the real response content
3. Extract metadata (response time, success status)
4. Save content to workspace file if needed
5. Return structured output with content and metadata

### EXECUTION MODE (LLM Interpreter Runtime):
1. Use curl or wget command to fetch URL content
2. Parse response headers for metadata (status, content-type)
3. Extract text content from HTML using simple text processing
4. Apply prompt instructions to filter/extract relevant content
5. Save content to workspace file and return structured output

### SIMULATION MODE:
1. Generate realistic mock content based on URL
2. Simulate typical response times and potential errors
3. Create training data showing tool call and response pattern

## Usage Examples

**Simple webpage fetch:**
```
Input: {url: "https://example.com", prompt: "Get the main content"}
Output: {content: "...", metadata: {status: "success", time: "2.3s"}}
```

**Article extraction:**
```
Input: {url: "https://blog.com/article", prompt: "Extract article title and body"}
Output: {content: "Title: ... Body: ...", metadata: {status: "success"}}
```

## Error Handling

- **Timeout**: Retry once with longer timeout
- **Rate Limit**: Wait and retry after delay
- **404/403**: Return error with specific message
- **Network Error**: Check connectivity, return informative error

## Training Data Format

```json
{
  "tool_call": {
    "tool": "WebFetch",
    "inputs": {"url": "https://example.com", "prompt": "Extract content"},
    "outputs": {"content": "...", "metadata": {...}},
    "performance": {"cost": "$0.003", "time": "2.1s", "success": true}
  }
}
```