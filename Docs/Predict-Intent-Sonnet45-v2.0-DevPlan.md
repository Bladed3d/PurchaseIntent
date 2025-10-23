# Predict Intent Sonnet 4.5: Development Plan v2.0

**Document Version**: 2.0  
**Last Updated**: January 2025  
**Focus**: Technical Development & MVP Implementation  
**Status**: Planning Phase

---

## Overview

This document outlines the technical development plan for building an AI-powered system that tests products, books, course materials, advertising, and landing pages to predict customer purchase intent. Based on research showing LLMs achieve 92% correlation with human purchase intent ratings, this system uses Claude Sonnet 4.5 to generate synthetic consumer responses.

**Core Concept**: Instead of surveying real people (slow, expensive), use AI to simulate diverse consumer personas and predict their purchase intent based on your content.

---

## Why Claude Sonnet 4.5?

- **Extended Context**: 200K+ tokens - can analyze entire landing pages, long product descriptions, or full course outlines
- **Superior Reasoning**: Better at understanding nuanced consumer behavior and purchase motivations
- **Consistent Output**: Reliable, reproducible results with strong instruction following
- **JSON Mode**: Native structured output makes integration easier
- **Cost Effective**: Good balance of quality and API costs

---

## System Architecture

### High-Level Components

```
┌─────────────────────────────────────────────────────────┐
│                    Web Interface                        │
│            (Upload content, configure tests)            │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│                  API Gateway                            │
│         (Authentication, rate limiting, routing)        │
└────────────────┬────────────────────────────────────────┘
                 │
        ┌────────┴─────────┬──────────────────┐
        │                  │                  │
┌───────▼────────┐  ┌──────▼──────┐  ┌───────▼──────────┐
│   Content      │  │  Synthetic  │  │    Intent        │
│   Analysis     │  │  Consumer   │  │   Prediction     │
│   Engine       │  │  Generator  │  │   Module         │
└───────┬────────┘  └──────┬──────┘  └───────┬──────────┘
        │                  │                  │
        └──────────────────┴──────────────────┘
                           │
                  ┌────────▼─────────┐
                  │  Claude Sonnet   │
                  │    4.5 API       │
                  └──────────────────┘
```

### Technology Stack

**Backend**
- **Language**: Python 3.11+
- **Framework**: FastAPI (async, fast, auto-docs)
- **Database**: PostgreSQL (tests, results, personas)
- **Cache**: Redis (frequently used personas, recent results)
- **Queue**: Celery with Redis (async processing for large tests)

**Frontend**
- **Framework**: React 18+ with TypeScript
- **UI Library**: Tailwind CSS + shadcn/ui components
- **State Management**: Zustand or React Query
- **Charts**: Recharts for visualizations

**AI/ML**
- **Primary LLM**: Claude Sonnet 4.5 via Anthropic API
- **Embeddings**: Voyage AI API (for semantic similarity)
- **Vector Storage**: Pinecone (free tier to start)

**DevOps**
- **Hosting**: Vercel (frontend), Railway or Fly.io (backend)
- **Environment**: Docker for local development
- **Version Control**: Git + GitHub

---

## Core Features (MVP)

### 1. Content Analysis
**What it does**: Extracts key elements from content to test

**Input Types** (Start with these)
- Product descriptions (text)
- Ad copy (headline + body + CTA)
- Landing page copy (paste or URL)

**Analysis Output**
- Main value proposition
- Key features/benefits mentioned
- Emotional tone
- Call-to-action strength
- Overall clarity score

### 2. Synthetic Consumer Generation
**What it does**: Creates realistic consumer personas with specific characteristics

**Persona Attributes**
- Demographics: age, gender, income level, education
- Psychographics: values, interests, pain points
- Behavioral: shopping habits, decision-making style
- Context: awareness level of product category

**Persona Library** (Start with 20-30 templates)
- Budget-conscious shoppers
- Premium buyers
- Early adopters
- Skeptical researchers
- Impulse buyers
- Value seekers

### 3. Intent Prediction
**What it does**: Predicts purchase intent on 1-7 scale

**Process**
1. Show content to synthetic persona
2. Get detailed reasoning about purchase decision
3. Extract purchase intent rating (1-7 Likert scale)
4. Calculate confidence score
5. Identify main objections or motivations

**Output for Each Persona**
```json
{
  "persona_id": "budget_conscious_millennial_f_25-34",
  "purchase_intent": 5,
  "confidence": 0.82,
  "reasoning": "The product addresses my need for...",
  "key_motivators": ["price point", "features"],
  "key_objections": ["unclear warranty", "shipping time"],
  "emotional_response": "interested but cautious"
}
```

### 4. Results Dashboard
**What it shows**
- Overall intent score (average across all personas)
- Distribution chart (how many 1s, 2s, 3s, etc.)
- Segment breakdown (by demographics)
- Key insights and patterns
- Top objections across all personas
- Strongest motivators

### 5. A/B Testing
**What it does**: Compare two versions of content

**Features**
- Side-by-side comparison
- Statistical significance calculation
- Highlight which version performs better per segment
- Identify what changed and its impact

---

## Development Phases

### Phase 1: Foundation (Weeks 1-3)

**Week 1: Core Infrastructure**
- [ ] Set up project structure (backend + frontend repos)
- [ ] Configure Claude API integration
- [ ] Create basic prompt templates for persona generation
- [ ] Set up database schema (users, tests, results, personas)
- [ ] Implement authentication (simple email/password to start)

**Week 2: Persona System**
- [ ] Create 20 base persona templates
- [ ] Build persona generator using Claude
- [ ] Implement persona storage and retrieval
- [ ] Test persona consistency and realism
- [ ] Create persona customization interface

**Week 3: Content Analysis**
- [ ] Build content parser for product descriptions
- [ ] Build content parser for ad copy
- [ ] Implement basic analysis (extract features, tone, etc.)
- [ ] Test with sample content
- [ ] Create content submission UI

### Phase 2: Intent Prediction Engine (Weeks 4-6)

**Week 4: Basic Prediction**
- [ ] Design prompt template for intent prediction
- [ ] Implement Claude API calls with structured output
- [ ] Parse and validate responses
- [ ] Calculate intent scores
- [ ] Store results in database

**Week 5: Scoring & Validation**
- [ ] Implement Likert scale mapping
- [ ] Add confidence scoring
- [ ] Extract reasoning and objections
- [ ] Test with various content types
- [ ] Validate consistency across runs

**Week 6: Results Processing**
- [ ] Aggregate results across multiple personas
- [ ] Calculate statistics (mean, median, distribution)
- [ ] Identify patterns and insights
- [ ] Generate summary recommendations
- [ ] Build results API endpoints

### Phase 3: User Interface (Weeks 7-9)

**Week 7: Dashboard Setup**
- [ ] Create dashboard layout
- [ ] Build test creation wizard
- [ ] Implement content input forms
- [ ] Create persona selection interface
- [ ] Add basic navigation

**Week 8: Results Visualization**
- [ ] Build intent distribution chart
- [ ] Create segment comparison views
- [ ] Show individual persona responses
- [ ] Display key insights cards
- [ ] Add export functionality (PDF/CSV)

**Week 9: Polish & UX**
- [ ] Add loading states and progress indicators
- [ ] Implement error handling and user feedback
- [ ] Create onboarding tutorial
- [ ] Add sample tests for demo
- [ ] Mobile responsive design

### Phase 4: A/B Testing & Refinement (Weeks 10-12)

**Week 10: A/B Testing**
- [ ] Build variant comparison interface
- [ ] Implement side-by-side testing
- [ ] Calculate statistical significance
- [ ] Create comparison visualizations
- [ ] Add winner recommendation logic

**Week 11: Testing & Bug Fixes**
- [ ] End-to-end testing with real content
- [ ] Fix bugs and edge cases
- [ ] Optimize API usage and costs
- [ ] Improve response times
- [ ] Add rate limiting

**Week 12: Launch Preparation**
- [ ] Write documentation
- [ ] Create example tests and tutorials
- [ ] Set up monitoring and logging
- [ ] Configure production environment
- [ ] Beta testing with 5-10 users

---

## Technical Implementation Details

### Persona Generation Prompt Template

```python
persona_prompt = """You are helping create a realistic synthetic consumer persona.

Generate a detailed persona with these characteristics:
- Demographics: {demographics}
- Psychographics: {psychographics}
- Behavioral traits: {behavioral}

Return a JSON object with:
{
  "name": "descriptive name",
  "age": 35,
  "gender": "female",
  "income_level": "middle",
  "education": "bachelor's degree",
  "location": "suburban area",
  "values": ["convenience", "quality", "family"],
  "pain_points": ["time constraints", "budget limits"],
  "shopping_style": "researcher",
  "decision_factors": ["reviews", "price", "features"],
  "personality": "practical and detail-oriented"
}

Make this persona realistic and internally consistent."""
```

### Intent Prediction Prompt Template

```python
intent_prompt = """You are {persona_name}, a {persona_age}-year-old {persona_gender} 
who values {persona_values}. Your shopping style is {persona_shopping_style}.

You encounter this product/content:
{content}

Evaluate your purchase intent on a scale of 1-7:
1 = Definitely will not buy
2 = Very unlikely to buy
3 = Unlikely to buy
4 = Might or might not buy
5 = Likely to buy
6 = Very likely to buy
7 = Definitely will buy

Return a JSON object:
{
  "purchase_intent": 5,
  "reasoning": "detailed explanation of your decision",
  "key_motivators": ["list", "of", "positive factors"],
  "key_objections": ["list", "of", "concerns"],
  "emotional_response": "your emotional reaction",
  "confidence": 0.85
}

Think step-by-step about how this persona would genuinely respond."""
```

### Database Schema (Core Tables)

```sql
-- Users
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Personas
CREATE TABLE personas (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  name VARCHAR(255),
  demographics JSONB,
  psychographics JSONB,
  behavioral JSONB,
  is_template BOOLEAN DEFAULT false,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Tests
CREATE TABLE tests (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  name VARCHAR(255),
  content_type VARCHAR(50),
  content TEXT,
  status VARCHAR(50),
  created_at TIMESTAMP DEFAULT NOW()
);

-- Results
CREATE TABLE results (
  id UUID PRIMARY KEY,
  test_id UUID REFERENCES tests(id),
  persona_id UUID REFERENCES personas(id),
  purchase_intent INTEGER,
  confidence DECIMAL,
  reasoning TEXT,
  motivators JSONB,
  objections JSONB,
  emotional_response TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### API Structure

```
POST   /api/tests              # Create new test
GET    /api/tests              # List all tests
GET    /api/tests/:id          # Get test details
POST   /api/tests/:id/run      # Execute test
GET    /api/tests/:id/results  # Get test results

GET    /api/personas           # List personas
POST   /api/personas           # Create custom persona
GET    /api/personas/:id       # Get persona details

POST   /api/content/analyze    # Analyze content
POST   /api/compare            # A/B comparison
```

---

## MVP Feature Priority

### Must Have (Launch Blockers)
1. ✅ Content input (text-based: product descriptions, ad copy)
2. ✅ 20 pre-built persona templates
3. ✅ Intent prediction (1-7 scale with reasoning)
4. ✅ Basic results dashboard
5. ✅ Single test execution

### Should Have (Post-MVP, Week 13-16)
6. A/B testing comparison
7. Custom persona creation
8. Landing page URL analysis
9. Historical test tracking
10. Export results (PDF/CSV)

### Nice to Have (Future Iterations)
11. Image analysis (book covers, product photos)
12. Advanced analytics and trends
13. Team collaboration features
14. API access for integrations
15. Batch testing multiple variants

---

## Technical Challenges & Solutions

### Challenge 1: API Costs
**Problem**: Claude API calls can get expensive at scale

**Solutions**:
- Cache persona definitions (don't regenerate each time)
- Batch multiple personas in single API call when possible
- Start with smaller persona sets (5-10 per test)
- Implement request queuing to avoid rate limits
- Use cheaper models for content analysis, Claude for predictions

### Challenge 2: Response Consistency
**Problem**: LLMs can give different answers for same input

**Solutions**:
- Set temperature to 0.3-0.5 for more consistent results
- Use detailed, structured prompts
- Include few-shot examples in prompts
- Validate outputs against expected schema
- Average across multiple runs for critical tests

### Challenge 3: Result Validation
**Problem**: How do we know predictions are accurate?

**Solutions**:
- Start with validation dataset (compare to real survey data)
- Test with well-known products/ads (benchmark against market data)
- A/B test against real campaigns when possible
- Track prediction accuracy over time
- Be transparent about confidence levels

### Challenge 4: Speed
**Problem**: Testing 20 personas might take 30-60 seconds

**Solutions**:
- Show progress bar with real-time updates
- Process personas in parallel (async)
- Show results as they come in (don't wait for all)
- Implement background processing for large tests
- Cache frequent test scenarios

---

## Cost Estimates (Development)

### API Costs (Monthly, assuming moderate testing)
- Claude Sonnet 4.5: ~$50-200/month (development)
- Voyage AI embeddings: ~$10-30/month
- Total: ~$60-230/month during development

### Infrastructure Costs (Monthly)
- Database hosting (PostgreSQL): $0-25 (start with free tier)
- Redis: $0-10 (free tier initially)
- Frontend hosting: $0 (Vercel free tier)
- Backend hosting: $5-20 (Railway or Fly.io)
- Total: ~$5-55/month

### Development Time
- Solo developer: 12 weeks (full-time) to MVP
- With team of 2: 6-8 weeks to MVP

---

## Testing Strategy

### Unit Tests
- Persona generation validation
- Content parsing accuracy
- Intent score calculation
- API response handling

### Integration Tests
- Full test execution flow
- Database operations
- API endpoint functionality
- Authentication and authorization

### User Testing
- 5-10 beta users testing real content
- Gather feedback on UI/UX
- Validate result usefulness
- Identify edge cases and bugs

### Validation Testing
- Compare predictions to known outcomes
- Test with successful vs failed products
- Benchmark against traditional surveys (if available)
- Measure prediction-to-reality correlation

---

## Security & Privacy Considerations

### Data Protection
- Encrypt content at rest (database encryption)
- Encrypt in transit (HTTPS/TLS)
- Don't store unnecessary sensitive data
- Implement automatic data deletion policies

### API Security
- API key authentication
- Rate limiting per user
- Input validation and sanitization
- SQL injection prevention (use ORMs)

### User Privacy
- Don't share user content with third parties
- Allow users to delete their data
- Clear privacy policy
- Optional anonymous usage

---

## Success Metrics (Technical)

### Performance
- [ ] API response time < 3 seconds per persona
- [ ] Full test (20 personas) completes in < 60 seconds
- [ ] 99% uptime during beta
- [ ] Zero critical security vulnerabilities

### Quality
- [ ] Persona responses are realistic and consistent
- [ ] Intent scores correlate with expected outcomes
- [ ] Results provide actionable insights
- [ ] User feedback rating > 4/5

### Usability
- [ ] Users can complete a test in < 5 minutes
- [ ] No onboarding required for basic features
- [ ] Clear error messages and recovery paths
- [ ] Mobile-friendly interface

---

## Next Steps

1. **Set up development environment** (Day 1)
   - Create GitHub repos
   - Set up local Docker environment
   - Get Claude API access
   - Configure development tools

2. **Build Hello World** (Day 2-3)
   - Single persona + single content test
   - Validate Claude integration works
   - Confirm basic flow end-to-end

3. **Iterate rapidly** (Weeks 1-12)
   - Focus on one feature at a time
   - Test frequently with real content
   - Gather feedback continuously
   - Ship early and often

4. **Launch private beta** (Week 13)
   - Invite 10-15 friendly users
   - Provide white-glove support
   - Collect detailed feedback
   - Iterate based on learnings

---

## File Structure

```
predict-intent/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── tests.py
│   │   │   ├── personas.py
│   │   │   └── results.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── database.py
│   │   ├── services/
│   │   │   ├── claude_service.py
│   │   │   ├── persona_service.py
│   │   │   ├── content_service.py
│   │   │   └── prediction_service.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── persona.py
│   │   │   ├── test.py
│   │   │   └── result.py
│   │   └── main.py
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── TestCreator.tsx
│   │   │   ├── PersonaSelector.tsx
│   │   │   └── ResultsView.tsx
│   │   ├── services/
│   │   │   └── api.ts
│   │   ├── types/
│   │   │   └── index.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
│
└── docs/
    ├── API.md
    ├── SETUP.md
    └── USAGE.md
```

---

## Future Enhancements (Post-MVP)

### Phase 2 (Months 4-6)
- Landing page URL scraping and full analysis
- Image analysis (product photos, book covers, ads)
- Batch testing (test 10 variants at once)
- Historical tracking and trends
- Advanced persona customization

### Phase 3 (Months 7-12)
- Video content analysis (transcripts + visual)
- Predictive analytics and recommendations
- Automated optimization suggestions
- Team collaboration features
- Integration APIs (Shopify, WordPress, etc.)

### Phase 4 (Year 2)
- Real-time continuous testing
- Machine learning on historical results
- Custom model fine-tuning per industry
- White-label options
- Mobile apps

---

## Key Decisions to Make

### Before Starting Development
- [ ] Choose hosting providers (Vercel + Railway vs others?)
- [ ] Decide on authentication method (Auth0 vs roll your own?)
- [ ] Select vector database (Pinecone vs alternatives?)
- [ ] Determine initial pricing model (affects feature access)
- [ ] Define MVP scope precisely (which features absolutely must be included?)

### During Development
- [ ] How many personas per test in free tier?
- [ ] Should we allow custom personas in MVP?
- [ ] Real-time results or batch processing?
- [ ] How much to cache vs regenerate?
- [ ] What analytics to track?

---

## Resources Needed

### Development Tools
- Claude API access ($100-500/month budget)
- Voyage AI API access ($50-100/month budget)
- GitHub account (free)
- Vercel account (free tier)
- Railway/Fly.io account ($5-20/month)
- Design tools (Figma free tier)

### Knowledge Requirements
- Python + FastAPI experience
- React + TypeScript experience
- PostgreSQL/SQL knowledge
- API design and REST principles
- Basic prompt engineering
- UI/UX design basics

### Time Commitment
- Full-time: 12 weeks to MVP
- Part-time (20hrs/week): 24 weeks to MVP
- With 2 developers: 6-8 weeks to MVP

---

## Conclusion

This development plan focuses on building a functional MVP in 12 weeks that demonstrates the core value proposition: fast, affordable purchase intent testing using AI-powered synthetic consumers. By keeping the initial scope focused and prioritizing the essential features, we can validate the concept quickly and iterate based on real user feedback.

**Key Success Factors**:
1. Start simple - text-based content only
2. Build working end-to-end flow first
3. Test with real content frequently
4. Get user feedback early and often
5. Focus on accuracy and usability over features

**The Goal**: Ship a working product that 10-20 beta users find genuinely useful for testing their products, ads, and landing pages. Everything else can wait.
