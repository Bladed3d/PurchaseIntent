# End Session - Update Daily Handoff

When user says "run /end-session" or "/end-session", launch the session-summarizer agent to update today's handoff file.

## What This Does

1. Reviews the Context/[today's date]/ folder
2. Finds the main HANDOFF file (e.g., HANDOFF-2025-10-24.md)
3. Identifies which session-*.md files haven't been summarized yet
4. Summarizes new sessions and appends to the HANDOFF file
5. Maintains ONE handoff file per day (not multiple)
6. **KEEPS original session files** (does not delete them)

## Execute Directly

DO NOT use SlashCommand tool - it causes double execution.

Instead, immediately use Task tool:

```
Task tool with:
- subagent_type: "session-summarizer"
- description: "Update today's handoff file"
- prompt: "Review Context/[current date]/ folder. Find the main HANDOFF file. Check which session files have NOT been summarized yet. Summarize any new sessions and update the single handoff file. Follow the established pattern of maintaining ONE handoff file per day. IMPORTANT: Do not delete source session files after processing."
```

## Important

- This preserves the user's existing workflow
- One clean handoff file per day
- New session summaries are APPENDED, not creating new files
- **Original session-*.md files are PRESERVED** (not deleted)
- Agent processes ALL unsummarized sessions in one pass
