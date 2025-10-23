# Complete Guide to Factory Droid Agents
## Mastering Specialized AI Sub-agents for Production Development

---

## Table of Contents
1. [Introduction & Philosophy](#introduction--philosophy)
2. [Droid Anatomy & Structure](#droid-anatomy--structure)
3. [Curtis's Design Principles](#curtiss-design-principles)
4. [The 29 Droid Compendium](#the-29-droid-compendium)
5. [Creation Framework](#creation-framework)
6. [Predict Intent GLM Application](#predict-intent-glm-application)
7. [Advanced Usage Patterns](#advanced-usage-patterns)
8. [Practical Integration Guide](#practical-integration-guide)
9. [Troubleshooting & Optimization](#troubleshooting--optimization)

---

## Introduction & Philosophy

### What Are Factory Droids?

Factory Droids are hyper-specialized AI sub-agents that embody a fundamental shift from generic assistants to **trust-delegated experts**. Unlike traditional prompts that say "think hard and code well," droids are **context-rich specialists** with surgical precision in specific domains.

> **The key insight from John Curtis**: "Building subagents isn't about writing better prompts. It's about teaching them context they couldn't have known. It's about curating their knowledge sources, giving them location awareness, making them team-aware, and letting them critique your architecture."

### Why Droids Transform Development

**Traditional Approach**:
- Generic coding assistants
- Vague instructions
- Repetitive context explanations
- Constant manual guidance

**Droid Approach**:
- Domain-specific expertise
- Forced context and constraints
- Autonomous problem-solving
- Production-ready implementations

**Real Results**: Curtis's 4-4.5M token session achieved:
- 1.5 hours of autonomous coding
- Production-ready Cloudflare Worker deployment
- All tests passing
- Zero manual intervention except API keys

### Alternative Perspectives & Research Insights

Beyond Curtis's approach, broader research reveals additional patterns and philosophies:

#### **Academic Research Pattern**: Mixture-of-Experts (MoE) at Agent Level
Research shows that applying Mixture-of-Experts principles to multi-agent systems enables **selective activation** of specialized agents, similar to how MoE activates relevant experts in LLMs. This approach:
- Reduces computational overhead by activating only relevant specialists
- Enables both hierarchical and flat structures
- Scales intelligence efficiently by focusing expertise

**Key Components from Research**:
1. **Prompt**: Blueprint for goals and constraints
2. **Memory**: Knowledge base for learning from interactions  
3. **Tools**: Specialized capabilities for specific tasks

#### **Community Evolution: From Solo Agents to Orchestras**
The evolution from early agents (AutoGPT, BabyAGI) to sophisticated systems shows:

**Why Single Agents Hit Walls**:
- **Tool Scalability**: LLMs struggle with >10 tools at once
- **Context Pollution**: Irrelevant intermediate steps overwhelm context
- **Jack of All Trades**: Need true specialists for complex tasks

**Multi-Agent Benefits**:
- **Divide and Conquer**: Each agent handles manageable tool sets
- **Easy Maintenance**: Fix individual components without system disruption
- **Specialized Expertise**: Tailored agents for specific capabilities
- **Predictable Flow**: More control over execution patterns

#### **Alternative Architectural Patterns** (from SuperAGI research)

1. **Router Pattern**: Simple receptionist that forwards to best agent
2. **Agents as Tools**: Project manager with specialist interns  
3. **Supervisor Pattern**: Shared context among all team members
4. **Coordinator Pattern**: Democratic approach where agents propose solutions
5. **Network Pattern**: Flat hierarchy (used by CrewAI, Microsoft Autogen, OpenAI Swarm)
6. **Hierarchical Pattern**: Corporate structure with layered management
7. **Custom Patterns**: Purpose-built for specific use cases

**Criticique of Network Pattern**: While flexible, it's:
- Less predictable in execution flow
- More expensive (agent chatter adds up)
- Slower to complete tasks

#### **Communication Paradigms**

**1. Tool Call Parameters**: Child agents work "blind" - only see explicitly passed data
**2. Shared Context**: More flexible collaboration - agents see full history and context

Research shows **shared context** generally works better for informed decision-making, but requires careful design to prevent interference.

---

## Droid Anatomy & Structure

### Standard Front Matter

Every droid follows a consistent structure:

```yaml
---
name: specialized-droid-name
description: Clear purpose statement with trigger conditions
model: gpt-5 | inherit
tools: [specific, tool, list]
createdAt: "2025-10-10T18:28:24.950Z"
updatedAt: "2025-10-10T18:28:24.950Z"
---
```

### Core Components

1. **Project-Specific Context** - Deep domain knowledge
2. **Precise Mission Statement** - Exact responsibilities  
3. **Technology Stack Definition** - Specific tools and frameworks
4. **Implementation Patterns** - Code templates and algorithms
5. **Guardrails & Constraints** - Operational boundaries
6. **Success Criteria** - Measurable outcomes
7. **Integration Points** - How it works with other droids

### Example: Similarity Math Tactician

This droid exemplifies the hyper-specific approach:

```typescript
// NOT: "Implement vector math"
// BUT: "Handle Float32Array operations for OpenAI embeddings with exact formulas"

interface Scores {
  score_dot: number        // dot(v_presented, v_item)
  score_cosine: number     // Same as score_dot (unit norm assumption)
  similarity_0to1: number  // 0.5 * (score_cosine + 1)
  distance_cosine: number  // 1 - score_cosine
}

// Exact formula from SCOPE.md lines 142-146
const score_dot = dot(v_presented, v_item);
const score_cosine = score_dot; // Because vectors are unit length
const similarity_0to1 = 0.5 * (score_cosine + 1);
const distance_cosine = 1 - score_cosine;
```

**Key differences from generic approaches**:
- Specifies exact algorithms (not "implement similarity")
- Performance constraints (Float32Array for Workers)
- Defensive programming thresholds (1e-3, 1e-5)
- Project-specific formulas from scope documents

---

## Curtis's Design Principles

### 1. Context Over Prompts

> "Context is King: The more specific context you provide, the better the output"

**Generic Approach**:
```prompt
You are a web developer. Build me a React component.
```

**Droid Approach**:
```yaml
# Project-Specific Context
This Cloudflare Worker API generates "writing style DNA" profiles with:
- Modular parsers (Exa, Firecrawl, Jina)  
- OpenAI Responses API integration
- Neon PostgreSQL caching
- tRPC endpoints with type safety

# Tech Stack
- Runtime: Cloudflare Workers (ESM modules)
- Framework: Hono
- API Layer: tRPC
- Database: Neon PostgreSQL
```

### 2. Constraints Enable Creativity

**Instead of**: "Make it efficient"
**Provide**: Exact performance requirements, memory limits, algorithm constraints

**Example from Cloudflare Worker droid**:
```yaml
Implementation Constraints:
- Use Float32Array exclusively (32-bit floats for speed)
- Handle zero vectors: throw error if magnitude < 1e-5
- Defensive normalization: if norm deviates from 1.0 by > 1e-3
- Use simple loops over reduce() in hot paths
```

### 3. Sub-agents are Specialists

Each droid has **one domain expertise**:
- `similarity-math-tactician` → Vector mathematics
- `embeddings-provider-strategist` → Embedding provider abstraction  
- `content-parser-architect` → Multi-provider content parsing
- `research-orchestrator` → Parallel.ai task management

### 4. Production-Ready Patterns

**Not**: Tutorial examples
**But**: Real-world implementations

**Example from Research Orchestrator**:
```typescript
// Webhook verification with standard-webhooks spec
function verifyWebhookSignature(
  payload: string,
  signature: string | null,
  secret: string
): boolean {
  // Extract timestamp and signatures from header
  // Format: "v1,timestamp,signature1 v1,timestamp,signature2"
  const signatures = signature.split(' ');
  
  // Verify timestamp is recent (within 5 minutes)
  const timestampMs = parseInt(timestamp) * 1000;
  if (Date.now() - timestampMs > 5 * 60 * 1000) continue;
  
  // Compute expected signature
  const signedPayload = `${timestamp}.${payload}`;
  const expectedHash = crypto
    .createHmac('sha256', secret)
    .update(signedPayload)
    .digest('hex');
}
```

### 5. Continuous Improvement Cycle

From Curtis's workflow:
1. After each coding session, ask main agent: "How could sub-agents improve?"
2. Each droid writes concerns to separate files
3. Review and approve ~80% of improvements
4. Iteratively refine droid definitions

---

## The 29 Droid Compendium

### 🔐 Authentication & Security

| Droid | Specialty | Use When... |
|-------|-----------|-------------|
| **access-identity-guard** | Clerk/Velt identity mapping | Implementing user authentication, RLS policies |
| **compliance-style-gate** | Style guide enforcement | Validating code against compliance rules |

### ☁️ Infrastructure & Deployment  

| Droid | Specialty | Use When... |
|-------|-----------|-------------|
| **cloudflare-worker-deployment-specialist** | Wrangler config, Workers deployment | Setting up Cloudflare Workers, edge optimization |
| **wrangler-scaffold-architect** | Cloudflare Workers project scaffolding | Creating new Worker projects |
| **neon-drizzle-cache-engineer** | Neon PostgreSQL caching with Drizzle ORM | Building database caches, hit tracking |

### 🔄 API & Integration

| Droid | Specialty | Use When... |
|-------|-----------|-------------|
| **content-parser-architect** | Multi-provider content parsing | Implementing Exa/Firecrawl/Jina parsers |
| **trpc-hono-integrator** | tRPC + Hono integration | Building type-safe APIs |
| **openai-llm-strategist** | OpenAI API integration | LLM implementation, prompt management |

### 🎨 Content & Media

| Droid | Specialty | Use When... |
|-------|-----------|-------------|
| **image-job-orchestrator** | Long-running image generation | Managing DALL-E/Imagen jobs, webhook handling |
| **image-prompt-architect** | Image prompt engineering | Crafting optimized image prompts |
| **image-feedback-interpreter** | Image annotation workflows | Handling image feedback, regeneration |

### 📊 Data & Database

| Droid | Specialty | Use When... |
|-------|-----------|-------------|
| **data-model-steward** | Neon schema design | Designing database schemas, migrations |
| **schema-fusion-engineer** | Multi-source data fusion | Merging schemas, resolving conflicts |
| **versioning-snapshot-gatekeeper** | Version control management | Managing snapshots, rollback strategies |

### 🔍 Research & Analysis

| Droid | Specialty | Use When... |
|-------|-----------|-------------|
| **research-orchestrator** | Parallel.ai research management | Long-running research tasks, webhook handling |
| **research-summarizer** | Research synthesis | Summarizing research outputs, extracting insights |
| **embeddings-provider-strategist** | Vector embeddings strategy | Choosing embedding providers, vector search |
| **similarity-math-tactician** | Vector mathematics | Implementing similarity algorithms |

### ✍️ Writing & Editing

| Droid | Specialty | Use When... |
|-------|-----------|-------------|
| **revision-planner** | Content revision planning | Planning Tiptap revisions, tracking changes |
| **rewrite-executor** | Automated content rewrites | Executing content updates, applying operations |
| **comment-canonicalizer** | Comment standardization | Enforcing comment style across codebase |

### 🔬 Quality & Testing

| Droid | Specialty | Use When... |
|-------|-----------|-------------|
| **turborepo-biome-qa-auditor** | Monorepo quality checks | Running Biome linting, workspace validation |
| **worker-qa-observer** | Cloudflare Worker testing | Testing Workers, integration testing |
| **cost-audit-accountant** | API cost tracking | Monitoring token usage, cost optimization |

### 🏗️ Architecture & Workflow

| Droid | Specialty | Use When... |
|-------|-----------|-------------|
| **workflow-runner** | React Flow DAG execution | Executing workflow graphs, state management |
| **nextjs-app-router-expert** | Next.js App Router patterns | Implementing App Router, server components |
| **doc-intake-normalizer** | Document processing | Normalizing document formats, metadata extraction |
| **live-collaboration-orchestrator** | Real-time collaboration | Implementing Velt collaboration, presence |
| **style-dna-schema-guardian** | Schema validation | Validating style DNA schemas, type safety |

---

## Creation Framework

### Step 1: Choose Your Architectural Paradigm

Based on research and community insights, select the right approach:

**For Simple, Predictable Workflows** → **Router Pattern**
- Linear tasks with clear decision points
- Example: Route to different parsers based on content type

**For Complex, Multi-Step Processes** → **Supervisor Pattern**  
- Need shared context and collaborative problem-solving
- Example: Purchase intent analysis requiring multiple perspectives

**For Hierarchical Expertise** → **Hierarchical Pattern**
- Layered decision-making with escalating expertise
- Example: Basic QA → Specialist QA → Architectural review

**For Democratic Innovation** → **Coordinator Pattern**
- Multiple agents propose solutions, coordinator decides
- Example: Creative content generation with multiple approaches

### Step 2: Identify the Domain

**Questions to ask**:
- What specific expertise is needed repeatedly?
- Where do we make the same mistakes repeatedly?
- What context do we find ourselves explaining over and over?
- Which architectural pattern best fits this domain?

**Example**: Vector similarity calculations
- Domain: Mathematical operations on embeddings
- Context: Float32Array optimization for Cloudflare Workers
- Constraints: OpenAI unit-normalized embeddings
- **Best Pattern**: Supervisor (shared context for mathematical precision)

### Step 2: Define Forced Context

**Project-Specific Template**:
```yaml
## Project-Specific Context

This project is a [PROJECT_TYPE] that [PROJECT_DESCRIPTION]. Your role is to handle [DOMAIN_SPECIFIC_TASK].

### Tech Stack
- **Runtime**: [SPECIFIC_RUNTIME]
- **Framework**: [SPECIFIC_FRAMEWORK] 
- **Database**: [SPECIFIC_DATABASE]
- **Key Constraints**: [PERFORMANCE/SECURITY REQUIREMENTS]
```

### Step 3: Specify Exact Responsibilities

Bad: "Handle database operations"
Good: "Implement Neon schema design and migration management with these exact tables..."

Bad: "Implement caching"  
Good: "Build PostgreSQL caches with Drizzle ORM, implementing hit tracking and TTL management"

### Step 4: Define Tool Permissions

Be specific about tools:
```yaml
tools:
  - Read
  - Write  
  - Edit
  - Bash
  - mcp__context7__resolve-library-id
  - mcp__context7__get-library-docs
  # NOT: "all tools" - be specific
```

### Step 5: Provide Implementation Patterns

Give exact code templates:
```typescript
// Standard droid implementation pattern
export function specializedFunction(config: SpecificConfig): Result {
  // Exact algorithm steps
  // Performance considerations
  // Error handling requirements
}
```

### Step 6: Define Guardrails

```yaml
### When to Create Tasks
- User explicitly requests [DOMAIN_TASK]
- Agent needs [SPECIFIC_KNOWLEDGE] for revision
- Workflow node of type `[WORKFLOW_TYPE]` executes

### When to Stop Waiting
- [SPECIFIC_COMPLETION_CONDITION]
- Timeout threshold reached ([SPECIFIC_TIME])
- User cancels operation

### Max Iterations
- [RATE_LIMITS_AND_RETRIES]
```

---

## Predict Intent GLM Application

### Relevant Droids for Our Project

**Core Development**:
- **openai-llm-strategist** → LLM integration for purchase intent analysis
- **embeddings-provider-strategist** → Embedding management for semantic similarity  
- **similarity-math-tactician** → Vector calculations for intent scoring
- **research-orchestrator** → Market research and consumer behavior analysis

**Data & Content**:
- **content-parser-architect** → Processing product descriptions and marketing copy
- **data-model-steward** → Schema design for consumer profiles and intent data
- **doc-intake-normalizer** → Processing training data from various sources

**API & Infrastructure**:
- **cloudflare-worker-deployment-specialist** → Edge deployment for real-time predictions
- **trpc-hono-integrator** → Type-safe API for customer intent analysis
- **wrangler-scaffold-architect** → Project setup for Workers environment

**Quality & Cost**:
- **cost-audit-accountant** → Tracking LLM usage across prediction workflows
- **worker-qa-observer** → Testing prediction accuracy and performance
- **turborepo-biome-qa-auditor** → Code quality for the system

### Custom Droid Creation for Purchase Intent

**New Droid Idea**: `purchase-intent-analyst`

```yaml
---
name: purchase-intent-analyst
description: Analyze consumer purchase intent using semantic similarity methods based on LLM research. Handles Likert scale prediction, consumer segment analysis, and confidence scoring for product testing scenarios.
model: gpt-5
tools: [Read, Write, Edit, Grep]
---

# Purchase Intent Analyst

## Project-Specific Context

This project implements AI-powered purchase intent prediction based on the research paper "LLMs Reproduce Human Purchase Intent via Semantic Similarity Elicitation of Likert Ratings" achieving 92% correlation with human judgments.

### Core Technology
- **Base Model**: GPT-4/Claude for semantic analysis
- **Similarity Method**: Embedding-based Likert scale anchor comparison
- **Cost Efficiency**: $0.00001 vs $1.00 per human response
- **Scale**: Unlimited simultaneous testing

## Key Responsibilities

### 1. Purchase Intent Prediction
```typescript
interface PurchaseIntentAnalysis {
  content: string;           // Product description, ad copy, or content
  consumerSegment: Persona;  // Target consumer profile
  confidenceScore: number;   // 0-1 confidence in prediction
  purchaseIntent: number;    // 1-7 Likert scale prediction
  reasoning: string;         // Semantic similarity explanation
}
```

### 2. Consumer Persona Generation
```typescript
interface Persona {
  demographics: {
    age: string;
    income: string;
    education: string;
    location: string;
  };
  psychographics: {
    values: string[];
    lifestyle: string;
    painPoints: string[];
  };
  behavioral: {
    purchasePatterns: string[];
    brandPreferences: string[];
  };
}
```

### 3. Content Type Analysis
- **Product Descriptions**: Feature analysis, value proposition assessment
- **Advertising Copy**: Headline effectiveness, CTA analysis
- **Landing Pages**: Conversion optimization, UX assessment
- **Course Materials**: Learning outcome prediction, engagement scoring
```

### Integration Workflow

1. **Content Intake** → `doc-intake-normalizer` processes materials
2. **Consumer Analysis** → `purchase-intent-analyst` generates personas and predictions  
3. **Vector Processing** → `embeddings-provider-strategist` + `similarity-math-tactician`
4. **Cost Tracking** → `cost-audit-accountant` monitors LLM usage
5. **Deployment** → `cloudflare-worker-deployment-specialist` for edge deployment

---

## Advanced Usage Patterns

### 1. Multi-Droid Collaboration

**Example: Purchase Intent Testing Workflow**

```typescript
// Orchestrate multiple specialists for comprehensive analysis
const workflow = {
  step1: 'doc-intake-normalizer',      // Process test materials
  step2: 'purchase-intent-analyst',    // Analyze intent per segment
  step3: 'similarity-math-tactician',   // Calculate similarity scores
  step4: 'research-orchestrator',       // Gather market context
  step5: 'cost-audit-accountant',      // Track analysis costs
  step6: 'worker-qa-observer'          // Validate predictions
};
```

### 2. Research-Backed Development

**Using research-orchestrator for knowledge gathering**:
```typescript
// Trigger research when encountering new domains
const researchTask = {
  processor: 'core',
  query: "Consumer behavior patterns for luxury goods purchasing decisions",
  webhookUrl: '/api/webhooks/research-complete',
  enableEvents: true
};

// Automatically triggers research-summarizer on completion
// Results flow to revision-planner for content optimization
```

### 3. Quality Assurance Workflows

**Using QA droids for validation**:
```typescript
// Multi-layer quality checks
const qualityPipeline = {
  codeQuality: 'turborepo-biome-qa-auditor',
  workerTesting: 'worker-qa-observer', 
  costOptimization: 'cost-audit-accountant',
  schemaValidation: 'style-dna-schema-guardian'
};
```

### 4. Continuous Improvement Cycle

**Curtis's refinement process**:
1. **Post-session review**: Ask main agent to evaluate droid performance
2. **Concern collection**: Each droid writes improvement suggestions
3. **Review and approve**: ~80% of suggestions implemented
4. **Iterate**: Next session starts with improved droids

**Example feedback loop**:
```
Session Complete → Droid Self-Assessment → Improvement Suggestions → Review → Implementation → Next Session
```

---

## Practical Integration Guide

### Calling Droids

**Basic Invocation**:
```json
{
  "subagent_type": "openai-llm-strategist",
  "description": "Implement LLM for purchase intent analysis",
  "prompt": "Create the semantic similarity pipeline for predicting purchase intent using 7-point Likert scales"
}
```

**With Context**:
```json
{
  "subagent_type": "similarity-math-tactician", 
  "description": "Implement vector math for intent scoring",
  "prompt": "Create the Float32Array operations for computing cosine similarity between product embeddings and intent anchors"
}
```

### Project Structure Integration

```
.purchase-intent-glm/
├── .factory/
│   └── droids/
│       ├── openai-llm-strategist.md
│       ├── embeddings-provider-strategist.md  
│       ├── similarity-math-tactician.md
│       ├── purchase-intent-analyst.md (custom)
│       └── cost-audit-accountant.md
├── src/
│   ├── lib/               # Droid-generated code
│   │   ├── openai.ts      # From openai-llm-strategist
│   │   ├── math.ts        # From similarity-math-tactician
│   │   └── providers/     # From embeddings-provider-strategist
│   ├── api/               # API endpoints
│   └── types/             # Generated schemas
└── docs/
    ├── droid-plan.md      # This guide
    └── droid-usage/       # Usage examples
```

### Environment Setup

**Required Variables**:
```bash
# LLM Integration
OPENAI_API_KEY=sk_...
ANTHROPIC_API_KEY=ant_...

# Embedding Providers  
OPENAI_EMBED_MODEL=text-embedding-3-large
EMBED_PROVIDER=ai|openai

# Vector Math
VECTOR_DIMENSIONS=3072
SIMILARITY_THRESHOLD=0.7

# Research Services
PARALLEL_API_KEY=sk_parallel_...
PARALLEL_WEBHOOK_SECRET=whsec_...

# Deployment
CLOUDFLARE_API_KEY=...
NEON_DATABASE_URL=...
```

### Testing Droid Integration

**Unit Test Pattern**:
```typescript
// Test droid-generated code
import { embedMany } from '@/lib/providers';
import { cosineSimilarity } from '@/lib/math';

describe('Purchase Intent Analysis', () => {
  it('should compute similarity between product and intent anchors', async () => {
    const productEmbedding = await embedMany(['Premium wireless headphones']);
    const intentAnchor = await embedMany(['I would definitely buy this']);
    
    const similarity = cosineSimilarity(productEmbedding[0], intentAnchor[0]);
    expect(similarity).toBeGreaterThan(0.7);
  });
});
```

---

## Troubleshooting & Optimization

### Common Issues

**1. Droid Context Gaps**
- **Symptom**: Droid asks for basic information repeatedly
- **Solution**: Add project-specific context to droid front matter
- **Example**: Include tech stack, API endpoints, database schema

**2. Tool Permission Errors**  
- **Symptom**: "Tool not available" errors
- **Solution**: Explicitly list required tools in droid config
- **Example**: Add `mcp__context7` for library documentation access

**3. Generic Output**
- **Symptom**: Droid provides vague, non-specific solutions
- **Solution**: Add implementation patterns and code templates
- **Example**: Include exact algorithm specifications

### Performance Optimization

**1. Token Usage**
```typescript
// Use cost-audit-accountant to track
const usage = await costAudit.trackUsage({
  operation: 'generateText',
  model: 'gpt-4o',
  tokens: inputTokens + outputTokens,
  metadata: { campaignTag: 'purchase-intent-analysis' }
});
```

**2. Droid Orchestration**
```typescript
// Parallel execution where possible
const [embeddings, research] = await Promise.all([
  embeddingsProvider.embedMany(content),
  researchOrchestrator.startTask(researchQuery)
]);
```

**3. Caching Strategies**
```typescript
// Cache droid results where appropriate
const cacheKey = `droid:${droidName}:${hash(input)}`;
const cached = await cache.get(cacheKey);
if (cached) return cached;
```

### Monitoring & Observability

**1. Droid Performance**
- Track success rates per droid  
- Monitor token usage patterns
- Measure output quality scores

**2. Integration Health**
- Monitor droid-to-droid communication
- Track workflow completion rates  
- Alert on timeout scenarios

**3. Cost Management**
```typescript
// Set budget alerts
await costAudit.setBudgetAlert({
  monthlyLimit: 1000,
  alertThresholds: [0.5, 0.8, 0.95],
  notificationWebhook: '/api/budget-alerts'
});
```

---

## Curtis's Practical Droid Creation Method

Beyond the complex frameworks, Curtis has developed a **beginner-friendly approach** that anyone can use. This method focuses on accessibility and rapid iteration rather than technical complexity.

### **Step 1: Get the Rules**
Visit https://docs.factory.ai/cli/configuration/custom-droids and copy the documentation page markdown
- This provides the official syntax and formatting requirements
- Includes examples and best practices from the Factory AI team

### **Step 2: AI-Assisted Creation**
**Open ANY LLM and ask**:
> "Hey my coworker told me to make a subagent. Can you read the rules here and then ask me 10 questions so that you can then write me my own custom subagent? I'm not technical so ask me in a way I can answer or explain. Make sure to handle formatting, I don't know what yaml and frontmatter are."

**Why this works**:
- **Non-technical approach**: LLM handles YAML syntax and frontmatter formatting
- **Socratic method**: Questions ensure domain expertise is captured correctly
- **Error prevention**: Professional formatting from the start

### **Step 3: Deploy and Use**
- **Save the output** to `.factory/droids/` (or `.factory/agents/` depending on version)
- **Use it immediately** - the best way to improve droids is through real usage
- **Expect frustration** - Curtis emphasizes that droids need iteration to become effective

### **Step 4: Daily Improvement Cycle**

**At the end of each coding session**, ask yourself or the main agent:
> "I want to talk about our subagent. Where could he have done better or different based on how things went today?"

**Key indicators to watch for**:
- **Agent avoidance**: "Hey main droid I noticed you didn't want to use sub agent much, why or what could be different for you to use it?"
- **Repeated failures**: Same tasks causing errors repeatedly
- **Wrong domain**: Agent trying to handle tasks outside its expertise
- **Missing context**: Agent asking for the same information repeatedly

### **Step 5: Rapid Iteration**
**Update the droid** based on session feedback:
- **Open another chat** with the LLM
- **Provide the current droid definition** and feedback points
- **Ask for improvements**: "I want to update my droid to address some of these items"
- **Overwrite the file** - you now have a slightly better subagent

### **Why Curtis's Method Works So Well**

#### **1. Low Barrier to Entry**
- **No YAML knowledge needed**: LLM handles syntax automatically  
- **No frontmatter expertise**: Formatting is taken care of for you
- **Plain language questions**: Domain knowledge captured naturally

#### **2. Domain-Driven by Default**
- The 10 questions naturally focus on the specific domain you need
- Forces you to think through the exact use cases and constraints
- Captures contextual knowledge that you'd otherwise forget to include

#### **3. Built-in Continuous Improvement**
- **Real usage feedback**: The most valuable improvement source
- **Session-based iteration**: Natural cycle of use → feedback → improve
- **Agent self-reflection**: Even the main agent can identify when to use specialists

#### **4. Fail-Friendly Approach**
- **Expectation management**: Curtis explicitly says "it will be frustrating"
- **Progressive refinement**: Each iteration makes it slightly better
- **No pressure for perfection**: Good enough to start, excellent through iteration

### **Example: Creating a Purchase Intent Analyst**

**Using Curtis's method would look like**:

**LLM Questions you'd answer**:
1. What specific domain will this droid help with? (Answer: "Purchase intent prediction for products and marketing")

2. What kind of tasks will it need to do? (Answer: "Analyze ad copy, product descriptions, landing pages and tell me if people will buy")

3. Are there any specific tools it needs? (Answer: "Read files, use OpenAI to analyze text, maybe create reports")

4. What makes this domain special or different from general coding? (Answer: "It's about psychology and marketing, not just technical stuff")

5. Are there any common mistakes or problems to avoid? (Answer: "Don't overpromise results, be honest about confidence levels")

6. What kind of background context should the droid know? (Answer: "Based on research paper about LLMs predicting purchase intent with 92% accuracy")

7. How should the droid communicate results? (Answer: "Simple scores 1-7 for likelihood to buy, plus explanation")

8. Are there any specific rules or constraints? (Answer: "Always mention the confidence score, don't make up fake data")

9. Who is the main user of this droid? (Answer: "Me, a developer building a purchase intent system")

10. What would make this droid most helpful to you? (Answer: "Quick analysis without me having to be a marketing expert")

**Result**: A perfectly formatted, domain-specific droid that you can use immediately and improve through real usage.

### **Curtis vs. Research-Heavy Approach**

| Aspect | Curtis Method | Research Approach |
|--------|---------------|-------------------|
| **Entry Barrier** | Very Low (anyone can start) | High (requires technical knowledge) |
| **Time to First Droid** | 30 minutes | 2-4 hours of learning |
| **Improvement Source** | Real usage feedback | Academic papers and frameworks |
| **Iteration Speed** | Daily sessions | Weekly/monthly overhauls |
| **Success Rate** | High (proven with beginners) | Variable (depends on expertise) |
| **Scalability** | Limited to personal use | Enterprise-ready |

### **Hybrid Best Practice**

**Combine both approaches**:
1. **Start with Curtis method** → Get working droid in 30 minutes
2. **Use it immediately** → Collect real feedback and patterns
3. **Apply research insights** → Enhance based on architectural patterns
4. **Iterate rapidly** → Daily improvements using Curtis cycles
5. **Gradually migrate** → Advanced features as needed

This gives you immediate results while building toward sophisticated systems.

---

## Advanced Usage Patterns

### Essential Droids for Purchase Intent GLM

**openai-llm-strategist**
- **Trigger**: Implementing LLM integration
- **Output**: Vercel AI SDK patterns, prompt engineering
- **Pattern**: `generateText()` with structured outputs

**embeddings-provider-strategist** 
- **Trigger**: Vector embedding needs
- **Output**: Provider abstraction, batching strategy
- **Pattern**: `embedMany()` with usage tracking

**similarity-math-tactician**
- **Trigger**: Vector calculations required  
- **Output**: Float32Array optimization, exact formulas
- **Pattern**: Dot product, cosine similarity, defensive normalization

**research-orchestrator**
- **Trigger**: External knowledge needed
- **Output**: Parallel.ai integration, webhook handling
- **Pattern**: Task creation → webhook → result retrieval

**cost-audit-accountant**
- **Trigger**: After any AI operation
- **Output**: Usage tracking, cost reports, budget alerts
- **Pattern**: Log every token, aggregate by dimensions

### Droid Invocation Cheat Sheet

```bash
# LLM Integration
task-cli --subagent openai-llm-strategist "Implement semantic similarity pipeline"

# Vector Operations  
task-cli --subagent similarity-math-tactician "Create Float32Array cosine similarity"

# Content Processing
task-cli --subagent content-parser-architect "Add Exa parser for product reviews"

# Research Tasks
task-cli --subagent research-orchestrator "Research consumer behavior patterns"

# Cost Analysis
task-cli --subagent cost-audit-accountant "Generate monthly spend report"
```

---

## Emerging Patterns & Future Research

### Advanced Research Directions

Based on current academic and industry research, several emerging patterns are shaping the future of multi-agent systems:

#### **1. Inference-Time Compute Integration**
- **OpenAI's o1 model**: Extra compute during inference for better reasoning
- **Application**: Droids that can dynamically activate deeper reasoning for complex tasks
- **Impact**: Adaptive intelligence scaling based on task complexity

#### **2. Reinforcement Learning for Agents**
- **Self-learning agents**: Systems that improve efficiency through experience
- **Multi-agent RL**: Groups of agents learning collaborative strategies
- **Application**: Purchase intent prediction agents that learn from user feedback

#### **3. Heterogeneous Agent Architectures**
**Research from 2025 shows optimal mixing of different agent types**:
- **Reactive agents**: Real-time task execution (like ad copy testing)
- **Deliberative agents**: Strategic planning (like market analysis)
- **Hybrid systems**: Combining both for complex workflows

#### **4. Agent Composition & Inheritance**
Emerging patterns for reusing and extending droid capabilities:
```yaml
# Base droid with core functionality
---
name: base-purchase-analyst
core_abilities: [llm_interaction, vector_math, cost_tracking]

# Specialized droid inheriting and extending
extends: base-purchase-analyst
specialization: luxury_goods
additional_context: "High-end consumer behavior patterns"
```

### Alternative Platforms & Approaches

Beyond Factory AI, research reveals competing philosophies:

#### **CrewAI Approach**
- **Network-first**: All agents can communicate directly
- **Role-based**: Each agent has specific role and crew assignment
- **Workflow**: Predefined processes with agent handoffs

#### **Microsoft AutoGen Focus**
- **Conversational patterns**: Agents negotiate and collaborate through dialogue
- **Group chat architecture**: Multi-agent conversations for problem-solving
- **Teaching**: Agents can teach and learn from each other

#### **OpenAI Swarm**
- ** lightweight orchestration**: Minimal overhead for agent coordination
- **Goal-oriented**: Focus on achieving objectives rather than rigid workflows
- **Adaptive**: Dynamic role assignment based on task needs

### Production Readiness Patterns

#### **1. Progressive Deployment**
```typescript
// Stage 1: Single agent testing
const singleResult = await testDroidAlone(droidName, testCases);

// Stage 2: Pairwise interaction testing
const pairResults = await testDroidPairs([droidA, droidB]);

// Stage 3: Full workflow orchestration
const workflowResults = await testFullWorkflow(droidOrchestra);
```

#### **2. Observability-First Design**
Based on research from Terminus and other production systems:
- **Autonomous monitoring**: Agents track their own performance
- **Self-healing**: Automatic recovery from common failures
- **Audit trails**: Complete recording of agent decisions

#### **3. Cost-Efficient Specialization**
Learnings from industrial applications:
- **Smart caching**: Shared memory pools for common operations
- **Selectivity**: Only use specialists when expertise differential justifies cost
- **Fallback strategies**: General agents when specialists are unavailable

### The "AI Factory" Evolution

Research shows maturation toward self-improving AI systems:

#### **Current State (Curtis-level)**
- Human-curated specialist agents
- Fixed expertise domains
- Manual improvement cycles

#### **Emerging State**
- **Self-generating agents**: Systems that create new specialists as needed
- **Domain discovery**: Identifying new expertise areas automatically  
- **Cross-learning**: Knowledge transfer between related domains

#### **Research Goals**
- **Autonomous specialization**: Agents developing new expertise without human guidance
- **Meta-learning**: Learning how to learn across multiple domains
- **Self-orchestration**: Systems that optimize their own agent composition

---

## Conclusion

Factory Droids represent a paradigm shift in AI-assisted development, but they're just the beginning. By synthesizing Curtis's proven approach with broader research insights from academia and industry, you can build even more sophisticated systems.

### Key Takeaways

**Curtis's Timeless Principles**:
- **Context is King** > Better than prompts every time
- **Constraints Enable Creativity** > Specific requirements beat generic
- **Sub-agents are Specialists** > One domain expertise each
- **Production-Ready Patterns** > Real implementations, not tutorials
- **Continuous Improvement** > Post-session refinement cycle

**Research-Enhanced Insights**:
- **Architectural variety**: Router, Supervisor, Coordinator, Hierarchical patterns
- **Shared context superiority** > Better decision-making though more complex
- **MoE principles at agent level** > Efficient specialization activation
- **Self-improving systems** > Future direction with autonomous optimization

For the Predict Intent GLM project, this hybrid approach will enable you to:
- Build production-ready LLM integration 10x faster
- Implement complex vector mathematics correctly the first time  
- Choose optimal architectural patterns for each domain
- Manage distributed AI operations reliably
- Track costs and optimize spend effectively
- Create purchase intent analysis that improves autonomously

### Strategic Recommendation

**Start with Curtis's approach** for immediate production value, then **gradually incorporate research patterns**:
1. **Phase 1**: Implement proven Curtis-style specialists
2. **Phase 2**: Add research-based architectural patterns (Supervisor for complex analysis)
3. **Phase 3**: Introduce emerging patterns (MoE activation, self-improvement cycles)

The key is **treating your droids as evolving team members rather than static tools**. Each session provides an opportunity to refine their capabilities, experiment with new patterns, and expand their autonomy.

Remember: **Context is King, but Architecture is Queen**. Force-feed context, but choose the right orchestration pattern for your specific needs.

---

*This guide incorporates both proven practitioner experience and cutting-edge research. It will evolve as droid technology advances and we discover new patterns in the Predict Intent GLM project. Check back regularly for updated patterns, new custom droid examples, and emerging research insights.*
