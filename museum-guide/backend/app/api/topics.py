from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import models as M
from ..database import repository as R
from ..database.database import get_session

router = APIRouter(prefix="/api", tags=["topics"])


@router.get("/topics")
def topics(db: Session = Depends(get_session)):
    rows = db.scalars(select(M.Topic).order_by(M.Topic.order)).all()
    out = []
    for t in rows:
        d = R.row_to_dict(t)
        d["n_events"] = sum(1 for e in db.scalars(select(M.Event)).all() if t.topic_id in (e.topic_ids or []))
        d["n_images"] = sum(1 for i in db.scalars(select(M.Image).where(M.Image.in_gallery.is_(True))).all() if t.topic_id in (i.related_book_topics or []))
        out.append(d)
    return {"items": out}


@router.get("/topics/{topic_id}")
def topic_detail(topic_id: str, db: Session = Depends(get_session)):
    t = db.get(M.Topic, topic_id)
    if t is None:
        raise HTTPException(404, "Không tìm thấy chủ đề")
    chapters = [R.row_to_dict(c) for c in db.scalars(select(M.Chapter).where(M.Chapter.chapter_id.in_(t.chapter_ids)).order_by(M.Chapter.order)).all()]
    events = [R.row_to_dict(e) for e in db.scalars(select(M.Event).order_by(M.Event.date_iso)).all() if topic_id in (e.topic_ids or [])]
    images = []
    for i in db.scalars(select(M.Image).where(M.Image.in_gallery.is_(True)).order_by(M.Image.image_id)).all():
        if topic_id in (i.related_book_topics or []):
            d = R.row_to_dict(i, skip=("search_text", "historical_context", "visual_description")); d["thumb_url"] = f"/api/images/{i.image_id}/file?size=thumb"; images.append(d)
    ch_ids = list(t.chapter_ids)
    passages = [R.row_to_dict(c, skip=("folded",)) for c in db.scalars(select(M.Chunk).where(M.Chunk.chapter_id.in_(ch_ids)).order_by(M.Chunk.chunk_id)).all()] if ch_ids else []
    return {**R.row_to_dict(t), "chapters": chapters, "events": events, "images": images[:24], "passages": passages[:30], "n_passages_total": len(passages)}
