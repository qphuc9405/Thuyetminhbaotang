"""Các hàm an toàn đầu vào: chặn đường dẫn tuỳ ý, trung hoà prompt-injection trong tài liệu truy xuất."""
from __future__ import annotations

import re
from pathlib import Path

# Các mẫu thường gặp của chỉ thị tiêm vào (vi/en/zh). Dùng để GẮN CỜ, không để thực thi.
INJECTION_PATTERNS = [
    r"ignore (all |any )?(the )?(previous|prior|above) (instructions|prompts?)",
    r"disregard (all |any )?(the )?(previous|prior|above)",
    r"(reveal|show|print|leak).{0,30}(system prompt|api key|secret)",
    r"you are now",
    r"bỏ qua (tất cả |mọi )?(các )?(chỉ thị|hướng dẫn|lệnh)",
    r"tiết lộ.{0,20}(system prompt|api key|khóa|khoá|mật khẩu)",
    r"忽略(之前|以上|所有).{0,6}(指令|提示)",
    r"(泄露|透露).{0,10}(系统提示|密钥)",
]
_INJ = re.compile("|".join(INJECTION_PATTERNS), re.I)


def looks_like_injection(text: str) -> bool:
    return bool(_INJ.search(text or ""))


def neutralize_context(text: str) -> str:
    """Làm mờ các dòng giống chỉ thị trong tài liệu truy xuất (vẫn giữ nội dung để trích dẫn)."""
    out = []
    for line in (text or "").splitlines():
        out.append("[nội dung giống chỉ thị đã bị vô hiệu hoá] " + line if _INJ.search(line) else line)
    return "\n".join(out)


def safe_join(root: str | Path, relative: str) -> Path:
    """Ghép đường dẫn và đảm bảo kết quả nằm trong `root` (chống path traversal)."""
    root_p = Path(root).resolve()
    p = (root_p / relative).resolve()
    if root_p != p and root_p not in p.parents:
        raise ValueError("Đường dẫn nằm ngoài thư mục cho phép")
    return p


ALLOWED_IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp"}
