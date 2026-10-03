# Dhaga & Co. Returns Intelligence Tool

**Problem solved:** 44% of Dhaga's returns land in a free-text "Other" box. Neha (Category Head) can only read a few hundred by hand per week. This tool classifies all of them, surfaces the root causes, and tells her exactly what to fix — without hiring an ML engineer.

**Live URL:** _(deployed link goes here — use HuggingFace Spaces or Railway)_

---

## What it does

1. You upload a CSV of returns (or load demo data with synthetic Hinglish entries).
2. The tool filters rows where `return_reason_dropdown == Other`.
3. Each "Other" row is classified into one of six reason categories using `claude-haiku-4-5`.
4. Low-confidence results are re-evaluated by a second Haiku call (evaluator pattern).
5. Results are routed into clusters by reason type (routing pattern).
6. Each cluster is synthesized by `claude-sonnet-4-6` into a root cause + recommended action.
7. Top-volume SKUs get individual risk summaries.
8. Neha can download the fully classified CSV and act on the flagged rows.

---

## Patterns used

| Pattern | Where | Why |
|---|---|---|
| Prompt chaining | classify → evaluate → synthesize | Each step narrows the problem; downstream steps receive cleaner signal |
| Routing | `route_by_category()` in classifier.py | Different reason types (fit vs quality vs colour) need different diagnostic questions |
| Evaluator | `evaluate_classification()` in classifier.py | Low-confidence calls from Haiku get a second pass before reaching Neha |

---

## How to run locally

```bash
# 1. Clone the repo
git clone https://github.com/neerajsujan/dhaga-returns-intelligence
cd dhaga-returns-intelligence

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set your OpenRouter API key
export OPENROUTER_API_KEY=your_openrouter_key_here

# 5. Run
streamlit run app.py
```

The app opens at `http://localhost:8501`. Click "Load demo data" to run without uploading a file.

---

## What it expects

**CSV columns required:**

| Column | Description |
|---|---|
| `order_id` | Unique order identifier |
| `sku_id` | Product SKU |
| `product_name` | Human-readable product name |
| `category` | womenswear / kidswear / mens |
| `vendor` | Vendor identifier (e.g. Tiruppur-V3) |
| `return_reason_dropdown` | Dropdown value — rows with "Other" are processed |
| `return_reason_text` | Free-text reason (can be Hinglish or English) |

Rows where `return_reason_dropdown` is not "Other" are counted but not processed by the LLM — this keeps cost proportional to the actual problem.

---

## What it does when something goes wrong

| Failure | Behaviour |
|---|---|
| API key missing | Orange warning banner. Demo data still loads; LLM button is disabled. |
| JSON parse error from model | Row is classified as UNCLEAR, flagged for review, never silently dropped. |
| Low-confidence result | Evaluator pass runs; if still below 60%, row appears in the "Flagged for review" table for Neha. |
| No "Other" rows in upload | Informational message; no LLM calls made, no cost incurred. |
| Model API error | Streamlit shows the error. No partial results are shown as complete. |

---

## Cost

| Scenario | Cost |
|---|---|
| This demo (40 rows) | ~$0.01 |
| One week at Dhaga scale (~6,500 Other rows) | ~$2.50 |
| One year at Dhaga scale | ~$130 |

Both models used: `claude-haiku-4-5-20251001` (classify + evaluate) and `claude-sonnet-4-6` (synthesize + recommend). Haiku earns its place on volume; Sonnet earns its place on judgment.

---

## Project structure

```
.
├── app.py                  # Streamlit entry point
├── pipeline/
│   ├── classifier.py       # Haiku: classify + evaluate + route
│   └── analyzer.py         # Sonnet: synthesize clusters + SKU summaries
├── data/
│   └── sample_returns.csv  # Synthetic demo data (Hinglish return reasons)
├── requirements.txt
├── .env.example
├── discovery-note.md       # Phase 1 deliverable
└── build-note.md           # Phase 2 deliverable
```
