# Drill-Down PRD - Purchase Intent System

**Last Updated:** 2025-10-31
**Status:** Active
**Maintainer:** Claude Code (update this file when workflow changes)

---

## Purpose

This document defines the **drill-down workflow** for the Purchase Intent system - how we go from a broad topic (e.g., "meditation") to ultra-specific niches (e.g., "walking meditation for anxiety relief") backed by real demand data.

---

## 🆕 Tiered API Strategy (2025-10-31)

**Problem Solved:** Google denied YouTube quota increase (10,000 units/day limit), and Google Trends has unpredictable rate limits.

**Solution:** Use cheap/unlimited sources for exploration, expensive sources only for final validation.

### **Three Modes:**

#### **1. Drill-Down Mode (Reddit-Only)**
```bash
python agents/agent_0/main.py --drill-down-mode "meditation"
```
- **Sources:** Reddit + AI Agent Research (Task tool)
- **Quota Cost:** ZERO (Reddit: 3,600 calls/hour, Agent: unlimited)
- **Confidence:** 60% (acceptable for exploration)
- **Use Case:** Explore 20-100 candidate topics, drill 3-5 levels deep
- **Speed:** Fast (no rate limit delays)

#### **2. Regular Mode (Reddit + Google Trends)**
```bash
python agents/agent_0/main.py "meditation"
```
- **Sources:** Reddit + Google Trends (24-hour cache)
- **Quota Cost:** Low (~15 Trends calls/hour safe limit with caching)
- **Confidence:** 100% (if both sources have data)
- **Use Case:** Standard analysis with trend signals
- **Speed:** Moderate (12s delay per Trends query)

#### **3. Validation Mode (All Sources)**
```bash
python agents/agent_0/main.py --enable-youtube "walking meditation for anxiety"
```
- **Sources:** Reddit + Google Trends + YouTube
- **Quota Cost:** High (~500-1,000 YouTube units per topic)
- **Confidence:** 100% (if all 3 sources have data)
- **Use Case:** Final validation before committing to write book
- **Quota Budget:** 10,000 units/day = 10-20 topics max

### **Recommended Workflow:**

```
Stage 1 (Exploration): Use --drill-down-mode
├─ Level 0: meditation (1 query)
├─ Level 1: 10 subtopics (10 queries)
├─ Level 2: 5 promising → 50 queries
└─ Total: 61 Reddit queries (~2% of hourly quota)

Stage 2 (Selection): Pick top 3 ultra-niches from Level 2

Stage 3 (Validation): Use --enable-youtube on final 3
├─ "walking meditation for anxiety" (1,000 units)
├─ "body scan meditation for sleep" (1,000 units)
├─ "loving kindness meditation" (1,000 units)
└─ Total: 3,000 units (~30% of daily YouTube quota)

Stage 4 (Decision): Choose 1 topic to write about
```

**Key Benefits:**
- Unlimited exploration (Reddit + Agent Research)
- YouTube quota lasts entire month (not just 1 day)
- Clear confidence scores guide when to validate
- Fail loudly with actionable error messages

---

## The "Rule of One" Goal

**Problem:** Broad topics (meditation, romance novels) have too much competition.
**Solution:** Drill down 2-3 levels until you find ultra-specific niches with validated demand but low competition.

**Example Drill-Down Path:**
```
Level 0: meditation (too broad)
  ↓
Level 1: walking meditation (still competitive)
  ↓
Level 2: walking meditation for anxiety (Rule of One niche - specific, validated, lower competition)
```

---

## User-Facing Workflow

### **User Says:**
"Generate and research 10 subtopics for meditation"

### **Claude Does:**

**Step 1: Generate 10 Subtopics (Using Task Tool)**
- Claude uses Task tool with general-purpose agent
- Agent performs web research using Grok methodology:
  - Brainstorms 15-25 candidate subtopics
  - Searches: "top meditation trends 2025 site:forbes.com OR site:healthline.com OR site:reddit.com"
  - Searches: "most popular meditation subtopics 2024-2025"
  - Extracts engagement signals from Reddit, X/Twitter
  - Calculates composite demand score: (0.5 × Trends) + (0.25 × Reddit) + (0.25 × X)
  - Returns top 10 subtopics ranked by demand
- Prompt is documented in: `Docs/Grok-drilldown.md`

**Step 2: Research Each Subtopic (Using Task Tool)**
- For EACH of the 10 subtopics, Claude uses Task tool to research:
  - **Description:** What IS this topic? (1-3 sentences from authoritative sources)
  - **Demand Score:** 0-100 based on mention frequency, engagement, recency
  - **Confidence:** 0-100 based on source quality and data availability
  - **Signals:** mention_count, source_quality, recency_score, engagement_score
  - **Top Sources:** URLs of research sources
- Research methodology: `Docs/AI-Agent-Research-Guide.md`
- Saves to: `cache/agent_results/{topic_name}.json`

**Step 3: Save Results**
- Claude saves 10 JSON files to `cache/agent_results/`
- Files persist across sessions (cached for future use)
- Responds: "Research complete! All 10 topics researched and saved."

**Step 4: Python Processing**

### **User Says (Exploration):**
"Run Python with drill-down mode for these topics under parent meditation"

### **Claude Does:**
- Runs: `python agents/agent_0/main.py <10 subtopics> --parent meditation --drill-down-mode`
- Python loads cached agent results (descriptions + demand scores)
- Python adds Reddit data (community engagement, top subreddits)
- **Skips:** Google Trends and YouTube (saves quotas)
- Python generates dashboard with Reddit-only validation (60% confidence)
- Claude opens dashboard in browser

### **User Says (Final Validation):**
"Run Python with YouTube enabled for my top 3 topics"

### **Claude Does:**
- Runs: `python agents/agent_0/main.py "topic1" "topic2" "topic3" --enable-youtube`
- Python loads all cached data
- Python adds Reddit data
- Python adds Google Trends data
- Python adds YouTube data (quota cost: ~3,000 units)
- Python generates dashboard with full 3-source validation (100% confidence)
- Claude opens dashboard in browser

**Step 5: User Reviews**
- Dashboard shows tree: meditation → 10 subtopics
- Click paper icon (📄) → See topic description, metrics, community links
- User identifies top 3-5 promising subtopics

**Step 6: Drill Down Again (Level 2)**

### **User Says:**
"Drill down on walking meditation"

### **Claude Repeats Steps 1-5:**
- Generate 10 walking meditation subtopics
- Research all 10 with Task tool
- Save JSON files
- Run Python with `--parent "walking meditation"`
- Generate new dashboard showing: meditation → walking meditation → 10 children

**Step 7: Find "Rule of One" Niche**
- User selects the ultra-specific niche with:
  - High demand (score >70)
  - Manageable competition
  - Clear audience
  - Validated by all 3 data sources

---

## Key Technical Details

### **Why We Don't Use Paid APIs**

❌ **WRONG (Previous Implementation):**
- `drill_down.py` tried to use paid Anthropic API
- Required `ANTHROPIC_API_KEY` in .env
- Added unnecessary cost
- Violated CLAUDE.md rule: "NO PAID APIs - User has Claude Pro subscription. Use Task tool, not Anthropic API."

✅ **CORRECT (Current Implementation):**
- Claude Code has Task tool built-in (FREE with Claude Pro)
- Task tool can launch agents with web search
- Agents save JSON results to cache
- Python loads cached results
- No additional API costs

### **Why drill_down.py Was Deleted**

**File:** `agents/agent_0/drill_down.py` (DELETED 2025-10-25)

**Why it existed:**
- Previous Claude tried to automate subtopic generation FROM Python code
- Used paid Anthropic SDK with `from anthropic import Anthropic`
- Had hardcoded pattern fallbacks for only 4 topics (meditation, romance novels, cooking, productivity)

**Why it was wrong:**
- Claude Code can't call Task tool from inside Python code
- Task tool only works when Claude is actively executing in chat
- Subtopic generation happens in CHAT (Claude uses Task tool), not in PYTHON
- Python's job is to LOAD cached results, not generate them

**Correct flow:**
```
CHAT (Claude with Task tool) → Generate subtopics → Save JSON
                                        ↓
                                Research subtopics → Save JSON
                                        ↓
PYTHON (loads cached JSON) → Add Reddit/YouTube → Generate dashboard
```

---

## File Locations

### **Code Files**
- `agents/agent_0/main.py` - Main research pipeline, loads agent results
- `agents/agent_0/agent_results_loader.py` - Loads JSON from cache
- `agents/agent_0/dashboard.py` - Generates HTML dashboard with tree view
- `agents/agent_0/drill_down_loader.py` - Manages drill trail (tree structure)

### **Cache Files**
- `cache/agent_results/{topic}.json` - Agent research results (persist across sessions)
- `cache/drill_trail.json` - Tree structure (parent-child relationships)
- `cache/trends_{topic}.json` - Google Trends data (if used)

### **Output Files**
- `outputs/agent0-dashboard.html` - Final dashboard (auto-opens in browser)
- `outputs/topic-selection.json` - Research results JSON

---

## Key Documentation Files

**READ THESE BEFORE DOING DRILL-DOWN:**

1. **`Docs/Topic-Description-Workflow.md`**
   - Complete user-facing workflow
   - How descriptions are collected and displayed
   - Troubleshooting guide

2. **`Docs/AI-Agent-Research-Guide.md`**
   - How Claude should research topics using Task tool
   - JSON format requirements
   - Research methodology (web search strategy)

3. **`Docs/Agent-Research-Workflow.md`**
   - Cross-session workflow (how cache persists)
   - When to refresh agent results
   - Batch research strategies

4. **`Docs/Grok-drilldown.md`**
   - Exact prompt for generating subtopics
   - Grok methodology (Trends + Reddit + X scoring)
   - Example outputs

5. **`Docs/Safe-Iteration-Workflow.md`**
   - When to create backups before risky changes
   - Git workflow safety rules
   - Required before editing >200 lines

---

## Data Sources (3-Source Validation)

### **Source 1: AI Agent Research (FREE - Task Tool)**
- **Provides:** Description, demand score, web trend signals
- **Method:** Claude uses Task tool → web search → saves JSON
- **Rate Limits:** NONE (uses web search, not APIs)
- **Quality:** High (searches Forbes, Healthline, Reddit threads, X/Twitter)

### **Source 2: Reddit (FREE - PRAW API)**
- **Provides:** Community engagement, top subreddits, upvotes, timestamps
- **Method:** Python queries Reddit API
- **Rate Limits:** 60 requests/minute (manageable)
- **Quality:** High (real community discussions, pain points)

### **Source 3: YouTube (FREE - Data API v3)**
- **Provides:** Video view counts, top channels, engagement metrics
- **Method:** Python queries YouTube API
- **Rate Limits:** 10,000 units/day default (requested 100,000)
- **Quality:** High (validates audience size, content creators)
- **Status:** API enabled 2025-10-25, quota increase pending

---

## Scoring System

### **Composite Score Formula**
```python
composite_score = (
    0.50 * trends_score +      # Web trend signals (Agent research)
    0.25 * reddit_score +      # Community engagement
    0.25 * youtube_score       # Video content validation
)
```

### **Score Interpretation**
- **90-100:** Excellent - High demand, strong validation
- **70-89:** Good - Viable opportunity with effort
- **50-69:** Moderate - Risky, needs unique angle
- **0-49:** Low - Niche or emerging, uncertain demand

### **Competition Levels**
- **0-40:** Low competition (GREEN zone - opportunity!)
- **41-60:** Moderate competition (YELLOW - viable with quality)
- **61-100:** High competition (RED - need strong differentiation)

### **Opportunity Zones**
- **Winning Zone:** Demand >80, Competition <50 (high demand, low competition)
- **Viable Zone:** Demand >70, Competition <70 (good opportunity)
- **Risky Zone:** Demand <70 OR Competition >70 (need unique angle)
- **Avoid Zone:** Demand <50, Competition >70 (saturated low-demand)

---

## Example Session Transcript

```
User: "Generate and research 10 subtopics for meditation"

Claude: I'll use the Task tool to generate and research subtopics for meditation.

[Claude launches Task tool with Grok prompt]
[Task tool generates: mindfulness meditation, walking meditation, body scan meditation, ...]
[Claude researches each subtopic via Task tool]
[Claude saves 10 JSON files to cache/agent_results/]

Claude: "Research complete! I've saved results for all 10 meditation subtopics:
        - mindfulness_meditation.json (demand: 100, confidence: 100%)
        - walking_meditation.json (demand: 95.8, confidence: 100%)
        - body_scan_meditation.json (demand: 96.2, confidence: 100%)
        ... (7 more)

        Ready to run Python?"

User: "Run Python with these topics under parent meditation"

Claude: [Runs Python via Bash]
        python agents/agent_0/main.py "mindfulness meditation" "walking meditation" \
            "body scan meditation" ... --parent meditation

[Python output shows 3 data sources loading]
[Dashboard generates with tree view]

Claude: "Dashboard generated! Opening in browser..."
        [Opens outputs/agent0-dashboard.html]

User: [Reviews dashboard, sees walking meditation has good scores]
      "Drill down on walking meditation"

Claude: [Repeats process - generates 10 walking meditation subtopics]
        [Researches all 10, saves JSON files]
        [Runs Python with --parent "walking meditation"]
        [Dashboard now shows 3 levels: meditation → walking meditation → 10 children]

User: [Finds ultra-specific niche: "walking meditation for anxiety relief"]
      [Demand: 78, Competition: 45, Opportunity: VIABLE]
      "This is the one - Rule of One achieved!"
```

---

## Common Issues & Solutions

### **Issue:** "I get hardcoded patterns instead of real research"

**Cause:** Previous Claude was using deleted `drill_down.py` with fallback patterns

**Solution:**
- `drill_down.py` has been DELETED
- Use Task tool in chat (not Python code) to generate subtopics
- Verify `cache/agent_results/` contains JSON files with real data

### **Issue:** "No agent results found for topic"

**Cause:** Topic hasn't been researched yet (normal!)

**Solution:**
- This is expected behavior
- Claude should research the topic using Task tool
- Save JSON to cache/agent_results/
- Re-run Python to load cached results

### **Issue:** "YouTube shows 1-2 subscriber channels"

**Cause:** YouTube API was disabled (fixed 2025-10-25)

**Status:**
- YouTube Data API v3 now ENABLED
- Quota increase pending (10K → 100K units/day)
- Should see real channel data in next research run

### **Issue:** "Descriptions show market stats instead of 'what it is'"

**Cause:** Agent results missing `description` field

**Solution:**
- Check `cache/agent_results/{topic}.json` has `description` field
- Re-research topic following `AI-Agent-Research-Guide.md`
- Description should explain WHAT the topic is, not market analysis

---

## Maintenance Instructions for Claude

**IMPORTANT:** Update this file when you change the drill-down workflow!

### **When to Update This File:**

✅ **Always update when:**
- You add/remove Python files related to drill-down
- You change how subtopic generation works
- You modify the scoring formula
- You add/remove data sources
- You change the JSON file format
- You discover workflow bugs and fix them
- User corrects your understanding of the process

✅ **Add to this file:**
- New cache file locations
- New documentation files
- Changed command-line arguments
- New troubleshooting issues and solutions
- Process improvements that work

❌ **Don't update for:**
- Minor bug fixes unrelated to workflow
- Dashboard styling changes (unless they affect drill-down UX)
- Documentation typos in other files

### **How to Update:**

1. Read this entire file first (understand current workflow)
2. Make your code/process changes
3. Update relevant sections in THIS file
4. Update "Last Updated" date at top
5. Add note to "Maintenance Log" below
6. Commit with message: "Update drill-down-prd.md - [what changed]"

### **Maintenance Log:**

- **2025-10-25:** Initial creation after deleting drill_down.py. Documented Task tool workflow, deleted paid API approach, clarified Claude does research in chat (not Python).

---

## Success Criteria

You know drill-down is working correctly when:

✅ Claude uses Task tool to generate subtopics (no hardcoded patterns)
✅ Claude researches each subtopic via web search (not paid API)
✅ JSON files saved to `cache/agent_results/` with descriptions
✅ Python loads 3 data sources (Agent + Reddit + YouTube)
✅ Dashboard shows tree with parent-child relationships
✅ Paper icon click shows real description (what topic IS)
✅ Scores reflect real demand data, not guesses
✅ User can drill down 2-3 levels to find "Rule of One" niche
✅ No rate limit errors (Agent research has no limits)
✅ Process works across different Claude sessions (cache persists)

---

## For New Claude Sessions

**If you're a new Claude chat and the user asks to drill down:**

1. **Read these files FIRST:**
   - This file (`drill-down-prd.md`)
   - `Docs/AI-Agent-Research-Guide.md`
   - `Docs/Topic-Description-Workflow.md`

2. **Use Task tool (NOT Python code) to generate subtopics**
   - Prompt is in: `Docs/Grok-drilldown.md`

3. **Research each subtopic (also with Task tool)**
   - Methodology: `Docs/AI-Agent-Research-Guide.md`
   - Save JSON files to `cache/agent_results/`

4. **Run Python when user says so**
   - Command: `python agents/agent_0/main.py <topics> --parent "parent topic"`
   - Python loads cache, doesn't generate subtopics

5. **Update this file if you discover the process has changed**

---

## Related Documentation

- **CLAUDE.md** - Project-level rules (NO PAID APIs, FAIL LOUDLY, etc.)
- **PROJECT_INDEX.md** - High-level project overview
- **Context/[date]/HANDOFF-[date].md** - Daily session summaries
- **Docs/Agent-Research-Workflow.md** - Cross-session agent workflow
- **Docs/Grok-drilldown.md** - Exact Grok prompt for subtopic generation

---

**End of PRD. Keep this file updated as the workflow evolves.**
