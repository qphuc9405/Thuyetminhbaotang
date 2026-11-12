from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

SESSION_RE = r"^[A-Za-z0-9_\-]{1,64}$"


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    language: Literal["vi", "en", "zh", "auto"] = "auto"
    session_id: str = Field("default", pattern=SESSION_RE)

    @field_validator("message")
    @classmethod
    def not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Câu hỏi không được để trống")
        return v


class NarrationRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=8000)
    language: Literal["vi", "en", "zh"] = "vi"
    voice_id: str | None = Field(None, pattern=r"^[A-Za-z0-9]{8,40}$")
