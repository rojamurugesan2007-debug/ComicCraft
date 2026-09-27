from PIL import Image
from app.schemas import ComicPanel, ComicStory
from app.services.exporters import export_pdf

def test_pdf_export_has_document_and_panel_art(tmp_path):
    story = ComicStory(title="The Night Map", panels=[ComicPanel(panel_number=1, title="A bright beginning", scene_description="A cartographer opens a glowing map.", narration="Beyond the hills...", dialogue="Let's go!", caption="The journey starts.", image_prompt="A warm comic scene")])
    image_path = tmp_path / "panel.png"
    Image.new("RGB", (320, 200), color=(40, 50, 90)).save(image_path)
    pdf_path = tmp_path / "comic.pdf"
    export_pdf(story, {1: image_path}, pdf_path)
    assert pdf_path.is_file()
    assert pdf_path.read_bytes().startswith(b"%PDF")
    assert pdf_path.stat().st_size > 1000
