# Add YAML frontmatter to agent files that don't have it
# This script checks agent markdown files and adds frontmatter if missing

Write-Host "Adding YAML frontmatter to agent files without frontmatter..."

# Process agent files in components/agents
$agentFiles = Get-ChildItem -Path "components/agents/*.md" -ErrorAction SilentlyContinue

foreach ($file in $agentFiles) {
    $content = Get-Content -Path $file.FullName -Raw
    
    # Check if file already has frontmatter
    if (-not ($content -match "^---\s*\n")) {
        Write-Host "Adding frontmatter to: $($file.Name)"
        
        # Extract agent name from filename
        $agentName = $file.BaseName.Replace("Agent", "").ToLower()
        $hyphenatedName = $agentName.ToLower() + "-agent"
        
        # Extract first heading to use as description
        $description = ""
        if ($content -match "# ([^\n]+)") {
            $description = $Matches[1]
            if ($description -match "Agent$") {
                $description = $description.Substring(0, $description.Length - 6).Trim()
            }
            $description = "A specialized agent for $description tasks"
        } else {
            $description = "A specialized agent for $agentName tasks"
        }
        
        # Determine tools based on content analysis
        $tools = "Read, Write"
        if ($content -contains "WebFetch" -or $content -contains "web" -or $content -contains "URL" -or $content -contains "internet") {
            $tools += ", WebFetch"
        }
        if ($content -contains "files" -or $content -contains "directory" -or $content -contains "search") {
            $tools += ", Glob, Grep"
        }
        if ($content -contains "execute" -or $content -contains "command" -or $content -contains "run") {
            $tools += ", Bash"
        }
        if ($content -contains "delegate" -or $content -contains "sub-agent" -or $content -contains "task") {
            $tools += ", Task"
        }
        
        # Create frontmatter
        $frontmatter = @"
---
name: $hyphenatedName
description: $description
tools: $tools
---

"@

        # Add frontmatter to content and save
        $newContent = $frontmatter + $content
        Set-Content -Path $file.FullName -Value $newContent
        
        Write-Host "  Added frontmatter with name: $hyphenatedName"
    } else {
        Write-Host "Skipping $($file.Name): Already has frontmatter"
    }
}

Write-Host "Frontmatter addition complete!"