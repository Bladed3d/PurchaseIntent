---
description: Creates a handoff summary at the end of a session for seamless context transfer to the next session
---

You are ending a work session and need to create a handoff summary for the next session.

## Instructions

1. **Find the current session file**
   - Look in `Context/2025-10-22/` (or current date folder)
   - Identify the most recent `session-*.md` file

2. **Use the session-summarizer agent**
   - Launch it with: Task tool, subagent_type: "general-purpose"
   - Provide it the session file path
   - Have it extract decisions and next actions

3. **Create handoff document**
   - Save to: `Context/[date]/HANDOFF-[date].md`
   - Format: Decision log (NOT chat summary)
   - Length: < 200 lines

4. **Confirm with user**
   - Show the handoff summary
   - Ask: "Does this capture our decisions? Anything missing?"

## What the Handoff Should Include

✅ **Essential:**
- Primary goal (one sentence)
- Key decisions made
- What was ruled out
- Next 3 concrete actions
- Blockers/open questions

❌ **Don't include:**
- Play-by-play chat recap
- Verbatim quotes
- Implementation details (those go in design docs)
- Speculation about future phases

## User's Next Session

Tell the user:

"Next time you start a session, open `Context/[date]/HANDOFF-[date].md` and paste it in chat, or simply say: 'Read the handoff file and continue where we left off.'"

This ensures seamless continuity without re-explaining everything.
