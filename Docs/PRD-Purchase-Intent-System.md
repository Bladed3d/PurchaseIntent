# Purchase Intent System - PRD

**Version:** 1.0
**Date:** 2025-10-22
**Status:** Approved for Development

---

## Goal

Build an AI-powered synthetic focus group system that predicts consumer purchase intent for digital products (ebooks) in minutes at zero marginal cost, achieving 7-12% higher accuracy than human focus groups.

---

## Scope

**Included:**
- CLI-based workflow with slash commands (`/discover-topics`, `/research-products`)
- 5 autonomous agents: Topic Research → Product Research → Demographics → Persona Generation → Intent Prediction
- HTML dashboard with Chart.js visualizations for interactive topic selection
- LED breadcrumb instrumentation (ranges 500-4599) for autonomous debugging
- Human checkpoints for validation between agent runs
- Persona reusability (test unlimited products with same 500 personas)

**Excluded:**
- Web UI or desktop application (CLI only for MVP)
- Real-time collaborative features (single-user sessions)
- API endpoints or SaaS offering (in-house tool only)
- Integration with external CRM/marketing platforms
- Non-ebook product categories (future expansion)

---

## User Experience

### Phase 1: Interactive Topic Discovery

1. User runs: `/discover-topics productivity`
2. **Agent 0** researches demand signals across:
   - Google Trends (search volume)
   - Reddit (pain points, discussions)
   - Amazon Kindle (competitor gaps)
   - YouTube (engagement metrics)
   - X/Twitter (trending topics)
3. HTML dashboard auto-opens in browser showing:
   - Top 5-10 topics ranked by demand score
   - Visual charts (bar chart of scores, trend lines)
   - Evidence cards for each topic (search volume, competition, audience clarity)
4. User clicks preferred topic to select

**Deliverable:** `data/sessions/{session_id}/topic-selection.json`

### Phase 2: Automated Research Pipeline

1. User runs: `/research-products "Overcoming Procrastination for ADHD Remote Workers"`
2. **Agents 1-4 run sequentially** with checkpoints:
   - **Agent 1:** Finds 5-10 comparable products (Amazon, YouTube, Reddit), discovers hidden segments via subreddit overlap
   - **Checkpoint 1:** User approves comparables
   - **Agent 2:** Extracts demographics (age, occupation, interests) from 500+ reviews/comments, triangulates across 3+ sources
   - **Checkpoint 2:** User approves demographics (confidence target: 80%+)
   - **Agent 3:** Generates 500 synthetic personas with psychographic conditioning, saves to reusable JSON
   - **Checkpoint 3:** User reviews persona distribution
   - **Agent 4:** Simulates 500 personas × 8 reasoning paths (ParaThinker) = 4,000 perspectives, outputs purchase intent distribution
   - **Checkpoint 4:** User reviews final report

**Deliverable:** `reports/{session_id}/intent-prediction-report.html`

---

## Technical Approach

### 5 Agents

- **Agent 0: Topic Research** (LED 500-599)
  Discovers high-demand ebook topics using Brian Moran's "Rule of One" strategy. Outputs scored topics for user selection.

- **Agent 1: Product Research** (LED 1500-1599)
  Finds comparable products, scrapes reviews/comments, discovers hidden audience segments via Reddit overlap analysis.

- **Agent 2: Demographics Analyst** (LED 2500-2599)
  Extracts customer demographics from text data, triangulates across 3+ sources, calculates confidence scores.

- **Agent 3: Persona Generator** (LED 3500-3599)
  Creates 500 synthetic customer personas with realistic psychographic profiles, saves as reusable asset.

- **Agent 4: ParaThinker Intent Simulator** (LED 4500-4599)
  Simulates purchase intent using 8 parallel reasoning paths (VALUE, FEATURES, EMOTIONS, RISKS, SOCIAL PROOF, ALTERNATIVES, TIMING, TRUST). Uses SSR (Semantic Similarity Rating) for realistic distributions.

### Implementation Steps

1. **Create slash command infrastructure** (reuse pattern from `.claude/commands/end-session.md`)
   - `/discover-topics [niche]` → Invokes Agent 0
   - `/research-products [topic]` → Invokes Agents 1-4 sequentially

2. **Build Agent 0 with HTML dashboard output** (reuse HTML template pattern if exists, or create minimal Chart.js template)
   - Python script for research logic
   - Jinja2 template for HTML report
   - Auto-open browser with `webbrowser.open()`

3. **Implement LED breadcrumb system** (reuse pattern from `CLAUDE.md` LED ranges)
   - Create `lib/breadcrumbs.py` utility
   - Log to `logs/agent-{N}-breadcrumbs.log`

4. **Build Agents 1-4 as Python modules** (modular architecture per `CLAUDE.md`)
   - Each agent: `agents/agent_{N}.py` < 300 lines
   - Data handoff via JSON: `data/sessions/{session_id}/agent{N}-output.json`
   - Checkpoint prompts between agents

5. **Create autonomous development loop workflow** (git worktrees + quality gates)
   - Lead Programmer → LED Breadcrumbs Agent → Testing Agent → Debug Agent (if needed) → Loop
   - Git worktree per agent for parallel development
   - Quality gates: IMPLEMENTED → INSTRUMENTED → TESTED → VALIDATED → MERGED

### Development Workflow

**Project Manager Orchestration:**

The Project Manager agent (`.claude/agents/project-manager.md`) orchestrates all development using three parallel execution patterns:

1. **Git Worktree Setup** (One-time initialization)
   ```bash
   cd D:\Projects\Ai\Purchase-Intent
   git worktree add ../pi-agent-0 main  # Agent 0: Topic Research
   git worktree add ../pi-agent-1 main  # Agent 1: Product Research
   git worktree add ../pi-agent-2 main  # Agent 2: Demographics Analyst
   git worktree add ../pi-agent-3 main  # Agent 3: Persona Generator
   git worktree add ../pi-agent-4 main  # Agent 4: ParaThinker Simulator
   ```

2. **Autonomous Loop Protocol** (Per Agent in Each Worktree)
   ```
   IMPLEMENTED:   Lead Programmer creates agent code
        ↓
   INSTRUMENTED:  Breadcrumbs Agent adds LED debugging (ranges 500-4599)
        ↓
   TESTED:        Testing Agent validates functionality
        ↓         (If fails → Debug Agent analyzes breadcrumbs → Loop to Lead Programmer)
   VALIDATED:     Manual user acceptance test
        ↓
   MERGED:        Git merge from worktree to main repository
   ```

3. **Parallel Development Patterns**

   **Pattern A: Parallel Implementation Across Agents**
   ```javascript
   // Deploy 5 Lead Programmers simultaneously (one per worktree)
   Task(subagent: "Lead Programmer", desc: "Agent 0", worktree: "../pi-agent-0")
   Task(subagent: "Lead Programmer", desc: "Agent 1", worktree: "../pi-agent-1")
   Task(subagent: "Lead Programmer", desc: "Agent 2", worktree: "../pi-agent-2")
   Task(subagent: "Lead Programmer", desc: "Agent 3", worktree: "../pi-agent-3")
   Task(subagent: "Lead Programmer", desc: "Agent 4", worktree: "../pi-agent-4")
   ```

   **Pattern B: Parallel Instrumentation**
   ```javascript
   // After implementations complete, instrument all 5 agents in parallel
   Task(subagent: "breadcrumbs-agent", desc: "Agent 0 LED", worktree: "../pi-agent-0")
   Task(subagent: "breadcrumbs-agent", desc: "Agent 1 LED", worktree: "../pi-agent-1")
   Task(subagent: "breadcrumbs-agent", desc: "Agent 2 LED", worktree: "../pi-agent-2")
   Task(subagent: "breadcrumbs-agent", desc: "Agent 3 LED", worktree: "../pi-agent-3")
   Task(subagent: "breadcrumbs-agent", desc: "Agent 4 LED", worktree: "../pi-agent-4")
   ```

   **Pattern C: Pipeline Overlap Optimization**
   ```javascript
   // Work on Agent 3 while testing Agent 2 and instrumenting Agent 1
   Task(subagent: "Lead Programmer", desc: "Agent 3 Implementation")
   Task(subagent: "breadcrumbs-agent", desc: "Agent 2 Instrumentation")
   Task(subagent: "testing-agent", desc: "Agent 1 Testing")
   ```

**Quality Gates (Purchase-Intent Specific):**
- **IMPLEMENTED**: Agent code works manually with sample data
  - Agent 0: Discovers topics from test niche
  - Agent 1: Finds comparable products
  - Agent 2: Extracts demographics from sample reviews
  - Agent 3: Generates 500 test personas
  - Agent 4: Predicts intent with 8-path reasoning

- **INSTRUMENTED**: LED breadcrumbs added per agent
  - Agent 0: Breadcrumbs 500-599
  - Agent 1: Breadcrumbs 1500-1599
  - Agent 2: Breadcrumbs 2500-2599
  - Agent 3: Breadcrumbs 3500-3599
  - Agent 4: Breadcrumbs 4500-4599

- **TESTED**: Automated tests pass
  - Unit tests for core functions
  - Integration tests for data handoffs
  - LED breadcrumb sequence validation

- **VALIDATED**: User acceptance test complete
  - Agent output matches expected format
  - Accuracy meets targets (Agent 2: 80%+, Agent 4: 85-90%)
  - Human checkpoint approval received

- **MERGED**: Code integrated into main branch
  ```bash
  cd D:\Projects\Ai\Purchase-Intent
  git merge --no-ff pi-agent-0/main -m "Merge Agent 0: Topic Research"
  # Repeat for each validated agent
  ```

**Merge Strategy:**
- Merge agents sequentially after VALIDATED status
- Test integration after each merge
- Final system test with all 5 agents together
- Only mark MVP complete when full pipeline works end-to-end

---

## Success Metrics

1. **Accuracy:** 85-90% correlation with human survey responses (validate Agent 4 output against PickFu or similar)
2. **Speed:** 35 minutes end-to-end (Agent 0: 15 min, Agents 1-4: 20 min) vs. 2-4 weeks for human focus groups
3. **Cost:** $0 per test during beta (Claude Code subscription) vs. $5,000-20,000 human focus groups
4. **Persona Reusability:** Test 100+ product variants with same 500 personas (marginal cost = $0)
5. **Hidden Segments Discovered:** Agent 1 identifies at least 2 underserved audience segments per product (via subreddit overlap)

---

## Technical Decisions

**Decision 1: Python CLI + Slash Commands (not Skills)**
*Rationale:* Agents require explicit user invocation for control over workflow. Skills would auto-trigger unpredictably. Slash commands provide clear entry points and match Claude Code's native pattern.

**Decision 2: HTML Dashboards with Chart.js (not terminal tables)**
*Rationale:* Visual topic selection is faster and more intuitive than scrolling terminal output. Chart.js is lightweight (no heavy framework). Auto-opens in browser for seamless UX.

**Decision 3: Zero Marginal Cost Model (Claude Code Subscription)**
*Rationale:* Beta deployment as in-house service eliminates per-request API costs. Unlimited testing during development. Optional SaaS pricing post-MVP if scaling beyond personal use.

**Decision 4: LED Breadcrumbs for Autonomous Debugging (500-4599 ranges)**
*Rationale:* Console output is machine-readable, enabling Claude to debug autonomously via grep/log analysis. Non-overlapping ranges isolate failures to specific agents instantly.

**Decision 5: ParaThinker 8-Path Architecture**
*Rationale:* Research shows 7-12% accuracy boost vs. sequential reasoning. Eliminates tunnel vision (70% conformity in human focus groups). Each path is independent, parallelizable.

---

**END OF PRD**

*For detailed agent specifications, see:* `Docs/4-agents-design.md`
*For development guidelines, see:* `CLAUDE.md`
