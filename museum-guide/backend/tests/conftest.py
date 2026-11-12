"""Fixture dùng chung. TẤT CẢ lời gọi LLM/TTS đi qua httpx.MockTransport -> không tốn quota Ollama/ElevenLabs."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

BACKEND = Path(__file__).resolve().parents[1]
ROOT = BACKEND.parent
sys.path.insert(0, str(BACKEND))

from app.config import Settings  # noqa: E402
from app.main import create_app  # noqa: E402
from app.services.llm_service import LLMService  # noqa: E402
from app.services.tts_service import TTSService  # noqa: E402

DB = ROOT / "data/museum.db"


class FakeBackend:
    """Mô phỏng Ollama + ElevenLabs. `llm_script`: danh sách phản hồi tuần tự (dict/Exception/callable)."""

    def __init__(self):
        self.llm_script: list = []
        self.llm_calls: list[dict] = []
        self.tts_calls: list[dict] = []
        self.tts_status = 200

    def llm_handler(self, request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        self.llm_calls.append({"body": body, "headers": dict(request.headers)})
        item = self.llm_script.pop(0) if self.llm_script else {"message": {"content": json.dumps({"answer": "Không có kịch bản.", "used_sources": [], "used_images": [], "insufficient_evidence": True, "confidence": "low"})}}
        if isinstance(item, Exception):
            raise item
        if callable(item):
            return item(request)
        return httpx.Response(200, json=item)

    def tts_handler(self, request: httpx.Request) -> httpx.Response:
        self.tts_calls.append({"url": str(request.url), "body": json.loads(request.content), "headers": dict(request.headers)})
        if self.tts_status != 200:
            return httpx.Response(self.tts_status, json={"detail": {"status": "quota_exceeded" if self.tts_status == 401 else "error"}})
        return httpx.Response(200, content=b"ID3FAKEMP3" + bytes(len(self.tts_calls)))


def llm_json(answer: str, used=("S1",), images=(), insufficient=False, conf="high") -> dict:
    return {"message": {"content": json.dumps({"answer": answer, "used_sources": list(used), "used_images": list(images), "insufficient_evidence": insufficient, "confidence": conf}, ensure_ascii=False)}}


@pytest.fixture(scope="session")
def fake():
    return FakeBackend()


@pytest.fixture(scope="session")
def db_copy(tmp_path_factory):
    """Bản sao CSDL cho test (chat_messages/narrations ghi vào bản sao, KHÔNG làm bẩn data/museum.db)."""
    import shutil
    p = tmp_path_factory.mktemp("db") / "museum_test.db"
    shutil.copy(DB, p)
    return p


@pytest.fixture
def settings(tmp_path, db_copy):
    return Settings(database_url=f"sqlite:///{db_copy}", audio_cache_dir=str(tmp_path / "audio"), ollama_host="https://ollama.com", ollama_model="gpt-oss:120b-cloud", ollama_api_key=SecretStr("test-ollama-key-123456"), elevenlabs_api_key=SecretStr("test-eleven-key-123456"),
                    llm_max_retries=2, llm_timeout_s=5, images_root=str(ROOT), cors_origins="http://localhost:5173")


@pytest.fixture
def client(settings, fake, monkeypatch):
    import app.services.llm_service as ls
    monkeypatch.setattr(ls.asyncio, "sleep", lambda *_a, **_k: _noop())  # không chờ backoff thật
    fake.llm_script.clear(); fake.llm_calls.clear(); fake.tts_calls.clear(); fake.tts_status = 200
    llm = LLMService(settings, transport=httpx.MockTransport(fake.llm_handler))
    tts = TTSService(settings, transport=httpx.MockTransport(fake.tts_handler))
    app = create_app(settings, llm=llm, tts=tts)
    with TestClient(app) as c:
        c.fake = fake
        yield c


async def _noop():
    return None


@pytest.fixture(scope="session")
def index_and_chunks():
    from app.database import repository as R
    from app.database.database import get_engine, session_scope
    from app.services.retrieval_service import RetrievalIndex
    get_engine(f"sqlite:///{DB}")
    with session_scope() as db:
        ch = R.load_chunks(db)
    return RetrievalIndex(ch), ch
