# Morning Test Guide - Playwright Validation & 3-Level Drill-Down

**Date:** 2025-10-24 (for next session)
**Purpose:** Validate Playwright CSV parsing + Demonstrate complete "Rule of One" workflow
**Estimated Time:** 30-40 minutes

---

## Pre-Test Checklist ✅

**Before starting:**
- [ ] Rate limits reset (waited 4+ hours since last test)
- [ ] Dashboard from previous test closed
- [ ] Terminal ready in project directory
- [ ] Coffee ☕ (optional but recommended)

**Verify installation:**
```bash
# Should show version 1.55.0
playwright --version

# Should show chromium installed
playwright show-trace
```

---

## Test 1: CSV Parsing Validation (5 minutes)

### **Goal:** Verify Playwright can download and parse Google Trends CSVs

**Command:**
```bash
cd D:\Projects\Ai\Purchase-Intent
python agents/agent_0/main.py --method playwright "cooking recipes"
```

### **What to Watch For:**

**✅ Success Indicators:**
```
[OK] LED 570: scrape_keyword_start
[OK] LED 571: browser_launch
[OK] LED 572: navigate_to_url
[OK] LED 573: cookie_consent_accepted (or not_found - both OK)
[OK] LED 574: export_buttons_found, count: 4
[OK] LED 575: download_csv_start (×4 times)
[OK] LED 576: csv_saved (×4 times)
[OK] LED 580-589: CSV parsing breadcrumbs
[OK] LED 593: conversion_complete
Quality Score: 100%
```

**❌ Failure Indicators:**
```
[OK] LED 577: rate_limit_429_detected
[FAIL] LED 577: Max retries exceeded
```
**If this happens:** Wait another hour, try again

### **Expected Output:**

**Console:**
```
[*] Using Playwright browser automation
============================================================
Querying Google Trends (batched - 1 topics)...
============================================================
[OK] Composite Score: 75.32 (Confidence: 100%)

Top Topics:
  1. cooking recipes - Score: 75.32
```

**Dashboard:**
- Opens in browser automatically
- Shows 1 bubble labeled "cooking recipes"
- Bubble positioned based on demand/competition scores
- Tooltip shows detailed metrics

### **Validation Checklist:**

- [ ] No 429 rate limit errors
- [ ] 4 CSVs downloaded (check `cache/playwright/cooking_recipes/`)
- [ ] LED breadcrumbs 570-599 all fired
- [ ] Dashboard displays correctly
- [ ] Score looks reasonable (demand + competition + opportunity)

**If all ✅ → Playwright is 100% validated! Proceed to Test 2.**

---

## Test 2: 3-Level Drill-Down Workflow (30 minutes)

### **Goal:** Demonstrate complete "Rule of One" niche discovery

---

### **Level 1: Broad Discovery** 🔍

**Topic:** Choose something you're interested in (examples below)

**Command:**
```bash
python agents/agent_0/main.py --drill-down "meditation" --method playwright
```

**Alternative topics:**
- `"productivity tips"`
- `"healthy recipes"`
- `"romance novels"`
- `"fitness routines"`

**What Happens:**
1. Generates 10 subtopics (pattern-based fallback)
2. Researches each with Playwright
3. Shows dashboard with 10 bubbles

**Time:** ~5-10 minutes

**Expected Output:**
```
============================================================
Generated 10 Subtopics:
============================================================
  1. guided meditation techniques
  2. mindfulness meditation practice
  3. sleep meditation methods
  4. body scan meditation
  5. loving-kindness meditation
  6. meditation for anxiety
  7. transcendental meditation
  8. zen meditation practice
  9. yoga meditation fusion
  10. manifestation meditation
============================================================

[*] Starting research on all 10 subtopics...
[*] This will take approximately 2.3 minutes
```

**Dashboard Shows:**
- 10 bubbles scattered by demand/competition
- Color-coded by opportunity score
- Tooltip with detailed metrics

---

### **Level 1: Review Dashboard** 📊

**What to Look For:**

**Demand (Y-axis):**
- **High (80-100):** Strong validated demand ✅
- **Medium (60-80):** Good demand signals ✅
- **Low (<60):** Weak demand ⚠️

**Competition (X-axis):**
- **Low (0-30):** Market gap opportunity! 🟢
- **Moderate (30-50):** Differentiation needed 🟡
- **High (50-70):** Strong positioning required 🟠
- **Very High (70+):** Saturated market 🔴

**Opportunity Score (Bubble Color):**
- **Green:** High priority - pursue!
- **Yellow:** Viable with effort
- **Blue:** Risky - need unique angle
- **Red:** Avoid

**Pick Your Top 3-5:**
```
Based on dashboard, I'll focus on:
1. "sleep meditation methods" (High demand, Low competition)
2. "meditation for anxiety" (High demand, Moderate competition)
3. "guided meditation techniques" (Very high demand, Moderate competition)
```

---

### **Level 2: Deep Validation** 🎯

**Command:**
```bash
python agents/agent_0/main.py --method playwright \
  "sleep meditation methods" \
  "meditation for anxiety" \
  "guided meditation techniques"
```

**What Happens:**
1. Deep research on your 3 chosen subtopics
2. More detailed competitive analysis
3. Dashboard with 3 bubbles (more accurate)

**Time:** ~1-2 minutes

**Expected Output:**
```
============================================================
Researching topic 1/3: sleep meditation methods
============================================================
  [OK] Composite Score: 87.45 (Confidence: 100%)

============================================================
Researching topic 2/3: meditation for anxiety
============================================================
  [OK] Composite Score: 82.30 (Confidence: 100%)

============================================================
Researching topic 3/3: guided meditation techniques
============================================================
  [OK] Composite Score: 79.15 (Confidence: 100%)

Top Topics:
  1. sleep meditation methods - Score: 87.45
  2. meditation for anxiety - Score: 82.30
  3. guided meditation techniques - Score: 79.15
```

---

### **Level 2: Select Winner** 🏆

**Decision Criteria:**

**Look at Opportunity Score:**
```
sleep meditation methods:
  Demand: 92.3
  Competition: 28.5
  Opportunity: 66.1 ← HIGHEST!
  Recommendation: HIGH PRIORITY 🟢

meditation for anxiety:
  Demand: 88.7
  Competition: 45.2
  Opportunity: 48.6
  Recommendation: VIABLE 🟡

guided meditation techniques:
  Demand: 95.2
  Competition: 62.8
  Opportunity: 35.4
  Recommendation: RISKY 🔵
```

**Winner:** "sleep meditation methods" (highest opportunity score)

**Why:**
- Strong demand (92.3)
- Low competition (28.5)
- Market gap opportunity!

---

### **Level 3: Ultra-Specific Niche** 🔬

**Command:**
```bash
python agents/agent_0/main.py --drill-down "sleep meditation methods" --method playwright
```

**What Happens:**
1. Generates 10 ultra-specific sub-niches
2. Researches each thoroughly
3. Final dashboard with "Rule of One" candidates

**Time:** ~5-10 minutes

**Expected Subtopics:**
```
Generated 10 Subtopics:
1. guided sleep meditation for insomnia
2. body scan sleep meditation
3. sleep meditation for anxiety relief
4. yoga nidra sleep meditation
5. sleep meditation rain sounds
6. sleep meditation for deep rest
7. sleep meditation breath work
8. sleep meditation visualization
9. sleep meditation for lucid dreaming
10. sleep meditation morning routine
```

**Dashboard Shows:**
- 10 ultra-specific bubbles
- Clear winner(s) with low competition
- Data to validate niche viability

---

### **Level 3: Final Selection** ✨

**Pick Your "Rule of One" Niche:**

**Example Decision:**
```
Winner: "guided sleep meditation for insomnia"

Why:
✅ Demand: 78.5 (good)
✅ Competition: 22.3 (LOW - market gap!)
✅ Opportunity: 61.2 (HIGH PRIORITY)
✅ Specific audience: People with insomnia
✅ Clear pain point: Can't sleep
✅ Actionable: Can create targeted ebook/course
✅ Brian Moran approved: Specific enough to dominate
```

**This is your niche!** 🎯

---

## Test Results Documentation

### **Create Test Report:**

**File:** `Context/2025-10-24/Playwright-Test-Results.md`

**Template:**
```markdown
# Playwright Test Results - 2025-10-24

## Test 1: CSV Parsing Validation
- Status: ✅ PASS / ❌ FAIL
- Rate Limits: Encountered? Yes/No
- CSVs Downloaded: X/4
- Quality Score: XX%
- Issues: None / [describe]

## Test 2: 3-Level Drill-Down

### Level 1: Broad Discovery
- Primary Topic: "meditation"
- Subtopics Generated: 10
- Time: X minutes
- Top 3 Picks:
  1. sleep meditation methods
  2. meditation for anxiety
  3. guided meditation techniques

### Level 2: Deep Validation
- Topics Researched: 3
- Winner: "sleep meditation methods"
- Opportunity Score: 66.1
- Time: X minutes

### Level 3: Ultra-Specific
- Primary Topic: "sleep meditation methods"
- Subtopics Generated: 10
- Final Selection: "guided sleep meditation for insomnia"
- Opportunity Score: 61.2
- Time: X minutes

## Overall Assessment
- Playwright Performance: Excellent / Good / Poor
- Rate Limit Handling: Working as expected
- CSV Parsing: Validated ✅
- Workflow Usability: Smooth / Issues
- Next Steps: [Ready for production / Need fixes]
```

---

## Quick Reference Commands

### **Single Topic Research:**
```bash
python agents/agent_0/main.py --method playwright "topic name"
```

### **Multiple Topics:**
```bash
python agents/agent_0/main.py --method playwright \
  "topic1" "topic2" "topic3"
```

### **Drill-Down (Generate Subtopics):**
```bash
python agents/agent_0/main.py --drill-down "topic" --method playwright
```

### **Fallback to PyTrends (if Playwright fails):**
```bash
python agents/agent_0/main.py "topic name"
# (no --method flag = uses pytrends)
```

---

## Troubleshooting

### **Still Getting 429 Errors:**

**Problem:** Rate limits haven't reset yet

**Solution:**
```bash
# Check how long since last test
# Wait another hour
# Or test with previously cached topics:
python agents/agent_0/main.py --method playwright \
  "billionaire romance novels"  # We cached this earlier
```

### **CSV Download Fails:**

**Check LED breadcrumbs:**
```
[OK] LED 574: export_buttons_found, count: ?
```
- If count = 0 → Page structure changed (Google updated HTML)
- If count = 4 → Buttons found, download issue
- Check `cache/playwright/[topic_name]/` for CSV files

**Solution:** Use fallback to pytrends for that topic

### **Browser Doesn't Launch:**

**Error:** `playwright executable not found`

**Solution:**
```bash
playwright install chromium
```

### **Parser Errors (LED 580-589):**

**Check specific LED:**
- 581: Interest Over Time parsing issue
- 582: Related Queries parsing issue
- 583: Related Topics parsing issue
- 584: Interest By Region parsing issue

**Solution:** Check CSV file manually in `cache/playwright/` to see format

---

## Success Criteria

**By end of morning test, you should have:**

- [x] ✅ Playwright 100% validated (CSVs download/parse correctly)
- [x] ✅ Complete 3-level workflow demonstrated
- [x] ✅ Data-backed "Rule of One" niche selected
- [x] ✅ Confidence in production usage
- [x] ✅ Understanding of rate limit behavior

**If all ✅ → Ready for production niche research!**

---

## Next Steps After Validation

### **Production Workflow:**

**Daily Niche Research:**
```bash
# Morning: Explore 3-5 general topics
python agents/agent_0/main.py --drill-down "topic1" --method playwright
python agents/agent_0/main.py --drill-down "topic2" --method playwright
python agents/agent_0/main.py --drill-down "topic3" --method playwright

# Review dashboards, pick winners

# Afternoon: Deep dive on top 3-5 from each
python agents/agent_0/main.py --method playwright \
  "winner1a" "winner1b" "winner2a" "winner2b" "winner3a"

# Select THE ONE, ultra-specific drill-down
python agents/agent_0/main.py --drill-down "THE_WINNER" --method playwright

# Final selection: Your "Rule of One" niche!
```

**Weekly Capacity:**
- ~60-100 niches researched per week
- 3-5 "Rule of One" niches validated with data
- No guessing, all data-backed decisions

---

## Files to Review After Test

**Check these for insights:**

1. **Dashboard:** `outputs/agent0-dashboard.html`
   - Visual representation
   - Bubble positions (demand vs competition)
   - Tooltip details

2. **JSON Output:** `outputs/topic-selection.json`
   - Raw data for analysis
   - Export to spreadsheet if needed

3. **LED Breadcrumbs:** Console output
   - Shows exact execution flow
   - Identifies bottlenecks
   - Debug any issues

4. **Downloaded CSVs:** `cache/playwright/[topic]/`
   - Raw Google Trends data
   - Verify parsing worked correctly

---

## Time Budget

**Total Session:** ~40 minutes

| Phase | Time | Activity |
|-------|------|----------|
| Test 1 | 5 min | CSV parsing validation |
| Level 1 | 10 min | Broad discovery (10 topics) |
| Review 1 | 5 min | Analyze dashboard, pick top 3-5 |
| Level 2 | 2 min | Deep validation (3-5 topics) |
| Review 2 | 3 min | Select winner |
| Level 3 | 10 min | Ultra-specific (10 sub-niches) |
| Review 3 | 5 min | Final "Rule of One" selection |

**Total:** ~40 minutes to go from "meditation" → "guided sleep meditation for insomnia"

---

## Final Notes

**Remember:**
- ✅ Rate limits reset overnight (should have clean slate)
- ✅ First query validates CSV parsing
- ✅ Playwright is already installed and working
- ✅ LED breadcrumbs show exactly what's happening
- ✅ Cache helps with repeated topics

**You're looking for:**
- High demand (80+)
- Low competition (20-40)
- High opportunity score (60+)
- Specific, actionable niche

**Have fun finding your first data-backed "Rule of One" niche!** 🚀

---

**Questions during test?**
- Check LED breadcrumbs first (they tell you exactly what happened)
- Review this guide's Troubleshooting section
- Check `Playwright-Implementation-Summary.md` for technical details
