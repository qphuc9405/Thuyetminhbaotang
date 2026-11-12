"""Lược đồ cơ sở tri thức. Sách, ảnh, sự kiện, chủ đề liên kết qua bảng `relations` (cạnh có kiểu + căn cứ)."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Source(Base):
    __tablename__ = "sources"
    source_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    title: Mapped[str] = mapped_column(Text)
    author: Mapped[str | None] = mapped_column(Text, nullable=True)
    publisher: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_type: Mapped[str] = mapped_column(String(32))  # BOOK | HISTORICAL_DOCUMENT | ARCHIVAL_PHOTO | ACADEMIC_RESEARCH | MUSEUM_DESCRIPTION | REFERENCE_WORK
    classification: Mapped[str] = mapped_column(String(32))  # primary | secondary | research | reference
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    language: Mapped[str] = mapped_column(String(8), default="vi")
    document_date: Mapped[str | None] = mapped_column(String(32), nullable=True)
    accessed_date: Mapped[str | None] = mapped_column(String(16), nullable=True)
    relevant_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    relevant_provisions: Mapped[str | None] = mapped_column(Text, nullable=True)
    access_status: Mapped[str] = mapped_column(String(64), default="accessed")
    verification_status: Mapped[str] = mapped_column(String(64), default="unverified")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class Chapter(Base):
    __tablename__ = "chapters"
    chapter_id: Mapped[str] = mapped_column(String(16), primary_key=True)
    order: Mapped[int] = mapped_column(Integer)
    part: Mapped[str | None] = mapped_column(String(64), nullable=True)
    title_vi: Mapped[str] = mapped_column(Text)
    title_en: Mapped[str] = mapped_column(Text)
    title_zh: Mapped[str] = mapped_column(Text)
    printed_start: Mapped[int] = mapped_column(Integer)
    printed_end: Mapped[int] = mapped_column(Integer)
    topic_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    period_scope: Mapped[str | None] = mapped_column(Text, nullable=True)


class Page(Base):
    __tablename__ = "pages"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_id: Mapped[str] = mapped_column(ForeignKey("sources.source_id"))
    pdf_page: Mapped[int] = mapped_column(Integer, index=True)
    side: Mapped[str] = mapped_column(String(8))  # left | right (mỗi trang PDF là 1 spread 2 trang sách)
    printed_page: Mapped[int] = mapped_column(Integer, index=True)  # = 2*pdf-1 (trái) | 2*pdf (phải)
    printed_page_detected: Mapped[int | None] = mapped_column(Integer, nullable=True)
    printed_page_agrees: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    chapter_id: Mapped[str | None] = mapped_column(ForeignKey("chapters.chapter_id"), nullable=True)
    ocr_text: Mapped[str] = mapped_column(Text)
    direct_text: Mapped[str] = mapped_column(Text, default="")
    word_count: Mapped[int] = mapped_column(Integer, default=0)
    ocr_mean_conf: Mapped[float | None] = mapped_column(Float, nullable=True)
    low_conf_words: Mapped[int] = mapped_column(Integer, default=0)
    needs_review: Mapped[bool] = mapped_column(Boolean, default=False)
    is_blank: Mapped[bool] = mapped_column(Boolean, default=False)
    page_image: Mapped[str | None] = mapped_column(Text, nullable=True)


class Chunk(Base):
    """Bản ghi tri thức (Knowledge Record, mục 9.1) – đồng thời là đơn vị truy xuất RAG."""
    __tablename__ = "chunks"
    chunk_id: Mapped[str] = mapped_column(String(48), primary_key=True)
    source_id: Mapped[str] = mapped_column(ForeignKey("sources.source_id"), index=True)
    source_title: Mapped[str] = mapped_column(Text)
    source_type: Mapped[str] = mapped_column(String(32))
    language: Mapped[str] = mapped_column(String(8))
    title: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(64))
    chapter_id: Mapped[str | None] = mapped_column(String(16), nullable=True, index=True)
    chapter: Mapped[str | None] = mapped_column(Text, nullable=True)
    section: Mapped[str | None] = mapped_column(Text, nullable=True)
    pdf_page: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pdf_page_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    printed_page: Mapped[int | None] = mapped_column(Integer, nullable=True)
    printed_page_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    provision: Mapped[str | None] = mapped_column(String(64), nullable=True)  # Điều/đoạn (văn kiện ngoài)
    content: Mapped[str] = mapped_column(Text)
    folded: Mapped[str] = mapped_column(Text)
    event_date: Mapped[str | None] = mapped_column(String(16), nullable=True)
    image_ids: Mapped[list] = mapped_column(JSON, default=list)
    keywords: Mapped[list] = mapped_column(JSON, default=list)
    confidence: Mapped[str] = mapped_column(String(16), default="medium")
    verification_status: Mapped[str] = mapped_column(String(64), default="ocr_unverified")
    needs_review: Mapped[bool] = mapped_column(Boolean, default=False)
    config_id: Mapped[str] = mapped_column(String(32), default="default")
    __table_args__ = (Index("ix_chunks_pages", "source_id", "printed_page"),)


class Image(Base):
    __tablename__ = "images"
    image_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    kind: Mapped[str] = mapped_column(String(24))  # archive_photo | book_figure | cover_design | contemporary_photo
    source_id: Mapped[str | None] = mapped_column(String(32), nullable=True)  # SRC001 (hình sách) | SRC002 | SRC006 …
    filename_title: Mapped[str | None] = mapped_column(Text, nullable=True)  # tiêu đề suy từ tên file (CHƯA xác minh)
    metadata_basis: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # trường -> căn cứ (filename | visual_inspection | document_caption …)
    filename: Mapped[str] = mapped_column(Text)
    image_path: Mapped[str] = mapped_column(Text)  # tương đối so với thư mục dự án
    title: Mapped[str] = mapped_column(Text)
    title_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    title_zh: Mapped[str | None] = mapped_column(Text, nullable=True)
    visual_description: Mapped[str] = mapped_column(Text)
    historical_context: Mapped[str] = mapped_column(Text)
    location: Mapped[str] = mapped_column(Text)
    location_confidence: Mapped[str] = mapped_column(String(16), default="low")
    time_period: Mapped[str] = mapped_column(String(64), default="Chưa xác định")
    estimated_date: Mapped[str] = mapped_column(String(64), default="Chưa xác định")
    main_objects: Mapped[list] = mapped_column(JSON, default=list)
    visible_text: Mapped[list] = mapped_column(JSON, default=list)
    people_description: Mapped[str] = mapped_column(Text, default="")
    historical_significance: Mapped[str] = mapped_column(Text, default="")
    related_events: Mapped[list] = mapped_column(JSON, default=list)
    related_book_topics: Mapped[list] = mapped_column(JSON, default=list)
    related_book_pages: Mapped[list] = mapped_column(JSON, default=list)  # [{start,end,link_type}]
    keywords: Mapped[list] = mapped_column(JSON, default=list)
    source: Mapped[str] = mapped_column(Text, default="")
    watermarks: Mapped[list] = mapped_column(JSON, default=list)
    rights_status: Mapped[str] = mapped_column(String(64), default="Chưa xác định")
    confidence_level: Mapped[str] = mapped_column(String(16), default="low")
    verification_notes: Mapped[str] = mapped_column(Text, default="")
    duplicate_group: Mapped[str | None] = mapped_column(String(32), nullable=True)
    similar_scene_group: Mapped[str | None] = mapped_column(String(32), nullable=True)
    sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    phash: Mapped[str | None] = mapped_column(String(32), nullable=True)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    file_format: Mapped[str | None] = mapped_column(String(16), nullable=True)
    pdf_page: Mapped[int | None] = mapped_column(Integer, nullable=True)
    printed_page: Mapped[int | None] = mapped_column(Integer, nullable=True)
    bbox: Mapped[list | None] = mapped_column(JSON, nullable=True)
    caption: Mapped[str | None] = mapped_column(Text, nullable=True)
    caption_status: Mapped[str | None] = mapped_column(String(64), nullable=True)
    in_gallery: Mapped[bool] = mapped_column(Boolean, default=True)
    search_text: Mapped[str] = mapped_column(Text, default="")


class Topic(Base):
    __tablename__ = "topics"
    topic_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    order: Mapped[int] = mapped_column(Integer)
    title_vi: Mapped[str] = mapped_column(Text)
    title_en: Mapped[str] = mapped_column(Text)
    title_zh: Mapped[str] = mapped_column(Text)
    description_vi: Mapped[str] = mapped_column(Text)
    chapter_ids: Mapped[list] = mapped_column(JSON, default=list)
    printed_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    printed_end: Mapped[int | None] = mapped_column(Integer, nullable=True)


class Event(Base):
    __tablename__ = "events"
    event_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    date_iso: Mapped[str] = mapped_column(String(16), index=True)  # YYYY | YYYY-MM | YYYY-MM-DD
    date_label: Mapped[str] = mapped_column(String(32))
    title_vi: Mapped[str] = mapped_column(Text)
    title_en: Mapped[str] = mapped_column(Text)
    title_zh: Mapped[str] = mapped_column(Text)
    summary_vi: Mapped[str] = mapped_column(Text)
    summary_en: Mapped[str] = mapped_column(Text)
    period: Mapped[str] = mapped_column(String(24))  # pre-1954 | 1954-1956 | 1956-1967
    source_id: Mapped[str] = mapped_column(ForeignKey("sources.source_id"))
    printed_page: Mapped[int | None] = mapped_column(Integer, nullable=True)
    provision: Mapped[str | None] = mapped_column(String(64), nullable=True)
    evidence_snippet: Mapped[str] = mapped_column(Text, default="")
    verification_status: Mapped[str] = mapped_column(String(64), default="anchor_verified_in_ocr")
    topic_ids: Mapped[list] = mapped_column(JSON, default=list)


class Relation(Base):
    """Cạnh quan hệ có kiểu: image→chunk/page/event/topic, event→chunk/source..., với căn cứ & độ tin cậy."""
    __tablename__ = "relations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    from_type: Mapped[str] = mapped_column(String(16))
    from_id: Mapped[str] = mapped_column(String(48))
    to_type: Mapped[str] = mapped_column(String(16))
    to_id: Mapped[str] = mapped_column(String(48))
    relation: Mapped[str] = mapped_column(String(32))
    basis: Mapped[str] = mapped_column(Text, default="")
    confidence: Mapped[str] = mapped_column(String(16), default="medium")
    __table_args__ = (Index("ix_rel_from", "from_type", "from_id"), Index("ix_rel_to", "to_type", "to_id"))


class Narration(Base):
    __tablename__ = "narrations"
    audio_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    language: Mapped[str] = mapped_column(String(8))
    voice_id: Mapped[str] = mapped_column(String(64))
    model: Mapped[str] = mapped_column(String(48))
    text_chars: Mapped[int] = mapped_column(Integer)
    n_segments: Mapped[int] = mapped_column(Integer, default=1)
    path: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="ready")  # ready | error
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(64), index=True)
    role: Mapped[str] = mapped_column(String(12))
    content: Mapped[str] = mapped_column(Text)
    language: Mapped[str | None] = mapped_column(String(8), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
