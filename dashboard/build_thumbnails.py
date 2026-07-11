"""
RHP Executive Status – Slide Thumbnail Generator
Produces dashboard/slides/slide_N.png  (1280×720 each) using Pillow only.
"""

from PIL import Image, ImageDraw, ImageFont
import os, textwrap

OUT_DIR = "dashboard/slides"
os.makedirs(OUT_DIR, exist_ok=True)

W, H = 1280, 720

# ── Palette ──────────────────────────────────────────────────────────────────
BG      = (15, 17, 23)
SURFACE = (26, 29, 39)
SURF2   = (34, 38, 58)
BORDER  = (46, 51, 80)
WHITE   = (255, 255, 255)
MUTED   = (143, 150, 179)
ACCENT  = (79, 142, 247)
GREEN   = (34, 197, 94)
YELLOW  = (245, 158, 11)
RED     = (239, 68, 68)
PURPLE  = (168, 85, 247)
GDIM    = (22, 91, 53)
YDIM    = (120, 75, 5)
RDIM    = (122, 29, 29)
BDIM    = (30, 58, 122)

def alpha(rgb, a):
    return rgb + (a,)

# ── Font helpers ──────────────────────────────────────────────────────────────
_font_cache = {}
def font(size, bold=False):
    key = (size, bold)
    if key not in _font_cache:
        try:
            path = "/usr/share/fonts/truetype/dejavu/DejaVuSans{}.ttf".format("-Bold" if bold else "")
            _font_cache[key] = ImageFont.truetype(path, size)
        except Exception:
            _font_cache[key] = ImageFont.load_default()
    return _font_cache[key]


def text(draw, txt, x, y, size=14, bold=False, color=WHITE,
         anchor="la", max_width=None, line_height=None):
    """Draw text, with optional word-wrap."""
    f = font(size, bold)
    if max_width and len(txt) > 10:
        avg_char = size * 0.55
        chars = max(10, int(max_width / avg_char))
        lines = textwrap.wrap(txt, width=chars)
    else:
        lines = [txt]
    lh = line_height or int(size * 1.4)
    for i, line in enumerate(lines):
        draw.text((x, y + i * lh), line, font=f, fill=color, anchor=anchor)
    return len(lines) * lh


def rect(draw, x, y, w, h, fill=SURFACE, outline=None, radius=6):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=radius,
                           fill=fill, outline=outline, width=1 if outline else 0)


def pill(draw, txt, x, y, w, h, fill, txt_color, size=11):
    rect(draw, x, y, w, h, fill=fill, radius=h // 2)
    cx = x + w // 2
    cy = y + h // 2
    draw.text((cx, cy), txt, font=font(size, bold=True), fill=txt_color,
              anchor="mm")


def header_bar(draw, title, badge=None, badge_color=YELLOW):
    rect(draw, 0, 0, W, 56, fill=SURFACE, radius=0)
    rect(draw, 0, 0, 6, 56, fill=ACCENT, radius=0)
    draw.text((18, 28), title, font=font(18, bold=True), fill=WHITE, anchor="lm")
    if badge:
        bw = len(badge) * 7 + 20
        bx = W - bw - 16
        pill(draw, badge, bx, 14, bw, 28, YDIM if badge_color == YELLOW
             else GDIM if badge_color == GREEN
             else RDIM if badge_color == RED else BDIM, badge_color, 10)


def hbar(draw, y, x1=30, x2=None, color=BORDER):
    draw.line([(x1, y), (x2 or W - 30, y)], fill=color, width=1)


def footer(draw, page_num):
    hbar(draw, H - 30)
    txt_f = f"Radiological Health Program Modernization  ·  Executive Status Report  ·  Page {page_num}"
    draw.text((W // 2, H - 14), txt_f, font=font(10), fill=MUTED, anchor="mm")


def progress_bar(draw, x, y, w, h, pct, color=ACCENT):
    rect(draw, x, y, w, h, fill=BORDER, radius=h // 2)
    if pct > 0:
        rect(draw, x, y, int(w * pct / 100), h, fill=color, radius=h // 2)


def status_circle(draw, letter, cx, cy, r=18, status="green"):
    bg_map = {"green": GDIM, "yellow": YDIM, "red": RDIM}
    c_map  = {"green": GREEN, "yellow": YELLOW, "red": RED}
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=bg_map[status])
    draw.text((cx, cy), letter, font=font(14, bold=True), fill=c_map[status], anchor="mm")


# ─────────────────────────────────────────────────────────────────────────────
# Slide 1 – Cover
# ─────────────────────────────────────────────────────────────────────────────
def slide1():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    rect(d, 0, 0, W, H, fill=SURFACE, radius=0)
    rect(d, 0, 0, 8, H, fill=ACCENT, radius=0)

    # Watermark
    d.text((W - 140, H // 2 - 80), "\u2622", font=font(180, bold=True),
           fill=(26, 31, 53), anchor="mm")

    d.text((30, 160), "Radiological Health Program",
           font=font(42, bold=True), fill=WHITE)
    d.text((30, 215), "Modernization Initiative",
           font=font(34, bold=True), fill=ACCENT)
    d.text((30, 280), "Executive Status Report  \u00b7  FY26  \u00b7  June 12, 2026",
           font=font(16), fill=MUTED)

    pill(d, "\u25cf  Overall Status: YELLOW", 30, 330, 280, 32, YDIM, YELLOW, 13)

    hbar(d, 400)
    d.text((30, 420), "Maryland Department of the Environment (MDE)  \u00b7  PCA: 79103  \u00b7  Radiation Control Fund",
           font=font(12), fill=MUTED)
    d.text((30, 445), "Prepared for Executive Review  \u00b7  July 10, 2026",
           font=font(12), fill=MUTED)

    footer(d, 1)
    return img


# ─────────────────────────────────────────────────────────────────────────────
# Slide 2 – Project Overview
# ─────────────────────────────────────────────────────────────────────────────
def slide2():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    header_bar(d, "Project Overview", "Overall: YELLOW", YELLOW)

    # Description card
    rect(d, 30, 70, W - 60, 90, fill=SURFACE)
    d.text((46, 80), "INITIATIVE", font=font(9, bold=True), fill=MUTED)
    text(d, ("The Radiological Health Program (RHP) is launching a strategic modernization initiative "
             "to transition its permitting and licensing application pipeline from legacy, manual workflows "
             "to a centralized online portal and electronic payment module."),
         46, 96, size=11, color=WHITE, max_width=W - 100)

    # Status indicators
    d.text((30, 175), "HEALTH STATUS INDICATORS", font=font(9, bold=True), fill=MUTED)
    dims = [
        ("Scope",    "G", "green"),
        ("Schedule", "G", "green"),
        ("Cost",     "G", "green"),
        ("Risk",     "G", "green"),
        ("Quality",  "R", "red"),
        ("Resources","Y", "yellow"),
    ]
    card_w = (W - 60 - 10) // 6
    for i, (name, letter, status) in enumerate(dims):
        cx = 30 + i * (card_w + 2)
        rect(d, cx, 192, card_w, 100, fill=SURF2)
        status_circle(d, letter, cx + card_w // 2, 232, status=status)
        color_map = {"green": GREEN, "yellow": YELLOW, "red": RED}
        d.text((cx + card_w // 2, 270), name,
               font=font(11, bold=True), fill=color_map[status], anchor="mm")

    # Rationale
    rect(d, 30, 308, W - 60, 78, fill=YDIM)
    d.text((46, 320), "\u26a0  WHY YELLOW?", font=font(10, bold=True), fill=YELLOW)
    text(d, ("Environment and resource changes have been identified. These changes are not expected to "
             "impact overall project delivery. A Tech Lead is being hired to address build/environment blockers."),
         46, 340, size=10, color=WHITE, max_width=W - 100)

    footer(d, 2)
    return img


# ─────────────────────────────────────────────────────────────────────────────
# Slide 3 – Sprint Schedule
# ─────────────────────────────────────────────────────────────────────────────
def slide3():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    header_bar(d, "Sprint Schedule & Delivery Milestones", "Sprint 2: IN PROGRESS", ACCENT)

    sprints = [
        ("Sprint 1", "Jun 17 – Jun 30, 2026", "Complete",    100, GREEN,
         "Group 3–9: PDF Portal Submissions & Electronic Payments enabled"),
        ("Sprint 2", "Jul 1 – Jul 14, 2026",  "In Progress",  64, ACCENT,
         "Group 3–9: Enable Notifications for customers & RHP Team Inbox"),
        ("Sprint 3", "Jul 15 – Jul 28, 2026", "Not Started",   0, MUTED,
         "Group 3–9: Provide option to download RHP permits"),
        ("Sprint 4", "Jul 29 – Aug 11, 2026", "Not Started",   0, MUTED,
         "Group 3–9: Reject & update status (CRM) for RHP permits"),
        ("Sprint 5", "TBD — Next",            "Not Started",   0, MUTED,
         "Group 1–2: Configuration and setup"),
        ("Sprint 6", "TBD — Next",            "Not Started",   0, MUTED,
         "Group 3–9: Web Forms Development"),
    ]

    status_col = {"Complete": GREEN, "In Progress": ACCENT, "Not Started": MUTED}
    status_bg  = {"Complete": GDIM,  "In Progress": BDIM,   "Not Started": SURF2}

    row_h = 94
    for i, (name, dates, status, pct, bar_color, goal) in enumerate(sprints):
        y = 68 + i * (row_h + 3)
        fill = SURFACE if i % 2 == 0 else SURF2
        rect(d, 30, y, W - 60, row_h, fill=fill)

        d.text((46, y + 14), name, font=font(13, bold=True), fill=WHITE)
        d.text((46, y + 36), dates, font=font(9), fill=MUTED)
        text(d, goal, 200, y + 18, size=10, color=WHITE, max_width=620)

        # Progress bar
        progress_bar(d, 870, y + 28, 220, 10, pct, color=bar_color)
        d.text((1100, y + 28), f"{pct}%", font=font(10, bold=True), fill=WHITE)

        # Status pill
        sc = status_col[status]
        sb = status_bg[status]
        pill(d, status, 870, y + 50, 140, 24, sb, sc, 9)

    hbar(d, H - 44)
    d.text((30, H - 38), "Near = within 2 sprints  ·  Next = planned future sprints",
           font=font(9), fill=MUTED)
    footer(d, 3)
    return img


# ─────────────────────────────────────────────────────────────────────────────
# Slide 4 – Financial Summary
# ─────────────────────────────────────────────────────────────────────────────
def slide4():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    header_bar(d, "Financial Summary", "Cost Status: GREEN", GREEN)

    # KPI cards
    kpis = [
        ("Total Approved", "$6.0M",  "FY25–FY26 Combined",  ACCENT, BDIM),
        ("Total Forecast", "$3.70M", "FY25–FY28 All Years", YELLOW, YDIM),
        ("Total Actual",   "$1.45M", "FY25+FY26 Spent",     GREEN,  GDIM),
        ("Remaining",      "$1.55M", "Balance / Variance",  PURPLE, (74, 31, 120)),
    ]
    kw = (W - 60 - 18) // 4
    for i, (lbl, val, sub, col, bg) in enumerate(kpis):
        x = 30 + i * (kw + 6)
        rect(d, x, 70, kw, 80, fill=bg)
        rect(d, x, 70, kw, 4, fill=col, radius=0)
        d.text((x + 10, 84), lbl.upper(), font=font(8, bold=True), fill=MUTED)
        d.text((x + 10, 100), val, font=font(22, bold=True), fill=col)
        d.text((x + 10, 134), sub, font=font(9), fill=MUTED)

    # Table
    rows = [
        ["Fiscal Year", "Approved",    "Forecast",    "Actual",      "Balance",    "Fund Source"],
        ["FY-25",  "$1,000,000",  "$500,000",    "$275,086",    "$724,914",   "Radiation Control (SF)"],
        ["FY-26",  "$2,000,000",  "$1,200,000",  "$1,177,504",  "$822,496",   "Radiation Control (SF)"],
        ["FY-27",  "$3,000,000",  "$1,468,511",  "—",           "$0",         "Special"],
        ["FY-28",  "—",           "$535,591",    "—",           "$0",         "Special"],
        ["TOTAL",  "$6,000,000",  "$3,704,102",  "$1,452,590",  "$1,547,410", "—"],
    ]
    col_w  = [100, 130, 130, 130, 130, 220]
    col_x  = [30]
    for cw in col_w[:-1]:
        col_x.append(col_x[-1] + cw)

    row_h = 34
    ty = 165
    for r, row in enumerate(rows):
        is_header = r == 0
        is_total  = r == len(rows) - 1
        for c, (cell, cx, cw) in enumerate(zip(row, col_x, col_w)):
            bg = (14, 18, 37) if is_header else BDIM if is_total else (SURFACE if r % 2 == 1 else SURF2)
            rect(d, cx, ty + r * row_h, cw, row_h, fill=bg, radius=0)
            txt_c = MUTED if is_header else GREEN if (c == 4 and cell not in ("$0", "—") and not is_total) else WHITE
            bold = is_header or is_total or c == 0
            anchor = "lm" if c in (0, 5) else "rm"
            tx = cx + 8 if c in (0, 5) else cx + cw - 8
            d.text((tx, ty + r * row_h + row_h // 2), cell,
                   font=font(9 if not is_total else 10, bold=bold), fill=txt_c, anchor=anchor)

    # Utilization bars
    d.text((30, 400), "BUDGET UTILIZATION", font=font(9, bold=True), fill=MUTED)
    util = [("FY-25", 27.5, GREEN), ("FY-26", 58.9, ACCENT), ("FY-27", 0.0, MUTED)]
    for i, (fy, pct, col) in enumerate(util):
        y = 420 + i * 36
        d.text((30, y + 4), fy, font=font(10), fill=MUTED)
        progress_bar(d, 90, y + 2, W - 190, 16, pct, color=col)
        d.text((W - 90, y + 4), f"{pct}%", font=font(10, bold=True), fill=WHITE)

    footer(d, 4)
    return img


# ─────────────────────────────────────────────────────────────────────────────
# Slide 5 – MVP Capabilities
# ─────────────────────────────────────────────────────────────────────────────
def slide5():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    header_bar(d, "MVP Capabilities — Groups 3 through 9")

    caps = [
        ("\U0001f4c4", "Portal Submissions",
         "PDF application submissions through the ESC Portal for Groups 3-9.", ACCENT, BDIM),
        ("\U0001f4b3", "Electronic Payments",
         "Credit/debit card and E-check to resolve clearing delays.", GREEN, GDIM),
        ("\U0001f514", "Notifications",
         "One-time email confirmations upon application and payment submission.", YELLOW, YDIM),
        ("\U0001f4e5", "RHP Team Inbox",
         "Automated notifications to the MDE Business User inbox.", PURPLE, (74, 31, 120)),
        ("\U0001f4c1", "Document Management",
         "Secure view, download of applications — individual files or ZIP.", (255, 127, 80), (112, 48, 21)),
        ("\U0001f510", "IAM Authentication",
         "MDE Business User auth via Identity and Access Management.", (6, 182, 212), (7, 69, 85)),
    ]

    card_w = (W - 60 - 20) // 3
    card_h = 170
    gap = 10
    sy = 76
    for i, (icon, name, desc, col, bg) in enumerate(caps):
        r = i // 3
        c = i % 3
        x = 30 + c * (card_w + gap)
        y = sy + r * (card_h + gap)
        rect(d, x, y, card_w, card_h, fill=bg)
        d.text((x + 14, y + 18), icon, font=font(28), fill=col)
        d.text((x + 58, y + 20), name, font=font(13, bold=True), fill=WHITE)
        text(d, desc, x + 14, y + 65, size=10, color=(204, 209, 232), max_width=card_w - 28)

    hbar(d, H - 44)
    d.text((30, H - 38), "Groups 1-2 configuration and setup planned in Sprint 5",
           font=font(9), fill=MUTED)
    footer(d, 5)
    return img


# ─────────────────────────────────────────────────────────────────────────────
# Slide 6 – Risks & Action Items
# ─────────────────────────────────────────────────────────────────────────────
def slide6():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    header_bar(d, "Risks, Impediments & Action Items", "Overall: YELLOW", YELLOW)

    d.text((30, 70), "ACTIVE RISKS & IMPEDIMENTS", font=font(9, bold=True), fill=MUTED)

    risks = [
        ("HIGH",   RED,    RDIM,
         "Environment & Build Issues",
         "Encountered environment and build issues impacting iterative delivery. "
         "Mitigation: Hiring a Tech Lead; validation processes established.",
         "Mitigate"),
        ("MEDIUM", YELLOW, YDIM,
         "Workflow Finalization",
         "Non-ETS workflow approach pending: status tracking, Third-Party access, "
         "Liability Checks. DoIT & MDE teams reviewing enterprise solutions.",
         "Transfer"),
        ("MEDIUM", YELLOW, YDIM,
         "Registration Number Automation",
         "Program must decide on folder naming convention and whether the system "
         "auto-generates sequence numbers. Awaiting program decision.",
         "Mitigate"),
    ]

    rh = 90
    for i, (level, col, bg, title, desc, strategy) in enumerate(risks):
        y = 88 + i * (rh + 6)
        rect(d, 30, y, W - 170, rh, fill=bg)
        rect(d, 30, y, W - 170, 3, fill=col, radius=0)
        pill(d, level, 46, y + 10, 65, 22, col, BG, 9)
        d.text((126, y + 10), title, font=font(12, bold=True), fill=WHITE)
        text(d, desc, 46, y + 42, size=9, color=(204, 209, 232), max_width=W - 230)
        rect(d, W - 134, y, 104, rh, fill=SURFACE)
        d.text((W - 126, y + 14), "RESPONSE", font=font(8, bold=True), fill=MUTED)
        d.text((W - 126, y + 40), strategy, font=font(14, bold=True), fill=col)

    # Action Items
    d.text((30, 368), "ACTION ITEMS", font=font(9, bold=True), fill=MUTED)
    actions = [
        (ACCENT, "MVP Time Savings",
         "Generate high-level estimates of days saved per MVP deliverable (80/20 rule)."),
        (YELLOW, "Liability Check",
         "Remain coordinated with Emil, Paul, and DoIT team awaiting State Data Officer update."),
        (GREEN,  "User Testing",
         "Align with Paul to integrate user testing seamlessly into development cycles."),
    ]
    aw = (W - 60 - 20) // 3
    for i, (col, title, desc) in enumerate(actions):
        x = 30 + i * (aw + 10)
        rect(d, x, 386, aw, 120, fill=SURFACE)
        rect(d, x, 386, aw, 4, fill=col, radius=0)
        d.text((x + 12, 400), title, font=font(11, bold=True), fill=col)
        text(d, desc, x + 12, 424, size=9, color=MUTED, max_width=aw - 24)

    hbar(d, H - 44)
    d.text((30, H - 38), "Mitigate = internal action  \u00b7  Transfer = escalate / partner",
           font=font(9), fill=MUTED)
    footer(d, 6)
    return img


# ─────────────────────────────────────────────────────────────────────────────
# Slide 7 – Successes
# ─────────────────────────────────────────────────────────────────────────────
def slide7():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    header_bar(d, "Successes & Key Progress — Reporting Period", "Sprint 1: COMPLETE", GREEN)

    successes = [
        (GREEN,  "\u2705", "MVP Release Development",
         "The team is actively working on the MVP release supporting New Applications for Groups 3-9. "
         "Re-certification and Renewal workflows are under review pending Liability Check clarification."),
        (ACCENT, "\u2699", "ESC Page Validations & Verification",
         "The RHP Team is developing the RHP Configuration Template to govern ESC Portal page validations, "
         "ensuring data integrity and compliance across all application submissions."),
        (PURPLE, "\U0001f512", "Authentication & Database Restructuring",
         "Work has commenced on MDE Business User authentication via IAM protocols, alongside "
         "restructuring of legacy RHP applications and database tables to support modern workflows."),
    ]

    rh = 168
    for i, (col, icon, title, desc) in enumerate(successes):
        y = 72 + i * (rh + 10)
        rect(d, 30, y, W - 60, rh, fill=SURFACE)
        rect(d, 30, y, 6, rh, fill=col, radius=0)
        d.text((54, y + rh // 2 - 14), icon, font=font(30), fill=col, anchor="lm")
        d.text((108, y + 24), title, font=font(14, bold=True), fill=WHITE)
        text(d, desc, 108, y + 52, size=10, color=(204, 209, 232), max_width=W - 160)

    hbar(d, H - 44)
    d.text((30, H - 38),
           "Sprint 1 completed successfully  \u00b7  Sprint 2 currently in progress (Jul 1-14, 2026)",
           font=font(9), fill=MUTED)
    footer(d, 7)
    return img


# ─────────────────────────────────────────────────────────────────────────────
# Slide 8 – Executive Summary
# ─────────────────────────────────────────────────────────────────────────────
def slide8():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    header_bar(d, "Executive Summary & Next Steps")

    # Status row
    statuses = [
        ("Overall",  "YELLOW",   YELLOW, YDIM),
        ("Schedule", "ON TRACK", GREEN,  GDIM),
        ("Cost",     "ON TRACK", GREEN,  GDIM),
        ("Delivery", "MVP Q3",   ACCENT, BDIM),
    ]
    sw = (W - 60 - 18) // 4
    for i, (lbl, val, col, bg) in enumerate(statuses):
        x = 30 + i * (sw + 6)
        rect(d, x, 68, sw, 60, fill=bg)
        rect(d, x, 68 + 56, sw, 4, fill=col, radius=0)
        d.text((x + sw // 2, 82), lbl.upper(), font=font(8, bold=True), fill=MUTED, anchor="mm")
        d.text((x + sw // 2, 108), val, font=font(16, bold=True), fill=col, anchor="mm")

    # Takeaways
    d.text((30, 146), "KEY TAKEAWAYS", font=font(9, bold=True), fill=MUTED)
    takeaways = [
        (GREEN,  "On Budget",              "Actual $1.45M below forecast. $1.55M buffer remaining."),
        (GREEN,  "Delivery On Track",      "Sprint 1 complete. MVP for Groups 3-9 on schedule."),
        (RED,    "Quality: Attention",     "Build/env issues in Sprint 1. Tech Lead hiring in progress."),
        (YELLOW, "Decisions Pending",      "Workflow finalization and registration numbers need decisions."),
    ]
    tw = (W - 60 - 18) // 4
    for i, (col, title, desc) in enumerate(takeaways):
        x = 30 + i * (tw + 6)
        rect(d, x, 162, tw, 130, fill=SURFACE)
        rect(d, x, 162, tw, 4, fill=col, radius=0)
        d.text((x + 10, 178), title, font=font(11, bold=True), fill=col)
        text(d, desc, x + 10, 202, size=9, color=MUTED, max_width=tw - 20)

    # Next steps
    d.text((30, 310), "IMMEDIATE NEXT STEPS", font=font(9, bold=True), fill=MUTED)
    next_steps = [
        (ACCENT, "Complete Sprint 2",       "Jul 1-14, 2026",     "Enable customer notifications & RHP Team inbox"),
        (ACCENT, "Finalize Workflow",        "Ongoing",            "Resolve non-ETS workflow with DoIT & MDE teams"),
        (YELLOW, "State Data Officer Input", "Awaiting",           "Liability Check decision — Emil/Paul/DoIT"),
        (GREEN,  "Hire Tech Lead",           "Active Recruiting",  "Address build/environment blockers proactively"),
        (GREEN,  "User Testing Alignment",   "Sprint 2-3",         "Coordinate with Paul to integrate testing"),
    ]
    for i, (col, step, timeline, detail) in enumerate(next_steps):
        y = 328 + i * 48
        fill = SURFACE if i % 2 == 0 else SURF2
        rect(d, 30, y, W - 60, 44, fill=fill, radius=4)
        draw_cx = 50
        draw_cy = y + 22
        d.ellipse([draw_cx - 6, draw_cy - 6, draw_cx + 6, draw_cy + 6], fill=col)
        d.text((68, y + 22), step, font=font(11, bold=True), fill=WHITE, anchor="lm")
        d.text((330, y + 22), timeline, font=font(10), fill=col, anchor="lm")
        d.text((500, y + 22), detail, font=font(10), fill=MUTED, anchor="lm")

    hbar(d, H - 44)
    d.text((30, H - 38),
           "RHP Modernization Initiative  \u00b7  MDE  \u00b7  Prepared for Executive Review  \u00b7  July 10, 2026",
           font=font(9), fill=MUTED)
    footer(d, 8)
    return img


# ─────────────────────────────────────────────────────────────────────────────
# Build all slides
# ─────────────────────────────────────────────────────────────────────────────
builders = [slide1, slide2, slide3, slide4, slide5, slide6, slide7, slide8]
titles   = [
    "01_Cover", "02_Project_Overview", "03_Sprint_Schedule",
    "04_Financial_Summary", "05_MVP_Capabilities",
    "06_Risks_Action_Items", "07_Successes", "08_Executive_Summary"
]

for fn, title in zip(builders, titles):
    img = fn()
    path = f"{OUT_DIR}/slide_{title}.png"
    img.save(path, "PNG", optimize=True)
    print(f"  Saved {path}")

print(f"\nDone — {len(builders)} slides in {OUT_DIR}/")
