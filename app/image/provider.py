"""External Hugging Face image generation; no local GPU/model required."""
from abc import ABC, abstractmethod
from io import BytesIO
from huggingface_hub import InferenceClient
from PIL import Image
from app.config import get_settings

class ImageProviderError(Exception):
    """Safe image-provider failure."""
class ImageProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> bytes: ...
class HuggingFaceImageProvider(ImageProvider):
    def __init__(self):
        settings = get_settings(); key = settings.effective_image_key
        if not key: raise ImageProviderError("Image generation is not configured. Add HF_API_KEY (or IMAGE_API_KEY) on the server.")
        self.client = InferenceClient(model=settings.image_model, token=key, timeout=settings.image_timeout_seconds)
    def generate(self, prompt: str) -> bytes:
        try:
            image = self.client.text_to_image(prompt); stream = BytesIO(); image.save(stream, format="PNG"); data = stream.getvalue()
            with Image.open(BytesIO(data)) as check: check.verify()
            return data
        except Exception as exc:
            message = str(exc).lower()
            if "401" in message or "403" in message or "token" in message: reason = "The image provider rejected its API key. Check HF_API_KEY."
            elif "429" in message or "rate" in message: reason = "Image generation rate limit reached. Please wait and retry."
            elif "timeout" in message: reason = "Image generation timed out. Please retry."
            elif "model" in message or "provider" in message: reason = "The configured image model is unavailable from the image provider."
            else: reason = "Image generation failed. Check the configured image service and retry."
            raise ImageProviderError(reason) from exc
