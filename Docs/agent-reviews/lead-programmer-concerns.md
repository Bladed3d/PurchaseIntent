# Lead Programmer - PRD v2.0 Review Concerns

**Reviewer:** Lead Programmer Agent
**Date:** 2025-10-23
**PRD Version:** 2.0
**Review Perspective:** Python Implementation Feasibility

---

## CRITICAL CONCERNS (Blocking Implementation)

### 1. Agent 4 Performance Claims Are Mathematically Impossible
**PRD Reference:** Lines 186-192, Lines 26-29

**Problem:**
- PRD claims: "20-25 minutes for 400 personas × 8 reasoning paths = 3,200 perspectives"
- **Reality Check:** Claude API (or any LLM API) has rate limits and latency
  - Anthropic Claude API: ~5-10 seconds per complex reasoning request
  - Even with batching (10 personas per batch), that's 40 batches minimum
  - Optimistic calculation: 40 batches × 5 seconds = 200 seconds (3.3 minutes) - **unrealistic**
  - Realistic calculation with error handling/retries: 40 batches × 15 seconds = 600 seconds (10 minutes) minimum
  - **3,200 individual API calls in 20-25 minutes = 0.4 seconds per call** - impossible

**Impact:** High - This is a core value proposition. If runtime is actually 2-4 hours, MVP fails.

**Questions:**
- Is there a Claude Code-specific batch API that bypasses rate limits?
- Are we using local models (Ollama, etc.) instead of API calls?
- Is "perspective" different from "API call"? (e.g., do 8 paths share one API call?)

**Recommendation:**
- Conduct actual benchmark with 10 personas × 8 paths and measure real-world runtime
- If using Claude API, revise target to 2-4 hours or reduce persona count to 50-100
- Specify exact API being used (Claude, GPT-4, local model, etc.)

---

### 2. Missing API Credentials and Setup Documentation
**PRD Reference:** Lines 115-120, Lines 250-254

**Problem:**
- PRD mentions: "requires Reddit app credentials", "requires Google API key"
- **No specification of:**
  - How to obtain credentials (step-by-step registration process)
  - Where to store credentials (`.env` file format not defined)
  - What happens if user doesn't have credentials (can't run MVP at all)
  - Rate limit quotas for free tier (60 req/min for Reddit, but how many total per day?)

**Impact:** High - Developers cannot implement Agent 0 without this information

**Example Missing Information:**
```python
# What should .env file look like?
REDDIT_CLIENT_ID=?  # Where to get? What format?
REDDIT_CLIENT_SECRET=?  # How to generate?
REDDIT_USER_AGENT=?  # Required by PRAW but not mentioned in PRD
YOUTUBE_API_KEY=?  # Google Cloud Console setup steps?
```

**Recommendation:**
- Add "Prerequisites & Setup" section to PRD with:
  - Step-by-step credential acquisition (links to Reddit/YouTube developer portals)
  - `.env` file template with all required variables
  - Fallback behavior if credentials are missing (skip that data source?)

---

### 3. Agent 2 Confidence Calculation Has Undefined Edge Cases
**PRD Reference:** Lines 132-174

**Problem:**
The confidence calculation methodology is well-defined for the happy path, but fails for common edge cases:

**Edge Case 1: Single Source Available**
- What if Reddit returns data but YouTube API quota is exceeded?
- Formula: `Agreement Score × Avg Quality Weight` - but agreement requires 2+ sources
- **No specification for single-source confidence calculation**

**Edge Case 2: Contradictory Data**
- Example: Reddit says "Age 18-24", YouTube says "Age 45-54" (0% overlap)
- Agreement Score = 0% → Confidence = 0% (automatic checkpoint failure)
- But what if both sources have high sample sizes (>500 each)? Is the data truly unreliable, or are there two distinct audience segments?

**Edge Case 3: Partial Attribute Agreement**
- Reddit: "Age 25-34, Male, Tech Industry"
- YouTube: "Age 25-44, Female, Marketing Industry"
- **How to calculate agreement?** (1 out of 3 attributes = 33%? Weighted by importance?)

**Impact:** Medium-High - Agent 2 will crash or produce nonsensical confidence scores without edge case handling

**Recommendation:**
- Define single-source confidence calculation (e.g., Quality Weight × 0.5 as penalty)
- Specify behavior for contradictory data (flag as "multi-segment audience" vs. "unreliable data")
- Document attribute weighting (age > gender > occupation?)

---

### 4. No Specification of Data Schema Between Agents
**PRD Reference:** Line 214 mentions "Data handoff via JSON" but provides no schemas

**Problem:**
- Agent 0 outputs "topic-selection.json" - what's inside?
- Agent 1 outputs "agent1-output.json" - what fields?
- Agent 2 needs to parse Agent 1's output - what structure?

**Example Missing Schema:**
```json
// What does topic-selection.json look like?
{
  "selected_topic": "Overcoming Procrastination for ADHD Remote Workers",
  "demand_score": 87.5,
  "sources": {
    "google_trends": { "search_volume": 12500, "trend": "rising" },
    "reddit": { "subscribers": 45000, "posts_per_day": 150 },
    "youtube": { "views": 2500000, "videos": 320 }
  }
}
// OR completely different structure?
```

**Impact:** High - Agents cannot communicate without defined schemas

**Recommendation:**
- Add "Data Schemas" appendix to PRD with JSON examples for each handoff:
  - `topic-selection.json` (Agent 0 → Agent 1)
  - `agent1-output.json` (Agent 1 → Agent 2)
  - `agent2-output.json` (Agent 2 → Agent 3)
  - `reusable-400.json` (Agent 3 → Agent 4)
  - `intent-prediction-report.html` (Agent 4 → User)

---

### 5. Python Module Structure Violates <300 Line Constraint
**PRD Reference:** Line 213 states "Each agent: `agents/agent_{N}.py` < 300 lines"

**Problem:**
Agent 0 alone requires:
- Google Trends API integration (~50 lines)
- Reddit PRAW API integration (~80 lines)
- YouTube Data API v3 integration (~80 lines)
- Demand score calculation algorithm (~60 lines)
- HTML dashboard generation with Jinja2 (~100 lines)
- LED breadcrumb instrumentation (~30 lines)
- Error handling and retry logic (~50 lines)
- **Total: ~450 lines minimum**

**Impact:** Medium - Either violate architectural constraint or split into sub-modules

**Possible Solutions:**
1. Split into `agents/agent_0/main.py`, `agents/agent_0/apis.py`, `agents/agent_0/scoring.py`
2. Extract common utilities to `lib/api_clients.py`, `lib/html_generator.py`
3. Revise constraint to <500 lines for main agents, <300 for utilities

**Recommendation:**
- PRD should specify if sub-modules are allowed (my preference: yes, with clear directory structure)
- Or revise line count constraint to realistic levels based on actual implementation needs

---

## MODERATE CONCERNS (Should Address Before Implementation)

### 6. LED Breadcrumb Ranges Have Gaps
**PRD Reference:** Lines 36-39, Lines 210-211

**Problem:**
- PRD allocates: 500-599 (Agent 0), 1500-1599 (Agent 1), 2500-2599 (Agent 2), etc.
- **Gap ranges 600-1499, 1600-2499, etc. are unallocated**
- CLAUDE.md specifies ranges 1000-9099 for entire Purchase-Intent system
- **Inconsistency:** PRD says "500-4599", CLAUDE.md says "1000-9099"

**Impact:** Low-Medium - Won't break functionality but creates confusion during debugging

**Recommendation:**
- Use contiguous ranges: 1000-1099 (Agent 0), 1100-1199 (Agent 1), etc.
- Reserve 5000-9099 for future expansion or shared utilities
- Update CLAUDE.md to match PRD's final allocation

---

### 7. No Specification for Checkpoint UI/UX
**PRD Reference:** Lines 96-102 mention "checkpoints" but no implementation details

**Problem:**
- How does user approve checkpoints? (CLI prompt? Web dashboard? Email notification?)
- What data is shown during checkpoint? (Raw JSON? Pretty-printed table? Charts?)
- Can user edit data at checkpoint? (e.g., manually adjust demographics if confidence is 79%)

**Example Ambiguity:**
```
Checkpoint 2: User approves demographics (confidence target: 80%+)
- Does user see: Terminal output? HTML dashboard? JSON file to review?
- How to approve: Type "yes"? Click button? Edit and save?
- What if user rejects: Return to Agent 1? Abort? Manual override?
```

**Impact:** Medium - Affects development timeline (CLI is fast, web UI is slow)

**Recommendation:**
- Specify checkpoint interface in PRD (suggest: CLI with pretty-printed tables for MVP)
- Defer HTML checkpoint dashboards to post-MVP

---

### 8. Persona Reusability Assumption May Be Flawed
**PRD Reference:** Lines 382-384 claim "marginal cost = $0" for subsequent product tests

**Problem:**
- Assumes 400 personas generated for "Overcoming Procrastination for ADHD Remote Workers" are valid for testing "Time Management for Busy Parents"
- **These are different demographics:**
  - ADHD Remote Workers: Age 25-40, tech industry, neurodivergent
  - Busy Parents: Age 30-50, diverse industries, parents of young children
- Reusing personas = wrong audience = invalid predictions

**Impact:** Medium - Undermines value proposition of persona reusability

**Possible Solutions:**
1. Generate "universal reader personas" (broad demographics) instead of topic-specific
2. Allow partial persona reuse (filter 400 personas to 200 relevant ones)
3. Accept that personas are topic-specific (reusability is for testing variants of SAME product)

**Recommendation:**
- Clarify in PRD: Persona reusability is for product *variants* (e.g., "ADHD Procrastination Ebook v1" vs. "v2 with different positioning")
- Not for testing completely different products with different demographics

---

### 9. No Error Recovery Strategy for Partial API Failures
**PRD Reference:** Lines 446-450 mention "graceful degradation" but no specifics

**Problem:**
- What if Google Trends works but Reddit API returns 429 (rate limit exceeded)?
- Does Agent 0 continue with 2 out of 3 sources? Show warning? Abort?
- **No specification for minimum viable data:**
  - Can Agent 0 complete with only 1 source?
  - Can Agent 1 work with only Reddit (no YouTube)?
  - Can Agent 2 calculate confidence with only 1 source? (see Concern #3)

**Impact:** Medium - Agents will be fragile in production without clear failure modes

**Recommendation:**
- Define "minimum viable data" per agent (e.g., Agent 0 requires at least 2 out of 3 sources)
- Specify retry logic (3x with exponential backoff is mentioned, but what's the backoff schedule?)

---

### 10. HTML Dashboard Dependencies Not Specified
**PRD Reference:** Lines 79-81, Lines 201-204 mention Chart.js but no version or CDN

**Problem:**
- Chart.js version? (v3.x has breaking changes from v2.x)
- Load from CDN or bundle locally? (CDN = internet required, bundle = larger repo)
- Jinja2 template engine mentioned but no version (Jinja2 vs. Jinja3?)
- Browser compatibility: "Chrome/Edge (primary)" - does this mean no testing on Firefox/Safari?

**Impact:** Low-Medium - Can be resolved during implementation but adds uncertainty

**Recommendation:**
- Add "Frontend Dependencies" section:
  - Chart.js v4.4.0 (CDN: https://cdn.jsdelivr.net/npm/chart.js)
  - Jinja2 v3.1.2 (pip install)
  - Browser support matrix (Chrome/Edge/Firefox latest versions)

---

## QUESTIONS NEEDING CLARIFICATION

### 11. What is the Claude Code "Subscription" Model?
**PRD Reference:** Lines 402-403, Lines 378-380

**Question:**
- PRD claims "$0 per test during beta (Claude Code subscription)"
- **Is Claude Code a paid service with unlimited API calls?**
- Or does it use the Claude API with per-token pricing?
- If paid subscription, what's the monthly cost? (affects "$0 marginal cost" claim)

**Why This Matters:**
- If Claude API is used, 3,200 API calls per test = substantial cost
- If Claude Code provides unlimited usage, this is a huge advantage (should be emphasized)

---

### 12. Is "ParaThinker" a Custom Implementation or Existing Library?
**PRD Reference:** Lines 181-192, Line 408

**Question:**
- Is ParaThinker an existing Python library/framework?
- Or is this a custom architecture we're building from scratch?
- If custom: Where is the specification for the 8 reasoning paths? (VALUE, FEATURES, EMOTIONS, etc.)

**Why This Matters:**
- If existing library: Need installation instructions and documentation links
- If custom: Need detailed prompt engineering specs for each of the 8 paths (could be 100+ lines of prompts)

---

### 13. How Are "Checkpoints" Implemented in Slash Commands?
**PRD Reference:** Lines 194-202, Lines 228-260

**Question:**
- Slash command `/research-products` triggers Agents 1-4 sequentially
- But checkpoints require user interaction between agents
- **How does this work?**
  - Does command pause and wait for user input?
  - Does each agent run separately (user must manually trigger next agent)?
  - Is there a "checkpoint daemon" that prompts user?

**Why This Matters:**
- Affects slash command implementation complexity
- May require stateful session management (not mentioned in PRD)

---

### 14. What Format Should LED Breadcrumb Logs Use?
**PRD Reference:** Line 209 mentions "logs/agent-{N}-breadcrumbs.log"

**Question:**
- Log format? (JSON? Plain text? CSV?)
- Example log entry structure?
  ```
  [2025-10-23 14:32:15] LED-500 | Agent 0 | Startup | Initializing API clients
  OR
  {"timestamp": "2025-10-23T14:32:15Z", "led": 500, "agent": 0, "message": "Initializing API clients"}
  ```

**Why This Matters:**
- Claude needs to grep these logs for autonomous debugging
- Structured format (JSON) is easier to parse than free-form text

**Recommendation:**
- Define log format in PRD (suggest JSON Lines for grep-friendly structured logs)

---

### 15. Are Git Worktrees Required or Optional?
**PRD Reference:** Lines 265-322 describe extensive git worktree workflow

**Question:**
- Is this workflow **required** for MVP?
- Or is it an optimization for parallel development?
- Can single developer work in main repository without worktrees?

**Why This Matters:**
- Git worktrees add complexity (5 separate directories to manage)
- If optional, should be clearly marked as "Advanced: Parallel Development Pattern"
- If required, needs more detailed setup instructions (worktree sync issues, merge conflicts, etc.)

---

## POSITIVE OBSERVATIONS

### What's Well-Specified:

1. **Clear Agent Separation** - 5 distinct agents with defined responsibilities (Lines 112-192)
2. **Confidence Calculation Methodology** - Agent 2's hybrid model is well-documented with example (Lines 132-174)
3. **API Selection Rationale** - Free tier APIs with low legal risk is smart for MVP (Lines 14-18)
4. **Success Metrics Are Measurable** - 85-90% accuracy vs. human baseline, with validation method specified (Lines 368-391)
5. **Rate Limiting Strategy** - Sequential queries with 2-3 second delays prevents API bans (Line 119)
6. **LED Breadcrumb Philosophy** - Non-overlapping ranges for autonomous debugging is excellent (Lines 405-406)
7. **Persona Reusability** - Even if limited to product variants, this is a strong differentiator (Lines 382-384)
8. **Checkpoint Failure Gates** - Agent 2's <80% confidence checkpoint prevents cascade failures (Lines 160-174)

---

## RISK ASSESSMENT SUMMARY

### High Risk (Require Resolution Before Implementation):
1. Agent 4 performance claims (Concern #1) - **Mathematical impossibility**
2. Missing API credentials documentation (Concern #2) - **Cannot implement without**
3. Missing data schemas (Concern #4) - **Agents cannot communicate**
4. Module size constraint violations (Concern #5) - **Architectural conflict**

### Medium Risk (Should Address During Implementation):
1. Agent 2 confidence edge cases (Concern #3)
2. Checkpoint UI/UX unspecified (Concern #7)
3. Persona reusability assumptions (Concern #8)
4. Partial API failure handling (Concern #9)

### Low Risk (Can Resolve During Development):
1. LED breadcrumb range gaps (Concern #6)
2. HTML dashboard dependency versions (Concern #10)

---

## RECOMMENDATIONS FOR PRD v2.1

### Must-Have Additions:
1. **Append "Agent 4 Performance Benchmark"** - Conduct 10-persona test, measure actual runtime, revise targets
2. **Add "Prerequisites & Setup" section** - Step-by-step API credential acquisition
3. **Add "Data Schemas Appendix"** - JSON examples for all agent handoffs
4. **Revise "Module Architecture"** - Allow sub-modules or adjust line count constraints

### Should-Have Additions:
1. **Define checkpoint interface** - CLI prompts with pretty-printed tables (defer web UI to post-MVP)
2. **Specify minimum viable data** - Agent can continue with N out of M data sources
3. **Add "Frontend Dependencies"** - Chart.js version, Jinja2 version, CDN vs. local

### Nice-to-Have Additions:
1. **LED breadcrumb log format specification** - JSON Lines example
2. **Clarify git worktree workflow as optional** - Mark as "Advanced Pattern" not requirement

---

## IMPLEMENTATION READINESS: 60%

**Blockers Remaining:** 4 critical concerns (Agent 4 performance, API setup, data schemas, module structure)

**Estimated Gap Closure Time:** 4-6 hours of PRD refinement

**Next Steps:**
1. Conduct Agent 4 performance benchmark with real API
2. Document API credential setup process
3. Define JSON schemas for all agent handoffs
4. Clarify module architecture constraints

**Once Resolved:** PRD will be implementation-ready with <10% ambiguity

---

**Lead Programmer Agent**
**Date:** 2025-10-23
**Review Status:** Critical concerns identified - recommend PRD v2.1 revision before implementation
