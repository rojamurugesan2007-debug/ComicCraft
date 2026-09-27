"""Google Gemini provider using the official google-genai SDK."""
import json

from google import genai
from google.genai import types

from app.ai.base import AIProvider, ProviderError
from app.config import get_settings
from app.prompts.outline import outline_prompt
from app.prompts.story import story_prompt
from app.schemas import ComicOutline, ComicRequest, ComicStory


class GeminiProvider(AIProvider):
    def __init__(self, model: str):
        super().__init__(model)
        key = get_settings().gemini_api_key
        if not key:
            raise ProviderError("Gemini is not configured. Add GEMINI_API_KEY to the server environment.")
        self.client = genai.Client(api_key=key, http_options=types.HttpOptions(timeout=get_settings().ai_timeout_seconds * 1000))

    def _json(self, prompt: str) -> dict:
        try:
            response = self.client.models.generate_content(
                model=self.model, contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json"),
            )
            return json.loads(response.text or "")
        except Exception as exc:
            message = str(exc).lower()
            if "timeout" in message:
                reason = "Gemini took too long to respond. Please retry."
            elif "429" in message or "quota" in message or "rate" in message:
                reason = "Gemini rate limit or quota reached. Please wait or choose another provider."
            elif "api key" in message or "401" in message or "403" in message:
                reason = "Gemini rejected its API key. Check GEMINI_API_KEY in the server environment."
            elif "503" in message or "unavailable" in message or "high demand" in message:
                reason = "Gemini is under heavy load right now. Please retry in a moment or choose Groq."
            elif "404" in message or "not found" in message or "unsupported model" in message:
                reason = "The selected Gemini model is unavailable. Choose a configured model."
            elif isinstance(exc, (json.JSONDecodeError, ValueError)):
                reason = "Gemini returned an unreadable response. Please retry."
            else:
                reason = "Gemini is temporarily unavailable. Please retry or choose Groq."
            raise ProviderError(reason) from exc

    def generate_outline(self, request: ComicRequest) -> ComicOutline:
        try:
            return ComicOutline.model_validate(self._json(outline_prompt(request)))
        except ProviderError:
            raise
        except Exception as exc:
            raise ProviderError("Gemini returned an invalid comic outline. Please retry.") from exc

    def generate_story(self, request: ComicRequest, outline: ComicOutline) -> ComicStory:
        try:
            story = ComicStory.model_validate(self._json(story_prompt(request, outline)))
            if len(story.panels) != request.panel_count:
                raise ValueError("Incorrect panel count")
            return story
        except ProviderError:
            raise
        except Exception as exc:
            raise ProviderError("Gemini returned an invalid comic story. Please retry.") from exc
