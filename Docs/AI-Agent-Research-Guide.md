# AI Agent Research Guide
**For Agent 0 Topic Research**

## Purpose
When the user asks you to research topics using AI agents (web search), you need to gather specific data and save it in a structured JSON format.

## When This Happens
User will say something like:
- "Generate and research 10 subtopics for meditation"
- "Research these topics: body scan meditation, chakra meditation"

## What You Need to Research
For each topic, gather:

1. **Description** (NEW - CRITICAL!)
   - A clear, concise explanation of WHAT the topic is
   - 1-3 sentences maximum
   - Focus on definition, not market analysis
   - Example: "Body scan meditation is a mindfulness practice where you systematically focus attention on different parts of your body, typically starting from your toes and moving upward. It helps develop body awareness and release physical tension."

2. **Demand Score** (0-100)
   - How popular/in-demand is this topic?
   - Based on: search volume, social mentions, content creation activity
   - Higher = more demand

3. **Confidence** (0-100)
   - How confident are you in your assessment?
   - Based on: number of sources, data quality, consistency

4. **Signals** (detailed metrics)
   - `mention_count`: How many times topic appears in sources (0-100)
   - `source_quality`: Quality of sources discussing it (0-100)
   - `recency_score`: How recent is the content? (0-100)
   - `engagement_score`: Social engagement levels (0-100)

5. **Top Sources** (optional)
   - Array of relevant URLs/sources you found

## Output Format

Save results to: `D:\Projects\Ai\Purchase-Intent\cache\agent_results\{topic_name}.json`

**File naming:**
- Convert topic to lowercase
- Replace spaces with underscores
- Example: "body scan meditation" → `body_scan_meditation.json`

**JSON Structure:**
```json
{
  "keyword": "body scan meditation",
  "description": "Body scan meditation is a mindfulness practice where you systematically focus attention on different parts of your body, typically starting from your toes and moving upward. It helps develop body awareness and release physical tension.",
  "demand_score": 72,
  "confidence": 80,
  "signals": {
    "mention_count": 68,
    "source_quality": 85,
    "recency_score": 70,
    "engagement_score": 65
  },
  "top_sources": [
    "https://www.mindful.org/body-scan-meditation/",
    "https://www.healthline.com/health/body-scan-meditation"
  ]
}
```

## Research Process

### Step 1: Web Search
Search for: `{topic} definition` OR `what is {topic}`
- Look for authoritative sources (Wikipedia, health sites, educational content)
- Read 2-3 top results

### Step 2: Extract Description
- Write a clear 1-3 sentence explanation
- **Focus on WHAT it is, not WHY it's good**
- Good: "A practice where you focus on your breathing..."
- Bad: "A popular technique with 10M followers that offers great opportunities..."

### Step 3: Assess Demand
Search for: `{topic} popularity` OR `{topic} trending`
- Look at: Reddit discussions, YouTube videos, blog posts
- High demand (80-100): Lots of recent content, active communities
- Medium demand (50-79): Moderate interest, some content
- Low demand (0-49): Limited content, niche interest

### Step 4: Calculate Signals
- **mention_count**: Count references across sources (estimate 0-100)
- **source_quality**: Rate credibility of sources (0-100)
- **recency_score**: How much content from last 6 months? (0-100)
- **engagement_score**: Social shares, comments, views (0-100)

### Step 5: Set Confidence
- High (80-100): Found multiple high-quality sources with consistent info
- Medium (50-79): Found some sources, data is okay
- Low (0-49): Limited sources, uncertain data

### Step 6: Save JSON
- Create file in `cache/agent_results/` directory
- Use exact format shown above
- Ensure all required fields are present

## Example Workflow

**User says:** "Generate and research 10 subtopics for meditation"

**You do:**
1. Generate 10 subtopic ideas
2. For EACH subtopic:
   - Web search for definition
   - Extract clear description
   - Assess demand and signals
   - Save JSON file
3. Respond: "I've completed the research and saved results for all 10 subtopics in cache/agent_results/. Ready for Python to process!"

## Critical Rules

✅ **DO:**
- Always include the `description` field
- Make descriptions factual and educational
- Base scores on actual web research
- Save files before telling user you're done

❌ **DON'T:**
- Skip the description field (it's required now!)
- Put market analysis in the description
- Guess scores without researching
- Tell user to run Python if files aren't ready

## Verification

Before responding "research complete":
1. Check all JSON files exist in `cache/agent_results/`
2. Verify each has `description` field
3. Confirm descriptions explain WHAT the topic is

## Next Step

After saving all JSON files, tell the user:
"Research complete! I've saved AI agent results for all topics. You can now tell me: 'Run Python with these topics under parent [parent_name]'"
