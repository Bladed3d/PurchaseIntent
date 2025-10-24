# 🪟 LED Monitoring Instructions for Purchase Intent System (Python on Windows)

**⚠️ CRITICAL: This is a WINDOWS machine running PYTHON CLI agents. Use Windows path format.**

## Windows Path Format Rules:
- ✅ Use forward slashes OR escaped backslashes: `D:/Projects/` or `D:\\Projects\\`
- ✅ Quote all paths with spaces: `"D:\Projects\Ai\Purchase-Intent"`
- ❌ NEVER use Linux paths like `/mnt/d/` or `/d/`
- ❌ NEVER use PowerShell cmdlets (Get-Process, Where-Object, etc.) in Bash tool

---

## Quick Start: Running Agent with LED Monitoring

### Step 1: Run Python Agent with Log Capture

```bash
# Git Bash command (Windows compatible):
cd "D:/Projects/Ai/Purchase-Intent" && python agents/agent_0/main.py > logs/agent0-run.log 2>&1

# Alternative: Run in background and monitor
python agents/agent_0/main.py > logs/agent0-run.log 2>&1 &
```

**What this does:**
- `> logs/agent0-run.log 2>&1` captures ALL console output (stdout + stderr)
- The `&` runs in background (optional) so you can continue monitoring
- Console output contains `[OK]` LED breadcrumbs
- JSON Lines log written to `logs/breadcrumbs.jsonl`

### Step 2: Monitor LED Activity in Real-Time

```bash
# Option A: Monitor console output (human-readable)
tail -f logs/agent0-run.log | grep --line-buffered -E "LED|\[OK\]|\[FAIL\]" &

# Option B: Monitor JSON Lines log (machine-readable)
tail -f logs/breadcrumbs.jsonl &

# Option C: Monitor specific LED range (e.g., Agent 0: 500-599)
tail -f logs/breadcrumbs.jsonl | grep --line-buffered -E '"id": (5[0-9]{2})' &
```

**This command:**
- `tail -f` follows the file as it grows (live monitoring)
- `grep --line-buffered` filters and outputs immediately
- `&` runs in background so you can continue working
- **Returns bash_id like:** `abc123`

### Step 3: Check LED Output (Claude Autonomous Debugging)

```bash
# Use BashOutput tool with the bash_id from Step 2
BashOutput bash_id="abc123"
```

---

## Autonomous LED Debugging Patterns

### Pattern 1: Check if Agent Completed Successfully

```bash
# Grep for specific agent range
grep -E '"id": (5[0-9]{2})' logs/breadcrumbs.jsonl | tail -20

# Expected: Should see LED 561 (Agent 0 completion marker)
# If missing: Agent crashed or didn't finish
```

### Pattern 2: Find All Failures

```bash
# JSON Lines approach (precise)
grep '"success": false' logs/breadcrumbs.jsonl

# Console approach (human-readable)
grep '\[FAIL\]' logs/agent0-run.log
```

**Example failure output:**
```json
{"id": 502, "name": "AGENT0_TOPIC_RESEARCH", "component": "Agent0_TopicResearch", "timestamp": 1761263805.123, "success": false, "error": "API rate limit exceeded", "stack": "Traceback...", "iso_timestamp": "2025-10-23T17:56:45.123456"}
```

### Pattern 3: Check Specific Operation Range

```bash
# Google Trends operations (LEDs 502-509)
grep -E '"id": (50[2-9])' logs/breadcrumbs.jsonl

# Reddit operations (LEDs 510-519)
grep -E '"id": (51[0-9])' logs/breadcrumbs.jsonl

# YouTube operations (LEDs 520-529)
grep -E '"id": (52[0-9])' logs/breadcrumbs.jsonl
```

### Pattern 4: Identify Missing LEDs (Execution Gaps)

```python
# Use Python to analyze
from lib.breadcrumb_system import BreadcrumbTrail

# Check Agent 0 range
result = BreadcrumbTrail.check_range(500, 599)
print(f"Missing LEDs: {result['missing']}")
print(f"Failed LEDs: {result['failed']}")

# Expected behavior: Agent doesn't use ALL 100 LEDs
# Only uses 15-20 strategic LEDs
# Missing LEDs in used ranges indicate incomplete execution
```

### Pattern 5: Quality Score Analysis

```python
# Get quality metrics
from lib.breadcrumb_system import BreadcrumbTrail

score = BreadcrumbTrail.get_quality_score()
print(f"Quality Score: {score}%")

# 100% = All LEDs succeeded
# 90-99% = Some non-critical failures
# <90% = Investigation required
```

---

## LED Range Reference for Purchase Intent System

### Agent-Specific Ranges (500-4599):
- **500-599**: Agent 0 - Topic Research Agent
  - 500-509: Initialization and input validation
  - 510-519: Google Trends operations
  - 520-529: Reddit PRAW operations
  - 530-539: YouTube API operations
  - 540-549: Data processing and scoring
  - 550-559: Dashboard generation
  - 560-569: Output and handoff

- **1500-1599**: Agent 1 - Product Researcher
  - 1500-1509: Initialization
  - 1510-1529: Product research operations
  - 1550-1559: Dashboard generation
  - 1560-1569: Output

- **2500-2599**: Agent 2 - Demographics Analyst
  - 2500-2509: Initialization
  - 2510-2529: Demographics analysis
  - 2530-2539: Confidence calculation
  - 2540-2549: Checkpoint validation (80% threshold)
  - 2560-2569: Output

- **3500-3599**: Agent 3 - Persona Generator
  - 3500-3509: Initialization
  - 3510-3529: Persona generation (400 personas)
  - 3550-3559: Validation and output

- **4500-4599**: Agent 4 - ParaThinker Intent Simulator
  - 4500-4509: Initialization
  - 4510-4529: Intent simulation (3,200 perspectives)
  - 4550-4559: Report generation
  - 4560-4569: Output

### General Application Ranges (5000-9099):
- **5000-5099**: Analytics and reporting
- **6000-6099**: API integration
- **7000-7099**: UI interactions
- **8000-8099**: Error handling and recovery
- **9000-9099**: Testing and validation

---

## LED Output Formats

### Console Output (Human-Readable)

**Success breadcrumb:**
```
[OK] LED 500: AGENT0_TOPIC_RESEARCH - {"action": "Agent 0 started"} Agent0_TopicResearch_500
```

**Failure breadcrumb:**
```
[FAIL] LED 502 FAILED [Agent0_TopicResearch]: AGENT0_TOPIC_RESEARCH API rate limit exceeded
```

### JSON Lines Log (Machine-Readable)

**Success:**
```json
{"id": 500, "name": "AGENT0_TOPIC_RESEARCH", "component": "Agent0_TopicResearch", "timestamp": 1761263801.577899, "success": true, "data": {"action": "Agent 0 started"}, "error": null, "stack": null, "iso_timestamp": "2025-10-23T17:56:41.577899"}
```

**Failure:**
```json
{"id": 502, "name": "AGENT0_TOPIC_RESEARCH", "component": "Agent0_TopicResearch", "timestamp": 1761263805.123, "success": false, "data": null, "error": "API rate limit exceeded", "stack": "Traceback (most recent call last):\n  File...", "iso_timestamp": "2025-10-23T17:56:45.123456"}
```

---

## Complete Windows LED Monitoring Workflow

### Workflow 1: Debug Single Agent Run

```bash
# 1. Navigate to project
cd "D:/Projects/Ai/Purchase-Intent"

# 2. Run agent with logging
python agents/agent_0/main.py > logs/agent0-run.log 2>&1 &
# bash_id: abc123

# 3. Monitor LED breadcrumbs in real-time
tail -f logs/breadcrumbs.jsonl &
# bash_id: def456

# 4. Check console output
BashOutput bash_id="abc123"

# 5. Check LED stream
BashOutput bash_id="def456"

# 6. After completion, analyze failures
grep '"success": false' logs/breadcrumbs.jsonl

# 7. Check quality score
python -c "from lib.breadcrumb_system import BreadcrumbTrail; print(f'Quality: {BreadcrumbTrail.get_quality_score()}%')"
```

### Workflow 2: Monitor Specific LED Range

```bash
# Debug Google Trends integration (LEDs 502-509)
tail -f logs/breadcrumbs.jsonl | grep --line-buffered -E '"id": (50[2-9])' &

# Debug checkpoints (LED 530)
tail -f logs/breadcrumbs.jsonl | grep --line-buffered '"id": 530' &
```

### Workflow 3: Compare Agent Runs

```bash
# Run 1 (baseline)
python agents/agent_0/main.py > logs/run1.log 2>&1
cp logs/breadcrumbs.jsonl logs/run1-breadcrumbs.jsonl

# Clear breadcrumbs
python -c "from lib.breadcrumb_system import BreadcrumbTrail; BreadcrumbTrail.clear()"

# Run 2 (after changes)
python agents/agent_0/main.py > logs/run2.log 2>&1
cp logs/breadcrumbs.jsonl logs/run2-breadcrumbs.jsonl

# Compare
diff logs/run1-breadcrumbs.jsonl logs/run2-breadcrumbs.jsonl
```

---

## Windows-Specific Process Checking

```bash
# Check if Python agent is running
tasklist | findstr /I "python.exe"

# Find specific Python process by PID
wmic process where "ProcessId=12345" get Caption,ProcessId,CommandLine

# Check network activity (if agents make API calls)
netstat -ano | findstr "ESTABLISHED"
```

---

## Common Debugging Scenarios

### Scenario 1: Agent Crashes Silently

**Symptoms:** No LED 561 (completion marker), process exits

**Debug:**
```bash
# Check last LED fired
tail -1 logs/breadcrumbs.jsonl

# Look for errors in console
tail -50 logs/agent0-run.log | grep -E "Error|Exception|Traceback"

# Check for failures
grep '"success": false' logs/breadcrumbs.jsonl | tail -1
```

**Example output:**
```json
{"id": 512, "success": false, "error": "ConnectionError: Reddit API unreachable"}
```
**Diagnosis:** Agent crashed at Reddit query (LED 512), implement graceful degradation

---

### Scenario 2: Agent Hangs/Infinite Loop

**Symptoms:** LEDs stop firing, process still running

**Debug:**
```bash
# Find last LED
tail -1 logs/breadcrumbs.jsonl
# Example: LED 520 (Starting YouTube query)

# Check if process still alive
tasklist | findstr /I "python.exe"

# Conclusion: Hung waiting for YouTube API response
```

**Solution:** Add timeout to API calls, implement LED 521 after API response

---

### Scenario 3: Checkpoint Failure

**Symptoms:** Agent stops at LED 530 (checkpoint)

**Debug:**
```bash
# Get checkpoint data
grep '"id": 530' logs/breadcrumbs.jsonl
```

**Example output:**
```json
{"id": 530, "name": "AGENT0_TOPIC_RESEARCH", "success": false, "error": "Checkpoint failed: Sufficient data collected", "data": {"trends": true, "reddit": 0, "youtube": 0}}
```

**Diagnosis:** Insufficient data (Reddit and YouTube returned 0 results), threshold not met

---

### Scenario 4: Performance Bottleneck

**Symptoms:** Agent takes too long

**Debug:**
```bash
# Analyze timestamps
python << 'EOF'
import json

with open('logs/breadcrumbs.jsonl') as f:
    leds = [json.loads(line) for line in f]

# Find time gaps
for i in range(1, len(leds)):
    delta = leds[i]['timestamp'] - leds[i-1]['timestamp']
    if delta > 5:  # >5 seconds
        print(f"Gap: LED {leds[i-1]['id']} -> {leds[i]['id']}: {delta:.2f}s")
EOF
```

**Example output:**
```
Gap: LED 520 -> LED 521: 12.45s
```
**Diagnosis:** YouTube API taking 12 seconds, add caching or reduce query scope

---

## ⚠️ Common Windows Mistakes to Avoid

❌ **DON'T USE:** `Get-Process` (PowerShell only)
✅ **USE:** `tasklist | findstr "python"`

❌ **DON'T USE:** `Test-Path` (PowerShell only)
✅ **USE:** `ls logs/breadcrumbs.jsonl`

❌ **DON'T USE:** `/mnt/d/Projects/` (WSL paths)
✅ **USE:** `D:/Projects/` or `"D:\\Projects\\"`

❌ **DON'T USE:** `ps aux | grep python` (Linux only)
✅ **USE:** `tasklist | findstr /I "python.exe"`

---

## 🪟 WINDOWS SYSTEM REMINDER

**This project runs on WINDOWS with PYTHON CLI agents. Always use:**
- Windows paths: `D:/Projects/` or `"D:\\Projects\\"`
- Git Bash commands: `tail`, `grep`, `cd`, `ls`
- Windows process tools: `tasklist`, `netstat`, `wmic`
- Python for LED analysis: `from lib.breadcrumb_system import BreadcrumbTrail`
- NEVER use PowerShell cmdlets in Bash tool
- NEVER use WSL/Linux paths like `/mnt/d/`

---

## Quick Reference: Essential Commands

```bash
# Run agent with logging
python agents/agent_0/main.py > logs/agent0-run.log 2>&1

# Monitor LEDs in real-time
tail -f logs/breadcrumbs.jsonl &

# Find failures
grep '"success": false' logs/breadcrumbs.jsonl

# Check quality score
python -c "from lib.breadcrumb_system import BreadcrumbTrail; print(f'Score: {BreadcrumbTrail.get_quality_score()}%')"

# Clear breadcrumbs (between runs)
python -c "from lib.breadcrumb_system import BreadcrumbTrail; BreadcrumbTrail.clear()"
```

---

**Document Purpose:** Enable Claude to autonomously debug Python Purchase Intent agents using LED breadcrumbs on Windows systems.

**Related Files:**
- `lib/breadcrumb_system.py` - Core LED library
- `lib/README.md` - LED library documentation
- `lib/breadcrumb_example.py` - Example usage
