"""Cấu hình ứng dụng. Mọi khoá bí mật chỉ đọc từ biến môi trường / .env, KHÔNG hardcode."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from urllib.parse import urlparse

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]  # thư mục dự án


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env", str(ROOT / "backend/.env")), extra="ignore")

    ollama_api_key: SecretStr = Field(default=SecretStr(""))
    ollama_host: str = "https://ollama.com"
    ollama_model: str = "gpt-oss:120b-cloud"
    llm_timeout_s: float = 60
    llm_max_retries: int = 2
    local_fast_mode: bool = True
    chat_cache_ttl_s: int = Field(default=600, ge=0)

    elevenlabs_api_key: SecretStr = Field(default=SecretStr(""))
    elevenlabs_model: str = "eleven_flash_v2_5"
    elevenlabs_voice_vi: str = "JBFqnCBsd6RMkjVDRZzb"
    elevenlabs_voice_en: str = "JBFqnCBsd6RMkjVDRZzb"
    elevenlabs_voice_zh: str = "JBFqnCBsd6RMkjVDRZzb"
    tts_chunk_chars: int = 900
    tts_timeout_s: float = 45

    database_url: str = f"sqlite:///{ROOT / 'data/museum.db'}"
    cors_origins: str = "http://localhost:5173"
    max_request_bytes: int = 20000
    max_message_chars: int = 800
    retrieval_top_k: int = 6
    embedding_backend: str = "tfidf"
    embedding_model: str = "intfloat/multilingual-e5-small"
    audio_cache_dir: str = str(ROOT / "data/audio_cache")
    images_root: str = str(ROOT)

    @property
    def local_llm(self) -> bool:
        return urlparse(self.ollama_host).hostname in {"localhost", "127.0.0.1", "::1"}

    @property
    def effective_ollama_model(self) -> str:
        """Gọi trực tiếp ollama.com thì dùng tên model không có hậu tố '-cloud' (theo docs Ollama)."""
        m = self.ollama_model
        if self.ollama_host.rstrip("/").endswith("ollama.com") and m.endswith("-cloud"):
            return m[: -len("-cloud")]
        return m

    def voice_for(self, lang: str) -> str:
        return {"vi": self.elevenlabs_voice_vi, "en": self.elevenlabs_voice_en, "zh": self.elevenlabs_voice_zh}.get(
            lang, self.elevenlabs_voice_en
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
