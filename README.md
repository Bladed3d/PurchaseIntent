# Purchase Intent System

AI-powered "synthetic focus group" that predicts consumer purchase likelihood by simulating hundreds of virtual customers with realistic demographics.

## 🎯 Project Goal

Build a system that delivers both quantitative ratings and qualitative feedback in minutes at **12,000x lower cost** than traditional human focus groups while achieving **7-12% higher accuracy**.

## 🏗️ Architecture

**5-Agent Modular System:**

```
USER NICHE → Agent 0 (Topic Research)
          → Agent 1 (Product Research)
          → Agent 2 (Demographics Analysis)
          → Agent 3 (Persona Generation)
          → Agent 4 (Intent Simulation)
          → REPORT
```

### Agent Overview

| Agent | Purpose | LED Range | Output |
|-------|---------|-----------|--------|
| **Agent 0** | Topic Research | 500-599 | 5-10 ranked ebook topics by demand |
| **Agent 1** | Product Research | 1500-1599 | Comparable products + data sources |
| **Agent 2** | Demographics | 2500-2599 | Customer profiles (validated via triangulation) |
| **Agent 3** | Persona Generator | 3500-3599 | 100-500 synthetic personas (reusable) |
| **Agent 4** | Intent Simulator | 4500-4599 | Purchase intent predictions + recommendations |

## 🔬 Research Foundation

- **SSR (Semantic Similarity Rating)**: 90% correlation with human responses
- **ParaThinker**: 8 parallel reasoning paths, eliminates tunnel vision
- **Triangulation Validation**: Cross-validate demographics from 3+ sources (78-85% accuracy)

## 💡 Key Innovation

Instead of asking AI "Rate this 1-5" (unrealistic distributions), we:
1. Generate 8 independent reasoning paths per persona
2. Use semantic embeddings to map text to intent scores
3. Achieve realistic distributions matching human surveys

## 🚀 Current Status

**Phase:** Architecture & Research Complete

**Ready to Build:**
- ✅ Complete 5-agent design (see `Docs/4-agents-design.md`)
- ✅ Data gathering research (Reddit PRAW, YouTube API, Playwright)
- ✅ LED breadcrumb instrumentation defined
- ✅ Validation methodology established

**Next Steps:**
1. Build Agent 0 (Topic Research) - Week 1 MVP
2. Build Agents 1-3 (Product → Demographics → Personas) - Weeks 2-3
3. Build Agent 4 (ParaThinker Intent Simulator) - Weeks 4-5

## 📊 Cost Model

**Beta Phase (Current):**
- **$0 per product test** (using Claude Code subscription)
- Unlimited testing during development

**Future (if scaling):**
- Optional API-based SaaS with metered pricing
- Estimated: $1.05-$1.15 per first run, $0.50 per persona reuse

**vs Traditional:**
- Human focus group: $5,000-20,000 per product
- Savings: **12,000x during beta**

## 🎓 Use Cases

### Primary: Book Title Testing
Test 70+ book titles to find optimal one (real case study: author increased sales significantly)

### Other Applications:
- Product concepts validation
- Ad copy testing
- Pricing strategy
- Audience segmentation
- Market research at scale

## 📁 Project Structure

```
Purchase-Intent/
├── .claude/
│   ├── agents/          # prd-simplifier, session-summarizer
│   └── commands/        # /end-session
├── Context/
│   └── 2025-10-22/
│       └── COMBINED-SESSION-HANDOFF.md  # Session decisions
├── Docs/
│   ├── 4-agents-design.md              # Complete architecture (v2.0)
│   ├── Research-customer-data01.md     # Data gathering research
│   ├── PurchaseIntent-overview.md      # Project vision
│   └── ANTI-OVER-ENGINEERING-GUIDE.md  # Development philosophy
└── CLAUDE.md                            # Development guidelines

```

## 🛠️ Tech Stack

**Data Gathering:**
- Reddit API (PRAW) - 60 req/min free tier
- YouTube Data API v3 - 10k quota/day
- Playwright - Amazon/Goodreads scraping

**Processing:**
- Claude API - Demographic extraction
- Sentence Transformers - Clustering
- ParaThinker - 8-path parallel reasoning

**Storage:**
- JSON files - Persona inventory
- Git - Version control

## 📖 Key Documents

- **[5-Agent Architecture](Docs/4-agents-design.md)** - Complete technical specification
- **[Research Report](Docs/Research-customer-data01.md)** - Data gathering tools & methods
- **[Session Handoff](Context/2025-10-22/COMBINED-SESSION-HANDOFF.md)** - Development decisions
- **[Anti-Over-Engineering Guide](Docs/ANTI-OVER-ENGINEERING-GUIDE.md)** - Development philosophy

## 🤝 Contributing

This is currently a solo project in active development. See `CLAUDE.md` for development guidelines.

## 📄 License

[Add your license here]

## 🔗 Links

- **Research Papers:**
  - SSR: `Docs/LLM-Predict-Purchase-Intent.pdf`
  - ParaThinker: `Docs/ParaThinker.pdf`
- **GitHub:** https://github.com/Bladed3d/PurchaseIntent

---

**Built with [Claude Code](https://claude.com/claude-code)**
