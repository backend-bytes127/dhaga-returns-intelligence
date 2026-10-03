"""
Classifier: uses a cheap fast model (via OpenRouter) to classify free-text return reasons.
Pattern: prompt chaining — raw text → structured reason category + sub-label.
Evaluator pattern: low-confidence results get a second pass before reaching Neha.
"""

import json
from openai import OpenAI

# Cheap model for bulk work — classification and evaluation
CHEAP_MODEL = "anthropic/claude-haiku-4.5"

REASON_CATEGORIES = [
    "FIT_SIZE",        # garment does not fit; size runs large/small vs size chart
    "QUALITY_DEFECT",  # stitching, fabric, pilling, structural damage
    "COLOR_MISMATCH",  # delivered colour differs from product image
    "EXPECTATION_GAP", # design feature differs from listing (length, sleeve, neckline, detail)
    "DELIVERY_DAMAGE", # item physically damaged during shipping
    "CUSTOMER_ERROR",  # customer explicitly acknowledges ordering wrong size/item
    "UNCLEAR",         # not enough information to classify
]

CLASSIFY_PROMPT = """You are a returns analyst for Dhaga & Co., a D2C fashion brand.
A customer submitted a return reason as "Other" with this free-text explanation:

<return_text>
{text}
</return_text>

Product: {product_name} (Category: {category}, Vendor: {vendor})

Classify into exactly ONE category:
- FIT_SIZE: garment does not fit; size runs large or small vs size chart
- QUALITY_DEFECT: stitching defect, fabric quality, pilling, structural damage
- COLOR_MISMATCH: colour delivered differs from product image/description
- EXPECTATION_GAP: design feature differs from listing (length, neckline, sleeve, embroidery etc.)
- DELIVERY_DAMAGE: item physically damaged during shipping or handling
- CUSTOMER_ERROR: customer explicitly acknowledges ordering wrong size or item
- UNCLEAR: not enough information to classify

Also extract:
1. sub_label: specific issue (e.g. "runs large", "seam split", "shade mismatch", "length shorter than shown")
2. confidence: 0-100

Return ONLY valid JSON with keys: category, sub_label, confidence, brief_evidence (quote key phrase)"""

EVALUATE_PROMPT = """You are a QA reviewer for a returns classifier.

Return text: {text}
Classified as: {category} ({sub_label})
Initial confidence: {confidence}

Is this classification correct? If wrong, name the correct category.
Return ONLY valid JSON: {{is_correct: bool, final_confidence: int, correction: null or correct category}}"""


def classify_return(client: OpenAI, row: dict) -> dict:
    """Prompt chain step 1: classify one Other-reason return using cheap model."""
    text = row.get("return_reason_text", "").strip()
    if not text:
        return {**row, "category": "UNCLEAR", "sub_label": "no text", "confidence": 0, "brief_evidence": ""}

    response = client.chat.completions.create(
        model=CHEAP_MODEL,
        max_tokens=300,
        temperature=0,
        messages=[{
            "role": "user",
            "content": CLASSIFY_PROMPT.format(
                text=text,
                product_name=row.get("product_name", "Unknown"),
                category=row.get("category", "Unknown"),
                vendor=row.get("vendor", "Unknown"),
            )
        }],
    )

    raw = (response.choices[0].message.content or "").strip()
    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        result = {"category": "UNCLEAR", "sub_label": "parse error", "confidence": 0, "brief_evidence": ""}

    return {**row, **result}


def evaluate_classification(client: OpenAI, classified_row: dict) -> dict:
    """Evaluator pattern: second cheap-model pass for borderline results."""
    initial_conf = classified_row.get("confidence", 0)

    # Only spend tokens on borderline cases
    if initial_conf >= 80:
        return {**classified_row, "final_confidence": initial_conf, "needs_review": False}

    response = client.chat.completions.create(
        model=CHEAP_MODEL,
        max_tokens=150,
        temperature=0,
        messages=[{
            "role": "user",
            "content": EVALUATE_PROMPT.format(
                text=classified_row.get("return_reason_text", ""),
                category=classified_row.get("category", "UNCLEAR"),
                sub_label=classified_row.get("sub_label", ""),
                confidence=initial_conf,
            )
        }],
    )

    raw = (response.choices[0].message.content or "").strip()
    try:
        ev = json.loads(raw)
    except json.JSONDecodeError:
        ev = {"is_correct": True, "final_confidence": initial_conf, "correction": None}

    if ev.get("correction"):
        classified_row = {**classified_row, "category": ev["correction"]}

    final_conf = ev.get("final_confidence", initial_conf)
    return {**classified_row, "final_confidence": final_conf, "needs_review": final_conf < 60}


def route_by_category(classified_rows: list[dict]) -> dict[str, list[dict]]:
    """Router pattern: group classified returns by category for downstream synthesis."""
    routed: dict[str, list[dict]] = {}
    for row in classified_rows:
        cat = row.get("category", "UNCLEAR")
        routed.setdefault(cat, []).append(row)
    return routed
