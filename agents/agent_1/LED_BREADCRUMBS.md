# Agent 1 LED Breadcrumb Reference Map

**LED Range**: 1500-1599 (100 LEDs allocated)
**Component**: Agent 1 - Product Researcher
**Purpose**: Multi-source product search, comparables ranking, subreddit overlap analysis

---

## LED Allocation Overview

| Range | Category | Description |
|-------|----------|-------------|
| 1500-1509 | Initialization | Agent startup and multi-source orchestration |
| 1510-1519 | Amazon | Amazon product scraping |
| 1520-1529 | Reddit | Reddit discussion search and overlap |
| 1530-1539 | YouTube | YouTube video discovery |
| 1540-1549 | Goodreads | Goodreads book search |
| 1550-1559 | Comparables | Product ranking and filtering |
| 1560-1569 | Overlap | Subreddit overlap analysis |
| 1570-1579 | Checkpoint | User approval workflow |
| 1580-1589 | Output | Data saving and handoff |
| 1590-1599 | Errors | Error codes by subsystem |

---

## Detailed LED Breakdown

### Initialization (1500-1509)

| LED | Name | Location | Data |
|-----|------|----------|------|
| 1500 | `LED_INIT` | `main.py:26` | `{"action": "agent_1_started", "product": description}` |
| 1501 | Multi-source search start | `search.py:60` | `{"action": "multi_source_search_started", "queries": {...}}` |
| 1502 | Multi-source search complete | `search.py:140` | `{"action": "multi_source_search_complete", "products_found": N, "discussions_found": M}` |

### Amazon Operations (1510-1519)

| LED | Name | Location | Data |
|-----|------|----------|------|
| 1510 | `LED_AMAZON_START` | `playwright_scraper.py:44` | `{"action": "amazon_scrape_started", "query": query}` |
| 1511 | Amazon scrape complete | `playwright_scraper.py:93` | `{"action": "amazon_scrape_complete", "products_found": N}` |

**Quota Cost**: ZERO (web scraping, no API)
**Rate Limit**: Use anti-bot delays (human-like behavior)

### Reddit Operations (1520-1529)

| LED | Name | Location | Data |
|-----|------|----------|------|
| 1520 | `LED_REDDIT_START` | `api_clients.py:63` | `{"action": "reddit_search_started", "query": query, "subreddits": [...]}` |
| 1521 | Reddit search complete | `api_clients.py:111` | `{"action": "reddit_search_complete", "discussions_found": N}` |

**Quota Cost**: ~3,600 calls/hour (PRAW free tier - effectively unlimited)
**Rate Limit**: 2.0 second delay between calls (`Config.REDDIT_DELAY`)

### YouTube Operations (1530-1539)

| LED | Name | Location | Data |
|-----|------|----------|------|
| 1530 | `LED_YOUTUBE_START` | `api_clients.py:287` | `{"action": "youtube_search_started", "query": query}` |
| 1531 | YouTube search complete | `api_clients.py:344` | `{"action": "youtube_search_complete", "videos_found": N}` |

**Quota Cost**: ~100 units per search (10,000 daily limit = 100 searches/day)
**Rate Limit**: Optional - can disable with `--no-youtube` flag to save quota

### Goodreads Operations (1540-1549)

| LED | Name | Location | Data |
|-----|------|----------|------|
| 1540 | `LED_GOODREADS_START` | `playwright_scraper.py:190` | `{"action": "goodreads_scrape_started", "query": query}` |
| 1541 | Goodreads scrape complete | `playwright_scraper.py:229` | `{"action": "goodreads_scrape_complete", "books_found": N}` |

**Quota Cost**: ZERO (web scraping, no API)
**Rate Limit**: Anti-bot delays (human-like behavior)
**Category**: Books only (enabled with `--enable-goodreads`)

### Comparables Ranking (1550-1559)

| LED | Name | Location | Data |
|-----|------|----------|------|
| 1550 | `LED_COMPARABLES_START` | `comparables.py:44` | `{"action": "comparables_ranking_started", "amazon_products": N, "goodreads_books": M}` |
| 1551 | Comparables ranking complete | `comparables.py:91` | `{"action": "comparables_ranking_complete", "comparables_selected": N, "avg_score": X.XX}` |

**Algorithm**:
- Sales signal (30%): BSR, views, review counts
- Review volume (30%): More data = better demographics
- Recency (20%): Recent products preferred
- Semantic similarity (20%): Jaccard similarity to user query

### Subreddit Overlap Analysis (1560-1569)

| LED | Name | Location | Data |
|-----|------|----------|------|
| 1560 | `LED_OVERLAP_START` | `api_clients.py:140` | `{"action": "overlap_analysis_started", "base_subreddit": r/XXX}` |
| 1561 | Overlap analysis complete | `api_clients.py:222` | `{"action": "overlap_analysis_complete", "overlaps_found": N}` |

**Purpose**: Discover hidden audience segments via user behavior overlap
**Data Source**: Reddit user activity across subreddits
**Output**: Subreddits with multiplier scores (2.0+ = significant overlap)

### Checkpoint Workflow (1570-1579)

| LED | Name | Location | Data |
|-----|------|----------|------|
| 1570 | `LED_CHECKPOINT_START` | `checkpoint.py:43` | `{"action": "checkpoint_report_generated", "comparables_count": N}` |
| 1571 | User approved | `checkpoint.py:215` | `{"action": "user_approved_checkpoint"}` |
| 1572 | User rejected | `checkpoint.py:226` | `{"action": "user_rejected_checkpoint"}` |

**User Actions**:
- [A] Approve → LED 1571 → Proceed to Agent 2
- [M] Modify → Manual edit request (not implemented)
- [R] Retry → LED 1572 → Abort Agent 1, run again

### Output Operations (1580-1589)

| LED | Name | Location | Data |
|-----|------|----------|------|
| 1580 | `LED_OUTPUT_START` | `checkpoint.py:285` | `{"action": "checkpoint_data_saved", "file": path}` |
| 1581 | Agent 1 complete | `main.py:94` | `{"action": "agent_1_complete", "output": path}` |

**Output Format**: JSON file `outputs/{timestamp}-agent1-output.json`
**Contents**:
- Comparable products (5-10)
- Discussion URLs (Reddit, YouTube)
- Subreddit overlaps with multipliers
- Segment insights and recommendations
- Data quality metrics

### Error Codes (1590-1599)

| LED | Error Type | Location | Trigger |
|-----|------------|----------|---------|
| 1590 | `LED_ERROR_START` | `api_clients.py:119` | Reddit API error |
| 1591 | Overlap error | `api_clients.py:230` | Subreddit overlap analysis failed |
| 1592 | YouTube error | `api_clients.py:352,362` | YouTube API error or quota exceeded |
| 1593 | Amazon error | `playwright_scraper.py:102,110` | Amazon scraping timeout or failure |
| 1594 | Goodreads error | `playwright_scraper.py:238,246` | Goodreads scraping timeout or failure |
| 1595 | Multi-source error | `search.py:116` | All sources failed |
| 1596 | Overlap analysis error | `subreddit_overlap.py:90` | Overlap analysis failed |
| 1597 | Config validation error | `main.py:31` | Missing API credentials |
| 1598 | User abort | `main.py:83` | User rejected checkpoint |
| 1599 | General error | `main.py:101` | Unhandled Agent 1 exception |

---

## Usage Examples

### Standard Run (All Sources)
```bash
python agents/agent_1/main.py "productivity books for entrepreneurs"
```
**LEDs fired**: 1500 → 1501 → 1510/1520/1530 → 1511/1521/1531 → 1550 → 1551 → 1560 → 1561 → 1570 → 1571 → 1580 → 1581

### Quota-Conscious Run (No YouTube)
```bash
python agents/agent_1/main.py "productivity books" --no-youtube
```
**LEDs fired**: 1500 → 1501 → 1510/1520 → 1511/1521 → 1550 → 1551 → 1560 → 1561 → 1570 → 1571 → 1580 → 1581
**YouTube LEDs skipped**: 1530-1531 (saves 100 quota units)

### Book-Specific Run (Goodreads Enabled)
```bash
python agents/agent_1/main.py "productivity books" --category book --enable-goodreads
```
**LEDs fired**: 1500 → 1501 → 1510/1520/1540 → 1511/1521/1541 → 1550 → 1551 → 1560 → 1561 → 1570 → 1571 → 1580 → 1581

### Error Scenario (Missing Reddit Credentials)
```bash
# Missing REDDIT_CLIENT_ID in .env
python agents/agent_1/main.py "test product"
```
**LEDs fired**: 1500 → 1597 (LED_ERROR_START + 7)
**Output**: `[FAIL] LED 1597 FAILED [Agent1_ProductResearch]: Missing required environment variables: REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET`

---

## Debug Commands

### View All Agent 1 LEDs
```bash
# Grep breadcrumb log for Agent 1 range
grep '"id": 15[0-9][0-9]' logs/breadcrumbs.jsonl | jq .

# Filter for failures only
grep '"id": 15[0-9][0-9]' logs/breadcrumbs.jsonl | jq 'select(.success == false)'
```

### Check LED Coverage
```python
from lib.breadcrumb_system import BreadcrumbTrail

# After running Agent 1
result = BreadcrumbTrail.check_range(1500, 1599)
print(f"Passed: {result['passed']}")
print(f"Missing LEDs: {result['missing']}")
print(f"Failed LEDs: {result['failed']}")
```

### Get Quality Score
```python
from lib.breadcrumb_system import BreadcrumbTrail

# Overall system quality
score = BreadcrumbTrail.get_quality_score()
print(f"System quality: {score}%")

# Agent 1 specific failures
failures = BreadcrumbTrail.get_range(1500, 1599)
failures = [b for b in failures if not b.success]
print(f"Agent 1 failures: {len(failures)}")
```

---

## Integration with Agent 2

**Handoff File**: `outputs/{timestamp}-agent1-output.json`

**Expected LEDs before Agent 2 starts**:
- ✅ LED 1581: Agent 1 complete
- ✅ LED 1580: Checkpoint data saved
- ✅ LED 1571: User approved checkpoint

**Agent 2 will read**:
- `comparables[]`: Product list for demographic scraping
- `discussion_urls[]`: Reddit/YouTube URLs for comment analysis
- `subreddit_overlaps[]`: Hidden audience segments to target
- `segment_insights`: Recommendations for persona targeting

**Agent 2 LED Range**: 2500-2599 (Demographics Analysis)

---

## Performance Benchmarks

| Operation | Avg Time | Quota Cost | LEDs |
|-----------|----------|------------|------|
| Amazon search (15 products) | 10-15s | ZERO | 1510-1511 |
| Reddit search (20 discussions) | 5-10s | 20 calls | 1520-1521 |
| YouTube search (10 videos) | 2-5s | ~100 units | 1530-1531 |
| Goodreads search (10 books) | 8-12s | ZERO | 1540-1541 |
| Comparables ranking | <1s | ZERO | 1550-1551 |
| Subreddit overlap (500 users) | 60-90s | 500 calls | 1560-1561 |
| **Total (all sources)** | **90-130s** | ~620 calls + 100 YT units | Full range |
| **Total (no YouTube)** | **85-125s** | ~520 calls | Skip 1530-1531 |

**Bottleneck**: Subreddit overlap analysis (60-90s)
**Optimization**: Sample 100 users instead of 500 (reduces to 30-45s)

---

## Autonomous Debugging Examples

### Example 1: Reddit API Rate Limit
**Symptom**: Agent 1 hangs during Reddit search
**Debug Trail**:
```
LED 1520: reddit_search_started
LED 1590 FAILED: Reddit API error: 429 Rate Limit Exceeded
```
**Resolution**: Increase `Config.REDDIT_DELAY` from 2.0s to 3.0s

### Example 2: Amazon Anti-Bot Detection
**Symptom**: Amazon search returns 0 products
**Debug Trail**:
```
LED 1510: amazon_scrape_started
LED 1593 FAILED: Amazon scraping failed: anti-bot detection
```
**Resolution**: Use rotating user agents or add random delays

### Example 3: Insufficient Data Quality
**Symptom**: Agent 1 completes but Agent 2 has insufficient data
**Debug Trail**:
```
LED 1551: comparables_ranking_complete (comparables_selected: 3)
LED 1570: checkpoint_report_generated
LED 1599 FAILED: Insufficient comparables found (need >=5, got 3)
```
**Resolution**: Broaden search query or lower `Config.MIN_REVIEWS_AMAZON`

---

## Version History

- **v1.0** (2025-10-31): Initial implementation with full LED coverage
- LED range 1500-1599 fully allocated
- Error codes comprehensive (10 types)
- Integration with breadcrumb_system.py complete

---

**Next Agent**: Agent 2 (Demographics Analysis) - LED Range 2500-2599
**Previous Agent**: Agent 0 (Topic Research) - LED Range 500-599
