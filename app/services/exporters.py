"""Build a printable PDF using FPDF2."""
from pathlib import Path
from fpdf import FPDF
from app.schemas import ComicStory


def pdf_text(value: str) -> str:
    """Keep arbitrary AI Unicode output safe for built-in PDF fonts."""
    return value.encode("latin-1", "replace").decode("latin-1")


class ComicPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(120, 110, 190)
        self.cell(0, 8, "COMICCRAFT  /  AI COMIC STORY", align="R", new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(25, 28, 45)


def export_pdf(story: ComicStory, image_paths: dict[int, Path], destination: Path) -> None:
    pdf = ComicPDF(format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_title(pdf_text(story.title))
    for panel in story.panels:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 22)
        pdf.multi_cell(0, 12, pdf_text(story.title), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "B", 15)
        pdf.multi_cell(0, 9, pdf_text(f"Panel {panel.panel_number}: {panel.title}"), new_x="LMARGIN", new_y="NEXT")
        image_path = image_paths.get(panel.panel_number)
        if image_path and image_path.is_file():
            image_y = pdf.get_y() + 2
            pdf.image(str(image_path), x=15, y=image_y, w=180, h=100, keep_aspect_ratio=True)
            pdf.set_y(image_y + 104)
        for label, value in (("Scene", panel.scene_description), ("Caption", panel.caption), ("Narration", panel.narration), ("Dialogue", panel.dialogue)):
            if value:
                pdf.set_font("Helvetica", "B", 10)
                pdf.multi_cell(0, 6, label, new_x="LMARGIN", new_y="NEXT")
                pdf.set_font("Helvetica", "", 11)
                pdf.multi_cell(0, 6, pdf_text(value), new_x="LMARGIN", new_y="NEXT")
                pdf.ln(2)
    pdf.output(str(destination))




