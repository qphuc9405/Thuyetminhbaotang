"""Phục vụ file ảnh an toàn (chặn path traversal) + tạo thumbnail có cache."""
from __future__ import annotations

from pathlib import Path

from PIL import Image as PILImage

from ..config import Settings
from ..core.security import ALLOWED_IMAGE_EXT, safe_join

SIZES = {"thumb": 360, "medium": 960}


def resolve_image_file(settings: Settings, image_path: str, size: str | None) -> Path:
    src = safe_join(settings.images_root, image_path)
    if src.suffix.lower() not in ALLOWED_IMAGE_EXT or not src.is_file():
        raise FileNotFoundError(image_path)
    if size not in SIZES:
        return src
    cache = safe_join(settings.images_root, f"data/thumbs/{size}/{src.stem}.jpg")
    if not cache.exists():
        cache.parent.mkdir(parents=True, exist_ok=True)
        with PILImage.open(src) as im:
            im = im.convert("RGB")
            im.thumbnail((SIZES[size], SIZES[size]))
            im.save(cache, "JPEG", quality=82)
    return cache
