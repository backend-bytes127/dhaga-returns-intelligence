"""Generate the Dhaga & Co. presentation deck as a .pptx file."""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
import copy

# Brand colours
DARK_BG   = RGBColor(0x1A, 0x1A, 0x2E)   # near-black navy
ACCENT    = RGBColor(0xFF, 0x6B, 0x6B)   # coral-red
WHITE     = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_GREY= RGBColor(0xCC, 0xCC, 0xCC)
GOLD      = RGBColor(0xFF, 0xD7, 0x00)

W = Inches(13.33)  # widescreen 16:9 width
H = Inches(7.5)


def new_prs() -> Presentation:
    prs = Presentation()
    prs.slide_width  = W
    prs.slide_height = H
    return prs


def blank_slide(prs: Presentation):
    blank_layout = prs.slide_layouts[6]  # completely blank
    return prs.slides.add_slide(blank_layout)


def bg(slide, colour: RGBColor = DARK_BG):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = colour


def add_text(slide, text: str, left, top, width, height,
             size=28, bold=False, colour=WHITE, align=PP_ALIGN.LEFT, italic=False):
    txb = slide.shapes.add_textbox(left, top, width, height)
    tf  = txb.text_frame
    tf.word_wrap = True
    p   = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size   = Pt(size)
    run.font.bold   = bold
    run.font.color.rgb = colour
    run.font.italic = italic
    return txb


def add_rect(slide, left, top, width, height, colour: RGBColor):
    shape = slide.shapes.add_shape(1, left, top, width, height)  # MSO_SHAPE.RECTANGLE
    shape.fill.solid()
    shape.fill.fore_color.rgb = colour
    shape.line.fill.background()
    return shape


def accent_bar(slide, width=Inches(1.8)):
    add_rect(slide, Inches(0.5), Inches(6.9), width, Pt(4), ACCENT)


# ── Slide builders ────────────────────────────────────────────────────────────

def slide_title(prs):
    s = blank_slide(prs)
    bg(s)
    # big title
    add_text(s, "Dhaga & Co.", Inches(0.8), Inches(1.8), Inches(11), Inches(1.5),
             size=64, bold=True, colour=WHITE, align=PP_ALIGN.CENTER)
    add_text(s, "What's hiding in the Other box",
             Inches(0.8), Inches(3.1), Inches(11), Inches(0.8),
             size=28, colour=LIGHT_GREY, align=PP_ALIGN.CENTER)
    add_text(s, "Group 4",
             Inches(0.8), Inches(5.8), Inches(11), Inches(0.5),
             size=18, colour=ACCENT, align=PP_ALIGN.CENTER)
    add_rect(s, Inches(4.5), Inches(4.6), Inches(4.3), Pt(3), ACCENT)


def slide_big_number(prs):
    s = blank_slide(prs)
    bg(s)
    add_text(s, "31%", Inches(0.8), Inches(1.0), Inches(11), Inches(2.5),
             size=144, bold=True, colour=ACCENT, align=PP_ALIGN.CENTER)
    add_text(s, "Of every 100 orders shipped, 31 come back.",
             Inches(0.8), Inches(3.6), Inches(11), Inches(0.8),
             size=28, colour=WHITE, align=PP_ALIGN.CENTER)
    add_text(s, "We are not here to talk about the return rate.\nWe are here to talk about why nobody knows why.",
             Inches(1.2), Inches(4.6), Inches(10.5), Inches(1.4),
             size=20, colour=LIGHT_GREY, align=PP_ALIGN.CENTER, italic=True)
    accent_bar(s, Inches(2.0))


def slide_other_box(prs):
    s = blank_slide(prs)
    bg(s)
    add_text(s, "The bottleneck has a name", Inches(0.5), Inches(0.3),
             Inches(12), Inches(0.7), size=36, bold=True, colour=WHITE)
    accent_bar(s)

    # Left box
    add_rect(s, Inches(0.5), Inches(1.3), Inches(5.5), Inches(4.5), RGBColor(0x2A,0x2A,0x45))
    add_text(s, "What the system captures", Inches(0.7), Inches(1.4), Inches(5.0), Inches(0.5),
             size=16, bold=True, colour=ACCENT)
    for i, (label, ok) in enumerate([("Size mismatch","✓"),("Quality issue","✓"),("Damaged","✓"),("Other","✗")]):
        colour = ACCENT if label == "Other" else RGBColor(0x55,0xEF,0xC4)
        add_text(s, f"{ok}  {label}", Inches(0.8), Inches(2.0 + i*0.7), Inches(4.8), Inches(0.6),
                 size=20, colour=colour, bold=(label=="Other"))

    # Right box
    add_rect(s, Inches(6.8), Inches(1.3), Inches(6.0), Inches(4.5), RGBColor(0x2A,0x2A,0x45))
    add_text(s, '"Other" in reality', Inches(7.0), Inches(1.4), Inches(5.5), Inches(0.5),
             size=16, bold=True, colour=ACCENT)
    facts = ["44% of all returns","~6,500 entries every week","Free text — often Hinglish","Read by hand, a few hundred at a time"]
    for i, f in enumerate(facts):
        add_text(s, f"•  {f}", Inches(7.0), Inches(2.0 + i*0.75), Inches(5.5), Inches(0.65),
                 size=20, colour=WHITE)

    add_text(s, '"Most of it is about fit, but I can only read a few hundred at a time."  — Neha, Category Head',
             Inches(0.5), Inches(6.1), Inches(12.3), Inches(0.7), size=15, colour=LIGHT_GREY, italic=True)


def slide_volume(prs):
    s = blank_slide(prs)
    bg(s)
    add_text(s, "What unread looks like at volume", Inches(0.5), Inches(0.3),
             Inches(12), Inches(0.7), size=36, bold=True, colour=WHITE)
    accent_bar(s)

    headers = ["This week's Other entries", "What Neha sees"]
    rows = [
        ("6,500 returns arrive",         "~200–300 read"),
        ("Fit issues on SKU-KRT-2291",   "Not visible"),
        ("Tiruppur-V3 runs large",        "Not visible"),
        ("Problem repeats week 5, 7, 9", "Not visible"),
    ]
    col_x = [Inches(0.5), Inches(7.0)]
    col_w = Inches(6.0)

    for j, h in enumerate(headers):
        add_text(s, h, col_x[j], Inches(1.2), col_w, Inches(0.5),
                 size=18, bold=True, colour=ACCENT)

    for i, (left, right) in enumerate(rows):
        y = Inches(1.9 + i * 0.9)
        add_rect(s, Inches(0.5), y, Inches(12.3), Inches(0.75),
                 RGBColor(0x28,0x28,0x48) if i % 2 == 0 else RGBColor(0x22,0x22,0x3E))
        add_text(s, left,  col_x[0], y + Pt(6), col_w, Inches(0.65), size=18, colour=WHITE)
        colour = ACCENT if right == "Not visible" else RGBColor(0x55,0xEF,0xC4)
        add_text(s, right, col_x[1], y + Pt(6), col_w, Inches(0.65), size=18, colour=colour, bold=(right=="Not visible"))

    add_text(s, "The signal exists. Nobody is reading it.",
             Inches(0.5), Inches(6.0), Inches(12.3), Inches(0.7),
             size=22, bold=True, colour=GOLD, align=PP_ALIGN.CENTER)


def slide_loop(prs):
    s = blank_slide(prs)
    bg(s)
    add_text(s, "The loop that keeps running", Inches(0.5), Inches(0.3),
             Inches(12), Inches(0.7), size=36, bold=True, colour=WHITE)
    accent_bar(s)

    steps = ["Return\nhappens", "Logged as\n\"Other\"", "Nobody reads\nat scale", "Same product\nships again"]
    xs = [Inches(0.7), Inches(3.7), Inches(6.7), Inches(9.7)]
    for i, (step, x) in enumerate(zip(steps, xs)):
        add_rect(s, x, Inches(2.5), Inches(2.6), Inches(1.8), RGBColor(0x2A,0x2A,0x50))
        add_text(s, step, x + Inches(0.1), Inches(2.65), Inches(2.4), Inches(1.5),
                 size=18, bold=True, colour=WHITE, align=PP_ALIGN.CENTER)
        if i < 3:
            add_text(s, "→", x + Inches(2.6), Inches(3.1), Inches(0.5), Inches(0.7),
                     size=32, colour=ACCENT, align=PP_ALIGN.CENTER)

    # loop-back arrow label
    add_text(s, "↑ ─────────────────── loop ─────────────────── ↓",
             Inches(0.7), Inches(4.5), Inches(12.0), Inches(0.5),
             size=16, colour=LIGHT_GREY, align=PP_ALIGN.CENTER)

    add_text(s, "This is what we chose to solve.",
             Inches(0.5), Inches(5.5), Inches(12.3), Inches(0.7),
             size=22, bold=True, colour=ACCENT, align=PP_ALIGN.CENTER)


def slide_cost(prs):
    s = blank_slide(prs)
    bg(s)
    add_text(s, "What it costs today", Inches(0.5), Inches(0.3),
             Inches(12), Inches(0.7), size=36, bold=True, colour=WHITE)
    accent_bar(s)

    metrics = [
        ("₹15 lakh+", "Estimated weekly reverse logistics from COD returns"),
        ("26%",        "COD return-to-origin rate — each costs ₹120 + loses a delivery slot"),
        ("6 quarters", "Repeat purchase stuck at 22% — unresolved fit issues are a driver"),
    ]
    for i, (num, label) in enumerate(metrics):
        y = Inches(1.4 + i * 1.6)
        add_rect(s, Inches(0.5), y, Inches(12.3), Inches(1.35), RGBColor(0x22,0x22,0x3E))
        add_text(s, num,   Inches(0.8), y + Pt(8), Inches(3.5), Inches(1.1),
                 size=44, bold=True, colour=ACCENT)
        add_text(s, label, Inches(4.5), y + Pt(18), Inches(8.0), Inches(0.9),
                 size=20, colour=WHITE)

    add_text(s, "48,000 orders/week  ×  31% returns  ×  26% COD RTO  ×  ₹120  =  ₹15 lakh/week",
             Inches(0.5), Inches(6.15), Inches(12.3), Inches(0.6),
             size=15, colour=LIGHT_GREY, italic=True, align=PP_ALIGN.CENTER)


def slide_success(prs):
    s = blank_slide(prs)
    bg(s)
    add_text(s, "What success looks like", Inches(0.5), Inches(0.3),
             Inches(12), Inches(0.7), size=36, bold=True, colour=WHITE)
    accent_bar(s)

    headers = ["Metric", "Source", "Today"]
    rows = [
        ("Return rate on flagged SKUs", "Orders table (11M rows, clean)", "31% overall"),
        ('"Other" entries with root cause', "Returns data", "0% today"),
        ("Time from signal to action", "Manual process", "Days to weeks"),
    ]
    col_x = [Inches(0.5), Inches(5.5), Inches(9.5)]
    col_w = [Inches(4.8), Inches(3.8), Inches(3.2)]

    for j, h in enumerate(headers):
        add_text(s, h, col_x[j], Inches(1.3), col_w[j], Inches(0.5),
                 size=16, bold=True, colour=ACCENT)

    for i, row in enumerate(rows):
        y = Inches(2.0 + i * 1.1)
        add_rect(s, Inches(0.5), y, Inches(12.3), Inches(0.95),
                 RGBColor(0x28,0x28,0x48) if i%2==0 else RGBColor(0x22,0x22,0x3E))
        for j, cell in enumerate(row):
            add_text(s, cell, col_x[j] + Inches(0.1), y + Pt(8), col_w[j], Inches(0.8),
                     size=17, colour=WHITE)

    add_text(s, "Target: after 6 weeks, return rate on actioned SKUs falls below category baseline.",
             Inches(0.5), Inches(5.5), Inches(12.3), Inches(0.7),
             size=20, bold=True, colour=GOLD, align=PP_ALIGN.CENTER)
    add_text(s, "All measurement uses data Dhaga already holds. No new tracking required.",
             Inches(0.5), Inches(6.2), Inches(12.3), Inches(0.55),
             size=16, colour=LIGHT_GREY, italic=True, align=PP_ALIGN.CENTER)


def slide_no_ml(prs):
    s = blank_slide(prs)
    bg(s)
    add_text(s, "It runs without an ML engineer", Inches(0.5), Inches(0.3),
             Inches(12), Inches(0.7), size=36, bold=True, colour=WHITE)
    accent_bar(s)

    points = [
        ("No model is trained.", "No weights to maintain. No infrastructure to manage."),
        ("Neha uploads a CSV.", "The tool runs. She gets a dashboard in under 2 minutes."),
        ("When it's wrong, it says so.", "Low-confidence rows are flagged for Neha's review — never silently passed through."),
    ]
    for i, (bold_part, rest) in enumerate(points):
        y = Inches(1.6 + i * 1.6)
        add_rect(s, Inches(0.5), y, Inches(12.3), Inches(1.3), RGBColor(0x22,0x22,0x3E))
        add_text(s, bold_part, Inches(0.8), y + Pt(6), Inches(11.5), Inches(0.55),
                 size=22, bold=True, colour=ACCENT)
        add_text(s, rest, Inches(0.8), y + Pt(32), Inches(11.5), Inches(0.7),
                 size=18, colour=LIGHT_GREY)

    add_text(s, "For Dev, CTO: whoever runs this on Monday after we leave — it is a file upload and a button.",
             Inches(0.5), Inches(6.3), Inches(12.3), Inches(0.55),
             size=15, colour=LIGHT_GREY, italic=True, align=PP_ALIGN.CENTER)


def slide_demo(prs):
    s = blank_slide(prs)
    bg(s)
    add_text(s, "LIVE DEMO", Inches(0.8), Inches(1.5), Inches(11.5), Inches(1.5),
             size=72, bold=True, colour=ACCENT, align=PP_ALIGN.CENTER)
    add_text(s, "dhaga-returns-intelligence-gjb4edycvf6wmxypkyv4jq.streamlit.app",
             Inches(0.8), Inches(3.2), Inches(11.5), Inches(0.8),
             size=20, colour=LIGHT_GREY, align=PP_ALIGN.CENTER)
    add_text(s, "We will show you where it gets it wrong — on purpose.",
             Inches(0.8), Inches(4.5), Inches(11.5), Inches(0.7),
             size=22, colour=WHITE, align=PP_ALIGN.CENTER, italic=True)


def slide_output(prs):
    s = blank_slide(prs)
    bg(s)
    add_text(s, "What the output gives Neha", Inches(0.5), Inches(0.3),
             Inches(12), Inches(0.7), size=36, bold=True, colour=WHITE)
    accent_bar(s)

    before = [
        "Read 200–300 Other entries manually",
        "No view across SKUs or vendors",
        "Root cause stays invisible",
        "Same fix needed next week",
    ]
    after = [
        "36 entries → structured in 90 seconds",
        "Cluster: FIT_SIZE on Tiruppur-V3 kurtis",
        "Action: flag vendor, update listing",
        "Low-confidence rows separated for review",
    ]

    for col, (heading, items, colour) in enumerate([
        ("Before", before, RGBColor(0xFF,0x6B,0x6B)),
        ("After this tool", after, RGBColor(0x55,0xEF,0xC4)),
    ]):
        x = Inches(0.5 + col * 6.5)
        add_rect(s, x, Inches(1.2), Inches(6.0), Inches(5.5), RGBColor(0x22,0x22,0x3E))
        add_text(s, heading, x + Inches(0.2), Inches(1.3), Inches(5.5), Inches(0.6),
                 size=22, bold=True, colour=colour)
        for i, item in enumerate(items):
            add_text(s, f"•  {item}", x + Inches(0.2), Inches(2.1 + i * 1.0),
                     Inches(5.5), Inches(0.85), size=18, colour=WHITE)


def slide_next(prs):
    s = blank_slide(prs)
    bg(s)
    add_text(s, "What we did not build", Inches(0.5), Inches(0.3),
             Inches(12), Inches(0.7), size=36, bold=True, colour=WHITE)
    accent_bar(s)

    rows = [
        ("Direct integration with Unicommerce / Freshdesk",
         "API credentials and data access from Dhaga"),
        ("410,000 product reviews as synthesis context",
         "Indexed review corpus — enriches root cause significantly"),
        ("Vendor comparison across all 40 suppliers",
         "Vendor PO table access — would name specific suppliers automatically"),
    ]
    for i, (what, need) in enumerate(rows):
        y = Inches(1.4 + i * 1.6)
        add_rect(s, Inches(0.5), y, Inches(12.3), Inches(1.3), RGBColor(0x22,0x22,0x3E))
        add_text(s, what, Inches(0.8), y + Pt(4), Inches(11.5), Inches(0.55),
                 size=19, bold=True, colour=ACCENT)
        add_text(s, f"What it would take: {need}", Inches(0.8), y + Pt(30),
                 Inches(11.5), Inches(0.65), size=16, colour=LIGHT_GREY)

    add_text(s, "We built a pilot. Not a production system. That distinction is intentional.",
             Inches(0.5), Inches(6.3), Inches(12.3), Inches(0.55),
             size=16, colour=GOLD, italic=True, align=PP_ALIGN.CENTER)


def slide_asks(prs):
    s = blank_slide(prs)
    bg(s)
    add_text(s, "Three things we would want from Dhaga", Inches(0.5), Inches(0.3),
             Inches(12), Inches(0.7), size=34, bold=True, colour=WHITE)
    accent_bar(s, Inches(4.5))

    asks = [
        ("01", "Read access to orders + returns table",
         "So the tool runs on live data weekly — not on CSV exports."),
        ("02", "A 4-week pilot with Neha",
         "She acts on flagged SKUs. We measure whether return rate moves."),
        ("03", "One vendor's PO data",
         "To test whether supplier-level patterns are visible before we build across all 40."),
    ]
    for i, (num, ask, detail) in enumerate(asks):
        y = Inches(1.5 + i * 1.6)
        add_text(s, num, Inches(0.5), y, Inches(0.9), Inches(1.4),
                 size=48, bold=True, colour=ACCENT)
        add_text(s, ask, Inches(1.6), y + Pt(4), Inches(10.7), Inches(0.6),
                 size=22, bold=True, colour=WHITE)
        add_text(s, detail, Inches(1.6), y + Pt(34), Inches(10.7), Inches(0.7),
                 size=17, colour=LIGHT_GREY)



# ── Build the deck ────────────────────────────────────────────────────────────

prs = new_prs()

slide_title(prs)
slide_big_number(prs)
slide_other_box(prs)
slide_volume(prs)
slide_loop(prs)
slide_cost(prs)
slide_success(prs)
slide_no_ml(prs)
slide_demo(prs)
slide_output(prs)
slide_next(prs)
slide_asks(prs)

out = "dhaga-returns-intelligence.pptx"
prs.save(out)
print(f"Saved: {out}  ({len(prs.slides)} slides)")
