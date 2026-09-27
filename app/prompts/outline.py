"""Structured outline prompt."""
from app.schemas import ComicRequest

def outline_prompt(request: ComicRequest) -> str:
    return f"""Create a coherent comic outline as JSON with exactly these keys: title, panels. Each panel has panel_number, title, scene_description, beat. Create exactly {request.panel_count} panels numbered in order. Give it a beginning, escalation, and satisfying ending. Keep protagonist, setting, and tone consistent. Return JSON only.
Character: {request.character_name}\nSetting: {request.setting}\nTone: {request.tone}\nArt direction: {request.art_style}\nStory idea: {request.prompt}"""
