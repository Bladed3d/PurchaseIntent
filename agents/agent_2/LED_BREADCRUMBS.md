# Agent 2: Demographics Analyst - LED Breadcrumb Reference

## LED Range: 2500-2599

Complete reference for all LED breadcrumbs in Agent 2 Demographics Analyst.

---

## LED Map

### Initialization (2500-2509)

| LED | Name | Location | Description | Metadata |
|-----|------|----------|-------------|----------|
| 2500 | INIT_START | main.py:48 | Agent 2 started | `input_path`, `action: agent_2_started` |
| 2501 | CONFIG_VALIDATED | main.py:60 | Configuration validated | `action: config_validated` |

**Success Path:** 2500 → 2501

**Failure Cases:**
- Config validation error triggers fail at LED 2501

---

### Data Scraping (2510-2539)

| LED | Name | Location | Description | Metadata |
|-----|------|----------|-------------|----------|
| 2510 | LOADING_AGENT1 | scraper.py:47 | Loading data from Agent 1 output | `action: loading_agent1_data`, `path` |
| 2511 | AGENT1_LOADED | scraper.py:69 | Agent 1 data loaded successfully | `amazon_reviews`, `reddit_comments`, `youtube_comments`, `total_data_points` |
| 2512 | LOADING_TEST | scraper.py:113 | Loading test data file | `action: loading_test_data`, `path` |
| 2513 | TEST_LOADED | scraper.py:134 | Test data loaded successfully | `amazon_reviews`, `reddit_comments`, `youtube_comments`, `total_data_points` |

**Success Path:**
- Production: 2510 → 2511
- Testing: 2512 → 2513

**Failure Cases:**
- File not found: fail at 2510 or 2512
- Invalid JSON: fail at 2510 or 2512
- Missing required fields: fail at 2510 or 2512

---

### Demographics Extraction (2540-2559)

| LED | Name | Location | Description | Metadata |
|-----|------|----------|-------------|----------|
| 2540 | EXTRACTION_START | demographics_extractor.py:110 | Starting demographic extraction | `action: extracting_demographics`, `batch_size` |
| 2541 | EXTRACTION_COMPLETE | demographics_extractor.py:121 | Demographics extracted | `action: extraction_complete`, `profiles_extracted` |

**Success Path:** 2540 → 2541

**Failure Cases:**
- Empty review list: fail at 2540
- Missing required fields: fail at 2540
- No profiles extracted: fail at 2541

**Available LEDs for Enhancement:** 2542-2559

---

### Aggregation & Clustering (2560-2569)

| LED | Name | Location | Description | Metadata |
|-----|------|----------|-------------|----------|
| 2560 | AGGREGATION_START | aggregator.py:54 | Starting demographics aggregation | `action: aggregating_demographics`, `total_profiles` |
| 2561 | AGGREGATION_COMPLETE | aggregator.py:135 | Aggregation complete | `action: aggregation_complete`, `age_range`, `top_occupation` |
| 2562 | CLUSTERING_START | aggregator.py:162 | Starting profile clustering | `action: clustering_profiles`, `num_profiles`, `target_clusters` |
| 2563 | CLUSTERING_COMPLETE | aggregator.py:194 | Clustering complete | `action: clustering_complete`, `clusters_created`, `cluster_sizes` |

**Success Path:** 2560 → 2561 → 2562 → 2563

**Failure Cases:**
- Empty profile list: fail at 2560 or 2562
- No valid age data: fail at 2560
- No valid occupation data: fail at 2560
- Failed to create clusters: fail at 2563

---

### Confidence Validation (2570-2579)

| LED | Name | Location | Description | Metadata |
|-----|------|----------|-------------|----------|
| 2570 | CONFIDENCE_START | confidence_calculator.py:55 | Starting confidence calculation | `action: calculating_confidence`, `num_sources`, `sample_size` |
| 2571 | CONFIDENCE_CALCULATED | confidence_calculator.py:85 | Confidence score calculated | `confidence_score`, `source_agreement`, `sample_size_score`, `benchmark_match` |

**Success Path:** 2570 → 2571

**Failure Cases:**
- Empty source demographics: fail at 2570
- Less than 2 sources: fail at 2570

---

### Checkpoint Gate (2575-2579)

| LED | Name | Location | Description | Metadata |
|-----|------|----------|-------------|----------|
| 2575 | CHECKPOINT_EVAL | checkpoint.py:51 | Evaluating confidence checkpoint | `action: evaluating_checkpoint`, `confidence_score`, `threshold`, `meets_threshold` |
| 2576 | CHECKPOINT_PASSED | checkpoint.py:60 | Checkpoint passed (auto) | `action: checkpoint_passed`, `confidence_score` |
| 2577 | CHECKPOINT_FAILED | checkpoint.py:81 | Checkpoint failed (needs approval) | `action: checkpoint_failed`, `confidence_score`, `threshold` |
| 2578 | USER_APPROVED | checkpoint.py:114 | User approved continuation | `action: checkpoint_user_approved`, `confidence_score` |
| 2579 | USER_DECLINED | checkpoint.py:129 | User declined to continue | FAIL - includes low confidence reasons |

**Success Paths:**
- High confidence: 2575 → 2576
- Low confidence approved: 2575 → 2577 → 2578
- Low confidence declined: 2575 → 2577 → 2579 (FAIL)

---

### Agent Completion (2580-2589)

| LED | Name | Location | Description | Metadata |
|-----|------|----------|-------------|----------|
| 2580 | AGENT_COMPLETE | main.py:274 | Agent 2 completed successfully | `action: agent_2_complete`, `output_path`, `confidence_score` |

**Success Path:** 2580 is final LED

**Failure Cases:**
- Output write error: fail at 2580

---

### Error Codes (2590-2599)

Reserved range for critical errors and system failures.

Currently unused - available for future error categorization:
- 2590: Data source errors
- 2591: Extraction errors
- 2592: Aggregation errors
- 2593: Confidence calculation errors
- 2594: Checkpoint errors
- 2595-2599: Reserved

---

## Complete Agent 2 Workflow

### Happy Path (High Confidence)
```
2500 INIT_START
  → 2501 CONFIG_VALIDATED
  → 2510 LOADING_AGENT1
  → 2511 AGENT1_LOADED
  → 2540 EXTRACTION_START
  → 2541 EXTRACTION_COMPLETE
  → 2560 AGGREGATION_START
  → 2561 AGGREGATION_COMPLETE
  → 2562 CLUSTERING_START
  → 2563 CLUSTERING_COMPLETE
  → 2570 CONFIDENCE_START
  → 2571 CONFIDENCE_CALCULATED
  → 2575 CHECKPOINT_EVAL
  → 2576 CHECKPOINT_PASSED
  → 2580 AGENT_COMPLETE
```

### Low Confidence Path (User Approved)
```
2500 → 2501 → 2510 → 2511 → 2540 → 2541 → 2560 → 2561 → 2562 → 2563
  → 2570 CONFIDENCE_START
  → 2571 CONFIDENCE_CALCULATED (score < 0.80)
  → 2575 CHECKPOINT_EVAL
  → 2577 CHECKPOINT_FAILED (user prompt)
  → 2578 USER_APPROVED (user says "yes")
  → 2580 AGENT_COMPLETE
```

### Failure Path (User Declined)
```
2500 → 2501 → 2510 → 2511 → 2540 → 2541 → 2560 → 2561 → 2562 → 2563
  → 2570 CONFIDENCE_START
  → 2571 CONFIDENCE_CALCULATED (score < 0.80)
  → 2575 CHECKPOINT_EVAL
  → 2577 CHECKPOINT_FAILED (user prompt)
  → 2579 USER_DECLINED (FAIL - agent aborted)
```

---

## Debugging Commands

### Console Commands (via breadcrumb_system.py)

```python
from lib.breadcrumb_system import BreadcrumbTrail

# Get all Agent 2 breadcrumbs
BreadcrumbTrail.get_range(2500, 2599)

# Check for failures
BreadcrumbTrail.get_failures()

# Get specific component trail
BreadcrumbTrail.get_component("Agent2_DemographicsAnalyst")

# Check range completion
BreadcrumbTrail.check_range(2500, 2580)

# Get quality score
BreadcrumbTrail.get_quality_score()
```

### Log File Analysis

Breadcrumbs are written to: `logs/breadcrumbs.jsonl`

```bash
# View all Agent 2 LEDs
grep -E '"id":(25[0-9]{2})' logs/breadcrumbs.jsonl

# View failures only
grep '"success":false' logs/breadcrumbs.jsonl | grep -E '"id":(25[0-9]{2})'

# View specific LED
grep '"id":2541' logs/breadcrumbs.jsonl

# Count LEDs fired
grep -E '"id":(25[0-9]{2})' logs/breadcrumbs.jsonl | wc -l
```

---

## Confidence Formula

**Calculation:** `Confidence = (Source Agreement × 40%) + (Sample Size × 30%) + (Benchmark Match × 30%)`

**Components tracked via LED 2571:**
- `source_agreement`: Agreement across Amazon, Reddit, YouTube demographics
- `sample_size_score`: Based on MIN_DATA_POINTS_REQUIRED (300)
- `benchmark_match`: Match against Pew Research/Statista data (if available)

**Threshold:** 0.80 (80%) - defined in `config.py`

**LED 2575-2579** handle checkpoint logic based on this score.

---

## Integration with Other Agents

### Input Requirements:
- **From Agent 1:** Product research output JSON (comparables, reviews, discussions)
  - LEDs: 2510-2511 track this loading

### Output Format:
- **For Agent 3:** Demographics JSON with clusters and validation
  - LED 2580 confirms successful output generation
  - File: `agents/agent_2/outputs/{timestamp}-demographics.json`

### LED Range Coordination:
- **Agent 0:** 500-599 (Topic Research)
- **Agent 1:** 1500-1599 (Product Research)
- **Agent 2:** 2500-2599 (Demographics Analysis) ← YOU ARE HERE
- **Agent 3:** 3500-3599 (Persona Generation)
- **Agent 4:** 4500-4599 (Intent Simulation)

**No conflicts** - Agent 2 LEDs are isolated to 2500-2599 range.

---

## Performance Monitoring

### Key Performance Indicators (tracked via LEDs):

**LED 2511 Metadata:**
- `total_data_points`: Should be >= 300 for high confidence
- Sample size directly impacts confidence score

**LED 2541 Metadata:**
- `profiles_extracted`: Should match or be close to input data points
- Low extraction rate indicates pattern matching issues

**LED 2563 Metadata:**
- `cluster_sizes`: Should be reasonably balanced (not all in one cluster)
- Indicates demographic diversity in customer base

**LED 2571 Metadata:**
- `confidence_score`: Core quality metric
- `source_agreement`: Should be >= 0.70 for reliable data
- `sample_size_score`: Indicates data volume adequacy
- `benchmark_match`: Indicates real-world alignment

### Quality Gates:

1. **Data Volume Gate** (LED 2511):
   - Warning if < 300 data points
   - Impacts sample_size_score in confidence calculation

2. **Extraction Gate** (LED 2541):
   - Fails if 0 profiles extracted
   - Indicates data quality or pattern matching issues

3. **Triangulation Gate** (LED 2570):
   - Requires >= 2 sources for confidence calculation
   - Fails if only 1 source available

4. **Confidence Gate** (LED 2575-2579):
   - Auto-pass if >= 80% confidence
   - User decision required if < 80%

---

## Testing Support

### Auto-Approve Mode:
```bash
python agents/agent_2/main.py --test-data tests/fixtures/agent2_test_data.json --auto-approve
```

This bypasses checkpoint gate for testing with low-confidence data.

**LEDs affected:**
- 2575: Still evaluates checkpoint
- 2576: Skipped (auto-approve mode)
- 2577: Logged as FAILED but not blocking
- 2578: Skipped
- 2579: Skipped

**LED 2580** still fires with success status.

---

## Summary

**Total LED Coverage:** 18 active breadcrumbs + error range (2590-2599)

**Autonomous Debugging Enabled:** Yes - full trail visibility via JSON Lines logs

**Integration Status:** Complete - works with lib/breadcrumb_system.py

**Quality Score Tracking:** Yes - via BreadcrumbTrail.get_quality_score()

**Next Agent:** Agent 3 (LED range 3500-3599) will consume Agent 2 output

---

**Last Updated:** 2025-10-31
**Agent Version:** Agent 2 v1.0
**LED System Version:** Purchase Intent Breadcrumb System v1.0
