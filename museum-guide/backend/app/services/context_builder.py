"""Dựng context cho LLM: đoạn văn kèm nguồn/trang/trạng thái xác minh + metadata ảnh. Tài liệu truy xuất là DỮ LIỆU,
không phải chỉ thị: nội dung bị gói trong thẻ và các dòng giống chỉ thị bị vô hiệu hoá."""
from __future__ import annotations

from dataclasses import dataclass

from ..core.security import looks_like_injection, neutralize_context


@dataclass
class BuiltContext:
    text: str
    source_map: dict  # "S1" -> chunk dict
    image_map: dict   # "I1" -> image dict
    truncated: bool
    injection_flags: list


def _page_label(c: dict) -> str:
    if c.get("printed_page") is None:
        return c.get("provision") or "n/a"
    a, b = c["printed_page"], c.get("printed_page_end") or c["printed_page"]
    return f"tr.{a}" if a == b else f"tr.{a}–{b}"


def build_context(chunks: list[dict], images: list[dict], *, max_chars: int = 7000, compact: bool = False) -> BuiltContext:
    parts, smap, imap, flags = [], {}, {}, []
    used, truncated = 0, False
    for i, c in enumerate(chunks, 1):
        sid = f"S{i}"
        if looks_like_injection(c["content"]):
            flags.append(c["chunk_id"])
        body = neutralize_context(c["content"])
        if compact and len(body) > 900:
            end = body.rfind(". ", 450, 900)
            body = body[:end + 1 if end >= 0 else 900]
            c = {**c, "content": body}
            truncated = True
        head = (f"[{sid}] nguồn={c['source_id']} | loại={c['source_type']} | tài liệu=\"{c['source_title']}\" | vị trí={_page_label(c)}"
                f" | chương=\"{c.get('chapter') or '-'}\" | xác minh={c.get('verification_status')}")
        if compact:
            head = f"[{sid}] {c['source_type']} | {c['source_title']} | {_page_label(c)} | {c.get('verification_status')}"
        block = f"<doc id=\"{sid}\">\n{head}\n{body}\n</doc>"
        if used + len(block) > max_chars and smap:
            truncated = True
            break
        parts.append(block); used += len(block); smap[sid] = c
    for j, im in enumerate(images, 1):
        iid = f"I{j}"
        cap = ""
        if im.get("caption"):
            st = im.get("caption_status") or ""
            where = f"chú thích trong bài {st.split(':')[1]}" if st.startswith("document_caption") else "chú thích sách"
            cap = f" | {where}=\"{im['caption']}\""
        if (im.get("metadata_basis") or {}).get("title") == "filename":
            cap += " | tiêu đề/thời gian/địa điểm theo mô tả đi kèm ảnh (CHƯA xác minh – khi nhắc phải nói rõ là chưa xác minh, không nhận dạng người)"
        block = (f"<img id=\"{iid}\">\n[{iid}] ảnh={im['image_id']} | tiêu đề=\"{im['title']}\" | thời gian={im['time_period']} | địa điểm=\"{im['location']}\" (độ chắc chắn: {im['location_confidence']})"
                 f"{cap}\nMô tả nhìn thấy: {im['visual_description'][:420]}\n</img>")
        if compact:
            block = f'<img id="{iid}">[{iid}] {im["title"]} | {im["time_period"]}. Không suy đoán người hoặc niên đại ảnh.</img>'
        if used + len(block) > max_chars + 1500:
            truncated = True
            break
        parts.append(block); used += len(block); imap[iid] = im
    if not smap:
        parts.append("(KHÔNG có đoạn tư liệu liên quan nào được truy xuất.)")
    return BuiltContext("\n".join(parts), smap, imap, truncated, flags)
