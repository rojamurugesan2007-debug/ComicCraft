import pytest
from app.ai.base import ProviderError
from app.ai.gemini_provider import GeminiProvider

def test_gemini_503_high_demand_is_retryable():
    class FakeModels:
        def generate_content(self, **kwargs):
            raise RuntimeError("503 UNAVAILABLE: model is currently experiencing high demand")
    provider = GeminiProvider.__new__(GeminiProvider)
    provider.model = "gemini-test"
    provider.client = type("FakeClient", (), {"models": FakeModels()})()
    with pytest.raises(ProviderError, match="heavy load"):
        provider._json("test")
