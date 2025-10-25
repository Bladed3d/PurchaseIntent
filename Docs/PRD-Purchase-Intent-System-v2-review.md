# Critical Review: PRD Purchase Intent System v2.0

**Reviewer:** prd-critical-reviewer agent
**Review Date:** 2025-10-23
**Document Reviewed:** PRD-Purchase-Intent-System-v2.md
**Review Type:** Pre-Implementation Technical Audit

---

## Executive Summary

**OVERALL VERDICT: NOT READY FOR IMPLEMENTATION - Major gaps and unsubstantiated claims require resolution**

This PRD demonstrates significant improvement over v1.0 and shows thoughtful collaborative refinement. However, it suffers from three critical flaws:

1. **Unvalidated Accuracy Claims**: The core value proposition (85-90% accuracy, 7-12% better than humans) has NO implementation path or validation methodology
2. **Missing Technical Specifications**: API integration details are superficial; actual data schemas, error handling, and edge cases are undefined
3. **Wishful Performance Targets**: Runtime estimates (20-25 min for Agent 4) are stated without benchmarks, prototypes, or evidence

The document conflates "detailed description" with "actionable specification." Before implementation can begin, the team must answer 23 critical questions (detailed below) and build proof-of-concept prototypes for Agents 2 and 4.

**Estimated Risk Level**: HIGH - 60% probability of discovering blocking issues during implementation

---

## SECTION 1: CRITICAL BLOCKING ISSUES

These issues will prevent the system from working as described or will cause major project delays.

### 1.1 The Accuracy Claim Has No Implementation Strategy

**Issue**: The document promises "85-90% accuracy vs. human focus groups' 60-70%" but provides ZERO methodology for achieving or measuring this.

**Evidence of the Problem**:
- Line 368-371: "Accuracy: 85-90% correlation with human survey responses (validate Agent 4 output against PickFu or similar)"
- Line 371: "Measurement: Compare purchase intent predictions to actual PickFu survey results (50 respondents minimum)"
- Line 372: "Validation Method: Semantic similarity between AI predictions and human responses >85%"

**Why This Breaks Everything**:
1. **Semantic Similarity is NOT Accuracy**: Comparing AI text to human text via semantic similarity measures how similarly they're phrased, not whether the predictions are correct. Example:
   - AI: "75% will buy because it solves their time management problem"
   - Human: "Most people want this for scheduling help"
   - Semantic similarity: 85% (seems good!)
   - Actual accuracy: Unknown - did 75% of humans actually say they'd buy? What does "most" mean numerically?

2. **PickFu Comparison is Circular Logic**: PickFu surveys are ALSO predictions (asking "would you buy this?"), not actual purchase data. You're comparing one prediction method to another, not validating against ground truth.

3. **No Ground Truth Defined**: True accuracy requires comparing predictions to ACTUAL PURCHASES. Where's the plan to track:
   - Did the predicted buyers actually buy?
   - Did the predicted non-buyers actually not buy?
   - What's the time window for validation (24 hours? 30 days? 1 year?)

**Critical Questions Requiring Answers**:
1. What is the mathematical definition of "accuracy" in this system? (Precision? Recall? F1 score? Mean Absolute Error on Likert scale?)
2. Where is the ground truth data for validation? (Actual sales data, conversion tracking, longitudinal studies?)
3. How do you validate predictions for products that don't exist yet? (The whole point of the system is to predict BEFORE launching)
4. What baseline are you comparing against? (Where's the evidence that human focus groups only achieve 60-70%? Citation needed.)
5. If you can't get ground truth, what's the proxy metric? (And how do you validate the proxy itself?)

**Required Action Before Implementation**:
- Define a MEASURABLE accuracy metric with mathematical formula
- Identify 3-5 historical ebook launches with known sales data
- Run Agent 4 predictions on those historical cases
- Calculate actual accuracy against real outcomes
- If ground truth unavailable, explicitly acknowledge this is an EXPERIMENT, not a proven 85-90% system

**Impact**: Without this, you're building a system with NO WAY TO KNOW if it works. You'll ship and only discover it's wrong when real products fail.

---

### 1.2 Agent 4 Performance Targets Are Unsubstantiated Guesses

**Issue**: The PRD claims Agent 4 will complete 3,200 perspectives (400 personas × 8 paths) in 20-25 minutes with NO benchmark, prototype, or calculation to support this.

**Evidence of the Problem**:
- Line 186: "Target Runtime: 20-25 minutes (accuracy-first approach)"
- Line 187: "Computation: 400 personas × 8 reasoning paths = 3,200 perspectives"
- Line 188-191: Lists optimization strategies (parallel processing, batch API calls, early stopping) but provides NO EVIDENCE these will achieve the target

**Why This Is Wishful Thinking**:
1. **Missing API Rate Limit Math**: Claude API (Opus) has rate limits. What are they?
   - If limit is 5 requests/minute: 3,200 ÷ 5 = 640 minutes (10.6 HOURS)
   - If limit is 50 requests/minute: 3,200 ÷ 50 = 64 minutes (FAILS target)
   - If batching 10 personas per request: 400 ÷ 10 = 40 requests... at what rate limit?

2. **No Token Budget Calculation**: Each persona evaluation requires:
   - Persona profile (500 tokens input)
   - Product description (300 tokens input)
   - 8 reasoning paths × 200 tokens output each = 1,600 tokens output
   - Total per persona: ~2,400 tokens
   - 400 personas × 2,400 = 960,000 tokens
   - At Claude Opus speed (assumed ~20 tokens/sec): 960,000 ÷ 20 = 48,000 seconds = 800 MINUTES = 13+ HOURS

3. **Parallel Processing Assumption Not Validated**: Line 189 says "8 reasoning paths run concurrently per persona" - but WHO executes this? Claude API doesn't support parallel path execution in a single request. Are you making 8 separate API calls per persona? (3,200 total calls, even worse for rate limits)

4. **Batch API Calls Don't Work This Way**: Line 189 says "Batch API calls (10 personas per batch to respect rate limits)" - but batch API pricing is for ASYNCHRONOUS jobs with 24-hour turnaround, not real-time responses.

**Critical Questions Requiring Answers**:
1. What are the actual Claude API rate limits for the subscription tier you're using?
2. What is the actual token throughput speed? (Measured, not assumed)
3. How are you implementing "parallel processing" of 8 reasoning paths? (Separate API calls? Single prompt with structured output? Multi-agent system?)
4. Have you built a prototype that processes even 10 personas? What was the actual time?
5. What's the fallback if runtime is 2+ hours instead of 25 minutes?

**Required Action Before Implementation**:
- Build a minimal prototype: Process 10 personas through Agent 4
- Measure actual time per persona (including API latency)
- Extrapolate: 400 personas = 10 personas × 40, calculate real estimated time
- If time exceeds 25 minutes, revise target OR reduce persona count OR change architecture
- Document MEASURED performance, not aspirational targets

**Impact**: If actual runtime is 2-4 hours instead of 25 minutes, the entire value proposition ("35-40 minutes end-to-end") collapses. Users will abandon the tool.

---

### 1.3 Agent 2 Confidence Calculation is Fatally Flawed

**Issue**: The confidence methodology (lines 133-174) looks sophisticated but has mathematical errors and will produce meaningless scores.

**Evidence of the Problem**:
```python
# From lines 148-158 (example calculation)
Confidence = (Agreement Score) × (Avg Quality Weight)

Example:
- Agreement: 60% (partial overlap on age range)
- Quality Weights: Reddit 1.2×, YouTube 1.0×
- Avg Quality: (1.2 + 1.0) / 2 = 1.1
- Confidence = 60% × 1.1 = 66% (FAILS checkpoint)
```

**Why This Is Wrong**:

**Flaw 1: Multiplication Inflates False Precision**
- If Reddit data is low quality (0.7× weight) and YouTube is low quality (0.7× weight)
- But they AGREE 100% (both say "age 25-34")
- Formula: 100% × 0.7 = 70% confidence
- **Reality**: Two garbage sources agreeing doesn't make them reliable. This should be LOWER confidence, not 70%.

**Flaw 2: Quality Weights Are Arbitrary**
- Line 144: "Reddit (1.0×), YouTube comments (0.9×), trends data (0.8×)"
- WHERE did these numbers come from? Why is Reddit 1.0 and not 0.95 or 1.1?
- This is cargo cult precision - inventing numbers to look scientific

**Flaw 3: Sample Size Weighting is Backwards**
- Line 143: "<100 comments = 0.7×, 100-500 = 1.0×, >500 = 1.2×"
- Sample size is NOT a multiplier on confidence. It affects the VARIANCE of estimates.
- Statistical formula: Confidence Interval = Mean ± (Z × σ/√n)
- You need margin of error calculations, not arbitrary multipliers

**Flaw 4: Recency Weighting Lacks Context**
- Line 143: "<3 months = 1.0×, 3-12 months = 0.9×, >12 months = 0.7×"
- For EVERGREEN topics (e.g., "productivity for entrepreneurs"), 12-month-old data is still valid
- For TRENDING topics (e.g., "ChatGPT productivity hacks"), 3-month-old data is ancient
- This needs topic-specific recency modeling, not blanket penalties

**Flaw 5: Agreement Score Methodology is Undefined**
- Line 138-140: "Calculate overlap: (Agreed Attributes / Total Attributes) × 100"
- WHICH attributes? How do you count them?
- Example: Reddit says "age 25-34", YouTube says "age 25-44"
  - Is this 0% agreement (different ranges)?
  - 60% agreement (overlap on 25-34)?
  - 50% agreement (one's a subset of the other)?
- No specification for HOW to calculate agreement on numerical ranges, categorical data, or free text

**What SHOULD Be Done Instead**:
Use Bayesian confidence scoring:
```python
# Proper confidence calculation
confidence = f(source_credibility, sample_size, cross_source_agreement, data_recency)

# Where:
# - source_credibility = historical accuracy of source (requires validation data)
# - sample_size = statistical significance (use actual confidence intervals)
# - cross_source_agreement = Cohen's Kappa or similar inter-rater reliability
# - data_recency = time-decay function based on topic volatility
```

**Critical Questions Requiring Answers**:
1. What published research supports these specific quality weights? (Or are they invented?)
2. How do you calculate agreement when data types differ? (numerical ranges, categories, free text)
3. Have you tested this formula on historical demographic data with known ground truth?
4. What happens when only 2 sources are available instead of 3? (Formula breaks)
5. Why use multiplication instead of weighted averaging or Bayesian updating?

**Required Action Before Implementation**:
- Revise formula using established statistical methods (confidence intervals, Bayesian inference)
- Test on 10 historical product datasets with known demographics
- Measure: How often does >80% confidence actually correlate with accurate demographics?
- If correlation is weak, the checkpoint gate is useless (false positives/negatives)

**Impact**: A broken confidence calculation means the checkpoint gate (which is supposed to prevent cascade failures) will either:
1. Block valid data (false negatives), wasting user time
2. Approve garbage data (false positives), producing wrong personas and wasting 25+ minutes on Agent 4

---

### 1.4 API Integration Strategy Lacks Failure Mode Planning

**Issue**: The PRD lists APIs (Reddit PRAW, YouTube Data API, pytrends) but doesn't specify what happens when they fail, change, or hit limits.

**Evidence of the Problem**:
- Line 119: "Rate Limiting Strategy: Sequential queries with 2-3 second delays between sources"
- Line 120: "Error Handling: Graceful degradation (continue with partial results if one source fails)"
- Line 447-450: Generic error handling table with "Retry 3× with exponential backoff"

**Missing Specifications**:

**API Failure Scenarios NOT Addressed**:
1. **Reddit API Changes**: PRAW broke in Jan 2025 when Reddit changed authentication. What's the fallback?
2. **YouTube Quota Exhaustion**: 10,000 units/day runs out after 100 video searches (100 units each). Then what? Wait 24 hours? Use cached data? Abort?
3. **Google Trends Blocking**: pytrends is unofficial and gets blocked unpredictably. What's the fallback source?
4. **Simultaneous Multi-Source Failure**: If Reddit AND YouTube both fail, does Agent 0 abort? Continue with only Trends data? How low can data quality go before results are unusable?

**Rate Limiting is Underspecified**:
- Line 119: "2-3 second delays" - Why not 1 second? Why not 5 seconds? Based on what measurement?
- Reddit PRAW: 60 requests/minute = 1 request per second. If you delay 3 seconds, you're wasting 2 seconds per request.
- YouTube API: No rate limit on requests, only on quota units. "Delays" don't help here.

**Graceful Degradation is Undefined**:
- Line 120: "continue with partial results" - WHAT is the minimum acceptable data?
- Example: Agent 0 queries 3 sources. If only Google Trends works, is that enough? (It only gives search volume, no demographics)
- What's the user notification? "Warning: Reddit failed, results may be incomplete"? Or silent degradation?

**Critical Questions Requiring Answers**:
1. What percentage of data sources must succeed for each agent to continue? (All? 2/3? 1/3?)
2. What's the retry strategy for transient failures vs. permanent failures? (API key expired vs. network timeout)
3. How do you handle API deprecation? (YouTube API v3 -> v4 migration plan?)
4. What's the user experience when APIs fail? (Error messages? Automatic retries? Manual intervention?)
5. Have you tested with API mocking to simulate failures? (Network timeout, 429 rate limit, 403 auth failure, 503 service down)

**Required Action Before Implementation**:
- Document EVERY API endpoint used with exact parameters
- List failure modes for each endpoint (auth failure, rate limit, quota exceeded, network timeout, invalid response)
- Define fallback strategy per failure mode
- Build integration tests that SIMULATE API failures (use mock servers)
- Test "degraded mode" operation with 1 source, 2 sources, 0 sources

**Impact**: Without failure mode planning, the system will crash in production when (not if) APIs fail. You'll discover these issues during user testing, not development, wasting weeks.

---

### 1.5 Data Schema is Completely Missing

**Issue**: The PRD describes data flow between agents (lines 427-435) but provides NO data schemas, field definitions, or validation rules.

**Evidence of the Problem**:
- Line 89: "Deliverable: data/sessions/{session_id}/topic-selection.json"
- Line 104: "Deliverable: reports/{session_id}/intent-prediction-report.html"
- Line 432: "Session directory structure: data/sessions/{session_id}/agent{N}-output.json"

**What's Missing**:
1. **Agent 0 Output Schema**: What fields does topic-selection.json contain?
   - Is it `{"selected_topic": "string"}` or `{"topic_id": 123, "topic_title": "...", "metadata": {...}}`?
   - How does Agent 1 consume this? Does it need the full topic object or just the title?

2. **Agent 1 Output Schema**: What does agent1-output.json look like?
   - List of URLs? Full product objects with metadata?
   - Do you store raw HTML? Parsed structured data? Just links?

3. **Agent 2 Output Schema**: Demographics - what fields?
   - `{"age_range": "25-34", "occupation": ["remote worker", "entrepreneur"]}` ?
   - How do you represent uncertainty? `{"age_range": "25-34", "confidence": 0.85}` ?
   - What if sources disagree? Do you store ALL source data or just the consensus?

4. **Agent 3 Output Schema**: Persona format?
   - Is it compatible with Agent 4's input requirements?
   - How many fields per persona? (Name, age, occupation, goals, pain points, psychographics?)
   - File size estimate: 400 personas × ? KB per persona = ? MB total (will it fit in memory?)

5. **Agent 4 Output Schema**: Intent prediction format?
   - Likert scale (1-5)? Binary (buy/don't buy)? Percentage (0-100%)?
   - Do you store per-persona predictions or just aggregates?
   - How do you represent the 8 reasoning paths? Separate fields or nested objects?

**Critical Questions Requiring Answers**:
1. What are the EXACT JSON schemas for each agent's input and output?
2. What validation rules apply? (Required fields, data types, value ranges)
3. How do you handle schema changes between versions? (Backward compatibility?)
4. What's the error handling when Agent N+1 receives invalid data from Agent N?
5. How do you serialize/deserialize complex types? (Date ranges, probability distributions, nested objects)

**Required Action Before Implementation**:
- Define JSON Schema (or TypeScript interfaces) for ALL inter-agent data
- Example:
```json
// agent0-output.schema.json
{
  "type": "object",
  "required": ["selected_topic", "topic_metadata"],
  "properties": {
    "selected_topic": {
      "type": "string",
      "minLength": 10,
      "maxLength": 200
    },
    "topic_metadata": {
      "type": "object",
      "properties": {
        "demand_score": {"type": "number", "minimum": 0, "maximum": 10},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "evidence": {"type": "object"}
      }
    }
  }
}
```
- Write schema validation tests BEFORE implementing agents
- Document schema evolution policy (how do you change schemas without breaking existing sessions?)

**Impact**: Without data schemas, agents will produce incompatible outputs. You'll spend days debugging "Agent 2 can't parse Agent 1's output" instead of building features.

---

## SECTION 2: MAJOR CONCERNS (High Risk, Not Immediately Blocking)

These issues will cause significant problems or delays if not addressed.

### 2.1 The 400-Persona Optimization Has No Data Behind It

**Concern**: Lines 179 and 191-192 claim "400 personas (reduced from 500) based on diminishing returns analysis" but NO analysis is shown.

**Missing Details**:
- What was the diminishing returns analysis? (Chart of personas vs. accuracy?)
- At 300 personas, what was the accuracy? 350? 450? 500?
- What's the confidence interval on "400 is optimal"? (Maybe 380 is better? Or 420?)
- Was this tested empirically or just estimated?

**Questions Requiring Answers**:
1. Where is the data showing 400 is the optimal number?
2. What accuracy drop occurs at 300 personas? (Is it actually 2% or 5% or 10%?)
3. What happens if you use 200 personas? (Faster, but how much less accurate?)
4. Is "optimal" the same for all product categories? (Maybe books need 400, but courses need 600)

**Recommendation**:
- Run a simulation with 100, 200, 300, 400, 500 personas
- Plot accuracy vs. count to identify the elbow point
- If no simulation data exists, admit this is an ASSUMPTION and plan to validate post-MVP

---

### 2.2 Slash Command Implementation Pattern is Underspecified

**Concern**: Lines 222-262 show an example slash command file, but critical integration details are missing.

**What's Unclear**:
1. **How does the command trigger Python execution?**
   - The .md file expands to a prompt... then what?
   - Does Claude Code automatically detect "Execute Agent 0" and run `python agents/agent_0.py`?
   - Or does the user have to manually run Python after reading the prompt?

2. **How are variables passed?**
   - Line 240: `{{niche}}` placeholder - how does this get substituted?
   - Is it string replacement before prompt expansion?
   - Where do the API credentials from .env get loaded? (Python script? Claude prompt?)

3. **How does Claude report progress?**
   - If Agent 0 takes 15 minutes, does Claude stream updates?
   - Or does the user stare at a blank screen waiting?
   - Where do LED breadcrumbs appear? (Console? Log file? Claude monitors it?)

4. **Error handling in slash commands?**
   - If Python script crashes, does the slash command fail?
   - How does Claude detect the crash vs. waiting for output?

**Questions Requiring Answers**:
1. What is the EXACT execution flow from `/discover-topics` to Python script completion?
2. How does Claude Code's slash command system work? (Is there documentation?)
3. Have you tested a prototype slash command that calls Python?
4. What's the user experience during long-running agents? (Loading indicator? Progress bar? Nothing?)

**Recommendation**:
- Build a minimal slash command prototype that calls a Python "hello world" script
- Document the execution flow with a sequence diagram
- Test error scenarios (script not found, Python crash, API failure)
- Clarify whether this is a Claude Code feature or custom implementation

---

### 2.3 LED Breadcrumb Ranges Don't Match CLAUDE.md

**Concern**: PRD says "ranges 500-4599" but CLAUDE.md says "ranges 1000-9099".

**Evidence**:
- PRD Line 55: "LED breadcrumb instrumentation (ranges 500-4599)"
- CLAUDE.md Line 165-174: "1000-1099: Application startup... 2000-2099: Intent detection... 9000-9099: Testing"

**Conflict**:
- CLAUDE.md reserves 1000-9099 for general application use
- PRD assigns 500-4599 to agents (which overlaps with nothing in CLAUDE.md)
- Is 500-4599 a NEW reservation? Or a mistake?

**Questions Requiring Answers**:
1. Are 500-4599 reserved for this specific project?
2. Does this need to be documented in CLAUDE.md (per PRD line 38)?
3. What happens if future projects also use 500-4599?
4. Why not use the existing 2000-2099 range (intent detection) instead of inventing new ranges?

**Recommendation**:
- Clarify the breadcrumb range allocation strategy
- Update CLAUDE.md to document 500-4599 as "Purchase Intent System agents" if confirmed
- Or revise PRD to use existing CLAUDE.md ranges (2000-2099 for intent, 4000-4099 for ML inference)

---

### 2.4 Git Worktree Strategy is Complex for Unclear Benefit

**Concern**: Lines 265-363 describe parallel development with git worktrees, but the complexity may outweigh benefits for a 5-agent system.

**Complexity Introduced**:
- 5 separate worktree directories (`../pi-agent-0` through `../pi-agent-4`)
- Parallel development across worktrees (Pattern A, B, C on lines 295-321)
- Sequential merge strategy (lines 358-363)
- Risk of merge conflicts if agents share common code (LED utilities, data schemas)

**Simpler Alternative**:
- Develop agents sequentially on feature branches (`feature/agent-0`, `feature/agent-1`, etc.)
- Merge each agent after VALIDATED status
- No worktree management overhead
- Easier for single developer or small team

**Questions Requiring Answers**:
1. How many developers are working on this? (If 1-2, worktrees are overkill)
2. What's the actual parallelism benefit? (Are you developing 5 agents simultaneously, or sequentially with parallel instrumentation/testing?)
3. Have you used git worktrees successfully before? (Non-trivial to manage)
4. What's the plan for shared code? (LED utilities, common dependencies) - developed in main repo or duplicated across worktrees?

**Recommendation**:
- Start with simple feature branches for MVP
- Only use worktrees if you have 3+ developers working in parallel
- Document worktree setup/teardown commands (easy to mess up)
- Clarify whether this is required or optional

---

### 2.5 ParaThinker Integration is Described But Not Designed

**Concern**: The PRD references "ParaThinker 8-Path Architecture" (line 408-409) but doesn't specify HOW it's implemented.

**What's Missing**:
1. **Is ParaThinker a separate library?** (Do you import it? Build it from scratch?)
2. **How are the 8 paths executed?** (Parallel API calls? Single prompt with structured output?)
3. **How do you aggregate 8 paths into a final decision?** (Averaging? Voting? Weighted combination?)
4. **What if paths disagree?** (Path 1 says "buy", Path 5 says "don't buy" - how do you resolve?)

**Reference to Research**:
- Line 409: "Research shows 7-12% accuracy boost vs. sequential reasoning"
- WHERE is this research? (Internal study? Published paper? Citation missing)
- Was this tested on purchase intent specifically, or general reasoning tasks?

**Questions Requiring Answers**:
1. Where is the ParaThinker implementation specification?
2. Is there a proof-of-concept showing it works for purchase intent?
3. What are the 8 paths specifically? (PRD lists them in 5-agents-design.md lines 137-148, but how do they map to API prompts?)
4. How do you validate that 8 paths are actually better than 1 path? (A/B test needed)

**Recommendation**:
- Build a minimal ParaThinker prototype with 2-3 paths (not 8) for MVP
- Compare 1-path vs. multi-path predictions on 10 sample personas
- Measure: Is multi-path actually more accurate, or just more expensive?
- Document the aggregation algorithm with pseudocode

---

### 2.6 Cost Model is Incomplete

**Concern**: Lines 379-381 claim "$0 per test during beta (Claude Code subscription)" but ignore hidden costs.

**Missing Costs**:
1. **Developer Time**: How many hours to build Agents 0-4? (100 hours? 200 hours?)
2. **PickFu Validation**: Line 381 says "$50 per PickFu survey" - how many surveys needed to validate accuracy? (10? 50? Cost: $500-2500)
3. **API Rate Limit Costs**: If free tiers are exceeded, what are paid tier costs?
   - YouTube API: $0 for 10k units/day, then what?
   - Reddit API: Free for PRAW, but enterprise API costs $ (future risk)
4. **Opportunity Cost**: If Agent 4 takes 2 hours instead of 25 minutes, what's the user's time worth?

**Questions Requiring Answers**:
1. What's the total development cost (person-hours × hourly rate)?
2. What's the ongoing validation cost (PickFu surveys per month)?
3. What happens if Claude Code subscription ends? (Lock-in risk)
4. What's the cost per test if you scale beyond free API tiers?

**Recommendation**:
- Add a "Total Cost of Ownership" section
- Break down: Development cost (one-time) + Validation cost (per test) + API cost (variable)
- Clarify "zero marginal cost" applies only AFTER initial investment and WITHIN free tier limits

---

## SECTION 3: MODERATE CONCERNS (Should Address, Not Blocking)

### 3.1 Edge Cases Not Considered

**Missing Scenarios**:
1. **Empty Results**: What if Agent 0 finds zero topics? (Niche too obscure)
2. **Disagreeing Sources**: What if Reddit says "age 25-34" but YouTube says "age 45-60"? (No overlap)
3. **Spam/Bot Data**: What if YouTube comments are spam? (How do you filter?)
4. **Outdated Data**: What if all Reddit discussions are from 2020? (Still valid for evergreen topics?)

**Recommendation**: Add an "Edge Cases" section documenting each scenario and its handling.

---

### 3.2 Security and Privacy Not Addressed

**Missing Considerations**:
1. **API Key Storage**: Line 252 says "Use credentials from .env" - is .env gitignored? (Yes, per CLAUDE.md, but PRD doesn't confirm)
2. **Data Privacy**: Are you storing PII from Reddit/YouTube comments? (User names, email addresses in text)
3. **Rate Limiting Abuse**: What if someone runs Agent 0 100 times in a day? (Hits YouTube quota, blocks the whole project)

**Recommendation**: Add a "Security & Privacy" section addressing credentials, PII handling, and rate limit monitoring.

---

### 3.3 Accessibility Requirements are Vague

**Issue**: Line 443-444 mentions "WCAG 2.1 AA compliant" but no implementation details.

**Questions**:
1. How do you make Chart.js charts screen-reader accessible?
2. What keyboard shortcuts are supported?
3. Have you tested with actual screen readers?

**Recommendation**: Either remove accessibility requirement (not critical for MVP) or provide detailed implementation guidance.

---

## SECTION 4: OVER-COMPLICATIONS

### 4.1 HTML Dashboard Might Be Premature

**Issue**: Agent 0 outputs an HTML dashboard (lines 201-204, 399-400) but the PRD also says "CLI only for MVP" (line 60).

**Contradiction**:
- A browser-based dashboard is NOT CLI
- If the goal is simplicity, a terminal table would be simpler

**Simpler Alternative**:
```
Agent 0 Results:
1. [8.7/10] Overcoming Procrastination for ADHD Remote Workers
2. [7.9/10] Time Blocking for Parents Working From Home
3. [7.2/10] Focus Strategies for Remote Developers

Select topic number (1-3):
```

**Questions**:
1. Is the HTML dashboard essential for MVP?
2. Would a terminal UI (rich/blessed library) be simpler?
3. What's the cost of Chart.js integration vs. simple text output?

**Recommendation**: Start with plain text output for MVP, add HTML dashboard in v2 if users request it.

---

### 4.2 Quality Gates Are Overly Rigid

**Issue**: Lines 323-356 define 5 quality gates (IMPLEMENTED → INSTRUMENTED → TESTED → VALIDATED → MERGED) but this may slow down MVP development.

**Simpler Alternative for MVP**:
- WORKING → TESTED → MERGED
- Add LED instrumentation AFTER agent works
- Skip formal "VALIDATED" gate until post-MVP

**Recommendation**: Clarify that quality gates are for production, not MVP. Allow rapid iteration for MVP.

---

## SECTION 5: STRENGTHS (What's Done Well)

To be fair, this PRD has notable strengths:

1. **Checkpoint Strategy is Smart**: Human validation between agents (lines 94-102) prevents garbage-in-garbage-out cascade failures. This is well-designed.

2. **Modular Agent Architecture is Correct**: Separating concerns into 5 agents (vs. 1 monolith) enables independent testing and iteration. Good decision.

3. **Explicit Scope Exclusions**: Lines 59-64 clearly state what's NOT included (web UI, SaaS, CRM integration). Prevents scope creep.

4. **Iterative Refinement is Evident**: The "Changes from v1.0" section (lines 10-40) shows collaborative improvement. This is proper PRD evolution.

5. **LED Breadcrumb Strategy is Solid**: Autonomous debugging via machine-readable breadcrumbs (lines 36-39, 405-406) aligns with CLAUDE.md principles.

6. **Data Source Research is Thorough**: The Grok-Book-data.md research backing Agent 0 source selection (Reddit, YouTube, Google Trends) shows due diligence.

7. **Persona Reusability is Clever**: Lines 57, 382-384 highlight that personas are a one-time cost, reusable for unlimited products. Good ROI thinking.

8. **Anti-Over-Engineering Awareness**: References to CLAUDE.md "start simple" philosophy (line 66-72 context) show cost-consciousness.

---

## SECTION 6: UNSUBSTANTIATED CLAIMS (Evidence Required)

| Claim | Line | Evidence Required | Test Needed |
|-------|------|------------------|-------------|
| "85-90% accuracy" | 368 | Historical validation data | Compare predictions to actual sales for 10 ebooks |
| "7-12% better than human focus groups" | 14, 45 | Benchmark study of human focus groups | Side-by-side test: AI vs. human predictions on same product |
| "60-70% human focus group accuracy" | 369 | Citation to research | Find published studies on focus group accuracy |
| "20-25 minute runtime for Agent 4" | 186 | Prototype benchmark | Build minimal Agent 4, process 10 personas, measure time |
| "400 personas is optimal" | 179, 191 | Diminishing returns analysis | Test 100, 200, 300, 400, 500 personas, plot accuracy vs. count |
| "<2% accuracy gain beyond 400 personas" | 192 | Empirical testing | Measure accuracy at 400 vs. 500 vs. 600 personas |
| "400 personas × 8 paths = 3,200 perspectives" | 187 | Calculation verification | Verify: Is each path independent, or are some combined? |
| "Zero marginal cost" | 379 | Cost model validation | Calculate actual API costs if free tiers exceeded |
| "Diminishing returns beyond 400 personas" | 418 | Analysis report | Show the curve, identify elbow point |
| "Semantic similarity >85%" | 372 | Methodology specification | Define: Which semantic similarity algorithm? (cosine? jaccard?) |

---

## SECTION 7: CRITICAL QUESTIONS REQUIRING ANSWERS BEFORE IMPLEMENTATION

### Accuracy & Validation (Must Answer Before Building Agent 4)
1. What is the mathematical definition of "accuracy" in this system?
2. Where is the ground truth data for validation?
3. How do you validate predictions for products that don't exist yet?
4. Where's the evidence that human focus groups achieve 60-70% accuracy?
5. What's the proxy metric if ground truth is unavailable?

### Performance & Scalability (Must Answer Before Building Agent 4)
6. What are the actual Claude API rate limits for your subscription tier?
7. What is the measured token throughput speed?
8. How are you implementing "parallel processing" of 8 reasoning paths?
9. Have you built a prototype that processes even 10 personas? What was the time?
10. What's the fallback if runtime is 2+ hours instead of 25 minutes?

### Confidence Calculation (Must Answer Before Building Agent 2)
11. What published research supports the quality weights (1.0×, 0.9×, 0.8×)?
12. How do you calculate agreement when data types differ?
13. Have you tested this formula on historical data with known ground truth?
14. What happens when only 2 sources are available instead of 3?

### API Integration (Must Answer Before Building Any Agent)
15. What percentage of data sources must succeed for each agent to continue?
16. What's the retry strategy for transient vs. permanent failures?
17. How do you handle API deprecation?
18. Have you tested with API mocking to simulate failures?

### Data Schemas (Must Answer Before Agent Integration)
19. What are the EXACT JSON schemas for each agent's input and output?
20. What validation rules apply?
21. How do you handle schema changes between versions?

### Implementation Details (Must Answer Before Building Slash Commands)
22. What is the EXACT execution flow from `/discover-topics` to Python script completion?
23. How does Claude Code's slash command system work?

---

## SECTION 8: RECOMMENDATIONS

### Immediate Research Required (Before Writing Code)

1. **Accuracy Validation Strategy**:
   - Identify 5 historical ebook launches with known sales data
   - Define MEASURABLE accuracy metric (not semantic similarity)
   - Build validation framework before building Agent 4

2. **Agent 4 Performance Prototype**:
   - Process 10 personas through minimal ParaThinker implementation
   - Measure actual time and extrapolate to 400 personas
   - Revise runtime targets based on evidence

3. **Agent 2 Confidence Formula Revision**:
   - Research proper statistical confidence methods (Bayesian, confidence intervals)
   - Test on 10 historical demographic datasets
   - Validate that >80% confidence correlates with accuracy

4. **API Integration Testing**:
   - Build mock servers for Reddit, YouTube, Google Trends
   - Simulate all failure modes (rate limit, timeout, auth failure)
   - Document fallback strategies

5. **Data Schema Definition**:
   - Write JSON schemas for ALL inter-agent data
   - Create schema validation tests
   - Document schema evolution policy

### Specification Improvements (Update PRD Before Implementation)

1. **Add Section: Accuracy Methodology**
   - Define mathematical accuracy metric
   - Specify validation approach
   - Acknowledge limitations if ground truth unavailable

2. **Add Section: Performance Benchmarks**
   - Document measured API latency
   - Provide time estimates based on prototypes
   - Specify fallback strategies if targets missed

3. **Add Section: Data Schemas**
   - Include all JSON schemas
   - Specify validation rules
   - Document error handling for schema violations

4. **Add Section: Edge Cases**
   - Empty results
   - Disagreeing sources
   - Spam/bot data
   - Outdated data

5. **Add Section: Security & Privacy**
   - API key management
   - PII handling
   - Rate limit monitoring

6. **Revise Section: Agent 2 Confidence Calculation**
   - Replace current formula with statistically sound method
   - Provide confidence interval calculations
   - Specify inter-rater reliability metric for source agreement

### Proof of Concept Requirements

**Do NOT proceed to full implementation until these PoCs are complete:**

1. **PoC: Agent 4 Minimal (BLOCKING)**
   - Process 10 personas with 3 reasoning paths (not 8)
   - Measure actual time and accuracy
   - Validates: Runtime targets, ParaThinker feasibility

2. **PoC: Agent 2 Confidence Calculation (BLOCKING)**
   - Test formula on 5 historical demographic datasets
   - Measure: False positive rate, false negative rate
   - Validates: Checkpoint gate effectiveness

3. **PoC: Slash Command Integration (BLOCKING)**
   - Build one slash command that calls Python script
   - Test error scenarios
   - Validates: Implementation pattern works

4. **PoC: API Failure Handling (HIGH PRIORITY)**
   - Simulate Reddit/YouTube/Trends failures
   - Test graceful degradation
   - Validates: System resilience

---

## SECTION 9: RISK ASSESSMENT

| Risk | Probability | Impact | Mitigation Required |
|------|------------|--------|---------------------|
| **Agent 4 runtime exceeds 2 hours** | HIGH (70%) | CRITICAL | Build prototype, measure actual time, reduce persona count if needed |
| **Accuracy claims unvalidatable** | HIGH (80%) | CRITICAL | Define measurable metric BEFORE implementation, or drop accuracy claims |
| **Agent 2 confidence gate produces false positives** | MEDIUM (60%) | MAJOR | Revise formula using statistical methods, validate on historical data |
| **API rate limits block agent execution** | MEDIUM (50%) | MAJOR | Document all rate limits, implement backoff/retry, test with mocks |
| **Data schema mismatches between agents** | HIGH (70%) | MAJOR | Define schemas before coding, write validation tests |
| **ParaThinker doesn't improve accuracy** | MEDIUM (40%) | MAJOR | Build PoC, A/B test 1-path vs. multi-path, be ready to simplify |
| **YouTube/Reddit APIs change or deprecate** | LOW (20%) | MAJOR | Monitor API changelogs, build abstraction layer for easy replacement |
| **Claude API costs exceed budget** | LOW (30%) | MODERATE | Calculate token budgets, monitor usage, set spending alerts |
| **Slash command pattern doesn't work** | MEDIUM (40%) | MAJOR | Build PoC first, have fallback (direct Python execution) |
| **HTML dashboard adds unnecessary complexity** | LOW (30%) | MINOR | Start with text output, defer HTML to v2 |

---

## SECTION 10: OVERALL VERDICT

**READY FOR IMPLEMENTATION?** **NO** - Conditional on resolving blockers

**Conditions for Implementation Readiness:**

### MUST FIX (Blocking Issues)
1. Define measurable accuracy metric with validation strategy
2. Build Agent 4 prototype and measure actual runtime
3. Revise Agent 2 confidence formula using statistical methods
4. Document all data schemas with validation rules
5. Specify API failure handling strategies

### SHOULD FIX (High Priority)
6. Test slash command pattern with prototype
7. Validate 400-persona optimization claim
8. Document edge cases and error handling
9. Add security/privacy section

### NICE TO HAVE (Lower Priority)
10. Simplify HTML dashboard to text output for MVP
11. Reconsider git worktree complexity
12. Add cost model breakdown

**Estimated Time to Fix Blockers:** 40-60 hours
- Agent 4 prototype: 16-20 hours
- Accuracy validation framework: 12-16 hours
- Agent 2 confidence formula revision: 8-12 hours
- Data schema definition: 8-12 hours
- API failure testing: 8-12 hours

**Revised Timeline:**
- Current PRD state: NOT READY
- After blockers fixed: READY for phased implementation
- Recommended: Build Agents 0-2 first, validate, THEN build Agents 3-4

**Final Recommendation:**
This PRD shows excellent collaborative refinement and thoughtful design. However, it conflates "detailed description" with "implementable specification." The team must resist the urge to start coding and instead:

1. Build targeted prototypes (Agent 2 confidence, Agent 4 runtime)
2. Validate core assumptions (400 personas, 20-25 min runtime, 85-90% accuracy)
3. Define precise data contracts (schemas, validation rules)
4. Test failure modes (API mocks, edge cases)

**Only then** will this PRD be ready for implementation. Attempting to build now will result in discovering these issues mid-development, wasting 2-4 weeks of work.

**Proceed with caution. Prototype first, implement second.**

---

**Review Complete**
**Document saved to:** D:\Projects\Ai\Purchase-Intent\Docs\PRD-Purchase-Intent-System-v2-review.md
**Next step:** Address blocking issues before implementation kickoff
