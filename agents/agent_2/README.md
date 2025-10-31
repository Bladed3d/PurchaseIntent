# Agent 2: Demographics Analyst

Extract demographic profiles from product reviews and discussions with confidence validation.

## Purpose

Transforms unstructured customer feedback into actionable demographic insights:
- **Input**: Reviews/comments from Amazon, Reddit, YouTube
- **Output**: Demographic profiles with age, occupation, pain points, interests
- **Validation**: Triangulation across 3+ sources with confidence scoring

## Features

- **Multi-Source Extraction**: Analyze Amazon reviews, Reddit comments, YouTube comments
- **Pattern-Based Demographics**: Extract age, occupation, pain points, interests using regex patterns
- **Clustering**: Group customers into 4 distinct segments
- **Confidence Scoring**: Triangulation formula validates reliability
- **Checkpoint Gate**: Blocks low-confidence results (<80%) unless user approves
- **ZERO API Cost**: Uses pattern matching (no paid AI APIs needed for MVP)

## LED Breadcrumb Range: 2500-2599

- **2500**: Agent 2 started
- **2510-2519**: Data scraping (Amazon, Reddit, YouTube)
- **2540-2559**: Demographics extraction
- **2560-2569**: Clustering and aggregation
- **2570-2579**: Confidence calculation and validation
- **2575-2579**: Checkpoint gate evaluation
- **2580**: Agent 2 complete
- **2590-2599**: Error range

## Usage

### Basic Usage (with Agent 1 output)
```bash
python agents/agent_2/main.py --input agents/agent_1/outputs/20251031_123456-comparables.json
```

### Testing with Test Data
```bash
python agents/agent_2/main.py --test-data tests/fixtures/agent2_test_data.json
```

### Auto-Approve Low Confidence (for testing)
```bash
python agents/agent_2/main.py --test-data tests/fixtures/agent2_test_data.json --auto-approve
```

## Output Format

```json
{
  "agent": "demographics_analyst",
  "status": "complete",
  "demographics_overall": {
    "age_range": "millennial",
    "age_distribution": {"millennial": 62%, "gen_x": 28%},
    "top_occupations": [
      {"occupation": "entrepreneur", "frequency": 38%}
    ],
    "top_pain_points": [
      {"pain": "time_management", "mentions": 67}
    ],
    "top_interests": ["productivity", "business_growth"]
  },
  "demographic_clusters": [
    {
      "cluster_id": "entrepreneur_millennial",
      "size": 152,
      "age_range": "30-45",
      "top_pain_points": ["delegation", "scaling"]
    }
  ],
  "validation": {
    "confidence_score": 0.85,
    "confidence_percentage": 85.0,
    "breakdown": {
      "source_agreement": 0.95,
      "sample_size_score": 1.0,
      "benchmark_match": 0.80
    },
    "meets_threshold": true
  }
}
```

## Confidence Formula

```
Confidence = (Source Agreement × 40%) + (Sample Size × 30%) + (Benchmark Match × 30%)
```

- **Source Agreement**: Do Amazon, Reddit, YouTube demographics align?
- **Sample Size**: Are there 300+ data points?
- **Benchmark Match**: Do demographics match industry benchmarks (Pew Research)?

## Checkpoint Gate

If confidence < 80%, user is prompted:
- **'yes'**: Continue with low confidence (accept risk)
- **'no'**: Abort and collect more data
- **'details'**: Show detailed demographic breakdown

## Configuration

Edit `agents/agent_2/config.py`:
```python
MIN_DATA_POINTS_REQUIRED = 300  # Minimum sample size
CONFIDENCE_THRESHOLD = 0.80     # 80% confidence required
NUM_DEMOGRAPHIC_CLUSTERS = 4    # Number of customer segments
```

## File Structure

```
agents/agent_2/
├── config.py                    # Configuration (<150 lines)
├── scraper.py                   # Data loader (<300 lines)
├── demographics_extractor.py    # Pattern-based extraction (<300 lines)
├── aggregator.py                # Clustering logic (<300 lines)
├── confidence_calculator.py     # Triangulation scoring (<300 lines)
├── checkpoint.py                # Confidence gate (<200 lines)
├── main.py                      # CLI entry point (<200 lines)
└── outputs/                     # JSON results directory
```

## Next Steps

After Agent 2 completes:
1. **Review demographics**: Check age, occupation, pain points
2. **Validate clusters**: Do customer segments make sense?
3. **Run Agent 3**: Generate synthetic personas based on these demographics

## Dependencies

- Python 3.8+
- No ML libraries needed for MVP (uses pattern matching)
- Future: sentence-transformers for advanced clustering

## Testing

Test with realistic data:
```bash
# Create test data with 15 reviews (Amazon, Reddit, YouTube)
python agents/agent_2/main.py --test-data tests/fixtures/agent2_test_data.json --auto-approve
```

Expected output:
- Demographics extracted from 15 profiles
- 4 clusters created (entrepreneur, software_developer, manager, etc.)
- Confidence ~40% (low due to small sample size)
- Auto-approved if --auto-approve flag set

## Troubleshooting

**Low Confidence (<80%)**:
- Increase sample size (collect more reviews/comments)
- Add more data sources (YouTube if not included)
- Find benchmark data (Pew Research, Statista)

**No Demographics Extracted**:
- Check review text contains demographic clues (age, occupation)
- Verify pattern matching in `demographics_extractor.py`
- Add more occupation/pain point patterns

**Agent 1 Not Found**:
- Run Agent 1 first: `python agents/agent_1/main.py <topic>`
- Or use test data: `--test-data tests/fixtures/agent2_test_data.json`
