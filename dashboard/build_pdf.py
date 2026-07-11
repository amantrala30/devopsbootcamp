"""
RHP Modernization – Executive Status PDF Export
Produces dashboard/RHP_Executive_Status.pdf  (8 pages, one per slide)
Uses ReportLab Platypus; no LibreOffice dependency.
"""

from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether, PageBreak
)
from reportlab.platypus.flowables import Flowable
from reportlab.graphics.shapes import (
    Drawing, Rect, Circle, String, Line, Polygon
)
from reportlab.graphics import renderPDF
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.legends import Legend
import io

PAGE_W, PAGE_H = landscape(A4)   # 841.89 x 595.28 pts
M = 28                            # margin

# ── Palette (Light Theme) ─────────────────────────────────────────────────────
C_BG      = colors.HexColor("#F0F6FF")   # very light blue page background
C_SURFACE = colors.HexColor("#0F172A")   # white card
C_SURF2   = colors.HexColor("#E5EEFC")   # light blue-gray alternate rows
C_BORDER  = colors.HexColor("#C4D2EB")   # subtle border
C_WHITE   = colors.white
C_TEXT    = colors.HexColor("#0F172A")   # near-black primary text
C_MUTED   = colors.HexColor("#4A5A82")   # medium blue-gray secondary text
C_ACCENT  = colors.HexColor("#2563EB")   # strong blue
C_GREEN   = colors.HexColor("#16803D")   # dark green (readable on light)
C_YELLOW  = colors.HexColor("#D97706")   # amber (readable on light)
C_RED     = colors.HexColor("#DC2626")   # red
C_PURPLE  = colors.HexColor("#6D28D9")   # purple
C_GDIM    = colors.HexColor("#DCFCE7")   # light green tint
C_YDIM    = colors.HexColor("#FEF3C7")   # light yellow tint
C_RDIM    = colors.HexColor("#FEE2E2")   # light red tint
C_BDIM    = colors.HexColor("#DBEAFE")   # light blue tint

# ── Styles ───────────────────────────────────────────────────────────────────

def make_styles():
    s = {}
    base = dict(fontName="Helvetica", textColor=C_TEXT, backColor=C_BG, leading=14)

    s["h1"]    = ParagraphStyle("h1",    fontSize=22, fontName="Helvetica-Bold",
                                textColor=C_TEXT, leading=28, spaceAfter=4)
    s["h2"]    = ParagraphStyle("h2",    fontSize=15, fontName="Helvetica-Bold",
                                textColor=C_TEXT, leading=20, spaceAfter=4)
    s["h3"]    = ParagraphStyle("h3",    fontSize=11, fontName="Helvetica-Bold",
                                textColor=C_TEXT, leading=15, spaceAfter=2)
    s["body"]  = ParagraphStyle("body",  fontSize=9,  fontName="Helvetica",
                                textColor=C_MUTED, leading=13, spaceAfter=2)
    s["bodyW"] = ParagraphStyle("bodyW", fontSize=9,  fontName="Helvetica",
                                textColor=C_TEXT, leading=13, spaceAfter=2)
    s["label"] = ParagraphStyle("label", fontSize=7,  fontName="Helvetica-Bold",
                                textColor=C_MUTED, leading=10, spaceAfter=2,
                                wordWrap="CJK")
    s["small"] = ParagraphStyle("small", fontSize=7.5, fontName="Helvetica",
                                textColor=C_MUTED, leading=10)
    s["center"]= ParagraphStyle("center",fontSize=9,  fontName="Helvetica",
                                textColor=C_TEXT, alignment=TA_CENTER, leading=13)
    s["accent"]= ParagraphStyle("accent",fontSize=9,  fontName="Helvetica-Bold",
                                textColor=C_ACCENT, leading=13)
    s["green"] = ParagraphStyle("green", fontSize=9,  fontName="Helvetica-Bold",
                                textColor=C_GREEN, leading=13)
    s["yellow"]= ParagraphStyle("yellow",fontSize=9,  fontName="Helvetica-Bold",
                                textColor=C_YELLOW, leading=13)
    s["red"]   = ParagraphStyle("red",   fontSize=9,  fontName="Helvetica-Bold",
                                textColor=C_RED, leading=13)
    s["footer"]= ParagraphStyle("footer",fontSize=7,  fontName="Helvetica",
                                textColor=C_MUTED, alignment=TA_CENTER, leading=10)
    return s

ST = make_styles()

# ── Custom Flowables ──────────────────────────────────────────────────────────

class ColorRect(Flowable):
    """A filled rectangle used as a separator or card background."""
    def __init__(self, w, h, fill=C_SURFACE, stroke=None, radius=4):
        Flowable.__init__(self)
        self.w, self.h, self.fill, self.stroke, self.radius = w, h, fill, stroke, radius
    def draw(self):
        self.canv.setFillColor(self.fill)
        if self.stroke:
            self.canv.setStrokeColor(self.stroke)
            self.canv.setLineWidth(0.5)
        else:
            self.canv.setStrokeColor(self.fill)
        self.canv.roundRect(0, 0, self.w, self.h, self.radius,
                            fill=1, stroke=1 if self.stroke else 0)

    def wrap(self, *args):
        return (self.w, self.h)


class HBar(Flowable):
    """Thin horizontal rule."""
    def __init__(self, w, color=C_BORDER, thickness=0.5):
        Flowable.__init__(self)
        self.w, self.color, self.thickness = w, color, thickness
    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, 0, self.w, 0)
    def wrap(self, *args):
        return (self.w, self.thickness)


class SlideHeader(Flowable):
    """Dark header bar with slide title."""
    def __init__(self, title, badge_text=None, badge_color=C_YELLOW):
        Flowable.__init__(self)
        self.title = title
        self.badge_text = badge_text
        self.badge_color = badge_color
        self.w = PAGE_W - 2 * M
        self.h = 26

    def draw(self):
        c = self.canv
        c.setFillColor(C_SURFACE)
        c.rect(0, 0, self.w, self.h, fill=1, stroke=0)
        c.setFillColor(C_ACCENT)
        c.rect(0, 0, 4, self.h, fill=1, stroke=0)
        c.setFont("Helvetica-Bold", 13)
        c.setFillColor(C_TEXT)
        c.drawString(10, 8, self.title)
        if self.badge_text:
            bw = len(self.badge_text) * 5.5 + 14
            bx = self.w - bw - 4
            c.setFillColor(C_YDIM if self.badge_color == C_YELLOW
                           else C_GDIM if self.badge_color == C_GREEN
                           else C_RDIM if self.badge_color == C_RED
                           else C_BDIM)
            c.roundRect(bx, 4, bw, 18, 3, fill=1, stroke=0)
            c.setFillColor(self.badge_color)
            c.setFont("Helvetica-Bold", 7)
            c.drawCentredString(bx + bw / 2, 9, self.badge_text)

    def wrap(self, *args):
        return (self.w, self.h)


class StatusCircle(Flowable):
    def __init__(self, letter, status="green", size=28):
        Flowable.__init__(self)
        self.letter, self.status, self.size = letter, status, size
        color_map = {"green": C_GDIM, "yellow": C_YDIM, "red": C_RDIM}
        txt_map   = {"green": C_GREEN, "yellow": C_YELLOW, "red": C_RED}
        self.bg_c  = color_map[status]
        self.txt_c = txt_map[status]

    def draw(self):
        c = self.canv
        r = self.size / 2
        c.setFillColor(self.bg_c)
        c.circle(r, r, r, fill=1, stroke=0)
        c.setFillColor(self.txt_c)
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(r, r - 4, self.letter)

    def wrap(self, *args):
        return (self.size, self.size)


class ProgressBar(Flowable):
    def __init__(self, w, pct, color=C_ACCENT, h=8):
        Flowable.__init__(self)
        self.w, self.pct, self.color, self.h = w, pct, color, h

    def draw(self):
        c = self.canv
        c.setFillColor(C_BORDER)
        c.roundRect(0, 0, self.w, self.h, 2, fill=1, stroke=0)
        if self.pct > 0:
            c.setFillColor(self.color)
            c.roundRect(0, 0, self.w * self.pct / 100, self.h, 2, fill=1, stroke=0)

    def wrap(self, *args):
        return (self.w, self.h)


class KPICard(Flowable):
    def __init__(self, label, value, sub, accent_color, w=168, h=68):
        Flowable.__init__(self)
        self.label, self.value, self.sub = label, value, sub
        self.accent, self.w, self.h = accent_color, w, h

    def draw(self):
        c = self.canv
        c.setFillColor(C_SURFACE)
        c.roundRect(0, 0, self.w, self.h, 5, fill=1, stroke=0)
        c.setFillColor(self.accent)
        c.roundRect(0, self.h - 3, self.w, 3, 0, fill=1, stroke=0)
        c.setFillColor(C_MUTED)
        c.setFont("Helvetica-Bold", 6.5)
        c.drawString(8, self.h - 16, self.label.upper())
        c.setFillColor(self.accent)
        c.setFont("Helvetica-Bold", 17)
        c.drawString(8, self.h - 38, self.value)
        c.setFillColor(C_MUTED)
        c.setFont("Helvetica", 7)
        c.drawString(8, 8, self.sub)

    def wrap(self, *args):
        return (self.w, self.h)


# ── Page background canvas callback ──────────────────────────────────────────

def dark_bg(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(C_BG)
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    # Footer bar
    canvas.setFillColor(C_SURF2)
    canvas.rect(0, 0, PAGE_W, 24, fill=1, stroke=0)
    # Footer top line
    canvas.setStrokeColor(C_BORDER)
    canvas.setLineWidth(0.5)
    canvas.line(0, 24, PAGE_W, 24)
    # Page number
    canvas.setFillColor(C_MUTED)
    canvas.setFont("Helvetica", 7)
    canvas.drawCentredString(PAGE_W / 2, 8,
        f"Radiological Health Program Modernization  ·  Executive Status Report  ·  Page {doc.page}")
    canvas.restoreState()


# ── Story helpers ─────────────────────────────────────────────────────────────

def sp(pts=6):
    return Spacer(1, pts)


def section_label(text):
    return Paragraph(f'<font color="#8F96B3"><b>{text.upper()}</b></font>', ST["label"])


def pill_text(text, color):
    hex_c = color.hexval() if hasattr(color, "hexval") else str(color)
    return Paragraph(f'<font color="{hex_c}"><b>{text}</b></font>', ST["small"])


# ── Slide builders ────────────────────────────────────────────────────────────

def page_title(story):
    """Slide 1 – Cover"""
    w = PAGE_W - 2 * M

    # Hero block
    class CoverHero(Flowable):
        def __init__(self):
            Flowable.__init__(self)
        def draw(self):
            c = self.canv
            c.setFillColor(C_SURFACE)
            c.rect(0, 0, w, 320, fill=1, stroke=0)
            # Left accent bar
            c.setFillColor(C_ACCENT)
            c.rect(0, 0, 5, 320, fill=1, stroke=0)
            # Title
            c.setFillColor(C_TEXT)
            c.setFont("Helvetica-Bold", 28)
            c.drawString(22, 250, "Radiological Health Program")
            c.setFillColor(C_ACCENT)
            c.setFont("Helvetica-Bold", 22)
            c.drawString(22, 218, "Modernization Initiative")
            # Sub
            c.setFillColor(C_MUTED)
            c.setFont("Helvetica", 11)
            c.drawString(22, 185, "Executive Status Report  \u00b7  FY26  \u00b7  June 12, 2026")
            # Badge
            c.setFillColor(C_YDIM)
            c.roundRect(22, 148, 210, 22, 4, fill=1, stroke=0)
            c.setFillColor(C_YELLOW)
            c.setFont("Helvetica-Bold", 9)
            c.drawString(32, 155, "\u25cf  Overall Status: YELLOW")
            # HR
            c.setStrokeColor(C_BORDER)
            c.setLineWidth(0.5)
            c.line(22, 120, w - 22, 120)
            # Footer info
            c.setFillColor(C_MUTED)
            c.setFont("Helvetica", 8)
            c.drawString(22, 102, "Maryland Department of the Environment (MDE)  \u00b7  PCA: 79103  \u00b7  Radiation Control Fund")
            c.drawString(22, 86, "Prepared for Executive Review  \u00b7  July 10, 2026")
            # Watermark symbol
            c.setFillColor(colors.HexColor("#C0D4F0"))
            c.setFont("Helvetica-Bold", 110)
            c.drawCentredString(w - 110, 155, "\u2622")

        def wrap(self, *args):
            return (w, 320)

    story.append(CoverHero())


def page_overview(story):
    """Slide 2 – Project Overview"""
    w = PAGE_W - 2 * M
    story.append(SlideHeader("Project Overview", "Overall: YELLOW", C_YELLOW))
    story.append(sp(8))

    # Description
    desc_data = [[
        Paragraph("<b><font color='#8F96B3'>INITIATIVE</font></b>", ST["label"]),
        Paragraph(
            "The Radiological Health Program (RHP) is launching a strategic modernization initiative to "
            "transition its permitting and licensing application pipeline from legacy, manual workflows "
            "to a centralized online portal and electronic payment module.",
            ST["bodyW"])
    ]]
    desc_tbl = Table(desc_data, colWidths=[80, w - 84])
    desc_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_SURFACE),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [C_SURFACE]),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(desc_tbl)
    story.append(sp(10))

    # Health status indicators
    story.append(section_label("Health Status Indicators"))
    story.append(sp(4))

    dims = [
        ("Scope",    "G", "green"),
        ("Schedule", "G", "green"),
        ("Cost",     "G", "green"),
        ("Risk",     "G", "green"),
        ("Quality",  "R", "red"),
        ("Resources","Y", "yellow"),
    ]
    cw_each = (w - 10) / 6
    cells = []
    for name, letter, status in dims:
        color_map = {"green": C_GREEN, "yellow": C_YELLOW, "red": C_RED}
        txt_c = color_map[status]
        cells.append([
            StatusCircle(letter, status, 30),
            Paragraph(f'<font color="{txt_c.hexval() if hasattr(txt_c,"hexval") else str(txt_c)}"><b>{name}</b></font>',
                      ParagraphStyle("sc", fontSize=8, fontName="Helvetica-Bold",
                                     textColor=txt_c, alignment=TA_CENTER, leading=11))
        ])

    status_rows = [[c[0] for c in cells], [c[1] for c in cells]]
    status_tbl = Table(status_rows, colWidths=[cw_each] * 6)
    status_tbl.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), C_SURF2),
        ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",   (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
        ("GRID",         (0, 0), (-1, -1), 0.3, C_BORDER),
    ]))
    story.append(status_tbl)
    story.append(sp(10))

    # Yellow rationale
    rationale = Table([[
        Paragraph(
            "<b><font color='#F59E0B'>⚠ WHY YELLOW?</font></b><br/>"
            "<font color='#4A5A82'>Environment and resource changes have been identified during the reporting period. "
            "These changes are not expected to impact overall project delivery. "
            "A Tech Lead is being hired to address environmental and build blockers, "
            "as key agency technical resources are engaged in other internal initiatives.</font>",
            ST["bodyW"])
    ]], colWidths=[w])
    rationale.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), C_YDIM),
        ("LEFTPADDING",  (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING",   (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 10),
        ("LINEABOVE",    (0, 0), (-1, 0), 1.5, C_YELLOW),
    ]))
    story.append(rationale)


def page_sprints(story):
    """Slide 3 – Sprint Schedule"""
    w = PAGE_W - 2 * M
    story.append(SlideHeader("Sprint Schedule & Delivery Milestones", "Sprint 2: IN PROGRESS", C_ACCENT))
    story.append(sp(8))

    sprints = [
        ("Sprint 1", "Jun 17 – Jun 30, 2026", "Complete",    100, C_GREEN,
         "Group 3–9: PDF Portal Submissions & Electronic Payments enabled"),
        ("Sprint 2", "Jul 1 – Jul 14, 2026",  "In Progress",  64, C_ACCENT,
         "Group 3–9: Enable Notifications for customers & RHP Team Inbox"),
        ("Sprint 3", "Jul 15 – Jul 28, 2026", "Not Started",   0, C_MUTED,
         "Group 3–9: Provide option to download RHP permits"),
        ("Sprint 4", "Jul 29 – Aug 11, 2026", "Not Started",   0, C_MUTED,
         "Group 3–9: Reject & update status (CRM) for RHP permits"),
        ("Sprint 5", "TBD — Next",            "Not Started",   0, C_MUTED,
         "Group 1–2: Configuration and setup"),
        ("Sprint 6", "TBD — Next",            "Not Started",   0, C_MUTED,
         "Group 3–9: Web Forms Development"),
    ]

    status_bg = {
        "Complete":    C_GDIM,
        "In Progress": C_BDIM,
        "Not Started": C_SURF2,
    }
    status_c = {
        "Complete":    C_GREEN,
        "In Progress": C_ACCENT,
        "Not Started": C_MUTED,
    }

    rows = []
    for name, dates, status, pct, bar_color, goal in sprints:
        txt_c = status_c[status]
        txt_hex = txt_c.hexval() if hasattr(txt_c, "hexval") else str(txt_c)
        rows.append([
            Paragraph(f"<b><font color='#0F172A'>{name}</font></b>", ST["h3"]),
            Paragraph(f"<font color='#8F96B3'>{dates}</font>", ST["small"]),
            Paragraph(f"<font color='#4A5A82'>{goal}</font>", ST["body"]),
            ProgressBar(120, pct, color=bar_color),
            Paragraph(f"<b><font color='{txt_hex}'>{status}</font></b>", ST["small"]),
        ])

    col_w = [70, 110, 310, 130, 80]
    tbl = Table(rows, colWidths=col_w, rowHeights=52)
    ts = [
        ("BACKGROUND",   (0, 0), (-1, -1), C_SURFACE),
        ("ROWBACKGROUNDS",(0,0),(-1,-1), [C_SURFACE, C_SURF2]),
        ("LEFTPADDING",  (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING",   (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 8),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("GRID",         (0, 0), (-1, -1), 0.3, C_BORDER),
    ]
    # Highlight sprint 1 (complete) and sprint 2 (in progress)
    tbl.setStyle(TableStyle(ts))
    story.append(tbl)
    story.append(sp(8))
    story.append(HBar(w))
    story.append(sp(4))
    story.append(Paragraph(
        "<font color='#8F96B3'>Near = within 2 sprints  ·  Next = planned future sprints</font>",
        ST["footer"]))


def page_financials(story):
    """Slide 4 – Financial Summary"""
    w = PAGE_W - 2 * M
    story.append(SlideHeader("Financial Summary", "Cost Status: GREEN", C_GREEN))
    story.append(sp(8))

    # KPI cards row
    kpi_gap = 8
    kpi_w   = (w - kpi_gap * 3) / 4

    kpis = [
        ("Total Approved",  "$6.0M",  "FY25–FY26 Combined",  C_ACCENT),
        ("Total Forecast",  "$3.70M", "FY25–FY28 All Years", C_YELLOW),
        ("Total Actual",    "$1.45M", "FY25+FY26 Spent",     C_GREEN),
        ("Remaining",       "$1.55M", "Balance / Variance",  C_PURPLE),
    ]
    kpi_row = [[KPICard(l, v, s, c, kpi_w - 2, 68) for l, v, s, c in kpis]]
    kpi_tbl = Table(kpi_row, colWidths=[kpi_w] * 4, rowHeights=[72])
    kpi_tbl.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), C_BG),
        ("LEFTPADDING",  (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING",   (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 0),
    ]))
    story.append(kpi_tbl)
    story.append(sp(10))

    # Budget table
    headers = ["Fiscal Year", "Approved", "Forecast", "Actual", "Balance", "Fund Source"]
    data = [
        ["FY-25",  "$1,000,000", "$500,000",    "$275,086",   "$724,914",   "Radiation Control (SF)"],
        ["FY-26",  "$2,000,000", "$1,200,000",  "$1,177,504", "$822,496",   "Radiation Control (SF)"],
        ["FY-27",  "$3,000,000", "$1,468,511",  "—",          "$0",         "Special"],
        ["FY-28",  "—",          "$535,591",    "—",          "$0",         "Special"],
        ["TOTAL",  "$6,000,000", "$3,704,102",  "$1,452,590", "$1,547,410", "—"],
    ]
    header_style = ParagraphStyle("th", fontSize=7.5, fontName="Helvetica-Bold",
                                  textColor=C_MUTED, alignment=TA_CENTER)
    cell_style   = ParagraphStyle("td", fontSize=9, fontName="Helvetica",
                                  textColor=C_TEXT, alignment=TA_RIGHT)
    cell_style_l = ParagraphStyle("tdL", fontSize=9, fontName="Helvetica",
                                  textColor=C_TEXT, alignment=TA_LEFT)
    green_style  = ParagraphStyle("tdG", fontSize=9, fontName="Helvetica-Bold",
                                  textColor=C_GREEN, alignment=TA_RIGHT)
    total_style  = ParagraphStyle("tdT", fontSize=9.5, fontName="Helvetica-Bold",
                                  textColor=C_TEXT, alignment=TA_RIGHT)
    total_styleL = ParagraphStyle("tdTL", fontSize=9.5, fontName="Helvetica-Bold",
                                  textColor=C_TEXT, alignment=TA_LEFT)

    tbl_data = [[Paragraph(h, header_style) for h in headers]]
    for r_idx, row in enumerate(data):
        is_total = r_idx == len(data) - 1
        styled_row = []
        for c_idx, cell in enumerate(row):
            if is_total:
                st = total_styleL if c_idx in (0, 5) else total_style
            elif c_idx == 4 and cell not in ("$0", "—"):
                st = green_style
            elif c_idx in (0, 5):
                st = cell_style_l
            else:
                st = cell_style
            styled_row.append(Paragraph(cell, st))
        tbl_data.append(styled_row)

    col_w = [70, 100, 100, 100, 100, 195 - 10]
    fin_tbl = Table(tbl_data, colWidths=col_w)
    fin_ts = [
        ("BACKGROUND",    (0, 0), (-1,  0), C_BDIM),
        ("BACKGROUND",    (0, 1), (-1, -2), C_SURFACE),
        ("ROWBACKGROUNDS",(0, 1), (-1, -2), [C_SURFACE, C_SURF2]),
        ("BACKGROUND",    (0, -1),(-1, -1), C_BDIM),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("GRID",          (0, 0), (-1, -1), 0.3, C_BORDER),
        ("LINEBELOW",     (0, 0), (-1, 0),  1, C_ACCENT),
    ]
    fin_tbl.setStyle(TableStyle(fin_ts))
    story.append(fin_tbl)
    story.append(sp(10))

    # Utilization bars
    story.append(section_label("Budget Utilization (Actual vs Approved)"))
    story.append(sp(4))
    util_data = [
        ("FY-25", 27.5, C_GREEN),
        ("FY-26", 58.9, C_ACCENT),
        ("FY-27",  0.0, C_MUTED),
    ]
    for fy, pct, col in util_data:
        row_data = [[
            Paragraph(f"<font color='#8F96B3'>{fy}</font>", ST["small"]),
            ProgressBar(w - 120, pct, color=col, h=9),
            Paragraph(f"<b><font color='#0F172A'>{pct}%</font></b>", ST["small"]),
        ]]
        u_tbl = Table(row_data, colWidths=[45, w - 120, 55])
        u_tbl.setStyle(TableStyle([
            ("BACKGROUND",   (0, 0), (-1, -1), C_BG),
            ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING",  (0, 0), (-1, -1), 2),
            ("RIGHTPADDING", (0, 0), (-1, -1), 2),
            ("TOPPADDING",   (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
        ]))
        story.append(u_tbl)


def page_mvp(story):
    """Slide 5 – MVP Capabilities"""
    w = PAGE_W - 2 * M
    story.append(SlideHeader("MVP Capabilities — Groups 3 through 9"))
    story.append(sp(8))

    caps = [
        ("📄", "Portal Submissions",
         "PDF application submissions through the ESC Portal for Groups 3–9.",
         C_ACCENT),
        ("💳", "Electronic Payments",
         "Credit/debit card and E-check to immediately resolve clearing delays.",
         C_GREEN),
        ("🔔", "Notifications",
         "One-time email confirmations for end-users upon application and payment submission.",
         C_YELLOW),
        ("📥", "RHP Team Inbox",
         "Automated notifications to the MDE Business User (RHP Team) inbox.",
         C_PURPLE),
        ("📁", "Document Management",
         "Secure view, download of applications and supporting documents — individual or ZIP.",
         colors.HexColor("#FF7F50")),
        ("🔐", "IAM Authentication",
         "MDE Business User auth via Identity and Access Management (IAM) protocols.",
         colors.HexColor("#06B6D4")),
    ]

    cap_rows = []
    row = []
    cw = (w - 8) / 3
    for i, (icon, name, desc, col) in enumerate(caps):
        hex_c = col.hexval() if hasattr(col, "hexval") else str(col)
        cell = Paragraph(
            f"<b><font color='{hex_c}' size='16'>{icon}</font>"
            f"  <font color='#0F172A'>{name}</font></b><br/>"
            f"<font color='#4A5A82' size='8'>{desc}</font>",
            ParagraphStyle("cap", fontSize=9, fontName="Helvetica",
                           textColor=C_TEXT, leading=14, leftIndent=4))
        row.append(cell)
        if len(row) == 3:
            cap_rows.append(row)
            row = []
    if row:
        while len(row) < 3:
            row.append(Paragraph("", ST["body"]))
        cap_rows.append(row)

    cap_tbl = Table(cap_rows, colWidths=[cw, cw, cw], rowHeights=90)
    cap_ts = [
        ("BACKGROUND",   (0, 0), (-1, -1), C_SURF2),
        ("ROWBACKGROUNDS",(0,0),(-1,-1), [C_SURF2, C_SURFACE]),
        ("GRID",         (0, 0), (-1, -1), 0.5, C_BORDER),
        ("LEFTPADDING",  (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING",   (0, 0), (-1, -1), 18),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 12),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
    ]
    cap_tbl.setStyle(TableStyle(cap_ts))
    story.append(cap_tbl)
    story.append(sp(8))
    story.append(HBar(w))
    story.append(sp(4))
    story.append(Paragraph(
        "<font color='#8F96B3'>Groups 1–2 configuration and setup planned in Sprint 5</font>",
        ST["footer"]))


def page_risks(story):
    """Slide 6 – Risks & Action Items"""
    w = PAGE_W - 2 * M
    story.append(SlideHeader("Risks, Impediments & Action Items", "Overall: YELLOW", C_YELLOW))
    story.append(sp(8))

    story.append(section_label("Active Risks & Impediments"))
    story.append(sp(4))

    risks = [
        ("HIGH",   C_RED,    C_RDIM,
         "Environment & Build Issues",
         "Encountered environment and build issues impacting iterative delivery. "
         "Development and validation processes are established. "
         "Mitigation: Hiring a Tech Lead to prevent future blockers.",
         "Mitigate"),
        ("MEDIUM", C_YELLOW, C_YDIM,
         "Workflow Finalization",
         "Non-ETS workflow approach requires finalization: status tracking, Third-Party access "
         "(Inspectors), Liability Checks, and invoice payment features. "
         "DoIT & MDE teams reviewing enterprise solutions.",
         "Transfer"),
        ("MEDIUM", C_YELLOW, C_YDIM,
         "Registration Number Automation",
         "Program must decide on folder naming convention and whether the system auto-generates "
         "sequence numbers or continues the current manual process. Awaiting program decision.",
         "Mitigate"),
    ]

    for level, col, bg_col, title, desc, strategy in risks:
        hex_c = col.hexval() if hasattr(col, "hexval") else str(col)
        risk_data = [[
            Paragraph(
                f"<b><font color='{hex_c}' size='7.5'>[{level}]</font></b><br/><br/>"
                f"<b><font color='#0F172A' size='10'>{title}</font></b><br/>"
                f"<font color='#4A5A82' size='8.5'>{desc}</font>",
                ST["bodyW"]),
            Paragraph(
                f"<font color='#8F96B3' size='7'>RESPONSE</font><br/>"
                f"<b><font color='{hex_c}' size='13'>{strategy}</font></b>",
                ST["bodyW"]),
        ]]
        risk_tbl = Table(risk_data, colWidths=[w - 130, 120])
        risk_tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), bg_col),
            ("BACKGROUND",    (1, 0), (1,  0),  C_SURFACE),
            ("LEFTPADDING",   (0, 0), (-1, -1), 12),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
            ("TOPPADDING",    (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("LINEABOVE",     (0, 0), (-1, 0), 1.5, col),
            ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(risk_tbl)
        story.append(sp(6))

    story.append(sp(4))
    story.append(section_label("Action Items"))
    story.append(sp(4))

    actions = [
        (C_ACCENT, "MVP Time Savings",
         "Collaborate with program team to generate high-level estimates of days saved per MVP deliverable (80/20 rule)."),
        (C_YELLOW, "Liability Check",
         "Remain coordinated with Emil, Paul, and DoIT team while awaiting update from State Data Officer."),
        (C_GREEN,  "User Testing",
         "Align with Paul to ensure user testing is seamlessly integrated into development cycles."),
    ]

    act_cells = []
    act_w = (w - 12) / 3
    for col, title, desc in actions:
        hex_c = col.hexval() if hasattr(col, "hexval") else str(col)
        act_cells.append(Paragraph(
            f"<b><font color='{hex_c}'>{title}</font></b><br/>"
            f"<font color='#8F96B3' size='8'>{desc}</font>",
            ST["bodyW"]))

    act_tbl = Table([act_cells], colWidths=[act_w, act_w, act_w], rowHeights=72)
    act_tbl.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), C_SURFACE),
        ("GRID",         (0, 0), (-1, -1), 0.4, C_BORDER),
        ("LEFTPADDING",  (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING",   (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 12),
        ("VALIGN",       (0, 0), (-1, -1), "TOP"),
        ("LINEABOVE",    (0, 0), (0, 0), 2, C_ACCENT),
        ("LINEABOVE",    (1, 0), (1, 0), 2, C_YELLOW),
        ("LINEABOVE",    (2, 0), (2, 0), 2, C_GREEN),
    ]))
    story.append(act_tbl)


def page_successes(story):
    """Slide 7 – Successes"""
    w = PAGE_W - 2 * M
    story.append(SlideHeader("Successes & Key Progress — Reporting Period", "Sprint 1: COMPLETE", C_GREEN))
    story.append(sp(8))

    successes = [
        (C_GREEN,  "✅", "MVP Release Development",
         "The team is actively working on the MVP release supporting New Applications for Groups 3 through 9. "
         "Re-certification and Renewal workflows are under review pending Liability Check clarification "
         "(Certificate of Good Standing — the new system does not require a Tax ID or SSN)."),
        (C_ACCENT, "⚙", "ESC Page Validations & Verification",
         "The RHP Team is developing the RHP Configuration Template to govern ESC Portal page validations, "
         "ensuring data integrity and compliance across all application submissions."),
        (C_PURPLE, "🔐","Authentication & Database Restructuring",
         "Work has commenced on MDE Business User authentication using Identity and Access Management (IAM) "
         "protocols, alongside the necessary restructuring of legacy RHP applications and database tables "
         "to support modern workflows."),
    ]

    for col, icon, title, desc in successes:
        hex_c = col.hexval() if hasattr(col, "hexval") else str(col)
        suc_data = [[
            Paragraph(f"<font size='22'>{icon}</font>", ST["center"]),
            Paragraph(
                f"<b><font color='#0F172A' size='12'>{title}</font></b><br/>"
                f"<font color='#4A5A82' size='9'>{desc}</font>",
                ST["bodyW"]),
        ]]
        suc_tbl = Table(suc_data, colWidths=[50, w - 54], rowHeights=85)
        suc_tbl.setStyle(TableStyle([
            ("BACKGROUND",   (0, 0), (-1, -1), C_SURFACE),
            ("LINEABOVE",    (0, 0), (-1, 0), 0, col),
            ("LEFTBORDER",   (0, 0), (0,  0), 4, col),
            ("LEFTPADDING",  (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ("TOPPADDING",   (0, 0), (-1, -1), 16),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 10),
            ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
            ("LINEBEFORE",   (0, 0), (0,  0), 4, col),
        ]))
        story.append(suc_tbl)
        story.append(sp(8))

    story.append(HBar(w))
    story.append(sp(4))
    story.append(Paragraph(
        "<font color='#8F96B3'>Sprint 1 completed successfully  ·  Sprint 2 currently in progress (Jul 1–14, 2026)</font>",
        ST["footer"]))


def page_summary(story):
    """Slide 8 – Executive Summary & Next Steps"""
    w = PAGE_W - 2 * M
    story.append(SlideHeader("Executive Summary & Next Steps"))
    story.append(sp(8))

    # At-a-glance status
    statuses = [
        ("Overall",  "YELLOW",   C_YELLOW, C_YDIM),
        ("Schedule", "ON TRACK", C_GREEN,  C_GDIM),
        ("Cost",     "ON TRACK", C_GREEN,  C_GDIM),
        ("Delivery", "MVP Q3",   C_ACCENT, C_BDIM),
    ]
    sw = (w - 18) / 4
    stat_cells = []
    for lbl, val, col, bg in statuses:
        hex_c = col.hexval() if hasattr(col, "hexval") else str(col)
        stat_cells.append(Paragraph(
            f"<font color='#8F96B3' size='7'>{lbl.upper()}</font><br/>"
            f"<b><font color='{hex_c}' size='14'>{val}</font></b>",
            ParagraphStyle("sc2", fontSize=9, fontName="Helvetica",
                           textColor=C_TEXT, alignment=TA_CENTER, leading=18)))

    stat_tbl = Table([stat_cells], colWidths=[sw, sw, sw, sw], rowHeights=52)
    stat_ts = [
        ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING",   (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 8),
        ("BACKGROUND",   (0, 0), (0, 0), C_YDIM),
        ("BACKGROUND",   (1, 0), (1, 0), C_GDIM),
        ("BACKGROUND",   (2, 0), (2, 0), C_GDIM),
        ("BACKGROUND",   (3, 0), (3, 0), C_BDIM),
        ("LINEBELOW",    (0, 0), (0, 0), 2, C_YELLOW),
        ("LINEBELOW",    (1, 0), (1, 0), 2, C_GREEN),
        ("LINEBELOW",    (2, 0), (2, 0), 2, C_GREEN),
        ("LINEBELOW",    (3, 0), (3, 0), 2, C_ACCENT),
    ]
    stat_tbl.setStyle(TableStyle(stat_ts))
    story.append(stat_tbl)
    story.append(sp(10))

    # Key takeaways
    story.append(section_label("Key Takeaways"))
    story.append(sp(4))

    takeaways = [
        (C_GREEN,  "On Budget",
         "Actual spend of $1.45M is tracking below forecast. Remaining balance of $1.55M provides a healthy fiscal buffer."),
        (C_GREEN,  "Delivery On Track",
         "Sprint 1 completed. Sprint 2 in progress. Core MVP capabilities on schedule for Groups 3–9."),
        (C_RED,    "Quality — Attention Needed",
         "Build/environment issues were encountered in Sprint 1. Tech Lead hiring in progress to prevent recurrence."),
        (C_YELLOW, "Decisions Pending",
         "Workflow finalization and registration number automation require program decisions to maintain delivery velocity."),
    ]
    tw = (w - 12) / 4
    tk_cells = []
    for col, title, desc in takeaways:
        hex_c = col.hexval() if hasattr(col, "hexval") else str(col)
        tk_cells.append(Paragraph(
            f"<b><font color='{hex_c}'>{title}</font></b><br/>"
            f"<font color='#8F96B3' size='8'>{desc}</font>",
            ST["bodyW"]))

    tk_tbl = Table([tk_cells], colWidths=[tw, tw, tw, tw], rowHeights=88)
    tk_ts = [
        ("BACKGROUND",   (0, 0), (-1, -1), C_SURFACE),
        ("GRID",         (0, 0), (-1, -1), 0.3, C_BORDER),
        ("LEFTPADDING",  (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING",   (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 10),
        ("VALIGN",       (0, 0), (-1, -1), "TOP"),
        ("LINEABOVE",    (0, 0), (0, 0), 2.5, C_GREEN),
        ("LINEABOVE",    (1, 0), (1, 0), 2.5, C_GREEN),
        ("LINEABOVE",    (2, 0), (2, 0), 2.5, C_RED),
        ("LINEABOVE",    (3, 0), (3, 0), 2.5, C_YELLOW),
    ]
    tk_tbl.setStyle(TableStyle(tk_ts))
    story.append(tk_tbl)
    story.append(sp(10))

    # Next steps
    story.append(section_label("Immediate Next Steps"))
    story.append(sp(4))

    next_steps = [
        (C_ACCENT, "Complete Sprint 2",        "Jul 1–14, 2026",     "Enable customer notifications & RHP Team inbox"),
        (C_ACCENT, "Finalize Workflow",         "Ongoing",            "Resolve non-ETS workflow with DoIT & MDE teams"),
        (C_YELLOW, "State Data Officer Input",  "Awaiting",           "Liability Check decision — Emil/Paul/DoIT"),
        (C_GREEN,  "Hire Tech Lead",            "Active Recruiting",  "Address build/environment blockers proactively"),
        (C_GREEN,  "User Testing Alignment",    "Sprint 2–3",         "Coordinate with Paul to integrate testing into dev cycle"),
    ]

    ns_rows = []
    for col, step, timeline, detail in next_steps:
        hex_c = col.hexval() if hasattr(col, "hexval") else str(col)
        ns_rows.append([
            Paragraph(f"<b><font color='{hex_c}'>●</font></b>", ST["center"]),
            Paragraph(f"<b><font color='#0F172A'>{step}</font></b>", ST["bodyW"]),
            Paragraph(f"<font color='{hex_c}'>{timeline}</font>", ST["bodyW"]),
            Paragraph(f"<font color='#8F96B3'>{detail}</font>", ST["body"]),
        ])

    ns_tbl = Table(ns_rows, colWidths=[20, 175, 120, w - 320], rowHeights=28)
    ns_tbl.setStyle(TableStyle([
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [C_SURFACE, C_SURF2]),
        ("GRID",          (0, 0), (-1, -1), 0.3, C_BORDER),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(ns_tbl)
    story.append(sp(8))
    story.append(HBar(w))
    story.append(sp(4))
    story.append(Paragraph(
        "RHP Modernization Initiative  ·  MDE  ·  Prepared for Executive Review  ·  July 10, 2026",
        ST["footer"]))


# ── Build ─────────────────────────────────────────────────────────────────────

def build():
    out = "dashboard/RHP_Executive_Status.pdf"
    doc = SimpleDocTemplate(
        out,
        pagesize=landscape(A4),
        leftMargin=M, rightMargin=M,
        topMargin=M, bottomMargin=30,
        title="RHP Modernization – Executive Status Report",
        author="Maryland Department of the Environment",
        subject="FY26 Project Status Report",
    )

    slides = [
        page_title,
        page_overview,
        page_sprints,
        page_financials,
        page_mvp,
        page_risks,
        page_successes,
        page_summary,
    ]

    story = []
    for i, slide_fn in enumerate(slides):
        slide_fn(story)
        if i < len(slides) - 1:
            story.append(PageBreak())

    doc.build(story, onFirstPage=dark_bg, onLaterPages=dark_bg)
    print(f"Saved → {out}")


if __name__ == "__main__":
    build()
