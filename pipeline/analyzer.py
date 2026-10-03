"""
Analyzer: uses a stronger model (via OpenRouter) to synthesize patterns across
a cluster of classified returns and generate actionable recommendations.
Pattern: prompt chaining step 3 — receives routed clusters, outputs structured insights.
"""

import json
from openai import OpenAI

# Stronger model for judgment calls — synthesis and recommendations
STRONG_MODEL = "anthropic/claude-sonnet-4.6"

SYNTHESIS_PROMPT = """You are a returns analyst presenting findings to Neha (Category Head) at Dhaga & Co.

You have {count} returns all classified as: {category}
Sub-labels observed: {sub_labels}

Sample return texts (Hinglish, verbatim):
{sample_texts}

SKUs affected: {sku_list}
Vendors involved: {vendor_list}

Synthesize into a JSON report with these exact keys:
- pattern_summary: one sentence describing the root problem in plain language
- top_sku: SKU with the most returns in this cluster
- likely_root_cause: vendor issue, attribute gap, listing error, or sizing standard
- attribute_gap: specific product attribute that is wrong or missing
- recommended_action: one concrete action Neha can take this week
- estimated_weekly_cost_inr: int (use Rs.120 per COD return, 61% of all returns are COD)

Return ONLY valid JSON."""

SKU_SUMMARY_PROMPT = """You are summarizing return risk for one SKU at Dhaga & Co.

SKU: {sku_id} — {product_name} (Category: {category}, Vendor: {vendor})
Total returns in this upload: {total_returns}
Return reasons breakdown: {reasons_breakdown}

Write a 2-sentence SKU risk summary for Neha:
- Name the dominant problem
- State what should change (listing, size chart, or supplier flag)

Return ONLY valid JSON with keys: sku_id, risk_summary, priority (HIGH/MEDIUM/LOW)"""


def synthesize_cluster(client: OpenAI, category: str, rows: list[dict]) -> dict:
    """Synthesize a cluster of same-category returns into a pattern + recommendation."""
    sub_labels = list({r.get("sub_label", "") for r in rows if r.get("sub_label")})
    sample_texts = "\n".join(f"- {r.get('return_reason_text', '')}" for r in rows[:8])
    sku_list = list({r.get("sku_id", "") for r in rows})
    vendor_list = list({r.get("vendor", "") for r in rows})

    response = client.chat.completions.create(
        model=STRONG_MODEL,
        max_tokens=500,
        temperature=0.3,
        messages=[{
            "role": "user",
            "content": SYNTHESIS_PROMPT.format(
                count=len(rows),
                category=category,
                sub_labels=", ".join(sub_labels) if sub_labels else "varied",
                sample_texts=sample_texts,
                sku_list=", ".join(sku_list),
                vendor_list=", ".join(vendor_list),
            )
        }],
    )

    raw = (response.choices[0].message.content or "").strip()
    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        result = {
            "pattern_summary": raw[:200],
            "top_sku": sku_list[0] if sku_list else "unknown",
            "likely_root_cause": "parse error — check raw output",
            "attribute_gap": "",
            "recommended_action": "",
            "estimated_weekly_cost_inr": 0,
        }
    return {"category": category, "return_count": len(rows), **result}


def summarize_sku(client: OpenAI, sku_id: str, rows: list[dict]) -> dict:
    """Generate a per-SKU risk summary for high-volume SKUs."""
    product_name = rows[0].get("product_name", "Unknown")
    category = rows[0].get("category", "Unknown")
    vendor = rows[0].get("vendor", "Unknown")
    reasons = {}
    for r in rows:
        cat = r.get("category", "UNCLEAR")
        reasons[cat] = reasons.get(cat, 0) + 1

    response = client.chat.completions.create(
        model=STRONG_MODEL,
        max_tokens=200,
        temperature=0.2,
        messages=[{
            "role": "user",
            "content": SKU_SUMMARY_PROMPT.format(
                sku_id=sku_id,
                product_name=product_name,
                category=category,
                vendor=vendor,
                total_returns=len(rows),
                reasons_breakdown=json.dumps(reasons),
            )
        }],
    )

    raw = (response.choices[0].message.content or "").strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"sku_id": sku_id, "risk_summary": raw[:200], "priority": "MEDIUM"}
