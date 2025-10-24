# Agent Research Workflow - Purchase Intent System

## Overview

The Purchase Intent system uses **3 data sources** to analyze ebook topics:
1. **AI Agent Research** - Web trend signals (unlimited, no rate limits)
2. **Reddit API** - Community engagement data
3. **YouTube API** - Video view/engagement metrics

This document explains how to use the AI agent research system across multiple Claude sessions.

---

## How It Works

### Data Flow

```
1. User runs Python → Checks for agent results
2. If found → Use cached agent data
3. If not found → Use Reddit + YouTube only (2 sources)
4. User asks Claude to research missing topics
5. Claude launches agents → Writes JSON results
6. User re-runs Python → Now uses all 3 sources
```

### File Structure

```
cache/agent_results/
├── meditation.json              # Cached agent research
├── romance_novels.json
├── productivity_apps.json
└── [keyword].json               # One file per topic
```

Each JSON file contains:
```json
{
  "keyword": "meditation",
  "demand_score": 87,              // 0-100 demand score
  "confidence": 92,                // 0-100 confidence
  "signals": {
    "mention_count": 94,           // # of web mentions
    "source_quality": 88,          // Quality of sources (0-100)
    "recency_score": 95,           // How recent (0-100)
    "engagement_score": 91         // Engagement indicators (0-100)
  },
  "top_sources": [...]             // URLs and quality scores
}
```

---

## For New Claude Sessions

### When You Start a New Chat

The agent result files **persist across sessions**. Any Claude session can:
1. Read existing agent results
2. Research new topics
3. Update existing topics (if needed)

### Typical Workflow

**Step 1: User runs Python**
```bash
python agents/agent_0/main.py "topic1" "topic2" "topic3"
```

**Step 2: Check output**
```
[OK] Found agent results for 'topic1' (age: 2.5h)
[ ] No agent results for 'topic2' - will use pytrends method
[ ] No agent results for 'topic3' - will use pytrends method
```

**Step 3: User asks Claude to research missing topics**
```
User: "Research topic2 and topic3 with agents"
```

**Step 4: Claude launches agents**
Claude will use the Task tool to launch research agents in parallel.

**Step 5: User re-runs Python**
Now all topics will have agent data + Reddit + YouTube (3 sources).

---

## How to Research Topics (For Claude)

### Single Topic Research

```
User: "Research 'meditation' with an agent"
```

**Claude's process:**
1. Launch agent with Task tool (general-purpose subagent)
2. Agent executes 3-5 web searches
3. Agent analyzes results and calculates demand score
4. Agent returns JSON
5. Claude saves to `cache/agent_results/meditation.json`

### Multiple Topics in Parallel

```
User: "Research these topics: meditation, yoga, romance novels"
```

**Claude's process:**
1. Launch 3 agents in parallel (single message, multiple Task calls)
2. Each agent researches its topic independently
3. All return JSON results
4. Claude saves all 3 files
5. User re-runs Python to see combined results

### Research Template

When Claude needs to research a topic, use this prompt structure:

```
Research the keyword "[KEYWORD]" to extract trend signals for ebook demand analysis.

Your task:
1. Execute 3-5 web searches:
   - "[keyword] trends 2025 site:forbes.com OR site:statista.com"
   - "[keyword] demand popular site:reddit.com OR site:medium.com"
   - "[keyword] viral trending 2025"
   - "[keyword] market size 2025"

2. Extract: source quality, year mentions, engagement indicators

3. Calculate scores (0-100 each):
   - Mention score
   - Source quality
   - Recency score
   - Engagement score
   - DEMAND SCORE = (mention*0.4 + quality*0.3 + recency*0.2 + engagement*0.1) * 100

4. Return ONLY JSON (no other text)
```

---

## Scoring Impact

### With 2 Sources (Reddit + YouTube Only)
- Moderate accuracy
- Missing web trend validation
- Lower demand scores

### With 3 Sources (Agent + Reddit + YouTube)
- High accuracy
- Complete market validation
- Significantly higher demand scores

**Example improvements:**
- Romance Novels: 92.76 → **100.00** (+7.24)
- Productivity Apps: 77.99 → **98.88** (+20.89)
- Baby Bibs: 59.00 → **82.80** (+23.80)
- Tax Strategies: 58.49 → **88.45** (+29.96)

---

## Cache Management

### When to Refresh Agent Results

Agent results are cached permanently. Refresh when:
- Topic trends change significantly (monthly)
- Need more recent data for time-sensitive topics
- First research was low confidence (<80%)

### How to Refresh

Simply research the topic again - new results overwrite old cache file.

---

## Troubleshooting

### "No agent results found"

**This is normal!** It just means:
- Topic hasn't been researched yet, OR
- Cache file doesn't exist

**Solution:** Ask Claude to research the topic.

### "Agent results but low confidence"

**Cause:** Limited web mentions for niche topics

**Solution:**
- Accept lower confidence (still useful data), OR
- Research again with broader search terms

### "Python shows old demand scores"

**Cause:** Agent results not saved to cache yet

**Solution:**
1. Verify JSON file exists in `cache/agent_results/`
2. Check file was created recently
3. Re-run Python

---

## Best Practices

### For Users

1. **Run Python first** - See which topics need research
2. **Research in batches** - Ask Claude to research multiple topics at once
3. **Re-run Python** - Get updated scores with all 3 sources
4. **Keep cache** - Never delete agent_results folder

### For Claude

1. **Launch agents in parallel** - Use single message with multiple Task calls
2. **Save all results** - Write JSON immediately after agent completes
3. **Validate JSON** - Ensure proper structure before saving
4. **Use consistent naming** - Sanitize keywords (spaces → underscores)

---

## Advanced Usage

### Drill-Down Workflow

When user wants to drill down from broad topic to specific niches:

1. **Level 1:** Research broad topic (e.g., "meditation")
2. **Generate 10 subtopics** (e.g., "guided meditation", "sleep meditation")
3. **Research all 10** with agents in parallel
4. **User selects top 3-5** from dashboard
5. **Level 2:** Research selected topics in detail
6. **User selects winner**
7. **Level 3:** Generate ultra-specific sub-niches

### Batch Pre-Research

For frequently used topics, pre-research them once:

```
User: "Pre-research these common topics: meditation, yoga, fitness,
       romance, productivity, cooking, parenting, finance"
```

Claude researches all 8, saves to cache. Future sessions use cached data instantly.

---

## Example Session Transcript

```
User: python agents/agent_0/main.py "meditation" "cooking" "gardening"

Output:
[OK] Found agent results for 'meditation' (age: 5.2h)
[ ] No agent results for 'cooking'
[ ] No agent results for 'gardening'

User: Research cooking and gardening with agents

Claude: I'll launch 2 agents in parallel to research both topics.

[Agents complete]

Claude: Results saved to:
- cache/agent_results/cooking.json (demand: 89, confidence: 94%)
- cache/agent_results/gardening.json (demand: 85, confidence: 91%)

User: python agents/agent_0/main.py "meditation" "cooking" "gardening"

Output:
[OK] Found agent results for 'meditation' (age: 5.2h)
[OK] Found agent results for 'cooking' (age: 0.0h)
[OK] Found agent results for 'gardening' (age: 0.0h)
[*] All topics have agent results - skipping Google Trends

Results:
1. meditation - Score: 98.50
2. cooking - Score: 96.32
3. gardening - Score: 94.15
```

---

## Success Metrics

You know the system is working when:
- ✅ Agent results load instantly from cache
- ✅ Google Trends is skipped (no rate limits!)
- ✅ Quality Score: 100%
- ✅ All 3 data sources show in dashboard (5/5 stars)
- ✅ Demand scores are significantly higher with agent data

---

## Support

If the workflow isn't working:
1. Check `cache/agent_results/` folder exists
2. Verify JSON files have correct structure
3. Check Python console for LED breadcrumbs 620-629
4. Verify agent results saved with correct filename (sanitized)

For future Claude sessions: Show this document and they'll understand the complete workflow.
