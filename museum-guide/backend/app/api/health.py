from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import models as M
from ..database.database import get_session

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
def health(request: Request, db: Session = Depends(get_session)):
    st = request.app.state
    return {
        "status": "ok", "version": "1.0.0",
        "database": {"ok": True, "chunks": db.scalar(select(func.count()).select_from(M.Chunk)), "images": db.scalar(select(func.count()).select_from(M.Image)),
                     "pages": db.scalar(select(func.count()).select_from(M.Page)), "events": db.scalar(select(func.count()).select_from(M.Event))},
        "retrieval": {"backend": st.index.backend, "image_retrieval": "metadata-based (không có image embedding)"},
        "llm": {"configured": bool(st.settings.ollama_api_key.get_secret_value()) or not st.settings.ollama_host.rstrip("/").endswith("ollama.com"), "model": st.settings.effective_ollama_model, "host": st.settings.ollama_host},
        "tts": {"configured": st.tts.available(), "model": st.settings.elevenlabs_model},
    }
