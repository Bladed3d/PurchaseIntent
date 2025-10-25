# Purchase-Intent Development Instructions

## 🚨 TOP 5 CRITICAL RULES

1. **FAIL LOUDLY** - Never create fallback code. Raise exceptions immediately. The user is the fallback.
2. **NO PAID APIs** - User has Claude Pro subscription. Use Task tool, not Anthropic API. No additional costs.
3. **ASK BEFORE AUTOMATING** - Never create slash commands, agents, or workflows without explicit user approval.
4. **START SIMPLE** - Edit existing files before creating new ones. Minimal solution first, add complexity only when needed.
5. **COMMIT OFTEN** - Git protects work. Commit before experiments, risky changes, or major edits.

---

## Development Rules (Structured)

```json
{
  "forbidden": {
    "fallback_code": "No try/except that masks errors. No .get(key, default) that hides missing data. Fail loudly.",
    "paid_apis": "No Anthropic API, OpenAI API, or any paid service. Use Task tool for agents.",
    "silent_automation": "No unprompted slash commands, agents, or workflow changes. Always ask first.",
    "over_engineering": "No new files without justification. No complex architectures for simple tasks.",
    "fake_data": "No hard-coded mock data in application code. Test data goes in separate fixtures.",
    "default_values": "No .get(key, 0) or similar that makes missing data look real. Require the data.",
    "process_kills": "Never taskkill by process name (node.exe, electron.exe). Use specific PIDs only."
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

## Project Context

**Mission:** AI-powered purchase intent detection system
**Stack:** Python (data research), React/TypeScript (future UI)
**GitHub:** https://github.com/Bladed3d/PurchaseIntent.git
**Branch:** main

**Agents Available:**
- `lead-programmer`: Feature implementation with LED instrumentation
- `breadcrumbs-agent`: Add LED debugging infrastructure

**LED Breadcrumb Ranges:**
- 500-599: Agent 0 (Topic Research)
- 1500-1599: Agent 1 (Product Research)
- 2500-2599: Agent 2 (Demographics)
- 3500-3599: Agent 3 (Persona Generator)
- 4500-4599: Agent 4 (Intent Simulator)

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
