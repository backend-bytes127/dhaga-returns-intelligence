# Discovery Note — Dhaga & Co. Engagement
**Date:** Sat 3 Oct 2026  
**Group:** Neeraj Sujan  
**Status:** Agreed before first commit

---

## 1. The problem in one sentence

Neha and her category team cannot read the 44% of return reasons that land in the free-text "Other" box at scale, so the fit and size problems that drive Dhaga's 31% return rate keep repeating across the same SKUs week after week.

---

## 2. Who owns it today, and what they do instead

**Primary owner:** Neha, Category Head.  
Today she reads the "Other" box by hand, a few hundred entries per batch, and flags patterns informally to suppliers. She has no structured view across the 6,500+ returns that land in "Other" every week. Faizan (Supply Chain) absorbs the logistics cost — ₹120 per COD return-to-origin — but has no visibility into why those returns happen at the product level.

---

## 3. Evidence from the brief

- Returns are 31% overall (Neha, Section 05). Of those, 44% land in "Other" (Section 04, Returns data).
- COD return-to-origin is 26% (Faizan, Section 05). Each costs ₹120 in logistics and burns a delivery slot (Faizan, Section 05).
- 410,000 product reviews, 18 months deep, are displayed on the app and never analysed (Section 04, Reviews row: "Nobody reads them. They are displayed and never analysed").
- The catalogue has 60-odd attributes per SKU but size charts differ per vendor and colour is typed 90 different ways (Section 04, Catalogue row) — the attribute data needed to link returns to specific product or supplier issues exists but is not connected.
- Neha says: "most of it is about fit, but I can only read a few hundred at a time" — confirming both the signal and the bottleneck.

---

## 4. What it costs them today

At 48,000 orders/week and a 31% return rate, roughly 14,900 returns arrive each week. Of those, 44% (~6,560) land in "Other" — unread.

- **Direct logistics cost:** 26% COD RTO × 48,000 × ₹120 = approximately **₹15 lakh per week** in reverse logistics alone.
- **Opportunity cost:** each RTO burns a delivery slot that could carry a new order.
- **Repeat cost:** because root causes are not read at scale, the same fit and sizing problems recur across new drops. A problem visible in week 1 data is still present in week 6 because nobody surfaced it.

This is a number Neha and Faizan both argue about in the same meeting, which means fixing it does not require organisational alignment to begin.

---

## 5. What success looks like

**Metric they already hold:** return rate per SKU per week (in the 11M-row orders table, clean and trustworthy).

**Success definition:** After six weeks of using the tool, the return rate on SKUs flagged with fit or size issues in week 1 has dropped, because Neha acted on the attribute gaps surfaced. Specifically: return rate on actioned SKUs falls below the baseline for that category.

**Measurable with data they have:** Orders table (return flag + reason), Catalogue table (SKU attributes), Vendor PO records (supplier origin). No new data collection required.

---

## 6. Ranked shortlist of four problems

| Rank | Problem | Owner | Ranked above the next because |
|---|---|---|---|
| **1** | 44% of return reasons are unread "Other" free text; fit and sizing root causes repeat week over week | Neha + Faizan | Two owners lose something measurable today. The fix uses data that already exists and is untouched (410K reviews, 11M orders). Cost is quantified, not estimated. Internal only — no customer-facing risk, no ML engineer needed to operate it. |
| **2** | Catalogue takes 6-9 days from sample to live; drop calendar slips = Tuesday traffic spike lost | Vivek | Vivek is the clear owner and the cost is visible (lost Tuesday revenue). But the build requires vision model calls on product images, human review loops, and attribute schema cleanup — more moving parts for one week. Ranked below #1 because the data (messy colour fields, vendor-specific size charts) needs pre-processing before an LLM is useful. |
| **3** | 58% of support tickets are WISMO (where is my order); agents copy-paste 4 replies; avg first response 9 hours | Arpita | The pain is real and the volume is high, but this is customer-facing output. The brief constraint ("safe to publish unread, or has a human review step designed on purpose") and Hinglish input complexity make a reliable MVP harder to ship in one week. Ranked below #2 because a broken WISMO bot actively damages customer trust in a way a broken returns classifier does not. |
| **4** | Repeat purchase rate stuck at 22% for 6 quarters; CAC up 40% YoY | Ritu + Sameer | Existential problem but no single lever. "Improve retention" is a programme, not a feature. No MVP built in one week can move a metric that has been flat for six quarters. Ranked last because there is no clear build target at this scope. |

---

## 7. Biggest assumption, and what would prove it wrong

**Assumption:** The "Other" free text contains enough structured signal — consistently typed return reasons, even in Hinglish — that an LLM can classify it into five to six reliable categories (fit, size, quality, expectation, delivery damage) at better than random accuracy.

**What would prove it wrong:** A sample of 200 "Other" entries that are predominantly uninformative, contradictory, or so sparse (one or two words) that classification confidence is below 60% on more than half of them. If Neha's statement that "most of it is about fit" is wrong and the text is actually noise, the core value proposition collapses.

**How we would test it before building further:** Export 200 real "Other" entries, run the classifier, review the low-confidence outputs with Neha, and decide whether to proceed, narrow scope, or redesign.
