from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..database.database import get_session
from ..schemas import NarrationRequest

router = APIRouter(prefix="/api/narration", tags=["narration"])


@router.post("/generate")
async def generate(req: NarrationRequest, request: Request, db: Session = Depends(get_session)):
    return await request.app.state.narration.generate(db, req.text, req.language, req.voice_id)


@router.get("/{audio_id}")
def get_audio(audio_id: str, request: Request, db: Session = Depends(get_session)):
    import re
    from fastapi import HTTPException
    if not re.fullmatch(r"[a-f0-9]{40}", audio_id):
        raise HTTPException(404, "audio_id không hợp lệ")
    p = request.app.state.narration.file_path(db, audio_id)
    return FileResponse(p, media_type="audio/mpeg", headers={"Cache-Control": "public, max-age=86400"})
