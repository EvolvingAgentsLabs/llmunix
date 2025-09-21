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

# Process project-specific agents
echo "Processing project-specific agents..."
if [ -d "projects" ]; then
    for project_dir in projects/*/; do
        if [ -d "$project_dir/components/agents" ]; then
            project_name=$(basename "$project_dir")
            echo "  Processing agents for project: $project_name"
            for agent in "$project_dir/components/agents"/*.md; do
                if [ -f "$agent" ]; then
                    # Add project prefix to avoid naming conflicts
                    agent_name=$(basename "$agent" .md)
                    dest_path=".claude/agents/${project_name}_${agent_name}.md"
                    process_agent_file "$agent" "$dest_path"
                fi
            done
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