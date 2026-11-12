from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import models as M
from ..database import repository as R
from ..database.database import get_session

router = APIRouter(prefix="/api", tags=["documents"])


@router.get("/sources")
def sources(db: Session = Depends(get_session)):
    return {"items": [R.row_to_dict(s) for s in db.scalars(select(M.Source).order_by(M.Source.source_id)).all()]}


@router.get("/sources/{source_id}")
def source_detail(source_id: str, db: Session = Depends(get_session)):
    s = db.get(M.Source, source_id)
    if s is None:
        raise HTTPException(404, "Không tìm thấy nguồn")
    return R.row_to_dict(s)


@router.get("/documents")
def documents(db: Session = Depends(get_session)):
    out = []
    for s in db.scalars(select(M.Source).order_by(M.Source.source_id)).all():
        d = R.row_to_dict(s)
        d["n_chunks"] = db.scalar(select(func.count()).select_from(M.Chunk).where(M.Chunk.source_id == s.source_id))
        if s.source_id == "SRC001":
            d["n_pages"] = db.scalar(select(func.count()).select_from(M.Page).where(M.Page.source_id == s.source_id))
            d["n_pages_need_review"] = db.scalar(select(func.count()).select_from(M.Page).where(M.Page.needs_review.is_(True)))
            d["ocr_mean_conf"] = round(db.scalar(select(func.avg(M.Page.ocr_mean_conf)).where(M.Page.ocr_mean_conf.is_not(None))) or 0, 2)
        n_img = db.scalar(select(func.count()).select_from(M.Image).where(M.Image.source_id == s.source_id))
        if n_img:
            d["n_images"] = n_img
        out.append(d)
    return {"items": out}


@router.get("/documents/SRC001/pages/{printed_page}")
def book_page(printed_page: int, db: Session = Depends(get_session)):
    p = db.scalar(select(M.Page).where(M.Page.printed_page == printed_page))
    if p is None:
        raise HTTPException(404, "Không có trang in này (1–260)")
    d = R.row_to_dict(p, skip=("direct_text",))
    d["note"] = "Văn bản là kết quả OCR (có thể sai dấu); trang in được suy ra từ vị trí spread, đối chiếu với số OCR."
    return d
