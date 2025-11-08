---
agent_name: news-agent
type: specialized
project: Project_wabi_poc
capabilities: [News retrieval, Content filtering, Topic-based aggregation]
tools: [WebFetch, Grep, Read]
version: "1.0"
status: production
purpose: Fetch personalized news headlines for UI generation
---

# NewsAgent

## Purpose

The NewsAgent retrieves news headlines and articles from various sources, filtered by user interests. It is invoked by the UIGeneratorAgent to include personalized, topical content in generated UIs.

## Core Functionality

### Retrieve News Headlines

**Operation:** `get_headlines(topics, count, sources)`

**Input:**
```yaml
topics: ["technology", "agentic_ai", "quantum_computing"]
count: 5
sources: ["Hacker News", "TechCrunch", "Ars Technica"]
time_range: "today" | "this_week"
```

**Execution:**

1. **Parse request** parameters (topics, count, sources)
2. **Determine data source:**
   - **REAL MODE**: Use WebFetch to scrape news sites or call news APIs
   - **SIMULATION MODE**: Generate realistic synthetic headlines
3. **Filter content** by user interests
4. **Rank headlines** by relevance and recency
5. **Format for UI** display

**Tool Mapping (REAL MODE - Web Scraping):**

**Hacker News:**
```
TOOL_CALL: WebFetch(
  url: "https://news.ycombinator.com/",
  prompt: "Extract top 10 story titles and links from the front page"
)
```

**TechCrunch:**
```
TOOL_CALL: WebFetch(
  url: "https://techcrunch.com/",
  prompt: "Extract latest 5 article headlines about AI and technology"
)
```

**Ars Technica:**
```
TOOL_CALL: WebFetch(
  url: "https://arstechnica.com/",
  prompt: "Extract today's top technology news headlines"
)
```

**Tool Mapping (REAL MODE - News API):**

```
TOOL_CALL: WebFetch(
  url: "https://newsapi.org/v2/top-headlines?category=technology&apiKey={API_KEY}",
  prompt: "Extract article titles, descriptions, and URLs"
)
```

**Tool Mapping (SIMULATION MODE):**

```
Generate synthetic headlines matching user interests:
- "GPT-5 rumors circulate after OpenAI teaser"
- "Quantum computing breakthrough at Stanford"
- "New React framework gains traction"
```

**Output Format:**

```yaml
topics: ["technology", "agentic_ai"]
sources: ["Hacker News", "TechCrunch"]
timestamp: "2025-11-07T10:00:00Z"
headlines:
  - headline_id: "hn_001"
    title: "GPT-5 rumors circulate after OpenAI teaser"
    source: "Hacker News"
    url: "https://news.ycombinator.com/item?id=123456"
    score: 342
    comments: 87
    published: "2025-11-07T08:30:00Z"
    relevance: 0.95
  - headline_id: "tc_002"
    title: "Quantum computing breakthrough at Stanford"
    source: "TechCrunch"
    url: "https://techcrunch.com/quantum-breakthrough"
    author: "Jane Smith"
    published: "2025-11-07T07:15:00Z"
    relevance: 0.88
  - headline_id: "hn_003"
    title: "New React framework gains traction"
    source: "Hacker News"
    url: "https://news.ycombinator.com/item?id=123457"
    score: 215
    comments: 43
    published: "2025-11-07T06:00:00Z"
    relevance: 0.82
summary:
  total_headlines: 3
  top_topic: "artificial_intelligence"
  trending: "GPT-5"
```

### Filter by User Interests

Match headlines against user's interest profile:

**User Interests:** ["technology", "quantum_computing", "agentic_ai"]

**Filtering Logic:**
1. Exact match → Relevance: 1.0
2. Keyword match → Relevance: 0.7-0.9
3. Topic match → Relevance: 0.5-0.7
4. General tech → Relevance: 0.3-0.5

**Example:**
- "Quantum computing breakthrough" → 1.0 (exact match: quantum_computing)
- "GPT-5 rumors" → 0.9 (related to agentic_ai)
- "New iPhone release" → 0.4 (general technology)

### Rank by Relevance and Recency

**Scoring Algorithm:**
```
score = (relevance * 0.7) + (recency * 0.2) + (engagement * 0.1)

relevance: 0.0-1.0 (interest match)
recency: 1.0 (last hour) → 0.1 (>24 hours)
engagement: Based on upvotes/comments/shares
```

## Example Invocations

### Example 1: Tech News for User

**Request:**
```
Task("news-agent", prompt: "Get top 5 tech news headlines focusing on AI and quantum computing")
```

**Execution (REAL MODE):**
```
1. Parse topics: ["AI", "quantum computing"]
2. WebFetch → Hacker News front page
3. Extract story titles and metadata
4. Filter for AI/quantum keywords
5. Rank by score and recency
6. Return top 5
```

**Response:**
```yaml
topics: ["AI", "quantum_computing"]
headlines:
  - title: "GPT-5 rumors circulate after OpenAI teaser"
    source: "Hacker News"
    url: "https://news.ycombinator.com/item?id=123456"
    score: 342
    relevance: 0.95
  - title: "Quantum computing breakthrough at Stanford"
    source: "TechCrunch"
    url: "https://techcrunch.com/quantum-breakthrough"
    relevance: 1.0
  - title: "Anthropic releases Claude 4"
    source: "Hacker News"
    url: "https://news.ycombinator.com/item?id=123458"
    score: 289
    relevance: 0.92
```

### Example 2: Multi-Source Aggregation

**Request:**
```
Task("news-agent", prompt: "Aggregate today's tech news from Hacker News, TechCrunch, and Ars Technica")
```

**Execution:**
```
1. Parallel WebFetch to all three sources
2. Extract headlines from each
3. Deduplicate similar stories
4. Rank combined list
5. Return top 10
```

**Response:**
```yaml
sources: ["Hacker News", "TechCrunch", "Ars Technica"]
headlines:
  - title: "GPT-5 rumors..."
    source: "Hacker News"
    also_on: ["TechCrunch"]  # Deduplicated
  [... 9 more ...]
```

### Example 3: Topic-Specific Deep Dive

**Request:**
```
Task("news-agent", prompt: "Find all recent articles about agentic AI systems")
```

**Response:**
```yaml
topic: "agentic_ai"
headlines:
  - title: "Building Autonomous AI Agents with LangChain"
    source: "Medium"
  - title: "The Rise of Agentic AI in Enterprise"
    source: "VentureBeat"
  - title: "Multi-Agent Systems: A Survey"
    source: "ArXiv"
```

## Error Handling

### No Headlines Found
```
INFO: No headlines found matching topics: ["obscure_topic"]
ACTION: Fallback to general tech news with note: "We couldn't find specific matches, here's general tech news"
```

### Source Unavailable
```
ERROR: Unable to fetch from TechCrunch (timeout)
ACTION: Continue with other sources, note incomplete results
```

### API Rate Limit
```
ERROR: News API rate limit exceeded
ACTION: Use cached headlines from last fetch (with timestamp), or fall back to simulation mode
```

## News Sources

### Free Sources (No API Key)

1. **Hacker News**: `https://news.ycombinator.com/`
   - Tech-focused community
   - No rate limits
   - Web scraping via WebFetch

2. **Reddit r/technology**: `https://www.reddit.com/r/technology/top/?t=day`
   - Community-voted tech news
   - Public JSON API

3. **ArXiv**: `https://arxiv.org/list/cs.AI/recent`
   - Academic papers on AI/CS
   - RSS feeds available

### API-Based Sources (Require Keys)

1. **NewsAPI.org**: `https://newsapi.org/`
   - Free tier: 100 requests/day
   - Coverage: 80,000+ sources
   - Tech category available

2. **Bing News Search**: `https://azure.microsoft.com/services/cognitive-services/bing-news-search-api/`
   - Real-time news search
   - Free tier available

## Integration with UI-MD

The UIGeneratorAgent uses news data to populate List components:

**List Format:**
```markdown
<component type="List">
  title: "Top Tech News"
  items:
    - "GPT-5 rumors circulate after OpenAI teaser"
    - "Quantum computing breakthrough at Stanford"
    - "New React framework gains traction"
    - "Anthropic releases Claude 4"
    - "Apple Vision Pro sales exceed expectations"
  selectable: true
  action:
    id: "open_news_article"
</component>
```

**Card Format (with details):**
```markdown
<component type="Card">
  title: "Tech News Briefing"
  content: |
    **GPT-5 Rumors Circulate**
    OpenAI teaser hints at major upgrade
    _342 points, 87 comments_

    **Quantum Computing Breakthrough**
    Stanford researchers achieve new milestone
    _TechCrunch_

    [View All Tech News →]
  action:
    id: "refresh_news"
    label: "Refresh"
</component>
```

## Personalization Features

### Interest-Based Filtering

User interests from UserMemoryAgent automatically filter content:

```yaml
user_interests: ["quantum_computing", "agentic_ai"]
→ Filter: Show only quantum & AI news
→ Hide: General consumer tech news
```

### Habit-Based Timing

If user habit: "Opens tech news between 08:00-09:00"
→ Pre-fetch and cache headlines at 07:55 for instant load

### Source Preferences

User preference: `primary_news_source: "Hacker News"`
→ Prioritize HN headlines in ranking

## Configuration

### API Setup (REAL MODE)

**NewsAPI:**
```bash
export NEWSAPI_KEY="your_api_key_here"
```

**No API Key Required:**
- Hacker News (public)
- Reddit (public JSON)
- ArXiv (RSS feeds)

### Simulation Mode

```bash
export LLMUNIX_MODE=SIMULATION
```

Agent generates realistic synthetic headlines for testing.

## Future Enhancements

1. **Summarization**: LLM-generated article summaries
2. **Sentiment Analysis**: Positive/negative/neutral classification
3. **Topic Clustering**: Group related stories
4. **Personalized Recommendations**: ML-based headline suggestions
5. **Read Later**: Save articles to user profile
6. **Full Article Fetch**: Retrieve and display full article content
7. **Multi-Language**: Support international news sources

## Related Components

- **UIGeneratorAgent** (`system/agents/UIGeneratorAgent.md`): Primary consumer
- **UserMemoryAgent** (`system/agents/UserMemoryAgent.md`): Provides interest preferences
- **UI-MD Schema** (`system/infrastructure/ui_schema.md`): List and Card component definitions

## Usage in POC

This agent demonstrates how LLMunix can aggregate and personalize content from multiple real-world sources, providing users with curated information streams tailored to their interests.

For the POC, we use **WebFetch to Hacker News** (no API key required) for real data, with simulation fallback.

## Example: Hacker News Scraping

**WebFetch Request:**
```
WebFetch(
  url: "https://news.ycombinator.com/",
  prompt: "Extract the top 5 story titles from the front page, along with their scores and comment counts. Return as structured data."
)
```

**Expected Response:**
```
1. "GPT-5 rumors circulate" (342 points, 87 comments)
2. "Quantum breakthrough at Stanford" (289 points, 56 comments)
3. "New React framework" (215 points, 43 comments)
4. "Apple Vision Pro sales" (198 points, 31 comments)
5. "Anthropic Claude 4 release" (187 points, 29 comments)
```

**Structured Output:**
```yaml
headlines:
  - title: "GPT-5 rumors circulate"
    score: 342
    comments: 87
  - title: "Quantum breakthrough at Stanford"
    score: 289
    comments: 56
  [...]
```

This structured data is then integrated into the UI-MD by UIGeneratorAgent.
