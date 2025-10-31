# Agent 1 LED Map - Visual Reference

```
AGENT 1 LED RANGE: 1500-1599 (Product Researcher)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌─────────────────────────────────────────────────────────────────────────────┐
│ INITIALIZATION (1500-1509)                                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1500  🟢  Agent 1 started                                                   │
│ 1501  🟢  Multi-source search started                                       │
│ 1502  🟢  Multi-source search complete                                      │
│ 1503-1509  [Reserved for future use]                                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ AMAZON OPERATIONS (1510-1519)                          💰 QUOTA: ZERO       │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1510  🟢  Amazon scrape started                                             │
│ 1511  🟢  Amazon scrape complete                                            │
│ 1512-1519  [Reserved for future use]                                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ REDDIT OPERATIONS (1520-1529)                          💰 QUOTA: ~520 calls │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1520  🟢  Reddit search started                                             │
│ 1521  🟢  Reddit search complete                                            │
│ 1522-1529  [Reserved for future use]                                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ YOUTUBE OPERATIONS (1530-1539)                         💰 QUOTA: ~100 units │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1530  🟢  YouTube search started                         (optional)         │
│ 1531  🟢  YouTube search complete                        (--no-youtube)     │
│ 1532-1539  [Reserved for future use]                                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ GOODREADS OPERATIONS (1540-1549)                       💰 QUOTA: ZERO       │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1540  🟢  Goodreads scrape started                       (--enable-goodreads)│
│ 1541  🟢  Goodreads scrape complete                      (books only)       │
│ 1542-1549  [Reserved for future use]                                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ COMPARABLES RANKING (1550-1559)                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1550  🟢  Comparables ranking started                                       │
│ 1551  🟢  Comparables ranking complete                                      │
│        ├─ Sales signal (30%)                                                │
│        ├─ Review volume (30%)                                               │
│        ├─ Recency (20%)                                                     │
│        └─ Semantic similarity (20%)                                         │
│ 1552-1559  [Reserved for future use]                                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ SUBREDDIT OVERLAP ANALYSIS (1560-1569)                 ⏱️  60-90 seconds    │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1560  🟢  Overlap analysis started                                          │
│ 1561  🟢  Overlap analysis complete                                         │
│        └─ Discovers hidden audience segments                                │
│ 1562-1569  [Reserved for future use]                                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ CHECKPOINT WORKFLOW (1570-1579)                        👤 USER APPROVAL     │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1570  🟢  Checkpoint report generated                                       │
│ 1571  🟢  User approved checkpoint                      [A] Approve         │
│ 1572  🔴  User rejected checkpoint                      [R] Retry           │
│        └─ Aborts Agent 1, prompts re-run                                    │
│ 1573-1579  [Reserved for future use]                                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ OUTPUT OPERATIONS (1580-1589)                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1580  🟢  Checkpoint data saved                                             │
│        └─ outputs/{timestamp}-agent1-output.json                            │
│ 1581  🟢  Agent 1 complete                              🎉 READY FOR AGENT 2│
│ 1582-1589  [Reserved for future use]                                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ ERROR CODES (1590-1599)                                🔴 FAILURE TRACKING  │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1590  ❌  Reddit API error                              (rate limit, auth)  │
│ 1591  ❌  Subreddit overlap error                       (overlap analysis)  │
│ 1592  ❌  YouTube API error                             (quota, auth)       │
│ 1593  ❌  Amazon scraping error                         (timeout, anti-bot) │
│ 1594  ❌  Goodreads scraping error                      (timeout, anti-bot) │
│ 1595  ❌  Multi-source search error                     (all sources failed)│
│ 1596  ❌  Overlap analysis subsystem error              (general overlap)   │
│ 1597  ❌  Config validation error                       (missing API keys)  │
│ 1598  ❌  User abort/retry                              (user rejected)     │
│ 1599  ❌  General Agent 1 error                         (unhandled exception)│
└─────────────────────────────────────────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Typical LED Sequence (Successful Run)

```
🎵 LED 1500: Agent 1 started
🎵 LED 1501: Multi-source search started
    ├── 🎵 LED 1510: Amazon scrape started
    ├── 🎵 LED 1520: Reddit search started
    └── 🎵 LED 1530: YouTube search started (optional)
    ├── 🎵 LED 1511: Amazon scrape complete (15 products)
    ├── 🎵 LED 1521: Reddit search complete (20 discussions)
    └── 🎵 LED 1531: YouTube search complete (10 videos)
🎵 LED 1502: Multi-source search complete
🎵 LED 1550: Comparables ranking started
🎵 LED 1551: Comparables ranking complete (10 comparables)
🎵 LED 1560: Overlap analysis started
🎵 LED 1561: Overlap analysis complete (8 overlaps)
🎵 LED 1570: Checkpoint report generated
    [User reviews report...]
🎵 LED 1571: User approved checkpoint
🎵 LED 1580: Checkpoint data saved
🎵 LED 1581: Agent 1 complete ✅
```

**Total LEDs**: 12-14 (depending on optional sources)
**Total Time**: 85-130 seconds

---

## Error Scenario (Reddit Rate Limit)

```
🎵 LED 1500: Agent 1 started
🎵 LED 1501: Multi-source search started
    ├── 🎵 LED 1510: Amazon scrape started
    ├── 🎵 LED 1520: Reddit search started
    ├── ❌ LED 1590 FAILED: Reddit API error: 429 Rate Limit Exceeded
    └── 🎵 LED 1511: Amazon scrape complete (15 products)
❌ LED 1595 FAILED: Insufficient discussions (need Reddit or YouTube)
❌ LED 1599 FAILED: Agent 1 error: Cannot proceed without discussions
```

**Resolution**: Increase `Config.REDDIT_DELAY` or wait for rate limit reset

---

## Quick Reference

### LED Ranges by Operation Type

| Range | Type | Count | Optional? |
|-------|------|-------|-----------|
| 1500-1509 | Init | 3/10 | No |
| 1510-1519 | Amazon | 2/10 | No |
| 1520-1529 | Reddit | 2/10 | No |
| 1530-1539 | YouTube | 2/10 | Yes (--no-youtube) |
| 1540-1549 | Goodreads | 2/10 | Yes (--enable-goodreads) |
| 1550-1559 | Ranking | 2/10 | No |
| 1560-1569 | Overlap | 2/10 | No |
| 1570-1579 | Checkpoint | 3/10 | No |
| 1580-1589 | Output | 2/10 | No |
| 1590-1599 | Errors | 10/10 | As needed |

**Total Allocated**: 100 LEDs
**Total Used**: 22 LEDs
**Reserved**: 78 LEDs (for future features)

---

## Debug Commands

### Grep for Agent 1 LEDs
```bash
# All Agent 1 breadcrumbs
grep '"id": 15[0-9][0-9]' logs/breadcrumbs.jsonl | jq .

# Failures only
grep '"id": 15[0-9][0-9]' logs/breadcrumbs.jsonl | jq 'select(.success == false)'

# Specific range (e.g., Reddit operations)
grep '"id": 152[0-9]' logs/breadcrumbs.jsonl | jq .
```

### Python Breadcrumb API
```python
from lib.breadcrumb_system import BreadcrumbTrail

# Get all Agent 1 breadcrumbs
agent1_leds = BreadcrumbTrail.get_range(1500, 1599)

# Check for failures
failures = BreadcrumbTrail.get_failures()
agent1_failures = [f for f in failures if 1500 <= f.id < 1600]

# Quality score
score = BreadcrumbTrail.get_quality_score()
print(f"System quality: {score}%")
```

---

## Agent Handoff

### From Agent 0 → Agent 1
**No direct handoff** (Agent 1 is independent)

### From Agent 1 → Agent 2
**Handoff File**: `outputs/{timestamp}-agent1-output.json`

**Required LEDs before Agent 2 starts**:
- ✅ LED 1581: Agent 1 complete
- ✅ LED 1580: Checkpoint data saved
- ✅ LED 1571: User approved checkpoint

**Agent 2 reads**:
- `comparables[]`: 5-10 products for demographic scraping
- `discussion_urls[]`: Reddit/YouTube URLs for comment analysis
- `subreddit_overlaps[]`: Hidden audience segments
- `segment_insights`: Recommendations for targeting

**Next LED Range**: 2500-2599 (Agent 2 - Demographics Analysis)

---

## Performance Benchmarks

```
OPERATION                TIME        QUOTA        LEDs
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Amazon search           10-15s       ZERO         1510-1511
Reddit search            5-10s      ~20 calls     1520-1521
YouTube search           2-5s       ~100 units    1530-1531
Goodreads search         8-12s       ZERO         1540-1541
Comparables ranking      <1s         ZERO         1550-1551
Subreddit overlap       60-90s      ~500 calls    1560-1561
Checkpoint               N/A         ZERO         1570-1572
Output save              <1s         ZERO         1580-1581
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOTAL (all sources)    90-130s      ~620 calls   Full range
                                    + 100 YT units
TOTAL (no YouTube)     85-125s      ~520 calls   Skip 1530-1531
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Bottleneck**: Subreddit overlap analysis (60-90s)
**Optimization**: Sample 100 users instead of 500 → reduces to 30-45s

---

**Visual Map Version**: 1.0
**Last Updated**: 2025-10-31
**Status**: Production Ready ✅
