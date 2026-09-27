from io import BytesIO
from fastapi.testclient import TestClient
from PIL import Image
from app.main import app
from app.schemas import ComicOutline, ComicPanel, ComicStory, OutlinePanel

def test_mocked_comic_pipeline_creates_preview_and_pdf(tmp_path, monkeypatch):
    import app.routes as routes


    class FakeTextProvider:
        def generate_outline(self, request):
            return ComicOutline(title="A Test Adventure", panels=[OutlinePanel(panel_number=i, title=f"Scene {i}", scene_description="A bright illustrated scene", beat="The hero takes a step") for i in range(1, request.panel_count + 1)])
        def generate_story(self, request, outline):
            return ComicStory(title=outline.title, panels=[ComicPanel(panel_number=p.panel_number, title=p.title, scene_description=p.scene_description, narration="A new story begins.", dialogue="Let's go!", caption="Onward.", image_prompt="A colorful comic illustration") for p in outline.panels])

    class FakeImageProvider:
        def generate(self, prompt):
            image = Image.new("RGB", (320, 200), (50, 65, 110))
            output = BytesIO()
            image.save(output, format="PNG")
            return output.getvalue()

    monkeypatch.setattr(routes, "get_provider", lambda provider, model: FakeTextProvider())
    monkeypatch.setattr(routes, "get_image_provider", lambda: FakeImageProvider())
    payload = {"prompt": "A fox explores a glowing forest", "character_name": "Finn", "setting": "Forest", "tone": "curious", "art_style": "comic book", "provider": "gemini", "model": "gemini-3.8-flash", "panel_count": 3}
    client = TestClient(app)
    result = client.post("/api/generate-comic/json", json=payload)
    assert result.status_code == 200
    body = result.json()
    assert len(body["comic"]["panels"]) == 3
    assert client.get(f"/comic/{body['comic_id']}").status_code == 200
    pdf = client.get(body["pdf_url"])
    assert pdf.status_code == 200 and pdf.content.startswith(b"%PDF")
    image = client.get(body["comic"]["panels"][0]["image_url"])
    assert image.status_code == 200 and image.headers["content-type"] == "image/png"
    from app.services.files import storage_paths
    panels_dir, exports_dir, comics_dir = storage_paths()
    for path in [comics_dir / f"{body['comic_id']}.json", exports_dir / f"comiccraft_{body['comic_id']}.pdf", *[panels_dir / f"{body['comic_id']}_{index:02d}.png" for index in range(1, 4)]]:
        path.unlink(missing_ok=True)
