"""Import documents into the local vector database."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from vector_store import VectorStore

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DB = BASE_DIR / "data" / "knowledge.sqlite3"
DEFAULT_SEED = BASE_DIR / "data" / "seed.json"


def main() -> None:
    parser = argparse.ArgumentParser(description="Quản lý tư liệu Vĩ tuyến 17")
    parser.add_argument("command", choices=["seed", "import", "list"])
    parser.add_argument("file", nargs="?", help="Tệp JSON khi dùng lệnh import")
    args = parser.parse_args()

    db_path = Path(os.environ.get("VITUYEN_DB_PATH", DEFAULT_DB))
    store = VectorStore(db_path)
    if args.command == "list":
        for document in store.list_documents():
            print(f"{document['id']} | {document['title']} | {document['chunks']} đoạn")
        return

    if args.command == "import" and not args.file:
        parser.error("Lệnh import cần đường dẫn tệp JSON.")
    path = DEFAULT_SEED if args.command == "seed" else Path(args.file)
    documents = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(documents, dict):
        documents = [documents]
    if not isinstance(documents, list):
        parser.error("Tệp JSON phải chứa một tài liệu hoặc danh sách tài liệu.")
    for document in documents:
        result = store.upsert(document)
        print(f"Đã lưu {result['id']}: {result['title']} ({result['chunks']} đoạn)")
    print(f"Cơ sở dữ liệu: {db_path}")


if __name__ == "__main__":
    main()
