from fastapi.testclient import TestClient
from app.main import app

def test_frontend_and_api_routes():
    client = TestClient(app)
    assert client.get("/").status_code == 200
    assert client.get("/docs").status_code == 200
    providers = client.get("/api/providers")
    assert providers.status_code == 200
    assert {p["id"] for p in providers.json()} == {"gemini", "groq"}
    assert client.get("/api/models?provider=gemini").status_code == 200
    groq_models = client.get("/api/models?provider=groq").json()
    assert groq_models["models"] and groq_models["default"] in groq_models["models"]
    assert client.get("/api/models?provider=nope").status_code == 400

def test_missing_ai_key_is_friendly(monkeypatch):
    from app.config import get_settings
    settings = get_settings().model_copy(update={"gemini_api_key": ""})
    monkeypatch.setattr("app.ai.factory.get_settings", lambda: settings)
    monkeypatch.setattr("app.ai.gemini_provider.get_settings", lambda: settings)
    payload = {"prompt": "A fox explores a glowing forest", "character_name": "Finn", "setting": "Forest", "tone": "curious", "art_style": "comic book", "provider": "gemini", "model": settings.default_gemini_model, "panel_count": 3}
    response = TestClient(app).post("/api/generate-comic/json", json=payload)
    assert response.status_code == 503
    assert "GEMINI_API_KEY" in response.json()["detail"]

def test_missing_image_key_is_friendly(monkeypatch):
    from app.config import get_settings
    settings = get_settings().model_copy(update={"image_api_key": "", "hf_api_key": ""})
    monkeypatch.setattr("app.image.provider.get_settings", lambda: settings)
    response = TestClient(app).post("/api/test-image", json={"prompt": "A comic-book lighthouse under a violet moon"})
    assert response.status_code == 503
    assert "HF_API_KEY" in response.json()["detail"]
