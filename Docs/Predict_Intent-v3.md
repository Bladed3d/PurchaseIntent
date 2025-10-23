# Predict Intent: AI-Powered Customer Response Testing System

**Document Version**: 3.0  
**Last Updated**: January 2025  
**Focus**: Research-Grounded Development Plan  
**Status**: Planning Phase

---

## Document Changelog

### Version 3.0 (Current)
- **Synthesized best ideas** from three previous plans:
  - v2.0: Practical 12-week development timeline and technical implementation
  - GLM: Comprehensive use cases and multi-provider architecture
  - Grok: Research-grounded SSR methodology and validation approach
- **Enhanced with**: Semantic Similarity Rating (SSR) implementation details, multimodal support, research validation framework
- **Improved**: Model selection strategy, prompt engineering, validation testing

---

## Executive Overview

This system tests products, books, course materials, advertising, and landing pages by simulating diverse customer personas using AI. Based on research achieving **92% correlation with human purchase intent ratings** (Maier et al., 2024), it replaces slow, expensive surveys with instant, scalable AI predictions.

**Core Innovation**: Uses **Semantic Similarity Rating (SSR)** instead of direct Likert scoring. LLMs generate natural textual responses, which are then mapped to rating scales via embedding similarity—avoiding the artificial response distributions that plague direct numerical elicitation.

### Key Benefits
- ⚡ **Speed**: Minutes vs weeks for traditional research
- 💰 **Cost**: 100x cheaper ($0.00001 vs $1.00 per response)
- 📊 **Accuracy**: 92% correlation with human judgments
- 🎯 **Scalability**: Test unlimited variations and personas
- 📈 **Insights**: Quantitative scores + qualitative reasoning

---

## Research Foundation: Why This Works

### The Semantic Similarity Rating (SSR) Breakthrough

**The Problem with Direct Elicitation**:
When you ask LLMs "Rate this 1-7", they produce unrealistically narrow distributions (e.g., mostly 5s and 6s) that don't match human response patterns.

**The Solution (SSR)**:
1. Ask LLM to respond naturally: "As this persona, how do you feel about this product?"
2. Embed the textual response using embedding models
3. Compare similarity to pre-defined anchor statements for each scale point
4. Map to Likert scale based on highest semantic similarity
5. Result: Realistic distributions matching human patterns

### Validation Metrics (from Research)
- **Correlation Attainment**: >80% (how often rankings match human rankings)
- **Kolmogorov-Smirnov (KS) Similarity**: >0.85 (distribution shape match)
- **Mean Absolute Error**: <0.5 on 7-point scale
- **Best Models Tested**: GPT-4o, Gemini-2.0-flash, Claude Sonnet

### Why Multiple LLM Options Matter
Research shows different models excel at different aspects:
- **GPT-4o**: Best overall correlation, strong with complex reasoning
- **Gemini-2.0-flash**: Faster, cost-effective, good distributions
- **Claude Sonnet 4.5**: Excellent reasoning, extended context (200K tokens), best for long content

---

## System Architecture

### High-Level Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    User Input Layer                         │
│  (Content + Target Demographics + Test Configuration)       │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│              Persona Generation Engine                      │
│    (Create diverse synthetic consumers from specs)          │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│            Content Analysis Engine                          │
│     (Extract features, parse structure, prep for LLM)       │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│         Response Generation (LLM Layer)                     │
│  Parallel API calls → Natural language responses           │
│     GPT-4o / Claude Sonnet 4.5 / Gemini 2.0                │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│      Semantic Similarity Rating (SSR) Engine                │
│  Embed responses → Compare to anchors → Map to scale        │
│         OpenAI Embeddings / Voyage AI                       │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│         Analysis & Aggregation Layer                        │
│  Stats + Distributions + Themes + Insights                  │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│            Results Dashboard & Reports                      │
│    Interactive visualizations + Exportable insights         │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Backend**
- **Language**: Python 3.11+
- **Framework**: FastAPI (async, type hints, auto-docs)
- **Database**: PostgreSQL (structured data) + pgvector (embeddings)
- **Cache**: Redis (persona templates, frequent queries)
- **Queue**: Celery + Redis (async batch processing)
- **Task Orchestration**: Prefect or Temporal (complex workflows)

**AI/ML Layer**
- **Primary LLM**: Claude Sonnet 4.5 (extended context, reasoning)
- **Alternate LLMs**: GPT-4o (multimodal), Gemini 2.0 Flash (cost/speed)
- **Embeddings**: Voyage AI (research-grade quality) with OpenAI fallback
- **Vector Store**: Pinecone or pgvector (for anchor embeddings)
- **Model Routing**: LiteLLM (unified interface across providers)

**Frontend**
- **Framework**: React 18+ with TypeScript
- **UI Library**: Tailwind CSS + shadcn/ui components
- **State**: Zustand (simple) + React Query (API state)
- **Charts**: Recharts + D3.js (custom visualizations)
- **Build**: Vite (fast HMR)

**DevOps & Monitoring**
- **Hosting**: 
  - Frontend: Vercel (edge deployment)
  - Backend: Railway or Fly.io (auto-scaling)
- **Containers**: Docker + docker-compose (local dev)
- **CI/CD**: GitHub Actions
- **Monitoring**: Sentry (errors) + Axiom (logs) + Prometheus (metrics)
- **APM**: OpenTelemetry for distributed tracing

---

## Core Features (MVP)

### 1. Content Analysis Engine

**Supported Input Types** (MVP):
- ✅ Product descriptions (text, up to 10K tokens)
- ✅ Ad copy (headline + body + CTA)
- ✅ Landing page copy (paste text or URL scraping)
- ✅ Book descriptions/summaries
- ✅ Course outlines and descriptions

**Future** (Post-MVP):
- 🔲 Images (product photos, book covers, ad creatives)
- 🔲 Full landing pages (screenshots via vision LLMs)
- 🔲 Video transcripts + thumbnails
- 🔲 Interactive demos/prototypes

**Analysis Output**:
```json
{
  "content_type": "product_description",
  "value_proposition": "Extracted core value prop",
  "key_features": ["Feature 1", "Feature 2"],
  "benefits": ["Benefit 1", "Benefit 2"],
  "emotional_tone": "excited and aspirational",
  "clarity_score": 0.85,
  "cta_strength": "medium",
  "readability": {
    "grade_level": 8.5,
    "avg_sentence_length": 15
  }
}
```

### 2. Synthetic Persona Generation

**Two-Tier Approach**:

**Tier 1: Template Library** (Fast, Consistent)
- 50 pre-built personas covering major demographics
- Categories:
  - Age groups: Gen Z (18-24), Millennial (25-40), Gen X (41-56), Boomer (57+)
  - Income: Budget-conscious, Middle-class, Premium buyers
  - Shopping styles: Impulse, Researcher, Value-seeker, Early adopter
  - Contexts: B2B vs B2C, first-time vs repeat buyer

**Tier 2: Dynamic Generation** (Flexible, Custom)
- User specifies demographics: age range, gender, location, income
- User specifies psychographics: values, pain points, interests
- LLM generates realistic, internally consistent personas
- Validation: Check for coherence and stereotype avoidance

**Persona Attributes** (JSON Schema):
```json
{
  "persona_id": "uuid",
  "name": "Sarah Chen",
  "demographics": {
    "age": 32,
    "gender": "female",
    "income_level": "$75K-$100K",
    "education": "Bachelor's degree",
    "location": "Seattle, WA (urban)",
    "family_status": "married, 1 child"
  },
  "psychographics": {
    "values": ["sustainability", "quality", "convenience"],
    "pain_points": ["time constraints", "decision fatigue"],
    "interests": ["fitness", "technology", "cooking"],
    "lifestyle": "busy professional, health-conscious"
  },
  "behavioral": {
    "shopping_style": "careful researcher",
    "decision_factors": ["reviews", "brand reputation", "value for money"],
    "purchase_frequency": "monthly for necessities",
    "price_sensitivity": "medium",
    "brand_loyalty": "moderate"
  },
  "context": {
    "product_familiarity": "aware of category, new to brand",
    "current_need_state": "actively searching for solution",
    "time_to_decision": "weeks"
  }
}
```

### 3. Response Generation & SSR Implementation

**Step 1: Natural Response Elicitation**

```python
# Prompt template for textual response
response_prompt = """
You are {persona_name}, a {age}-year-old {gender} living in {location}.

Your characteristics:
- Values: {values}
- Shopping style: {shopping_style}
- You care most about: {decision_factors}

You encounter this {content_type}:
---
{content}
---

Respond naturally as this person would. Consider:
- Does this align with your values and needs?
- What catches your attention (positive or negative)?
- What questions or concerns do you have?
- How does it make you feel?

Write a brief, authentic response (2-4 sentences) about your reaction to this.
Do NOT use numbers or explicit ratings.
"""
```

**Configuration**:
- Model: Claude Sonnet 4.5 or GPT-4o
- Temperature: 0.5-0.7 (balance consistency & diversity)
- Max tokens: 150-200 (natural paragraph response)
- System prompt: "Respond authentically as the described persona"

**Step 2: Semantic Similarity Rating (SSR)**

**Anchor Statement Sets** (Example for Purchase Intent, 5-point Likert):

```python
# Set 1: Direct intent statements
anchors_set_1 = {
    1: "I would definitely not buy this. It doesn't appeal to me at all.",
    2: "I'm very unlikely to buy this. It has some issues that concern me.",
    3: "I might or might not buy this. I'm neutral about it.",
    4: "I'm likely to buy this. It seems promising and addresses my needs.",
    5: "I would definitely buy this. It's exactly what I'm looking for."
}

# Set 2: Emotional reactions
anchors_set_2 = {
    1: "This is completely wrong for me. I'm not interested whatsoever.",
    2: "This doesn't really work for me. I have significant reservations.",
    3: "I'm on the fence. It's okay but nothing special.",
    4: "I'm genuinely interested. This could be a good fit for me.",
    5: "I'm excited about this! This is perfect for what I need."
}

# Set 3: Action-oriented
anchors_set_3 = {
    1: "I would scroll past this without a second thought.",
    2: "I might glance at it but wouldn't pursue further.",
    3: "I'd probably bookmark it to consider later.",
    4: "I'd add this to my cart or shortlist.",
    5: "I'd buy this right now without hesitation."
}

# Research shows: Average across 6 anchor sets for robustness
```

**SSR Algorithm**:

```python
def calculate_ssr_score(response_text: str, anchor_sets: List[Dict]) -> Dict:
    """
    Map textual response to Likert scale via semantic similarity.
    
    Returns:
        {
            "rating": float,  # 1.0 to 5.0 (or 7.0)
            "confidence": float,  # 0.0 to 1.0
            "distribution": dict,  # probability mass function
            "method": "SSR"
        }
    """
    # 1. Embed the response
    response_embedding = embed_text(response_text)
    
    all_scores = []
    
    # 2. For each anchor set
    for anchor_set in anchor_sets:
        set_similarities = {}
        
        # 3. Compute similarity to each anchor
        for scale_point, anchor_text in anchor_set.items():
            anchor_embedding = embed_text(anchor_text)
            similarity = cosine_similarity(response_embedding, anchor_embedding)
            set_similarities[scale_point] = similarity
        
        # 4. Normalize to probability distribution
        total_similarity = sum(set_similarities.values())
        pmf = {k: v/total_similarity for k, v in set_similarities.items()}
        
        # 5. Calculate expected value for this set
        expected_value = sum(scale * prob for scale, prob in pmf.items())
        all_scores.append(expected_value)
    
    # 6. Average across all anchor sets
    final_rating = np.mean(all_scores)
    confidence = 1.0 - np.std(all_scores)  # Lower variance = higher confidence
    
    # 7. Average distribution across sets
    avg_distribution = calculate_avg_distribution(anchor_sets, response_embedding)
    
    return {
        "rating": round(final_rating, 2),
        "confidence": round(confidence, 2),
        "distribution": avg_distribution,
        "method": "SSR"
    }
```

**Fallback: Follow-up Likert Rating (FLR)**

If SSR confidence is low (<0.6), use direct follow-up:

```python
flr_prompt = """
Based on your previous response: "{response_text}"

On a scale of 1-5, where:
1 = Definitely would NOT buy/engage
2 = Probably would not
3 = Might or might not
4 = Probably would
5 = Definitely would

What number best represents your intent?
Respond with ONLY the number.
"""
```

### 4. Results Analysis & Aggregation

**Quantitative Metrics**:

```json
{
  "overall_metrics": {
    "mean_intent": 3.8,
    "median_intent": 4.0,
    "std_dev": 1.2,
    "distribution": {
      "1": 5,   // 5% rated 1
      "2": 10,
      "3": 20,
      "4": 40,
      "5": 25
    },
    "sample_size": 100,
    "confidence_interval_95": [3.55, 4.05]
  },
  
  "segmentation": {
    "by_age": {
      "18-24": {"mean": 4.2, "n": 20},
      "25-40": {"mean": 3.9, "n": 40},
      "41-56": {"mean": 3.5, "n": 25},
      "57+": {"mean": 3.2, "n": 15}
    },
    "by_income": {
      "budget": {"mean": 3.1, "n": 30},
      "middle": {"mean": 3.9, "n": 45},
      "premium": {"mean": 4.5, "n": 25}
    }
  },
  
  "validation_metrics": {
    "ks_similarity": 0.87,  // vs benchmark if available
    "response_consistency": 0.82  // across reruns
  }
}
```

**Qualitative Analysis**:

```python
# Extract themes from textual responses
def analyze_themes(responses: List[str]) -> Dict:
    """
    Cluster responses and extract common themes.
    """
    # 1. Embed all responses
    embeddings = [embed_text(r) for r in responses]
    
    # 2. Cluster into positive/neutral/negative
    clusters = kmeans_cluster(embeddings, n_clusters=3)
    
    # 3. Extract representative quotes
    top_quotes = get_representative_samples(clusters, responses)
    
    # 4. Identify common keywords/phrases
    themes = extract_themes_via_llm(responses)
    
    return {
        "key_motivators": [
            "Feature X mentioned 45 times",
            "Price point appreciated by 60%",
            "Brand reputation cited by 30%"
        ],
        "key_objections": [
            "Unclear shipping policy (25% concern)",
            "Perceived as expensive (20%)",
            "Skepticism about claims (15%)"
        ],
        "sentiment_distribution": {
            "positive": 55,
            "neutral": 30,
            "negative": 15
        },
        "representative_quotes": {
            "positive": ["This is exactly what I need!", ...],
            "neutral": ["Seems okay but not sure yet", ...],
            "negative": ["Too expensive for what it offers", ...]
        }
    }
```

### 5. A/B Testing & Comparison

**Features**:
- Compare 2-10 variants simultaneously
- Statistical significance testing (Bayesian & Frequentist)
- Effect size calculation
- Winner recommendation with confidence level

**Output**:
```json
{
  "test_id": "uuid",
  "variants": ["A", "B"],
  "winner": "B",
  "confidence": 0.95,
  "results": {
    "A": {"mean": 3.5, "n": 100},
    "B": {"mean": 4.2, "n": 100}
  },
  "effect_size": 0.7,  // Cohen's d
  "p_value": 0.002,
  "recommendation": "Variant B performs significantly better (p<0.05). Deploy with confidence.",
  "key_difference": "Variant B's clearer value proposition resonates better with 25-40 age group."
}
```

---

## Development Phases (12 Weeks to MVP)

### Phase 1: Foundation & SSR Implementation (Weeks 1-3)

**Week 1: Core Infrastructure + LLM Integration**
- [ ] Set up project repos (backend, frontend, monorepo structure)
- [ ] Configure multi-LLM integration via LiteLLM
  - Claude Anthropic API
  - OpenAI API (GPT-4o + embeddings)
  - Google Gemini API
- [ ] Implement LLM routing logic (primary/fallback)
- [ ] Set up PostgreSQL + pgvector for embeddings
- [ ] Create basic prompt template system
- [ ] Implement authentication (Auth0 or Clerk for simplicity)

**Week 2: SSR Engine Development**
- [ ] Implement embedding pipeline (Voyage AI + OpenAI fallback)
- [ ] Create anchor statement library for purchase intent
- [ ] Build SSR scoring algorithm
- [ ] Test SSR with sample data from research paper
- [ ] Validate against research benchmarks (aim for KS >0.85)
- [ ] Implement FLR fallback mechanism
- [ ] Create anchor sets for other intent types (engagement, satisfaction)

**Week 3: Persona System**
- [ ] Design persona database schema
- [ ] Create 30 template personas (demographics + psychographics)
- [ ] Build dynamic persona generator using Claude
- [ ] Implement persona validation (coherence checking)
- [ ] Test persona consistency across multiple generations
- [ ] Create persona API endpoints
- [ ] Build persona selection UI component

### Phase 2: Content Analysis & Response Generation (Weeks 4-6)

**Week 4: Content Processing**
- [ ] Build content parser for product descriptions
- [ ] Build content parser for ad copy (headline/body/CTA separation)
- [ ] Implement landing page text extraction
- [ ] Build book/course outline parser
- [ ] Create content quality analyzer (readability, clarity, tone)
- [ ] Implement URL scraping for landing pages
- [ ] Test with diverse content samples

**Week 5: Response Generation Pipeline**
- [ ] Design optimal prompts for natural response elicitation
- [ ] Implement parallel API calls (async processing)
- [ ] Build response validation and error handling
- [ ] Add retry logic with exponential backoff
- [ ] Implement rate limiting per API provider
- [ ] Create progress tracking for batch operations
- [ ] Test response quality across different LLMs

**Week 6: Integration & Testing**
- [ ] Connect content analysis → persona → response → SSR pipeline
- [ ] Implement end-to-end test flow
- [ ] Build results aggregation engine
- [ ] Create statistical analysis functions
- [ ] Implement theme extraction from responses
- [ ] Test full pipeline with real content examples
- [ ] Benchmark performance (speed, cost, accuracy)

### Phase 3: User Interface & Visualization (Weeks 7-9)

**Week 7: Dashboard Foundation**
- [ ] Create dashboard layout and navigation
- [ ] Build test creation wizard
  - Content input (text area, file upload, URL)
  - Test type selection (product, book, ad, etc.)
  - Target audience specification
- [ ] Implement persona selection interface (templates + custom)
- [ ] Create sample size configurator
- [ ] Add test preview before running
- [ ] Build test queue and status tracking

**Week 8: Results Visualization**
- [ ] Create intent distribution chart (histogram)
- [ ] Build segment comparison view (grouped bar charts)
- [ ] Display individual persona responses (cards/table)
- [ ] Show key insights summary (cards with icons)
- [ ] Create theme extraction visualization (word clouds, bar charts)
- [ ] Add representative quotes section
- [ ] Implement CSV/PDF export

**Week 9: UX Polish & Onboarding**
- [ ] Add loading states and progress indicators
- [ ] Implement real-time result streaming (show as they arrive)
- [ ] Create error handling and user feedback system
- [ ] Build interactive onboarding tutorial
- [ ] Add sample/demo tests (pre-populated)
- [ ] Mobile responsive design
- [ ] Accessibility audit (WCAG 2.1 AA)
- [ ] User testing with 3-5 people

### Phase 4: A/B Testing & Launch Prep (Weeks 10-12)

**Week 10: A/B Testing Features**
- [ ] Build variant comparison interface
- [ ] Implement side-by-side test execution
- [ ] Add statistical significance calculators
- [ ] Create comparison visualizations (delta charts)
- [ ] Build winner recommendation engine
- [ ] Add historical test tracking
- [ ] Implement test result comparison across time

**Week 11: Validation & Optimization**
- [ ] Validate against research paper benchmarks
  - Run tests on known products with human data
  - Measure correlation attainment (target >80%)
  - Verify distribution similarity (KS >0.85)
- [ ] Optimize API costs (caching, batching)
- [ ] Performance optimization (query optimization, caching)
- [ ] Security audit (API keys, data encryption, input sanitization)
- [ ] Load testing (100 concurrent tests)
- [ ] Bug fixes from internal testing

**Week 12: Launch Preparation**
- [ ] Write comprehensive documentation
  - Getting started guide
  - API documentation
  - Best practices for writing testable content
- [ ] Create tutorial videos (3-5 minutes each)
- [ ] Set up monitoring and alerting
  - API error rates
  - Response times
  - Cost tracking
- [ ] Deploy to production
- [ ] Invite 10-20 beta users
- [ ] Set up feedback collection system
- [ ] Create launch announcement materials

---

## Technical Implementation Deep-Dive

### Multimodal Content Support (Post-MVP)

**Vision-Enabled Testing**:

```python
# For image-based content (book covers, product photos, ads)
def analyze_visual_content(image_url: str, content_type: str) -> Dict:
    """
    Use GPT-4o or Claude with vision to analyze visual content.
    """
    prompt = f"""
    You are analyzing this {content_type} image.
    
    Describe:
    1. Visual design and aesthetics
    2. Key elements and messaging
    3. Emotional tone conveyed
    4. Target audience signals
    5. Overall professional quality
    
    Be specific and detailed.
    """
    
    response = gpt4o_vision_call(
        prompt=prompt,
        image_url=image_url,
        max_tokens=500
    )
    
    return {
        "visual_analysis": response,
        "extracted_text": extract_text_from_image(image_url),  # OCR
        "design_quality_score": calculate_design_score(response)
    }
```

**Combined Text + Visual Analysis**:

```python
# For ads or landing pages with both text and images
combined_prompt = """
You are {persona_name}...

You see an advertisement with:

TEXT:
{ad_copy_text}

VISUAL DESCRIPTION:
{visual_analysis}

Respond naturally to this complete ad experience.
"""
```

### Advanced Prompt Engineering

**Few-Shot Examples for Consistency**:

```python
persona_response_prompt_with_examples = """
You are responding to content as a specific persona. Here are examples:

Example 1:
Persona: Budget-conscious college student
Content: Premium wireless headphones ($299)
Response: "These look amazing but way out of my price range. I'd need to save for months. 
The features are impressive but I could get something decent for $50. Pass for now."

Example 2:
Persona: Tech early adopter with high income
Content: Same headphones
Response: "Finally! The noise cancellation specs look solid. I've been waiting for something 
like this. Price is reasonable for the tech. Would definitely pick these up."

Now, your turn:
Persona: {persona_description}
Content: {content}
Response:
"""
```

### Caching Strategy for Cost Optimization

```python
# Cache persona embeddings (reuse across tests)
def get_or_create_persona_embedding(persona_id: str) -> np.ndarray:
    """
    Cache persona descriptions to avoid redundant embedding calls.
    """
    cache_key = f"persona_embedding:{persona_id}"
    
    cached = redis.get(cache_key)
    if cached:
        return np.frombuffer(cached)
    
    persona = db.get_persona(persona_id)
    embedding = embed_text(persona.full_description)
    
    # Cache for 30 days
    redis.setex(cache_key, 30*24*3600, embedding.tobytes())
    
    return embedding

# Cache anchor embeddings (compute once, reuse forever)
def initialize_anchor_cache():
    """
    Pre-compute all anchor statement embeddings on startup.
    """
    for intent_type in ['purchase', 'engagement', 'satisfaction']:
        for anchor_set_id, anchors in get_anchor_sets(intent_type):
            for scale_point, anchor_text in anchors.items():
                cache_key = f"anchor:{intent_type}:{anchor_set_id}:{scale_point}"
                if not redis.exists(cache_key):
                    embedding = embed_text(anchor_text)
                    redis.set(cache_key, embedding.tobytes())
```

### Database Schema (Enhanced)

```sql
-- Users
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(255),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Personas (with embeddings)
CREATE TABLE personas (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  name VARCHAR(255),
  demographics JSONB,
  psychographics JSONB,
  behavioral JSONB,
  full_description TEXT,
  embedding vector(1536),  -- pgvector for semantic search
  is_template BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX ON personas USING ivfflat (embedding vector_cosine_ops);

-- Tests
CREATE TABLE tests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  name VARCHAR(255),
  content_type VARCHAR(50),  -- product, ad, landing_page, book, course
  content TEXT,
  content_metadata JSONB,  -- extracted features
  test_config JSONB,  -- sample size, personas, etc.
  status VARCHAR(50),  -- pending, running, completed, failed
  created_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ
);

-- Responses (textual responses before SSR)
CREATE TABLE responses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  test_id UUID REFERENCES tests(id),
  persona_id UUID REFERENCES personas(id),
  raw_response TEXT,
  response_embedding vector(1536),
  llm_provider VARCHAR(50),
  llm_model VARCHAR(100),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Results (after SSR mapping)
CREATE TABLE results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  test_id UUID REFERENCES tests(id),
  response_id UUID REFERENCES responses(id),
  persona_id UUID REFERENCES personas(id),
  
  -- SSR outputs
  intent_rating DECIMAL(3,2),  -- 1.00 to 7.00
  confidence DECIMAL(3,2),  -- 0.00 to 1.00
  rating_method VARCHAR(10),  -- SSR or FLR
  distribution JSONB,  -- probability mass function
  
  -- Extracted insights
  sentiment VARCHAR(20),  -- positive, neutral, negative
  key_motivators TEXT[],
  key_objections TEXT[],
  emotional_response TEXT,
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX ON results (test_id, intent_rating);
CREATE INDEX ON results (persona_id);

-- Anchor statements (for SSR)
CREATE TABLE anchor_statements (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  intent_type VARCHAR(50),  -- purchase, engagement, satisfaction
  set_id INTEGER,  -- 1-6 (multiple sets for robustness)
  scale_point INTEGER,  -- 1-7
  statement TEXT,
  embedding vector(1536),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX ON anchor_statements (intent_type, set_id);

-- Test comparisons (for A/B tests)
CREATE TABLE test_comparisons (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  name VARCHAR(255),
  test_ids UUID[],
  winner_test_id UUID,
  confidence DECIMAL(3,2),
  statistical_summary JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### API Structure (Complete)

```
# Authentication
POST   /api/auth/register
POST   /api/auth/login
POST   /api/auth/logout
GET    /api/auth/me

# Personas
GET    /api/personas                  # List all (templates + user's)
GET    /api/personas/templates        # Get template library
POST   /api/personas                  # Create custom persona
GET    /api/personas/:id              # Get persona details
PUT    /api/personas/:id              # Update persona
DELETE /api/personas/:id              # Delete persona
POST   /api/personas/generate         # AI-generate from specs

# Content Analysis
POST   /api/content/analyze           # Analyze content before testing
POST   /api/content/extract-url       # Extract content from URL

# Tests
POST   /api/tests                     # Create new test
GET    /api/tests                     # List user's tests
GET    /api/tests/:id                 # Get test details
POST   /api/tests/:id/run             # Execute test (async)
GET    /api/tests/:id/status          # Check test progress
GET    /api/tests/:id/results         # Get results (when complete)
POST   /api/tests/:id/export          # Export to PDF/CSV
DELETE /api/tests/:id                 # Delete test

# Comparisons (A/B Testing)
POST   /api/comparisons               # Create A/B comparison
GET    /api/comparisons/:id           # Get comparison results
GET    /api/comparisons/:id/export    # Export comparison report

# Analytics
GET    /api/analytics/summary         # User's usage stats
GET    /api/analytics/trends          # Historical trends across tests

# Admin (future)
GET    /api/admin/validation          # System validation metrics
POST   /api/admin/anchors             # Update anchor statements
```

---

## Use Cases & Applications (Comprehensive)

### 1. Product Testing

**Scenario: E-commerce Product Launch**
- **Input**: New product description, images, price point
- **Personas**: Target demographic (e.g., 25-40 year olds, tech enthusiasts, $50K+ income)
- **Output**: 
  - Purchase intent score (1-7)
  - Price sensitivity analysis
  - Feature appeal ranking
  - Objections to address in marketing

**Example Test Configuration**:
```json
{
  "content_type": "product",
  "content": "SmartClean Pro: AI-powered robotic vacuum...",
  "target_audience": {
    "age_range": [25, 45],
    "income_range": ["$50K", "$150K"],
    "interests": ["smart home", "technology", "convenience"],
    "pain_points": ["busy schedule", "pet hair", "allergies"]
  },
  "test_focus": "purchase_intent",
  "sample_size": 200
}
```

**Actionable Insights**:
- "65% of target audience rates intent 4+, strong product-market fit"
- "Price point ($399) acceptable for 70% of premium segment"
- "Concern: 30% mention 'unproven brand' - add social proof"
- "Feature most cited: 'AI room mapping' - emphasize in marketing"

### 2. Book Publishing

**Scenario: Title & Cover Testing**
- **Input**: 3 title options, 2 cover designs, book description
- **Personas**: Target readers (genre-specific)
- **Output**:
  - Reading intent scores per variant
  - Title appeal by demographic
  - Cover design preference
  - Genre expectation alignment

**Example**: Mystery Novel
```json
{
  "variants": [
    {
      "title": "The Last Witness",
      "cover": "dark_atmospheric.jpg",
      "description": "A gripping thriller..."
    },
    {
      "title": "Shadows of Testimony",
      "cover": "minimalist_red.jpg",
      "description": "Same description"
    }
  ],
  "target_readers": {
    "genre": "mystery/thriller",
    "age_range": [30, 60],
    "reading_frequency": "1-3 books/month"
  }
}
```

**Results**:
- **Winner**: "The Last Witness" + dark atmospheric cover (4.2 vs 3.5 intent)
- "Title A is 'more intriguing and genre-appropriate' (78% mention)"
- "Cover A 'sets the right mood' for thriller readers"
- "Older readers (50+) prefer straightforward titles"

### 3. Course Material Development

**Scenario: Online Course Positioning**
- **Input**: Course outline, learning objectives, pricing tiers
- **Personas**: Target students (skill level, goals, budget)
- **Output**:
  - Enrollment intent
  - Pricing perception (value vs cost)
  - Content appropriateness
  - Competitive differentiation

**Example**: Web Development Bootcamp
```json
{
  "course_title": "Full-Stack Web Dev in 12 Weeks",
  "outline": "Week 1: HTML/CSS, Week 2: JavaScript...",
  "price_tiers": ["$499 self-paced", "$1499 mentored", "$2999 job guarantee"],
  "target_students": {
    "experience_level": "beginner to intermediate",
    "goal": "career change or upskilling",
    "age_range": [22, 40]
  }
}
```

**Insights**:
- "Mentored tier ($1499) has highest intent (4.5/7) - perceived best value"
- "Concern: 'Pace seems too fast' (40% of beginners) - add prerequisite course"
- "Job guarantee tier appeals to career changers (4.8 intent) but not upskillers (3.2)"
- "Suggestion: Split into beginner/intermediate tracks"

### 4. Advertising Campaigns

**Scenario: Facebook Ad Creative Testing**
- **Input**: 5 ad variants (different headlines, images, CTAs)
- **Personas**: Social media users matching target demo
- **Output**:
  - Click/engagement intent
  - Attention-grabbing score
  - CTA effectiveness
  - Ad fatigue prediction

**Example**: SaaS Product Ad
```json
{
  "variants": [
    {
      "headline": "Boost Productivity by 40% in 30 Days",
      "body": "Join 50,000+ teams...",
      "cta": "Start Free Trial",
      "image": "team_collaboration.jpg"
    },
    {
      "headline": "Stop Wasting Time on Manual Tasks",
      "body": "Automate your workflow...",
      "cta": "See How It Works",
      "image": "automation_graphic.jpg"
    }
  ],
  "platform": "facebook",
  "target_audience": {
    "role": ["manager", "founder", "operations"],
    "company_size": "10-200 employees"
  }
}
```

**Results**:
- **Winner**: Variant 2 (4.1 vs 3.6 engagement intent)
- "Negative framing ('Stop Wasting') more attention-grabbing (82%)"
- "CTA 'See How It Works' feels less committal than 'Free Trial' (73% prefer)"
- "Automation visual more relevant than generic team photo"

### 5. Landing Page Optimization

**Scenario: Homepage Conversion Testing**
- **Input**: Landing page URL or full copy
- **Personas**: Website visitors (traffic source-specific)
- **Output**:
  - Conversion intent (sign-up, purchase)
  - Clarity of value proposition
  - Trust/credibility perception
  - Friction points identified

**Example**: B2B SaaS Landing Page
```json
{
  "url": "https://example.com/pricing",
  "test_elements": [
    "headline",
    "pricing table",
    "social proof section",
    "CTA placement"
  ],
  "visitor_personas": {
    "source": "google search",
    "intent": "evaluating solutions",
    "company_role": "decision maker"
  }
}
```

**Findings**:
- "Conversion intent: 3.8/7 (moderate, needs improvement)"
- "Friction point: Pricing tiers unclear - 45% mention confusion"
- "Social proof section strong (4.6 trust score)"
- "Recommendation: Add comparison table, highlight 'most popular' tier"

---

## Validation & Testing Strategy

### Research Validation (Critical for Credibility)

**Benchmark Testing**:
```python
def validate_against_research_paper():
    """
    Replicate tests from Maier et al. (2024) to validate our implementation.
    """
    # 1. Get sample products from paper (personal care items)
    test_products = load_paper_test_products()
    
    # 2. Generate synthetic responses using our system
    our_results = []
    for product in test_products:
        result = run_test(
            content=product.description,
            personas=generate_personas_matching_paper_demos(),
            sample_size=200
        )
        our_results.append(result)
    
    # 3. Compare to paper's reported results
    paper_results = load_paper_results()
    
    validation_metrics = {
        "correlation_attainment": calculate_correlation_attainment(
            our_results, paper_results
        ),  # Target: >80%
        
        "ks_similarity": calculate_ks_similarity(
            our_results, paper_results
        ),  # Target: >0.85
        
        "mean_absolute_error": calculate_mae(
            our_results, paper_results
        )  # Target: <0.5 on 7-point scale
    }
    
    return validation_metrics
```

**Continuous Validation**:
- Monthly benchmarking against new research
- A/B test predictions vs real user data (when available)
- Track accuracy metrics over time
- Alert if metrics degrade below thresholds

### Unit Testing

```python
# Test SSR algorithm
def test_ssr_mapping():
    response = "I love this product! It's exactly what I needed."
    result = calculate_ssr_score(response, purchase_intent_anchors)
    assert result['rating'] >= 4.0  # Should be high intent
    assert result['confidence'] > 0.7

def test_persona_consistency():
    persona = generate_persona(demographics={"age": 30, "income": "high"})
    # Generate response twice
    r1 = generate_response(persona, test_content)
    r2 = generate_response(persona, test_content)
    # Responses should be similar (embedding similarity >0.8)
    assert cosine_similarity(embed(r1), embed(r2)) > 0.8

def test_anchor_coverage():
    # Ensure we have anchors for all scale points
    for intent_type in ['purchase', 'engagement', 'satisfaction']:
        anchors = get_anchor_sets(intent_type)
        for anchor_set in anchors:
            assert all(i in anchor_set for i in range(1, 8))
```

### Integration Testing

```python
def test_full_pipeline():
    """End-to-end test from content to results."""
    # 1. Create test
    test = create_test(
        content="Test product description",
        personas=["template_persona_1", "template_persona_2"],
        content_type="product"
    )
    
    # 2. Run test
    results = run_test_sync(test.id)
    
    # 3. Validate outputs
    assert len(results.individual_results) == 2
    assert 1.0 <= results.mean_intent <= 7.0
    assert 'key_motivators' in results.qualitative_analysis
    assert results.confidence > 0.5

def test_ab_comparison():
    """Test A/B comparison logic."""
    test_a = run_test(content="Version A", personas=standard_set)
    test_b = run_test(content="Version B", personas=standard_set)
    
    comparison = compare_tests([test_a.id, test_b.id])
    
    assert comparison.winner in [test_a.id, test_b.id]
    assert 0.0 <= comparison.confidence <= 1.0
    assert 'statistical_summary' in comparison
```

### User Acceptance Testing

**Beta Testing Plan** (Week 12-14):
1. Recruit 10-20 diverse beta users:
   - E-commerce businesses (3-5)
   - Authors/publishers (2-3)
   - Course creators (2-3)
   - Marketing agencies (2-3)
   - SaaS companies (2-3)

2. Testing protocol:
   - Each user runs 3-5 tests on real content
   - Collect feedback via structured survey
   - Track: accuracy perception, usability, usefulness
   - Monitor: time to complete test, confusion points

3. Success criteria:
   - 80%+ would use again
   - Average rating >4/5
   - <5 critical bugs
   - Mean time to first test <10 minutes

---

## Technical Challenges & Solutions

### Challenge 1: API Costs at Scale

**Problem**: Testing 100 personas per test = 100+ LLM calls. At $0.01/call, could get expensive.

**Solutions**:
1. **Batching**: Send multiple persona prompts in one API call where possible
   ```python
   # Instead of 100 separate calls
   batched_prompt = """
   Generate responses for these 10 personas:
   Persona 1: {p1_description}
   Persona 2: {p2_description}
   ...
   
   For each, respond to: {content}
   
   Format as JSON array.
   """
   ```

2. **Smart sampling**: Start with 20-30 personas, extrapolate if distribution is clear
   ```python
   if standard_deviation < threshold and n > 30:
       # Distribution is stable, no need for more samples
       break
   ```

3. **Caching**: Reuse persona responses for similar content
   ```python
   cache_key = hash(persona_id + content_hash)
   if redis.exists(cache_key):
       return redis.get(cache_key)
   ```

4. **Model selection**: Use cheaper models (Gemini Flash) for initial screening, expensive (GPT-4o) for final scoring

**Cost Projections**:
- Small test (20 personas): $0.20-0.40
- Medium test (50 personas): $0.50-1.00
- Large test (100 personas): $1.00-2.00
- Still 10-100x cheaper than human surveys ($20-200)

### Challenge 2: Response Consistency & Quality

**Problem**: LLMs sometimes generate inconsistent or unrealistic responses.

**Solutions**:
1. **Temperature tuning**: 0.5-0.7 balances creativity and consistency
2. **Structured prompts**: Include explicit constraints and examples
3. **Validation layer**:
   ```python
   def validate_response(response: str, persona: Dict) -> bool:
       """Check if response is realistic and coherent."""
       checks = [
           len(response) > 20,  # Not too short
           len(response) < 500,  # Not too long
           contains_relevant_keywords(response, persona),
           sentiment_matches_expected(response, persona),
           no_generic_phrases(response)  # e.g., "As an AI..."
       ]
       return all(checks)
   
   # Retry if validation fails (max 3 attempts)
   ```

4. **Ensemble approach**: Generate 3 responses, use median or consensus
5. **Human-in-the-loop**: Flag outliers for manual review

### Challenge 3: Multimodal Content Complexity

**Problem**: Analyzing images, videos requires different models and approaches.

**Solutions**:
1. **Modular architecture**: Separate analyzers per content type
   ```python
   class ContentAnalyzer:
       def analyze(self, content: Content) -> AnalysisResult:
           if content.type == 'text':
               return TextAnalyzer().analyze(content)
           elif content.type == 'image':
               return ImageAnalyzer().analyze(content)  # GPT-4o Vision
           elif content.type == 'video':
               return VideoAnalyzer().analyze(content)  # Extract frames + transcript
           elif content.type == 'multimodal':
               return MultimodalAnalyzer().analyze(content)  # Combine all
   ```

2. **Progressive enhancement**: Start with text-only MVP, add image/video post-launch
3. **Cost management**: Vision API calls are more expensive, offer as premium feature

### Challenge 4: Result Interpretation

**Problem**: Users may not understand what a "3.8 intent score" means.

**Solutions**:
1. **Contextualization**: Always show benchmark or comparison
   ```
   "Score: 3.8/7 (Above average for this category)"
   "This is higher than 65% of similar products we've tested"
   ```

2. **Actionable insights**: Translate numbers to recommendations
   ```
   "3.8 indicates moderate intent. To improve:"
   - Address top objection: unclear pricing (35% mention)
   - Emphasize benefit X (43% found this most appealing)
   ```

3. **Qualitative emphasis**: Show quotes and themes prominently
4. **Visualization**: Use colors (red/yellow/green), icons, progress bars
5. **Tutorials**: Include interpretation guide in documentation

### Challenge 5: Ethical & Bias Concerns

**Problem**: AI personas may reflect LLM biases or stereotypes.

**Solutions**:
1. **Bias auditing**: Regularly check for demographic biases in outputs
   ```python
   def audit_for_bias(results: List[Result]) -> BiasReport:
       """Check if certain demographics are systematically rated differently."""
       # E.g., are female personas always more price-sensitive?
       # Are older personas always more skeptical?
       by_demo = group_results_by_demographics(results)
       bias_indicators = detect_systematic_patterns(by_demo)
       return BiasReport(indicators=bias_indicators)
   ```

2. **Diverse persona sets**: Ensure templates cover wide range, avoid stereotypes
3. **Transparency**: Disclaimer that these are AI simulations, not real people
4. **Human validation**: Recommend users validate critical decisions with real surveys
5. **Fairness constraints**: If bias detected, adjust persona generation prompts

---

## Success Metrics & KPIs

### Technical Performance

**Speed**:
- [ ] Single persona response: <3 seconds
- [ ] 20-persona test: <60 seconds
- [ ] 100-persona test: <5 minutes
- [ ] 99th percentile API latency: <10 seconds

**Accuracy** (validated against research):
- [ ] Correlation attainment: >80%
- [ ] KS similarity: >0.85
- [ ] Mean absolute error: <0.5 on 7-point scale
- [ ] Response consistency (test-retest): >0.80 correlation

**Reliability**:
- [ ] API uptime: >99% during beta
- [ ] Error rate: <2% of tests
- [ ] Data integrity: Zero data loss

**Cost Efficiency**:
- [ ] Average cost per test: $0.50-2.00 (50-100 personas)
- [ ] 95%+ cheaper than human surveys

### Product Metrics (Post-Launch)

**Usage**:
- [ ] Active users: 50+ in first 3 months
- [ ] Tests per user per month: 5+
- [ ] Test completion rate: >85%

**Quality**:
- [ ] User satisfaction: >4/5 average rating
- [ ] Recommendation (NPS): >40
- [ ] Repeat usage rate: >60%

**Engagement**:
- [ ] Time to first test: <10 minutes
- [ ] Features used per session: 3+
- [ ] Return rate: >50% users return within 7 days

---

## Resources & Budget (Development Phase)

### API & Infrastructure Costs (Months 1-3)

**Development & Testing**:
- Claude API: $100-300/month
- OpenAI API (GPT-4o + embeddings): $100-300/month
- Gemini API: $50-100/month
- Voyage AI embeddings: $20-50/month
- **Total AI APIs**: $270-750/month

**Infrastructure**:
- PostgreSQL (Supabase/Railway): $0-25/month (free tier initially)
- Redis (Upstash): $0-10/month (free tier)
- Vector DB (Pinecone): $0-70/month (free tier 100K vectors)
- Frontend hosting (Vercel): $0/month (free tier)
- Backend hosting (Railway/Fly.io): $10-30/month
- **Total Infrastructure**: $10-135/month

**Tools & Services**:
- GitHub (repos, actions): $0/month (free for individuals)
- Monitoring (Sentry, Axiom): $0-50/month (free tiers)
- Auth provider (Clerk/Auth0): $0-25/month (free tier)
- **Total Tools**: $0-75/month

**Grand Total**: $280-960/month during development

### Time Investment

**Solo Developer**:
- 12 weeks full-time (40 hrs/week) = 480 hours
- At $100/hr equivalent = $48,000 opportunity cost
- OR: 6 months part-time (20 hrs/week) = same outcome

**Small Team (2 people)**:
- 6-8 weeks to MVP
- Developer 1: Backend + AI
- Developer 2: Frontend + UX

### Knowledge Requirements

**Must Have**:
- Python (FastAPI, async programming)
- React + TypeScript
- API integration (REST, async)
- SQL and database design
- Basic machine learning concepts
- Prompt engineering

**Nice to Have**:
- LLM fine-tuning experience
- Statistics and A/B testing
- UX design skills
- DevOps (Docker, CI/CD)

**Learning Resources** (if needed):
- FastAPI tutorial: 10 hours
- LangChain/LiteLLM docs: 5 hours
- Prompt engineering guide: 5 hours
- Research paper deep-dive: 3 hours
- **Total**: ~25 hours of learning

---

## Future Enhancements (Post-MVP Roadmap)

### Phase 2: Enhanced Capabilities (Months 4-6)

1. **Multimodal Support**
   - Image analysis (product photos, book covers, ads)
   - Landing page screenshot analysis
   - Video thumbnail evaluation

2. **Batch Testing**
   - Test 5-10 variants simultaneously
   - Automated winner selection
   - Recommendation engine for optimization

3. **Advanced Analytics**
   - Historical trending across tests
   - Category benchmarks (compare to industry)
   - Predictive revenue modeling

4. **Custom Personas**
   - User-created persona library
   - Import from customer data/surveys
   - Persona builder wizard

5. **Integrations**
   - Shopify plugin
   - WordPress/WooCommerce
   - Email marketing platforms (Mailchimp)
   - Export to Google Sheets

### Phase 3: Scale & Intelligence (Months 7-12)

1. **Real-Time Testing**
   - Webhook for continuous testing
   - Monitor and alert on intent drops
   - Auto-optimization suggestions

2. **Machine Learning Layer**
   - Learn from historical tests
   - Custom model fine-tuning per industry
   - Predictive analytics (forecast success)

3. **Collaborative Features**
   - Team workspaces
   - Commenting and annotations
   - Approval workflows

4. **API & Developer Platform**
   - Public API for integrations
   - Webhook system
   - SDK (Python, JavaScript)

5. **International Expansion**
   - Multi-language support
   - Cultural persona adaptation
   - Regional benchmarks

### Phase 4: Enterprise & Scale (Year 2+)

1. **Enterprise Features**
   - SSO and advanced permissions
   - Custom security/compliance
   - Dedicated infrastructure
   - White-label options

2. **Advanced AI**
   - Custom LLM fine-tuning per client
   - Proprietary persona models
   - Real-time A/B test optimization
   - Generative content suggestions

3. **Platform Ecosystem**
   - Marketplace for custom personas
   - Third-party integrations
   - Partner agency program

---

## Key Decisions Before Starting

### Technical Decisions

1. **Primary LLM Provider**
   - [ ] Claude Sonnet 4.5 (extended context, reasoning) ✅ Recommended for MVP
   - [ ] GPT-4o (multimodal, proven accuracy)
   - [ ] Gemini 2.0 Flash (cost/speed balance)
   - **Decision**: Start with Claude, add GPT-4o for vision later

2. **Embedding Provider**
   - [ ] Voyage AI (research-grade quality, $0.12/1M tokens) ✅ Recommended
   - [ ] OpenAI text-embedding-3-small (proven, $0.02/1M tokens)
   - **Decision**: Voyage for SSR, OpenAI fallback

3. **Vector Database**
   - [ ] Pinecone (managed, free tier for 100K vectors) ✅ Recommended for MVP
   - [ ] pgvector (PostgreSQL extension, self-hosted)
   - **Decision**: Pinecone for simplicity, migrate to pgvector if cost becomes issue

4. **Hosting**
   - [ ] Vercel (frontend) + Railway (backend) ✅ Recommended
   - [ ] All-in-one: Render or Fly.io
   - **Decision**: Vercel + Railway for simplicity and free tiers

5. **Authentication**
   - [ ] Clerk (modern, easy integration) ✅ Recommended
   - [ ] Auth0 (enterprise-grade)
   - [ ] Roll your own (Firebase Auth)
   - **Decision**: Clerk for MVP speed

### Product Decisions

1. **MVP Scope**
   - [x] Text-only content analysis (no images/video)
   - [x] 30 pre-built personas (no custom creation in MVP)
   - [x] Purchase intent + engagement intent (expand later)
   - [x] Basic A/B testing (2 variants)
   - [ ] Historical tracking (nice-to-have, could be MVP)

2. **Pricing Model** (for beta)
   - [ ] Completely free during beta (3 months)
   - [ ] Freemium: 10 tests/month free, pay per test after
   - [ ] Early bird: $19/month unlimited tests
   - **Decision**: TBD based on feedback

3. **Beta User Selection**
   - Target: 15-20 users across diverse industries
   - Recruit via: Product Hunt, Reddit (r/entrepreneur, r/marketing), LinkedIn
   - Incentive: Free lifetime access if provide detailed feedback

---

## Conclusion & Next Steps

This v3.0 plan synthesizes the best ideas from three previous iterations:
- **v2.0**: Practical 12-week development timeline
- **GLM**: Comprehensive use cases and multi-LLM architecture
- **Grok**: Research-grounded SSR methodology

### What Makes This Plan Strong

1. **Research-Validated**: Built on peer-reviewed methodology with proven 92% correlation
2. **Technically Detailed**: SSR algorithm, prompt templates, database schemas ready to implement
3. **Practical Timeline**: 12 weeks to working MVP with clear weekly milestones
4. **Multi-Modal Ready**: Architecture supports text now, images/video later
5. **Cost-Conscious**: Caching strategies and smart sampling to control API costs
6. **Validation-First**: Benchmarking against research to ensure accuracy

### Immediate Next Steps

**Week 0: Setup** (Before Week 1)
1. [ ] Secure API access (Anthropic, OpenAI, Voyage AI)
2. [ ] Create GitHub organization and repos
3. [ ] Set up Vercel and Railway accounts
4. [ ] Register domain name (if needed)
5. [ ] Set up project management (Linear, GitHub Projects)

**Week 1: Day 1 Tasks**
1. [ ] Clone starter templates (FastAPI + React)
2. [ ] Configure environment variables
3. [ ] Test API connections (Claude, embeddings)
4. [ ] Set up database (PostgreSQL)
5. [ ] Create first prompt template
6. [ ] Build "Hello World" test (1 persona, 1 product)

**Beta Launch Checklist** (Week 12)
1. [ ] 10 example tests covering all use cases
2. [ ] Documentation: getting started guide
3. [ ] 3 tutorial videos (5 min each)
4. [ ] Feedback form integrated
5. [ ] Monitoring and alerting configured
6. [ ] 15-20 beta users recruited and onboarded

### Success Criteria (3 Months Post-Launch)

**Must Achieve**:
- [ ] 50+ active users
- [ ] >4.0/5.0 user satisfaction
- [ ] >80% correlation with real data (where available)
- [ ] <3% critical error rate
- [ ] Self-sustaining (revenue covers API costs)

**Stretch Goals**:
- [ ] 100+ active users
- [ ] Featured on Product Hunt (top 5 of the day)
- [ ] 10+ case studies/testimonials
- [ ] Partnership with 1-2 platforms (Shopify, WordPress)
- [ ] Media coverage (TechCrunch, Hacker News)

---

**The Bottom Line**: This system democratizes market research by making it 100x cheaper and 100x faster while maintaining research-grade accuracy. By implementing the proven SSR methodology and focusing on a tight MVP scope, we can ship a valuable product in 12 weeks and iterate based on real user feedback.

**Let's build this!** 🚀
