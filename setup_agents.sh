#!/bin/bash
# LLMunix Agent Setup Script for Claude Code
# This script copies all agent markdown files to the .claude/agents directory to make them discoverable by Claude Code

# Create the .claude/agents directory if it doesn't exist
mkdir -p .claude/agents

# Function to process agent files with YAML frontmatter
process_agent_file() {
    local source_path="$1"
    local dest_path="$2"
    
    echo "Processing agent: $source_path -> $dest_path"
    
    # Check if the file has YAML frontmatter
    if grep -q "^---" "$source_path"; then
        # File already has frontmatter, copy it directly
        cp "$source_path" "$dest_path"
        echo "  Copied with existing frontmatter"
    else
        echo "  WARNING: File lacks YAML frontmatter, skipping: $source_path"
        # In a future version, we could add code to automatically generate frontmatter
    fi
}

# Clear existing agent files in the destination directory
echo "Cleaning up old agent files..."
rm -f .claude/agents/*.md

# Process system agents
echo "Processing system agents..."
if [ -d "system/agents" ]; then
    for agent in system/agents/*.md; do
        if [ -f "$agent" ]; then
            dest_path=".claude/agents/$(basename "$agent")"
            process_agent_file "$agent" "$dest_path"
        fi
    done
fi

# Process component agents
echo "Processing component agents..."
if [ -d "components/agents" ]; then
    for agent in components/agents/*.md; do
        if [ -f "$agent" ]; then
            dest_path=".claude/agents/$(basename "$agent")"
            process_agent_file "$agent" "$dest_path"
        fi
    done
fi

echo "Agent setup complete. Agents are now discoverable by Claude Code."
echo "Available agents:"
for agent in .claude/agents/*.md; do
    if [ -f "$agent" ]; then
        name=$(grep -m 1 "name:" "$agent" | sed 's/name:\s*//' | tr -d '\r')
        if [ -n "$name" ]; then
            echo "  - $name"
        else
            echo "  - $(basename "$agent" .md) (no name in frontmatter)"
        fi
    fi
done