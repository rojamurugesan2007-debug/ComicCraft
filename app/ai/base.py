"""Shared provider contract and safe provider exceptions."""
from abc import ABC, abstractmethod

from app.schemas import ComicOutline, ComicRequest, ComicStory


class ProviderError(Exception):
    """A user-safe AI provider failure."""


class AIProvider(ABC):
    def __init__(self, model: str):
        self.model = model

    @abstractmethod
    def generate_outline(self, request: ComicRequest) -> ComicOutline: ...

    @abstractmethod
    def generate_story(self, request: ComicRequest, outline: ComicOutline) -> ComicStory: ...
