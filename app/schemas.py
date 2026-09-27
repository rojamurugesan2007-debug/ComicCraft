"""Validated request and response data structures for comics."""
from typing import Literal
from pydantic import BaseModel, Field, field_validator, model_validator
from app.config import get_settings

class ComicRequest(BaseModel):
    prompt: str = Field(min_length=10, max_length=2000)
    character_name: str = Field(min_length=1, max_length=60)
    setting: str = Field(min_length=2, max_length=120)
    tone: str = Field(min_length=2, max_length=40)
    art_style: str = Field(min_length=2, max_length=60)
    provider: Literal["gemini", "groq"] = "gemini"
    model: str = ""
    panel_count: int = Field(default=5, ge=3, le=9)

    @field_validator("prompt", "character_name", "setting", "tone", "art_style", mode="before")
    @classmethod
    def trim_text(cls, value: str) -> str:
        return value.strip() if isinstance(value, str) else value

    @field_validator("prompt")
    @classmethod
    def prompt_limit(cls, value: str) -> str:
        if len(value) > get_settings().max_prompt_length:
            raise ValueError("Prompt exceeds MAX_PROMPT_LENGTH")
        return value

    @field_validator("panel_count")
    @classmethod
    def allowed_panel_count(cls, value: int) -> int:
        if value not in {3, 5, 7, 9} or value > get_settings().max_panels:
            raise ValueError("Panel count must be 3, 5, 7, or 9 and within MAX_PANELS")
        return value

class OutlinePanel(BaseModel):
    panel_number: int = Field(ge=1)
    title: str = Field(min_length=1, max_length=100)
    scene_description: str = Field(min_length=1, max_length=600)
    beat: str = Field(min_length=1, max_length=300)

class ComicOutline(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    panels: list[OutlinePanel]
    @model_validator(mode="after")
    def ordered_panels(self):
        if [p.panel_number for p in self.panels] != list(range(1, len(self.panels) + 1)):
            raise ValueError("Outline panels must be numbered in order")
        return self

class ComicPanel(BaseModel):
    panel_number: int = Field(ge=1)
    title: str = Field(min_length=1, max_length=100)
    scene_description: str = Field(min_length=1, max_length=800)
    narration: str = Field(default="", max_length=500)
    dialogue: str = Field(default="", max_length=500)
    caption: str = Field(default="", max_length=300)
    image_prompt: str = Field(min_length=1, max_length=1200)
    image_url: str = ""

class ComicStory(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    panels: list[ComicPanel]
    metadata: dict[str, str] = Field(default_factory=dict)
    @model_validator(mode="after")
    def ordered_panels(self):
        if [p.panel_number for p in self.panels] != list(range(1, len(self.panels) + 1)):
            raise ValueError("Comic panels must be numbered in order")
        return self

class GenerationResponse(BaseModel):
    success: bool = True
    comic_id: str
    comic: ComicStory
    pdf_url: str

class ProviderInfo(BaseModel):
    id: str
    name: str
    configured: bool
    models: list[str]
class ImageTestRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=800)
