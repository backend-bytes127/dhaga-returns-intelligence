# Presentation Script — Dhaga & Co. Returns Intelligence
**Group 4 | Slot: Sat 3 Oct, 5:45–6:00 PM | Presenter: all five members**

---

## SLIDE 1 — Title (no time spent here, just up while people settle)

**Heading:** Dhaga & Co.
**Subheading:** What's hiding in the Other box
**Bottom line:** Group 4

---

## SEGMENT 1: THE PROBLEM (3 min)
*Goal: Neha and Ritu recognise their own problem in the first 60 seconds.*

---

### SLIDE 2 — The number you already argue about

**Big number, centred:**
**31%**

**Below it:**
Of every 100 orders shipped, 31 come back.

**Speaker note:**
"Ritu, you said we acquire well and retain badly. Faizan, every one of those returns costs you ₹120 in logistics before anyone asks why it happened. We are not here to talk about the return rate. We are here to talk about why nobody knows why."

---

### SLIDE 3 — The bottleneck has a name

**Left column — What the system captures:**
- Size mismatch ✓
- Quality issue ✓
- Damaged ✓
- **Other** ✗

**Right column — What "Other" actually is:**
- 44% of all returns
- ~6,500 entries every week
- Free text, often Hinglish
- Read by one person, a few hundred at a time

**Quote, bottom:**
*"Most of it is about fit, but I can only read a few hundred at a time."*
— Neha, Category Head

**Speaker note:**
"The dropdown was designed to capture structured data. 44% of customers ignored it and typed what they actually meant. Neha reads those entries manually, a batch at a time. The rest sit unread."

---

### SLIDE 4 — What unread looks like at volume

**Visual: two columns**

| This week's Other entries | What Neha sees |
|---|---|
| 6,500 returns | ~200–300 read |
| Fit issues repeating across SKU-KRT-2291 | Not visible |
| Tiruppur-V3 running consistently large | Not visible |
| Same problem in week 3, week 5, week 7 | Not visible |

**Bottom line:**
The signal exists. Nobody is reading it.

**Speaker note:**
"This is not a data problem. Dhaga has 410,000 product reviews sitting untouched for 18 months and a clean orders table with 11 million rows. The problem is that nobody has connected those signals to the question Neha is trying to answer."

---

### SLIDE 5 — The loop that keeps running

**Simple diagram — three boxes in a circle:**

`Return happens` → `Reason logged as "Other"` → `Nobody reads it at scale` → `Same product ships with same fit problem next week` → _(loop back)_

**Speaker note:**
"Because the root cause is never surfaced, it never gets fixed. The same fit issue on the same SKU from the same vendor appears in week one data and is still there in week six. This is what we chose to solve."

---

## SEGMENT 2: WHY IT MATTERS (3 min)
*Goal: give Faizan and Ritu a number they can act on. Make Dev understand it runs without an ML engineer.*

---

### SLIDE 6 — What it costs today

**Three metrics, large:**

| | |
|---|---|
| **₹15 lakh+** | Estimated weekly reverse logistics from COD returns |
| **26%** | COD return-to-origin rate (each costs ₹120 + loses a delivery slot) |
| **6 quarters** | Repeat purchase rate stuck at 22% — unresolved fit issues are a driver |

**Formula shown:**
48,000 orders/week × 31% return rate × 26% COD RTO × ₹120 = **~₹15 lakh/week**

**Speaker note:**
"Faizan, this is not an estimate we invented. It is the arithmetic from your own numbers in the brief. Every week this loop runs uninterrupted costs roughly ₹15 lakh in logistics alone — not counting the opportunity cost of the delivery slot or the customer who does not come back."

---

### SLIDE 7 — What success looks like

**We would measure it with data Dhaga already holds:**

| Metric | Source | Baseline today |
|---|---|---|
| Return rate on flagged SKUs | Orders table (11M rows, clean) | 31% overall |
| "Other" entries with structured root cause | Returns data | 0% today |
| Time from return signal to category action | Manual process | Days to weeks |

**Target:**
After 6 weeks, return rate on SKUs Neha acted on drops below category baseline.

**Speaker note:**
"We are not proposing a metric you have to start tracking. Everything we need is already in your Postgres orders table. The question is whether the signal reaches Neha before the next drop."

---

### SLIDE 8 — It runs without an ML engineer

**Three facts:**

- No model is trained. No weights to maintain.
- Neha uploads a CSV. The tool runs. She gets a dashboard.
- When the model is wrong, it says so and flags the row for her review.

**Dev's question, answered before he asks it:**
"Whoever runs this on Monday after we leave: it is a file upload and a button. No infrastructure beyond what Streamlit already provides."

**Speaker note:**
"Dev, we heard you. Sixteen engineers, no ML engineer. This tool makes one API call per return reason. It costs less per week than two reverse logistics events. A non-technical team member can operate it."

---

## SEGMENT 3: LIVE DEMO (6 min)
*Drive the deployed URL live. Show the happy path first, then deliberately show a failure.*

---

### SLIDE 9 — DEMO (just a URL on screen)

**Full screen:**
https://dhaga-returns-intelligence-gjb4edycvf6wmxypkyv4jq.streamlit.app/

**Speaker note — what to click through:**
1. Open the URL. Show it loading cold (no narration needed — the client can see it).
2. Click "Load demo data" — show the 40 rows of Hinglish returns preview.
3. Point out the metrics: 36 "Other" rows, estimated ₹15L+ logistics cost.
4. Click "Classify 36 'Other' returns" — watch the progress bar run.
5. Show the bar chart — FIT_SIZE dominant.
6. Read out one cluster insight: "Tiruppur-V3 kurtis are running 1 size large. Neha's action this week: add size-up guidance to affected listings."
7. Show the flagged-for-review table — "These 4 rows, the model said it wasn't confident enough. Neha sees them explicitly."
8. Show the download button.

**Then show the failure case on purpose:**

"Now I want to show you where it gets it wrong."

- Point to a row in the flagged table that says UNCLEAR.
- Read the original text: *"return kar do"* — "return it."
- "This tells us nothing. The system knows it tells us nothing. It does not invent a category. It flags it. That is the design — the system fails visibly, not silently."

---

### SLIDE 10 — What the output gives Neha

**Two columns:**

**Before this tool:**
- Read 200–300 Other entries manually
- No view across SKUs or vendors
- Root cause stays invisible

**After this tool:**
- 36 entries → structured in 90 seconds
- Cluster: "FIT_SIZE on Tiruppur-V3 kurtis — size chart runs 1 size large"
- Action: flag vendor, update listing
- Low-confidence rows flagged separately — Neha reviews those only

---

## SEGMENT 4: WHAT WE WOULD BUILD NEXT (2 min)
*Be honest. This scores 10 points. Judges want to see you know what you didn't build.*

---

### SLIDE 11 — What we did not build

**Three honest gaps:**

| What we skipped | What it would take |
|---|---|
| Direct connection to Freshdesk / Unicommerce | API credentials and data access from Dhaga |
| 410,000 product reviews as context | Indexed review corpus — enriches synthesis significantly |
| Vendor comparison across SKUs | Vendor PO table access — would name specific suppliers automatically |

**Speaker note:**
"We used CSV upload as a proxy for the real data integration. The pipeline logic works on real data the same way — the plumbing to connect it to Unicommerce is a week of engineering, not a research problem."

---

### SLIDE 12 — What we would want from Dhaga to go further

**Three asks — framed as questions, not demands:**

1. **Read access to the orders + returns table** — so the tool runs on live data weekly, not on exports.
2. **A pilot with Neha for 4 weeks** — she acts on the flagged SKUs, we measure whether return rate moves.
3. **One vendor's PO data** — to test whether supplier-level patterns are visible before we build across all 40.

**Closing line:**
"The signal is already in your data. We have read 36 rows of it. You have 18 months of reviews and 11 million orders that have never been asked this question."

---

## Q&A PREP — likely pushback and how to handle it

| What they'll ask | Your answer |
|---|---|
| "What happens when the model gets it wrong?" | "It tells Neha. Low-confidence rows appear in a separate flagged table. She reviews those. The tool never silently overwrites her judgment." |
| "Who operates this on Monday after you leave?" | "Anyone who can upload a CSV and click a button. No code, no model weights, no infrastructure to maintain." |
| "What does this cost us?" | "Less than ₹300/week at full Dhaga scale. That is less than three COD return logistics events. The arithmetic is in our build note." |
| "We tried something like this before and it didn't work." | "Tell us what broke — that is exactly the information we need before recommending we go further. We have built a pilot, not a production system." |
| "Is this accurate enough to trust?" | "On the demo data, roughly 90% of classifications hold up to the evaluator's second pass. The 10% that don't are flagged for review. We would want to test on 200 real 'Other' entries with Neha before claiming a production accuracy number." |

---

## SPEAKER ASSIGNMENTS (fill in with your team)

| Segment | Speaker | Time |
|---|---|---|
| Title + Problem (Slides 1–5) | Neeraj Sujan | 3 min |
| Why It Matters (Slides 6–8) | Shubham Sharma | 3 min |
| Live Demo (Slides 9–10) | Kancharla Prasad | 6 min |
| What Next (Slides 11–12) | Subhrima Raha | 2 min |
| Q&A anchor | Rohan Jain | 6 min |
