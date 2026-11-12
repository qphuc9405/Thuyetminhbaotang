"""ElevenLabs Text-to-Speech – dịch vụ độc lập. Lỗi TTS KHÔNG được làm chatbot ngừng hoạt động.
Model ưu tiên eleven_flash_v2_5 (32 ngôn ngữ gồm vi/en/zh; giới hạn 40.000 ký tự/lần gọi; 0,5 credit/ký tự).
Gói Free: không dùng được Voice Library qua API → dùng giọng premade (voice_id cấu hình theo ngôn ngữ)."""
from __future__ import annotations

import logging

import httpx

from ..config import Settings
from ..core.exceptions import ConfigError, TTSUnavailable

log = logging.getLogger(__name__)
API = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"


class TTSService:
    def __init__(self, settings: Settings, transport: httpx.AsyncBaseTransport | None = None):
        self.s = settings
        self._transport = transport

    def available(self) -> bool:
        return bool(self.s.elevenlabs_api_key.get_secret_value())

    async def synthesize(self, text: str, language: str, voice_id: str | None = None) -> bytes:
        key = self.s.elevenlabs_api_key.get_secret_value()
        if not key:
            raise ConfigError("Chưa cấu hình ELEVENLABS_API_KEY.", code="elevenlabs_key_missing")
        voice = voice_id or self.s.voice_for(language)
        url = API.format(voice_id=voice)
        params = {"output_format": "mp3_44100_128"}
        headers = {"xi-api-key": key, "Content-Type": "application/json", "Accept": "audio/mpeg"}
        body = {"text": text, "model_id": self.s.elevenlabs_model, "language_code": language}
        async with httpx.AsyncClient(timeout=self.s.tts_timeout_s, transport=self._transport) as client:
            for attempt in (1, 2):
                try:
                    r = await client.post(url, params=params, headers=headers, json=body)
                except httpx.TimeoutException:
                    raise TTSUnavailable("Dịch vụ giọng nói quá thời gian chờ.", code="tts_timeout")
                except httpx.HTTPError:
                    raise TTSUnavailable("Không kết nối được dịch vụ giọng nói.", code="tts_network_error")
                if r.status_code == 200 and r.content:
                    return r.content
                if r.status_code in (400, 422) and "language_code" in body and attempt == 1:
                    body.pop("language_code")  # một số voice/model không chấp nhận language_code → thử lại không có
                    continue
                self._raise(r)
        raise TTSUnavailable("Tạo giọng nói thất bại.", code="tts_failed")

    @staticmethod
    def _raise(r: httpx.Response) -> None:
        detail = ""
        try:
            d = r.json().get("detail")
            detail = (d.get("status") if isinstance(d, dict) else str(d or ""))[:80]
        except Exception:
            pass
        if r.status_code == 401:
            if "quota" in detail.lower():
                raise TTSUnavailable("Đã hết hạn mức ký tự (quota) ElevenLabs.", code="tts_quota_exceeded")
            raise TTSUnavailable("Khoá ElevenLabs không hợp lệ hoặc không có quyền.", code="tts_auth_error")
        if r.status_code == 429:
            raise TTSUnavailable("Dịch vụ giọng nói đang quá tải/giới hạn tốc độ.", code="tts_rate_limited")
        raise TTSUnavailable(f"Dịch vụ giọng nói trả lỗi {r.status_code}.", code="tts_failed")
