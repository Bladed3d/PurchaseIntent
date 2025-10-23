# Anti-Over-Engineering Quick Reference

## Problem
Claude defaults to enterprise-scale solutions, wasting time and tokens on unnecessary complexity.

## Solution Implemented

### 1. Updated CLAUDE.md Files
Both global (`~/.claude/CLAUDE.md`) and project (`CLAUDE.md`) now contain:
- **Anti-Over-Engineering Protocol**: Forces minimal solutions first
- **Documentation Rule**: Max 10 min on initial drafts, < 100 lines
- **Complexity Approval Process**: Must ask before creating new files/patterns
- **Quality ≠ Complexity**: Simple code is better code

### 2. Created PRD-Simplifier Subagent
**Location**: `.claude/agents/prd-simplifier.md`

**When to use**: When you need any planning document, PRD, spec, or architecture design

**How to invoke**:
```
You: "I need a PRD for [feature]"
You: "Use the prd-simplifier agent"
```

Or with the Task tool in conversations with Claude.

**What it does**:
- Creates minimal bullet-point PRDs (< 100 lines)
- Focuses on reusing existing code patterns
- Shows you the minimal version FIRST
- Only expands sections you explicitly request
- Saves you time and money

## Quick Commands for You

### When Claude Over-Engineers
Say: **"That's too complex. What's the simplest version that works?"**

### When Creating PRDs
Say: **"Use the prd-simplifier agent to create a minimal PRD"**

### When Claude Suggests New Files
Say: **"Can we do this by editing existing files instead?"**

### When You See Elaborate Plans
Say: **"Show me the 5-minute version first"**

## What Changed in Your Workflow

**Before:**
- Claude creates 4-agent document → 30+ minutes wasted
- Elaborate PRDs with sections you didn't need
- New files for things that could edit existing files
- Enterprise architecture for simple apps

**After:**
- Claude must show minimal version first (< 10 min)
- Must ask before creating new files
- Must reuse existing patterns
- Must get approval before expanding

## Emergency Override

If Claude still over-engineers despite these rules, paste this:

```
STOP. Re-read the ANTI-OVER-ENGINEERING PROTOCOL in CLAUDE.md.
I need the MINIMAL solution, not an enterprise architecture.
Can you do this by editing 1-2 existing files? Show me that approach first.
```

## Success Indicators

You'll know it's working when:
- ✅ PRDs are < 100 lines initially
- ✅ Claude asks "Should I proceed with this simple approach?"
- ✅ Solutions reuse existing code patterns
- ✅ You say "yes, go ahead" more often than "that's too complex"
- ✅ Less time planning, more time building

## Cost Savings

**Before**: 30-60 minutes on over-engineered plans = 50,000-100,000 tokens wasted
**After**: 5-10 minutes on minimal plans = 10,000-20,000 tokens used
**Savings**: ~80% reduction in planning overhead

## File Versioning Reminder

When you say "version this document," Claude should:
1. ✅ Keep the original file as-is
2. ✅ Create a new file with changes (e.g., `document-v2.md`)
3. ❌ NOT just type "Version 2" inside the existing document

## Notes

- These rules are now permanent in your CLAUDE.md files
- Every Claude session will load these instructions
- The prd-simplifier agent is always available
- You can still request detailed documentation when needed - just ask explicitly

## Testing It Out

Next time you need a PRD, try:
```
"I need a PRD for adding user profile editing. Use the prd-simplifier agent."
```

You should get a focused, minimal document in < 10 minutes that you can approve or request expansions for.
