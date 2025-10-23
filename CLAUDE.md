# Purchase-Intent - Development Instructions

## Project Mission
Build a clean, modern application that detects and analyzes purchase intent signals using AI-powered analysis.

## Technical Standards & Stack

### Core Technology Stack:
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Node.js** - Backend services

### Architecture Requirements:
- **Components < 400 lines** - Keep everything maintainable
- **LED Breadcrumbs** - Instrument all critical operations (ranges 1000-9099)
- **Quality first** - Robust, production-ready code only

## Available Agents
- **breadcrumbs-agent**: Adds LED infrastructure to functional code
- **lead-programmer**: Implements features with LED instrumentation

## Modular Architecture Standards
**CRITICAL: All code must follow strict modularization to prevent bloat**

**File Size Limits (STRICTLY ENFORCED):**
- Components: < 400 lines maximum
- Services: < 300 lines maximum
- Main app files: < 200 lines (orchestration only)
- Utilities: < 150 lines maximum

**Directory Structure:**
```
src/
├── components/
│   ├── common/           # Reusable UI < 100 lines
│   └── intent/           # Intent detection UI < 400 lines
├── services/
│   ├── detection/        # Intent detection logic
│   ├── analytics/        # Analytics processing
│   └── storage/          # Data persistence
├── hooks/                # Custom React hooks < 100 lines
├── types/                # TypeScript definitions
└── lib/                  # Utilities and breadcrumb system
```

**Separation Rules:**
1. ONE RESPONSIBILITY per file
2. NO business logic in UI components
3. Services handle data/state management
4. Components only handle presentation
5. Hooks bridge services and components
6. Communication: Service → Hook → Component

## ANTI-OVER-ENGINEERING PROTOCOL
**CRITICAL: Cost-conscious development - every token matters**

### Start Simple, Add Complexity Only When Needed
**Default approach: Minimal viable solution**

Before implementing ANY feature or creating ANY document:

1. **Deletion First**: Can we achieve this by REMOVING or simplifying existing code?
2. **One File Challenge**: Can this be done by editing a SINGLE existing file?
3. **Pattern Detective**: Find similar patterns already in the codebase - reuse them
4. **No New Files Without Strong Justification**: Prefer editing over creating

### The PRD/Documentation Rule
When creating any planning document:
- **First draft**: Single page, bullet points, essentials only (< 100 lines)
- **Show minimal version FIRST**: Let user review before expanding
- **Iterate UP not DOWN**: Add detail only when user explicitly requests it
- **Never spend 30+ minutes on a planning document**

**Example of what NOT to do:**
- ❌ Creating a 4-agent architecture document that takes 30+ minutes
- ❌ Adding detailed sections the user didn't request
- ❌ Building enterprise-scale solutions for simple apps

**What TO do instead:**
- ✅ Simple bullet list (5 minutes max)
- ✅ User reviews and provides feedback
- ✅ Expand only requested sections
- ✅ Keep it under 200 lines unless explicitly asked for more

### Complexity Approval Required
**These require explicit user approval BEFORE implementing:**
- Creating new files (explain why editing existing files won't work)
- Introducing new patterns not found in codebase
- Adding new dependencies or frameworks
- Architectural changes or refactoring
- Any solution that touches > 3 files

### Quality ≠ Complexity
- Production-ready does NOT mean complex architecture
- Simple, tested code > elaborate abstractions
- Every line of code = future maintenance burden
- Fewer files = fewer bugs = lower cost

## Development Rules
✅ **Always do:**
- **START WITH THE SIMPLEST SOLUTION THAT WORKS**
- Add LED breadcrumbs to critical operations
- Use TypeScript for type safety
- Test thoroughly before claiming complete
- Build for maintainability
- **Follow modular architecture strictly**
- **Reuse existing patterns from the codebase**

❌ **Never do:**
- Over-engineer solutions (bicycle not spaceship)
- Create components over 400 lines
- Skip error handling
- Compromise quality for speed
- **Put business logic in UI components**
- **Create monolithic files**
- **Hard-code fake/mock data directly into application code**
- **Create new files without strong justification**

## LED Breadcrumb System - Debugging Protocol

### 🚨 CRITICAL: LED Breadcrumbs Are Claude's Responsibility

**The LED breadcrumb system exists specifically to enable Claude to debug problems autonomously.**

❌ **NEVER tell the user to:**
- "Monitor the console output"
- "Watch the LED breadcrumbs"
- "Check the terminal for breadcrumb numbers"
- "Look at the console to see what's happening"

✅ **Claude MUST:**
- **Read the console output yourself** using Playwright or browser tools
- **Grep log files** for specific breadcrumb ranges when debugging
- **Analyze breadcrumb sequences** to identify where processes fail
- **Use breadcrumb numbers** to pinpoint exact failure locations
- **Present findings to user** with specific breadcrumb evidence

### Why This Matters:
The console output contains too much data for humans to monitor effectively. LED breadcrumbs (numbered 1000-9099) are designed to be machine-readable so Claude can:
1. Quickly filter logs for relevant operations
2. Identify exactly which step in a process failed
3. Trace execution flow through complex operations
4. Provide precise debugging information to the user

### Debugging Workflow:
When investigating an issue:
1. **Use Playwright/browser tools** to capture console output
2. **Grep for breadcrumb ranges** relevant to the problem area
3. **Analyze the sequence** to find where execution stopped or errored
4. **Report findings** to user with specific breadcrumb numbers and what they mean
5. **Propose fixes** based on breadcrumb evidence

**Example:**
```
User: "The intent detection isn't working"

Claude: [Uses browser tools to check console]
Claude: "I found the issue. LED breadcrumb 2045 fired successfully
        (data validation complete), but breadcrumb 2050 (starting
        intent analysis) never appeared. This indicates the problem is
        in the transition between validation and analysis processing.
        Let me check the validation completion handler..."
```

### LED Breadcrumb Ranges
- **1000-1099**: Application startup and initialization
- **2000-2099**: Intent detection and classification
- **3000-3099**: Data processing and transformation
- **4000-4099**: ML inference and predictions
- **5000-5099**: Analytics and reporting
- **6000-6099**: API integration
- **7000-7099**: UI interactions and state management
- **8000-8099**: Error handling and recovery
- **9000-9099**: Testing and validation

## Data Policy
**CRITICAL: NO FAKE DATA IN APPLICATION CODE**

✅ **Acceptable for testing/development:**
- External test data files in `tests/fixtures/` or `docs/test-data/`
- Separate mock data services that can be easily disabled/removed
- User-supplied test data during development sessions
- Environment-based data loading (development vs production)

❌ **NEVER acceptable:**
- Hard-coded mock data directly in components or services
- Fake user data embedded in application logic
- Sample data that ships with production code
- Demo content that cannot be easily removed

**Rationale:** Hard-coded fake data creates maintenance debt, confuses users, and can accidentally ship to production. Always keep test data separate from application code.

## Version Control & Git Workflow
**CRITICAL: This project uses git for version control**

### GitHub Repository
- **Remote:** https://github.com/Bladed3d/PurchaseIntent.git
- **Branch:** main
- **Status:** Active, all work must be committed

### Document Versioning Protocol
When user asks to "version" a document:
1. ✅ **CORRECT:** Create new file with version suffix
   - Example: `design-v1.md` → keep original, create `design-v2.md`
   - OR: `design.md` → keep original, create `design-2024-10-22.md`
2. ❌ **WRONG:** Edit the original file in place
   - Never overwrite original documents
   - Never just update version number in metadata

### Git Commit Workflow
**Before making significant changes:**
1. Check git status: `git status`
2. Create feature branch if needed: `git checkout -b feature/agent-0`
3. Make changes
4. Stage files: `git add [files]`
5. Commit with descriptive message
6. Push to GitHub: `git push origin [branch]`

**Commit message format:**
```
Brief description of changes (50 chars max)

- Bullet point of what changed
- Why the change was needed
- Any breaking changes

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### What to Commit
✅ **Always commit:**
- Source code files
- Documentation (Docs/*.md)
- Architecture designs
- Configuration files (CLAUDE.md, .claude/*)
- Session handoff files (Context/**/HANDOFF-*.md)

❌ **Never commit:**
- API keys or secrets (.env files)
- Large session logs (Context/**/session-*.md)
- Temporary data (temp/, cache/)
- Node modules or Python venv
- Personal notes with sensitive info

See `.gitignore` for complete list.

### Critical Lesson
**Why this matters:** In session 2025-10-22, a document (4-agents-design.md v1.1) was overwritten instead of versioned, destroying original work. Git prevents this by:
- Tracking all changes
- Allowing reversion to any previous state
- Preserving history even when files are edited

**Always commit before major changes** to create recovery points.

## Success Criteria
- Clean, maintainable codebase that any developer can understand
- Comprehensive LED breadcrumb coverage for debugging
- Production-ready with robust error handling
- Zero hard-coded fake data in production code
- **All significant work committed to git with clear history**
