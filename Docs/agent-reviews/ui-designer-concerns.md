# UI Designer - PRD Review Concerns

**PRD Version:** 2.0
**Reviewer:** UI Designer Agent
**Date:** 2025-10-23
**Focus:** Agent 0 HTML Dashboard Implementation Readiness

---

## CRITICAL CONCERNS (Blocking Implementation)

### 1. Missing Visual Design Specification for Dashboard Components
**PRD Reference:** Lines 78-88 (Phase 1 dashboard description)

**Problem:** The PRD describes WHAT to show ("bar chart of scores, trend lines, evidence cards") but provides zero design guidance on HOW to show it:
- No color palette specified for demand score thresholds (high vs. medium vs. low)
- No typography hierarchy defined (heading sizes, body text, labels)
- No spacing/layout specification (card dimensions, chart sizing, whitespace)
- No interaction state designs (hover, active, selected states for topics)

**Impact:** Without design specifications, each developer will implement differently. Creates inconsistent UX and requires rework when design decisions are finally made.

**Needed:**
```
Visual Design System Specification:
- Color palette (primary, secondary, semantic colors for scores)
- Typography scale (H1-H4, body, labels with font sizes/weights)
- Spacing system (8px grid? Component padding/margins?)
- Component dimensions (evidence card size, chart height)
- Interaction states (default, hover, focus, active, selected)
```

### 2. Insufficient Chart.js Implementation Details
**PRD Reference:** Lines 79, 399 (Chart.js visualizations)

**Problem:** "Visual charts (bar chart of scores, trend lines showing momentum)" is too vague for implementation:
- Which Chart.js chart types? (bar + line combo chart? separate charts?)
- How do bar chart and trend line interact visually? (overlay? side-by-side?)
- What data format feeds each chart? (x-axis labels, y-axis scales)
- Are charts interactive? (tooltips on hover? click-to-select from chart?)
- Responsive behavior? (chart resizes on window resize? mobile adaptation?)

**Impact:** Developer will make arbitrary chart type decisions that may not match user expectations or accessibility requirements.

**Needed:**
```
Chart Specifications:
- Chart type selection with rationale (e.g., horizontal bar for top 10 topics)
- Data schema for each chart (JSON structure with labels/values)
- Interactive features (tooltips, click handlers, animations)
- Accessibility features (ARIA labels, keyboard navigation for chart elements)
- Responsive breakpoints (desktop primary, tablet secondary)
```

### 3. "Evidence Cards" Design Completely Unspecified
**PRD Reference:** Line 80 ("Evidence cards for each topic")

**Problem:** Zero information about evidence card structure, content, or visual design:
- What information appears on each card? (just the 3 sources listed? metrics? dates?)
- How are cards laid out? (grid? list? accordion? tabs?)
- How do cards relate to the selected topic? (expand on click? always visible? sidebar?)
- Visual hierarchy within cards? (what's emphasized - search volume? engagement? authority?)

**Impact:** Cannot design cards without knowing content structure. This is a critical component for user decision-making.

**Needed:**
```
Evidence Card Specification:
- Content structure (data fields to display per source)
- Layout pattern (card grid, list, or detail panel)
- Visual hierarchy (primary/secondary/tertiary information)
- Interaction model (click to expand? static display?)
- Relationship to topic selection (pre-selection vs post-selection view)
```

### 4. Click-to-Select Interaction Pattern Underspecified
**PRD Reference:** Line 81 ("User clicks preferred topic to select")

**Problem:** Where does the user click? How does selection feedback work?
- Click the bar in the chart? Click the topic name? Click an entire evidence card?
- What visual feedback indicates selection? (highlight? checkmark? border change?)
- Can user change selection before submitting? (radio button pattern? toggle?)
- How does selection trigger the save to JSON? (submit button? auto-save on click?)

**Impact:** Unclear interaction model leads to confused users and inconsistent implementation.

**Needed:**
```
Interaction Flow Specification:
1. User views topics (initial state)
2. User hovers over topic X (hover state visual feedback)
3. User clicks topic X (click target specification - where exactly?)
4. System shows selection feedback (selected state visual design)
5. User confirms/submits selection OR changes mind (deselect pattern?)
6. System saves to JSON (loading indicator? success message?)
```

---

## MODERATE CONCERNS (Should Address)

### 5. Keyboard Navigation Details Missing
**PRD Reference:** Line 84 ("keyboard navigation for accessibility")

**Problem:** "Keyboard navigation" mentioned but not specified:
- What's the tab order? (topics first? charts first? evidence cards?)
- How does keyboard selection work? (Tab to focus + Enter to select? Arrow keys?)
- Focus indicators designed? (outline style, color, thickness)
- Keyboard shortcuts? (numbers 1-10 to select topics? Escape to cancel?)

**Recommendation:** Define complete keyboard interaction model aligned with WCAG 2.1 AA requirements (referenced line 443).

### 6. Performance Target Lacks Breakdown
**PRD Reference:** Line 86 ("<2 second load, interactive immediately")

**Problem:** "Interactive immediately" is subjective. What does this mean?
- Does it mean HTML renders in <2s with charts loading progressively?
- Or does it mean ALL charts fully rendered and interactive in <2s?
- What if data fetch takes longer than 2s? (loading states? skeleton screens?)
- What's the perceived performance target vs actual load time?

**Recommendation:** Break down into measurable metrics:
```
Performance Targets:
- Initial HTML render: <500ms (First Contentful Paint)
- Charts interactive: <2s (Time to Interactive)
- Data fetch timeout: 5s max (with loading indicator)
- Chart animation duration: <300ms (perceived as instant)
```

### 7. Browser Compatibility Strategy Vague
**PRD Reference:** Line 87 ("Chrome/Edge (primary), Firefox/Safari (secondary)")

**Problem:** What does "secondary" mean for Firefox/Safari?
- Must it work perfectly? Or just "good enough"?
- Are Chart.js features cross-browser tested? (some chart types have rendering issues)
- What about browser-specific bugs? (flexbox differences, font rendering)
- Testing strategy? (manual test in 4 browsers? automated Playwright tests?)

**Recommendation:** Define compatibility tiers:
```
Tier 1 (Must be perfect): Chrome 120+, Edge 120+
Tier 2 (Must be functional): Firefox 115+, Safari 17+
Tier 3 (Best effort): Older versions, mobile browsers
Known limitations: [list Chart.js browser quirks]
```

### 8. Visual Hierarchy Guidance for "Demand Score" Missing
**PRD Reference:** Line 79 ("Top 5-10 topics ranked by composite demand score")

**Problem:** How do we visually communicate score importance?
- Are scores color-coded? (green = high demand, yellow = medium, red = low?)
- Do we show absolute scores? Relative rankings? Both?
- How granular are scores? (0-100? 1-5 stars? percentages?)
- What's the threshold for "high demand" vs "medium" vs "low"?

**Recommendation:** Define score visualization system:
```
Score Display:
- Format: 0-100 scale with color coding
- Thresholds: 80-100 (green, high), 50-79 (blue, medium), <50 (gray, low)
- Visual weight: Larger text/bolder for higher scores
- Context: Show relative ranking (e.g., "#1" badge on top topic)
```

### 9. Responsive Design Spec Insufficient
**PRD Reference:** Line 86 (performance target mentions desktop focus, but no responsive spec)

**Problem:** Dashboard must work on different screen sizes, but no guidance provided:
- What's the minimum supported screen width? (1024px? 1280px?)
- How do charts adapt to smaller screens? (stack vertically? horizontal scroll?)
- How do evidence cards reflow? (grid to single column?)
- Mobile behavior? (PRD says "CLI only" but dashboard is HTML - does it work on tablet?)

**Recommendation:** Define responsive breakpoints and behavior:
```
Breakpoints:
- Desktop: 1440px+ (primary design target)
- Laptop: 1024-1439px (charts resize, same layout)
- Tablet: 768-1023px (single column layout)
- Mobile: <768px (not optimized, basic functionality only)
```

---

## QUESTIONS NEEDING CLARIFICATION

### 10. Chart.js Version and CDN Strategy
**Question:** Which Chart.js version should be used? (v3.x vs v4.x have breaking changes)
**Why it matters:** Affects syntax, features, and accessibility capabilities.
**Recommendation:** Specify version and loading strategy (CDN link vs npm package).

### 11. Data Refresh Interaction
**Question:** Can users refresh data while viewing dashboard? Or is it static once loaded?
**Why it matters:** Affects UI design (need refresh button? loading states? cache indicators?).
**PRD Gap:** Line 89 says "deliverable: topic-selection.json" but doesn't specify if dashboard is one-time or interactive.

### 12. Error State Design
**Question:** What happens if API calls fail during Agent 0 execution?
**Why it matters:** PRD mentions "graceful degradation" (line 121) but no UI design for partial results.
**Needed:** Error state designs for:
- Total failure (no data loaded)
- Partial failure (missing Google Trends but Reddit/YouTube loaded)
- Stale data (cached results shown with warning)

### 13. Topic Selection Persistence
**Question:** Can user navigate away from dashboard and return to see previous selection?
**Why it matters:** Affects state management and localStorage usage.
**PRD Gap:** JSON save is specified but not browser-based state persistence.

### 14. Jinja2 Template Pattern Assumption
**PRD Reference:** Line 203 ("Jinja2 template for HTML report")

**Question:** Does a Jinja2 template pattern already exist in the codebase to reuse?
**Why it matters:** PRD says "reuse HTML template pattern if exists" but provides no fallback spec if it doesn't exist.
**Needed:** Either reference existing template OR provide minimal template structure specification.

---

## POSITIVE OBSERVATIONS

### What's Well-Specified:

1. **Clear User Journey** (Lines 72-81)
   - Phase 1 workflow is well-documented (command → research → dashboard → selection)
   - Deliverable format specified (JSON structure and file path)
   - Success criteria clear (user selects topic, system saves it)

2. **Performance Target Stated** (Line 86)
   - "<2 second load" is measurable
   - "Interactive immediately" shows intent (even if definition needs work)
   - Desktop-first approach (1440px+) aligns with target user (professional researchers)

3. **Accessibility Mentioned** (Line 443, Line 84)
   - WCAG 2.1 AA compliance requirement is excellent
   - Keyboard navigation acknowledged as requirement
   - Screen reader compatibility mentioned
   - Alt text for charts specified

4. **Data Sources Clear** (Lines 74-77)
   - Three data sources explicitly named (Google Trends, Reddit, YouTube)
   - API implementation details provided (lines 115-121)
   - Content for evidence cards is derivable from API response structure

5. **Technology Choice Justified** (Lines 399-400)
   - Chart.js rationale clear (lightweight, no heavy framework)
   - Auto-open browser pattern specified (webbrowser.open())
   - HTML dashboard vs terminal UI decision well-reasoned

6. **Browser Compatibility Prioritized** (Line 87)
   - Primary browsers identified (Chrome/Edge)
   - Secondary browsers acknowledged (Firefox/Safari)
   - Desktop focus appropriate for use case

---

## IMPLEMENTATION READINESS ASSESSMENT

**Status:** NOT READY FOR IMPLEMENTATION (65% complete)

**Blocking Gaps:**
1. Visual design system (colors, typography, spacing) - CRITICAL
2. Chart.js specification (chart types, data schema, interactions) - CRITICAL
3. Evidence card design (structure, layout, content) - CRITICAL
4. Click-to-select interaction model (click targets, feedback, states) - CRITICAL

**Recommended Next Steps:**

1. **Create Visual Design Spec (2-4 hours)**
   - Define color palette and semantic color usage
   - Specify typography scale and hierarchy
   - Design component states (hover, focus, active, selected)
   - Document spacing system (padding, margins, gutters)

2. **Design Chart Mockup (1-2 hours)**
   - Sketch/wireframe showing chart types and layout
   - Define data-to-visual mapping (how scores become bar heights)
   - Specify interactive features (tooltips, click handlers)
   - Document accessibility features (ARIA labels, keyboard nav)

3. **Design Evidence Card Component (1 hour)**
   - Define card content structure (which metrics to show)
   - Specify card layout (grid dimensions, internal hierarchy)
   - Design interaction pattern (click to expand? static display?)

4. **Document Interaction Flow (1 hour)**
   - Create step-by-step interaction diagram
   - Define all UI states (initial, hover, selected, loading, success, error)
   - Specify keyboard interaction model
   - Document state transitions and feedback

**Estimated Spec Completion Time:** 5-8 hours

**Alternative Approach (Anti-Over-Engineering):**
If time is constrained, create MINIMAL functional dashboard first:
- Simple HTML table with topic names and scores (no Chart.js initially)
- Radio buttons for selection (standard HTML pattern)
- Single "Submit" button to save JSON
- Iterate UP by adding charts/cards after core functionality validated

This gets Agent 0 to IMPLEMENTED status quickly while design details are refined in parallel.

---

## NOTES FOR PROJECT MANAGER

**Handoff Recommendation:**
Before assigning to Lead Programmer, either:

**Option A (Design-First):**
1. Assign to UI Designer Agent for 5-8 hours to create complete visual spec
2. Then assign to Lead Programmer with full design documentation
3. Result: Higher quality, less rework, but longer timeline

**Option B (Anti-Over-Engineering):**
1. Assign to Lead Programmer with instruction to build MINIMAL functional dashboard
2. Get to IMPLEMENTED status quickly (HTML table + radio buttons)
3. Assign to UI Designer to enhance in iteration 2 (add Chart.js visualizations)
4. Result: Faster MVP, incremental polish, aligns with "start simple" principle

**My Recommendation:** Option B
- Rationale: PRD emphasizes quality but CLAUDE.md emphasizes "start simple"
- Agent 0 is first in pipeline - validate data research logic before polishing UI
- User can select topics from HTML table just as effectively as fancy charts
- Chart.js can be added in iteration 2 after confirming Agent 0's data quality

---

**END OF UI DESIGNER REVIEW**
