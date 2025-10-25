# Topic Research Methodology: "Cooking Recipes" Example

## Overview
This document explains the complete research methodology used by Agent 0 (Topic Research Agent) to analyze topics and generate the data displayed in dashboard tooltips.

**Example Topic:** "cooking recipes"

---

## Data Collection Process

### Phase 1: Google Trends Analysis
**API:** pytrends (unofficial Google Trends API)
**Query:** Single keyword query for "cooking recipes"
**Timeframe:** Last 12 months (today-12m)
**Rate Limiting:** 12-second delay between requests, exponential backoff on errors
**Caching:** 24-hour local cache to avoid redundant queries

**Data Collected:**
- Interest over time (weekly data points for 12 months = ~53 data points)
- Average interest score (0-100, absolute not relative)
- Peak interest score (highest point in 12 months)
- Trend direction (rising/falling/stable based on first-half vs second-half comparison)

**Example Output:**
```json
{
  "average_interest": 11.11,
  "peak_interest": 100.0,
  "trend_direction": "rising",
  "data_points": 53
}
```

---

### Phase 2: Reddit Analysis
**API:** PRAW (Python Reddit API Wrapper)
**Configuration:**
- `MAX_REDDIT_POSTS = 50` (configurable limit)
- Sort order: "relevance" (not "new" or "hot")
- Time filter: all time

**Query Process:**
1. Search Reddit for keyword "cooking recipes"
2. Retrieve up to 50 posts
3. Extract engagement metrics (upvotes/score)
4. Extract timestamps (`created_utc`)
5. Identify top subreddits

**Data Collected:**
- Total posts: 50 (sample size)
- Total engagement: Sum of all post scores
- Average engagement: Total engagement ÷ post count
- Top subreddits: Most common subreddits (top 5)
- **Timestamps:** Unix timestamps for each post (NEW - added for recency)

**Example Output:**
```json
{
  "total_posts": 50,
  "total_engagement": 473096,
  "avg_engagement": 9461.92,
  "top_subreddits": [
    {"name": "Cooking", "count": 16},
    {"name": "IAmA", "count": 2}
  ],
  "timestamps": [1754610234.0, 1737071033.0, ...]
}
```

**LIMITATION:** Only samples 50 posts out of potentially millions. Not sorted by recency - uses Reddit's "relevance" algorithm which may return older popular posts.

---

### Phase 3: YouTube Analysis
**API:** YouTube Data API v3
**Configuration:**
- `MAX_YOUTUBE_VIDEOS = 20` (configurable limit)
- Search type: video
- Order: relevance (not viewCount or date)

**Query Process:**
1. Search YouTube for "cooking recipes"
2. Retrieve up to 20 video IDs
3. Batch fetch video statistics
4. Extract view counts and timestamps

**Data Collected:**
- Total videos: 20 (sample size)
- Total views: Sum of all video views
- Average views: Total views ÷ video count
- Top channels: Most common channels (top 5)
- **Timestamps:** Published dates converted to Unix timestamps (NEW)

**Example Output:**
```json
{
  "total_videos": 20,
  "total_views": 172500569,
  "avg_views": 8625028.45,
  "top_channels": [
    {"name": "Louis Gantus", "count": 4},
    {"name": "Fitwaffle Kitchen", "count": 2}
  ],
  "timestamps": [1704214808.0, 1699559954.0, ...]
}
```

**LIMITATION:** Only samples 20 videos out of potentially millions. Sorted by "relevance" not "upload date", so may miss very recent content.

---

## Scoring & Analysis

### Demand Score Calculation
**Formula:** Weighted composite of 3 sources
```
demand_score = (trends_score × 0.35) + (reddit_score × 0.35) + (youtube_score × 0.30)
```

**Component Scoring:**
- **Trends Score:** Normalized average interest (0-100)
- **Reddit Score:** Engagement-based percentile (0-100)
- **YouTube Score:** View-based percentile (0-100)

**"Cooking Recipes" Example:**
```
Demand Score: 70.13/100
- Trends: 11.11 average interest
- Reddit: 50 posts, 9462 avg engagement
- YouTube: 20 videos, 8.6M avg views
```

---

### Competition Analysis
**Method:** Analyze saturation in each data source

**Metrics:**
- **Trends Competition:** Based on peak interest (higher = more competition)
- **Reddit Competition:** Based on post volume and engagement (higher = saturated)
- **YouTube Competition:** Based on video count and views (higher = crowded)

**Competition Levels:**
- 0-33: Low (🟢)
- 34-66: Moderate (🟡)
- 67-100: High (🔴)

**"Cooking Recipes" Example:**
```
Overall Competition: 31.67/100 (MODERATE)
- Trends: 20 (LOW - based on interest consistency)
- Reddit: 45 (MODERATE - 16 posts in r/Cooking indicates saturation)
- YouTube: 30 (MODERATE - high view counts but not oversaturated)
```

---

### Opportunity Score
**Formula:**
```
opportunity_score = demand_score - (competition_score × competition_penalty)
```

Where competition penalty varies by level:
- Low competition: 0.3x penalty
- Moderate competition: 0.5x penalty
- High competition: 0.7x penalty

**"Cooking Recipes" Example:**
```
Opportunity Score: 47.92/100 (VIABLE)
= 70.13 - (31.67 × 0.5)
= VIABLE recommendation (good opportunity with effort)
```

---

### Data Richness Scoring
**Purpose:** Measure confidence in scoring based on data availability

**Components:**
1. **Trends richness:** Data points + average interest
2. **Reddit richness:** Post volume + engagement quality
3. **YouTube richness:** Video count + view quality

**Scoring Bands:**
- 90-100: ⭐⭐⭐⭐⭐ (5 stars - Excellent)
- 70-89: ⭐⭐⭐⭐ (4 stars - Good)
- 50-69: ⭐⭐⭐ (3 stars - Moderate)
- 30-49: ⭐⭐ (2 stars - Low)
- 0-29: ⭐ (1 star - Very Low)

**"Cooking Recipes" Example:**
```
Richness Score: 4/5 stars (GOOD)
├─ Trends: 53 pts : 11.1 interest
├─ Reddit: 50 posts : 9462 engage
└─ YouTube: 20 videos : 8,625,028.45 views
```

---

### Recency/Urgency Scoring (NEW)
**Purpose:** Measure how "hot" or "trending" a topic is based on content freshness

**Formula:**
```
recency_score = (recent_activity × 0.60) + (trend_momentum × 0.30) + (freshness × 0.10)
```

**Components:**

1. **Recent Activity (60%):** Percentage of sampled content in last 90 days
   ```
   recent_90_count = count(posts/videos where age ≤ 90 days)
   recent_activity_pct = (recent_90_count / total_sampled) × 100
   recent_activity_score = min(recent_activity_pct, 100) × 0.60
   ```

2. **Trend Momentum (30%):** From Google Trends direction
   - Rising: 100 × 0.30 = 30 points
   - Stable: 60 × 0.30 = 18 points
   - Falling: 30 × 0.30 = 9 points

3. **Content Freshness (10%):** Inverse of average age
   ```
   avg_age_days = sum(age_of_each_item) / total_items
   freshness_score = max(0, (1 - (avg_age_days / 365)) × 100) × 0.10
   ```

**"Cooking Recipes" Example:**
```
Recency Score: 39.4/100
Recent Activity: 15.7% in 90d (11/70 items)
  - Recent 30 days: 5 items (Reddit + YouTube combined)
  - Recent 90 days: 11 items total
  - Total sampled: 70 items (50 Reddit + 20 YouTube)
Trend: rising (from Google Trends)
Avg Age: 938 days (~2.6 years)

Calculation:
= (15.7 × 0.60) + (100 × 0.30) + ((1 - (938/365)) × 100 × 0.10)
= 9.42 + 30 + 0
= 39.4/100
```

**CRITICAL LIMITATION:**
The "5 items in last 30 days" statistic is based on a **sample of 70 items** (50 Reddit + 20 YouTube), NOT the total universe of content about "cooking recipes".

**Reality Check:**
- Actual "cooking recipes" posts per day: Thousands on Reddit, tens of thousands on YouTube
- Our sample: 70 total items, sorted by "relevance" not "recency"
- **The recency score measures freshness of our SAMPLE, not the entire topic**

**Why This Matters:**
For broad topics like "cooking recipes", the recency score may be artificially LOW because:
1. Reddit/YouTube return "most relevant" posts (often older, highly-engaged content)
2. We only sample 70 items total
3. Popular evergreen content dominates the sample

For niche topics like "sci-fi romance novels set in Victorian era", recency is more accurate because:
1. Smaller content universe
2. Sample represents larger % of total content
3. Relevance sorting still captures recent posts

---

## Tooltip Data Assembly

### Information Hierarchy

**Primary Metrics:**
- Topic name
- Demand score (0-100)
- Competition score (0-100)
- Opportunity score (0-100)
- Audience size (estimated market size)

**Data Quality Metrics:**
- Data Richness (1-5 stars)
- Breakdown by source (Trends, Reddit, YouTube)

**Timing Metrics (NEW):**
- Recency/Urgency score (0-100)
- Recent activity percentage (90-day window)
- Items in last 30 days
- Trend direction
- Average content age

**Strategic Classification:**
- Zone (GOLD MINE / VIABLE / RISKY NICHE / AVOID)

---

## Tooltip Display Format

```
Topic: cooking recipes
Demand: 70.1/100
Competition: 31.7/100
Opportunity: 47.9/100
Audience: 174,084,665

Data Richness: ⭐⭐⭐⭐ (4/5)
├─ Trends: 53 pts : 11.1 interest
├─ Reddit: 50 posts : 9462 engage
└─ YouTube: 20 videos : 8,625,028.45 views

Recency/Urgency: 39.4/100
├─ Recent Activity: 15.7% in 90d
├─ Last 30 days: 5 items
├─ Trend: rising
└─ Avg Age: 938 days

Zone: GOLD MINE
```

---

## Known Limitations & Caveats

### 1. Sample Size Limitations
- **Reddit:** Only 50 posts sampled (may represent < 0.001% of total for broad topics)
- **YouTube:** Only 20 videos sampled (may represent < 0.0001% of total)
- **Impact:** Recency metrics may underestimate activity for very broad topics

### 2. Sorting Bias
- **Current:** Results sorted by "relevance" (platform algorithm)
- **Issue:** May favor older, highly-engaged content over recent posts
- **Impact:** Recency scores skewed toward older content for popular topics

### 3. API Rate Limits
- **Google Trends:** ~10-15 requests/hour (free tier)
- **Reddit:** 60 requests/minute (authenticated)
- **YouTube:** 10,000 quota units/day (~100 searches/day)
- **Mitigation:** 12s delays, caching, exponential backoff

### 4. Absolute vs Relative Scoring
- **Google Trends:** Scores are absolute (0-100) when querying individually
- **Issue:** Batch queries return relative scores (normalized against each other)
- **Solution:** Query each keyword individually to maintain score independence

### 5. Timestamp Accuracy
- **Reddit:** Unix timestamps are exact (post creation time)
- **YouTube:** ISO 8601 format converted to Unix (video publish time)
- **Issue:** Does not account for viral spikes or seasonal variations

---

## Recommendations for Improvement

### Short-term (< 1 hour):
1. ✅ **Increase sample sizes**
   - Reddit: 50 → 100 posts
   - YouTube: 20 → 50 videos
   - Cost: Slower queries, more API usage

2. ✅ **Change sort order to "new"**
   - Reddit: Sort by "new" instead of "relevance"
   - YouTube: Order by "date" instead of "relevance"
   - Benefit: More accurate recency metrics

3. ✅ **Update tooltip labeling**
   - Change "Last 30 days: 5 items" → "Last 30 days: 5/70 sampled (7%)"
   - Make sampling methodology transparent to user

### Medium-term (2-4 hours):
4. **Implement dual sampling strategy**
   - Sample A: 50 posts sorted by "relevance" (for quality)
   - Sample B: 50 posts sorted by "new" (for recency)
   - Combine results for balanced view

5. **Add timestamp distribution visualization**
   - Show histogram of post ages in tooltip
   - Visual representation more informative than single "avg age" number

### Long-term (future):
6. **Multi-timeframe analysis**
   - Query "last week", "last month", "last year" separately
   - Detect momentum shifts and seasonal patterns

7. **Weighted recency scoring**
   - Weight recent items higher than old items
   - Use exponential decay: recent items count more toward score

8. **Topic categorization**
   - Classify topics as "broad" vs "niche"
   - Apply different sampling strategies based on category
   - Broad topics need larger samples, niche topics can use smaller samples

---

## Conclusion

The tooltip provides a **multi-dimensional snapshot** of a topic's market potential by combining:
- **Demand signals** (Google Trends, Reddit engagement, YouTube views)
- **Competition analysis** (saturation across platforms)
- **Data confidence** (richness scoring based on sample quality)
- **Timing intelligence** (recency/urgency scoring)

**Critical Understanding:**
All metrics are based on **sampled data**, not exhaustive data. For broad topics like "cooking recipes", the sample may represent a tiny fraction of total content. The system is optimized for **relative comparison between topics** rather than absolute market measurement.

**Use Case:**
Best used to compare multiple topic candidates against each other (e.g., "cooking recipes" vs "vegan desserts" vs "air fryer recipes") rather than as definitive market sizing data.
