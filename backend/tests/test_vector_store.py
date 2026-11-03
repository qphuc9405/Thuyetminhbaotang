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


if __name__ == "__main__":
    unittest.main()
