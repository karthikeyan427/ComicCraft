import os
import re
import time
import uuid
import logging
from pathlib import Path
from typing import List, Dict, Any
from fpdf import FPDF

logger = logging.getLogger(__name__)

STATIC_EXPORTS_DIR = Path("static/exports")
STATIC_EXPORTS_DIR.mkdir(parents=True, exist_ok=True)


class ComicPDF(FPDF):
    def __init__(self, comic_title: str):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.comic_title = comic_title
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        if self.page_no() > 1:
            self.set_font("Helvetica", "B", 9)
            self.set_text_color(120, 120, 140)
            self.cell(0, 8, f"COMICCRAFT  |  {self.comic_title[:60].upper()}", align="L")
            self.ln(6)
            self.set_draw_color(220, 220, 230)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(4)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(140, 140, 150)
        self.cell(0, 8, f"Generated with ComicCraft (Gemini AI & Stable Diffusion)  |  Page {self.page_no()}", align="C")


def clean_text_for_pdf(text: str) -> str:
    """Replaces or encodes Unicode characters that standard standard fonts cannot encode."""
    if not text:
        return ""
    replacements = {
        "—": "-",
        "–": "-",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "…": "...",
        "•": "*",
        "™": "TM",
        "©": "(c)",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    # Ensure all characters are strictly within ASCII printable range to prevent FPDF font encoding errors
    clean = "".join(c for c in text if 32 <= ord(c) <= 126 or c in "\n\t")
    return clean


def save_pdf(
    layout: List[Dict[str, Any]],
    comic_title: str = "ComicCraft Story",
    character_name: str = "Hero",
    setting: str = "Comic World",
    tone: str = "Dramatic",
    art_style: str = "Comic Book",
    output_dir: str = "static/exports"
) -> str:
    """
    Compiles the full comic into a multi-page PDF using FPDF.
    Each panel's image, title, scene description, caption, and dialogue are formatted
    neatly with professional comic styling.
    
    Returns the relative web path: '/static/exports/comic_...pdf'
    """
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    timestamp = int(time.time())
    safe_slug = re.sub(r'[^a-zA-Z0-9_\-]', '', comic_title.replace(" ", "_").lower())[:20] or "comic"
    filename = f"comic_{safe_slug}_{timestamp}_{uuid.uuid4().hex[:6]}.pdf"
    pdf_path = target_dir / filename

    pdf = ComicPDF(comic_title=comic_title)

    # -----------------------------
    # PAGE 1: TITLE & COVER
    # -----------------------------
    pdf.add_page()
    
    # Comic Banner Background Header
    pdf.set_fill_color(24, 26, 42)
    pdf.rect(10, 15, 190, 48, style="F")
    pdf.set_draw_color(255, 180, 0)
    pdf.set_line_width(1.2)
    pdf.rect(10, 15, 190, 48, style="D")

    # Title
    pdf.set_xy(15, 22)
    pdf.set_font("Helvetica", "B", 24)
    pdf.set_text_color(255, 195, 0)
    pdf.cell(180, 10, clean_text_for_pdf("COMICCRAFT CHRONICLES"), ln=True, align="C")

    # Subtitle / Story title
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(255, 255, 255)
    clean_title = clean_text_for_pdf(comic_title[:80])
    pdf.cell(180, 8, f'"{clean_title}"', ln=True, align="C")

    pdf.ln(18)

    # Metadata Box
    pdf.set_fill_color(245, 246, 250)
    pdf.set_draw_color(200, 205, 220)
    pdf.set_line_width(0.4)
    pdf.rect(10, 68, 190, 28, style="FD")

    pdf.set_xy(15, 72)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(40, 40, 60)
    pdf.cell(45, 6, clean_text_for_pdf(f"PROTAGONIST: {character_name}"), ln=False)
    pdf.cell(50, 6, clean_text_for_pdf(f"SETTING: {setting}"), ln=False)
    pdf.cell(45, 6, clean_text_for_pdf(f"TONE: {tone}"), ln=False)
    pdf.cell(45, 6, clean_text_for_pdf(f"STYLE: {art_style}"), ln=True)

    pdf.set_xy(15, 80)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(100, 100, 120)
    pdf.cell(180, 6, clean_text_for_pdf(f"Story outline powered by Gemini Flash & Pro | Illustrations by Stable Diffusion | 5 Panels"), ln=True)

    pdf.ln(16)

    # -----------------------------
    # COMIC PANELS (Each on its own page or dedicated slots)
    # -----------------------------
    for panel in layout:
        # If not the first panel, create a fresh page for maximum visual impact
        if panel["panel_number"] > 1 or pdf.get_y() > 100:
            pdf.add_page()

        panel_num = panel.get("panel_number", 1)
        panel_title = clean_text_for_pdf(panel.get("title", f"Panel {panel_num}"))
        scene_desc = clean_text_for_pdf(panel.get("scene_description", ""))
        caption = clean_text_for_pdf(panel.get("caption", ""))
        narration = clean_text_for_pdf(panel.get("narration", ""))
        dialogue = clean_text_for_pdf(panel.get("dialogue", ""))
        image_prompt = clean_text_for_pdf(panel.get("image_prompt", ""))
        img_rel_path = panel.get("image_path", "")

        # Panel Title Header with Comic Badge
        pdf.set_fill_color(255, 180, 0)
        pdf.set_draw_color(0, 0, 0)
        pdf.set_line_width(0.6)
        pdf.rect(10, pdf.get_y(), 190, 9, style="FD")
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(10, 15, 30)
        pdf.cell(190, 9, f"  {panel_title.upper()}", ln=True, align="L")
        pdf.ln(3)

        # Panel Illustration Image
        img_full_path = None
        if img_rel_path.startswith("/static/"):
            img_full_path = Path(img_rel_path[1:])
        elif img_rel_path.startswith("static/"):
            img_full_path = Path(img_rel_path)

        img_rendered_height = 92
        if img_full_path and img_full_path.exists():
            try:
                # Center image on page
                y_pos = pdf.get_y()
                pdf.image(str(img_full_path), x=15, y=y_pos, w=180, h=img_rendered_height)
                pdf.set_y(y_pos + img_rendered_height + 4)
            except Exception as e:
                logger.error(f"Error rendering image in PDF: {e}")
                pdf.set_font("Helvetica", "I", 10)
                pdf.cell(180, 15, "[Image file could not be embedded]", ln=True, align="C")
        else:
            pdf.set_fill_color(230, 230, 240)
            pdf.rect(15, pdf.get_y(), 180, 40, style="F")
            pdf.set_xy(15, pdf.get_y() + 15)
            pdf.set_font("Helvetica", "I", 10)
            pdf.cell(180, 8, "[Panel Illustration]", ln=True, align="C")
            pdf.ln(15)

        # Scene description (in italics, as specified)
        pdf.set_font("Helvetica", "I", 10)
        pdf.set_text_color(80, 80, 90)
        pdf.multi_cell(180, 5, scene_desc)
        pdf.ln(3)

        # Caption Box (Classic comic narrative box)
        if caption:
            pdf.set_fill_color(255, 248, 220)  # Pale comic yellow
            pdf.set_draw_color(210, 160, 50)
            pdf.set_line_width(0.4)
            curr_y = pdf.get_y()
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(60, 45, 10)
            pdf.multi_cell(180, 5.5, f"CAPTION: {caption}", border=1, fill=True)
            pdf.ln(2)

        # Narration & Dialogue Box
        if narration or dialogue:
            pdf.set_fill_color(248, 250, 255)
            pdf.set_draw_color(180, 190, 215)
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(25, 30, 45)
            
            story_block = ""
            if narration:
                story_block += f"Narration: {narration}\n"
            if dialogue:
                story_block += f"Dialogue: {dialogue}"
                
            pdf.multi_cell(180, 5.5, story_block.strip(), border=1, fill=True)
            pdf.ln(2)

        # Image Prompt Reference (Small footnote)
        if image_prompt:
            pdf.set_font("Helvetica", "I", 7.5)
            pdf.set_text_color(140, 140, 150)
            pdf.multi_cell(180, 4, f"Art Prompt Ref: {image_prompt[:140]}...")

    pdf.output(str(pdf_path))
    logger.info(f"Successfully compiled PDF to {pdf_path}")
    return f"/static/exports/{filename}"
