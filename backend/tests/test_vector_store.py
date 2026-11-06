import sqlite3
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from vector_store import VectorStore, split_content


class VectorStoreTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.path = Path(self.directory.name) / "knowledge.sqlite3"
        self.store = VectorStore(self.path)

    def tearDown(self):
        self.directory.cleanup()

    def test_upsert_persists_vectors_and_replaces_old_chunks(self):
        self.store.upsert({
            "id": "bridge",
            "title": "Cầu Hiền Lương",
            "content": "Cầu Hiền Lương bắc qua sông Bến Hải.",
            "source": "Tư liệu kiểm duyệt",
        })
        self.assertEqual(VectorStore(self.path).search("sông Bến Hải")[0]["id"], "bridge")

        self.store.upsert({
            "id": "bridge",
            "title": "Cầu Hiền Lương",
            "content": "Cây cầu được trùng tu nhiều lần.",
        })
        self.assertEqual(len(self.store.list_documents()), 1)
        self.assertEqual(self.store.list_documents()[0]["chunks"], 1)
        self.assertNotIn("sông Bến Hải", self.store.search("cầu được trùng tu")[0]["content"])

    def test_search_finds_relevant_document_and_empty_answer_is_safe(self):
        self.store.upsert({
            "id": "bridge", "title": "Cầu Hiền Lương",
            "content": "Cầu Hiền Lương bắc qua sông Bến Hải.",
        })
        self.store.upsert({
            "id": "museum", "title": "Nhà trưng bày",
            "content": "Nơi lưu giữ ảnh tư liệu và hiện vật.",
        })
        self.assertEqual(self.store.search("ảnh tư liệu")[0]["id"], "museum")
        self.assertEqual(self.store.answer("ảnh tư liệu")["sources"][0]["id"], "museum")
        self.assertEqual(self.store.answer("món ăn ở Hà Nội")["sources"], [])

    def test_long_document_is_split_with_overlap(self):
        content = " ".join(f"word{i}" for i in range(250))
        chunks = split_content(content)
        self.assertEqual(len(chunks), 2)
        self.assertIn("word135", chunks[0])
        self.assertIn("word135", chunks[1])

    def test_chat_search_stays_within_selected_location(self):
        self.store.upsert({
            "id": "bridge", "title": "Cầu Hiền Lương",
            "content": "Cầu Hiền Lương bắc qua sông Bến Hải.",
        })
        self.store.upsert({
            "id": "museum", "title": "Nhà trưng bày Vĩ tuyến 17",
            "content": "Nhà trưng bày lưu giữ hiện vật và ảnh tư liệu.",
        })
        self.assertTrue(all(
            item["id"].startswith("bridge")
            for item in self.store.search("hiện vật và ảnh tư liệu", zone_id="bridge")
        ))
        with self.assertRaises(ValueError):
            self.store.answer("Cầu Hiền Lương", zone_id="unknown")

    def test_custom_id_is_shared_by_narration_and_chat(self):
        document = {"id": "cau-hien-luong-nguon-1", "zone_id": "bridge",
                    "title": "Cầu Hiền Lương", "content": "Cầu Hiền Lương bắc qua sông Bến Hải.",
                    "source": "Nguồn kiểm tra"}
        self.store.upsert(document)
        narration = self.store.narration("bridge")["documents"]
        self.assertEqual(narration[0]["content"], document["content"])
        self.assertEqual(self.store.answer("sông Bến Hải", "bridge")["sources"][0]["id"], document["id"])
        self.assertEqual(self.store.narration("museum")["documents"], [])
        self.assertEqual(self.store.search("sông Bến Hải", zone_id="museum"), [])
        document["zone_id"] = "museum"
        self.store.upsert(document)
        self.assertEqual(self.store.narration("bridge")["documents"], [])
        self.assertEqual(self.store.search("sông Bến Hải", zone_id="bridge"), [])
        self.assertEqual(self.store.search("sông Bến Hải", zone_id="museum")[0]["id"], document["id"])

    def test_invalid_zone_types_and_missing_assignment(self):
        for zone in ([], {}, 42, True, "", "unknown"):
            with self.subTest(zone=zone):
                with self.assertRaises(ValueError):
                    self.store.answer("cầu", zone)
                with self.assertRaises(ValueError):
                    self.store.narration(zone)
                with self.assertRaises(ValueError):
                    self.store.upsert({"id": "custom", "title": "Cầu", "content": "Cầu", "zone_id": zone})
        with self.assertRaises(ValueError):
            self.store.upsert({"id": "custom", "title": "Cầu", "content": "Cầu"})
        self.store.upsert({"id": "custom", "title": "Cầu", "content": "Cầu", "zone_id": None})
        self.assertEqual(len(self.store.search("Cầu")), 1)
        self.assertEqual(self.store.search("Cầu", zone_id="bridge"), [])

    def test_migrates_legacy_database_without_losing_content(self):
        old_path = Path(self.directory.name) / "old.sqlite3"
        with sqlite3.connect(old_path) as db:
            db.execute("""CREATE TABLE documents (id TEXT PRIMARY KEY, title TEXT NOT NULL,
                content TEXT NOT NULL, source TEXT NOT NULL DEFAULT '', category TEXT NOT NULL DEFAULT '',
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)""")
            db.executemany("INSERT INTO documents(id,title,content) VALUES (?,?,?)", [
                ("bridge-1", "Chủ đề", "Nội dung cũ"),
                ("bridge", "Tổng quan", "Bài giới thiệu cũ"),
                ("custom", "Chưa phân loại", "Giữ nguyên"),
            ])
        migrated = VectorStore(old_path)
        self.assertEqual([d["id"] for d in migrated.narration("bridge")["documents"]], ["bridge", "bridge-1"])
        self.assertEqual(migrated.narration("bridge")["documents"][0]["content"], "Bài giới thiệu cũ")
        self.assertEqual(len(VectorStore(old_path).list_documents()), 3)
        custom = next(d for d in migrated.list_documents() if d["id"] == "custom")
        self.assertIsNone(custom["zone_id"])


if __name__ == "__main__":
    unittest.main()
