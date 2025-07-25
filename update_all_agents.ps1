# Update all agent files with YAML frontmatter
# This script processes all agent files in components/agents directory

Write-Host "Updating all agent files with YAML frontmatter..."

$agents = @(
    @{
        "file" = "IntelligenceBriefingAgent.md"
        "name" = "intelligence-briefing-agent"
        "description" = "A specialized agent for generating intelligence briefings from collected data and trends"
        "tools" = "Read, Write, WebFetch, Glob, Grep"
    },
    @{
        "file" = "QAReviewAgent.md"
        "name" = "qa-review-agent"
        "description" = "A specialized agent for reviewing and quality checking content and reports"
        "tools" = "Read, Write, Grep, Glob"
    },
    @{
        "file" = "RealSummarizationAgent.md"
        "name" = "real-summarization-agent"
        "description" = "A specialized agent for summarizing content and extracting key information"
        "tools" = "Read, Write, WebFetch"
    },
    @{
        "file" = "ResearchReportAgent.md"
        "name" = "research-report-agent"
        "description" = "A specialized agent for creating detailed research reports from collected data"
        "tools" = "Read, Write, WebFetch, Glob, Grep"
    },
    @{
        "file" = "SummarizationAgent.md"
        "name" = "summarization-agent"
        "description" = "A specialized agent for summarizing content and extracting key points"
        "tools" = "Read, Write, WebFetch"
    },
    @{
        "file" = "TrendingTopicExtractorAgent.md"
        "name" = "trending-topic-extractor-agent"
        "description" = "A specialized agent for identifying and extracting trending topics from content"
        "tools" = "Read, Write, WebFetch, Glob, Grep"
    },
    @{
        "file" = "WritingAgent.md"
        "name" = "writing-agent"
        "description" = "A specialized agent for creating written content and documentation"
        "tools" = "Read, Write, Glob, Grep"
    }
)

foreach ($agent in $agents) {
    $filePath = "components/agents/$($agent.file)"
    
    if (Test-Path $filePath) {
        Write-Host "Processing $($agent.file)..."
        $content = Get-Content -Path $filePath -Raw
        
        # Check if file already has frontmatter
        if (-not ($content -match "^---\s*\n")) {
            # Create frontmatter
            $frontmatter = @"
---
name: $($agent.name)
description: $($agent.description)
tools: $($agent.tools)
---

"@

            # Add frontmatter to content and save
            $newContent = $frontmatter + $content
            Set-Content -Path $filePath -Value $newContent
            
            Write-Host "  Added frontmatter to $($agent.file)"
        } else {
            Write-Host "  $($agent.file) already has frontmatter, skipping"
        }
    } else {
        Write-Host "Warning: File $filePath does not exist"
    }
}

Write-Host "Agent file updates complete!"