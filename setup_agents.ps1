# LLMunix Agent Setup Script for Claude Code
# This script copies all agent markdown files to the .claude/agents directory to make them discoverable by Claude Code

# Create the .claude/agents directory if it doesn't exist
New-Item -ItemType Directory -Force -Path ".\.claude\agents"

# Function to process agent files with YAML frontmatter
function Process-AgentFile {
    param (
        [string]$sourcePath,
        [string]$destPath
    )
    
    Write-Host "Processing agent: $sourcePath -> $destPath"
    
    # Check if the file has YAML frontmatter
    $content = Get-Content -Path $sourcePath -Raw
    if ($content -match "^---\s*\n") {
        # File already has frontmatter, copy it directly
        Copy-Item -Path $sourcePath -Destination $destPath -Force
        Write-Host "  Copied with existing frontmatter"
    } else {
        Write-Host "  WARNING: File lacks YAML frontmatter, skipping: $sourcePath"
        # In a future version, we could add code to automatically generate frontmatter
    }
}

# Clear existing agent files in the destination directory
Write-Host "Cleaning up old agent files..."
Remove-Item -Path ".\.claude\agents\*.md" -Force -ErrorAction SilentlyContinue

# Process system agents
Write-Host "Processing system agents..."
$systemAgents = Get-ChildItem -Path "system\agents\*.md" -ErrorAction SilentlyContinue
foreach ($agent in $systemAgents) {
    $destPath = ".\.claude\agents\$($agent.Name)"
    Process-AgentFile -sourcePath $agent.FullName -destPath $destPath
}

# Process component agents
Write-Host "Processing component agents..."
$componentAgents = Get-ChildItem -Path "components\agents\*.md" -ErrorAction SilentlyContinue
foreach ($agent in $componentAgents) {
    $destPath = ".\.claude\agents\$($agent.Name)"
    Process-AgentFile -sourcePath $agent.FullName -destPath $destPath
}

Write-Host "Agent setup complete. Agents are now discoverable by Claude Code."
Write-Host "Available agents:"
Get-ChildItem -Path ".\.claude\agents\*.md" | ForEach-Object { 
    $content = Get-Content -Path $_.FullName -Raw
    if ($content -match "name:\s*([^\n]+)") {
        Write-Host "  - $($Matches[1].Trim())"
    } else {
        Write-Host "  - $($_.BaseName) (no name in frontmatter)"
    }
}