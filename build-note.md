# Build Note — Dhaga & Co. Returns Intelligence Tool

**Max two pages. This is one.**

---

## Code vs model split

| Step | Code or model | Model if used | Why |
|---|---|---|---|
| Load CSV, filter "Other" rows | Code | — | Deterministic filter; no judgment needed |
| Classify return reason text | Model | `claude-haiku-4-5-20251001` | Free text in Hinglish with messy spelling; rule-based classification would miss 70%+ of variants |
| Evaluate low-confidence results | Model | `claude-haiku-4-5-20251001` | Second LLM pass is cheaper than Sonnet and catches systematic errors from the first pass |
| Route classified rows into clusters | Code | — | `if category == X` grouping; deterministic |
| Synthesize root cause + recommendation | Model | `claude-sonnet-4-6` | Needs to reason across 8-10 varied return texts, infer root cause (vendor vs listing vs attribute), and write a specific action — this is judgment, not lookup |
| Per-SKU risk summary | Model | `claude-sonnet-4-6` | Same reasoning requirement; SKU-level patterns cross reason types |
| Cost estimate, download, flagging | Code | — | Arithmetic and display |

---

## Why each pattern is there

**Prompt chaining (classify → evaluate → synthesize):**
The classify step uses Haiku for speed and cost. But Haiku occasionally miscategorises borderline Hinglish — e.g. "elastic tight hai" going to QUALITY_DEFECT instead of FIT_SIZE. The evaluator catches this before the output reaches Neha. Sonnet only runs on the synthesized cluster, not on individual rows — that choice drives 80% of the cost saving.

**Routing (cluster by category before synthesis):**
A fit problem and a colour problem have completely different root causes and different owners (sizing charts vs photography brief). Sending all 6,500 returns to Sonnet as one blob would produce a generic summary. Routing first means each synthesis call has a coherent set of examples, which produces a specific recommended action rather than a vague observation.

**Evaluator (second Haiku pass for low-confidence):**
The boundary between FIT_SIZE and EXPECTATION_GAP is genuinely ambiguous ("length choti hai" — is the garment short, or did the listing show it longer?). Rather than letting low-confidence calls through unchecked, the evaluator flags them for Neha's review table. This is the "fails visibly" requirement from the brief: the system knows what it does not know.

---

## Cost line

| Scenario | Cost per run (USD) | At Dhaga scale |
|---|---|---|
| Demo (40 rows, 5 clusters) | ~$0.01 | — |
| One week (6,560 Other rows, 5 clusters) | ~$2.50 | ₹210/week |
| Break-even vs one returns logistics cost | — | $2.50 saves 20+ ₹120 returns = ₹2,400 |

The cost-per-week at scale is less than two COD return logistics events. Dev (CTO) asked for the arithmetic — there it is.

---

## The thing that broke that we did not expect

**The "Other" category is not a clean signal — it is a dustbin.**

We assumed most "Other" entries would be fit or size complaints, based on Neha's observation. In the demo data, roughly 55% are FIT_SIZE or EXPECTATION_GAP — that held. But a significant minority (around 10%) are genuinely uninformative: "not needed", "changed mind", "return kar do". These are UNCLEAR classifications with low confidence and the evaluator correctly flags them. We had not designed a path for this class.

What we did: added the CUSTOMER_ERROR and UNCLEAR categories and excluded them from synthesis, so Sonnet never tries to extract a root cause from noise. The flagged-for-review table gives Neha visibility without fabricating a pattern.

**What we did not build:**
- Integration with Dhaga's actual Freshdesk/Unicommerce data (we used CSV upload as a proxy)
- Connection to the 410,000 product reviews (would enrich the synthesis significantly — the next build)
- Vendor comparison across SKUs (needs the Vendor PO table, which would require access we do not have)
- Automatic listing update (customer-facing, requires the human review gate Dhaga does not yet have)
