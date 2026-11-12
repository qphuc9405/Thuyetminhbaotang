"""Narration: chia văn bản dài thành đoạn, gọi TTS từng đoạn, ghép MP3, cache theo (model, voice, ngôn ngữ, văn bản)."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

from sqlalchemy.orm import Session

from ..config import Settings
from ..core.exceptions import NotFound
from ..core.security import safe_join
from ..database import models as M
from .text_utils import split_sentences
from .tts_service import TTSService

_CLEAN = re.compile(r"\[(?:S|I)\d+\]")


def clean_for_speech(text: str) -> str:
    return re.sub(r"\s+", " ", _CLEAN.sub("", text)).strip()


def split_for_tts(text: str, max_chars: int) -> list[str]:
    out, cur = [], ""
    for s in split_sentences(text) or [text]:
        while len(s) > max_chars:  # câu cực dài: cắt theo dấu phẩy/khoảng trắng
            cut = max(s.rfind(",", 0, max_chars), s.rfind(" ", 0, max_chars), max_chars // 2)
            if cur:
                out.append(cur); cur = ""
            out.append(s[:cut].strip()); s = s[cut:].lstrip(", ")
        if cur and len(cur) + 1 + len(s) > max_chars:
            out.append(cur); cur = s
        else:
            cur = (cur + " " + s).strip()
    if cur:
        out.append(cur)
    return [x for x in out if x]


def audio_id_for(model: str, voice: str, lang: str, text: str) -> str:
    return hashlib.sha256(f"{model}|{voice}|{lang}|{text}".encode()).hexdigest()[:40]


class NarrationService:
    def __init__(self, settings: Settings, tts: TTSService):
        self.s, self.tts = settings, tts
        Path(settings.audio_cache_dir).mkdir(parents=True, exist_ok=True)

    async def generate(self, db: Session, text: str, language: str, voice_id: str | None = None) -> dict:
        text = clean_for_speech(text)
        voice = voice_id or self.s.voice_for(language)
        aid = audio_id_for(self.s.elevenlabs_model, voice, language, text)
        row = db.get(M.Narration, aid)
        path = safe_join(self.s.audio_cache_dir, f"{aid}.mp3")
        if row and row.status == "ready" and path.exists():
            return self._info(row, cached=True)
        segs = split_for_tts(text, self.s.tts_chunk_chars)
        audio = b""
        for seg in segs:  # lỗi ở bất kỳ đoạn nào → ném TTSUnavailable (API trả 503, chatbot không bị ảnh hưởng)
            audio += await self.tts.synthesize(seg, language, voice)
        path.write_bytes(audio)
        if row is None:
            row = M.Narration(audio_id=aid, language=language, voice_id=voice, model=self.s.elevenlabs_model, text_chars=len(text), n_segments=len(segs), path=str(path.name), status="ready")
            db.add(row)
        else:
            row.status, row.path, row.n_segments = "ready", path.name, len(segs)
        db.commit()
        return self._info(row, cached=False)

    def file_path(self, db: Session, audio_id: str) -> Path:
        row = db.get(M.Narration, audio_id)
        if not row or row.status != "ready":
            raise NotFound("Không tìm thấy audio.")
        p = safe_join(self.s.audio_cache_dir, f"{audio_id}.mp3")
        if not p.exists():
            raise NotFound("Tệp audio không còn trong cache.")
        return p

    @staticmethod
    def _info(row: M.Narration, cached: bool) -> dict:
        return {"audio_id": row.audio_id, "status": row.status, "language": row.language, "voice_id": row.voice_id, "model": row.model,
                "segments": row.n_segments, "characters": row.text_chars, "cached": cached, "audio_url": f"/api/narration/{row.audio_id}"}
