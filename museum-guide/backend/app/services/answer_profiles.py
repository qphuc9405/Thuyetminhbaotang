"""Hồ sơ trả lời theo loại câu hỏi: quyết định top_k, mở rộng đoạn lân cận, độ dài mục tiêu, giới hạn context và token.

Lý do: câu hỏi tra cứu một con số cần câu trả lời gọn; câu hỏi "kể lại câu chuyện 1954–1967" cần nhiều tư liệu
hơn (nhiều chương, nhiều trang) và đầu ra dài hơn. Độ dài là MỤC TIÊU THAM KHẢO, không phải yêu cầu viết thêm chữ:
nếu tư liệu không đủ, mô hình phải dừng và nói rõ giới hạn.
"""
from __future__ import annotations

import re
from dataclasses import replace
from dataclasses import dataclass


@dataclass(frozen=True)
class Profile:
    kind: str           # simple | event | entity | period | story
    top_k: int          # số đoạn lấy từ bộ truy xuất
    expand: int         # số kết quả đầu được bổ sung đoạn liền kề (cùng chương)
    words: tuple        # (min, max) số từ mục tiêu
    max_context: int    # ký tự context tối đa
    max_tokens: int     # num_predict cho LLM
    chronological: bool  # sắp context theo trang (kể chuyện theo thời gian)


PROFILES = {
    "simple": Profile("simple", 6, 0, (100, 180), 7000, 1100, False),
    "event": Profile("event", 8, 2, (200, 350), 12000, 1800, False),
    "entity": Profile("entity", 8, 2, (200, 350), 12000, 1800, False),
    "period": Profile("period", 10, 3, (350, 550), 13000, 2600, True),
    "story": Profile("story", 12, 4, (450, 700), 16000, 3400, True),
}

_STORY = re.compile(r"(kể|câu chuyện|toàn bộ|từ đầu|thuyết minh cho|tell me the story|tell the story|narrate|whole story|walk me through|讲述|故事|讲一讲|介绍一下.*历史)", re.I)
_PERIOD = re.compile(r"(giai đoạn|thời kỳ|thời kì|so sánh|phân tích|từ năm \d{4} đến|\d{4}\s*[–-]\s*\d{4}|period|compare|analy[sz]e|between \d{4} and|时期|阶段|比较|分析)", re.I)
_SIMPLE = re.compile(r"(bao nhiêu|khi nào|ngày nào|năm nào|mấy giờ|ở đâu|là ai|how many|how much|how tall|how wide|when |what year|where |多少|几|何时|哪一年|哪里|多高|多宽)", re.I)
_EVENT = re.compile(r"(sự kiện|vụ |diễn ra|diễn biến|chuyện gì|xảy ra|what happened|event|incident|事件|发生)", re.I)
_DEEP = re.compile(r"(chi tiết|kỹ hơn|kĩ hơn|sâu|giải thích|vì sao|tại sao|ý nghĩa|in detail|explain|why|significance|详细|为什么|意义|解释)", re.I)
_AUDIENCE_KID = re.compile(r"(học sinh|trẻ em|chưa biết|đơn giản|for a student|for kids|simple terms|学生|孩子|简单)", re.I)
_AUDIENCE_TOUR = re.compile(r"(đoàn khách|khách tham quan|như đang thuyết minh|tour group|visitors|游客|讲解)", re.I)


def classify(message: str) -> Profile:
    m = message.strip()
    if _STORY.search(m):
        return PROFILES["story"]
    if _PERIOD.search(m):
        return PROFILES["period"]
    if _SIMPLE.search(m) and not _DEEP.search(m):
        return PROFILES["simple"]
    if _EVENT.search(m) or re.search(r"\d{1,2}[-/]\d{1,2}[-/]\d{4}", m):
        return PROFILES["event"]
    if _DEEP.search(m):
        return PROFILES["entity"]
    return PROFILES["entity"] if len(m.split()) > 6 else PROFILES["simple"]


def audience(message: str) -> str:
    if _AUDIENCE_KID.search(message):
        return "student"
    if _AUDIENCE_TOUR.search(message):
        return "tour"
    return "general"


def local_profile(profile: Profile, message: str) -> Profile:
    """CPU local: câu thông thường ngắn; vẫn giữ dư địa cho yêu cầu phân tích/kể chuyện."""
    detailed = profile.kind in {"story", "period"} or bool(_DEEP.search(message))
    return replace(profile, top_k=5 if detailed else 3, expand=0,
                   words=(120, 180) if detailed else (45, 80),
                   max_context=5000 if detailed else 2400,
                   max_tokens=850 if detailed else 400)
