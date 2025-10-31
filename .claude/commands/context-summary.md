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

**Step 1: Save the session (no Claude tokens used)**

Run the Python script to save the full chat:

```bash
python save-session.py
```

This creates:
- `Context/{date}/session-{timestamp}.md` - Full chat history
- Updates `PROJECT_INDEX.md` - Current project structure

**Step 2: Extract decisions (uses Claude tokens)**

Now use the session-summarizer agent to extract what matters:

```
Use the session-summarizer agent to find and analyze the most recent session file in Context/
(it may be from a previous date, not necessarily today).

Create a HANDOFF-{session-date}.md in the same directory as the session file with:
- Decisions made
- What was ruled out
- Next 3 actions
- Blockers

If a HANDOFF file already exists for that session's date, APPEND the new summary to it (don't overwrite).
Use a separator like "--- Session [timestamp] ---" between entries.
```

---

## Example Usage

```
User: /context-summary
Claude:
[Reminds user to run save-session.py first]

User: [Runs python save-session.py]

Claude:
[Automatically invokes session-summarizer agent]
[Finds and reads most recent session file (may be from previous date)]
[Creates or appends to HANDOFF file in same directory as session]
[Reports: "Session saved + summary appended to Context/2025-10-22/HANDOFF-2025-10-22.md"]
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

1. **Run save-session.py FIRST** - This is local Python, no tokens used
2. **Then let Claude extract decisions** - This uses tokens but creates actionable summary
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
