import pytest
from pydantic import ValidationError
from app.schemas import ComicRequest

def test_valid_comic_request():
    request = ComicRequest(prompt="A fox explores a forest", character_name="Finn", setting="Forest", tone="curious", art_style="comic book", panel_count=5)
    assert request.provider == "gemini"
    assert request.panel_count == 5

def test_rejects_invalid_panel_count():
    with pytest.raises(ValidationError):
        ComicRequest(prompt="A fox explores a forest", character_name="Finn", setting="Forest", tone="curious", art_style="comic book", panel_count=4)
