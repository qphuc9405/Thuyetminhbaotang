"""LLM Service độc lập (thay model chỉ cần đổi config). Gọi Ollama Cloud trực tiếp qua httpx.

- Endpoint: POST {OLLAMA_HOST}/api/chat, header Authorization: Bearer <OLLAMA_API_KEY> (theo docs.ollama.com/cloud).
- Gọi trực tiếp https://ollama.com dùng tên model KHÔNG có hậu tố '-cloud' (config.effective_ollama_model xử lý).
- Timeout, retry có giới hạn (429/5xx/timeout, tôn trọng Retry-After), lỗi xác thực → thông báo rõ, không ghi bí mật vào log."""
from __future__ import annotations

import asyncio
import json
import logging
import random
import re
import time
from dataclasses import dataclass

import httpx

from ..config import Settings
from ..core.exceptions import ConfigError, LLMUnavailable

log = logging.getLogger(__name__)


@dataclass
class LLMResult:
    content: str
    model: str
    elapsed_ms: int
    attempts: int
    thinking: str | None = None


class LLMService:
    def __init__(self, settings: Settings, transport: httpx.AsyncBaseTransport | None = None):
        self.s = settings
        self._transport = transport  # tiêm mock transport cho unit test (không tốn quota)

    @property
    def model(self) -> str:
        return self.s.effective_ollama_model

    def _check_config(self) -> None:
        direct_cloud = self.s.ollama_host.rstrip("/").endswith("ollama.com")
        if direct_cloud and not self.s.ollama_api_key.get_secret_value():
            raise ConfigError("Chưa cấu hình OLLAMA_API_KEY (tạo tại https://ollama.com/settings/keys).", code="ollama_key_missing")

    async def chat(self, messages: list[dict], *, json_mode: bool = True, temperature: float = 0.1, max_tokens: int = 1200) -> LLMResult:
        self._check_config()
        url = self.s.ollama_host.rstrip("/") + "/api/chat"
        headers = {"Content-Type": "application/json"}
        key = self.s.ollama_api_key.get_secret_value()
        if key:
            headers["Authorization"] = f"Bearer {key}"
        body = {"model": self.model, "messages": messages, "stream": False,
                "options": {"temperature": temperature, "num_predict": max_tokens}}
        if json_mode:
            body["format"] = "json"
        if self.s.local_llm:
            body["keep_alive"] = "30m"
        t0 = time.perf_counter()
        last_err = "unknown"
        max_attempts = 1 + max(0, self.s.llm_max_retries)
        async with httpx.AsyncClient(timeout=self.s.llm_timeout_s, transport=self._transport) as client:
            for attempt in range(1, max_attempts + 1):
                try:
                    r = await client.post(url, headers=headers, json=body)
                except httpx.TimeoutException:
                    last_err = "timeout"
                except httpx.HTTPError as e:
                    last_err = f"network_error:{type(e).__name__}"
                else:
                    if r.status_code == 200:
                        data = r.json()
                        msg = data.get("message", {}) or {}
                        content = (msg.get("content") or "").strip()
                        if not content:
                            last_err = "empty_response"
                        else:
                            return LLMResult(content=content, model=self.model, elapsed_ms=int((time.perf_counter() - t0) * 1000),
                                             attempts=attempt, thinking=msg.get("thinking"))
                    elif r.status_code in (401, 403):
                        raise LLMUnavailable("Xác thực Ollama Cloud thất bại (kiểm tra OLLAMA_API_KEY).", code="llm_auth_error")
                    elif r.status_code == 404:
                        raise LLMUnavailable(f"Model '{self.model}' không tồn tại trên máy chủ Ollama.", code="llm_model_not_found")
                    elif r.status_code == 429 or r.status_code >= 500:
                        last_err = f"http_{r.status_code}"
                        ra = r.headers.get("Retry-After")
                        if ra and ra.isdigit() and attempt < max_attempts:
                            await asyncio.sleep(min(10, int(ra)))
                            continue
                    else:
                        raise LLMUnavailable(f"Ollama trả mã lỗi {r.status_code}.", code="llm_bad_request")
                if attempt < max_attempts:
                    await asyncio.sleep(min(8, 0.8 * (2 ** (attempt - 1))) + random.random() * 0.2)
        log.warning("LLM không khả dụng sau %d lần thử: %s", max_attempts, last_err)
        code = "llm_rate_limited" if last_err == "http_429" else ("llm_timeout" if last_err == "timeout" else "llm_unavailable")
        raise LLMUnavailable("Dịch vụ mô hình AI tạm thời không khả dụng.", code=code)


def parse_json_loose(text: str) -> dict | None:
    """Parse JSON do LLM trả về; chấp nhận bọc ```json hoặc có chữ thừa."""
    t = text.strip()
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", t, flags=re.I)
    try:
        v = json.loads(t)
        return v if isinstance(v, dict) else None
    except Exception:
        m = re.search(r"\{.*\}", t, re.S)
        if m:
            try:
                v = json.loads(m.group(0))
                return v if isinstance(v, dict) else None
            except Exception:
                return None
    return None
