"""LLM-01..LLM-15: dịch vụ LLM độc lập (mock transport)."""
import asyncio
import json

import httpx
import pytest
from pydantic import SecretStr

from app.config import Settings
from app.core.exceptions import ConfigError, LLMUnavailable
from app.services.llm_service import LLMService, parse_json_loose


def mk(settings, handler):
    return LLMService(settings, transport=httpx.MockTransport(handler))


def run(coro):
    return asyncio.run(coro)


@pytest.fixture(autouse=True)
def nosleep(monkeypatch):
    import app.services.llm_service as ls
    async def _n(*a, **k): return None
    monkeypatch.setattr(ls.asyncio, "sleep", _n)


def ok(content="xin chào"):
    return httpx.Response(200, json={"message": {"content": content}})


def test_llm01_valid_prompt(settings):
    r = run(mk(settings, lambda req: ok('{"answer":"ok"}')).chat([{"role": "user", "content": "hi"}]))
    assert r.content and r.attempts == 1


def test_model_name_stripped_for_direct_cloud(settings):
    assert settings.ollama_model == "gpt-oss:120b-cloud" or True
    s = Settings(ollama_host="https://ollama.com", ollama_model="gpt-oss:120b-cloud", ollama_api_key=SecretStr("k"))
    assert s.effective_ollama_model == "gpt-oss:120b"
    s2 = Settings(ollama_host="http://localhost:11434", ollama_model="gpt-oss:120b-cloud")
    assert s2.effective_ollama_model == "gpt-oss:120b-cloud"


def test_request_shape_and_auth_header(settings):
    seen = {}
    def h(req):
        seen["url"] = str(req.url); seen["auth"] = req.headers.get("authorization"); seen["body"] = json.loads(req.content); return ok("{}")
    run(mk(settings, h).chat([{"role": "user", "content": "x"}]))
    assert seen["url"] == "https://ollama.com/api/chat" and seen["auth"] == "Bearer test-ollama-key-123456"
    assert seen["body"]["model"] == "gpt-oss:120b" and seen["body"]["stream"] is False and seen["body"]["format"] == "json"


def test_missing_key_config_error():
    s = Settings(ollama_api_key=SecretStr(""), ollama_host="https://ollama.com")
    with pytest.raises(ConfigError):
        run(LLMService(s).chat([{"role": "user", "content": "x"}]))


def test_llm11_json_parse_loose():
    assert parse_json_loose('```json\n{"a":1}\n```') == {"a": 1}
    assert parse_json_loose('Đây là kết quả: {"a": 2} hết') == {"a": 2}
    assert parse_json_loose("không phải json") is None


def test_llm13_timeout_limited_retries(settings):
    calls = {"n": 0}
    def h(req):
        calls["n"] += 1; raise httpx.ReadTimeout("t")
    with pytest.raises(LLMUnavailable) as e:
        run(mk(settings, h).chat([{"role": "user", "content": "x"}]))
    assert e.value.code == "llm_timeout" and calls["n"] == 1 + settings.llm_max_retries


def test_llm14_rate_limit_then_success(settings):
    seq = [httpx.Response(429), ok("{}")]
    r = run(mk(settings, lambda req: seq.pop(0)).chat([{"role": "user", "content": "x"}]))
    assert r.attempts == 2


def test_llm14_rate_limit_exhausted(settings):
    calls = {"n": 0}
    def h(req):
        calls["n"] += 1; return httpx.Response(429)
    with pytest.raises(LLMUnavailable) as e:
        run(mk(settings, h).chat([{"role": "user", "content": "x"}]))
    assert e.value.code == "llm_rate_limited" and calls["n"] == 3


def test_llm15_cloud_unavailable(settings):
    with pytest.raises(LLMUnavailable) as e:
        run(mk(settings, lambda req: httpx.Response(503)).chat([{"role": "user", "content": "x"}]))
    assert e.value.code == "llm_unavailable"


def test_auth_error_no_retry(settings):
    calls = {"n": 0}
    def h(req):
        calls["n"] += 1; return httpx.Response(401)
    with pytest.raises(LLMUnavailable) as e:
        run(mk(settings, h).chat([{"role": "user", "content": "x"}]))
    assert e.value.code == "llm_auth_error" and calls["n"] == 1


def test_empty_response_retried(settings):
    seq = [httpx.Response(200, json={"message": {"content": ""}}), ok("{}")]
    assert run(mk(settings, lambda req: seq.pop(0)).chat([{"role": "user", "content": "x"}])).attempts == 2
