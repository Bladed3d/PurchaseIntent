Automated Purchase Intent Prediction Process for Claude Skills
Below is the adapted version of the "Automated Purchase Intent Prediction Process" specifically for Claude Skills (part of Anthropic's Claude AI platform). Claude Skills allow you to create modular, reusable prompt-based "skills" that can be defined in a Claude Project and invoked sequentially or in chains. Each skill is a self-contained instruction set that Claude follows when called.
This adaptation maintains the core workflow from the flowchart: Start with a product idea, search for similar products, extrapolate demographics, generate personas, simulate intent in parallel (using multiple skills/models if available via Claude's multi-model support or sub-prompts), synthesize with SSR, validate, and iterate. It aligns with the objectives from the PDFs:

From ParaThinker.pdf: Implements native parallel thinking by generating multiple diverse reasoning paths (using control tokens like <think i>) within skills to avoid "Tunnel Vision." Paths explore different angles (e.g., value, features, emotions, risks) and are aggregated for 7.5-12.3% potential accuracy gains, scaling compute in width rather than depth.
From LLM-Predict-Purchase-Intent.pdf: Uses Semantic Similarity Rating (SSR) for textual elicitation and mapping to a 5-point Likert scale via embeddings. Avoids direct numerical ratings to ensure realistic distributions (target KS similarity >0.85 and ~90% correlation with human data). Skills generate synthetic consumers conditioned on demographics to replicate human biases.

Setup in Claude

Create a Claude Project: Log into Claude.ai, start a new Project, and define each skill below as a separate "Skill" in the Knowledge or Instructions section. Use the skill name as the title.
Orchestrator Skill: Use the main "Orchestrator" skill to chain the others. Invoke skills by name in prompts (e.g., "Run Skill: Input Product Idea with [input]").
Tools Integration: If your Claude setup has API access or extensions for tools (e.g., web search, code execution), reference them in skills. Otherwise, simulate with manual inputs or Claude's built-in capabilities. For embeddings in SSR, use Python code snippets Claude can "execute" via reasoning (or integrate with external APIs if available).
Input/Output: Skills use JSON for structured data. Provide product idea as JSON input to the Orchestrator.
Ethical Note: All skills include a disclaimer: "This is synthetic data; validate with real human surveys."
Scalability: For parallelism, define sub-skills or use Claude's multi-response feature. Limit personas to 100 for quick runs, scale to 500 for accuracy.

Defined Claude Skills

Skill: Input Product Idea

Description: Receives and validates the product idea input.
Instructions for Claude:
textYou are processing a product idea for purchase intent prediction. Input is JSON: {"description": "...", "features": ["..."], "benefits": ["..."], "price": number}.

Steps:
1. Validate: Ensure description is >50 words. If not, respond with error JSON: {"error": "Add more details"}.
2. Generate search query: "similar products to [description] with features like [features]".
3. Output JSON: {"query": "search query", "product": input JSON}.

Disclaimer: This is synthetic data; validate with real surveys.



Skill: Search for Similar Products

Description: Searches for 3-5 comparable products using web tools.
Instructions for Claude:
textInput: JSON from previous skill with "query".

Steps:
1. Use web_search tool: Query "[query] site:amazon.com OR site:rei.com OR site:walmart.com" (num_results=10).
2. Extract from results: 3-5 products with names, descriptions, features, benefits, prices, review URLs, ratings.
3. If images: Use view_image on product images for visual analysis (e.g., "Summarize visual appeal").
4. Output JSON: {"comparables": [{"name": "...", "description": "...", "reviews_url": "...", "avg_rating": number}]}.

Align with Purchase Intent PDF: Ground in real data for realistic simulations.
Disclaimer: This is synthetic data; validate with real surveys.



Skill: Extrapolate Demographics

Description: Infers demographics from comparable product data.
Instructions for Claude:
textInput: JSON with "comparables".

Steps:
1. For each comparable, use browse_page on reviews_url: Instructions "Extract demographics (age, gender, income, interests, pain points) from reviews. Summarize patterns."
2. Or use x_keyword_search: Query "reviews [product name] demographics" (limit=20, mode=Latest).
3. Aggregate: Use code_execution for stats (e.g., code: import pandas; df = pd.DataFrame(data); print(df.groupby('age').mean())).
4. Fallback: Web search "demographics for [product category] buyers" if data sparse.
5. Output JSON: {"demographics": {"age": "25-44", "interests": ["..."], "pain_points": ["..."]}}.

Align with Purchase Intent PDF: Replicate human biases via conditioned personas.
Disclaimer: This is synthetic data; validate with real surveys.



Skill: Generate Personas

Description: Creates synthetic personas based on demographics.
Instructions for Claude:
textInput: JSON with "demographics".

Steps:
1. Define 4-8 segments (e.g., "budget-conscious 34-year-old camper").
2. Generate 100-500 personas: Prompt "Generate diverse personas matching [demographics]. Include age, gender, etc. JSON list."
3. Output JSON: {"personas": [{"id": 1, "details": "..."}]}.

Align with Purchase Intent PDF: Ensure variability to mirror human panels.
Disclaimer: This is synthetic data; validate with real surveys.



Skill: Simulate Intent (Parallel)

Description: Simulates intent using parallel paths, assignable to different "models" via sub-skills if Claude supports (or simulate with varied prompts).
Instructions for Claude:
textInput: JSON with "personas", "product".

Steps:
1. Batch personas (groups of 100).
2. For each persona: Generate 4-8 parallel paths (ParaThinker-style).
   Prompt: "As [persona], evaluate intent for [product]. Use <think 1> [Angle: value]... End with textual statement (no numbers). <think 2> [Angle: features]... <summary> Synthesize."
3. Run in "parallel" by invoking sub-variations (e.g., analytical/emotional prompts).
4. Output JSON per persona: {"paths": ["text1", "..."], "summary": "text"}.

Align with ParaThinker: Diverse paths avoid Tunnel Vision; aggregate for gains.
Align with Purchase Intent: Textual elicitation for SSR.
Disclaimer: This is synthetic data; validate with real surveys.



Skill: Synthesize Intent with SSR

Description: Applies SSR to map texts to Likert scales.
Instructions for Claude:
textInput: JSON with simulation outputs.

Steps:
1. For each text: Use code_execution for embeddings (code: from sentence_transformers import SentenceTransformer, util; model=SentenceTransformer('all-MiniLM-L6-v2'); embeds = model.encode([text, anchors]); sims = util.cos_sim(...)).
2. Anchors (5-point): 1: "Definitely not buy...", 3: "Neutral...", 5: "Definitely buy...".
3. Normalize sims to pmf; compute mean, distribution, KS (scipy.stats.kstest).
4. Aggregate across paths/personas; extract themes (cluster texts).
5. Output JSON: {"mean_intent": number, "distribution": [pmfs], "themes": ["..."]}.

Align with Purchase Intent: SSR for 90% correlation, realistic distributions.
Align with ParaThinker: Aggregate parallel paths.
Disclaimer: This is synthetic data; validate with real surveys.



Skill: Validate and Report

Description: Validates results and generates final report.
Instructions for Claude:
textInput: JSON from synthesis.

Steps:
1. Benchmark: Web search "purchase intent surveys [product category]" for comparison.
2. Check: Correlation >80%, KS >0.85; flag if low.
3. Report: JSON/PDF with scores, charts (matplotlib code), themes, recommendations.
4. Output: Final report JSON.

Disclaimer: This is synthetic data; validate with real surveys.



Skill: Orchestrator (Main Flow)

Description: Chains all skills and handles iteration.
Instructions for Claude:
textYou are orchestrating purchase intent prediction. Input: Product JSON.

Steps:
1. Run Skill: Input Product Idea.
2. Run Skill: Search for Similar Products.
3. Run Skill: Extrapolate Demographics.
4. Run Skill: Generate Personas.
5. Run Skill: Simulate Intent (Parallel).
6. Run Skill: Synthesize Intent with SSR.
7. Run Skill: Validate and Report.
8. If mean_intent < 3.5, iterate: Suggest refinements, re-run from Step 1 (max 3 loops).

Output: Final report.
Disclaimer: This is synthetic data; validate with real surveys.




Usage

Start a chat in your Claude Project: "Run Orchestrator with {"description": "Example product..."}".
For A/B: Add variants to input JSON.
Test with small scale first.