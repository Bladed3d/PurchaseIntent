Instructions for Factory Droid: Automated Purchase Intent Prediction Process
Below is a comprehensive set of instructions you can copy and paste directly into Factory Droid (or your AI agent orchestration system) to automate the purchase intent prediction workflow. These instructions are designed to be self-contained, modular, and executable as a script or task flow. They integrate the core objectives from the two PDF documents:

From ParaThinker.pdf: Emphasize parallel thinking to avoid "Tunnel Vision" (where sequential reasoning locks into suboptimal paths). Use multiple independent reasoning paths (e.g., via control tokens like <think i>) to explore diverse angles, then aggregate them for superior accuracy. This scales test-time compute efficiently, achieving 7.5-12.3% gains on benchmarks by generating diverse thoughts in parallel and synthesizing them.
From LLM-Predict-Purchase-Intent.pdf: Use Semantic Similarity Rating (SSR) for eliciting and mapping purchase intent. Avoid direct numerical Likert ratings (which produce unrealistic distributions). Instead, generate textual responses from synthetic consumers, map them to a 5-point Likert scale via embedding similarities to anchor statements, and ensure realistic distributions (aim for KS similarity >0.85 and ~90% correlation with human data). Ground in synthetic personas conditioned on demographics to replicate human biases.

The process follows the improved flowchart: Start with a product idea, search for similar products, extrapolate demographics, generate personas, simulate intent in parallel using multiple AI models, synthesize with SSR, validate, and iterate if needed. Assume Factory Droid has access to subagents with models (GLM-4.6, GPT-5, Sonnet 4.5, Haiku 4.5) and tools for web search, embedding calculation, and reporting.
Prerequisites for Factory Droid Setup

Subagents: Assign one subagent per AI model (e.g., Subagent1: GLM-4.6 for analytical focus; Subagent2: GPT-5 for balanced; Subagent3: Sonnet 4.5 for emotional nuance; Subagent4: Haiku 4.5 for quick risk assessment).
Tools Needed: Web search (e.g., for similar products and demographics), code execution (for embeddings/SSR calculations using libraries like sentence-transformers or numpy), and output formatting (e.g., JSON reports).
Input Parameters: Provide the product idea as a JSON object, e.g., {"description": "Lightweight camping tent for families", "features": ["Waterproof", "Easy setup"], "benefits": ["Portable", "Durable"], "price": 150}.
Output: A final JSON report with mean intent score, distribution, qualitative themes, and recommendations.
Error Handling: If any step fails (e.g., no similar products found), log the issue and default to broad demographics (e.g., "general consumers aged 25-44").
Ethical Note: Include a disclaimer in reports: "This is synthetic data simulating human responses; validate with small real surveys for critical decisions."

Step-by-Step Process Instructions
Run this as an orchestrated workflow. Use parallel execution where noted (e.g., for AI models) to mimic ParaThinker's efficiency.

Input Product Idea:

Receive the product idea input (description, features, benefits, price).
Validate: Ensure description is at least 50 words; if not, prompt for more details.
Output: A query string for searching similar products, e.g., "similar products to [description] like [features]".


Search for Similar Products (Data Gathering Phase):

Use web search tool to find 3-5 comparable products. Query: "top similar products to [product description] [features] site:amazon.com OR site:rei.com OR site:walmart.com" (limit to 10 results).
Extract from results: Product names, descriptions, features, benefits, prices, review links, and sales data (e.g., ratings, number of reviews).
If multimodal, analyze images if available (e.g., via view_image tool for product visuals).
Objective Alignment: This grounds the process in real market data, as per Purchase Intent PDF's emphasis on realistic synthetic simulations.
Output: JSON list of comparables, e.g., [{"name": "Competitor Tent", "reviews_url": "amazon.com/reviews/123", "avg_rating": 4.5}].


Extrapolate Demographics from Real Data:

For each comparable product, browse review pages or use X semantic search: Query "customer reviews and demographics for [product name]" (limit 20 posts/results).
Analyze snippets: Infer demographics (age, gender, income, location, interests, pain points) from patterns, e.g., "Many reviewers are 30-40-year-old families who camp weekends; complaints about weight."
Aggregate: Use code execution to compute stats (e.g., via pandas: group by inferred age groups).
Fallback: If data sparse, default to broad segments (e.g., from web search "demographics for camping gear buyers").
Objective Alignment: Replicates human panel diversity as in Purchase Intent PDF, avoiding biases in synthetic consumers.
Output: Aggregated demographics JSON, e.g., {"age": "25-44", "interests": ["outdoor activities", "family bonding"], "pain_points": ["high price", "durability"]}.


Generate Target Customer and Synthetic Personas (Persona Creation Phase):

Define target customer: Combine extrapolated demographics into 4-8 segments (e.g., "budget-conscious 34-year-old urban camper").
Generate 100-500 synthetic personas per segment: Use a subagent (e.g., GPT-5) to create variations, conditioning on demographics.
Prompt Template: "Generate [number] diverse personas matching [demographics]. Include age, gender, income, interests, pain points. Output as JSON list."
Objective Alignment: Ensures synthetic consumers mirror human variability, as per Purchase Intent PDF.
Output: JSON array of personas.


Simulate Intent with Parallel Paths (Simulation Phase - Parallel Execution):

For each persona (batch in groups of 100 for efficiency), assign to the 4 subagents in parallel.
Prompt each subagent (tailored to model strengths): Act as [persona]. Evaluate purchase intent for [product description/features/benefits/price].
Incorporate ParaThinker: Generate 4-8 diverse reasoning paths per subagent. Use control tokens: <think 1> [Angle: value for money]... End with textual intent statement (1-2 sentences, no numbers). Repeat for each path.
Then, <summary> Synthesize paths into one cohesive textual intent statement.
Enforce diversity: Paths must explore different angles (e.g., features, emotions, risks) to avoid Tunnel Vision.
Elicitation Style (from Purchase Intent PDF): Use textual responses only (e.g., "I'd consider buying if it's durable, but the price seems high.") to enable SSR.
For A/B Testing: If variants provided, compare options in prompts.
Run in parallel across subagents to simulate multi-threaded thinking.
Objective Alignment: Parallel paths unlock latent potential (ParaThinker), while textual elicitation ensures realistic distributions (Purchase Intent).
Output: Per persona/subagent: JSON with paths and summary textual response.


Synthesize Intent Using SSR (Aggregation Phase):

For each textual response (use summaries or individual paths for diversity):

Compute embeddings: Use code execution (e.g., with sentence-transformers: from sentence_transformers import SentenceTransformer; model = SentenceTransformer('all-MiniLM-L6-v2'); embed(text)).
Define 5 Likert anchors (from Purchase Intent PDF, Appendix C.1): e.g., 1: "I would definitely not buy this; it doesn't appeal at all." 3: "I'm neutral." 5: "I would definitely buy this; it's perfect."
Map: Compute cosine similarities to anchors, normalize to probability mass function (pmf), derive mean score and distribution.
Aggregate: Average pmfs across paths/subagents/personas for overall mean (1-5), std dev, and KS similarity check (code: scipy.stats.kstest for human-like spread).


Extract themes: Use a subagent to cluster textual responses (e.g., pros/cons via topic modeling with BERTopic if available).
Objective Alignment: SSR achieves 90% human correlation; parallelism boosts by exploring diverse thoughts before mapping.
Output: JSON with mean intent, distribution histogram, themes (e.g., "Top motivator: durability (mentioned in 60% responses)").


Validate and Report (Validation Phase):

Compare to benchmarks: Use web search for real purchase intent data on similar products (e.g., "average purchase intent for camping tents surveys").
Check metrics: Correlation attainment >80%, KS >0.85. If low, flag for iteration.
Generate Report: JSON/PDF with scores, visualizations (e.g., matplotlib bar chart of distribution), themes, recommendations (e.g., "Improve price to boost intent from 3.2 to 4.0").
Disclaimer: "Synthetic simulation; actual human testing recommended."
Objective Alignment: Ensures reliability as in both PDFs (e.g., test-retest in Purchase Intent, benchmark gains in ParaThinker).
Output: Final report file.


Iterate if Needed (Feedback Loop):

If mean intent < threshold (e.g., 3.5/5), loop back: Suggest refinements (e.g., "Lower price by 20%") and re-run from Step 1 with updated idea.
For A/B: Run parallel variants and compare.
Stop after 3 iterations or user approval.
Objective Alignment: Addresses diminishing returns in sequential scaling (ParaThinker) by iterating on aggregated insights.



Execution Guidelines for Factory Droid

Parallelism: Use Droid's orchestration to run subagents concurrently in Step 5.
Scalability: Batch personas; limit to 100 for quick tests, scale to 500 for accuracy.
Cost Monitoring: Track API calls; use Haiku for initial drafts.
Logging: Log each step's output for debugging.
Run Command Example: droid run --input product.json --output report.json.

This process should achieve high-fidelity predictions (~90%+ human-like) while being efficient and scalable.