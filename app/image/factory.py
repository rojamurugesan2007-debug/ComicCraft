"""Create the configured image provider."""
from app.config import get_settings
from app.image.provider import HuggingFaceImageProvider, ImageProvider, ImageProviderError

def get_image_provider() -> ImageProvider:
    name = get_settings().image_provider.strip().lower()
    if name in {"huggingface", "hf", "hf-inference"}: return HuggingFaceImageProvider()
    if name in {"", "none", "disabled"}: raise ImageProviderError("Image generation is disabled. Configure IMAGE_PROVIDER=huggingface and HF_API_KEY.")
    raise ImageProviderError("Unsupported image provider. Configure IMAGE_PROVIDER=huggingface.")
