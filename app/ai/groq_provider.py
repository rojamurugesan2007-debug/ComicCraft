"""Groq provider using the official Groq Python SDK."""
import json

from groq import Groq

from app.ai.base import AIProvider, ProviderError
from app.config import get_settings
from app.prompts.outline import outline_prompt
from app.prompts.story import story_prompt
from app.schemas import ComicOutline, ComicRequest, ComicStory


class GroqProvider(AIProvider):
    def __init__(self, model: str):
        super().__init__(model)
        key = get_settings().groq_api_key
        if not key:
            raise ProviderError("Groq is not configured. Add GROQ_API_KEY to the server environment.")
        self.client = Groq(api_key=key, timeout=get_settings().ai_timeout_seconds, max_retries=1)

    def _json(self, prompt: str) -> dict:
        try:
            result = self.client.chat.completions.create(
                model=self.model, temperature=0.7, response_format={"type": "json_object"},
                messages=[{"role": "system", "content": "Return only valid JSON. Follow the requested JSON structure exactly."},
                          {"role": "user", "content": prompt}],
            )
            return json.loads(result.choices[0].message.content or "")
        except Exception as exc:
            message = str(exc).lower()
            if "429" in message or "rate limit" in message:
                reason = "Groq rate limit reached. Please wait or choose another provider."
            elif "api key" in message or "401" in message or "403" in message:
                reason = "Groq rejected its API key. Check GROQ_API_KEY in the server environment."
            elif "model" in message or "404" in message:
                reason = "The selected Groq model is unavailable. Choose a configured model."
            elif isinstance(exc, (json.JSONDecodeError, IndexError, ValueError)):
                reason = "Groq returned an unreadable response. Please retry."
            elif "timeout" in message:
                reason = "Groq took too long to respond. Please retry."
            else:
                reason = "Groq is temporarily unavailable. Please retry or choose Gemini."
            raise ProviderError(reason) from exc

    def generate_outline(self, request: ComicRequest) -> ComicOutline:
        try:
            return ComicOutline.model_validate(self._json(outline_prompt(request)))
        except ProviderError:
            raise
        except Exception as exc:
            raise ProviderError("Groq returned an invalid comic outline. Please retry.") from exc

    def generate_story(self, request: ComicRequest, outline: ComicOutline) -> ComicStory:
        try:
            story = ComicStory.model_validate(self._json(story_prompt(request, outline)))
            if len(story.panels) != request.panel_count:
                raise ValueError("Incorrect panel count")
            return story
        except ProviderError:
            raise
        except Exception as exc:
            raise ProviderError("Groq returned an invalid comic story. Please retry.") from exc
