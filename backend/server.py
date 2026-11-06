"""HTTP API for the Vĩ tuyến 17 local knowledge base."""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from vector_store import VectorStore

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get("VITUYEN_DB_PATH", BASE_DIR / "data" / "knowledge.sqlite3"))
store = VectorStore(DB_PATH)


class Handler(BaseHTTPRequestHandler):
    def _json(self, status: int, payload: dict | list) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "http://localhost:5173")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
        self.wfile.write(body)

    def _body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length < 1 or length > 120_000:
            raise ValueError("Dữ liệu gửi lên quá lớn hoặc trống.")
        payload = json.loads(self.rfile.read(length))
        if not isinstance(payload, dict):
            raise ValueError("Dữ liệu phải là một JSON object.")
        return payload

    def do_OPTIONS(self) -> None:
        self._json(200, {})

    def do_GET(self) -> None:
        route = urlparse(self.path)
        if route.path == "/api/health":
            self._json(200, {"status": "ok", "documents": len(store.list_documents())})
        elif route.path == "/api/documents":
            self._json(200, {"documents": store.list_documents()})
        elif route.path == "/api/narration":
            try:
                zone_id = parse_qs(route.query).get("zone_id", [None])[0]
                self._json(200, store.narration(zone_id))
            except ValueError as error:
                self._json(400, {"error": str(error)})
        elif route.path == "/api/search":
            params = parse_qs(route.query)
            try:
                query = params.get("q", [""])[0]
                limit = int(params.get("limit", ["5"])[0])
                zone_id = params.get("zone_id", [None])[0]
                self._json(200, {"results": store.search(query, limit, zone_id)})
            except ValueError as error:
                self._json(400, {"error": str(error)})
        else:
            self._json(404, {"error": "Đường dẫn không tồn tại."})

    def do_POST(self) -> None:
        route = urlparse(self.path).path
        try:
            payload = self._body()
            if route == "/api/documents":
                self._json(201, {"document": store.upsert(payload)})
            elif route == "/api/chat":
                self._json(200, store.answer(payload.get("question", ""), payload.get("zone_id")))
            else:
                self._json(404, {"error": "Đường dẫn không tồn tại."})
        except (ValueError, json.JSONDecodeError) as error:
            self._json(400, {"error": str(error)})


def main() -> None:
    host = os.environ.get("VITUYEN_HOST", "127.0.0.1")
    port = int(os.environ.get("VITUYEN_PORT", "8000"))
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"API: http://{host}:{port} | Vector DB: {DB_PATH}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
