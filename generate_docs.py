###############################################################
# AI LINUX COMMAND ASSISTANT — DOCUMENTATION GENERATOR
# Generates a professional PDF user guide
# Run: python generate_docs.py
###############################################################

from reportlab.lib.pagesizes   import A4
from reportlab.lib.styles      import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units       import cm, mm
from reportlab.lib             import colors
from reportlab.lib.enums       import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus        import (
    SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, HRFlowable, PageBreak, ListFlowable,
    ListItem, KeepTogether
)
from reportlab.platypus.flowables import Flowable
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Circle
from reportlab.graphics        import renderPDF
import datetime

###############################################################
# OUTPUT FILE
###############################################################
OUTPUT_FILE = "AI_Linux_Assistant_Documentation.pdf"

###############################################################
# COLOR PALETTE
###############################################################
C_BG         = colors.HexColor("#1e1e2e")
C_BLUE       = colors.HexColor("#89b4fa")
C_GREEN      = colors.HexColor("#a6e3a1")
C_YELLOW     = colors.HexColor("#f9e2af")
C_RED        = colors.HexColor("#f38ba8")
C_PURPLE     = colors.HexColor("#cba6f7")
C_ORANGE     = colors.HexColor("#fab387")
C_GRAY       = colors.HexColor("#6c7086")
C_WHITE      = colors.HexColor("#cdd6f4")
C_DARK       = colors.HexColor("#181825")
C_MID        = colors.HexColor("#313244")
C_BLACK      = colors.HexColor("#11111b")
C_TEAL       = colors.HexColor("#94e2d5")

###############################################################
# PAGE TEMPLATE WITH HEADER/FOOTER
###############################################################
class DocTemplate(SimpleDocTemplate):
    def __init__(self, filename, **kwargs):
        super().__init__(filename, **kwargs)
        self.page_num = 0

    def handle_pageBegin(self):
        self.page_num += 1
        super().handle_pageBegin()


def header_footer(canvas, doc):
    """Draw header and footer on every page."""
    canvas.saveState()
    w, h = A4

    # ── HEADER ────────────────────────────────────────────
    canvas.setFillColor(C_BG)
    canvas.rect(0, h - 1.2*cm, w, 1.2*cm, fill=1, stroke=0)

    canvas.setFillColor(C_BLUE)
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(
        1.5*cm, h - 0.85*cm,
        "AI Linux Command Assistant"
    )

    canvas.setFillColor(C_GRAY)
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(
        w - 1.5*cm, h - 0.85*cm,
        "User Documentation v1.0"
    )

    # header line
    canvas.setStrokeColor(C_BLUE)
    canvas.setLineWidth(1.5)
    canvas.line(1.5*cm, h - 1.2*cm, w - 1.5*cm, h - 1.2*cm)

    # ── FOOTER ────────────────────────────────────────────
    canvas.setFillColor(C_BG)
    canvas.rect(0, 0, w, 1.2*cm, fill=1, stroke=0)

    # footer line
    canvas.setStrokeColor(C_MID)
    canvas.setLineWidth(1)
    canvas.line(1.5*cm, 1.2*cm, w - 1.5*cm, 1.2*cm)

    canvas.setFillColor(C_GRAY)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(
        1.5*cm, 0.5*cm,
        f"© {datetime.datetime.now().year} AI Linux Command Assistant"
        " — All Rights Reserved"
    )
    canvas.drawRightString(
        w - 1.5*cm, 0.5*cm,
        f"Page {doc.page}"
    )

    canvas.restoreState()


def header_footer_skip_cover(canvas, doc):
    """Skip header/footer on cover page."""
    if doc.page == 1:
        return
    header_footer(canvas, doc)


###############################################################
# CUSTOM FLOWABLES
###############################################################
class ColorBar(Flowable):
    """Colored horizontal divider bar."""
    def __init__(self, color=C_BLUE, height=4, width=None):
        super().__init__()
        self.bar_color  = color
        self.bar_height = height
        self.bar_width  = width

    def draw(self):
        w = self.bar_width or self.canv._pagesize[0] - 3*cm
        self.canv.setFillColor(self.bar_color)
        self.canv.rect(0, 0, w, self.bar_height, fill=1, stroke=0)

    def wrap(self, availWidth, availHeight):
        self.bar_width = availWidth
        return availWidth, self.bar_height


class SectionBox(Flowable):
    """Colored background box for section headers."""
    def __init__(self, text, bg=C_BG, text_color=C_BLUE,
                 font_size=14, padding=10):
        super().__init__()
        self.text       = text
        self.bg         = bg
        self.text_color = text_color
        self.font_size  = font_size
        self.padding    = padding
        self._width     = 400
        self._height    = font_size + padding * 2

    def draw(self):
        self.canv.setFillColor(self.bg)
        self.canv.roundRect(
            0, 0, self._width,
            self._height, 6,
            fill=1, stroke=0
        )
        self.canv.setFillColor(C_BLUE)
        self.canv.rect(
            0, 0, 5, self._height,
            fill=1, stroke=0
        )
        self.canv.setFillColor(self.text_color)
        self.canv.setFont("Helvetica-Bold", self.font_size)
        self.canv.drawString(
            self.padding + 6,
            self.padding,
            self.text
        )

    def wrap(self, availWidth, availHeight):
        self._width  = availWidth
        self._height = self.font_size + self.padding * 2
        return availWidth, self._height


class CodeBlock(Flowable):
    """Styled code block."""
    def __init__(self, code, bg=C_DARK, text_color=C_GREEN,
                 font_size=9.5):
        super().__init__()
        self.code       = code
        self.bg         = bg
        self.text_color = text_color
        self.font_size  = font_size
        self._width     = 400
        self.lines      = code.strip().splitlines()

    def draw(self):
        line_h = self.font_size + 4
        total_h = len(self.lines) * line_h + 16

        # background
        self.canv.setFillColor(self.bg)
        self.canv.roundRect(
            0, 0, self._width,
            total_h, 4,
            fill=1, stroke=0
        )

        # left accent bar
        self.canv.setFillColor(C_GREEN)
        self.canv.rect(0, 0, 4, total_h, fill=1, stroke=0)

        # code text
        self.canv.setFillColor(self.text_color)
        self.canv.setFont("Courier", self.font_size)

        y = total_h - line_h - 4
        for line in self.lines:
            self.canv.drawString(12, y, line)
            y -= line_h

    def wrap(self, availWidth, availHeight):
        self._width  = availWidth
        line_h       = self.font_size + 4
        total_h      = len(self.lines) * line_h + 16
        return availWidth, total_h


###############################################################
# STYLES
###############################################################
def build_styles():
    base = getSampleStyleSheet()

    styles = {
        "cover_title": ParagraphStyle(
            "cover_title",
            fontSize=38,
            fontName="Helvetica-Bold",
            textColor=C_BLUE,
            alignment=TA_CENTER,
            spaceAfter=6
        ),
        "cover_sub": ParagraphStyle(
            "cover_sub",
            fontSize=16,
            fontName="Helvetica",
            textColor=C_WHITE,
            alignment=TA_CENTER,
            spaceAfter=4
        ),
        "cover_version": ParagraphStyle(
            "cover_version",
            fontSize=12,
            fontName="Helvetica",
            textColor=C_GRAY,
            alignment=TA_CENTER,
            spaceAfter=2
        ),
        "h1": ParagraphStyle(
            "h1",
            fontSize=20,
            fontName="Helvetica-Bold",
            textColor=C_BLUE,
            spaceBefore=18,
            spaceAfter=8,
            borderPad=4
        ),
        "h2": ParagraphStyle(
            "h2",
            fontSize=15,
            fontName="Helvetica-Bold",
            textColor=C_YELLOW,
            spaceBefore=12,
            spaceAfter=6
        ),
        "h3": ParagraphStyle(
            "h3",
            fontSize=12,
            fontName="Helvetica-Bold",
            textColor=C_GREEN,
            spaceBefore=8,
            spaceAfter=4
        ),
        "body": ParagraphStyle(
            "body",
            fontSize=10.5,
            fontName="Helvetica",
            textColor=C_WHITE,
            spaceBefore=4,
            spaceAfter=4,
            leading=16,
            alignment=TA_JUSTIFY
        ),
        "bullet": ParagraphStyle(
            "bullet",
            fontSize=10.5,
            fontName="Helvetica",
            textColor=C_WHITE,
            spaceBefore=2,
            spaceAfter=2,
            leftIndent=16,
            leading=15
        ),
        "note": ParagraphStyle(
            "note",
            fontSize=10,
            fontName="Helvetica-Oblique",
            textColor=C_YELLOW,
            spaceBefore=4,
            spaceAfter=4,
            leftIndent=12,
            leading=14
        ),
        "warn": ParagraphStyle(
            "warn",
            fontSize=10,
            fontName="Helvetica-Bold",
            textColor=C_RED,
            spaceBefore=4,
            spaceAfter=4,
            leftIndent=12,
            leading=14
        ),
        "tip": ParagraphStyle(
            "tip",
            fontSize=10,
            fontName="Helvetica",
            textColor=C_TEAL,
            spaceBefore=4,
            spaceAfter=4,
            leftIndent=12,
            leading=14
        ),
        "toc_h1": ParagraphStyle(
            "toc_h1",
            fontSize=11,
            fontName="Helvetica-Bold",
            textColor=C_BLUE,
            spaceBefore=6,
            spaceAfter=2,
            leftIndent=0
        ),
        "toc_h2": ParagraphStyle(
            "toc_h2",
            fontSize=10,
            fontName="Helvetica",
            textColor=C_WHITE,
            spaceBefore=2,
            spaceAfter=1,
            leftIndent=16
        ),
        "table_header": ParagraphStyle(
            "table_header",
            fontSize=10,
            fontName="Helvetica-Bold",
            textColor=C_BG,
            alignment=TA_CENTER
        ),
        "table_cell": ParagraphStyle(
            "table_cell",
            fontSize=9.5,
            fontName="Helvetica",
            textColor=C_WHITE,
            leading=13
        ),
        "shortcut_key": ParagraphStyle(
            "shortcut_key",
            fontSize=9.5,
            fontName="Courier-Bold",
            textColor=C_YELLOW,
            alignment=TA_CENTER
        ),
    }
    return styles


###############################################################
# TABLE STYLE HELPER
###############################################################
def styled_table(data, col_widths, header_bg=C_BLUE):
    tbl = Table(data, colWidths=col_widths)
    tbl.setStyle(TableStyle([
        # header row
        ("BACKGROUND",  (0, 0), (-1, 0),  header_bg),
        ("TEXTCOLOR",   (0, 0), (-1, 0),  C_BG),
        ("FONTNAME",    (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, 0),  10),
        ("ALIGN",       (0, 0), (-1, 0),  "CENTER"),
        ("TOPPADDING",  (0, 0), (-1, 0),  8),
        ("BOTTOMPADDING",(0, 0),(-1, 0),  8),

        # data rows
        ("BACKGROUND",  (0, 1), (-1, -1), C_DARK),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),  [C_DARK, C_BG]),
        ("TEXTCOLOR",   (0, 1), (-1, -1), C_WHITE),
        ("FONTNAME",    (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",    (0, 1), (-1, -1), 9.5),
        ("ALIGN",       (0, 1), (-1, -1), "LEFT"),
        ("TOPPADDING",  (0, 1), (-1, -1), 6),
        ("BOTTOMPADDING",(0,1),(-1,-1),   6),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),

        # grid
        ("GRID",        (0, 0), (-1, -1), 0.5, C_MID),
        ("ROUNDEDCORNERS", [4]),
    ]))
    return tbl


###############################################################
# DOCUMENT SECTIONS
###############################################################

# ── COVER PAGE ────────────────────────────────────────────────
def build_cover(S):
    elems = []

    # ── TOP SPACE ─────────────────────────────────────────
    elems.append(Spacer(1, 1.5*cm))

    # ── FAKE TERMINAL BANNER (pure Table, no Drawing) ─────
    terminal_lines = [
        ["$ ollama run llama3"],
        ["> How do I monitor CPU usage?"],
        ["  top -bn1 | grep 'Cpu(s)'"],
        ["  "],
    ]
    terminal_tbl = Table(terminal_lines, colWidths=[15.5*cm])
    terminal_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#0d0d0d")),
        ("TEXTCOLOR",     (0, 0), (0, 0),   colors.HexColor("#a6e3a1")),
        ("TEXTCOLOR",     (0, 1), (0, 1),   colors.HexColor("#89b4fa")),
        ("TEXTCOLOR",     (0, 2), (0, 2),   colors.HexColor("#cdd6f4")),
        ("TEXTCOLOR",     (0, 3), (0, 3),   colors.HexColor("#0d0d0d")),
        ("FONTNAME",      (0, 0), (-1, -1), "Courier-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 12),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 16),
        ("BOX",           (0, 0), (-1, -1), 2, colors.HexColor("#89b4fa")),
    ]))

    # title bar row above terminal
    titlebar_data = [
        ["  ● ● ●    AI Linux Command Assistant Terminal"],
    ]
    titlebar_tbl = Table(titlebar_data, colWidths=[15.5*cm])
    titlebar_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#313244")),
        ("TEXTCOLOR",     (0, 0), (-1, -1), colors.HexColor("#6c7086")),
        ("FONTNAME",      (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 10),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("BOX",           (0, 0), (-1, -1), 2, colors.HexColor("#89b4fa")),
    ]))

    elems.append(titlebar_tbl)
    elems.append(terminal_tbl)

    # ── SPACE AFTER BANNER ────────────────────────────────
    elems.append(Spacer(1, 1.0*cm))

    # ── MAIN TITLE ────────────────────────────────────────
    elems.append(Paragraph(
        "AI Linux Command Assistant",
        ParagraphStyle(
            "ct",
            fontSize=32,
            fontName="Helvetica-Bold",
            textColor=colors.HexColor("#89b4fa"),
            alignment=TA_CENTER,
            spaceAfter=0,
            spaceBefore=0,
            leading=38,
        )
    ))

    # ── SPACE ─────────────────────────────────────────────
    elems.append(Spacer(1, 0.4*cm))

    # ── SUBTITLE ──────────────────────────────────────────
    elems.append(Paragraph(
        "Intelligent Terminal  ·  Powered by Ollama LLM",
        ParagraphStyle(
            "cs",
            fontSize=14,
            fontName="Helvetica",
            textColor=colors.HexColor("#cdd6f4"),
            alignment=TA_CENTER,
            spaceAfter=0,
            spaceBefore=0,
            leading=20,
        )
    ))

    # ── SPACE ─────────────────────────────────────────────
    elems.append(Spacer(1, 0.4*cm))

    # ── BLUE DIVIDER ──────────────────────────────────────
    divider_data = [[" "]]
    divider_tbl = Table(divider_data, colWidths=[15.5*cm])
    divider_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#89b4fa")),
        ("TOPPADDING",    (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))
    elems.append(divider_tbl)

    # ── SPACE ─────────────────────────────────────────────
    elems.append(Spacer(1, 0.4*cm))

    # ── VERSION ───────────────────────────────────────────
    elems.append(Paragraph(
        "User Documentation  —  Version 1.0.0",
        ParagraphStyle(
            "cv",
            fontSize=11,
            fontName="Helvetica",
            textColor=colors.HexColor("#6c7086"),
            alignment=TA_CENTER,
            spaceAfter=0,
            spaceBefore=0,
            leading=16,
        )
    ))

    # ── DATE ──────────────────────────────────────────────
    elems.append(Paragraph(
        f"Generated: {datetime.datetime.now().strftime('%B %d, %Y')}",
        ParagraphStyle(
            "cd",
            fontSize=10,
            fontName="Helvetica",
            textColor=colors.HexColor("#6c7086"),
            alignment=TA_CENTER,
            spaceAfter=0,
            spaceBefore=0,
            leading=14,
        )
    ))

    # ── SPACE ─────────────────────────────────────────────
    elems.append(Spacer(1, 0.8*cm))

    # ── APP INFO TABLE ────────────────────────────────────
    info_data = [
        ["Application",   "AI Linux Command Assistant"],
        ["Version",       "1.0.0"],
        ["Platform",      "Windows / Linux / macOS"],
        ["Language",      "Python 3.10+"],
        ["AI Engine",     "Ollama  (Local LLM — No internet required)"],
        ["GUI Framework", "PyQt5"],
        ["Database",      "SQLite3"],
    ]
    info_tbl = Table(info_data, colWidths=[5*cm, 10*cm])
    info_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (0, -1), colors.HexColor("#313244")),
        ("BACKGROUND",    (1, 0), (1, -1), colors.HexColor("#181825")),
        ("TEXTCOLOR",     (0, 0), (0, -1), colors.HexColor("#89b4fa")),
        ("TEXTCOLOR",     (1, 0), (1, -1), colors.HexColor("#cdd6f4")),
        ("FONTNAME",      (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME",      (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 0), (-1, -1), 10),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#313244")),
    ]))
    elems.append(info_tbl)

    # ── SPACE ─────────────────────────────────────────────
    elems.append(Spacer(1, 0.6*cm))

    # ── GRAY DIVIDER ──────────────────────────────────────
    gray_div = [[" "]]
    gray_tbl = Table(gray_div, colWidths=[15.5*cm])
    gray_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#313244")),
        ("TOPPADDING",    (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))
    elems.append(gray_tbl)

    # ── SPACE ─────────────────────────────────────────────
    elems.append(Spacer(1, 0.5*cm))

    # ── AUTHOR TABLE ──────────────────────────────────────
    author_data = [
        ["Author / Developer", "Joseph Iskandar"],
        ["Role",               "Software Engineer & Developer"],
        ["Tool",               "AI Linux Command Assistant v1.0.0"],
    ]
    author_tbl = Table(author_data, colWidths=[5*cm, 10*cm])
    author_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (0, -1), colors.HexColor("#2a2a3e")),
        ("BACKGROUND",    (1, 0), (1, -1), colors.HexColor("#181825")),
        ("TEXTCOLOR",     (0, 0), (0, -1), colors.HexColor("#cba6f7")),
        ("TEXTCOLOR",     (1, 0), (1, -1), colors.HexColor("#f9e2af")),
        ("FONTNAME",      (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME",      (1, 0), (1, -1), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 10),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#313244")),
    ]))
    elems.append(author_tbl)

    # ── END OF COVER ──────────────────────────────────────
    elems.append(PageBreak())
    return elems


# ── TABLE OF CONTENTS ─────────────────────────────────────────
def build_toc(S):
    elems = []
    elems.append(Spacer(1, 0.5*cm))
    elems.append(SectionBox("TABLE OF CONTENTS", bg=C_BG, font_size=16))
    elems.append(Spacer(1, 0.5*cm))
    elems.append(ColorBar(C_BLUE, height=2))
    elems.append(Spacer(1, 0.4*cm))

    toc = [
        ("1", "Introduction",                            "3"),
        ("1.1", "What is AI Linux Command Assistant?",   "3"),
        ("1.2", "Key Benefits",                          "3"),
        ("1.3", "Technology Stack",                      "3"),
        ("2", "System Requirements",                     "4"),
        ("2.1", "Hardware Requirements",                 "4"),
        ("2.2", "Software Requirements",                 "4"),
        ("3", "Installation Guide",                      "5"),
        ("3.1", "Step 1: Install Python",                "5"),
        ("3.2", "Step 2: Install Ollama",                "5"),
        ("3.3", "Step 3: Install Dependencies",          "5"),
        ("3.4", "Step 4: Download AI Model",             "6"),
        ("3.5", "Step 5: Run the Application",           "6"),
        ("4", "Application Layout",                      "7"),
        ("4.1", "Toolbar",                               "7"),
        ("4.2", "AI Chat Panel",                         "7"),
        ("4.3", "Terminal Output Panel",                 "7"),
        ("4.4", "Favorites & History Tabs",              "8"),
        ("5", "Using the AI Assistant",                  "8"),
        ("5.1", "Asking Questions",                      "8"),
        ("5.2", "Running Commands",                      "9"),
        ("5.3", "Switching AI Models",                   "9"),
        ("6", "Favorites Database",                      "10"),
        ("6.1", "Adding Favorites",                      "10"),
        ("6.2", "Searching & Filtering",                 "10"),
        ("6.3", "Editing & Deleting",                    "10"),
        ("6.4", "Import & Export",                       "11"),
        ("7", "Command History",                         "11"),
        ("8", "Font Size & Display",                     "11"),
        ("9", "Keyboard Shortcuts",                      "12"),
        ("10", "Supported AI Models",                    "12"),
        ("11", "Troubleshooting",                        "13"),
        ("12", "FAQ",                                    "14"),
        ("13", "Safety & Security",                      "15"),
    ]

    for num, title, page in toc:
        is_main = len(num) == 1
        style   = S["toc_h1"] if is_main else S["toc_h2"]
        dots    = "." * max(1, 60 - len(f"{num}. {title}") - len(str(page)))
        elems.append(Paragraph(
            f"{num}. {title} "
            f"<font color='#313244'>{dots}</font> "
            f"<font color='#89b4fa'>{page}</font>",
            style
        ))

    elems.append(PageBreak())
    return elems


# ── SECTION 1: INTRODUCTION ──────────────────────────────────
def build_intro(S):
    elems = []
    elems.append(Paragraph("1. Introduction", S["h1"]))
    elems.append(ColorBar(C_BLUE, height=2))
    elems.append(Spacer(1, 0.3*cm))

    # 1.1
    elems.append(Paragraph(
        "1.1 What is AI Linux Command Assistant?", S["h2"]
    ))
    elems.append(Paragraph(
        "AI Linux Command Assistant is a professional desktop application "
        "that combines the power of a local Large Language Model (LLM) "
        "with a fully functional Linux terminal interface. "
        "It allows users to ask natural language questions about Linux "
        "commands and receive accurate, context-aware answers — all running "
        "locally on your machine with no internet required.",
        S["body"]
    ))
    elems.append(Paragraph(
        "Whether you are a system administrator, DevOps engineer, developer, "
        "or student learning Linux, this tool dramatically accelerates your "
        "workflow by eliminating the need to manually search documentation "
        "or memorize complex command syntax.",
        S["body"]
    ))

    # 1.2
    elems.append(Paragraph("1.2 Key Benefits", S["h2"]))
    benefits = [
        "✔  Ask any Linux question in plain English and get instant answers",
        "✔  Execute commands directly inside the app without switching windows",
        "✔  Save your favorite commands in a searchable personal database",
        "✔  All AI processing runs locally — your data never leaves your machine",
        "✔  Streaming AI responses appear in real-time as they are generated",
        "✔  Full command history with one-click reuse",
        "✔  Built-in safety checks to prevent accidental destructive commands",
        "✔  Professional dark theme UI with adjustable font sizes",
        "✔  Support for multiple Ollama AI models",
        "✔  Export and import your favorite commands as JSON",
    ]
    for b in benefits:
        elems.append(Paragraph(b, S["bullet"]))

    # 1.3
    elems.append(Paragraph("1.3 Technology Stack", S["h2"]))
    tech_data = [
        ["Component",     "Technology",    "Purpose"],
        ["GUI Framework", "PyQt5",         "Professional desktop interface"],
        ["AI Engine",     "Ollama",        "Local LLM inference"],
        ["AI Models",     "LLaMA 3 / Mistral / CodeLlama",
                                           "Natural language processing"],
        ["Database",      "SQLite3",       "Favorites storage"],
        ["Terminal",      "subprocess",    "Linux command execution"],
        ["Syntax Highlight","QSyntaxHighlighter","Code colorization"],
        ["Packaging",     "PyInstaller",   "EXE build"],
    ]
    tech_tbl = styled_table(
        tech_data,
        [4*cm, 5*cm, 6.5*cm]
    )
    elems.append(tech_tbl)
    elems.append(PageBreak())
    return elems


# ── SECTION 2: REQUIREMENTS ───────────────────────────────────
def build_requirements(S):
    elems = []
    elems.append(Paragraph("2. System Requirements", S["h1"]))
    elems.append(ColorBar(C_BLUE, height=2))
    elems.append(Spacer(1, 0.3*cm))

    elems.append(Paragraph("2.1 Hardware Requirements", S["h2"]))
    hw_data = [
        ["Component", "Minimum",           "Recommended"],
        ["CPU",       "Intel Core i5",     "Intel Core i7 / AMD Ryzen 7"],
        ["RAM",       "8 GB",              "16 GB or more"],
        ["Storage",   "10 GB free space",  "20 GB free space"],
        ["GPU",       "Not required",      "NVIDIA GPU (speeds up LLM)"],
        ["Display",   "1280 × 720",        "1920 × 1080 or higher"],
    ]
    elems.append(styled_table(hw_data, [4*cm, 4.5*cm, 7*cm]))
    elems.append(Spacer(1, 0.4*cm))

    elems.append(Paragraph("2.2 Software Requirements", S["h2"]))
    sw_data = [
        ["Software",      "Version",    "Notes"],
        ["Python",        "3.10 +",     "Must be installed before running"],
        ["Ollama",        "Latest",     "Free download at ollama.com"],
        ["PyQt5",         "5.15 +",     "pip install PyQt5"],
        ["ollama (Python)","Latest",    "pip install ollama"],
        ["reportlab",     "Latest",     "pip install reportlab (for docs)"],
        ["PyInstaller",   "Latest",     "pip install pyinstaller (for EXE)"],
        ["OS",            "Any",        "Windows 10+, Ubuntu 20+, macOS 12+"],
    ]
    elems.append(styled_table(sw_data, [4*cm, 3*cm, 8.5*cm]))
    elems.append(PageBreak())
    return elems


# ── SECTION 3: INSTALLATION ───────────────────────────────────
def build_installation(S):
    elems = []
    elems.append(Paragraph("3. Installation Guide", S["h1"]))
    elems.append(ColorBar(C_BLUE, height=2))
    elems.append(Spacer(1, 0.3*cm))

    # 3.1
    elems.append(Paragraph("3.1 Step 1 — Install Python", S["h2"]))
    elems.append(Paragraph(
        "Download and install Python 3.10 or higher from the official website:",
        S["body"]
    ))
    elems.append(CodeBlock("https://www.python.org/downloads/"))
    elems.append(Paragraph(
        "⚠  During installation on Windows, check "
        "'Add Python to PATH' before clicking Install.",
        S["warn"]
    ))
    elems.append(Paragraph(
        "Verify the installation by opening a terminal and running:",
        S["body"]
    ))
    elems.append(CodeBlock("python --version"))
    elems.append(Spacer(1, 0.3*cm))

    # 3.2
    elems.append(Paragraph("3.2 Step 2 — Install Ollama", S["h2"]))
    elems.append(Paragraph(
        "Ollama is the local AI engine that powers the assistant. "
        "Download and install it from:",
        S["body"]
    ))
    elems.append(CodeBlock("https://ollama.com"))
    elems.append(Paragraph(
        "After installation, start the Ollama service:",
        S["body"]
    ))
    elems.append(CodeBlock("ollama serve"))
    elems.append(Paragraph(
        "💡 Tip: On Windows, Ollama runs automatically as a system tray app "
        "after installation.",
        S["tip"]
    ))
    elems.append(Spacer(1, 0.3*cm))

    # 3.3
    elems.append(Paragraph(
        "3.3 Step 3 — Install Python Dependencies", S["h2"]
    ))
    elems.append(Paragraph(
        "Open a terminal (or PyCharm terminal) and run:",
        S["body"]
    ))
    elems.append(CodeBlock(
        "pip install PyQt5 ollama reportlab pyinstaller"
    ))
    elems.append(Spacer(1, 0.3*cm))

    # 3.4
    elems.append(Paragraph(
        "3.4 Step 4 — Download an AI Model", S["h2"]
    ))
    elems.append(Paragraph(
        "Pull your preferred AI model. LLaMA 3 is recommended for best results:",
        S["body"]
    ))
    elems.append(CodeBlock(
        "ollama pull llama3\n"
        "\n"
        "# Other available models:\n"
        "ollama pull mistral\n"
        "ollama pull codellama\n"
        "ollama pull gemma2\n"
        "ollama pull phi3"
    ))
    elems.append(Paragraph(
        "⚠  The first download may take several minutes depending on "
        "your internet speed. Model sizes range from 2 GB to 7 GB.",
        S["warn"]
    ))
    elems.append(Spacer(1, 0.3*cm))

    # 3.5
    elems.append(Paragraph(
        "3.5 Step 5 — Run the Application", S["h2"]
    ))
    elems.append(Paragraph(
        "Navigate to your project folder and run:",
        S["body"]
    ))
    elems.append(CodeBlock(
        "cd AI_command_assistant\n"
        "python ai_linux_assistant.py"
    ))
    elems.append(Paragraph(
        "Or if you have the EXE build:",
        S["body"]
    ))
    elems.append(CodeBlock("dist\\AI_Linux_Assistant.exe"))
    elems.append(Paragraph(
        "💡 Tip: Make sure Ollama is running before starting "
        "the application, otherwise AI responses will fail.",
        S["tip"]
    ))
    elems.append(PageBreak())
    return elems


# ── SECTION 4: LAYOUT ─────────────────────────────────────────
def build_layout(S):
    elems = []
    elems.append(Paragraph("4. Application Layout", S["h1"]))
    elems.append(ColorBar(C_BLUE, height=2))
    elems.append(Spacer(1, 0.3*cm))
    elems.append(Paragraph(
        "The application is divided into four main areas:",
        S["body"]
    ))

    # layout diagram
    layout_data = [
        ["TOOLBAR",
         "Model selector · Font controls · Clear · Save · About"],
        ["LEFT PANEL",
         "AI Chat display · Input box · Action buttons"],
        ["RIGHT TOP",
         "Terminal output · Direct command input · Run/Clear"],
        ["RIGHT BOTTOM",
         "Favorites tab + History tab (tabbed interface)"],
        ["STATUS BAR",
         "Current status · Active model · Last action"],
    ]
    tbl = Table(layout_data, colWidths=[4*cm, 11.5*cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (0, -1), C_MID),
        ("BACKGROUND",   (1, 0), (1, -1), C_DARK),
        ("TEXTCOLOR",    (0, 0), (0, -1), C_YELLOW),
        ("TEXTCOLOR",    (1, 0), (1, -1), C_WHITE),
        ("FONTNAME",     (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME",     (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE",     (0, 0), (-1, -1), 10),
        ("TOPPADDING",   (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 8),
        ("LEFTPADDING",  (0, 0), (-1, -1), 10),
        ("GRID",         (0, 0), (-1, -1), 0.5, C_MID),
    ]))
    elems.append(tbl)
    elems.append(Spacer(1, 0.4*cm))

    # 4.1
    elems.append(Paragraph("4.1 Toolbar", S["h2"]))
    toolbar_data = [
        ["Element",           "Description"],
        ["App Title",         "Displays application name and version"],
        ["Model Selector",    "Dropdown to switch between Ollama AI models"],
        ["A− Button",         "Decrease font size by 1 point"],
        ["Font Size Label",   "Shows current font size in points"],
        ["A+ Button",         "Increase font size by 1 point"],
        ["↺ Reset Button",    "Reset font size to default (14pt)"],
        ["🗑 Clear Chat",      "Clear the AI conversation history"],
        ["💾 Save Chat",       "Export the chat log to a text file"],
        ["ℹ About",           "Show application version information"],
    ]
    elems.append(styled_table(
        toolbar_data, [5*cm, 10.5*cm]
    ))
    elems.append(Spacer(1, 0.4*cm))

    # 4.2
    elems.append(Paragraph("4.2 AI Chat Panel (Left)", S["h2"]))
    elems.append(Paragraph(
        "The left panel is the main conversation area where you interact "
        "with the AI assistant. Messages are displayed as colored chat "
        "bubbles — blue for your messages and green for AI responses. "
        "Code blocks are automatically highlighted and formatted.",
        S["body"]
    ))
    chat_data = [
        ["Element",           "Description"],
        ["Chat Display",      "Shows full conversation with formatted bubbles"],
        ["Thinking Indicator","Shows '⟳ AI is thinking...' during processing"],
        ["Input Box",         "Type your question or command here"],
        ["⮕ Send Button",     "Send your message to the AI"],
        ["▶ Run Last Command","Execute the last command suggested by AI"],
        ["⎘ Copy Command",    "Copy the last AI command to clipboard"],
        ["⭐ Save Command",    "Save last AI command to favorites"],
        ["✕ Clear Chat",      "Clear the conversation history"],
    ]
    elems.append(styled_table(
        chat_data, [5*cm, 10.5*cm]
    ))
    elems.append(Spacer(1, 0.4*cm))

    # 4.3
    elems.append(Paragraph("4.3 Terminal Output Panel (Right Top)", S["h2"]))
    elems.append(Paragraph(
        "The terminal panel displays real-time output from executed commands. "
        "Output is color-coded: green for normal output, red for errors, "
        "and blue for command headers.",
        S["body"]
    ))
    term_data = [
        ["Element",           "Description"],
        ["Output Display",    "Shows stdout and stderr from commands"],
        ["Command Input",     "Type Linux commands to run directly"],
        ["▶ Run Button",      "Execute the typed command"],
        ["✕ Clear Button",    "Clear the terminal output"],
        ["Exit Code",         "Shows return code and execution time after run"],
    ]
    elems.append(styled_table(
        term_data, [5*cm, 10.5*cm]
    ))

    # 4.4
    elems.append(Paragraph(
        "4.4 Favorites & History Tabs (Right Bottom)", S["h2"]
    ))
    elems.append(Paragraph(
        "The bottom-right section contains two tabs: Favorites and History. "
        "Switch between them by clicking the tab labels.",
        S["body"]
    ))
    elems.append(PageBreak())
    return elems


# ── SECTION 5: USING THE ASSISTANT ───────────────────────────
def build_usage(S):
    elems = []
    elems.append(Paragraph("5. Using the AI Assistant", S["h1"]))
    elems.append(ColorBar(C_BLUE, height=2))
    elems.append(Spacer(1, 0.3*cm))

    # 5.1
    elems.append(Paragraph("5.1 Asking Questions", S["h2"]))
    elems.append(Paragraph(
        "Simply type your question in the input box at the bottom of the "
        "chat panel and press Enter or click Send. The AI will respond "
        "with a detailed explanation and the exact command to use.",
        S["body"]
    ))
    elems.append(Paragraph(
        "Example questions you can ask:",
        S["body"]
    ))
    examples = [
        "How do I check disk usage on my system?",
        "Show me how to monitor CPU usage in real time",
        "How do I find all files larger than 100MB?",
        "What command shows all running processes?",
        "How do I check which ports are open?",
        "How do I restart the nginx service?",
        "Show me how to check network traffic",
        "How do I compress a folder into a tar.gz file?",
        "How do I check system memory usage?",
        "How do I view the last 50 lines of a log file?",
    ]
    for ex in examples:
        elems.append(Paragraph(
            f'<font color="#89b4fa">▷</font>  "{ex}"',
            S["bullet"]
        ))

    elems.append(Spacer(1, 0.3*cm))
    elems.append(Paragraph(
        "💡 Tip: The AI remembers your last 12 messages, "
        "so you can ask follow-up questions naturally.",
        S["tip"]
    ))

    # 5.2
    elems.append(Paragraph("5.2 Running Commands", S["h2"]))
    elems.append(Paragraph(
        "There are three ways to run commands in the application:",
        S["body"]
    ))
    run_data = [
        ["Method",                "How to Use"],
        ["▶ Run Last Command",    "Click this button to run the last command "
                                  "the AI suggested"],
        ["Direct Terminal Input", "Type any command in the terminal input box "
                                  "and press Enter or click Run"],
        ["From Favorites",        "Double-click any item in the Favorites tab "
                                  "to run it instantly"],
        ["From History",          "Double-click any item in the History tab "
                                  "to load it into the command input"],
    ]
    elems.append(styled_table(
        run_data, [4.5*cm, 11*cm]
    ))
    elems.append(Spacer(1, 0.3*cm))
    elems.append(Paragraph(
        "⚠  Safety Warning: The application automatically blocks "
        "known destructive commands such as 'rm -rf /', 'mkfs', "
        "and 'dd if=' to protect your system.",
        S["warn"]
    ))

    # 5.3
    elems.append(Paragraph("5.3 Switching AI Models", S["h2"]))
    elems.append(Paragraph(
        "Use the Model dropdown in the toolbar to switch between "
        "different Ollama models at any time during a session.",
        S["body"]
    ))
    models_data = [
        ["Model",       "Best For",              "Size"],
        ["llama3",      "General Linux help",     "~4.7 GB"],
        ["llama3.2",    "Faster responses",       "~2.0 GB"],
        ["mistral",     "Detailed explanations",  "~4.1 GB"],
        ["codellama",   "Command & script help",  "~3.8 GB"],
        ["gemma2",      "Concise answers",        "~5.0 GB"],
        ["phi3",        "Lightweight / fast",     "~2.3 GB"],
    ]
    elems.append(styled_table(
        models_data,
        [4*cm, 6*cm, 4*cm]
    ))
    elems.append(Paragraph(
        "💡 Tip: Use 'codellama' for script writing and "
        "'llama3' for general system administration questions.",
        S["tip"]
    ))
    elems.append(PageBreak())
    return elems


# ── SECTION 6: FAVORITES ──────────────────────────────────────
def build_favorites(S):
    elems = []
    elems.append(Paragraph("6. Favorites Database", S["h1"]))
    elems.append(ColorBar(C_BLUE, height=2))
    elems.append(Spacer(1, 0.3*cm))
    elems.append(Paragraph(
        "The Favorites system lets you build a personal database of "
        "your most-used Linux commands, organized by category, with "
        "custom names and descriptions. Data is stored in a local "
        "SQLite database file (favorites.db).",
        S["body"]
    ))

    # 6.1
    elems.append(Paragraph("6.1 Adding Favorites", S["h2"]))
    add_steps = [
        "Click the '⭐ Add New' button in the Favorites tab",
        "Fill in the Name field (required)",
        "Enter the Command (required)",
        "Select a Category from the dropdown",
        "Add an optional Description",
        "Click Save",
    ]
    for i, step in enumerate(add_steps, 1):
        elems.append(Paragraph(
            f'<font color="#f9e2af">{i}.</font>  {step}',
            S["bullet"]
        ))
    elems.append(Paragraph(
        "💡 Tip: You can also click '⭐ Save Command' in the chat panel "
        "to save the last AI-suggested command directly to favorites.",
        S["tip"]
    ))
    elems.append(Spacer(1, 0.3*cm))

    # categories
    elems.append(Paragraph("Available Categories:", S["h3"]))
    cat_data = [
        ["General",  "Network",  "Files",    "Process"],
        ["System",   "Disk",     "Testing",  "Security"],
        ["Docker",   "Custom",   "",         ""],
    ]
    cat_tbl = Table(cat_data, colWidths=[3.8*cm]*4)
    cat_tbl.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), C_MID),
        ("TEXTCOLOR",    (0, 0), (-1, -1), C_TEAL),
        ("FONTNAME",     (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, -1), 10),
        ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING",   (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 7),
        ("GRID",         (0, 0), (-1, -1), 0.5, C_DARK),
    ]))
    elems.append(cat_tbl)

    # 6.2
    elems.append(Paragraph("6.2 Searching and Filtering", S["h2"]))
    elems.append(Paragraph(
        "The Favorites tab includes a live search bar that instantly "
        "filters your favorites as you type. You can also filter by "
        "category using the dropdown next to the search bar.",
        S["body"]
    ))
    search_data = [
        ["Feature",          "How It Works"],
        ["Live Search",      "Type in the search box — results update instantly"],
        ["Search Fields",    "Searches name, command, description, and category"],
        ["Category Filter",  "Select a category to show only those commands"],
        ["Clear Filter",     "Select 'All Categories' to show everything"],
    ]
    elems.append(styled_table(
        search_data, [4.5*cm, 11*cm]
    ))

    # 6.3
    elems.append(Paragraph("6.3 Editing and Deleting", S["h2"]))
    elems.append(Paragraph(
        "Select any favorite in the list and use the action buttons:",
        S["body"]
    ))
    ed_data = [
        ["Button",       "Action"],
        ["✏ Edit",       "Opens the edit dialog with current values pre-filled"],
        ["🗑 Delete",     "Shows confirmation dialog before deleting"],
        ["▶ Run",        "Runs the selected favorite command immediately"],
        ["Double-click", "Also runs the command immediately"],
    ]
    elems.append(styled_table(
        ed_data, [4.5*cm, 11*cm]
    ))

    # 6.4
    elems.append(Paragraph("6.4 Import and Export", S["h2"]))
    elems.append(Paragraph(
        "You can back up and share your favorites using JSON files:",
        S["body"]
    ))
    elems.append(CodeBlock(
        "# Export format (favorites_export.json):\n"
        "[\n"
        "  {\n"
        '    "name": "Check Disk Usage",\n'
        '    "command": "df -h",\n'
        '    "category": "Disk",\n'
        '    "description": "Shows disk usage in human-readable format",\n'
        '    "created_at": "2025-01-01 12:00:00"\n'
        "  }\n"
        "]"
    ))
    elems.append(PageBreak())
    return elems


# ── SECTION 7-8: HISTORY & FONT ──────────────────────────────
def build_history_font(S):
    elems = []

    # Section 7
    elems.append(Paragraph("7. Command History", S["h1"]))
    elems.append(ColorBar(C_BLUE, height=2))
    elems.append(Spacer(1, 0.3*cm))
    elems.append(Paragraph(
        "Every command you run is automatically saved to the History tab "
        "and stored in the command_history.json file. The history persists "
        "between sessions.",
        S["body"]
    ))
    hist_data = [
        ["Feature",              "Description"],
        ["Auto-save",            "Commands are saved automatically on execution"],
        ["Persistent",           "History survives app restarts"],
        ["Double-click to load", "Loads command into the terminal input box"],
        ["▶ Use Button",         "Loads selected command into terminal input"],
        ["⭐ Save to Favorites", "Promotes a history item to your favorites"],
        ["✕ Clear History",      "Removes all history entries"],
        ["Max entries",          "100 most recent commands are kept"],
    ]
    elems.append(styled_table(
        hist_data, [5*cm, 10.5*cm]
    ))
    elems.append(Spacer(1, 0.5*cm))

    # Section 8
    elems.append(Paragraph("8. Font Size and Display", S["h1"]))
    elems.append(ColorBar(C_BLUE, height=2))
    elems.append(Spacer(1, 0.3*cm))
    elems.append(Paragraph(
        "The font size is fully adjustable and affects all panels "
        "simultaneously — the chat panel, terminal, input boxes, "
        "and history list. Your preferred size is saved to settings.json "
        "and restored automatically on next launch.",
        S["body"]
    ))
    font_data = [
        ["Control",          "Action"],
        ["A+ Button",        "Increase font size by 1 point"],
        ["A− Button",        "Decrease font size by 1 point"],
        ["↺ Reset",          "Reset to default size (14 pt)"],
        ["Ctrl + =  or  +",  "Increase font size (keyboard shortcut)"],
        ["Ctrl + −",         "Decrease font size (keyboard shortcut)"],
        ["Ctrl + 0",         "Reset to default size (keyboard shortcut)"],
        ["Range",            "10 pt minimum — 26 pt maximum"],
        ["Auto-save",        "Font size saved to settings.json on change"],
    ]
    elems.append(styled_table(
        font_data, [5*cm, 10.5*cm]
    ))
    elems.append(PageBreak())
    return elems


# ── SECTION 9: SHORTCUTS ─────────────────────────────────────
def build_shortcuts(S):
    elems = []
    elems.append(Paragraph("9. Keyboard Shortcuts", S["h1"]))
    elems.append(ColorBar(C_BLUE, height=2))
    elems.append(Spacer(1, 0.3*cm))

    shortcuts_data = [
        ["Shortcut",          "Action"],
        ["Enter",             "Send message / Run command"],
        ["Ctrl + =",          "Increase font size"],
        ["Ctrl + −",          "Decrease font size"],
        ["Ctrl + 0",          "Reset font size to default"],
        ["F11",               "Toggle fullscreen mode"],
        ["Ctrl + C",          "Copy selected text"],
        ["Ctrl + A",          "Select all text in input"],
    ]
    elems.append(styled_table(
        shortcuts_data, [5*cm, 10.5*cm]
    ))
    elems.append(PageBreak())
    return elems


# ── SECTION 10: MODELS ───────────────────────────────────────
def build_models(S):
    elems = []
    elems.append(Paragraph("10. Supported AI Models", S["h1"]))
    elems.append(ColorBar(C_BLUE, height=2))
    elems.append(Spacer(1, 0.3*cm))
    elems.append(Paragraph(
        "The assistant supports all models available through Ollama. "
        "Below are the recommended models for this application:",
        S["body"]
    ))
    models_data = [
        ["Model",        "Speed",    "Quality",  "Size",   "Best Use Case"],
        ["llama3",       "Medium",   "Excellent","4.7 GB", "General Linux help"],
        ["llama3.2",     "Fast",     "Very Good","2.0 GB", "Quick answers"],
        ["mistral",      "Medium",   "Excellent","4.1 GB", "Detailed guides"],
        ["codellama",    "Medium",   "Excellent","3.8 GB", "Scripts & code"],
        ["gemma2",       "Medium",   "Very Good","5.0 GB", "Concise answers"],
        ["phi3",         "Very Fast","Good",     "2.3 GB", "Lightweight use"],
    ]
    elems.append(styled_table(
        models_data,
        [3*cm, 2.5*cm, 2.5*cm, 2.5*cm, 5*cm]
    ))
    elems.append(Spacer(1, 0.4*cm))
    elems.append(Paragraph(
        "To add a new model, run in your terminal:",
        S["body"]
    ))
    elems.append(CodeBlock(
        "ollama pull <model_name>\n"
        "# Example:\n"
        "ollama pull codellama"
    ))
    elems.append(Paragraph(
        "💡 Tip: Browse all available models at https://ollama.com/library",
        S["tip"]
    ))
    elems.append(PageBreak())
    return elems


# ── SECTION 11: TROUBLESHOOTING ──────────────────────────────
def build_troubleshooting(S):
    elems = []
    elems.append(Paragraph("11. Troubleshooting", S["h1"]))
    elems.append(ColorBar(C_BLUE, height=2))
    elems.append(Spacer(1, 0.3*cm))

    issues = [
        {
            "problem": "AI returns error: 'Ollama not running'",
            "cause":   "Ollama service is not started",
            "fix":     "ollama serve",
        },
        {
            "problem": "Model not found error",
            "cause":   "Model was not downloaded",
            "fix":     "ollama pull llama3",
        },
        {
            "problem": "App window is blank or crashes",
            "cause":   "PyQt5 not installed or wrong version",
            "fix":     "pip install --upgrade PyQt5",
        },
        {
            "problem": "Font is very small",
            "cause":   "Default font size too small for your display",
            "fix":     "Use A+ button or Ctrl + = to increase font size",
        },
        {
            "problem": "Command output shows permission denied",
            "cause":   "Command requires elevated privileges",
            "fix":     "Prefix with sudo (e.g. sudo df -h)",
        },
        {
            "problem": "Favorites not saving",
            "cause":   "favorites.db file permissions issue",
            "fix":     "Run app from a folder you have write access to",
        },
        {
            "problem": "EXE build crashes on launch",
            "cause":   "Missing data files not bundled",
            "fix":     "Use --add-data flag in PyInstaller command",
        },
        {
            "problem": "AI responses are slow",
            "cause":   "Model is large or no GPU available",
            "fix":     "Switch to phi3 or llama3.2 for faster responses",
        },
    ]

    for item in issues:
        elems.append(KeepTogether([
            Paragraph(
                f'<font color="#f38ba8">⚠  {item["problem"]}</font>',
                S["h3"]
            ),
            Paragraph(
                f'<font color="#6c7086">Cause:</font>  {item["cause"]}',
                S["body"]
            ),
            Paragraph(
                f'<font color="#a6e3a1">Fix:</font>',
                S["body"]
            ),
            CodeBlock(item["fix"]),
            Spacer(1, 0.3*cm),
        ]))

    elems.append(PageBreak())
    return elems


# ── SECTION 12: FAQ ──────────────────────────────────────────
def build_faq(S):
    elems = []
    elems.append(Paragraph("12. Frequently Asked Questions", S["h1"]))
    elems.append(ColorBar(C_BLUE, height=2))
    elems.append(Spacer(1, 0.3*cm))

    faqs = [
        {
            "q": "Does this app send my data to the internet?",
            "a": "No. All AI processing is done locally using Ollama. "
                 "Your commands and conversations never leave your machine."
        },
        {
            "q": "Can I use this app on Windows?",
            "a": "Yes. The app runs on Windows 10+, Linux, and macOS. "
                 "On Windows, commands are executed via the Windows shell "
                 "(cmd.exe / PowerShell)."
        },
        {
            "q": "How do I update the AI model?",
            "a": "Run 'ollama pull <model_name>' in your terminal to get "
                 "the latest version of any model."
        },
        {
            "q": "Can I add my own custom categories to favorites?",
            "a": "Yes. The 'Custom' category is available for this purpose. "
                 "Additional categories can be added by editing the "
                 "CATEGORIES list in the source code."
        },
        {
            "q": "How many favorites can I save?",
            "a": "There is no limit. The SQLite database can store "
                 "thousands of favorites with no performance impact."
        },
        {
            "q": "Can I share my favorites with a teammate?",
            "a": "Yes. Use the Export JSON button to save your favorites "
                 "to a file, then share that file. Your teammate can "
                 "import it using the Import JSON button."
        },
        {
            "q": "What happens if I type a wrong command?",
            "a": "The terminal will show the error output in red. "
                 "No changes are made to your system until a command "
                 "actually runs successfully."
        },
        {
            "q": "Can I run multiple commands at once?",
            "a": "Yes. Use shell operators like && or ; to chain commands. "
                 "Example: cd /var/log && ls -la"
        },
    ]

    for item in faqs:
        elems.append(KeepTogether([
            Paragraph(
                f'<font color="#89b4fa">Q:  {item["q"]}</font>',
                S["h3"]
            ),
            Paragraph(
                f'<font color="#cdd6f4">A:  {item["a"]}</font>',
                S["body"]
            ),
            Spacer(1, 0.3*cm),
        ]))

    elems.append(PageBreak())
    return elems


# ── SECTION 13: SAFETY ───────────────────────────────────────
def build_safety(S):
    elems = []
    elems.append(Paragraph("13. Safety and Security", S["h1"]))
    elems.append(ColorBar(C_RED, height=2))
    elems.append(Spacer(1, 0.3*cm))

    elems.append(Paragraph(
        "The application includes built-in safety features to "
        "prevent accidental execution of dangerous commands. "
        "However, users must exercise caution when running "
        "any system command.",
        S["body"]
    ))

    elems.append(Paragraph("Built-in Blocked Commands:", S["h2"]))
    blocked_data = [
        ["Blocked Pattern",  "Reason"],
        ["rm -rf /",         "Deletes entire root filesystem"],
        ["mkfs",             "Formats a disk partition"],
        ["> /dev/sda",       "Overwrites raw disk device"],
        ["dd if=",           "Raw disk copy — can destroy data"],
    ]
    elems.append(styled_table(
        blocked_data, [6*cm, 9.5*cm],
        header_bg=C_RED
    ))
    elems.append(Spacer(1, 0.3*cm))

    elems.append(Paragraph("Best Practices:", S["h2"]))
    practices = [
        "Always read and understand a command before running it",
        "Do not run commands with sudo unless you understand the effect",
        "Test destructive commands on non-production systems first",
        "Back up important data before running disk or file operations",
        "Use the AI to explain what a command does before executing it",
        "Do not share your favorites.db if it contains sensitive info",
    ]
    for p in practices:
        elems.append(Paragraph(
            f'<font color="#f38ba8">⚠</font>  {p}',
            S["bullet"]
        ))

    elems.append(Spacer(1, 0.5*cm))
    elems.append(ColorBar(C_MID, height=2))
    elems.append(Spacer(1, 0.3*cm))
    elems.append(Paragraph(
        "End of Documentation",
        ParagraphStyle(
            "end",
            fontSize=10,
            fontName="Helvetica-Oblique",
            textColor=C_GRAY,
            alignment=TA_CENTER
        )
    ))
    elems.append(Paragraph(
        f"AI Linux Command Assistant v1.0.0  —  "
        f"Generated {datetime.datetime.now().strftime('%B %d, %Y')}",
        ParagraphStyle(
            "end2",
            fontSize=9,
            fontName="Helvetica",
            textColor=C_GRAY,
            alignment=TA_CENTER
        )
    ))
    return elems


###############################################################
# MAIN BUILD FUNCTION
###############################################################
def build_pdf():
    print(f"Building: {OUTPUT_FILE} ...")

    doc = DocTemplate(
        OUTPUT_FILE,
        pagesize=A4,
        leftMargin=1.5*cm,
        rightMargin=1.5*cm,
        topMargin=1.8*cm,
        bottomMargin=1.8*cm,
    )

    S = build_styles()

    story = []

    # Cover (no header/footer)
    story += build_cover(S)

    # All other sections (with header/footer)
    story += build_toc(S)
    story += build_intro(S)
    story += build_requirements(S)
    story += build_installation(S)
    story += build_layout(S)
    story += build_usage(S)
    story += build_favorites(S)
    story += build_history_font(S)
    story += build_shortcuts(S)
    story += build_models(S)
    story += build_troubleshooting(S)
    story += build_faq(S)
    story += build_safety(S)

    doc.build(
        story,
        onFirstPage=header_footer_skip_cover,
        onLaterPages=header_footer
    )

    print(f"✔ Documentation generated: {OUTPUT_FILE}")
    print(f"  Pages: ~15+")
    print(f"  Location: {OUTPUT_FILE}")


if __name__ == "__main__":
    build_pdf()
