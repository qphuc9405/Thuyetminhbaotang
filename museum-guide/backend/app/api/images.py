from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from ..database import models as M
from ..database import repository as R
from ..database.database import get_session
from ..services.image_service import resolve_image_file
from ..services.text_utils import fold

router = APIRouter(prefix="/api", tags=["images"])
IMG_TOPIC_LABELS = {"bridge": ("Cầu Hiền Lương", "Hien Luong bridge", "贤良桥"), "demarcation": ("Giới tuyến quân sự tạm thời", "Provisional military demarcation line", "临时军事分界线"),
    "banner_diem": ("Băng-rôn/khẩu hiệu bờ Nam", "Banners of the southern bank", "南岸横幅"), "gate": ("Cổng chào Hiền Lương", "Hien Luong gateway", "贤良牌楼"),
    "police": ("Công an/cảnh sát giới tuyến", "Demarcation-line police", "分界线警察"), "flagpoles": ("Cột cờ Hiền Lương", "Hien Luong flagpoles", "贤良旗杆"),
    "slogan_wall": ("Tường khẩu hiệu hai bờ", "Slogan walls", "两岸标语墙"), "loudspeakers": ("Hệ thống loa phát thanh", "Loudspeaker system", "广播扩音系统"),
    "geneva_conf": ("Hội nghị Genève 1954", "1954 Geneva Conference", "1954年日内瓦会议"),
    "memorial_site": ("Di tích Đôi bờ Hiền Lương – Bến Hải ngày nay", "Hien Luong–Ben Hai relic site today", "今日贤良—边海两岸遗迹")}
LIST_SKIP = ("search_text", "historical_context", "visual_description")


@router.get("/images")
def list_images(request: Request, q: str | None = None, topic: str | None = None, kind: str | None = None, group: str | None = None,
                hide_variants: bool = False, limit: int = 100, offset: int = 0, db: Session = Depends(get_session)):
    limit = min(max(limit, 1), 200)
    stmt = select(M.Image).where(M.Image.in_gallery.is_(True)).order_by(M.Image.image_id)
    if kind:
        stmt = stmt.where(M.Image.kind == kind)
    if group:
        stmt = stmt.where(or_(M.Image.duplicate_group == group, M.Image.similar_scene_group == group))
    rows = db.scalars(stmt).all()
    if topic:
        rows = [r for r in rows if topic in (r.related_book_topics or [])]
    if q:
        fq = fold(q)
        toks = [t for t in fq.split() if len(t) > 1]
        rows = [r for r in rows if all(t in r.search_text for t in toks)]
    if hide_variants:
        seen, keep = set(), []
        for r in rows:
            if r.duplicate_group:
                if r.duplicate_group in seen:
                    continue
                seen.add(r.duplicate_group)
            keep.append(r)
        rows = keep
    total = len(rows)
    items = []
    for r in rows[offset: offset + limit]:
        d = R.row_to_dict(r, skip=LIST_SKIP)
        d["image_url"] = f"/api/images/{r.image_id}/file"; d["thumb_url"] = f"/api/images/{r.image_id}/file?size=thumb"
        items.append(d)
    return {"total": total, "offset": offset, "limit": limit, "items": items}


@router.get("/images/{image_id}")
def image_detail(image_id: str, db: Session = Depends(get_session)):
    im = db.get(M.Image, image_id)
    if im is None:
        raise HTTPException(404, "Không tìm thấy ảnh")
    d = R.row_to_dict(im, skip=("search_text",))
    d["image_url"] = f"/api/images/{image_id}/file"; d["thumb_url"] = f"/api/images/{image_id}/file?size=thumb"
    rels = db.scalars(select(M.Relation).where(or_((M.Relation.from_type == "image") & (M.Relation.from_id == image_id), (M.Relation.to_type == "image") & (M.Relation.to_id == image_id)))).all()
    d["related_images"] = [{"image_id": (r.to_id if r.from_id == image_id else r.from_id), "relation": r.relation, "basis": r.basis, "confidence": r.confidence} for r in rels if r.to_type == "image"]
    chunk_rels = sorted([r for r in rels if r.to_type == "chunk" and r.from_id == image_id], key=lambda r: {"captioned_in_document": 0, "same_figure_in_book": 1}.get(r.relation, 2))
    chunk_ids = [r.to_id for r in chunk_rels][:6]
    chunks = [db.get(M.Chunk, cid) for cid in chunk_ids]
    d["related_passages"] = [{"chunk_id": c.chunk_id, "source_id": c.source_id, "source_title": c.source_title, "source_type": c.source_type, "provision": c.provision,
                              "printed_page": c.printed_page, "printed_page_end": c.printed_page_end, "chapter": c.chapter, "excerpt": c.content[:260],
                              "link_type": next((r.basis for r in chunk_rels if r.to_id == c.chunk_id), None),
                              "relation": next((r.relation for r in chunk_rels if r.to_id == c.chunk_id), None)} for c in chunks if c]
    d["related_events_detail"] = [{"event_id": e.event_id, "date_label": e.date_label, "title_vi": e.title_vi} for e in (db.get(M.Event, i) for i in (im.related_events or [])) if e]
    td = []
    for i in (im.related_book_topics or []):
        t = db.get(M.Topic, i)
        if t:
            td.append({"topic_id": t.topic_id, "title_vi": t.title_vi, "title_en": t.title_en, "title_zh": t.title_zh})
        elif i in IMG_TOPIC_LABELS:
            vi, en, zh = IMG_TOPIC_LABELS[i]
            tid = "bridgeflag" if i in ("bridge", "flagpoles", "gate", "demarcation", "banner_diem") else ("broadcast" if i in ("loudspeakers", "slogan_wall") else "police")
            td.append({"topic_id": tid, "title_vi": vi, "title_en": en, "title_zh": zh})
    d["topics_detail"] = td
    return d


@router.get("/images/{image_id}/file")
def image_file(image_id: str, request: Request, size: str | None = None, db: Session = Depends(get_session)):
    im = db.get(M.Image, image_id)
    if im is None:
        raise HTTPException(404, "Không tìm thấy ảnh")
    try:
        p = resolve_image_file(request.app.state.settings, im.image_path, size)
    except (FileNotFoundError, ValueError):
        raise HTTPException(404, "Tệp ảnh không tồn tại")
    return FileResponse(p, headers={"Cache-Control": "public, max-age=86400"})
