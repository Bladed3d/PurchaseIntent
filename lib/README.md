# Purchase Intent System - LED Breadcrumb Library

Python implementation of the LED breadcrumb debugging system for autonomous error detection and monitoring.

## Overview

The LED (Light-Emitting Diagnostic) breadcrumb system provides:

- **Autonomous debugging** - Claude can grep logs to find exact failure points
- **Structured logging** - JSON Lines format for easy parsing
- **Quality metrics** - Automatic calculation of success/failure rates
- **Verification support** - Built-in assertion and checkpoint mechanisms
- **Range-based organization** - Each agent has dedicated LED ranges (500-4599)

## Quick Start

```python
from lib.breadcrumb_system import BreadcrumbTrail

# Initialize trail for your agent/component
trail = BreadcrumbTrail("Agent0_TopicResearch")

# Light successful operations
trail.light(500, {"action": "Started", "mode": "research"})
trail.light(501, {"topics_found": 15})

# Record failures
try:
    risky_operation()
    trail.light(502, {"status": "complete"})
except Exception as e:
    trail.fail(502, e)  # Captures error message and stack trace

# Create checkpoints
def validation():
    return data_quality > 0.8

if not trail.checkpoint(503, "Data Quality Gate", validation):
    print("Checkpoint failed - cannot proceed")
```

## LED Range Allocation

**Purchase Intent System (500-4599):**
- **500-599**: Agent 0 - Topic Research
- **1500-1599**: Agent 1 - Product Research
- **2500-2599**: Agent 2 - Demographics Analysis
- **3500-3599**: Agent 3 - Persona Generation
- **4500-4599**: Agent 4 - ParaThinker Intent Simulation

**General Application (5000-9099):**
- **5000-5099**: Analytics and reporting
- **6000-6099**: API integration
- **7000-7099**: UI interactions
- **8000-8099**: Error handling
- **9000-9099**: Testing and validation

## Core Features

### 1. Basic LED Lighting

```python
trail = BreadcrumbTrail("MyComponent")

# Simple success
trail.light(500, {"message": "Operation started"})

# With structured data
trail.light(501, {
    "api": "Google Trends",
    "query": "romance novels",
    "results": 42
})
```

### 2. Failure Tracking

```python
try:
    response = api_call()
    trail.light(502, {"response_code": 200})
except Exception as e:
    # Automatically captures error message and stack trace
    trail.fail(502, e)
```

### 3. Verification

```python
from lib.breadcrumb_system import VerificationResult

# Verify expected vs actual values
verification = VerificationResult(
    expect=True,
    actual=len(results) > 0
)

success = trail.light_with_verification(503, results, verification)
if not success:
    print("Verification failed - no results returned")
```

### 4. Checkpoints

```python
# Create validation gates
def has_minimum_data():
    return reddit_posts > 5 and youtube_videos > 3

passed = trail.checkpoint(
    510,
    "Minimum Data Threshold",
    has_minimum_data,
    {"reddit": reddit_posts, "youtube": youtube_videos}
)

if not passed:
    return  # Stop execution
```

## Autonomous Debugging

### For Claude to Debug Issues

```python
# Get all breadcrumbs in a range
agent0_leds = BreadcrumbTrail.get_range(500, 599)

# Check if a range completed successfully
result = BreadcrumbTrail.check_range(500, 599)
print(f"Missing LEDs: {result['missing']}")
print(f"Failed LEDs: {result['failed']}")

# Get all failures
failures = BreadcrumbTrail.get_failures()
for f in failures:
    print(f"LED {f.id}: {f.error}")

# Quality score
score = BreadcrumbTrail.get_quality_score()
print(f"System quality: {score}%")
```

### Grep JSON Lines Logs

```bash
# Find all Agent 0 operations
grep "Agent0_TopicResearch" logs/breadcrumbs.jsonl

# Find failures
grep '"success": false' logs/breadcrumbs.jsonl

# Find specific LED range
grep -E '"id": (5[0-9]{2})' logs/breadcrumbs.jsonl

# Find operations with errors
grep '"error":' logs/breadcrumbs.jsonl | grep -v '"error": null'
```

## Output Formats

### Console Output

```
[OK] LED 500: AGENT0_TOPIC_RESEARCH - {"action": "Started"} Agent0_TopicResearch_500
[OK] LED 501: AGENT0_TOPIC_RESEARCH - {"topics": 15} Agent0_TopicResearch_501
[FAIL] LED 502 FAILED [Agent0_TopicResearch]: AGENT0_TOPIC_RESEARCH API rate limit exceeded
```

### JSON Lines Log (`logs/breadcrumbs.jsonl`)

```json
{"id": 500, "name": "AGENT0_TOPIC_RESEARCH", "component": "Agent0_TopicResearch", "timestamp": 1761263801.577899, "success": true, "data": {"action": "Started"}, "error": null, "stack": null, "iso_timestamp": "2025-10-23T17:56:41.577899"}
{"id": 502, "name": "AGENT0_TOPIC_RESEARCH", "component": "Agent0_TopicResearch", "timestamp": 1761263805.123456, "success": false, "data": null, "error": "API rate limit exceeded", "stack": "Traceback...", "iso_timestamp": "2025-10-23T17:56:45.123456"}
```

## Verification Summary

```python
summary = trail.get_verification_summary()

print(f"Total LEDs: {summary['total_leds']}")
print(f"Failures: {summary['failures']}")
print(f"Failure Rate: {summary['failure_rate']:.2%}")
print(f"Verification Passed: {summary['verification_passed']}")
```

Output:
```
Total LEDs: 15
Failures: 0
Failure Rate: 0.00%
Verification Passed: True
```

## Best Practices

### 1. LED Numbering Strategy

Use logical groupings within your agent's range:

```python
# Agent 0 (500-599)
500-509: Initialization and input validation
510-519: Google Trends operations
520-529: Reddit PRAW operations
530-539: YouTube API operations
540-549: Data processing and scoring
550-559: Dashboard generation
560-569: Output and handoff
```

### 2. Structured Data

Always use dictionaries for data:

```python
# Good
trail.light(500, {"action": "query", "source": "reddit", "count": 42})

# Avoid
trail.light(500, "query reddit 42")  # Hard to parse
```

### 3. Meaningful Error Context

```python
try:
    data = fetch_trends(topic)
    trail.light(502, {"topic": topic, "data_points": len(data)})
except RateLimitError as e:
    trail.fail(502, Exception(f"Rate limit for topic '{topic}': {e}"))
```

### 4. Checkpoint Critical Operations

```python
# Before proceeding to expensive operations
if not trail.checkpoint(530, "Sufficient Data", has_data):
    # Exit early rather than waste compute
    return None
```

## Example: Complete Agent Workflow

See `lib/breadcrumb_example.py` for a full Agent 0 implementation example.

```bash
python lib/breadcrumb_example.py
```

## Files

- `breadcrumb_system.py` - Core library (240 lines)
- `breadcrumb_example.py` - Complete Agent 0 example
- `README.md` - This documentation
- `../logs/breadcrumbs.jsonl` - JSON Lines log output

## Integration with Agents

Each agent should:

1. Initialize trail in `__init__` or `main()`
2. Light LEDs at every major operation
3. Use checkpoints for quality gates (e.g., Agent 2's 80% confidence threshold)
4. Log failures with full error context
5. Generate verification summary at completion

This enables Claude to autonomously debug issues by grepping logs and analyzing LED sequences.

## Windows Compatibility

The library handles Windows console encoding automatically:
- Attempts to output emojis (🎵 for success, ❌ for failure)
- Falls back to `[OK]` and `[FAIL]` if emojis not supported
- All data logged to JSON Lines regardless of console encoding
