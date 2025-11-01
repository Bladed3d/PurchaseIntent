---
description: Save session + extract decisions when running out of context
---

# Context Summary Command

This command combines session saving with decision extraction.

**What it does:**
1. Saves the full chat session to `Context/{date}/session-{time}.md`
2. Extracts key decisions, action items, and next steps
3. Appends summary to `Context/{date}/HANDOFF-{date}.md`

**When to use:**
- When Claude Code shows context warnings
- Before running `/compact`
- At the end of any significant session

---

## Workflow

**Assumption:** User has already run `python save-session.py` before invoking this command.

**Your task:** Use the session-summarizer agent to find and analyze the most recent session file in Context/ (it may be from a previous date, not necessarily today).

Create a HANDOFF-{session-date}.md in the same directory as the session file with:
- Decisions made
- What was ruled out
- Next 3 actions
- Blockers

If a HANDOFF file already exists for that session's date, APPEND the new summary to it (don't overwrite).
Use a separator like "--- Session [timestamp] ---" between entries.

---

## Example Usage

```
User: /context-summary

Claude:
[Immediately invokes session-summarizer agent]
[Finds and reads most recent session file (may be from previous date)]
[Creates or appends to HANDOFF file in same directory as session]
[Reports: "Summary appended to Context/2025-10-22/HANDOFF-2025-10-22.md"]
```

---

## What Gets Saved

**Full Session** (`session-{timestamp}.md`):
- Complete chat history
- All tool uses
- All code blocks
- Full context for archaeology

**Handoff Summary** (`HANDOFF-{date}.md`):
- ✅ Decisions made this session
- ❌ What was ruled out
- 🚀 What's ready to build
- 🚧 Blockers/open questions
- 📋 Next 3 actions

---

## Important Notes

1. **User runs save-session.py before invoking this command** - Local Python saves full session (zero tokens)
2. **Claude immediately extracts decisions** - Uses session-summarizer agent (costs tokens but adds value)
3. **Multiple sessions per day** - HANDOFF file gets appended, not overwritten
4. **Start next session** - Read HANDOFF file to continue with full context

---

## Technical Details

**Why two steps?**
- `save-session.py` is pure Python (zero API costs, instant)
- `session-summarizer` uses Claude to extract meaning (costs tokens, adds value)
- Separating them gives you control: save everything, then choose what to analyze

**File locations:**
- Sessions: `Context/2025-10-22/session-16-39-46.md`
- Handoffs: `Context/2025-10-22/HANDOFF-2025-10-22.md`
- Index: `PROJECT_INDEX.md` (root directory)
