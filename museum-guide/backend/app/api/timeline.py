from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import models as M
from ..database import repository as R
from ..database.database import get_session

router = APIRouter(prefix="/api", tags=["timeline"])


@router.get("/timeline")
def timeline(period: str | None = None, db: Session = Depends(get_session)):
    stmt = select(M.Event).order_by(M.Event.date_iso, M.Event.event_id)
    if period:
        stmt = stmt.where(M.Event.period == period)
    rels = db.scalars(select(M.Relation).where(M.Relation.to_type == "event", M.Relation.from_type == "image")).all()
    src = {s.source_id: s for s in db.scalars(select(M.Source)).all()}
    items = []
    for e in db.scalars(stmt).all():
        d = R.row_to_dict(e)
        d["source_title"] = src[e.source_id].title
        d["source_type"] = src[e.source_id].source_type
        imgs = sorted([r for r in rels if r.to_id == e.event_id], key=lambda r: 0 if r.relation == "illustrates" else 1)
        d["images"] = [{"image_id": r.from_id, "thumb_url": f"/api/images/{r.from_id}/file?size=thumb", "medium_url": f"/api/images/{r.from_id}/file?size=medium",
                        "relation": r.relation, "basis": r.basis} for r in imgs]
        items.append(d)
    return {"periods": {"1954-1956": "Giai đoạn 1954–1956 (theo sách: 7/1954–7/1956)", "1956-1967": "Giai đoạn 1956–1967", "pre-1954": "Trước 1954"}, "items": items,
            "note": "Mốc thời gian chỉ gồm sự kiện có trích dẫn trang sách hoặc điều khoản văn kiện; không có mốc chưa xác minh."}
