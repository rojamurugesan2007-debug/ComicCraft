"""Safe controlled storage helpers."""
import json
import uuid
from pathlib import Path
from app.config import get_settings

def storage_paths() -> tuple[Path, Path, Path]:
    root = get_settings().storage_dir.resolve(); panels, exports, comics = root / "panels", root / "exports", root / "comics"
    for path in (panels, exports, comics): path.mkdir(parents=True, exist_ok=True)
    return panels, exports, comics

def safe_id(value: str) -> str:
    try: return str(uuid.UUID(value))
    except (ValueError, AttributeError) as exc: raise FileNotFoundError("Comic not found") from exc

def save_manifest(comic_id: str, data: dict) -> Path:
    _, _, comics = storage_paths(); target = comics / f"{safe_id(comic_id)}.json"
    target.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8"); return target

def load_manifest(comic_id: str) -> dict:
    _, _, comics = storage_paths(); return json.loads((comics / f"{safe_id(comic_id)}.json").read_text(encoding="utf-8"))
