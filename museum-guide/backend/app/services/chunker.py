"""Chia văn bản sách thành chunk theo cấu trúc (trang → khối/đoạn → câu), có overlap, cấu hình được.

Quy trình: (1) dựng danh sách đoạn từ OCR từng trang (bỏ số trang, lọc chú thích-trích dẫn thuần);
(2) nối đoạn bị ngắt qua dòng/trang; (3) nhận diện đề mục đánh số; (4) đóng gói đoạn vào chunk <= max_chars,
đoạn quá dài tách theo câu; overlap = các câu cuối của chunk trước (<= overlap_chars).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from .text_utils import nfc, split_sentences

_CITATION = re.compile(r"(sđd|sđđ|Nxb|NXB|tr\.\s*\d|Trung tâm Lưu trữ|Tldd|tlđd|kí hiệu|kí hiệu|Phông|Hồ sơ số|Tp\. ?HCM|Tp\. Hồ Chí Minh)", re.I)
_FOOTNOTE_START = re.compile(r"^\s*[\dIl]{1,2}[\s_\.\-\)]+\S")
_SECTION = re.compile(r"^\s*(\d{1,2}(\.\d{1,2})?\.\s+[A-ZĐÀ-ỴẮẰẲẴẶÂẦẤẨẪẬÊỀẾỂỄỆÔỒỐỔỖỘƠỜỚỞỠỢƯỪỨỬỮỰ][^\n]{6,160})$")
_END_PUNCT = re.compile(r"[\.\!\?:;”\"’\)…\]]\s*[\d\)\]]*\s*$")


@dataclass
class Paragraph:
    text: str
    pdf_pages: list[int]
    printed_pages: list[int]
    chapter_id: str | None
    section: str | None = None
    is_heading: bool = False
    needs_review: bool = False


@dataclass
class ChunkSpec:
    text: str
    pdf_page: int
    pdf_page_end: int
    printed_page: int
    printed_page_end: int
    chapter_id: str | None
    section: str | None
    needs_review: bool
    n_paragraphs: int = 0
    extra: dict = field(default_factory=dict)


def _is_citation_only_footnote(block: str) -> bool:
    return bool(_FOOTNOTE_START.match(block)) and bool(_CITATION.search(block)) and "%" not in block and len(block) < 380


def build_paragraphs(pages: list[dict], *, include_footnotes: bool = False) -> tuple[list[Paragraph], dict]:
    """pages: [{pdf_page, printed_page, chapter_id, ocr_text, needs_review, is_blank}] theo thứ tự đọc."""
    paras: list[Paragraph] = []
    stats = {"footnote_blocks_excluded": 0, "page_number_lines_dropped": 0, "merged_across_blocks": 0}
    cur_section: dict[str | None, str | None] = {}
    for pg in pages:
        if pg.get("is_blank"):
            continue
        blocks = [b.strip() for b in re.split(r"\n\s*\n", nfc(pg["ocr_text"])) if b.strip()]
        for b in blocks:
            if re.fullmatch(r"\d{1,3}", b):
                stats["page_number_lines_dropped"] += 1
                continue
            b1 = re.sub(r"\s*\n\s*", " ", b).strip()
            if not include_footnotes and _is_citation_only_footnote(b1):
                stats["footnote_blocks_excluded"] += 1
                continue
            # dòng cuối của khối có thể là số trang dính
            b1 = re.sub(r"\s+\d{1,3}$", "", b1) if re.search(r"[\.\!\?”\"]\s+\d{1,3}$", b1) else b1
            ch = pg.get("chapter_id")
            m = _SECTION.match(b1)
            heading = bool(m) and len(b1) < 200
            if heading:
                cur_section[ch] = b1
            can_merge = (
                paras and not heading and not paras[-1].is_heading and paras[-1].chapter_id == ch
                and not _END_PUNCT.search(paras[-1].text) and b1[:1].islower()
            )
            if can_merge:
                p = paras[-1]
                p.text = p.text + " " + b1
                if pg["pdf_page"] not in p.pdf_pages:
                    p.pdf_pages.append(pg["pdf_page"])
                if pg["printed_page"] not in p.printed_pages:
                    p.printed_pages.append(pg["printed_page"])
                p.needs_review = p.needs_review or pg.get("needs_review", False)
                stats["merged_across_blocks"] += 1
            else:
                paras.append(Paragraph(text=b1, pdf_pages=[pg["pdf_page"]], printed_pages=[pg["printed_page"]], chapter_id=ch,
                                       section=cur_section.get(ch), is_heading=heading, needs_review=pg.get("needs_review", False)))
    return paras, stats


def make_chunks(paras: list[Paragraph], *, max_chars: int = 900, overlap_chars: int = 150, min_chars: int = 120) -> list[ChunkSpec]:
    """Đóng gói đoạn thành chunk; không trộn chương; đoạn dài tách theo câu."""
    units: list[tuple[str, Paragraph]] = []
    for p in paras:
        if len(p.text) <= max_chars:
            units.append((p.text, p))
        else:
            cur = ""
            for s in split_sentences(p.text):
                if cur and len(cur) + 1 + len(s) > max_chars:
                    units.append((cur, p)); cur = s
                else:
                    cur = (cur + " " + s).strip()
            if cur:
                units.append((cur, p))
    chunks: list[ChunkSpec] = []
    buf: list[tuple[str, Paragraph]] = []

    def flush(carry: list[tuple[str, Paragraph]] | None = None):
        nonlocal buf
        if not buf:
            return
        text = "\n".join(t for t, _ in buf).strip()
        ps = [p for _, p in buf]
        pdfs = sorted({x for p in ps for x in p.pdf_pages}); prs = sorted({x for p in ps for x in p.printed_pages})
        sec = next((p.section for p in reversed(ps) if p.section), None)
        chunks.append(ChunkSpec(text=text, pdf_page=pdfs[0], pdf_page_end=pdfs[-1], printed_page=prs[0], printed_page_end=prs[-1],
                                chapter_id=ps[0].chapter_id, section=sec, needs_review=any(p.needs_review for p in ps), n_paragraphs=len(ps)))
        buf = []

    cur_len = 0
    cur_ch = None
    for text, p in units:
        if buf and (p.chapter_id != cur_ch or cur_len + len(text) + 1 > max_chars):
            prev_text = "\n".join(t for t, _ in buf)
            prev_last = buf[-1][1]
            same_chapter = p.chapter_id == cur_ch
            flush()
            buf = []
            if same_chapter and overlap_chars > 0:
                tail, acc = [], 0
                for s in reversed(split_sentences(prev_text)):
                    if acc + len(s) > overlap_chars and tail:
                        break
                    tail.insert(0, s); acc += len(s) + 1
                    if acc > overlap_chars:
                        break
                if tail:
                    buf.append((" ".join(tail), prev_last))  # overlap giữ đúng trang gốc của đoạn trước
            cur_len = sum(len(t) + 1 for t, _ in buf)
        cur_ch = p.chapter_id
        buf.append((text, p))
        cur_len += len(text) + 1
    flush()
    # gộp chunk quá ngắn vào chunk trước cùng chương
    merged: list[ChunkSpec] = []
    for c in chunks:
        if merged and len(c.text) < min_chars and merged[-1].chapter_id == c.chapter_id:
            m = merged[-1]
            m.text += "\n" + c.text
            m.pdf_page_end = max(m.pdf_page_end, c.pdf_page_end); m.printed_page_end = max(m.printed_page_end, c.printed_page_end)
            m.needs_review = m.needs_review or c.needs_review
        else:
            merged.append(c)
    return merged
