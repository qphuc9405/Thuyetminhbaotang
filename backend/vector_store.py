"""SQLite document store with persistent, deterministic text vectors."""

from __future__ import annotations

import hashlib
import math
import re
import sqlite3
import struct
import unicodedata
from pathlib import Path

ZONE_IDS = {"bridge", "museum", "flag", "monument", "union"}


def validate_zone(zone_id: str | None) -> None:
    if zone_id is not None and (not isinstance(zone_id, str) or zone_id not in ZONE_IDS):
        raise ValueError("Địa điểm không hợp lệ.")


VECTOR_SIZE = 384
WORD_RE = re.compile(r"[\w]+", re.UNICODE)


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFD", text.lower())
    text = "".join(char for char in text if unicodedata.category(char) != "Mn")
    return text.replace("đ", "d")


def embed(text: str) -> tuple[float, ...]:
    """Hash Vietnamese word and character features into a unit vector.

    This works offline. It measures lexical similarity, not deep semantic meaning.
    """
    words = WORD_RE.findall(normalize(text))
    vector = [0.0] * VECTOR_SIZE
    features = [(f"w:{word}", 2.0) for word in words]
    features += [(f"b:{a}_{b}", 1.0) for a, b in zip(words, words[1:])]
    for word in words:
        if len(word) >= 4:
            features.extend((f"c:{word[i:i + 3]}", 0.3) for i in range(len(word) - 2))

    for feature, weight in features:
        digest = hashlib.blake2b(feature.encode("utf-8"), digest_size=8).digest()
        number = int.from_bytes(digest, "little")
        index = number % VECTOR_SIZE
        sign = 1 if number & (1 << 63) else -1
        vector[index] += sign * weight

    magnitude = math.sqrt(sum(value * value for value in vector))
    return tuple(value / magnitude for value in vector) if magnitude else tuple(vector)


def pack_vector(vector: tuple[float, ...]) -> bytes:
    return struct.pack(f"<{VECTOR_SIZE}f", *vector)


def unpack_vector(blob: bytes) -> tuple[float, ...]:
    return struct.unpack(f"<{VECTOR_SIZE}f", blob)


def split_content(content: str, size: int = 160, overlap: int = 25) -> list[str]:
    words = content.split()
    if not words:
        return []
    chunks = []
    step = size - overlap
    for start in range(0, len(words), step):
        chunk = " ".join(words[start:start + size])
        if chunk:
            chunks.append(chunk)
        if start + size >= len(words):
            break
    return chunks


class VectorStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _initialize(self) -> None:
        with self._connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    source TEXT NOT NULL DEFAULT '',
                    category TEXT NOT NULL DEFAULT '',
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS chunks (
                    document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                    position INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    vector BLOB NOT NULL,
                    PRIMARY KEY (document_id, position)
                );
                CREATE INDEX IF NOT EXISTS chunks_document_id ON chunks(document_id);
            """)

            columns = {row["name"] for row in db.execute("PRAGMA table_info(documents)")}
            if "zone_id" not in columns:
                db.execute("ALTER TABLE documents ADD COLUMN zone_id TEXT")
                for zone_id in ZONE_IDS:
                    db.execute("UPDATE documents SET zone_id = ? WHERE id = ? OR id LIKE ?",
                               (zone_id, zone_id, f"{zone_id}-%"))
            db.execute("CREATE INDEX IF NOT EXISTS documents_zone_id ON documents(zone_id)")

    def upsert(self, document: dict) -> dict:
        if not isinstance(document, dict):
            raise ValueError("Mỗi tài liệu phải là một JSON object.")
        identifier = document.get("id")
        title = document.get("title")
        content = document.get("content")
        source = document.get("source", "")
        category = document.get("category", "")
        if not all(isinstance(value, str) for value in (identifier, title, content, source, category)):
            raise ValueError("id, title, content, source và category phải là chuỗi.")
        if not identifier or not title.strip() or not content.strip():
            raise ValueError("id, title và content không được để trống.")
        if len(identifier) > 120 or len(title) > 240 or len(content) > 100_000:
            raise ValueError("Tài liệu vượt quá giới hạn độ dài.")

        if "zone_id" in document:
            zone_id = document["zone_id"]
        else:
            zone_id = next((zone for zone in ZONE_IDS if identifier == zone or identifier.startswith(f"{zone}-")), None)
            if zone_id is None:
                raise ValueError("Tài liệu cần zone_id; dùng null cho tư liệu tổng quan.")
        validate_zone(zone_id)
        chunks = split_content(content)
        with self._connect() as db:
            db.execute("""
                INSERT INTO documents(id, title, content, source, category, zone_id, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(id) DO UPDATE SET
                    title=excluded.title,
                    content=excluded.content,
                    source=excluded.source,
                    category=excluded.category,
                    zone_id=excluded.zone_id,
                    updated_at=CURRENT_TIMESTAMP
            """, (identifier, title.strip(), content.strip(), source.strip(), category.strip(), zone_id))
            db.execute("DELETE FROM chunks WHERE document_id = ?", (identifier,))
            db.executemany(
                "INSERT INTO chunks(document_id, position, content, vector) VALUES (?, ?, ?, ?)",
                [
                    (identifier, index, chunk, pack_vector(embed(f"{title} {chunk}")))
                    for index, chunk in enumerate(chunks)
                ],
            )
        return {"id": identifier, "title": title.strip(), "chunks": len(chunks), "zone_id": zone_id}

    def list_documents(self) -> list[dict]:
        with self._connect() as db:
            rows = db.execute("""
                SELECT d.id, d.title, d.source, d.category, d.zone_id, d.updated_at,
                       COUNT(c.position) AS chunks
                FROM documents d LEFT JOIN chunks c ON c.document_id = d.id
                GROUP BY d.id ORDER BY d.title
            """).fetchall()
        return [dict(row) for row in rows]

    def narration(self, zone_id: str) -> dict:
        validate_zone(zone_id)
        if zone_id is None:
            raise ValueError("Thuyết minh cần địa điểm.")
        with self._connect() as db:
            rows = db.execute("""
                SELECT id, title, content, source, category, zone_id FROM documents
                WHERE zone_id = ? ORDER BY CASE WHEN id = ? THEN 0 ELSE 1 END, title, id
            """, (zone_id, zone_id)).fetchall()
        return {"zone_id": zone_id, "documents": [dict(row) for row in rows]}

    def search(self, query: str, limit: int = 5, zone_id: str | None = None) -> list[dict]:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("Câu hỏi không được để trống.")
        validate_zone(zone_id)
        query_vector = embed(query)
        with self._connect() as db:
            sql = """
                SELECT d.id, d.title, d.source, d.category,
                       c.position, c.content, c.vector
                FROM chunks c JOIN documents d ON d.id = c.document_id
            """
            params: tuple = ()
            if zone_id:
                sql += " WHERE d.zone_id = ?"
                params = (zone_id,)
            rows = db.execute(sql, params).fetchall()

        ranked = []
        for row in rows:
            score = sum(a * b for a, b in zip(query_vector, unpack_vector(row["vector"])))
            ranked.append({
                "id": row["id"],
                "title": row["title"],
                "source": row["source"],
                "category": row["category"],
                "position": row["position"],
                "content": row["content"],
                "score": round(score, 4),
            })
        ranked.sort(key=lambda item: item["score"], reverse=True)
        return ranked[:max(1, min(limit, 20))]

    def answer(self, question: str, zone_id: str | None = None) -> dict:
        matches = [item for item in self.search(question, limit=3, zone_id=zone_id) if item["score"] >= 0.16]
        if not matches:
            return {
                "answer": "Chưa tìm thấy tư liệu phù hợp trong cơ sở dữ liệu. Hãy thêm tài liệu hoặc thử câu hỏi khác.",
                "sources": [],
            }
        best = matches[0]
        return {
            "answer": f"Theo tư liệu “{best['title']}”: {best['content']}",
            "sources": [
                {"id": item["id"], "title": item["title"], "source": item["source"], "score": item["score"]}
                for item in matches
            ],
        }
