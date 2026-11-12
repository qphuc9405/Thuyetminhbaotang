"""Tiện ích văn bản: chuẩn hoá, bỏ dấu (để tìm kiếm chịu lỗi OCR dấu), tách từ, nhận diện ngôn ngữ."""
from __future__ import annotations

import re
import unicodedata

_VI_SPECIFIC = set("ăâêôơưđĂÂÊÔƠƯĐ")
_VI_TONE = re.compile("[̣̀́̃̉]")
_CJK = re.compile(r"[一-鿿]")
_EN_STOP = {"the", "of", "and", "why", "what", "when", "where", "who", "how", "was", "were", "is", "are", "did", "does",
            "in", "at", "to", "for", "on", "about", "between", "which", "tell", "me", "a", "an", "bridge", "river", "line"}
_VI_UNACCENTED = {"la", "cua", "khong", "nhu", "gi", "tai", "sao", "nao", "nhung", "duoc", "cac", "mot", "va", "trong",
                  "co", "den", "vi", "ve", "voi", "khi", "nam", "ai", "o", "dau", "bao", "gio", "the"}


def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s or "")


def fold(s: str) -> str:
    """Hạ chữ thường, bỏ dấu, đ→d. Dùng cho chỉ mục tìm kiếm (OCR hay sai dấu: Hiền/Hiển)."""
    s = (s or "").lower().replace("đ", "d").replace("Đ", "d")
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s


_TOKEN = re.compile(r"[a-z0-9]+")


def tokenize(folded: str) -> list[str]:
    return _TOKEN.findall(folded)


def detect_language(text: str) -> str:
    """vi | en | zh. Heuristic nhẹ, không phụ thuộc thư viện ngoài."""
    t = nfc(text or "")
    if not t.strip():
        return "vi"
    cjk = len(_CJK.findall(t))
    letters = sum(ch.isalpha() for ch in t) or 1
    if cjk / letters > 0.2:
        return "zh"
    if any(ch in _VI_SPECIFIC for ch in t) or _VI_TONE.search(unicodedata.normalize("NFD", t)):
        return "vi"
    toks = tokenize(t.lower())
    en = sum(1 for w in toks if w in _EN_STOP)
    vi = sum(1 for w in toks if w in _VI_UNACCENTED and w not in _EN_STOP)
    return "en" if en >= vi and en > 0 else ("vi" if vi else "en")


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[\.\!\?;”\"])\s+(?=[A-ZÀ-ỴĐ“\"(\[0-9])", text.replace("\n", " "))
    return [p.strip() for p in parts if p.strip()]
