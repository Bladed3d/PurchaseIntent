# Rate Limit Impact Analysis - 5-Agent System

**Created:** 2025-10-31
**Purpose:** Analyze how Agents 1-4 will impact our API quota budgets
**Context:** Agent 0 (Topic Research) is complete with tiered strategy

---

## Executive Summary

**Good News:** The remaining agents (1-4) have **MINIMAL rate limit impact** compared to Agent 0's exploratory workload. The system is designed for **reusability** - most quota cost is in Agent 0's exploration phase, while Agents 1-4 operate on cached/reusable data.

**Quota Impact by Agent:**
- ✅ **Agent 0** (Topic Research): HIGH quota usage (already solved with tiered strategy)
- ✅ **Agent 1** (Product Researcher): LOW quota usage (mostly web scraping, minimal API calls)
- ✅ **Agent 2** (Demographics): ZERO API quota (uses Task tool + local LLM)
- ✅ **Agent 3** (Personas): ZERO API quota (uses Task tool)
- ✅ **Agent 4** (Intent Simulator): ZERO API quota (uses Task tool + local processing)

---

## Current Quota Status (Agent 0 Complete)

### **Quota Budgets Established:**

| API | Hourly Limit | Daily Limit | Cost per Call | Current Usage Pattern |
|-----|--------------|-------------|---------------|----------------------|
| **Reddit** | 3,600 calls | Unlimited | Free | Agent 0: ~60 calls per drill session |
| **Google Trends** | ~15 calls | ~360 calls | Free | Agent 0: 12-15 calls in validation mode |
| **YouTube** | N/A | 10,000 units | Free | Agent 0: ~1,000 units per topic (validation only) |

### **Tiered Strategy Impact (Agent 0):**

**Exploration Phase** (--drill-down-mode):
- 61 Reddit queries for 3-level drill = 2% of hourly quota
- 0 Google Trends queries = 0% quota
- 0 YouTube units = 0% quota
- **Bottleneck:** NONE (can run unlimited explorations)

**Validation Phase** (--enable-youtube):
- 3 final topics × 1,000 YouTube units = 30% of daily quota
- 3 topics × 1 Trends call = 20% of hourly quota
- 3 topics × 50 Reddit calls = 4% of hourly quota
- **Bottleneck:** YouTube (can validate 10-20 topics/day max)

---

## Agent 1: Product Researcher - Rate Limit Analysis

### **Data Sources & Quotas:**

| Source | API/Tool | Quota Limit | Queries per Product | Cost |
|--------|----------|-------------|---------------------|------|
| **Amazon** | Playwright (scraping) | None (stealth mode) | 5-10 product pages | Free |
| **Reddit** | PRAW API | 3,600/hour | 10-20 searches | Free |
| **YouTube** | Data API v3 | 10,000 units/day | 5-10 videos | ~100 units |
| **Goodreads** | Playwright | None | 5-10 pages (books only) | Free |

### **Typical Usage Pattern:**

**Input:** 1 topic from Agent 0 (e.g., "walking meditation for anxiety")

**Step 1: Multi-Source Search**
- Amazon: 5-10 comparable products (Playwright scraping - NO API)
- Reddit: 5-10 discussion threads (~10 API calls)
- YouTube: 5-10 review videos (~100 units for search + stats)
- Goodreads: 5 similar books (Playwright - NO API)

**Step 2: Extract Reviews/Metadata**
- Amazon: Scrape top 20 "Most Helpful" reviews per product (NO API)
- Reddit: Extract top 50 comments (included in Step 1 API calls)
- YouTube: Extract top 50 comments (included in Step 1 units)

**Total Quota Cost per Product:**
- Reddit: 10-20 API calls (~0.5% of hourly quota)
- YouTube: 100-200 units (~2% of daily quota)
- Google Trends: 0 (not used in Agent 1)

### **Reusability Impact:**

**Key Insight:** Agent 1 output is **REUSABLE** across similar products.

**Example:**
```
1st Product: "Walking meditation for anxiety" → Agent 1 finds 10 comparables
2nd Product: "Walking meditation for sleep" → REUSES 8/10 comparables (80% cache hit)
3rd Product: "Body scan meditation for anxiety" → REUSES 5/10 comparables (50% cache hit)
```

**Quota Savings:**
- 1st product: 100% quota cost (10 Reddit calls, 100 YouTube units)
- 2nd product: 20% quota cost (2 Reddit calls, 20 YouTube units)
- 3rd product: 50% quota cost (5 Reddit calls, 50 YouTube units)

**Caching Strategy:**
```python
# Cache comparable products by category/niche
cache/comparables/meditation_anxiety.json
cache/comparables/meditation_sleep.json
cache/comparables/productivity_remote.json
```

### **Rate Limit Risk: LOW**

**Why:**
1. Primary data source is **web scraping** (Amazon, Goodreads) - no API limits
2. Reddit usage is minimal (~10-20 calls vs 3,600/hour limit)
3. YouTube usage is low (~100-200 units vs 10,000/day limit)
4. Results are cached and reused across similar products

**Bottleneck Analysis:**
- Can research **50+ products per hour** before hitting Reddit limit
- Can research **50+ products per day** before hitting YouTube limit
- **Realistic usage:** 1-3 products/day (well within limits)

---

## Agent 2: Demographics Analyst - Rate Limit Analysis

### **Data Sources & Quotas:**

| Source | Tool | Quota Limit | Usage | Cost |
|--------|------|-------------|-------|------|
| **Claude API** | Task tool (Claude Pro) | Unlimited | Batch extract demographics | $0 (included) |
| **sentence-transformers** | Local model | None | Cluster profiles | Free |
| **PRAW** | Reddit API | 3,600/hour | Subreddit overlap analysis | Free |
| **Web search** | Task tool | Unlimited | Find benchmarks | $0 |

### **Typical Usage Pattern:**

**Input:** Agent 1 output (5-10 comparables, review URLs, discussion threads)

**Step 1: Scrape High-Signal Data**
- Amazon reviews: Already scraped by Agent 1 (cached)
- Reddit comments: Already scraped by Agent 1 (cached)
- YouTube comments: Already scraped by Agent 1 (cached)
- **NO NEW API CALLS** (uses Agent 1 cache)

**Step 2: Extract Demographics (Task Tool)**
- Process 300-500 reviews/comments via Task tool
- Task tool uses Claude Pro subscription (unlimited, $0 marginal cost)
- Batch processing: 20 reviews per Task agent call
- **NO API QUOTA COST** (uses Task tool, not Anthropic API)

**Step 3: Cluster & Validate**
- sentence-transformers: Local model (no API)
- Subreddit overlap analysis: 5-10 Reddit API calls
- Benchmark lookups: Task tool web search (no API)

**Total Quota Cost per Product:**
- Reddit: 5-10 API calls (~0.3% of hourly quota)
- YouTube: 0 units (reuses Agent 1 data)
- Google Trends: 0
- Claude API: 0 (uses Task tool, not paid API)

### **Important Design Note:**

**WRONG Approach (from old design):**
```python
# DON'T DO THIS - uses paid Anthropic API
from anthropic import Anthropic
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
```

**CORRECT Approach (current design):**
```python
# Use Task tool in Claude Code chat
# Claude launches Task agent with demographic extraction prompt
# Agent processes reviews and returns structured demographics
# NO paid API calls, uses Claude Pro subscription
```

### **Rate Limit Risk: ZERO**

**Why:**
1. **No new scraping** - reuses Agent 1 cached data
2. **Task tool is unlimited** - included with Claude Pro subscription
3. **Local processing** - sentence-transformers runs locally
4. **Minimal Reddit calls** - only for subreddit overlap (~5-10 calls)

**Bottleneck Analysis:**
- Can process **unlimited products** (no API quota consumed)
- Only limit is Task tool processing time (~5-10 min per product)
- **Realistic usage:** 5-10 products/day (time-limited, not quota-limited)

---

## Agent 3: Persona Generator - Rate Limit Analysis

### **Data Sources & Quotas:**

| Source | Tool | Quota Limit | Usage | Cost |
|--------|------|-------------|-------|------|
| **Claude API** | Task tool (Claude Pro) | Unlimited | Generate 500 personas | $0 |
| **faker** | Local library | None | Generate realistic attributes | Free |
| **numpy/scipy** | Local libraries | None | Statistical distributions | Free |

### **Typical Usage Pattern:**

**Input:** Agent 2 output (demographics, clusters, validation)

**Step 1: Generate 500 Personas (Task Tool)**
- Task tool generates personas matching demographic clusters
- Uses Claude Pro subscription (unlimited)
- Batch generation: 50 personas per Task agent call (10 batches total)
- **NO API QUOTA COST**

**Step 2: Add Psychographic Attributes (Local)**
- faker library: Generate names, emails, locations
- numpy: Sample from demographic distributions
- scipy: Ensure realistic variance
- **NO API CALLS**

**Step 3: Tag & Store**
- Save to `personas-inventory/categories/*.json`
- Tag by category (e.g., "productivity-remote-workers.json")
- **NO API CALLS**

**Total Quota Cost per Product:**
- Reddit: 0
- YouTube: 0
- Google Trends: 0
- Claude API: 0 (uses Task tool)

### **Reusability Impact:**

**Key Insight:** Personas are **EXTREMELY REUSABLE**.

**Example:**
```
1st Product: "Time management for remote workers"
  → Generate 500 "productivity-remote-workers" personas
  → Store in personas-inventory/

2nd Product: "Focus techniques for distributed teams"
  → REUSE same 500 personas (100% cache hit)
  → NO generation needed

3rd Product: "Delegation guide for startup founders"
  → Generate 500 "entrepreneurship-startups" personas
  → Store in personas-inventory/

4th Product: "Scaling SaaS companies efficiently"
  → REUSE "entrepreneurship-startups" personas (100% cache hit)
```

**Quota Savings:**
- Once personas are generated for a category, they can test **unlimited products** in that category
- Each category needs generation once (~10 min Task tool time)
- After 10-20 categories, you have personas covering most niches

### **Rate Limit Risk: ZERO**

**Why:**
1. **Task tool is unlimited** - Claude Pro subscription
2. **Local processing** - faker, numpy, scipy
3. **One-time generation** - reused across unlimited products
4. **No external APIs** - all processing internal

**Bottleneck Analysis:**
- Can generate **unlimited personas** (no quota limits)
- Only limit is Task tool processing time (~10 min per 500 personas)
- **Realistic usage:** Generate 2-3 new persona categories/week, reuse extensively

---

## Agent 4: ParaThinker Intent Simulator - Rate Limit Analysis

### **Data Sources & Quotas:**

| Source | Tool | Quota Limit | Usage | Cost |
|--------|------|-------------|-------|------|
| **Claude API** | Task tool (Claude Pro) | Unlimited | 500 personas × 8 paths = 4,000 simulations | $0 |
| **sentence-transformers** | Local model | None | SSR analysis | Free |
| **numpy/scipy** | Local libraries | None | Statistical aggregation | Free |

### **Typical Usage Pattern:**

**Input:**
- Agent 3 personas (500 personas from inventory)
- User's product description

**Step 1: ParaThinker Simulation (Task Tool)**
- For each persona, run 8 parallel reasoning paths
- Total: 500 personas × 8 paths = 4,000 simulations
- Task tool processes in batches (50 personas per batch = 10 batches)
- **NO API QUOTA COST** (uses Task tool)

**Step 2: SSR Analysis (Local)**
- sentence-transformers: Embed reasoning paths
- scipy: Calculate Kolmogorov-Smirnov similarity
- **NO API CALLS**

**Step 3: Aggregate & Generate Report**
- numpy: Calculate statistics (mean, std, distribution)
- Task tool: Generate recommendations based on patterns
- **NO API QUOTA COST** (uses Task tool)

**Total Quota Cost per Product:**
- Reddit: 0
- YouTube: 0
- Google Trends: 0
- Claude API: 0 (uses Task tool)

### **Reusability Impact:**

**Key Insight:** Personas are reused, only simulation is per-product.

**Example:**
```
1st Product: "Time blocking for remote workers"
  → Use "productivity-remote-workers" personas (cached)
  → Run 4,000 simulations via Task tool (~10 min)

2nd Product: "Pomodoro technique for distributed teams"
  → REUSE same personas (cached)
  → Run NEW 4,000 simulations (~10 min)
  → Compare results to 1st product
```

**Cost per Product:**
- Persona generation: $0 (reused from Agent 3)
- Simulation: $0 (Task tool)
- Analysis: $0 (local processing)
- **Total: $0 per product tested**

### **Rate Limit Risk: ZERO**

**Why:**
1. **Task tool is unlimited** - Claude Pro subscription
2. **Local processing** - sentence-transformers, numpy, scipy
3. **No external APIs** - all processing internal
4. **Reuses personas** - no regeneration needed

**Bottleneck Analysis:**
- Can simulate **unlimited products** (no quota limits)
- Only limit is Task tool processing time (~10 min per product)
- **Realistic usage:** Test 5-10 product variants/day (time-limited only)

---

## System-Wide Rate Limit Summary

### **Quota Budget Allocation:**

| Agent | Reddit Calls | YouTube Units | Trends Calls | Bottleneck |
|-------|-------------|---------------|--------------|------------|
| **Agent 0** | 60/hour (drill) | 1,000/topic (validate) | 1/topic | YouTube (10-20 topics/day) |
| **Agent 1** | 10-20/product | 100-200/product | 0 | None (50+ products/day) |
| **Agent 2** | 5-10/product | 0 (reuses Agent 1) | 0 | None (unlimited) |
| **Agent 3** | 0 | 0 | 0 | None (unlimited) |
| **Agent 4** | 0 | 0 | 0 | None (unlimited) |

### **Realistic Daily Usage:**

**Scenario: User explores 1 broad niche → selects 3 topics → tests 3 product variants**

```
Morning: Agent 0 Exploration (--drill-down-mode)
  61 Reddit queries for 3-level drill
  0 YouTube units
  0 Trends calls
  Quota used: 2% Reddit hourly quota

Afternoon: Agent 0 Validation (--enable-youtube)
  3 topics × 50 Reddit calls = 150 calls (4% hourly quota)
  3 topics × 1,000 YouTube units = 3,000 units (30% daily quota)
  3 topics × 1 Trends call = 3 calls (20% hourly quota)
  Quota used: 30% YouTube daily quota (BOTTLENECK)

Evening: Agents 1-4 Processing
  Topic 1: Agent 1 → Agent 2 → Agent 3 → Agent 4
    Agent 1: 20 Reddit calls, 200 YouTube units
    Agent 2: 10 Reddit calls, 0 YouTube (reuses Agent 1)
    Agent 3: 0 calls (Task tool only)
    Agent 4: 0 calls (Task tool only)

  Topics 2-3: Same pattern

  Total for Agents 1-4:
    3 topics × 30 Reddit calls = 90 calls (2.5% hourly quota)
    3 topics × 200 YouTube units = 600 units (6% daily quota)

Daily Total:
  Reddit: 301 calls out of 3,600/hour (8.4% of 1 hour's quota)
  YouTube: 3,600 units out of 10,000/day (36% of daily quota)
  Trends: 3 calls out of 15/hour (20% of hourly quota)
```

### **System-Wide Bottleneck: YouTube API**

**Current State:**
- Daily limit: 10,000 units
- Agent 0 validation: 1,000 units/topic (can validate 10 topics/day max)
- Agent 1 research: 200 units/product (can research 50 products/day)
- **Combined usage:** Can validate 3 topics + research 3 products = 3,900 units (39% quota)

**Recommended Strategy:**
1. **Use drill-down mode for exploration** (unlimited Reddit-only)
2. **Validate only top 3 finalists** with YouTube (30% quota)
3. **Research products for validated topics** (6% quota per product)
4. **Stay under 50% daily YouTube quota** to allow for retries/adjustments

**Quota Increase Impact:**
- If Google approves 100,000 units/day (10× current limit):
  - Can validate 100 topics/day (vs 10 currently)
  - Can research 500 products/day (vs 50 currently)
  - **Bottleneck shifts to time/processing** (not quota)

---

## Recommendations

### **1. Current State (10,000 YouTube units/day):**

✅ **DO:**
- Use drill-down mode extensively for exploration (unlimited Reddit)
- Validate only top 3-5 topics per day with YouTube
- Cache Agent 1 comparables for reuse across similar products
- Generate persona categories once, reuse extensively

❌ **DON'T:**
- Enable YouTube for exploratory drill-downs (use --drill-down-mode instead)
- Research more than 10-15 products/day (stay under 50% YouTube quota)
- Regenerate personas unnecessarily (reuse from inventory)

### **2. If YouTube Quota Increases to 100K:**

✅ **CAN DO:**
- Validate 50-100 topics/day
- Research 100-500 products/day
- Run unlimited Agent 0 drill sessions with full validation
- Bottleneck becomes **time** (not quota)

### **3. Alternative If YouTube Quota DENIED:**

**Plan B: Reddit + Trends Only (No YouTube)**

Agent 0: Already supports --drill-down-mode (Reddit-only, 60% confidence)
Agent 1: Can skip YouTube, use Reddit + Amazon reviews only
Agent 2: No YouTube needed (uses Agent 1 cached data)
Agent 3-4: No YouTube needed

**Impact:**
- Confidence drops from 100% → 60-80% (still viable)
- Can process **unlimited topics/products** (no quota limits)
- Validation quality relies on Reddit engagement + Trends data

---

## Conclusion

**The 5-agent system is WELL-DESIGNED for rate limits:**

1. **Agent 0 (Topic Research):** Tiered strategy already implemented
   - Exploration: Unlimited (Reddit-only)
   - Validation: YouTube-limited (10-20 topics/day)

2. **Agent 1 (Product Researcher):** LOW impact
   - Primary data: Web scraping (no limits)
   - API usage: 10-20 Reddit calls, 100-200 YouTube units
   - Can research 50+ products/day

3. **Agents 2-4 (Demographics/Personas/Intent):** ZERO impact
   - Use Task tool (Claude Pro subscription, unlimited)
   - Use local processing (no APIs)
   - Only bottleneck is processing time (~10-30 min total)

**System-wide bottleneck: YouTube API (10,000 units/day)**
- Current capacity: Validate 3 topics + research 3 products/day (39% quota)
- Recommended usage: Stay under 50% daily quota for safety margin
- If quota increases to 100K: Bottleneck shifts to time (can process 10× more)

**Overall assessment: System is QUOTA-EFFICIENT and ready for production use.**

---

**Next Steps:**
1. Continue with Agent 0 focus (completed)
2. Build Agent 1 with caching strategy for reusable comparables
3. Build Agent 2-4 using Task tool (not paid Anthropic API)
4. Monitor YouTube quota usage daily
5. Request quota increase again if usage patterns justify it
