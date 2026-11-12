from __future__ import annotations


class AppError(Exception):
    status_code = 500
    code = "internal_error"

    def __init__(self, message: str, *, code: str | None = None):
        super().__init__(message)
        self.message = message
        if code:
            self.code = code


class ConfigError(AppError):
    status_code = 503
    code = "config_missing"


class LLMUnavailable(AppError):
    status_code = 503
    code = "llm_unavailable"


class TTSUnavailable(AppError):
    status_code = 503
    code = "tts_unavailable"


class NotFound(AppError):
    status_code = 404
    code = "not_found"
