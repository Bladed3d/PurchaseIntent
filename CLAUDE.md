# Purchase-Intent Development Instructions

## 🚨 TOP 6 CRITICAL RULES

1. **NEVER COMMIT SECRETS** - API keys, tokens, passwords MUST NEVER touch git. Breadcrumb system auto-sanitizes, but NEVER log secrets intentionally.
2. **FAIL LOUDLY** - Never create fallback code. Raise exceptions immediately. The user is the fallback.
3. **NO PAID APIs** - User has Claude Pro subscription. Use Task tool, not Anthropic API. No additional costs.
4. **ASK BEFORE AUTOMATING** - Never create slash commands, agents, or workflows without explicit user approval.
5. **START SIMPLE** - Edit existing files before creating new ones. Minimal solution first, add complexity only when needed.
6. **COMMIT OFTEN** - Git protects work. Commit before experiments, risky changes, or major edits.

---

## Development Rules (Structured)

```json
{
  "forbidden": {
    "commit_secrets": "NEVER commit API keys, tokens, passwords. NEVER log them in breadcrumbs. NEVER include them in error messages. .env ONLY.",
    "fallback_code": "No try/except that masks errors. No .get(key, default) that hides missing data. Fail loudly.",
    "paid_apis": "No Anthropic API, OpenAI API, or any paid service. Use Task tool for agents.",
    "silent_automation": "No unprompted slash commands, agents, or workflow changes. Always ask first.",
    "over_engineering": "No new files without justification. No complex architectures for simple tasks.",
    "fake_data": "No hard-coded mock data in application code. Test data goes in separate fixtures.",
    "default_values": "No .get(key, 0) or similar that makes missing data look real. Require the data.",
    "process_kills": "Never taskkill by process name (node.exe, electron.exe). Use specific PIDs only.",
    "log_secrets": "NEVER trail.light() with api_key, token, secret fields. NEVER print API responses with credentials."
  },
  "required": {
    "fail_loudly": "Raise ValueError/KeyError immediately when data is missing or APIs fail.",
    "ask_before_create": "Propose slash commands/automation, explain what it does, wait for 'yes'.",
    "start_simple": "Can we delete code? Edit one file? Reuse existing patterns? Do that first.",
    "commit_before_risk": "git commit before experiments, large edits (>200 lines), or git checkout.",
    "led_breadcrumbs": "Instrument critical operations. Use breadcrumbs to debug, not user.",
    "modular_code": "Components <400 lines, Services <300 lines, Utils <150 lines.",
    "one_responsibility": "One file = one job. No business logic in UI components."
  },
  "workflow": {
    "planning_docs": "First draft: <100 lines, bullet points only. Show user FIRST. Iterate up, not down.",
    "git_commits": "Commit message: Brief title + bullet points + Co-Authored-By: Claude",
    "error_handling": "Clear error messages. Tell user what failed and what to check (API key, quota, file path).",
    "debugging": "Claude reads console/logs using Grep, not user. Present findings with LED breadcrumb numbers."
  }
}
```

---

## 📚 Documentation Guide (New Claude Chats Start Here)

**If you're a new Claude session, read these in order:**

1. **Docs/PRD-Purchase-Intent-System-v3.md** (LATEST) - Complete system overview
   - All 5 agents explained
   - Agent 0 complete status + tiered strategy
   - Agents 1-4 specifications + next steps

2. **Docs/drill-down-prd.md** - Agent 0 workflow (IMPLEMENTED)
   - Tiered API strategy (drill-down/regular/validation modes)
   - Complete user-facing workflow with examples

3. **Docs/rate-limit-analysis.md** - Quota budgets for all agents
   - Agent 0: YouTube bottleneck (solved with tiered strategy)
   - Agents 1-4: Mostly ZERO quota cost (Task tool + web scraping)

4. **This file** (CLAUDE.md) - Project rules and context

**Quick Status:**
- ✅ Agent 0 (Topic Research): Complete with quota visualization
- ⏳ Agents 1-4: Not started, ready to build

---

## Project Context

**Mission:** AI-powered purchase intent detection system
**Stack:** Python (data research), React/TypeScript (future UI)
**GitHub:** https://github.com/Bladed3d/PurchaseIntent.git
**Branch:** main
**Current PRD:** Docs/PRD-Purchase-Intent-System-v3.md (2025-10-31)

**Agents Available:**
- `lead-programmer`: Feature implementation with LED instrumentation
- `breadcrumbs-agent`: Add LED debugging infrastructure

**LED Breadcrumb Ranges:**
- 500-599: Agent 0 (Topic Research)
  - 510-519: Google Trends operations
  - 520-529: Reddit operations + Purchase Intent (525-529)
  - 530-539: YouTube operations (optional, validation only)
  - 540-549: Scoring and competition analysis
- 1500-1599: Agent 1 (Product Research)
- 2500-2599: Agent 2 (Demographics)
- 3500-3599: Agent 3 (Persona Generator)
- 4500-4599: Agent 4 (Intent Simulator)

---

## Tiered API Strategy (NEW - 2025-10-31)

**Problem:** YouTube quota limited (10,000 units/day), Google Trends rate limited

**Solution:** Use unlimited sources for exploration, expensive sources for final validation

### Three Operating Modes:

**1. Drill-Down Mode (Exploration)**
```bash
python agents/agent_0/main.py --drill-down-mode "topic"
```
- Sources: Reddit + AI Agent Research only
- Quota: ZERO cost (unlimited exploration)
- Confidence: 60% (acceptable for finding candidates)
- Use: Drill 3-5 levels deep, analyze 20-100 topics

**2. Regular Mode (Standard)**
```bash
python agents/agent_0/main.py "topic"
```
- Sources: Reddit + Google Trends
- Quota: Low (15 calls/hour with 24hr cache)
- Confidence: 100% if both sources have data
- Use: Standard analysis with trend signals

**3. Validation Mode (Final Decision)**
```bash
python agents/agent_0/main.py --enable-youtube "specific niche topic"
```
- Sources: Reddit + Google Trends + YouTube
- Quota: HIGH (~1,000 YouTube units per topic)
- Confidence: 100% if all 3 sources have data
- Use: Validate final 1-3 topics before writing book

### Quota Budgets:
- Reddit: 3,600 calls/hour (effectively unlimited)
- Google Trends: ~15 calls/hour safe (with caching)
- YouTube: 10,000 units/day = 10-20 topics max

### Recommended Workflow:
1. Explore with --drill-down-mode (unlimited, fast)
2. Select top 3 ultra-niches
3. Validate with --enable-youtube (uses 30% daily quota)
4. Choose 1 topic to write about

### Complete Quota Analysis:
See **Docs/rate-limit-analysis.md** for:
- System-wide capacity planning (all 5 agents)
- Daily usage patterns and bottlenecks
- Agent 1-4 quota impact (spoiler: mostly ZERO - Task tool FTW!)

---

## 🔒 SECURITY: API Key Protection

**CRITICAL: Previous Claude session exposed Google API key to GitHub by logging it in breadcrumbs.jsonl**

### Protections Implemented:

1. **Automatic Sanitization** (`lib/breadcrumb_system.py`)
   - Auto-redacts API keys before writing to logs
   - Detects patterns: AIza..., sk-..., Bearer tokens, etc.
   - Redacts keys by name: api_key, token, secret, password, etc.

2. **.gitignore Protection**
   - `logs/` directory NEVER committed
   - `*.jsonl` files blocked
   - `.env` and credentials blocked

3. **Pre-Commit Hook** (`.git/hooks/pre-commit`)
   - Scans every commit for secret patterns
   - Blocks commit if API keys detected
   - Must pass security check before push

4. **Developer Responsibility**
   - NEVER `trail.light(id, {"api_key": key})` - sanitizer will redact it anyway
   - NEVER print API responses that might contain credentials
   - NEVER log full error messages from API clients (may contain tokens in URLs)
   - ALWAYS use `os.getenv('API_KEY')` - never hardcode

### If You Accidentally Commit a Secret:

1. **Revoke the key IMMEDIATELY** at the API provider's console
2. **Generate new key** and update `.env`
3. **Remove from git history:**
   ```bash
   # Find the commit
   git log --all -p | grep "YOUR_SECRET"

   # Remove file from history
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch FILE_WITH_SECRET" \
     --prune-empty --tag-name-filter cat -- --all

   # Force push to overwrite GitHub
   git push origin --force --all
   ```

### Why This Matters:

**Claude Code/Anthropic provides ZERO secret protection.** They will blindly commit your API keys if you're not careful. The protections above were implemented BY THIS PROJECT, not by Anthropic.

**DO NOT TRUST Claude/Anthropic to protect your secrets. They won't.**

---

## Code Examples

### ❌ WRONG - Silent Fallback
```python
try:
    data = api.fetch()
except:
    data = hardcoded_patterns()  # User never knows API failed!
```

### ✅ CORRECT - Fail Loudly
```python
data = api.fetch()
if not data:
    raise ValueError("API returned no data. Check YOUTUBE_API_KEY and quota at console.cloud.google.com")
```

### ❌ WRONG - Hidden Missing Data
```python
subscribers = channel.get('subscriberCount', 0)  # 0 looks real!
```

### ✅ CORRECT - Require Data
```python
subscribers = channel['subscriberCount']  # KeyError if missing - GOOD!
if subscribers == 0:
    raise ValueError(f"Channel {channel_id} has 0 subscribers - invalid data")
```

---

## File Size Limits

| Type | Max Lines | Notes |
|------|-----------|-------|
| Components | 400 | UI presentation only |
| Services | 300 | Business logic/data |
| Main files | 200 | Orchestration only |
| Utilities | 150 | Helper functions |

---

## Git Workflow

**Always commit:**
- Source code
- Documentation (Docs/*.md)
- Config (CLAUDE.md, .claude/*)
- Handoff files (Context/**/HANDOFF-*.md)

**Never commit:**
- API keys (.env)
- Session logs (Context/**/session-*.md)
- Cache/temp data
- node_modules or Python venv

**Before risky changes:**
```bash
git add .
git commit -m "WIP: Working state before experiment"
```

---

## Anti-Patterns to Avoid

1. **"I'll create a fallback..."** → NO. Fail loudly instead.
2. **"Let me add a try/except..."** → Only if you re-raise or log for debugging.
3. **"I'll create a new file for this..."** → Can you edit existing file instead?
4. **"Let me build a slash command for you..."** → Ask first. User might prefer manual control.
5. **"The API failed, so I'll use patterns..."** → NO. Tell user API failed and stop.

---

## Success Criteria

✅ Code fails fast with clear error messages
✅ No hidden fallbacks or silent degradation
✅ User knows immediately when something breaks
✅ Simple solutions that edit existing files
✅ All work committed to git regularly
✅ LED breadcrumbs for autonomous debugging
