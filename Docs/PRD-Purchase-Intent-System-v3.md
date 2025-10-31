# Purchase Intent System - PRD

**Version:** 3.0 - Production Implementation Specification
**Date:** 2025-10-31
**Status:** Agent 0 Complete, Ready for Agents 1-4 Development
**Previous Version:** 2.0 (archived as PRD-Purchase-Intent-System-v2.md)

---

## Changes from v2.0

**Implementation Updates (2025-10-31):**

### **1. Agent 0 Tiered API Strategy - IMPLEMENTED ✅**

**Problem Solved:**
- YouTube quota denied increase (stuck at 10K units/day)
- Google Trends has unpredictable rate limits (~15 calls/hour safe)
- Need unlimited exploration capability for drill-down workflow

**Solution - Three Operating Modes:**

| Mode | CLI Flag | Data Sources | Quota Cost | Confidence | Use Case |
|------|----------|--------------|------------|------------|----------|
| **Drill-Down** | `--drill-down-mode` | Reddit + AI Agent Research | ZERO | 60% | Explore 20-100 topics |
| **Regular** | *(default)* | Reddit + Google Trends | Low (~15 Trends/hour) | 100% | Standard validation |
| **Validation** | `--enable-youtube` | Reddit + Trends + YouTube | High (~1,000 YouTube/topic) | 100% | Final 1-3 topics only |

**Impact:**
- ✅ Can explore **unlimited topics** (Reddit-only mode)
- ✅ Can validate **10-20 topics/day** (YouTube-limited mode)
- ✅ Dashboard shows **real-time quota usage** (visual progress bars)
- ✅ All **None-handling bugs fixed** for drill-down mode

**Files Updated:**
- `agents/agent_0/config.py` - Added mode flags
- `agents/agent_0/main.py` - CLI parsing + conditional API calls
- `agents/agent_0/scoring.py` - YouTube scoring + None-handling
- `agents/agent_0/dashboard.py` - Quota visualization
- `Docs/drill-down-prd.md` - Complete workflow documentation

**Reference:** See `Docs/drill-down-prd.md` for detailed workflow

---

### **2. System-Wide Rate Limit Analysis - COMPLETED ✅**

**Finding:** Agents 2-4 have **ZERO API quota impact**

| Agent | Primary Tool | API Quota Cost | Capacity |
|-------|--------------|----------------|----------|
| **Agent 0** | Reddit/Trends/YouTube | HIGH (YouTube bottleneck) | 10-20 topics/day (validation) |
| **Agent 1** | Playwright scraping | LOW (10-20 Reddit, 100-200 YouTube) | 50+ products/day |
| **Agent 2** | **Task tool** (Claude Pro) | **ZERO** | Unlimited |
| **Agent 3** | **Task tool** (Claude Pro) | **ZERO** | Unlimited |
| **Agent 4** | **Task tool** (Claude Pro) | **ZERO** | Unlimited |

**Key Discovery:** Original design specified paid Anthropic API for Agents 2-4 (~$0.50 per product). Corrected to use **Task tool** (Claude Pro subscription) instead → **$0 marginal cost**.

**System-Wide Bottleneck:** YouTube API (10,000 units/day)
- Current capacity: Validate 3 topics + research 3 products/day (36% quota)
- Recommended: Stay under 50% daily quota for safety margin
- If quota increases to 100K: Bottleneck shifts to time (not quota)

**Reference:** See `Docs/rate-limit-analysis.md` for detailed quota budgets

---

### **3. Agent 0 LED Breadcrumbs - IMPLEMENTED ✅**

**Added YouTube LED range (530-539):**
- LED 530: youtube_search_api_call
- LED 531: youtube_search_complete (videos found)
- LED 532: fetching_video_statistics
- LED 533: processing_statistics
- LED 534: youtube_success
- LED 535: API failure (trail.fail)
- LED 536: quota_exceeded

**Status:** All Agent 0 operations fully instrumented across all modes

---

### **4. Documentation Structure - REORGANIZED ✅**

**Created Specialized PRDs:**

| Document | Purpose | Audience | Status |
|----------|---------|----------|--------|
| **This file** (PRD-v3.md) | System overview, all 5 agents | New Claude chats, stakeholders | ✅ Current |
| `drill-down-prd.md` | Agent 0 workflow, tiered strategy | Developers, Agent 0 users | ✅ Updated 2025-10-31 |
| `5-agents-design.md` | Deep technical specs, all agents | Developers, architects | ⚠️ Needs quota updates |
| `rate-limit-analysis.md` | Quota budgets, capacity planning | Developers, future Claude chats | ✅ Created 2025-10-31 |

**For New Claude Chats:**
1. Read **this file** (PRD-v3.md) first - complete system overview
2. Read `Docs/drill-down-prd.md` - Agent 0 is implemented, understand tiered workflow
3. Read `Docs/rate-limit-analysis.md` - quota budgets for planning Agents 1-4
4. Read `Docs/5-agents-design.md` - deep technical specs when implementing
5. Read `CLAUDE.md` - project rules (NO PAID APIs, FAIL LOUDLY, LED ranges)

---

## Goal

Build an AI-powered synthetic focus group system that predicts consumer purchase intent for digital products (ebooks) in minutes at zero marginal cost, achieving 7-12% higher accuracy than human focus groups.

---

## Current Status

### ✅ **Agent 0 (Topic Research) - COMPLETE**

**What's Working:**
- Three-mode operation (drill-down/regular/validation)
- Drill-down workflow with tree navigation
- Real-time quota visualization in dashboard
- LED breadcrumbs (500-599 range including YouTube 530-539)
- None-handling for all edge cases

**CLI Commands:**
```bash
# Exploration (unlimited)
python agents/agent_0/main.py --drill-down-mode "meditation"

# Regular (low quota)
python agents/agent_0/main.py "meditation"

# Validation (high quota, final topics only)
python agents/agent_0/main.py --enable-youtube "walking meditation for anxiety"
```

**Deliverables:**
- `outputs/agent0-dashboard.html` - Interactive chart with quota bars
- `outputs/topic-selection.json` - Scored topics for Agent 1 input
- `cache/drill_trail.json` - Tree structure for drill-down navigation
- `cache/agent_results/{topic}.json` - AI agent research cache

**Next Step:** User selects top topic(s) from dashboard → feeds to Agent 1

---

### ⏳ **Agents 1-4 - NOT STARTED**

**Ready to Build:**
- Agent 0 provides validated topics with demand scores
- Rate limit analysis complete (know quota budgets)
- Task tool strategy clarified (not paid API)
- LED ranges allocated (1500-1599, 2500-2599, 3500-3599, 4500-4599)

**Recommended Build Order:**
1. **Agent 1** (Product Researcher) - Needs Agent 0 topics as input
2. **Agent 2** (Demographics) - Depends on Agent 1 comparables
3. **Agent 3** (Personas) - Depends on Agent 2 demographics
4. **Agent 4** (Intent Simulator) - Depends on Agent 3 personas

---

## Scope

**Included:**
- CLI-based workflow with slash commands (`/discover-topics`, `/research-products`)
- 5 autonomous agents: Topic Research → Product Research → Demographics → Persona Generation → Intent Prediction
- HTML dashboards with Chart.js visualizations + quota monitoring
- LED breadcrumb instrumentation (ranges 500-4599) for autonomous debugging
- Human checkpoints for validation between agent runs (with confidence-based failure gates)
- Persona reusability (test unlimited products with same 400 personas)
- Tiered API strategy (exploration vs validation modes)

**Excluded:**
- Web UI or desktop application (CLI only for MVP)
- Real-time collaborative features (single-user sessions)
- API endpoints or SaaS offering (in-house tool only)
- Integration with external CRM/marketing platforms
- Non-ebook product categories (future expansion)

---

## User Experience

### Phase 1: Interactive Topic Discovery (Agent 0)

**Workflow:**

1. **User runs exploration mode** (unlimited):
   ```bash
   /discover-topics meditation --drill-down-mode
   ```

2. **Agent 0 researches demand signals** (Reddit + AI Agent Research):
   - Reddit: Subreddit activity, pain points, engagement metrics
   - AI Agent Research (Task tool): Web search for trend signals
   - **No quota cost** (Reddit: 3,600/hour, Task tool: unlimited)

3. **Dashboard auto-opens** showing:
   - Top 10 topics ranked by composite demand score
   - Quota usage bars (Reddit: unlimited, Trends: 0, YouTube: 0)
   - Tree navigation for drill-down to Level 2, 3
   - Click topic → "Drill down further" or "Validate with YouTube"

4. **User drills down** to find ultra-specific niche:
   ```
   Level 0: meditation (too broad)
     ↓
   Level 1: walking meditation (still competitive)
     ↓
   Level 2: walking meditation for anxiety (Rule of One - specific niche)
   ```

5. **User validates top 3 finalists** with YouTube:
   ```bash
   python agents/agent_0/main.py --enable-youtube \
     "walking meditation for anxiety" \
     "body scan meditation for sleep" \
     "loving kindness meditation"
   ```
   - Adds YouTube + Google Trends data (quota cost: 3,000 units)
   - Dashboard shows 100% confidence scores (all 3 sources)
   - Quota bars update: YouTube 30%, Trends 20%

6. **User selects final topic** from dashboard

**Deliverable:** `data/sessions/{session_id}/topic-selection.json`

**Reference:** See `Docs/drill-down-prd.md` for complete workflow

---

### Phase 2: Automated Research Pipeline (Agents 1-4)

1. **User runs product research:**
   ```bash
   /research-products "Walking Meditation for Anxiety Relief"
   ```

2. **Agents 1-4 run sequentially** with checkpoints:

   **Agent 1: Product Researcher**
   - Finds 5-10 comparable products via:
     - **Web scraping** (Amazon, Goodreads) - NO API quota
     - **Reddit** (10-20 API calls) - ~0.5% hourly quota
     - **YouTube** (100-200 units) - ~2% daily quota
   - Discovers hidden segments via subreddit overlap
   - **Checkpoint 1:** User approves comparables
   - **Quota Impact:** LOW (can research 50+ products/day)

   **Agent 2: Demographics Analyst**
   - Extracts demographics from reviews/comments via **Task tool**
   - Uses **local processing** (sentence-transformers) for clustering
   - Calculates confidence via triangulation (3+ sources)
   - **Checkpoint 2:** User approves demographics (must be ≥80% confidence)
   - **Quota Impact:** ZERO (Task tool unlimited, reuses Agent 1 data)

   **Agent 3: Persona Generator**
   - Generates 400 synthetic personas via **Task tool**
   - Uses **local libraries** (faker, numpy, scipy) for attributes
   - Saves to reusable inventory: `personas-inventory/anxiety-meditation.json`
   - **Checkpoint 3:** User reviews persona distribution
   - **Quota Impact:** ZERO (Task tool unlimited, local processing)
   - **Reusability:** Use same personas to test 100+ product variants

   **Agent 4: ParaThinker Intent Simulator**
   - Simulates 400 personas × 8 reasoning paths = 3,200 perspectives via **Task tool**
   - Uses **local processing** (sentence-transformers, numpy) for SSR analysis
   - Outputs purchase intent distribution + recommendations
   - **Checkpoint 4:** User reviews final report
   - **Quota Impact:** ZERO (Task tool unlimited, local processing)

**Deliverable:** `reports/{session_id}/intent-prediction-report.html`

**Total Quota Cost for Full Pipeline:**
- Agent 0 validation: 1,000 YouTube units + 1 Trends call
- Agent 1 research: 100-200 YouTube units + 10-20 Reddit calls
- Agents 2-4: **ZERO** (Task tool + local processing)

**Daily Capacity:** 3 complete pipelines = 3,600 YouTube units (36% quota)

---

## Technical Architecture

### API Quota Strategy

**Design Principle:** Use unlimited sources for exploration, quota-limited sources for final validation.

**Quota Budgets (Updated 2025-10-31):**

| API | Daily Limit | Hourly Limit | Agents Using It | Bottleneck? | Notes |
|-----|-------------|--------------|-----------------|-------------|-------|
| **Reddit** | Unlimited | 3,600 calls | Agent 0, Agent 1 | ❌ No | PRAW API, free tier |
| **Google Trends** | ~360 calls | ~15 calls (safe) | Agent 0 only | ❌ No | With 24hr caching |
| **YouTube** | 10,000 units | N/A | Agent 0, Agent 1 | ✅ Yes | Primary bottleneck |
| **Task Tool** | Unlimited | Unlimited | Agents 0, 2, 3, 4 | ❌ No | Claude Pro subscription |
| **Web Scraping** | Unlimited | N/A | Agent 1 (Playwright) | ❌ No | Amazon, Goodreads |

**System Capacity (Current Quotas):**
- **Exploration:** Unlimited topics (Agent 0 drill-down mode)
- **Validation:** 10-20 topics/day (Agent 0 with YouTube)
- **Product Research:** 50+ products/day (Agent 1 minimal YouTube)
- **Demographics/Personas/Intent:** Unlimited (Agents 2-4 use Task tool)

**If YouTube Quota Increases to 100K:**
- Validation capacity: 100-200 topics/day
- Product research: 500+ products/day
- Bottleneck shifts from quota → processing time

**Reference:** See `Docs/rate-limit-analysis.md` for detailed analysis

---

### 5 Agents Overview

**Agent 0: Topic Research (LED 500-599)** - ✅ COMPLETE
- Discovers high-demand ebook topics using Brian Moran's "Rule of One" strategy
- Three modes: drill-down (unlimited), regular (low quota), validation (YouTube)
- Outputs scored topics with tree navigation for drill-down workflow
- **Status:** Fully implemented with quota visualization

**Agent 1: Product Research (LED 1500-1599)** - ⏳ NOT STARTED
- Finds 5-10 comparable products via web scraping + minimal API calls
- Discovers hidden audience segments via Reddit subreddit overlap
- **Quota Impact:** LOW (web scraping primary, 100-200 YouTube units per product)
- **Reference:** `Docs/5-agents-design.md` Section 3

**Agent 2: Demographics Analyst (LED 2500-2599)** - ⏳ NOT STARTED
- Extracts demographics from reviews/comments using **Task tool** (not paid API)
- Triangulates across 3+ sources, calculates confidence scores
- Checkpoint gate: <80% confidence = must user-approve to continue
- **Quota Impact:** ZERO (Task tool unlimited, reuses Agent 1 scraped data)
- **Reference:** `Docs/5-agents-design.md` Section 4

**Agent 3: Persona Generator (LED 3500-3599)** - ⏳ NOT STARTED
- Generates 400 synthetic personas via **Task tool** (not paid API)
- Saves to reusable inventory, can test unlimited products per category
- **Quota Impact:** ZERO (Task tool unlimited, local libraries for attributes)
- **Reference:** `Docs/5-agents-design.md` Section 5

**Agent 4: ParaThinker Intent Simulator (LED 4500-4599)** - ⏳ NOT STARTED
- Simulates 400 personas × 8 reasoning paths = 3,200 perspectives via **Task tool**
- Uses SSR (Semantic Similarity Rating) for realistic distributions
- **Quota Impact:** ZERO (Task tool unlimited, local processing for analysis)
- **Target Runtime:** 20-25 minutes (accuracy-first approach)
- **Reference:** `Docs/5-agents-design.md` Section 6

---

### Key Technical Decisions

**Decision 1: Task Tool vs Paid Anthropic API**
- **Original Design (v2.0):** Agents 2-4 use paid Anthropic API (~$0.50 per product)
- **Updated Design (v3.0):** Agents 2-4 use **Task tool** (Claude Pro subscription)
- **Impact:** $0 marginal cost per product, unlimited quota
- **Rationale:** CLAUDE.md rule "NO PAID APIs - User has Claude Pro subscription"

**Decision 2: Tiered API Strategy for Agent 0**
- **Problem:** YouTube quota limited (10K/day), Google Trends rate limited
- **Solution:** Three modes (drill-down/regular/validation) balance quota vs confidence
- **Impact:** Unlimited exploration + selective validation
- **Implementation:** Complete as of 2025-10-31

**Decision 3: Web Scraping First for Agent 1**
- **Primary Data:** Playwright scraping (Amazon, Goodreads) - no API limits
- **API Usage:** Only for Reddit discussions + YouTube videos (minimal quota)
- **Impact:** Can research 50+ products/day before hitting YouTube limits
- **Rationale:** Minimize quota consumption, maximize data quality

**Decision 4: LED Breadcrumbs for Autonomous Debugging (500-4599)**
- Console output is machine-readable, enabling Claude to debug autonomously
- Non-overlapping ranges isolate failures to specific agents instantly
- YouTube operations instrumented (530-539) for quota tracking

**Decision 5: ParaThinker 8-Path Architecture**
- Research shows 7-12% accuracy boost vs. sequential reasoning
- Each path independent, parallelizable via Task tool
- Eliminates tunnel vision (70% conformity in human focus groups)

**Decision 6: Agent 2 Confidence Gate (<80% = Checkpoint Failure)**
- Prevents cascade failures (bad demographics → invalid personas → wasted 25+ min)
- User must explicitly approve to continue if confidence <80%
- Early validation minimizes wasted compute, improves final accuracy

**Decision 7: 400 Personas (not 500) for Optimal Balance**
- Diminishing returns analysis: <2% accuracy gain beyond 400 personas
- 40% faster runtime vs 500 personas
- Target: 20-25 minutes while maintaining 85-90% accuracy

---

## Success Metrics

**1. Accuracy:** 85-90% correlation with human survey responses
- Target: Surpass human focus groups' 60-70% accuracy baseline
- Measurement: Compare predictions to PickFu survey results (50 respondents minimum)
- Validation: Semantic similarity between AI predictions and human responses >85%

**2. Speed:** 35-40 minutes end-to-end vs. 2-4 weeks for human focus groups
- Agent 0: <15 minutes (3 modes: drill-down instant, validation ~10 min)
- Agents 1-4 Combined: 20-25 minutes
- Checkpoint Time: <5 minutes per checkpoint (4 checkpoints = 20 min)

**3. Cost:** $0 per test during beta (Claude Pro + free APIs) vs. $5,000-20,000 human focus groups
- **API Costs:** $0 (free tier APIs + Claude Pro Task tool)
  - Agent 0: Free (Reddit, Trends, YouTube within quotas)
  - Agent 1: Free (web scraping + minimal Reddit/YouTube)
  - Agents 2-4: **$0 marginal cost** (Task tool uses Claude Pro, not paid API)
- **Validation Costs:** ~$50 per PickFu survey (for accuracy measurement only)
- **Unlimited testing** with no per-request costs

**4. Quota Efficiency:** Stay under 50% daily YouTube quota for safety margin
- Current usage: 3 topics validated + 3 products researched = 3,600 units (36%)
- Target: Monitor via dashboard quota bars, adjust workflow if approaching limits

**5. Persona Reusability:** Test 100+ product variants with same 400 personas
- First run: 35-40 minutes (full pipeline)
- Subsequent runs: 3-5 minutes (Agent 4 only with cached personas)
- Marginal cost: $0 per variant

**6. Hidden Segments Discovered:** Agent 1 identifies ≥2 underserved audience segments per product
- Via subreddit overlap analysis (e.g., r/productivity → r/ADHD = 8.7× overlap)

**7. Confidence Gate Effectiveness:** <5% false pass rate
- Track: Correlation between Agent 2 confidence scores and final Agent 4 accuracy
- Target: 80%+ confidence demographics → 85%+ final accuracy

---

## Implementation Roadmap

### ✅ Phase 0: Agent 0 Topic Research (COMPLETE)

**Deliverables:**
- [x] Agent 0 with tiered strategy (drill-down/regular/validation modes)
- [x] Dashboard with quota visualization
- [x] Drill-down workflow with tree navigation
- [x] LED breadcrumbs (500-599 including YouTube 530-539)
- [x] None-handling for all edge cases
- [x] Documentation (drill-down-prd.md, rate-limit-analysis.md)

**Files:**
- `agents/agent_0/main.py` (376 lines)
- `agents/agent_0/config.py` (81 lines)
- `agents/agent_0/api_clients.py` (638 lines)
- `agents/agent_0/scoring.py` (502 lines)
- `agents/agent_0/dashboard.py` (1,350 lines)
- `agents/agent_0/drill_down_loader.py` (285 lines)
- `Docs/drill-down-prd.md` (509 lines)
- `Docs/rate-limit-analysis.md` (483 lines)

---

### ⏳ Phase 1: Agents 1-3 (Product → Demographics → Personas)

**Estimated Timeline:** 2-3 weeks

**Agent 1: Product Researcher**
- [ ] Implement web scraping (Playwright for Amazon, Goodreads)
- [ ] Integrate Reddit API (PRAW) for discussions
- [ ] Integrate YouTube API (minimal quota usage)
- [ ] Subreddit overlap analysis for hidden segments
- [ ] LED breadcrumbs (1500-1599)
- [ ] Caching strategy for reusable comparables
- [ ] Checkpoint 1 UI for user approval

**Agent 2: Demographics Analyst**
- [ ] Implement Task tool integration (not paid Anthropic API)
- [ ] Demographic extraction from text (batch processing)
- [ ] Triangulation across 3+ sources
- [ ] Confidence calculation (hybrid model)
- [ ] LED breadcrumbs (2500-2599)
- [ ] Checkpoint 2 UI with confidence gate (<80% = fail)

**Agent 3: Persona Generator**
- [ ] Implement Task tool integration for persona generation
- [ ] Local attribute generation (faker, numpy, scipy)
- [ ] Persona inventory system (reusable categories)
- [ ] LED breadcrumbs (3500-3599)
- [ ] Checkpoint 3 UI for distribution review

**Reference:** `Docs/5-agents-design.md` Sections 3-5

---

### ⏳ Phase 2: Agent 4 (ParaThinker Intent Simulator)

**Estimated Timeline:** 1-2 weeks

**Agent 4: ParaThinker Intent Simulator**
- [ ] Implement 8-path reasoning architecture
- [ ] Task tool integration for 3,200 simulations
- [ ] SSR analysis (sentence-transformers local model)
- [ ] Statistical aggregation (numpy, scipy)
- [ ] LED breadcrumbs (4500-4599)
- [ ] Runtime optimization (target <25 minutes)
- [ ] HTML report generation
- [ ] Checkpoint 4 UI for final review

**Reference:** `Docs/5-agents-design.md` Section 6

---

### ⏳ Phase 3: Integration & Validation

**Estimated Timeline:** 1 week

**Tasks:**
- [ ] End-to-end testing (Agent 0 → Agent 4)
- [ ] Slash command infrastructure (`/discover-topics`, `/research-products`)
- [ ] Data handoff validation (JSON format consistency)
- [ ] Checkpoint flow testing (all 4 gates)
- [ ] PickFu survey validation (50 respondents)
- [ ] Accuracy measurement (target: 85-90%)
- [ ] Performance benchmarking (target: 35-40 min)

---

## Documentation Reference

**For New Claude Chats - Read These First:**

1. **This file** (`PRD-Purchase-Intent-System-v3.md`) - Complete system overview, current status
2. `Docs/drill-down-prd.md` - Agent 0 workflow, tiered strategy (IMPLEMENTED)
3. `Docs/rate-limit-analysis.md` - Quota budgets, capacity planning for Agents 1-4
4. `Docs/5-agents-design.md` - Deep technical specifications for all 5 agents
5. `CLAUDE.md` - Project rules (NO PAID APIs, FAIL LOUDLY, LED ranges, tiered strategy)

**Additional References:**
- `Docs/AI-Agent-Research-Guide.md` - How to research topics using Task tool
- `Docs/Agent-Research-Workflow.md` - Cross-session workflow, caching strategy
- `Docs/Grok-drilldown.md` - Subtopic generation prompt
- `Docs/Topic-Description-Workflow.md` - User-facing workflow
- `Context/[date]/HANDOFF-[date].md` - Session summaries with decisions

**For Troubleshooting:**
- Check LED breadcrumbs in `logs/breadcrumbs.jsonl`
- Agent 0 uses ranges 500-599 (including YouTube 530-539)
- Agents 1-4 use ranges 1500-1599, 2500-2599, 3500-3599, 4500-4599

---

## Next Steps for Development

**Immediate Next Step:** Build Agent 1 (Product Researcher)

**Prerequisites:**
- ✅ Agent 0 complete and working
- ✅ Rate limit analysis complete
- ✅ Quota budgets understood
- ✅ Task tool strategy clarified (not paid API)

**Recommended Approach:**
1. Read `Docs/5-agents-design.md` Section 3 (Agent 1 specification)
2. Read `Docs/rate-limit-analysis.md` Agent 1 section
3. Implement web scraping first (Amazon, Goodreads via Playwright)
4. Add minimal API calls (Reddit, YouTube) with caching
5. Add LED breadcrumbs (1500-1599)
6. Test with Agent 0 output as input
7. Validate quota usage matches predictions (<200 YouTube units)

**Success Criteria:**
- Finds 5-10 comparable products from web scraping
- Uses <20 Reddit API calls per product
- Uses <200 YouTube units per product
- Discovers ≥2 hidden segments via subreddit overlap
- LED breadcrumbs capture all operations
- Checkpoint 1 UI allows user approval/rejection
- Cached comparables reused across similar products (80%+ cache hit rate)

---

**END OF PRD v3.0**

**Status:** Agent 0 complete with tiered strategy and quota visualization. Ready for Agents 1-4 development.

**Last Updated:** 2025-10-31
**Next Review:** After Agent 1 implementation (or if quota limits change)
