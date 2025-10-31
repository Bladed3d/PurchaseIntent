# PRD Update Recommendations - Rate Limits & Tiered Strategy

**Created:** 2025-10-31
**Purpose:** Recommend how to integrate rate limit analysis and tiered strategy into PRD documentation
**Context:** Agent 0 tiered strategy now complete, system-wide rate analysis complete

---

## Summary

You asked: *"Should the rate doc be referenced in our PRD? Should the PRD be updated to reflect the tiered strategy or app structure?"*

**Answer: YES - but strategically.** Here's what to update and why:

---

## Recommended Updates

### **1. Update Main System PRD (PRD-Purchase-Intent-System-v2.md)**

**Status:** Last updated 2025-10-23 (before tiered strategy was implemented)

**What to Add:**

#### **Section: "Changes from v2.0" (create new changelog section at top)**

```markdown
## Changes from v2.0

**Post-Review Updates (2025-10-31):**

1. **Agent 0 Tiered API Strategy Implemented**
   - **Problem Solved:** YouTube quota limited (10K units/day), Google Trends rate limited
   - **Solution:** Three-mode operation (drill-down/regular/validation) balances quota vs confidence
   - **Impact:** Can explore unlimited topics (Reddit-only) + validate 10-20/day (YouTube)
   - **Details:** See `Docs/drill-down-prd.md` (Agent 0 workflow) and `Docs/rate-limit-analysis.md` (system-wide impact)

2. **System-Wide Rate Limit Analysis Completed**
   - **Finding:** Agents 2-4 have ZERO API quota impact (use Task tool, not paid Anthropic API)
   - **Finding:** Agent 1 has LOW impact (primary data from web scraping)
   - **Bottleneck:** YouTube API (10K units/day) limits final validation, not exploration
   - **Capacity:** Can validate 3 topics + research 3 products/day (36% YouTube quota)
   - **Reference:** See `Docs/rate-limit-analysis.md` for detailed quota budgets
```

#### **Section: "Phase 1: Interactive Topic Discovery" (update existing section)**

**Current (lines 70-89):**
```markdown
1. User runs: `/discover-topics productivity`
2. **Agent 0** researches demand signals across:
   - **Google Trends** (pytrends library): Search volume trends, regional interest
   - **Reddit** (PRAW API): Subreddit activity, pain point discussions, engagement metrics
   - **YouTube** (YouTube Data API v3): Video view counts, comment sentiment, channel authority
```

**Proposed Update:**
```markdown
1. User runs: `/discover-topics productivity`
   - **Exploration Mode** (default): `--drill-down-mode` uses Reddit-only (unlimited, 60% confidence)
   - **Validation Mode**: `--enable-youtube` adds YouTube + Trends (quota-limited, 100% confidence)
2. **Agent 0** researches demand signals:
   - **Exploration (unlimited):**
     - **Reddit** (PRAW API): 3,600 calls/hour = unlimited exploration
     - **AI Agent Research** (Task tool): Web search for trend signals
   - **Validation (quota-limited):**
     - **Google Trends** (pytrends): ~15 calls/hour safe limit (with 24hr caching)
     - **YouTube** (Data API v3): 10,000 units/day = 10-20 topics max
3. Dashboard shows quota usage in real-time (visual progress bars)
```

#### **Section: "Technical Architecture" → Add new subsection "API Quota Strategy"**

```markdown
### API Quota Strategy

**Design Principle:** Use unlimited sources for exploration, quota-limited sources for final validation.

**Quota Budgets:**

| API | Daily Limit | Hourly Limit | Agents Using It | Bottleneck? |
|-----|-------------|--------------|-----------------|-------------|
| **Reddit** | Unlimited | 3,600 calls | Agent 0, Agent 1 | ❌ No |
| **Google Trends** | ~360 calls | ~15 calls | Agent 0 only | ❌ No (with caching) |
| **YouTube** | 10,000 units | N/A | Agent 0, Agent 1 | ✅ Yes (primary bottleneck) |
| **Task Tool** | Unlimited | Unlimited | Agents 2, 3, 4 | ❌ No (Claude Pro subscription) |

**System Capacity (with current quotas):**
- **Exploration:** Unlimited topics (Reddit + AI Agent Research)
- **Validation:** 10-20 topics/day (YouTube-limited)
- **Product Research:** 50+ products/day (Agent 1 uses minimal YouTube)
- **Demographics/Personas/Intent:** Unlimited (Agents 2-4 use Task tool)

**If YouTube Quota Increases to 100K:**
- Validation capacity: 100-200 topics/day
- Bottleneck shifts from quota → processing time

**Reference:** See `Docs/rate-limit-analysis.md` for detailed analysis of all 5 agents.
```

#### **Section: "Success Metrics" → Update API costs**

**Current (line 379):**
```markdown
- **API Costs:** $0 (all free tiers within quota limits)
```

**Proposed Update:**
```markdown
- **API Costs:** $0 (all free tier APIs + Claude Pro Task tool)
  - Agent 0: Free (Reddit, Trends, YouTube within quotas)
  - Agent 1: Free (web scraping + minimal Reddit/YouTube)
  - Agents 2-4: $0 marginal cost (Task tool uses Claude Pro subscription, not paid Anthropic API)
  - Unlimited testing with no per-request costs
```

---

### **2. Update Agent 0 Drill-Down PRD (drill-down-prd.md)**

**Status:** Already updated 2025-10-31 with tiered strategy ✅

**Additional Recommended Updates:**

#### **Section: "Related Documentation" (line 498) → Add rate-limit-analysis.md**

**Current:**
```markdown
## Related Documentation

- **CLAUDE.md** - Project-level rules (NO PAID APIs, FAIL LOUDLY, etc.)
- **PROJECT_INDEX.md** - High-level project overview
- **Context/[date]/HANDOFF-[date].md** - Daily session summaries
- **Docs/Agent-Research-Workflow.md** - Cross-session agent workflow
- **Docs/Grok-drilldown.md** - Exact Grok prompt for subtopic generation
```

**Proposed Update:**
```markdown
## Related Documentation

- **CLAUDE.md** - Project-level rules (NO PAID APIs, FAIL LOUDLY, etc.)
- **Docs/rate-limit-analysis.md** - System-wide quota budgets and capacity analysis
- **Docs/5-agents-design.md** - Complete 5-agent architecture specification
- **Docs/PRD-Purchase-Intent-System-v2.md** - Main system PRD (all agents)
- **PROJECT_INDEX.md** - High-level project overview
- **Context/[date]/HANDOFF-[date].md** - Daily session summaries
- **Docs/Agent-Research-Workflow.md** - Cross-session agent workflow
- **Docs/Grok-drilldown.md** - Exact Grok prompt for subtopic generation
```

#### **Section: "Maintenance Log" (line 451) → Add 2025-10-31 entry**

**Current:**
```markdown
### **Maintenance Log:**

- **2025-10-25:** Initial creation after deleting drill_down.py. Documented Task tool workflow, deleted paid API approach, clarified Claude does research in chat (not Python).
```

**Proposed Update:**
```markdown
### **Maintenance Log:**

- **2025-10-25:** Initial creation after deleting drill_down.py. Documented Task tool workflow, deleted paid API approach, clarified Claude does research in chat (not Python).
- **2025-10-31:** Added tiered API strategy (drill-down/regular/validation modes). Updated quota budgets (Reddit unlimited, Trends ~15/hour, YouTube 10K/day). Fixed None-handling bugs for drill-down mode. Added quota visualization to dashboard. Updated related docs to reference rate-limit-analysis.md.
```

---

### **3. Update 5-Agents Design Doc (5-agents-design.md)**

**Status:** Contains Agent 1-4 specifications but may have outdated quota info

**Recommended Updates:**

#### **Section: "Agent 0 Tools & Data Sources" (lines 125-133) → Update quota numbers**

**Current:**
```markdown
| Source | Tool | Purpose | Cost |
|--------|------|---------|------|
| **Google Trends** | pytrends or web scraping | Search volume trends, rising queries | Free |
| **Reddit** | PRAW API | Pain points in discussions, subreddit activity | Free (60 req/min) |
| **Amazon Kindle** | Playwright | Bestseller gaps, review complaints | Free |
| **YouTube** | YouTube Data API | Video topics, comment engagement | Free (10k quota/day) |
| **X/Twitter** | Web scraping or API | Trending discussions, viral threads | Free tier |
```

**Proposed Update:**
```markdown
| Source | Tool | Purpose | Quota Limit | Cost |
|--------|------|---------|-------------|------|
| **Google Trends** | pytrends | Search volume trends, rising queries | ~15 calls/hour (with caching) | Free |
| **Reddit** | PRAW API | Pain points in discussions, subreddit activity | 3,600 calls/hour (effectively unlimited) | Free |
| **YouTube** | YouTube Data API v3 | Video topics, comment engagement | 10,000 units/day (quota-limited) | Free |
| **AI Agent Research** | Task tool (Claude Pro) | Web search for trend signals | Unlimited | $0 (included) |

**Note:** Amazon and X/Twitter deferred post-MVP due to scraping complexity. Agent 0 now uses tiered strategy:
- **Drill-down mode** (--drill-down-mode): Reddit + AI Agent only (unlimited)
- **Regular mode**: Reddit + Google Trends (low quota)
- **Validation mode** (--enable-youtube): All sources (YouTube-limited)

**Reference:** See `Docs/drill-down-prd.md` and `Docs/rate-limit-analysis.md`
```

#### **Section: "Agent 1 Tools & Data Sources" (line 288-295) → Add note about quota impact**

**Proposed Addition After Table:**
```markdown
**Quota Impact Analysis:**
- Primary data source: **Playwright scraping** (Amazon, Goodreads) - NO API limits
- Reddit: 10-20 calls per product (~0.5% of hourly quota)
- YouTube: 100-200 units per product (~2% of daily quota)
- **Reusability:** Comparable products cached and reused across similar topics
- **Capacity:** Can research 50+ products/day before hitting limits
- **Reference:** See `Docs/rate-limit-analysis.md` for detailed breakdown
```

#### **Section: "Agent 2 Tools & Data Sources" (line 559-566) → Update Claude API cost**

**Current:**
```markdown
| Tool | Purpose | Cost |
|------|---------|------|
| **Claude API** | Extract demographics from text (batch 20 reviews per call) | ~$0.50 per 100 reviews |
```

**Proposed Update:**
```markdown
| Tool | Purpose | Quota Limit | Cost |
|------|---------|-------------|------|
| **Task Tool (Claude Pro)** | Extract demographics from text (batch 20 reviews per call) | Unlimited | $0 (included in subscription) |
| **sentence-transformers** | Cluster similar customer profiles | None | Free (local) |
| **PRAW** | Analyze subreddit user activity (for overlap insights) | 3,600 calls/hour | Free |
| **Web search (Task tool)** | Find benchmark data (Pew Research, Statista) | Unlimited | $0 (included) |

**IMPORTANT:** Use **Task tool** (Claude Pro subscription), NOT paid Anthropic API.
- Task tool has unlimited quota (included in Claude Pro)
- Paid Anthropic API violates CLAUDE.md rule: "NO PAID APIs"
- Agent 2 has ZERO API quota impact on system
- **Reference:** See `Docs/rate-limit-analysis.md`
```

#### **Section: "Cost & Time Estimates" (throughout doc) → Update all Claude API costs to $0**

**Example - Agent 4 (lines 2106-2114):**

**Current:**
```markdown
| Resource | Cost | Time |
|----------|------|------|
| Claude API (ParaThinker: 500 personas × 8 paths) | ~$0.50 | 5 min |
```

**Proposed Update:**
```markdown
| Resource | Tool | Cost | Time |
|----------|------|------|------|
| ParaThinker (500 personas × 8 paths = 4,000 simulations) | Task tool (Claude Pro) | $0 | 5-10 min |
| SSR embedding (local sentence-transformers) | Local model | $0 | 2 min |
| Psychographic weighting & aggregation | Local processing | $0 | 1 min |
| **Total** | | **$0** | **8-13 min** |

**Note:** Uses Task tool (Claude Pro subscription), not paid Anthropic API. Zero marginal cost per product tested.
```

---

### **4. Update CLAUDE.md Project Context**

**Recommended Addition:**

#### **Section: "Project Context" → Add "API Quota Strategy" subsection**

**After the existing "Agents Available" section, add:**

```markdown
**API Quota Budgets:**
- Reddit: 3,600 calls/hour (effectively unlimited for our usage)
- Google Trends: ~15 calls/hour safe limit (with 24hr caching)
- YouTube: 10,000 units/day (primary bottleneck for validation)
- Task Tool: Unlimited (Claude Pro subscription)

**Tiered Strategy:**
- Exploration: Use --drill-down-mode (Reddit-only, unlimited)
- Validation: Use --enable-youtube (quota-limited, 10-20 topics/day)
- Product Research: Agent 1 uses minimal quota (web scraping first)
- Demographics/Personas/Intent: Agents 2-4 use Task tool (zero quota cost)

**Reference:** See `Docs/rate-limit-analysis.md` for system-wide capacity analysis.
```

---

## Implementation Priority

### **High Priority (Do First):**

1. ✅ **Update drill-down-prd.md** → Add maintenance log entry (already mostly done)
2. ⚠️ **Update PRD-Purchase-Intent-System-v2.md** → Add v2.0 changes section + quota strategy
3. ⚠️ **Update CLAUDE.md** → Add quota budgets reference

**Why:** These are the primary docs future Claude chats will read. They need to know:
- Tiered strategy exists and why
- Quota budgets for planning Agents 1-4
- Where to find detailed rate limit analysis

### **Medium Priority (Do Soon):**

4. 📋 **Update 5-agents-design.md** → Fix outdated quota numbers, clarify Task tool usage
5. 📋 **Create cross-reference** → Ensure all PRDs link to rate-limit-analysis.md

**Why:** Agent 1-4 implementation is coming soon. Developers need accurate quota info.

### **Low Priority (Nice to Have):**

6. 📝 **Update PROJECT_INDEX.md** → Add rate-limit-analysis.md to documentation index
7. 📝 **Create README section** → Quick quota reference for new developers

**Why:** Helpful for discoverability but not critical for immediate work.

---

## Rationale: Why These Updates Matter

### **For Future Claude Chats:**

**Without Updates:**
```
Future Claude: "Let me read the PRD to understand the system..."
[Reads PRD v2.0 from 2025-10-23]
[No mention of tiered strategy or quota analysis]
[Assumes YouTube is always used for Agent 0]
[Plans Agent 1-4 assuming $0.50 Claude API costs]
❌ WRONG ASSUMPTIONS
```

**With Updates:**
```
Future Claude: "Let me read the PRD to understand the system..."
[Reads PRD v2.0 with 2025-10-31 updates]
[Sees tiered strategy in changes section]
[Finds link to rate-limit-analysis.md]
[Understands quota budgets and Task tool strategy]
✅ CORRECT UNDERSTANDING
```

### **For You (The Human):**

**Without Updates:**
- PRD says "Agent 2 costs $0.50 per 100 reviews" → You might think it's expensive
- PRD doesn't mention drill-down mode → You might forget it exists
- No quota budgets documented → Hard to plan daily workflow

**With Updates:**
- Clear documentation of $0 costs (Task tool strategy)
- Tiered strategy documented with examples
- Quota budgets show realistic daily capacity
- Future decisions based on accurate data

---

## Suggested Approach

### **Option A: Update Now (Recommended)**

**Pros:**
- Documentation stays synchronized with implementation
- Future Claude chats have accurate context
- Capture decisions while they're fresh
- Reference docs are ready for Agent 1 implementation

**Cons:**
- Takes ~30-60 minutes to update all docs
- Need to commit multiple file changes

**Command:**
```bash
# Update all 4 docs in one session
1. Update PRD-Purchase-Intent-System-v2.md
2. Update drill-down-prd.md (maintenance log)
3. Update 5-agents-design.md (quota tables)
4. Update CLAUDE.md (quota reference)
5. Commit: "Sync PRDs with implemented tiered strategy and quota analysis"
```

### **Option B: Update Incrementally**

**Pros:**
- Can prioritize high-impact docs first
- Spread work across multiple sessions
- Less context switching

**Cons:**
- Risk of forgetting to update some docs
- Docs temporarily out of sync
- Future Claude might read outdated info

**Timeline:**
- Today: Update PRD v2.0 + CLAUDE.md (high priority)
- This week: Update 5-agents-design.md (before Agent 1 work)
- Later: Update cross-references and indexes

### **Option C: Wait Until Needed**

**Pros:**
- No immediate work required
- Update only when starting Agent 1

**Cons:**
- ❌ Future Claude chats have outdated context
- ❌ Decisions not captured while fresh
- ❌ Risk of forgetting implementation details

**Not Recommended:** Documentation drift causes more problems than it solves.

---

## Recommendation

**I recommend Option A: Update all 4 docs now.**

**Estimated Time:** 30-60 minutes total
- PRD v2.0: ~15 min (add changes section, quota strategy)
- drill-down-prd.md: ~5 min (maintenance log entry)
- 5-agents-design.md: ~20 min (update tables, add Task tool notes)
- CLAUDE.md: ~5 min (add quota reference)
- Commit + review: ~10 min

**Benefits:**
✅ Documentation matches implementation
✅ Future Claude chats have accurate context
✅ Rate limit analysis is properly integrated
✅ Ready to start Agent 1 work with confidence
✅ Decisions captured while details are fresh

**Next Steps:**
1. Review this recommendation doc
2. Decide: Option A, B, or C?
3. If Option A: I can make the updates now in this session
4. If Option B/C: Create TodoList for tracking

---

## What Do You Think?

**Questions to Consider:**

1. **Urgency:** Do you plan to start Agent 1 work soon? (If yes → Option A)
2. **Completeness:** Do you want docs fully synced? (If yes → Option A)
3. **Time:** Do you have 30-60 min now? (If no → Option B)

Let me know which option you prefer, and I'll proceed accordingly!
