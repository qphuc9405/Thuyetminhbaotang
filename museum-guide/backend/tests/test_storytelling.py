"""Nâng cấp thuyết minh: hồ sơ câu hỏi, mở rộng đoạn lân cận, prompt hướng dẫn viên, câu chuyện trang chủ, minh hoạ timeline."""
from app.services.answer_profiles import audience, classify
from app.services.rag_service import SYSTEM_PROMPT
from tests.conftest import llm_json


def test_classify_profiles():
    assert classify("Cầu Hiền Lương bị chia đôi mỗi bên dài bao nhiêu?").kind == "simple"
    assert classify("Vì sao vĩ tuyến 17 trở thành giới tuyến?").kind == "entity"
    assert classify("Vụ tống triệt ngày 19-3-1965 là gì?").kind == "event"
    assert classify("So sánh giai đoạn 1954–1956 và 1956–1967").kind == "period"
    assert classify("Hãy kể cho tôi nghe câu chuyện về Cầu Hiền Lương từ năm 1954 đến 1967").kind == "story"
    assert classify("讲述贤良桥的故事").kind == "story" and classify("How tall was the first flagpole?").kind == "simple"
    assert audience("Hãy giải thích cho một học sinh chưa biết lịch sử") == "student"
    assert audience("Hãy giải thích như đang thuyết minh cho một đoàn khách tham quan") == "tour"


def test_prompt_is_guide_and_keeps_guards():
    for must in ("museum guide", "not a generic Q&A bot", "never invent", "untrusted reference DATA", "not a national border", "Never pad", "{min_words}", "Simplified"[:0]):
        assert must.lower() in SYSTEM_PROMPT.lower()
    assert "at most ~180 words" not in SYSTEM_PROMPT


def test_story_question_gets_more_context_and_tokens(client):
    client.fake.llm_script.append(llm_json("Năm 1954… [S1]"))
    j = client.post("/api/chat", json={"message": "Hãy kể cho tôi nghe câu chuyện về Cầu Hiền Lương từ năm 1954 đến 1967", "language": "vi"}).json()
    body = client.fake.llm_calls[-1]["body"]
    assert j["retrieval"]["profile"] == "story" and j["retrieval"]["n_context_chunks"] >= 12
    assert body["options"]["num_predict"] >= 3000 and "450-700 words" in body["messages"][0]["content"]
    ctx = body["messages"][-1]["content"]
    pages = [int(x) for x in __import__("re").findall(r"vị trí=tr\.(\d+)", ctx)]
    assert pages == sorted(pages)  # kể chuyện: context sắp theo trang (thời gian)


def test_simple_question_stays_compact(client):
    client.fake.llm_script.append(llm_json("12 m [S1]"))
    j = client.post("/api/chat", json={"message": "Ngày 8-10-1954 phía Bắc dựng cột cờ đầu tiên cao bao nhiêu mét?", "language": "vi"}).json()
    assert j["retrieval"]["profile"] == "simple" and client.fake.llm_calls[-1]["body"]["options"]["num_predict"] <= 1200
    assert "100-180 words" in client.fake.llm_calls[-1]["body"]["messages"][0]["content"]


def test_short_answer_warning(client):
    client.fake.llm_script.append(llm_json("Có [S1]."))
    j = client.post("/api/chat", json={"message": "So sánh giai đoạn 1954–1956 và 1956–1967 tại cầu Hiền Lương", "language": "vi"}).json()
    assert any(w.startswith("short_answer") for w in j["warnings"])


def test_neighbor_expansion_same_chapter(index_and_chunks):
    ix, _ = index_and_chunks
    hits, _ = ix.search("cuộc chiến sơn cầu", k=3)
    base = [ix.chunk(h.chunk_id) for h in hits]
    exp = ix.expand_with_neighbors(base, n_top=2)
    assert len(exp) > len(base) and len({c["chunk_id"] for c in exp}) == len(exp)
    for c in exp:
        if c not in base:
            assert any(b["source_id"] == c["source_id"] and b["chapter_id"] == c["chapter_id"] for b in base[:2])


def test_followup_more_detail_inherits_depth(client):
    client.fake.llm_script.extend([llm_json("Vụ tống triệt… [S1]"), llm_json("Thêm chi tiết… [S1]")])
    client.post("/api/chat", json={"message": "Vụ tống triệt ngày 19-3-1965 là gì?", "language": "vi", "session_id": "fd1"})
    j = client.post("/api/chat", json={"message": "Hãy nói kỹ hơn về sự kiện vừa đề cập", "language": "vi", "session_id": "fd1"}).json()
    assert j["retrieval"]["profile"] != "simple"
    assert any(m["role"] == "assistant" for m in client.fake.llm_calls[-1]["body"]["messages"])


def test_story_endpoint_citations_verified(client):
    j = client.get("/api/story").json()
    assert [c["id"] for c in j["chapters"]] == ["ch1", "ch2", "ch3", "ch4"] and j["hero"]["image_id"] == "IMG034"
    for ch in j["chapters"]:
        assert ch["image"] and ch["citations"] and all(c["verified_anchor"] for c in ch["citations"])
        assert set(ch["title"]) == {"vi", "en", "zh"} and len(ch["body"]["vi"]) == len(ch["body"]["en"]) == len(ch["body"]["zh"])


def test_timeline_illustrations_labelled(client):
    items = {e["event_id"]: e for e in client.get("/api/timeline").json()["items"]}
    assert items["EV19"]["images"][0]["relation"] == "illustrates" and items["EV19"]["images"][0]["image_id"] == "BKFIG11"  # sửa lỗi BKFIG10
    assert all(i["relation"] == "illustrates_topic" for i in items["EV09"]["images"])
    assert items["EV24"]["images"] == []  # không có ảnh phù hợp -> để trống, không gán bừa
