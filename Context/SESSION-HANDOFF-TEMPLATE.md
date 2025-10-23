# Session Handoff Template

**Use this at the START of each new session to orient Claude**

Copy and paste this into your new chat:

```
Read Context/[date]/HANDOFF-[latest-date].md and continue where we left off.
The handoff contains our decisions and next actions.
```

That's it. Claude will:
1. Read the handoff summary
2. Understand what was decided
3. Know what to do next
4. Ask if priorities have changed

---

# How to Create a Handoff (End of Session)

When ending a session, type:

```
/end-session
```

Or manually:

```
Use the session-summarizer agent on Context/[date]/session-[time].md
to create a handoff summary
```

This creates `HANDOFF-[date].md` with:
- ✅ Decisions made
- ❌ What was ruled out
- 🚀 What's ready to build
- 🚧 Blockers/questions
- 📋 Next 3 actions

---

# Why This Matters

**Problem:** Long context files (6000+ lines) exceed Claude's read limits
**Solution:** Decision logs extract ONLY what matters for next session
**Result:** New sessions start with full context in < 200 lines

---

# Example Handoff Flow

## End of Session 1:
You: `/end-session`
Claude: [Creates HANDOFF-2025-10-22.md with decisions and next actions]

## Start of Session 2:
You: `Read Context/2025-10-22/HANDOFF-2025-10-22.md and continue`
Claude: [Reads handoff] "I see we decided to build Agent 0 first using PRAW and YouTube API. Next action is creating a minimal PRD. Should we proceed?"

No re-explaining. No "what are we building again?" Just seamless continuation.

---

# Quick Reference Card

| When | Command | Result |
|------|---------|--------|
| **End session** | `/end-session` | Creates HANDOFF-[date].md |
| **Start session** | `Read HANDOFF-[date].md and continue` | Claude has full context |
| **Mid-session check** | `What are our next actions?` | Claude references handoff |

---

# File Locations

- **Handoffs**: `Context/[date]/HANDOFF-[date].md` (decision logs)
- **Full sessions**: `Context/[date]/session-[time].md` (complete chat)
- **Design docs**: `Docs/*.md` (approved specifications)

Use handoffs for continuity, full sessions for deep archeology.
