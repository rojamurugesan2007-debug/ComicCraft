"""Image prompt helper that reinforces visual continuity."""
from app.schemas import ComicPanel, ComicRequest

def consistent_image_prompt(request: ComicRequest, panel: ComicPanel) -> str:
    return (f"{request.art_style} comic illustration, recurring character {request.character_name} in {request.setting}; "
            f"{panel.image_prompt}. Scene: {panel.scene_description}. Maintain the same character design across panels. "
            "Dynamic readable composition, expressive pose, cinematic lighting, no lettering, no words, no speech bubbles.")
