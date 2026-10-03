"""
Dhaga & Co. Returns Intelligence Tool
======================================
Problem: 44% of returns land in free-text "Other" — Neha (Category Head)
can only read a few hundred by hand. This tool classifies them at scale,
surfaces patterns, and tells Neha exactly what to fix and where.

Patterns used:
  - Prompt chaining: classify → evaluate → synthesize (3 steps)
  - Routing: cluster by reason category before synthesis
  - Evaluator: low-confidence classifications flagged for human review

Models:
  - claude-haiku-4-5-20251001  (bulk classify + evaluate — cheap, fast)
  - claude-sonnet-4-6          (synthesize patterns + recommendations — judgment calls)
"""

import os
import pandas as pd
import streamlit as st
from collections import Counter
from openai import OpenAI

from pipeline.classifier import classify_return, evaluate_classification, route_by_category
from pipeline.analyzer import synthesize_cluster, summarize_sku

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dhaga & Co. — Returns Intelligence",
    page_icon="📦",
    layout="wide",
)

CATEGORY_COLOURS = {
    "FIT_SIZE": "#FF6B6B",
    "QUALITY_DEFECT": "#FF9F43",
    "COLOR_MISMATCH": "#54A0FF",
    "EXPECTATION_GAP": "#A29BFE",
    "DELIVERY_DAMAGE": "#FD79A8",
    "CUSTOMER_ERROR": "#55EFC4",
    "UNCLEAR": "#B2BEC3",
}

DEMO_CSV_PATH = os.path.join(os.path.dirname(__file__), "data", "sample_returns.csv")


def load_client() -> OpenAI | None:
    api_key = os.environ.get("OPENROUTER_API_KEY") or st.secrets.get("OPENROUTER_API_KEY", "")
    if not api_key:
        return None
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )


def cost_estimate(n_other_rows: int) -> dict:
    """Rough cost for one run at actual Dhaga scale (48K orders/week, 31% returns, 44% Other)."""
    weekly_other = int(48_000 * 0.31 * 0.44)
    haiku_per_row = 0.0003   # ~300 input + 150 output tokens at Haiku pricing
    sonnet_per_cluster = 0.006  # ~5 clusters per run
    run_cost = (n_other_rows * haiku_per_row * 1.5) + (5 * sonnet_per_cluster)
    weekly_cost = (weekly_other * haiku_per_row * 1.5) + (5 * sonnet_per_cluster)
    return {
        "this_run_usd": round(run_cost, 3),
        "weekly_usd": round(weekly_cost, 2),
        "weekly_other_rows": weekly_other,
    }


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://placehold.co/200x60/1a1a2e/ffffff?text=Dhaga+%26+Co.", use_container_width=True)
    st.markdown("## Returns Intelligence Tool")
    st.markdown(
        "Classifies free-text return reasons at scale so Neha's team can act on "
        "fit and sizing patterns without reading 6,500 entries by hand."
    )
    st.divider()
    st.markdown("**Models in use**")
    st.markdown("- `claude-haiku-4-5` — classify + evaluate")
    st.markdown("- `claude-sonnet-4-6` — synthesize + recommend")
    st.divider()
    st.markdown("**Patterns**")
    st.markdown("- Prompt chaining (classify → evaluate → synthesize)")
    st.markdown("- Routing (cluster by reason type)")
    st.markdown("- Evaluator (flag low-confidence rows for Neha)")

# ── Main ──────────────────────────────────────────────────────────────────────
st.title("Returns Intelligence — Dhaga & Co.")
st.caption(
    "Upload a returns export (or use demo data) to surface root causes "
    "hidden in the 'Other' free-text box. Patterns flow to Neha; cost goes to Faizan."
)

client = load_client()
if not client:
    st.warning(
        "No API key found. Set `OPENROUTER_API_KEY` in environment or Streamlit secrets. "
        "The demo data loads, but LLM processing needs the key."
    )

# ── File upload ───────────────────────────────────────────────────────────────
col_upload, col_demo = st.columns([3, 1])
with col_upload:
    uploaded = st.file_uploader(
        "Upload returns CSV",
        type="csv",
        help="Required columns: order_id, sku_id, product_name, category, vendor, return_reason_dropdown, return_reason_text",
    )
with col_demo:
    st.write("")
    use_demo = st.button("Load demo data", use_container_width=True)

df: pd.DataFrame | None = None

if uploaded:
    df = pd.read_csv(uploaded)
    st.success(f"Loaded {len(df)} rows from upload.")
elif use_demo or st.session_state.get("demo_loaded"):
    df = pd.read_csv(DEMO_CSV_PATH)
    st.session_state["demo_loaded"] = True
    st.info(f"Demo data loaded: {len(df)} rows of synthetic Dhaga & Co. returns (Hinglish).")

if df is None:
    st.stop()

# ── Data preview ──────────────────────────────────────────────────────────────
required_cols = {"return_reason_dropdown", "return_reason_text", "sku_id", "product_name", "category", "vendor"}
missing = required_cols - set(df.columns)
if missing:
    st.error(f"Missing columns: {missing}. Check your CSV format.")
    st.stop()

with st.expander("Preview raw data", expanded=False):
    st.dataframe(df, use_container_width=True)

# ── Scope ─────────────────────────────────────────────────────────────────────
other_mask = df["return_reason_dropdown"].str.lower().str.strip() == "other"
df_other = df[other_mask].copy()
df_non_other = df[~other_mask].copy()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total returns", len(df))
col2.metric("'Other' (unclassified)", len(df_other), f"{len(df_other)/len(df)*100:.0f}%")
col3.metric("Already labelled", len(df_non_other))
costs = cost_estimate(len(df_other))
col4.metric("Logistics cost (est.)", f"₹{int(len(df)*0.26*120):,}", "at ₹120/COD return")

if len(df_other) == 0:
    st.info("No 'Other' rows found. All returns already have structured labels.")
    st.stop()

# ── Run ───────────────────────────────────────────────────────────────────────
st.divider()
run_btn = st.button(
    f"Classify {len(df_other)} 'Other' returns",
    type="primary",
    disabled=client is None,
    use_container_width=True,
)

if run_btn or st.session_state.get("results"):
    if run_btn:
        rows = df_other.to_dict("records")
        classified = []
        evaluated = []

        progress = st.progress(0, text="Classifying returns with Haiku...")
        for i, row in enumerate(rows):
            c = classify_return(client, row)
            classified.append(c)
            progress.progress((i + 1) / len(rows) / 2, text=f"Classifying {i+1}/{len(rows)}...")

        progress.progress(0.5, text="Evaluating low-confidence results...")
        for i, row in enumerate(classified):
            e = evaluate_classification(client, row)
            evaluated.append(e)
            progress.progress(0.5 + (i + 1) / len(rows) / 2, text=f"Evaluating {i+1}/{len(rows)}...")

        progress.progress(1.0, text="Synthesizing patterns with Sonnet...")

        routed = route_by_category(evaluated)

        cluster_insights = []
        for cat, cat_rows in routed.items():
            if cat in ("CUSTOMER_ERROR", "UNCLEAR") or len(cat_rows) < 2:
                continue
            insight = synthesize_cluster(client, cat, cat_rows)
            cluster_insights.append(insight)

        # Per-SKU summaries for top-volume SKUs
        sku_groups: dict[str, list] = {}
        for row in evaluated:
            sku_groups.setdefault(row["sku_id"], []).append(row)
        top_skus = sorted(sku_groups.items(), key=lambda x: len(x[1]), reverse=True)[:5]
        sku_summaries = [summarize_sku(client, sku, rows) for sku, rows in top_skus]

        progress.empty()
        st.session_state["results"] = {
            "evaluated": evaluated,
            "routed": routed,
            "cluster_insights": cluster_insights,
            "sku_summaries": sku_summaries,
        }

    # ── Results ───────────────────────────────────────────────────────────────
    results = st.session_state["results"]
    evaluated = results["evaluated"]
    routed = results["routed"]
    cluster_insights = results["cluster_insights"]
    sku_summaries = results["sku_summaries"]

    st.success(f"Classified {len(evaluated)} returns. {sum(1 for r in evaluated if r.get('needs_review'))} flagged for Neha's review.")

    # Distribution chart
    st.subheader("Return reason breakdown")
    cat_counts = Counter(r.get("category", "UNCLEAR") for r in evaluated)
    chart_data = pd.DataFrame(
        {"Category": list(cat_counts.keys()), "Count": list(cat_counts.values())}
    ).sort_values("Count", ascending=False)
    st.bar_chart(chart_data.set_index("Category"))

    # Cluster insights
    st.subheader("Root cause patterns (Sonnet synthesis)")
    if cluster_insights:
        for insight in sorted(cluster_insights, key=lambda x: x.get("return_count", 0), reverse=True):
            cat = insight.get("category", "")
            colour = CATEGORY_COLOURS.get(cat, "#888")
            with st.container(border=True):
                header_col, count_col = st.columns([4, 1])
                with header_col:
                    st.markdown(f"### {cat.replace('_', ' ').title()}")
                with count_col:
                    st.metric("Returns", insight.get("return_count", 0))

                st.markdown(f"**Pattern:** {insight.get('pattern_summary', '')}")
                st.markdown(f"**Root cause:** {insight.get('likely_root_cause', '')}")
                st.markdown(f"**Attribute gap:** {insight.get('attribute_gap', '')}")
                st.success(f"**Action for Neha this week:** {insight.get('recommended_action', '')}")
                cost_inr = insight.get("estimated_weekly_cost_inr", 0)
                if cost_inr:
                    st.caption(f"Est. weekly logistics cost from this cluster: ₹{int(cost_inr):,}")
    else:
        st.info("Not enough returns per category to synthesize patterns. Upload a larger export.")

    # Per-SKU risk table
    st.subheader("Top-volume SKU risk summary")
    if sku_summaries:
        priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        sku_summaries_sorted = sorted(sku_summaries, key=lambda x: priority_order.get(x.get("priority", "LOW"), 2))
        for s in sku_summaries_sorted:
            priority = s.get("priority", "MEDIUM")
            icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(priority, "⚪")
            with st.container(border=True):
                st.markdown(f"{icon} **{s.get('sku_id', '')}** — {priority} priority")
                st.markdown(s.get("risk_summary", ""))

    # Needs-review table
    flagged = [r for r in evaluated if r.get("needs_review")]
    if flagged:
        st.subheader(f"Flagged for manual review ({len(flagged)} rows)")
        st.caption("Confidence below 60% — Neha should verify these before acting.")
        flagged_df = pd.DataFrame(flagged)[
            ["order_id", "sku_id", "return_reason_text", "category", "final_confidence", "sub_label"]
        ]
        st.dataframe(flagged_df, use_container_width=True)

    # Full classified export
    st.subheader("Download classified returns")
    full_classified = pd.DataFrame(evaluated)
    csv_bytes = full_classified.to_csv(index=False).encode()
    st.download_button(
        "Download CSV",
        data=csv_bytes,
        file_name="dhaga_returns_classified.csv",
        mime="text/csv",
        use_container_width=True,
    )

    # Cost transparency
    st.divider()
    st.subheader("Cost transparency (for Dev, CTO)")
    c1, c2, c3 = st.columns(3)
    c1.metric("This run (USD)", f"${costs['this_run_usd']:.3f}")
    c2.metric("At Dhaga scale/week (USD)", f"${costs['weekly_usd']:.2f}")
    c3.metric("Weekly 'Other' returns at scale", f"{costs['weekly_other_rows']:,}")
    st.caption(
        "Haiku at ~$0.0003/row for classify + evaluate. "
        "Sonnet at ~$0.006 per category cluster (5 clusters typical). "
        "Weekly figure assumes 48K orders, 31% return rate, 44% landing in Other."
    )
