"""Truy vấn DB → dict thuần (tách tầng dữ liệu khỏi API/service)."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models as M


def row_to_dict(r, skip=()) -> dict:
    return {c.name: getattr(r, c.name) for c in r.__table__.columns if c.name not in skip}


def load_chunks(db: Session) -> list[dict]:
    return [row_to_dict(c) for c in db.scalars(select(M.Chunk).order_by(M.Chunk.chunk_id)).all()]


def load_images(db: Session) -> list[dict]:
    return [row_to_dict(i) for i in db.scalars(select(M.Image).order_by(M.Image.image_id)).all()]


def recent_messages(db: Session, session_id: str, limit: int = 6) -> list[dict]:
    rows = db.scalars(select(M.ChatMessage).where(M.ChatMessage.session_id == session_id).order_by(M.ChatMessage.id.desc()).limit(limit)).all()
    return [{"role": r.role, "content": r.content} for r in reversed(rows)]


def save_message(db: Session, session_id: str, role: str, content: str, language: str | None) -> None:
    db.add(M.ChatMessage(session_id=session_id, role=role, content=content[:4000], language=language))
    db.commit()


def chunk_image_links(db: Session) -> dict[str, list[tuple[str, str]]]:
    """chunk_id -> [(image_id, link_basis)] cho quan hệ ảnh→đoạn (in trong sách / topic_corroborated)."""
    out: dict[str, list[tuple[str, str]]] = {}
    for r in db.scalars(select(M.Relation).where(M.Relation.from_type == "image", M.Relation.to_type == "chunk")).all():
        out.setdefault(r.to_id, []).append((r.from_id, r.basis))
    # ưu tiên liên kết trực tiếp
    for k in out:
        out[k].sort(key=lambda x: 0 if x[1] != "topic_corroborated" else 1)
    return out
