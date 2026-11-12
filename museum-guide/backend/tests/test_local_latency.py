"""Ngăn hồi quy ngân sách CPU và cache làm lẫn ngữ cảnh/ngôn ngữ."""
from app.services.answer_profiles import classify, local_profile
from app.services.context_builder import build_context
from app.services.rag_service import local_chunks
from tests.conftest import llm_json


def enable_local(client):
    client.app.state.settings.ollama_host = "http://127.0.0.1:11434"


def test_local_short_budget_and_explicit_detail():
    q = "Khu di tích Vĩ tuyến 17 có gì nổi bật?"
    short = local_profile(classify(q), q)
    detail = local_profile(classify("Hãy kể câu chuyện về Cầu Hiền Lương"), "Hãy kể câu chuyện về Cầu Hiền Lương")
    assert short.max_tokens <= 400 and short.max_context <= 2400 and short.expand == 0
    assert detail.max_tokens > short.max_tokens and detail.max_context > short.max_context


def test_cache_reuses_independent_answer_but_not_followup_or_other_language(client):
    enable_local(client)
    q = "Cột cờ Hiền Lương cao bao nhiêu?"
    client.fake.llm_script.append(llm_json("Theo tư liệu, cột cờ cao 12 m [S1]."))
    first = client.post("/api/chat", json={"message": q, "session_id": "cache-one"}).json()
    assert first["sources"] and not first["warnings"]
    again = client.post("/api/chat", json={"message": q, "session_id": "cache-two"}).json()
    assert again["answer"] == first["answer"] and again["retrieval"]["answer_cached"]
    assert len(client.fake.llm_calls) == 1
    body = client.fake.llm_calls[0]["body"]
    assert body["options"]["num_predict"] <= 400 and body["keep_alive"] == "30m"
    client.fake.llm_script.append(llm_json("The flagpole is 12 m high [S1]."))
    client.post("/api/chat", json={"message": q, "language": "en", "session_id": "cache-en"})
    assert len(client.fake.llm_calls) == 2
    client.fake.llm_script.append(llm_json("Theo tư liệu, lá cờ rộng 24 m² [S1]."))
    client.post("/api/chat", json={"message": "Còn lá cờ thì rộng bao nhiêu?", "session_id": "cache-one"})
    assert len(client.fake.llm_calls) == 3
    assert any(m["role"] == "assistant" for m in client.fake.llm_calls[-1]["body"]["messages"])


def test_warned_answer_is_not_cached(client):
    enable_local(client)
    client.fake.llm_script.extend([llm_json("Không có nguồn.", used=()), llm_json("Có nguồn [S1].")])
    for sid in ("bad-cache-1", "bad-cache-2"):
        client.post("/api/chat", json={"message": "Cột cờ Hiền Lương cao bao nhiêu?", "session_id": sid})
    assert len(client.fake.llm_calls) == 2


def test_expired_cache_calls_model_again(client):
    enable_local(client)
    q = "Cột cờ Hiền Lương cao bao nhiêu?"
    client.fake.llm_script.extend([llm_json("Cột cờ cao 12 m [S1]."), llm_json("Cột cờ cao 12 m [S1].")])
    client.post("/api/chat", json={"message": q, "session_id": "expired-1"})
    cache = client.app.state.rag._answer_cache
    key = next(iter(cache))
    _, result = cache[key]
    cache[key] = (0, result)
    client.post("/api/chat", json={"message": q, "session_id": "expired-2"})
    assert len(client.fake.llm_calls) == 2


def test_compact_context_validation_only_sees_text_sent_to_model():
    c = {"chunk_id": "LONG", "source_id": "SRC001", "source_type": "BOOK", "source_title": "Sách", "content": "Cột cờ. " * 180 + "Năm 1999.", "printed_page": 1}
    ctx = build_context([c], [], compact=True)
    assert "1999" not in ctx.text and "1999" not in ctx.source_map["S1"]["content"]
    assert ctx.truncated and "1999" in c["content"]


def test_local_compression_keeps_answer_below_top_three_and_conflict_note(index_and_chunks):
    index, _ = index_and_chunks
    q = "Cột cờ đầu tiên ở Hiền Lương cao bao nhiêu?"
    hits, _ = index.search(q, k=6)
    chosen = local_chunks([index.chunk(h.chunk_id) for h in hits], q, 3)
    assert any("12m" in c["content"] or "12 m" in c["content"] for c in chosen)
    assert any(c["source_type"] == "CURATOR_NOTE" for c in chosen)
