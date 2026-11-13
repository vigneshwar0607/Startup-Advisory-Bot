"""Builds the daily PDF: page 1 = 90-day course index (today marked), then the lesson. Plain black-and-white."""
import os
from pathlib import Path

import markdown
from fpdf import FPDF
from fpdf.fonts import FontFace, TextStyle

from .syllabus import COURSE_DAYS, index_rows

FONT_DIRS = ["/usr/share/fonts/truetype/dejavu", "/usr/share/fonts/dejavu", str(Path(__file__).parent / "fonts")]
BLACK = (0, 0, 0)


def _font_path(name: str) -> str:
    for d in FONT_DIRS:
        p = os.path.join(d, name)
        if os.path.exists(p):
            return p
    raise FileNotFoundError(f"{name} not found; install fonts-dejavu-core")


class LessonPDF(FPDF):
    def footer(self):
        self.set_y(-12)
        self.set_font("DejaVu", size=8)
        self.cell(0, 8, f"Page {self.page_no()}", align="C")


def _fit(pdf: FPDF, text: str, width: float) -> str:
    if pdf.get_string_width(text) <= width:
        return text
    while text and pdf.get_string_width(text + "…") > width:
        text = text[:-1]
    return text.rstrip() + "…"


def _index_page(pdf: FPDF, current_day: int) -> None:
    pdf.add_page()
    pdf.set_font("DejaVu", "B", 14)
    pdf.cell(0, 7, "Startup Advisory — 90-Day Course Index", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("DejaVu", size=8.5)
    status = (f"Today: Day {current_day} of {COURSE_DAYS} (marked ▶)" if current_day <= COURSE_DAYS
              else f"Course complete — today is bonus Day {current_day} (case studies & revision)")
    pdf.cell(0, 5, status + "   ·   [e₹] = full Digital Rupee lesson; every lesson also ends with a short "
             "Digital Rupee box", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    rows = index_rows()
    # split into two columns at the module boundary nearest the middle
    module_starts = [i for i, r in enumerate(rows) if r[0] == "module"]
    split = min(module_starts, key=lambda i: abs(i - len(rows) / 2))
    columns = [rows[:split], rows[split:]]

    top = pdf.get_y()
    gutter = 6
    col_w = (pdf.w - pdf.l_margin - pdf.r_margin - gutter) / 2
    line_h = min(4.4, (pdf.h - 18 - top) / max(len(c) for c in columns))
    for ci, col in enumerate(columns):
        x = pdf.l_margin + ci * (col_w + gutter)
        y = top
        for kind, day, title in col:
            pdf.set_xy(x, y)
            if kind == "module":
                pdf.set_font("DejaVu", "B", 8)
                y += 1.2 if y > top else 0
                pdf.set_xy(x, y)
                pdf.cell(col_w, line_h, _fit(pdf, title, col_w))
                pdf.line(x, y + line_h, x + col_w, y + line_h)
                y += 0.6
            else:
                is_today = day == current_day
                pdf.set_font("DejaVu", "B" if is_today else "", 7.6)
                label = f"{'▶' if is_today else ' '} {day:>2}  "
                pdf.cell(9, line_h, label)
                pdf.cell(col_w - 9, line_h, _fit(pdf, title, col_w - 9))
            y += line_h


def markdown_to_pdf(title: str, md_text: str, out_path: str, current_day: int | None = None,
                    index_only: bool = False) -> str:
    html = markdown.markdown(md_text, extensions=["tables", "sane_lists"])
    pdf = LessonPDF(format="A4")
    pdf.set_margins(16, 14, 16)
    pdf.set_auto_page_break(True, margin=16)
    pdf.add_font("DejaVu", "", _font_path("DejaVuSans.ttf"))
    pdf.add_font("DejaVu", "B", _font_path("DejaVuSans-Bold.ttf"))
    pdf.add_font("DejaVu", "I", _font_path("DejaVuSans-Oblique.ttf"))
    pdf.add_font("DejaVu", "BI", _font_path("DejaVuSans-BoldOblique.ttf"))

    if current_day is not None:
        _index_page(pdf, current_day)
    if index_only:
        pdf.output(out_path)
        return out_path

    pdf.add_page()
    pdf.set_font("DejaVu", "B", 15)
    pdf.multi_cell(0, 8, title)
    pdf.ln(3)
    pdf.set_font("DejaVu", size=10)
    styles = {
        "h1": TextStyle(font_family="DejaVu", font_style="B", font_size_pt=14, color=BLACK, t_margin=5, b_margin=2),
        "h2": TextStyle(font_family="DejaVu", font_style="B", font_size_pt=12, color=BLACK, t_margin=5, b_margin=2),
        "h3": TextStyle(font_family="DejaVu", font_style="B", font_size_pt=11, color=BLACK, t_margin=4, b_margin=1),
        "a": FontFace(color=BLACK, emphasis="UNDERLINE"),
    }
    pdf.write_html(html, font_family="DejaVu", tag_styles=styles,
                   li_prefix_color=BLACK, table_line_separators=True)
    pdf.output(out_path)
    return out_path
