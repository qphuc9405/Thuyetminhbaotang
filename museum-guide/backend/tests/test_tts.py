"""TTS-01..TTS-10 (mock ElevenLabs): chia đoạn, cache, lỗi/quota không làm chatbot chết."""
import pytest

from app.services.narration_service import clean_for_speech, split_for_tts
from tests.conftest import llm_json


def gen(client, text, lang="vi", **kw):
    return client.post("/api/narration/generate", json={"text": text, "language": lang, **kw})


@pytest.mark.parametrize("lang", ["vi", "en", "zh"])
def test_tts01_03_languages(client, lang):
    r = gen(client, f"Văn bản thử {lang}.", lang)
    assert r.status_code == 200 and r.json()["status"] == "ready"
    call = client.fake.tts_calls[-1]
    assert call["body"]["model_id"] == "eleven_flash_v2_5" and call["body"]["language_code"] == lang
    assert call["headers"]["xi-api-key"] == "test-eleven-key-123456" and "mp3" in call["url"]
    a = client.get(r.json()["audio_url"])
    assert a.status_code == 200 and a.headers["content-type"] == "audio/mpeg" and a.content.startswith(b"ID3")


def test_tts04_long_text_split():
    text = " ".join(f"Câu số {i} nói về cột cờ Hiền Lương và cây cầu hai màu." for i in range(60))
    segs = split_for_tts(text, 900)
    assert len(segs) > 1 and all(len(s) <= 900 for s in segs) and " ".join(segs).replace("  ", " ") == " ".join(text.split())
    long_one = "a " * 1500
    assert all(len(s) <= 900 for s in split_for_tts(long_one, 900))


def test_tts04_endpoint_segments(client):
    text = " ".join(f"Câu số {i} nói về cột cờ Hiền Lương." for i in range(80))
    j = gen(client, text).json()
    assert j["segments"] == len(client.fake.tts_calls) and j["segments"] > 1


def test_tts05_cache(client):
    a = gen(client, "Nội dung giống hệt để kiểm tra cache.").json()
    n = len(client.fake.tts_calls)
    b = gen(client, "Nội dung giống hệt để kiểm tra cache.").json()
    assert a["audio_id"] == b["audio_id"] and b["cached"] is True and len(client.fake.tts_calls) == n
    c = gen(client, "Nội dung giống hệt để kiểm tra cache.", "en").json()
    assert c["audio_id"] != a["audio_id"]


def test_tts_citation_markers_not_spoken(client):
    assert clean_for_speech("Cột cờ cao 12 m [S1][S2]. Xem [I1].") == "Cột cờ cao 12 m . Xem ."


def test_tts06_api_error_message(client):
    client.fake.tts_status = 500
    r = gen(client, "Văn bản lỗi riêng biệt 500.")
    assert r.status_code == 503 and r.json()["error"]["code"] == "tts_failed"


def test_tts07_quota_chatbot_still_works(client):
    client.fake.tts_status = 401
    r = gen(client, "Văn bản hết quota riêng biệt.")
    assert r.status_code == 503 and r.json()["error"]["code"] == "tts_quota_exceeded"
    client.fake.llm_script.append(llm_json("Cột cờ cao 12 m [S1]."))
    c = client.post("/api/chat", json={"message": "Ngày 8-10-1954 phía Bắc dựng cột cờ đầu tiên cao bao nhiêu mét?", "language": "vi"})
    assert c.status_code == 200 and c.json()["mode"] == "llm"


def test_api10_tts_key_missing(settings, fake):
    from fastapi.testclient import TestClient
    from pydantic import SecretStr
    from app.main import create_app
    s = settings.model_copy(update={"elevenlabs_api_key": SecretStr("")})
    with TestClient(create_app(s)) as c:
        r = c.post("/api/narration/generate", json={"text": "Xin chào", "language": "vi"})
        assert r.status_code == 503 and r.json()["error"]["code"] == "elevenlabs_key_missing"
        assert c.get("/api/health").json()["tts"]["configured"] is False


def test_audio_id_validation(client):
    assert client.get("/api/narration/..%2f..%2fetc%2fpasswd").status_code in (404, 422)
    assert client.get("/api/narration/" + "a" * 40).status_code == 404
    assert client.get("/api/narration/not-hex").status_code == 404


def test_language_code_fallback_on_422(client):
    calls = {"n": 0}
    import httpx
    def h(req):
        calls["n"] += 1
        import json
        if "language_code" in json.loads(req.content):
            return httpx.Response(422, json={"detail": "bad"})
        return httpx.Response(200, content=b"ID3OK")
    from app.services.tts_service import TTSService
    import asyncio
    t = TTSService(client.app.state.settings, transport=httpx.MockTransport(h))
    assert asyncio.run(t.synthesize("x", "vi")) == b"ID3OK" and calls["n"] == 2
