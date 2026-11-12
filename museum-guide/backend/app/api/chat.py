from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from ..database import repository as R
from ..database.database import get_session
from ..schemas import ChatRequest

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat")
async def chat(req: ChatRequest, request: Request, db: Session = Depends(get_session)):
    st = request.app.state
    history = R.recent_messages(db, req.session_id, 6)
    result = await st.rag.answer(req.message, req.language, history)
    p = result.payload
    R.save_message(db, req.session_id, "user", req.message, p["language"])
    R.save_message(db, req.session_id, "assistant", p["answer"], p["language"])
    return p


@router.get("/search")
def search(q: str, request: Request, k: int = 6, source_type: str | None = None, chapter: str | None = None):
    """Chỉ truy xuất (không gọi LLM) – dùng để kiểm tra/ debug retrieval."""
    if not q.strip() or len(q) > 400:
        from fastapi import HTTPException
        raise HTTPException(422, "q không hợp lệ")
    st = request.app.state
    flt = {}
    if source_type: flt["source_types"] = [source_type]
    if chapter: flt["chapter_ids"] = [chapter]
    hits, qp = st.index.search(q, k=min(max(k, 1), 20), flt=flt or None)
    out = []
    for h in hits:
        c = st.index.chunk(h.chunk_id)
        out.append({"chunk_id": h.chunk_id, "score": h.score, "coverage": h.coverage, "components": h.components, "source_id": c["source_id"], "source_title": c["source_title"],
                    "source_type": c["source_type"], "chapter": c["chapter"], "pdf_page": c["pdf_page"], "printed_page": c["printed_page"], "printed_page_end": c["printed_page_end"],
                    "provision": c.get("provision"), "content": c["content"]})
    return {"query": q, "language": qp["language"], "glossary_hits": qp["glossary_hits"], "results": out}
