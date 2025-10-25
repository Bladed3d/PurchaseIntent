# SSR (Semantic Similarity Rating) - Implementation Summary

**Source:** LLM-Predict-Purchase-Intent.pdf (PyMC Labs + Colgate-Palmolive, Oct 2025)

---

## Core Problem SSR Solves

**❌ Don't ask LLMs for direct numeric ratings (1-5)**
- Produces unrealistic distributions (too narrow, regression to mean)
- Over-concentrated on "3" (safe middle choice)
- Misses extremes (rarely outputs 1 or 5)
- KS similarity to human data: only 0.26-0.39

**✅ Instead: Elicit text, then map via semantic similarity**
- Realistic distributions matching human surveys
- KS similarity: 0.80-0.88 (vs 0.26-0.39 for direct rating)
- 90% correlation attainment (test-retest reliability ceiling)
- Rich qualitative feedback as byproduct

---

## The SSR Method (3 Steps)

### Step 1: Elicit Free-Text Response
Prompt persona with product concept, ask:
> "How likely are you to purchase this product?"

**Don't constrain to 1-5.** Let LLM respond naturally in text.

**Example responses:**
- "I'm somewhat interested. If it works well and isn't too expensive, I might give it a try."
- "It's very likely I'd buy it. I love the convenience and the price is reasonable."
- "It's rather unlikely I'd buy it. I don't see much value for my needs."

### Step 2: Create Reference Anchor Statements

Define 5 anchor statements (one per Likert point 1-5):

| Rating | Example Anchor Statement |
|--------|-------------------------|
| 1 | "It's rather unlikely I'd buy it." |
| 2 | "I might consider it, but probably not." |
| 3 | "I'm neutral - could go either way." |
| 4 | "I'd probably buy it if the price is right." |
| 5 | "It's very likely I'd buy it." |

**Note:** Use 6 different reference sets, average results (improves stability)

### Step 3: Map Text to Distribution via Embeddings

1. **Get embeddings:**
   - Embed the LLM's text response: `v_response`
   - Embed all 5 anchor statements: `v_anchor[1..5]`
   - Use: OpenAI `text-embedding-3-small` (research used this)

2. **Calculate cosine similarity:**
   ```
   similarity(rating_i) = cosine(v_response, v_anchor[i])
   ```

3. **Convert to probability distribution:**
   ```
   p(rating_i) ∝ similarity(rating_i) - min(similarity) + ε

   where:
   - Subtract minimum similarity to increase spread
   - ε = small constant (0 in research, but tunable)
   - Normalize so Σ p(rating_i) = 1
   ```

4. **Optional temperature control:**
   ```
   p(rating_i, T) ∝ p(rating_i)^(1/T)

   where T = 1 is default (can optimize for better fit)
   ```

**Result:** Each persona produces a probability distribution over 1-5, not a single number.

---

## Key Research Findings

### Success Metrics
- **90% correlation attainment** - achieves 90% of theoretical maximum (human test-retest ceiling)
- **KS similarity > 0.85** - distributions match human surveys
- **Zero fine-tuning required** - works with vanilla GPT-4o, Gemini-2.0-flash
- **Realistic spread** - wider dynamic range than human surveys (less positivity bias)

### What Matters for Accuracy

**✅ Critical factors:**
1. **Demographic conditioning** - Age and income level mirror human behavior well
2. **Multiple reference sets** - Average over 6 sets (not just 1)
3. **Textual elicitation first** - Never ask for numbers directly

**❌ Less important:**
- Gender, region, ethnicity - poorly replicated
- Temperature (0.5 vs 1.5) - minimal difference
- Image vs text stimulus - image slightly better but text works

**🔴 Dealbreaker:**
- **NO demographics = 50% correlation** (vs 90% with demographics)
- Even with perfect distribution similarity (0.91), ranking products fails without persona conditioning

---

## Implementation for Purchase-Intent System

### Agent 3: Persona Generator (LED 3500-3599)
**Output:** 500 personas with demographics
- Age (use bins: 20-30, 31-40, 41-50, 51-60, 61-70, 71-80)
- Income level (6 tiers from research)
- Optional: gender, region (less critical but include)

**Format:** JSON array
```json
{
  "persona_id": "P0001",
  "age": 35,
  "income_level": 4,
  "gender": "female",
  "region": "South"
}
```

### Agent 4: ParaThinker Intent Simulator (LED 4500-4599)

**For each persona × 8 reasoning paths:**

1. **Generate text response** (not numeric!)
   - System prompt: "You are a {age}-year-old {gender} from {region} with income level {income}..."
   - User prompt: "How likely are you to purchase this product? Explain briefly."

2. **Apply SSR mapping:**
   - Embed response with `text-embedding-3-small`
   - Compare to 5 anchor embeddings
   - Calculate probability distribution p(1), p(2), p(3), p(4), p(5)

3. **Aggregate 8 paths:**
   - Average distributions across VALUE, FEATURES, EMOTIONS, RISKS, SOCIAL_PROOF, ALTERNATIVES, TIMING, TRUST paths
   - Each path produces its own p(i), final persona rating = mean of 8 distributions

4. **Report distribution:**
   - Don't collapse to single number yet
   - Keep full distribution for analysis
   - Mean purchase intent = Σ(i × p(i)) for ranking

---

## Reference Anchor Sets

**Research used 6 sets for purchase intent. Here's Set 1 (minimal):**

```python
REFERENCE_ANCHORS_SET_1 = {
    1: "It's rather unlikely I'd buy it.",
    2: "I might consider it, but I'm not convinced.",
    3: "I'm on the fence - could go either way.",
    4: "I'd probably buy it if it meets my needs.",
    5: "It's very likely I'd buy it."
}
```

**For Agent 4:** Create 6 similar sets with slight variations, average SSR results.

---

## Validation Formula

**Confidence Scoring (from handoff):**
```
Confidence = (Source Agreement × 40%) +
             (Sample Size × 30%) +
             (Benchmark Match × 30%)

Target: 80%+ for Agent 2 (Demographics)
```

**Triangulation (3+ sources minimum):**
- Reddit reviews
- Amazon reviews
- YouTube comments
- Subreddit overlap analysis

**SSR Distribution Check:**
- KS similarity to validation benchmark > 0.80
- Mean purchase intent within ±0.2 of expected
- No over-concentration on single rating

---

## Common Pitfalls to Avoid

1. **❌ Direct numeric elicitation**
   ```python
   # WRONG
   response = llm("Rate 1-5: How likely to purchase?")
   rating = int(response)  # Terrible distributions!
   ```

2. **❌ Single reference set**
   - Use 6 sets, average results (research shows this matters)

3. **❌ Skipping demographics**
   - Without age/income: 50% correlation
   - With demographics: 90% correlation

4. **❌ Collapsing too early**
   - Keep distributions through analysis
   - Only compute mean for final ranking

5. **❌ Ignoring minimum similarity**
   - Subtract `min(similarity)` before normalizing
   - Otherwise distributions too flat

---

## Code Snippet (Pseudocode)

```python
def ssr_rating(text_response, reference_anchors, embedding_model):
    """
    Convert text response to Likert distribution via SSR.

    Args:
        text_response: LLM's free-text answer
        reference_anchors: dict {1: "text", 2: "text", ...5: "text"}
        embedding_model: OpenAI text-embedding-3-small

    Returns:
        dict: {1: p1, 2: p2, 3: p3, 4: p4, 5: p5}
    """
    # Get embeddings
    v_response = embedding_model.embed(text_response)
    v_anchors = {i: embedding_model.embed(text)
                 for i, text in reference_anchors.items()}

    # Calculate cosine similarities
    similarities = {}
    for i in range(1, 6):
        similarities[i] = cosine_similarity(v_response, v_anchors[i])

    # Subtract minimum (increase spread)
    min_sim = min(similarities.values())
    adjusted = {i: sim - min_sim for i, sim in similarities.items()}

    # Normalize to probability distribution
    total = sum(adjusted.values())
    distribution = {i: adj / total for i, adj in adjusted.items()}

    return distribution

# Usage for 8-path ParaThinker
distributions = []
for path in ["VALUE", "FEATURES", "EMOTIONS", "RISKS",
             "SOCIAL_PROOF", "ALTERNATIVES", "TIMING", "TRUST"]:

    text = generate_response(persona, product, reasoning_path=path)
    dist = ssr_rating(text, REFERENCE_ANCHORS_SET_1, embedding_model)
    distributions.append(dist)

# Average across paths
final_distribution = average_distributions(distributions)
mean_rating = sum(i * p for i, p in final_distribution.items())
```

---

## Success Criteria for Our System

**Agent 4 (ParaThinker) must achieve:**
- ✅ **85-90% correlation** with human survey responses
- ✅ **KS similarity > 0.85** for distribution matching
- ✅ **Realistic spread** - no over-concentration on middle values
- ✅ **500 personas × 8 paths = 4,000 perspectives** (not 4,000 single numbers!)

**Validation against PickFu or similar:**
- Run 10 test products through both systems
- Measure correlation of mean purchase intents
- Target: R > 0.85 (Pearson correlation)

---

## References

- **Paper:** "LLMs Reproduce Human Purchase Intent via Semantic Similarity Elicitation of Likert Ratings" (arXiv:2510.08338v1, Oct 2025)
- **Authors:** PyMC Labs + Colgate-Palmolive
- **Dataset:** 57 personal care product surveys, 9,300 human responses
- **Models tested:** GPT-4o, Gemini-2.0-flash (both work well)
- **Embedding:** OpenAI `text-embedding-3-small`

---

**Key Insight:** The problem wasn't that LLMs can't predict purchase intent. The problem was asking them for numbers instead of language. SSR fixes this by letting LLMs do what they're good at (generate text), then using embeddings to map that text to structured ratings.
