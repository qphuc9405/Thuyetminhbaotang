"""Câu chuyện trang chủ (4 chương) – dữ liệu biên soạn có trích dẫn trang sách đã kiểm tra anchor (knowledge_base/story.json)."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from ..database import models as M
from ..database.database import get_session

router = APIRouter(prefix="/api", tags=["story"])


@lru_cache(maxsize=4)
def _load(path: str) -> list[dict]:
    p = Path(path)
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else []


@router.get("/story")
def story(request: Request, db: Session = Depends(get_session)):
    root = Path(request.app.state.settings.images_root)
    chapters = _load(str(root / "knowledge_base/story.json"))
    if not chapters:
        raise HTTPException(503, "Chưa có dữ liệu câu chuyện (chạy scripts/build_knowledge_base.py)")
    out = []
    for ch in chapters:
        im = db.get(M.Image, ch["image_id"])
        d = dict(ch)
        d["image"] = None if im is None else {"image_id": im.image_id, "title": im.title, "title_en": im.title_en, "title_zh": im.title_zh, "caption": im.caption,
                                              "image_url": f"/api/images/{im.image_id}/file", "medium_url": f"/api/images/{im.image_id}/file?size=medium",
                                              "kind": im.kind, "printed_page": im.printed_page, "location": im.location, "time_period": im.time_period}
        out.append(d)
    hero = db.get(M.Image, "IMG034")
    return {"chapters": out, "hero": None if hero is None else {"image_id": "IMG034", "image_url": "/api/images/IMG034/file", "title": hero.title, "title_en": hero.title_en, "title_zh": hero.title_zh,
                                                               "note": "Ảnh trùng với hình in tr.187 của sách ('Cây cầu Hiền Lương có hai màu'); năm chụp chưa xác định."}}


def _img(im) -> dict:
    return {"image_id": im.image_id, "title": im.title, "title_en": im.title_en, "title_zh": im.title_zh, "caption": im.caption, "kind": im.kind,
            "image_url": f"/api/images/{im.image_id}/file", "medium_url": f"/api/images/{im.image_id}/file?size=medium",
            "thumb_url": f"/api/images/{im.image_id}/file?size=thumb", "printed_page": im.printed_page, "time_period": im.time_period}


@router.get("/anecdotes")
def anecdotes(request: Request, db: Session = Depends(get_session)):
    """Mục 'Những mẩu chuyện thú vị' (knowledge_base/anecdotes.json): văn kể biên soạn từ sách/bài viết/báo web, trích dẫn đã kiểm tra anchor."""
    root = Path(request.app.state.settings.images_root)
    items = _load(str(root / "knowledge_base/anecdotes.json"))
    if not items:
        raise HTTPException(503, "Chưa có dữ liệu mẩu chuyện (chạy scripts/build_knowledge_base.py)")
    out = []
    for a in items:
        d = dict(a)
        d["images"] = [_img(im) for im in (db.get(M.Image, i) for i in a["image_ids"]) if im is not None]
        d["notes_detail"] = [{"chunk_id": c.chunk_id, "title": c.title} for c in (db.get(M.Chunk, n) for n in a.get("notes", [])) if c is not None]
        out.append(d)
    return {"items": out, "note": "Văn kể do nhóm biên soạn từ các nguồn được trích; chỗ các nguồn khác nhau được nêu rõ (ghi chú đối chiếu NOTE-xx)."}


@router.get("/exhibits")
def exhibits(request: Request, group: str | None = None):
    """Gian trưng bày số: hiện vật có thuyết minh + trích dẫn (knowledge_base/exhibits.json)."""
    items = _load(str(Path(request.app.state.settings.images_root) / "knowledge_base/exhibits.json"))
    if not items:
        raise HTTPException(503, "Chưa có dữ liệu gian trưng bày (chạy scripts/build_knowledge_base.py)")
    if group:
        items = [e for e in items if e["group"] == group]
    return {"items": items, "total": len(items)}


@router.get("/zones/{zone_id}")
def zone(zone_id: str, request: Request):
    """Nội dung theo khu vực trên bản đồ tham quan: bridge | flag | museum | monument | union."""
    zones = _load(str(Path(request.app.state.settings.images_root) / "knowledge_base/zones.json"))
    if not zones:
        raise HTTPException(503, "Chưa có dữ liệu khu vực")
    if not isinstance(zones, dict) or zone_id not in zones:
        raise HTTPException(404, "Không có khu vực này")
    return {"zone_id": zone_id, **zones[zone_id]}
