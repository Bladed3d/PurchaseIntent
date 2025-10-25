# Safe Iteration Workflow with Claude

## Problem
When iterating experimental features with Claude, there's risk of losing working code if experiments fail.

## Solution: Three-Stage Safety Protocol

### Stage 1: BEFORE Trying Experimental Changes

**Claude should automatically:**
```bash
# Create timestamped backup
cp file.py file.py.backup-$(date +%Y%m%d-%H%M%S)

# OR commit WIP to git
git add file.py
git commit -m "WIP: Working state before [experiment name]"
```

**User confirms:** "Yes, backup created. Proceed with experiment."

### Stage 2: DURING Experiment

**If things go wrong:**
- **Option A** (Manual backup exists): `cp file.py.backup-* file.py`
- **Option B** (Git WIP commit): `git checkout HEAD~1 -- file.py`
- **Option C** (Git stash): `git stash pop`

### Stage 3: AFTER Experiment Success

**Clean up:**
```bash
# Remove backup if experiment succeeded
rm file.py.backup-*

# OR squash WIP commits
git rebase -i HEAD~2  # Combine WIP + final commit
```

## Rules for Claude

### Always Create Backup Before:
1. `git checkout` (file revert) - VERY DESTRUCTIVE
2. `git reset` (history changes)
3. Major refactoring (>100 lines changed in one file)
4. Experimental features user asks to "try"
5. Any operation that could lose uncommitted work

### Always Ask User:
- "Should I create a backup before trying this?"
- "This changes 300 lines. Create git WIP commit first?"
- "This experiment might break things. Backup first?"

### Never Do:
- `git checkout file.py` without confirming backup exists
- `git reset --hard` without explicit user approval
- Delete files without asking
- Overwrite files >100 lines without backup

## Example Safe Workflow

```
User: "Can we try making the grid extend to 120?"

Claude: "That will modify ~50 lines of dashboard.py. Should I:
         A) Create backup file first (dashboard.py.backup-20251024)
         B) Create git WIP commit first
         C) Just try it (risky)

         Recommended: A or B"

User: "B"

Claude: [Creates WIP commit]
        "Backup created: commit abc123f
         Now trying grid extension to 120..."

[Makes changes]

User: "The labels are showing weird decimals"

Claude: "Want to:
         A) Try to fix it
         B) Revert to backup (git checkout HEAD~1 -- dashboard.py)"

User: "B - just revert"

Claude: [Reverts file]
        "Reverted. We're back to working state."
```

## Git Workflow Integration

### Daily Workflow
```bash
# Morning: Start fresh
git checkout main
git pull

# During dev: Frequent WIP commits
git add .
git commit -m "WIP: Added zoom plugin"  # Every 30-60 min

# Evening: Clean up WIP commits
git rebase -i HEAD~5  # Squash WIPs into meaningful commits
git push
```

### Experiment Workflow
```bash
# Try risky change
git stash push -m "Working state before grid experiment"

# Experiment fails
git stash pop  # Restore working state

# OR experiment succeeds
git stash drop  # Delete backup, keep changes
```

## Cost Consideration

User pays for tokens. Backing up and reverting is CHEAP compared to:
- Rebuilding lost code (expensive tokens)
- User frustration (wasted time)
- Lost productivity (redoing work)

**Always favor safety over speed.**

## Quick Reference

| Operation | Risk Level | Action Required |
|-----------|------------|-----------------|
| Edit <50 lines | Low | None |
| Edit 50-200 lines | Medium | Ask about backup |
| Edit >200 lines | High | **Require backup** |
| Refactoring | High | **Require backup** |
| Experimental feature | High | **Require backup** |
| `git checkout file` | **CRITICAL** | **Require backup verification** |
| `git reset` | **CRITICAL** | **User must explicitly approve** |

