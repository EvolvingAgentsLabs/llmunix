### Tools

#### ask_ollama
`sh`
```sh
#!/bin/bash
if ! command -v jq &> /dev/null || ! command -v curl &> /dev/null; then
    echo "Error: 'jq' and 'curl' are required but not found in the environment." >&2
    exit 1
fi
MODEL=$(echo "$GEMINI_TOOL_ARGS" | jq -r .model)
PROMPT=$(echo "$GEMINI_TOOL_ARGS" | jq -r .prompt)
if [ -z "$MODEL" ] || [ -z "$PROMPT" ]; then
  echo "Error: 'model' and 'prompt' are required arguments." >&2
  exit 1
fi
PAYLOAD=$(cat <<EOF
{
  "model": "$MODEL",
  "prompt": "$PROMPT",
  "stream": false
}
EOF
)
OLLAMA_HOST="http://localhost:11434"
RESPONSE=$(curl -s --fail "$OLLAMA_HOST/api/generate" -d "$PAYLOAD")
if [ $? -ne 0 ]; then
    echo "Error: Failed to connect to Ollama at $OLLAMA_HOST. Is Ollama running and accessible?" >&2
    exit 1
fi
echo "$RESPONSE" | jq -r .response
```
`json`
```json
{
  "name": "ask_ollama",
  "description": "Sends a prompt to a locally running LLM via the Ollama API and returns the text response. Useful for quick, non-critical text generation, summarization, or evaluation tasks that should be handled by a different model.",
  "parameters": {
    "type": "object",
    "properties": {
      "model": {
        "type": "string",
        "description": "The name of the Ollama model to use, e.g., 'llama3' or 'phi3'."
      },
      "prompt": {
        "type": "string",
        "description": "The prompt to send to the Ollama model."
      }
    },
    "required": ["model", "prompt"]
  }
}
```