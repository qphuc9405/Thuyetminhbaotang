"""Embedding tách khỏi LLM. Hai backend:
- tfidf  : TF-IDF n-gram ký tự trên văn bản đã bỏ dấu (luôn chạy được, offline). KHÔNG phải embedding ngữ nghĩa.
- sbert  : sentence-transformers đa ngôn ngữ (vd intfloat/multilingual-e5-small) – cần cài thư viện + tải model (Internet).
Backend sbert được cài đặt nhưng KHÔNG được chạy/kiểm thử trong môi trường phát triển này (không tải được model)."""
from __future__ import annotations

import logging
from typing import Protocol, Sequence

import numpy as np

log = logging.getLogger(__name__)


class Embedder(Protocol):
    name: str
    def encode_passages(self, texts: Sequence[str]) -> np.ndarray: ...
    def encode_queries(self, texts: Sequence[str]) -> np.ndarray: ...


class SBertEmbedder:
    def __init__(self, model_name: str):
        from sentence_transformers import SentenceTransformer  # import muộn: phụ thuộc tuỳ chọn
        self.name = f"sbert:{model_name}"
        self.model = SentenceTransformer(model_name)
        self._e5 = "e5" in model_name.lower()

    def encode_passages(self, texts):
        t = [("passage: " + x) if self._e5 else x for x in texts]
        return np.asarray(self.model.encode(t, normalize_embeddings=True, show_progress_bar=False), dtype=np.float32)

    def encode_queries(self, texts):
        t = [("query: " + x) if self._e5 else x for x in texts]
        return np.asarray(self.model.encode(t, normalize_embeddings=True, show_progress_bar=False), dtype=np.float32)


def get_dense_embedder(backend: str, model_name: str) -> Embedder | None:
    if backend != "sbert":
        return None
    try:
        return SBertEmbedder(model_name)
    except Exception as e:  # thiếu thư viện hoặc không tải được model -> hạ cấp về lexical, ghi log rõ ràng
        log.warning("Không khởi tạo được embedding sbert (%s): %s. Hạ cấp về tìm kiếm lexical.", model_name, type(e).__name__)
        return None
