### Tools

#### ask_openai
`sh`
```sh
#!/bin/bash
# This script sends a prompt to the OpenAI API.

# 1. Security Check: Ensure the API key is available as an environment variable.
if [ -z "$OPENAI_API_KEY" ]; then
    echo "Error: The OPENAI_API_KEY environment variable is not set. This tool cannot function without it." >&2
    exit 1
fi

# 2. Parse arguments
MODEL=$(echo "$GEMINI_TOOL_ARGS" | jq -r .model)
PROMPT=$(echo "$GEMINI_TOOL_ARGS" | jq -r .prompt)

# 3. Construct the JSON payload for the OpenAI Chat Completions API
PAYLOAD=$(cat <<EOF
{
  "model": "$MODEL",
  "messages": [
    {
      "role": "user",
      "content": "$PROMPT"
    }
  ]
}
EOF
)

# 4. Make the API call using curl with the authorization header
RESPONSE=$(curl -s --fail "https://api.openai.com/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d "$PAYLOAD")

if [ $? -ne 0 ]; then
    echo "Error: The OpenAI API call failed. Check your API key, model name, and network connection." >&2
    echo "Response from server: $RESPONSE" >&2
    exit 1
fi

# 5. Parse the response to extract the message content
echo "$RESPONSE" | jq -r '.choices[0].message.content'
```
`json`
```json
{
  "name": "ask_openai",
  "description": "Sends a prompt to an OpenAI model (e.g., gpt-4o) and returns the text response. Use for tasks that require a specific model's capabilities or for cross-model evaluation.",
  "parameters": {
    "type": "object",
    "properties": {
      "model": {
        "type": "string",
        "description": "The name of the OpenAI model to use, e.g., 'gpt-4o' or 'gpt-3.5-turbo'."
      },
      "prompt": {
        "type": "string",
        "description": "The prompt to send to the OpenAI model."
      }
    },
    "required": ["model", "prompt"]
  }
}
```