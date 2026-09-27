import pytest
from app.ai.base import ProviderError
from app.ai.factory import get_provider
from app.config import Settings

def test_factory_rejects_unknown_provider():
    with pytest.raises(ProviderError):
        get_provider("other", "x")

def test_factory_rejects_unconfigured_model(monkeypatch):
    settings = Settings(gemini_api_key="fake", gemini_models="gemini-test", default_gemini_model="gemini-test")
    monkeypatch.setattr("app.ai.factory.get_settings", lambda: settings)
    monkeypatch.setattr("app.ai.gemini_provider.get_settings", lambda: settings)
    with pytest.raises(ProviderError):
        get_provider("gemini", "not-configured")

def test_factory_reports_missing_key(monkeypatch):
    settings = Settings(gemini_api_key="", gemini_models="gemini-test", default_gemini_model="gemini-test")
    monkeypatch.setattr("app.ai.factory.get_settings", lambda: settings)
    monkeypatch.setattr("app.ai.gemini_provider.get_settings", lambda: settings)
    with pytest.raises(ProviderError, match="GEMINI_API_KEY"):
        get_provider("gemini", "gemini-test")
