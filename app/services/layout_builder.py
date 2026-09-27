"""Store generated panel images under generated comic identifiers."""
from pathlib import Path

def store_panel_image(panel_number: int, image_data: bytes, comic_id: str, directory: Path) -> str:
    filename = f"{comic_id}_{panel_number:02d}.png"; (directory / filename).write_bytes(image_data)
    return f"/media/panels/{filename}"
