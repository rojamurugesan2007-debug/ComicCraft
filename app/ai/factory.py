"""Provider and model validation."""
from app.ai.base import AIProvider, ProviderError
from app.ai.gemini_provider import GeminiProvider
from app.ai.groq_provider import GroqProvider
from app.config import get_settings


def get_provider(provider_name: str, model_name: str = "") -> AIProvider:
    settings = get_settings()
    name = provider_name.strip().lower()
    if name not in {"gemini", "groq"}:
        raise ProviderError("Choose Google Gemini or Groq as the AI provider.")
    models = settings.models_for(name)
    model = model_name.strip() or settings.default_model_for(name)
    if model not in models:
        raise ProviderError("That model is not configured for this provider. Refresh the model list and try again.")
    if name == "gemini":
        return GeminiProvider(model)
    return GroqProvider(model)
