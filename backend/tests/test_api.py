"""Exercise actual HTTP parsing/serialization without opening a network socket."""
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
with tempfile.TemporaryDirectory() as folder:
    with patch.dict(os.environ, {"VITUYEN_DB_PATH": str(Path(folder) / "initial.sqlite3")}):
        import server
from vector_store import VectorStore


class Connection:
    def __init__(self, request):
        self.input = io.BytesIO(request)
        self.output = io.BytesIO()

    def makefile(self, *args, **kwargs):
        return self.input

    def sendall(self, data):
        self.output.write(data)


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.store = VectorStore(Path(self.folder.name) / "test.sqlite3")

    def tearDown(self):
        self.folder.cleanup()

    def request(self, method, path, payload=None):
        body = json.dumps(payload).encode() if payload is not None else b""
        request = f"{method} {path} HTTP/1.0\r\nContent-Length: {len(body)}\r\n\r\n".encode() + body
        connection = Connection(request)
        with patch.object(server, "store", self.store), patch.object(server.Handler, "log_message"):
            server.Handler(connection, ("127.0.0.1", 0), None)
        headers, body = connection.output.getvalue().split(b"\r\n\r\n", 1)
        return int(headers.split()[1]), json.loads(body)

    def test_invalid_zone_returns_json_400(self):
        for zone in ([], {}, 123, True, "bad"):
            status, result = self.request("POST", "/api/chat", {"question": "cầu", "zone_id": zone})
            self.assertEqual(status, 400)
            self.assertIn("error", result)
        self.assertEqual(self.request("GET", "/api/narration")[0], 400)

    def test_import_narration_and_chat_use_same_location(self):
        document = {"id": "custom", "zone_id": "bridge", "title": "Cầu Hiền Lương",
                    "content": "Cầu Hiền Lương bắc qua sông Bến Hải.", "source": "Nguồn kiểm tra"}
        self.assertEqual(self.request("POST", "/api/documents", document)[0], 201)
        status, result = self.request("GET", "/api/narration?zone_id=bridge")
        self.assertEqual(status, 200)
        self.assertEqual(result["documents"][0]["content"], document["content"])
        status, answer = self.request("POST", "/api/chat", {"question": "sông Bến Hải", "zone_id": "bridge"})
        self.assertEqual(status, 200)
        self.assertIn(document["content"], answer["answer"])
        self.assertEqual(answer["sources"][0]["source"], document["source"])
        _, answer = self.request("POST", "/api/chat", {"question": "sông Bến Hải", "zone_id": "museum"})
        self.assertEqual(answer["sources"], [])

    def test_union_is_a_separate_destination(self):
        self.assertEqual(self.request("GET", "/api/narration?zone_id=union"),
                         (200, {"zone_id": "union", "documents": []}))
        document = {"id": "union-test", "zone_id": "union", "title": "Nhà liên hiệp",
                    "content": "Tư liệu kiểm tra dành riêng cho Nhà liên hiệp."}
        self.assertEqual(self.request("POST", "/api/documents", document)[0], 201)
        _, narration = self.request("GET", "/api/narration?zone_id=union")
        self.assertEqual(narration["documents"][0]["content"], document["content"])
        status, answer = self.request("POST", "/api/chat", {"question": "Nhà liên hiệp", "zone_id": "union"})
        self.assertEqual(status, 200)
        self.assertEqual(answer["sources"][0]["id"], document["id"])
        self.assertEqual(self.request("GET", "/api/narration?zone_id=museum")[1]["documents"], [])
