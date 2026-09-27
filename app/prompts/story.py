"""Prompt for expanding an outline into panel copy."""
import json
from app.schemas import ComicOutline, ComicRequest

def story_prompt(request: ComicRequest, outline: ComicOutline) -> str:
    shape = {"title":"Comic title","panels":[{"panel_number":1,"title":"Panel title","scene_description":"Visual scene","narration":"Optional narration","dialogue":"Character dialogue","caption":"Short caption","image_prompt":"Detailed illustration prompt"}]}
    return f"""Expand this outline into a polished comic. Return JSON only shaped like {json.dumps(shape)}. Produce exactly {request.panel_count} panels, preserving order, character identity, plot continuity, setting, and tone. Keep dialogue and captions concise. Image prompts must specify recurring character appearance, environment, action, camera angle, lighting, {request.art_style} style, mood, and composition. Do not request text or lettering in the art.
Character: {request.character_name}\nSetting: {request.setting}\nTone: {request.tone}\nArt style: {request.art_style}\nOriginal idea: {request.prompt}\nOutline: {outline.model_dump_json()}"""
