"""
RHP Executive Status – Slide Thumbnail Generator (Light Theme)
Produces dashboard/slides/slide_N.png  (1280×720 each) using Pillow only.
"""

from PIL import Image, ImageDraw, ImageFont
import os, textwrap

OUT_DIR = "dashboard/slides"
os.makedirs(OUT_DIR, exist_ok=True)

W, H = 1280, 720

# ── Light Palette ─────────────────────────────────────────────────────────────
BG      = (240, 246, 255)   # very light blue page background
SURFACE = (255, 255, 255)   # white card
SURF2   = (229, 238, 252)   # light blue-gray for alternate rows / inner cards
BORDER  = (196, 210, 235)   # subtle border
TEXT    = (15,  23,  42)    # near-black primary text
MUTED   = (74,  90, 130)    # medium blue-gray secondary text
ACCENT  = (37,  99, 235)    # strong blue
GREEN   = (21, 128,  61)    # green (slightly dark for light bg)
YELLOW  = (161,  98,   7)   # amber (dark enough for light bg)
RED     = (185,  28,  28)   # red
PURPLE  = (109,  40, 217)   # purple
WHITE   = (255, 255, 255)

# Light-tint dim versions (card fills for colored sections)
GDIM    = (220, 252, 231)   # light green tint
YDIM    = (254, 243, 199)   # light yellow tint
RDIM    = (254, 226, 226)   # light red tint
BDIM    = (219, 234, 254)   # light blue tint
PDIM    = (237, 233, 254)   # light purple tint

# Bright versions for badges / pills (displayed against their dim backgrounds)
G_BRIGHT = (22, 163,  74)
Y_BRIGHT = (217, 119,   6)
R_BRIGHT = (220,  38,  38)
B_BRIGHT = (37,  99, 235)

# ── Font helpers ──────────────────────────────────────────────────────────────
_font_cache = {}
def font(size, bold=False):
    key = (size, bold)
    if key not in _font_cache:
        try:
            path = "/usr/share/fonts/truetype/dejavu/DejaVuSans{}.ttf".format(
                "-Bold" if bold else "")
            _font_cache[key] = ImageFont.truetype(path, size)
        except Exception:
            _font_cache[key] = ImageFont.load_default()
    return _font_cache[key]


def text(draw, txt, x, y, size=14, bold=False, color=TEXT,
         anchor="la", max_width=None, line_height=None):
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


def rect(draw, x, y, w, h, fill=SURFACE, outline=BORDER, radius=6):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=radius,
                           fill=fill, outline=outline, width=1)


def pill(draw, txt, x, y, w, h, fill, txt_color, size=11):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=h // 2,
                           fill=fill, outline=None)
    draw.text((x + w // 2, y + h // 2), txt, font=font(size, bold=True),
              fill=txt_color, anchor="mm")


def header_bar(draw, title, badge=None, badge_color=Y_BRIGHT, badge_fill=YDIM):
    # White header bar with blue left accent
    draw.rectangle([0, 0, W, 56], fill=SURFACE)
    draw.rectangle([0, 56, W, 57], fill=BORDER)
    draw.rectangle([0, 0, 6, 56], fill=ACCENT)
    draw.text((18, 28), title, font=font(18, bold=True), fill=TEXT, anchor="lm")
    if badge:
        bw = len(badge) * 7 + 20
        bx = W - bw - 16
        draw.rounded_rectangle([bx, 14, bx + bw, 42], radius=6,
                               fill=badge_fill, outline=None)
        draw.text((bx + bw // 2, 28), badge, font=font(10, bold=True),
                  fill=badge_color, anchor="mm")


def hbar(draw, y, x1=30, x2=None, color=BORDER):
    draw.line([(x1, y), (x2 or W - 30, y)], fill=color, width=1)


def footer(draw, page_num):
    draw.rectangle([0, H - 28, W, H], fill=SURF2)
    hbar(draw, H - 28)
    txt_f = (f"Radiological Health Program Modernization  ·  "
             f"Executive Status Report  ·  Page {page_num}")
    draw.text((W // 2, H - 14), txt_f, font=font(10), fill=MUTED, anchor="mm")


def progress_bar(draw, x, y, w, h, pct, color=ACCENT):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=h // 2,
                           fill=SURF2, outline=BORDER, width=1)
    if pct > 0:
        draw.rounded_rectangle([x, y, x + int(w * pct / 100), y + h],
                               radius=h // 2, fill=color, outline=None)


def status_circle(draw, letter, cx, cy, r=18, status="green"):
    bg_map  = {"green": GDIM,  "yellow": YDIM,  "red": RDIM}
    c_map   = {"green": GREEN, "yellow": YELLOW, "red": RED}
    out_map = {"green": (34, 197, 94, 180), "yellow": (245, 158, 11, 180),
               "red": (220, 38, 38, 180)}
    draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                 fill=bg_map[status], outline=c_map[status], width=2)
    draw.text((cx, cy), letter, font=font(14, bold=True),
              fill=c_map[status], anchor="mm")


def section_label(draw, txt, x, y):
    draw.text((x, y), txt.upper(), font=font(9, bold=True), fill=MUTED)


# ─────────────────────────────────────────────────────────────────────────────
# Slide 1 – Cover
# ─────────────────────────────────────────────────────────────────────────────
def slide1():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # Hero card
    rect(d, 0, 0, W, H - 28, fill=SURFACE, outline=None, radius=0)

    # Left accent bar
    d.rectangle([0, 0, 8, H], fill=ACCENT)

    # Top accent stripe
    d.rectangle([0, 0, W, 6], fill=ACCENT)

    # Decorative circle watermark (light)
    d.ellipse([W - 300, H // 2 - 200, W + 100, H // 2 + 200],
              fill=(229, 238, 252), outline=None)

    d.text((30, 150), "Radiological Health Program",
           font=font(44, bold=True), fill=TEXT)
    d.text((30, 208), "Modernization Initiative",
           font=font(32, bold=False), fill=ACCENT)
    d.text((30, 272), "Executive Status Report  ·  FY26  ·  June 12, 2026",
           font=font(15), fill=MUTED)

    # Status badge
    pill(d, "● Overall Status: YELLOW", 30, 320, 272, 34, YDIM, YELLOW, 13)

    hbar(d, 388)
    d.text((30, 406), "Maryland Department of the Environment (MDE)  ·  PCA: 79103  ·  Radiation Control Fund",
           font=font(12), fill=MUTED)
    d.text((30, 428), "Prepared for Executive Review  ·  July 10, 2026",
           font=font(12), fill=MUTED)

    footer(d, 1)
    return img


# ─────────────────────────────────────────────────────────────────────────────
# Slide 2 – Project Overview
# ─────────────────────────────────────────────────────────────────────────────
def slide2():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    header_bar(d, "Project Overview", "Overall: YELLOW", YELLOW, YDIM)

    # Description card
    rect(d, 30, 70, W - 60, 86, fill=SURFACE)
    section_label(d, "Initiative", 46, 78)
    text(d, ("The Radiological Health Program (RHP) is launching a strategic modernization initiative "
             "to transition its permitting and licensing application pipeline from legacy, manual workflows "
             "to a centralized online portal and electronic payment module."),
         46, 94, size=11, color=TEXT, max_width=W - 100)

    # Health status indicators
    section_label(d, "Health Status Indicators", 30, 173)
    dims = [
        ("Scope",    "G", "green"),
        ("Schedule", "G", "green"),
        ("Cost",     "G", "green"),
        ("Risk",     "G", "green"),
        ("Quality",  "R", "red"),
        ("Resources","Y", "yellow"),
    ]
    color_map = {"green": GREEN, "yellow": YELLOW, "red": RED}
    card_w = (W - 60 - 10) // 6
    for i, (name, letter, status) in enumerate(dims):
        cx = 30 + i * (card_w + 2)
        rect(d, cx, 190, card_w, 106, fill=SURFACE)
        status_circle(d, letter, cx + card_w // 2, 232, status=status)
        d.text((cx + card_w // 2, 272), name,
               font=font(11, bold=True), fill=color_map[status], anchor="mm")

    # Yellow rationale
    rect(d, 30, 312, W - 60, 82, fill=YDIM, outline=(217, 119, 6), radius=6)
    d.text((46, 322), "⚠  WHY YELLOW?", font=font(10, bold=True), fill=YELLOW)
    text(d, ("Environment and resource changes have been identified. These changes are not expected to "
             "impact overall project delivery. A Tech Lead is being hired to address build/environment blockers."),
         46, 342, size=10, color=TEXT, max_width=W - 100)

    footer(d, 2)
    return img


# ─────────────────────────────────────────────────────────────────────────────
# Slide 3 – Sprint Schedule
# ─────────────────────────────────────────────────────────────────────────────
def slide3():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    header_bar(d, "Sprint Schedule & Delivery Milestones", "Sprint 2: IN PROGRESS", ACCENT, BDIM)

    sprints = [
        ("Sprint 1", "Jun 17 – Jun 30, 2026", "Complete",    100, G_BRIGHT,
         "Group 3–9: PDF Portal Submissions & Electronic Payments enabled"),
        ("Sprint 2", "Jul 1 – Jul 14, 2026",  "In Progress",  64, B_BRIGHT,
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

    status_col  = {"Complete": G_BRIGHT, "In Progress": B_BRIGHT, "Not Started": MUTED}
    status_fill = {"Complete": GDIM,     "In Progress": BDIM,     "Not Started": SURF2}

    row_h = 92
    for i, (name, dates, status, pct, bar_color, goal) in enumerate(sprints):
        y = 68 + i * (row_h + 3)
        fill = SURFACE if i % 2 == 0 else SURF2
        rect(d, 30, y, W - 60, row_h, fill=fill)
        d.text((46, y + 14), name, font=font(13, bold=True), fill=TEXT)
        d.text((46, y + 36), dates, font=font(9), fill=MUTED)
        text(d, goal, 200, y + 18, size=10, color=TEXT, max_width=620)
        progress_bar(d, 870, y + 28, 220, 10, pct, color=bar_color)
        d.text((1100, y + 28), f"{pct}%", font=font(10, bold=True), fill=TEXT)
        sc = status_col[status]
        sb = status_fill[status]
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
    header_bar(d, "Financial Summary", "Cost Status: GREEN", GREEN, GDIM)

    kpis = [
        ("Total Approved", "$6.0M",  "FY25–FY26 Combined",  ACCENT,  BDIM,  BORDER),
        ("Total Forecast", "$3.70M", "FY25–FY28 All Years", YELLOW,  YDIM,  (217, 119, 6)),
        ("Total Actual",   "$1.45M", "FY25+FY26 Spent",     GREEN,   GDIM,  (22, 163, 74)),
        ("Remaining",      "$1.55M", "Balance / Variance",  PURPLE,  PDIM,  (109, 40, 217)),
    ]
    kw = (W - 60 - 18) // 4
    for i, (lbl, val, sub, col, bg, outline) in enumerate(kpis):
        x = 30 + i * (kw + 6)
        rect(d, x, 70, kw, 82, fill=bg, outline=outline)
        d.rectangle([x, 70, x + kw, 74], fill=col)
        d.text((x + 10, 84), lbl.upper(), font=font(8, bold=True), fill=MUTED)
        d.text((x + 10, 100), val, font=font(22, bold=True), fill=col)
        d.text((x + 10, 136), sub, font=font(9), fill=MUTED)

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

    row_h = 32
    ty = 165
    for r, row in enumerate(rows):
        is_header = r == 0
        is_total  = r == len(rows) - 1
        for c, (cell, cx, cw) in enumerate(zip(row, col_x, col_w)):
            bg = BDIM if is_header else (BDIM if is_total else
                 (SURFACE if r % 2 == 1 else SURF2))
            rect(d, cx, ty + r * row_h, cw, row_h, fill=bg,
                 outline=BORDER, radius=0)
            txt_c = MUTED if is_header else (GREEN if (c == 4 and cell not in ("$0", "—") and not is_total) else TEXT)
            bold = is_header or is_total or c == 0
            anchor = "lm" if c in (0, 5) else "rm"
            tx = cx + 8 if c in (0, 5) else cx + cw - 8
            d.text((tx, ty + r * row_h + row_h // 2), cell,
                   font=font(9 if not is_total else 10, bold=bold),
                   fill=txt_c, anchor=anchor)

    section_label(d, "Budget Utilization (Actual vs Approved)", 30, 398)
    util = [("FY-25", 27.5, G_BRIGHT), ("FY-26", 58.9, B_BRIGHT), ("FY-27", 0.0, MUTED)]
    for i, (fy, pct, col) in enumerate(util):
        y = 418 + i * 36
        d.text((30, y + 4), fy, font=font(10), fill=MUTED)
        progress_bar(d, 90, y + 2, W - 190, 18, pct, color=col)
        d.text((W - 90, y + 4), f"{pct}%", font=font(10, bold=True), fill=TEXT)

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
         "PDF application submissions through the ESC Portal for Groups 3-9.",
         ACCENT,  BDIM,  BORDER),
        ("\U0001f4b3", "Electronic Payments",
         "Credit/debit card and E-check to resolve clearing delays.",
         GREEN,   GDIM,  (22, 163, 74)),
        ("\U0001f514", "Notifications",
         "One-time email confirmations upon application and payment submission.",
         YELLOW,  YDIM,  (217, 119, 6)),
        ("\U0001f4e5", "RHP Team Inbox",
         "Automated notifications to the MDE Business User inbox.",
         PURPLE,  PDIM,  (109, 40, 217)),
        ("\U0001f4c1", "Document Management",
         "Secure view, download of applications — individual files or ZIP.",
         (180, 83, 9),  (255, 237, 213), (180, 83, 9)),
        ("\U0001f510", "IAM Authentication",
         "MDE Business User auth via Identity and Access Management.",
         (8, 145, 178), (207, 250, 254), (8, 145, 178)),
    ]

    card_w = (W - 60 - 20) // 3
    card_h = 172
    gap = 10
    sy = 74
    for i, (icon, name, desc, col, bg, outline) in enumerate(caps):
        r = i // 3
        c = i % 3
        x = 30 + c * (card_w + gap)
        y = sy + r * (card_h + gap)
        rect(d, x, y, card_w, card_h, fill=bg, outline=outline)
        d.text((x + 14, y + 18), icon, font=font(28), fill=col)
        d.text((x + 58, y + 22), name, font=font(13, bold=True), fill=TEXT)
        text(d, desc, x + 14, y + 68, size=10, color=MUTED, max_width=card_w - 28)

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
    header_bar(d, "Risks, Impediments & Action Items", "Overall: YELLOW", YELLOW, YDIM)

    section_label(d, "Active Risks & Impediments", 30, 68)

    risks = [
        ("HIGH",   R_BRIGHT, RDIM,  (220, 38, 38),
         "Environment & Build Issues",
         "Encountered environment and build issues impacting iterative delivery. "
         "Mitigation: Hiring a Tech Lead; validation processes established.",
         "Mitigate"),
        ("MEDIUM", YELLOW,   YDIM,  (217, 119, 6),
         "Workflow Finalization",
         "Non-ETS workflow approach pending: status tracking, Third-Party access, "
         "Liability Checks. DoIT & MDE teams reviewing enterprise solutions.",
         "Transfer"),
        ("MEDIUM", YELLOW,   YDIM,  (217, 119, 6),
         "Registration Number Automation",
         "Program must decide on folder naming convention and whether the system "
         "auto-generates sequence numbers. Awaiting program decision.",
         "Mitigate"),
    ]

    rh = 88
    for i, (level, col, bg, outline, title, desc, strategy) in enumerate(risks):
        y = 86 + i * (rh + 6)
        rect(d, 30, y, W - 170, rh, fill=bg, outline=outline)
        pill(d, level, 46, y + 10, 68, 22, col, WHITE if col == R_BRIGHT else TEXT, 9)
        d.text((126, y + 12), title, font=font(12, bold=True), fill=TEXT)
        text(d, desc, 46, y + 42, size=9, color=MUTED, max_width=W - 230)
        rect(d, W - 134, y, 104, rh, fill=SURFACE, outline=BORDER)
        d.text((W - 126, y + 14), "RESPONSE", font=font(8, bold=True), fill=MUTED)
        d.text((W - 126, y + 40), strategy, font=font(14, bold=True), fill=col)

    section_label(d, "Action Items", 30, 368)
    actions = [
        (ACCENT, BDIM, BORDER,
         "MVP Time Savings",
         "Generate high-level estimates of days saved per MVP deliverable (80/20 rule)."),
        (YELLOW, YDIM, (217, 119, 6),
         "Liability Check",
         "Remain coordinated with Emil, Paul, and DoIT team awaiting State Data Officer update."),
        (GREEN,  GDIM, (22, 163, 74),
         "User Testing",
         "Align with Paul to integrate user testing seamlessly into development cycles."),
    ]
    aw = (W - 60 - 20) // 3
    for i, (col, bg, outline, title, desc) in enumerate(actions):
        x = 30 + i * (aw + 10)
        rect(d, x, 386, aw, 118, fill=bg, outline=outline)
        d.rectangle([x, 386, x + aw, 390], fill=col)
        d.text((x + 12, 402), title, font=font(11, bold=True), fill=col)
        text(d, desc, x + 12, 424, size=9, color=MUTED, max_width=aw - 24)

    hbar(d, H - 44)
    d.text((30, H - 38), "Mitigate = internal action  ·  Transfer = escalate / partner",
           font=font(9), fill=MUTED)
    footer(d, 6)
    return img


# ─────────────────────────────────────────────────────────────────────────────
# Slide 7 – Successes
# ─────────────────────────────────────────────────────────────────────────────
def slide7():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    header_bar(d, "Successes & Key Progress — Reporting Period", "Sprint 1: COMPLETE", GREEN, GDIM)

    successes = [
        (GREEN,  (22, 163, 74),  "\u2705", "MVP Release Development",
         "The team is actively working on the MVP release supporting New Applications for Groups 3-9. "
         "Re-certification and Renewal workflows are under review pending Liability Check clarification."),
        (ACCENT, BORDER,         "\u2699", "ESC Page Validations & Verification",
         "The RHP Team is developing the RHP Configuration Template to govern ESC Portal page validations, "
         "ensuring data integrity and compliance across all application submissions."),
        (PURPLE, (109, 40, 217), "\U0001f512", "Authentication & Database Restructuring",
         "Work has commenced on MDE Business User authentication via IAM protocols, alongside "
         "restructuring of legacy RHP applications and database tables to support modern workflows."),
    ]

    rh = 162
    for i, (col, outline, icon, title, desc) in enumerate(successes):
        y = 72 + i * (rh + 10)
        rect(d, 30, y, W - 60, rh, fill=SURFACE, outline=BORDER)
        d.rectangle([30, y, 38, y + rh], fill=col)
        d.text((54, y + rh // 2 - 14), icon, font=font(30), fill=col, anchor="lm")
        d.text((108, y + 26), title, font=font(14, bold=True), fill=TEXT)
        text(d, desc, 108, y + 56, size=10, color=MUTED, max_width=W - 160)

    hbar(d, H - 44)
    d.text((30, H - 38),
           "Sprint 1 completed successfully  ·  Sprint 2 currently in progress (Jul 1-14, 2026)",
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
        ("Overall",  "YELLOW",   YELLOW, YDIM,  (217, 119, 6)),
        ("Schedule", "ON TRACK", GREEN,  GDIM,  (22, 163, 74)),
        ("Cost",     "ON TRACK", GREEN,  GDIM,  (22, 163, 74)),
        ("Delivery", "MVP Q3",   ACCENT, BDIM,  BORDER),
    ]
    sw = (W - 60 - 18) // 4
    for i, (lbl, val, col, bg, outline) in enumerate(statuses):
        x = 30 + i * (sw + 6)
        rect(d, x, 68, sw, 60, fill=bg, outline=outline)
        d.rectangle([x, 122, x + sw, 126], fill=col)
        d.text((x + sw // 2, 82), lbl.upper(), font=font(8, bold=True), fill=MUTED, anchor="mm")
        d.text((x + sw // 2, 106), val, font=font(16, bold=True), fill=col, anchor="mm")

    # Key takeaways
    section_label(d, "Key Takeaways", 30, 146)
    takeaways = [
        (GREEN,  (22,163,74), "On Budget",              "Actual $1.45M below forecast. $1.55M buffer remaining."),
        (GREEN,  (22,163,74), "Delivery On Track",      "Sprint 1 complete. MVP for Groups 3-9 on schedule."),
        (RED,    (220,38,38), "Quality: Attention",     "Build/env issues in Sprint 1. Tech Lead hiring in progress."),
        (YELLOW, (217,119,6), "Decisions Pending",      "Workflow finalization and registration numbers need decisions."),
    ]
    tw = (W - 60 - 18) // 4
    for i, (col, outline, title, desc) in enumerate(takeaways):
        x = 30 + i * (tw + 6)
        rect(d, x, 162, tw, 126, fill=SURFACE, outline=BORDER)
        d.rectangle([x, 162, x + tw, 166], fill=col)
        d.text((x + 10, 180), title, font=font(11, bold=True), fill=col)
        text(d, desc, x + 10, 204, size=9, color=MUTED, max_width=tw - 20)

    # Next steps
    section_label(d, "Immediate Next Steps", 30, 308)
    next_steps = [
        (ACCENT, "Complete Sprint 2",       "Jul 1-14, 2026",     "Enable customer notifications & RHP Team inbox"),
        (ACCENT, "Finalize Workflow",        "Ongoing",            "Resolve non-ETS workflow with DoIT & MDE teams"),
        (YELLOW, "State Data Officer Input", "Awaiting",           "Liability Check decision — Emil/Paul/DoIT"),
        (GREEN,  "Hire Tech Lead",           "Active Recruiting",  "Address build/environment blockers proactively"),
        (GREEN,  "User Testing Alignment",   "Sprint 2-3",         "Coordinate with Paul to integrate testing"),
    ]
    for i, (col, step, timeline, detail) in enumerate(next_steps):
        y = 326 + i * 46
        fill = SURFACE if i % 2 == 0 else SURF2
        rect(d, 30, y, W - 60, 42, fill=fill, outline=BORDER, radius=4)
        d.ellipse([44, y + 13, 56, y + 25], fill=col)
        d.text((68, y + 20), step, font=font(11, bold=True), fill=TEXT, anchor="lm")
        d.text((330, y + 20), timeline, font=font(10), fill=col, anchor="lm")
        d.text((500, y + 20), detail, font=font(10), fill=MUTED, anchor="lm")

    hbar(d, H - 44)
    d.text((30, H - 38),
           "RHP Modernization Initiative  ·  MDE  ·  Prepared for Executive Review  ·  July 10, 2026",
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
