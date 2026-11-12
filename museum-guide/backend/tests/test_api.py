"""API-01..API-10, UI-contract, bảo mật đầu vào."""
import pytest

from tests.conftest import llm_json


def test_api01_health(client):
    j = client.get("/api/health").json()
    assert j["status"] == "ok" and j["database"]["pages"] == 260 and j["database"]["chunks"] > 500
    assert j["retrieval"]["image_retrieval"].startswith("metadata-based")
    assert "key" not in str(j).lower().replace("configured", "")  # không lộ khoá


def test_api03_api04_validation(client):
    assert client.post("/api/chat", json={"message": "", "language": "vi"}).status_code == 422
    assert client.post("/api/chat", json={"message": "   ", "language": "vi"}).status_code == 422
    assert client.post("/api/chat", json={"language": "vi"}).status_code == 422
    assert client.post("/api/chat", json={"message": "x", "language": "fr"}).status_code == 422
    assert client.post("/api/chat", json={"message": "x", "session_id": "../etc"}).status_code == 422
    assert client.post("/api/chat", content="not json", headers={"content-type": "application/json"}).status_code == 422
    e = client.post("/api/chat", json={"message": ""}).json()["error"]
    assert e["code"] == "validation_error"


def test_request_size_limit(client):
    r = client.post("/api/chat", content=b"x" * 30000, headers={"content-type": "application/json", "content-length": "30000"})
    assert r.status_code == 413


def test_api05_images_list_and_filters(client):
    j = client.get("/api/images?limit=200").json()
    assert j["total"] >= 46 and all("thumb_url" in i for i in j["items"])
    arch = client.get("/api/images?kind=archive_photo&limit=200").json()
    assert arch["total"] == 34 + 10  # 34 ảnh Archive_2 + 10 ảnh lịch sử của Archive_4 (6 ảnh còn lại là contemporary_photo)
    assert client.get("/api/images?kind=archive_photo&hide_variants=true&limit=200").json()["total"] == 44 - 8  # 8 bản trùng (7 nhóm cũ + DUP-S024)
    assert client.get("/api/images?kind=contemporary_photo&limit=200").json()["total"] == 6
    assert client.get("/api/images?q=Nam+Bac+mot+nha").json()["total"] >= 2
    assert client.get("/api/images?topic=loudspeakers").json()["total"] >= 2
    assert client.get("/api/images?limit=5000").json()["limit"] == 200


def test_api06_image_404(client):
    assert client.get("/api/images/NOPE").status_code == 404
    assert client.get("/api/images/NOPE/file").status_code == 404


def test_image_detail_and_file(client):
    d = client.get("/api/images/IMG007").json()
    for f in ["image_id", "title", "visual_description", "historical_context", "location", "time_period", "estimated_date", "main_objects", "visible_text", "people_description",
              "historical_significance", "related_events", "related_book_topics", "related_book_pages", "keywords", "source", "confidence_level", "verification_notes", "duplicate_group"]:
        assert f in d, f
    assert d["estimated_date"] == "Chưa xác định" and d["duplicate_group"] == "DUP-B"
    assert any(r["relation"] == "same_photograph_as_book_figure" for r in d["related_images"])
    assert any(p["link_type"] == "direct_match_book_figure" for p in d["related_passages"])
    f = client.get("/api/images/IMG007/file")
    assert f.status_code == 200 and f.headers["content-type"].startswith("image/jpeg")
    t = client.get("/api/images/IMG007/file?size=thumb")
    assert t.status_code == 200 and len(t.content) < len(f.content)


def test_api07_topics(client):
    j = client.get("/api/topics").json()["items"]
    assert len(j) == 13 and {"geneva", "bridgeflag"} <= {t["topic_id"] for t in j}
    d = client.get("/api/topics/bridgeflag").json()
    assert d["chapters"][0]["printed_start"] == 183 and d["events"] and d["images"] and d["passages"]
    assert client.get("/api/topics/zzz").status_code == 404


def test_api08_timeline(client):
    j = client.get("/api/timeline").json()
    assert len(j["items"]) == 31  # 29 + EV29 (sách tr.116) + EV-S01 (bài viết)
    assert all(i["image_id"].startswith(("IMG", "BKFIG")) for e in j["items"] for i in e["images"])  # chỉ ảnh, không lẫn ghi chú
    dates = [e["date_iso"] for e in j["items"]]
    assert dates == sorted(dates)
    assert all(e["verification_status"] != "anchor_not_found" for e in j["items"])
    p = client.get("/api/timeline?period=1954-1956").json()["items"]
    assert p and all(e["period"] == "1954-1956" for e in p)
    # e2e-07/08: sự kiện 1965 không bị gán vào giai đoạn 1954-1956
    e1965 = [e for e in j["items"] if e["date_iso"].startswith("1965")]
    assert e1965 and all(e["period"] == "1956-1967" for e in e1965)


def test_sources_documents_pages(client):
    s = client.get("/api/sources").json()["items"]
    ids = {x["source_id"] for x in s}
    assert {"SRC001", "SRC002", "DOC001", "DOC002", "DOC003", "DOC004", "DOC005"} <= ids
    d5 = next(x for x in s if x["source_id"] == "DOC005")
    assert d5["verification_status"] == "not_accessed"
    docs = client.get("/api/documents").json()["items"]
    book = next(x for x in docs if x["source_id"] == "SRC001")
    assert book["n_pages"] == 260 and book["n_chunks"] > 500
    p = client.get("/api/documents/SRC001/pages/188").json()
    assert p["printed_page"] == 188 and p["pdf_page"] == 94 and "cột cờ" in p["ocr_text"].lower()
    assert client.get("/api/documents/SRC001/pages/999").status_code == 404


def test_search_endpoint(client):
    j = client.get("/api/search", params={"q": "cuộc chiến sơn cầu", "k": 3}).json()
    assert j["results"] and all(r["source_id"] and (r["chapter"] or r["provision"]) for r in j["results"])
    assert client.get("/api/search", params={"q": " "}).status_code == 422


def test_chat_persists_session_history(client):
    client.fake.llm_script.append(llm_json("Cột cờ cao 12 m [S1]."))
    client.post("/api/chat", json={"message": "Ngày 8-10-1954 phía Bắc dựng cột cờ đầu tiên cao bao nhiêu mét?", "language": "vi", "session_id": "persist1"})
    from app.database import repository as R
    from app.database.database import session_scope
    with session_scope() as db:
        msgs = R.recent_messages(db, "persist1")
    assert [m["role"] for m in msgs] == ["user", "assistant"]


def test_cors_only_configured_origin(client):
    r = client.options("/api/chat", headers={"Origin": "http://evil.example", "Access-Control-Request-Method": "POST"})
    assert "access-control-allow-origin" not in r.headers
    r2 = client.options("/api/chat", headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "POST"})
    assert r2.headers.get("access-control-allow-origin") == "http://localhost:5173"
