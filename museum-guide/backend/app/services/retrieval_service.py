"""Truy xuất lai (hybrid): BM25 (từ, đã bỏ dấu) + TF-IDF n-gram ký tự (+ dense tuỳ chọn), hợp nhất bằng RRF,
rerank nhẹ theo cụm từ/đề mục, lọc metadata. Luôn trả về metadata nguồn đầy đủ.

LƯU Ý TRUNG THỰC: khi backend là `tfidf`, đây là truy xuất TỪ KHOÁ/n-gram chứ không phải embedding ngữ nghĩa.
Truy vấn tiếng Anh/Trung được ánh xạ sang thuật ngữ Việt bằng glossary (xem glossary.py)."""
from __future__ import annotations

import math
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass, field
from typing import Iterable

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from .embedding_service import Embedder
from .glossary import expand_query, match_groups
from .text_utils import detect_language, fold, tokenize

STOP = set("""la cua va cac nhung mot cho trong khi duoc o tai voi de den tu nam nguoi da dang se co khong nay do nhu thi ma
cung nen boi vi neu hay hoac the theo ve len ra vao sau truoc gi sao nao ai dau bao nhieu hoi nhung cai viec phai rat qua
the a an of and or to in on at is are was were be been it its this that these those for from by with as did do does why what when where who how which about""".split())
# từ hỏi/từ chung không mang nội dung (không tính vào độ phủ khái niệm)
GENERIC_Q = set("""vai tro lich su y nghia dien ke cho biet gioi thieu noi hoi cau hoi tai sao nhu the nao ra sao nhung gi duoc
role history historical important importance significance happen happened tell explain describe meaning mean whom whose did does
play played events event story during period time year years was were has have had can could would should please give show list name summarize summarise define compare hay cho toi ban xin vui long january february march april may june july august september october november december monday tuesday wednesday thursday friday saturday sunday""".split())


@dataclass
class Hit:
    chunk_id: str
    score: float
    rank: int
    components: dict = field(default_factory=dict)
    coverage: float = 0.0
    gate: dict = field(default_factory=dict)  # strong: có nhóm khái niệm đặc thù; group_cov; phrase: số bigram khớp


class BM25:
    def __init__(self, docs_tokens: list[list[str]], k1: float = 1.4, b: float = 0.75):
        self.k1, self.b = k1, b
        self.N = len(docs_tokens)
        self.doc_len = np.array([len(d) for d in docs_tokens], dtype=np.float32)
        self.avgdl = float(self.doc_len.mean()) if self.N else 1.0
        self.tf: list[Counter] = [Counter(d) for d in docs_tokens]
        df: Counter = Counter()
        for c in self.tf:
            df.update(c.keys())
        self.idf = {t: math.log(1 + (self.N - n + 0.5) / (n + 0.5)) for t, n in df.items()}
        self.inv: dict[str, list[int]] = {}
        for i, c in enumerate(self.tf):
            for t in c:
                self.inv.setdefault(t, []).append(i)

    def scores(self, q_tokens: list[str]) -> np.ndarray:
        s = np.zeros(self.N, dtype=np.float32)
        for t in set(q_tokens):
            idf = self.idf.get(t)
            if idf is None:
                continue
            for i in self.inv[t]:
                f = self.tf[i][t]
                s[i] += idf * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * self.doc_len[i] / self.avgdl))
        return s


class RetrievalIndex:
    """Chỉ mục trong bộ nhớ. Corpus nhỏ (~600 chunk) nên không cần vector DB ngoài; có thể thay bằng Chroma/FAISS qua cùng interface."""

    def __init__(self, chunks: list[dict], dense: Embedder | None = None):
        self.chunks = chunks
        self.by_id = {c["chunk_id"]: i for i, c in enumerate(chunks)}
        self.index_text = [fold((c.get("chapter") or "") + " . " + (c.get("section") or "")) + " . " + c["folded"] for c in chunks]
        self.tokens = [[t for t in tokenize(x) if t not in STOP] for x in self.index_text]
        self.bm25 = BM25(self.tokens)
        self.bigrams = [set(zip(t, t[1:])) for t in self.tokens]
        self.trigrams = [set(zip(t, t[1:], t[2:])) for t in self.tokens]
        self.vocab = set(self.bm25.idf)
        self.tfidf = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True, min_df=1)
        self.mat = self.tfidf.fit_transform(self.index_text)
        self.dense = dense
        self.dense_mat = dense.encode_passages([c["content"] for c in chunks]) if dense else None
        self.backend = "hybrid(bm25+char-tfidf" + ("+dense:" + dense.name if dense else "") + ")"

    # ---- query processing
    def process_query(self, query: str) -> dict:
        lang = detect_language(query)
        expanded, hits = expand_query(query)
        toks = [t for t in tokenize(expanded) if t not in STOP and t not in GENERIC_Q]
        orig = [t for t in tokenize(fold(query)) if t not in STOP and t not in GENERIC_Q]
        groups = match_groups(query)
        grouptext = " ".join(" ".join(a) for _, a in groups)
        leftover = [t for t in dict.fromkeys(orig) if t not in GENERIC_Q and len(t) > 1 and not re.search(rf"\b{re.escape(t)}\b", grouptext)]
        exp_only = [t for t in toks if t not in set(orig)]
        expanded_clean = " ".join(t for t in tokenize(expanded) if t not in GENERIC_Q)
        ents = self.unknown_entities(query)
        return {"unknown_entities": ents, "language": lang, "expanded": expanded_clean, "glossary_hits": hits, "tokens": toks, "orig_tokens": orig, "exp_tokens": exp_only,
                "groups": groups, "leftover": leftover}

    def concept_coverage(self, qp: dict, i: int) -> float:
        """Độ phủ theo khái niệm (có trọng số): nhóm glossary tính 1.0; token còn lại tính theo IDF (OOV = 0.8)."""
        c = self.chunks[i]
        folded = c["folded"]
        tokset = set(self.tokens[i])
        num = den = 0.0
        for _, alts in qp["groups"]:
            den += 1.0
            if any(a in folded for a in alts):
                num += 1.0
        mx = max(self.bm25.idf.values()) if self.bm25.idf else 1.0
        for t in qp["leftover"]:
            idf = self.bm25.idf.get(t)
            w = (idf / mx) if idf is not None else 0.3  # từ không có trong kho: nhẹ (đã có luật thực thể lạ riêng)
            den += w
            if t in tokset or (len(t) >= 5 and any(x.startswith(t[:5]) for x in tokset)):
                num += w
        return num / den if den else 0.0

    WEAK_GROUPS = {"vietnam", "france", "us", "agreement", "year1965", "people_life"}

    def gate_info(self, qp: dict, i: int) -> dict:
        folded = self.chunks[i]["folded"]
        strong = [k for k, _ in qp["groups"] if k not in self.WEAK_GROUPS]
        gcov = (sum(1 for _, alts in qp["groups"] if any(a in folded for a in alts)) / len(qp["groups"])) if qp["groups"] else 0.0
        ot = qp["orig_tokens"]
        phrase = len(set(zip(ot, ot[1:])) & self.bigrams[i])
        return {"strong": bool(strong), "group_cov": gcov, "phrase": phrase}

    def unknown_entities(self, query: str) -> list[str]:
        """Danh từ riêng (viết hoa, không đứng đầu câu) KHÔNG xuất hiện trong kho và không thuộc glossary -> câu hỏi nhắc thực thể ngoài kho."""
        gl = " ".join(" ".join(a) for _, a in match_groups(query))
        out = []
        words = [w for w in re.findall(r"[\wÀ-ỹ]+", query) if w[0].isupper() and len(w) > 2]
        for w in words:
            f = fold(w)
            if len(f) >= 3 and f not in self.vocab and f not in gl and f not in GENERIC_Q and f not in STOP:
                out.append(w)
        return out

    def _filter_mask(self, flt: dict | None) -> np.ndarray:
        m = np.ones(len(self.chunks), dtype=bool)
        if not flt:
            return m
        for i, c in enumerate(self.chunks):
            if flt.get("source_ids") and c["source_id"] not in flt["source_ids"]: m[i] = False; continue
            if flt.get("source_types") and c["source_type"] not in flt["source_types"]: m[i] = False; continue
            if flt.get("chapter_ids") and c["chapter_id"] not in flt["chapter_ids"]: m[i] = False; continue
            if flt.get("language") and c["language"] != flt["language"]: m[i] = False; continue
            pa, pb = flt.get("printed_from"), flt.get("printed_to")
            if (pa or pb) and c["printed_page"] is not None:
                end = c["printed_page_end"] or c["printed_page"]
                if (pa and end < pa) or (pb and c["printed_page"] > pb): m[i] = False
        return m

    def search(self, query: str, k: int = 6, flt: dict | None = None, rerank: bool = True) -> tuple[list[Hit], dict]:
        qp = self.process_query(query)
        toks = qp["tokens"]
        if not toks:
            return [], qp
        mask = self._filter_mask(flt)
        bm_orig = self.bm25.scores(qp["orig_tokens"]) if qp["orig_tokens"] else np.zeros(len(self.chunks), dtype=np.float32)
        bm_exp = self.bm25.scores(qp["exp_tokens"]) if qp["exp_tokens"] else np.zeros(len(self.chunks), dtype=np.float32)
        bm = self.bm25.scores(toks)
        qv = self.tfidf.transform([qp["expanded"]])
        cs = (self.mat @ qv.T).toarray().ravel()
        # thành phần "cụm từ": số bigram/trigram liền kề của câu hỏi xuất hiện trong chunk (tên riêng nhiều âm tiết, cụm thuật ngữ)
        ot = qp["orig_tokens"]
        qbi, qtri = set(zip(ot, ot[1:])), set(zip(ot, ot[1:], ot[2:]))
        ph = np.array([len(qbi & b) + 2 * len(qtri & t3) for b, t3 in zip(self.bigrams, self.trigrams)], dtype=np.float32) if qbi else np.zeros(len(self.chunks), dtype=np.float32)
        ph = ph + 1e-3 * bm_orig / (bm_orig.max() + 1e-9)  # hoà thì xếp theo BM25
        comps = {"bm25_orig": bm_orig, "bm25_exp": bm_exp, "char_tfidf": cs, "phrase": np.where(ph >= 1.0, ph, 0.0)}
        if self.dense is not None:
            dq = self.dense.encode_queries([query])[0]
            comps["dense"] = self.dense_mat @ dq
        # RRF
        fused = np.zeros(len(self.chunks), dtype=np.float32)
        weights: dict[str, float] = {}  # đã thử phrase=2.0: MRR +0.024 nhưng Recall@5 -0.010 -> không đủ bằng chứng, giữ trọng số đều
        for name, sc in comps.items():
            sc = np.where(mask, sc, -1e9)
            order = np.argsort(-sc)[:100]
            for r, i in enumerate(order):
                if sc[i] > 0:
                    fused[i] += weights.get(name, 1.0) / (60 + r + 1)
        fused = np.where(mask, fused, 0)
        # cụm TÊN RIÊNG (≥2 âm tiết viết hoa liền nhau) khớp NGUYÊN VĂN CÓ DẤU: bỏ dấu làm "O Nhạn" ≈ "ở nhân", "Ngô Thị Diệm" ≈ "ngồi thì diễm"…
        names = [m.lower() for m in re.findall(r"(?:[A-ZÀ-Ỵ][\wÀ-ỹ]*\s+){1,3}[A-ZÀ-Ỵ][\wÀ-ỹ]*", unicodedata.normalize("NFC", query)) if m.split()[0][0].isupper()]
        names = [n for n in names if len(n) >= 5 and fold(n) not in GENERIC_NAME_PHRASES]
        if rerank:
            qbig = set(zip(toks, toks[1:]))
            for i in np.argsort(-fused)[:30]:
                if fused[i] <= 0:
                    continue
                ct = self.tokens[i]
                big = set(zip(ct, ct[1:]))
                bonus = 0.004 * len(qbig & big)
                head = fold((self.chunks[i].get("section") or "") + " " + (self.chunks[i].get("chapter") or "") + " " + " ".join(self.chunks[i].get("keywords") or []))
                bonus += 0.003 * sum(1 for t in set(toks) if len(t) > 3 and t in head)
                if names:
                    body = self.chunks[i]["content"].lower()
                    bonus += 0.03 * sum(1 for n in names if n in body)
                fused[i] += bonus
        order = [i for i in np.argsort(-fused) if fused[i] > 0]
        # Truy vấn không phải tiếng Việt: thêm tối đa 2 đoạn từ kho tài liệu CÙNG ngôn ngữ (vd văn kiện Genève tiếng Anh) nếu phủ khái niệm đủ tốt
        if qp["language"] != "vi" and (qp["orig_tokens"] or qp["groups"]):
            nl = {qp["language"]} | ({"en"} if qp["language"] == "zh" else set())  # tiếng Trung: kho văn kiện ngoài là tiếng Anh
            native = [i for i in order if self.chunks[i]["language"] in nl and self.concept_coverage(qp, i) >= 0.5]
            if not native:
                nat_sc = np.where(mask & np.array([c["language"] in nl for c in self.chunks]), np.maximum(bm_orig, bm_exp), 0)
                native = [i for i in np.argsort(-nat_sc)[:6] if nat_sc[i] > 0 and self.concept_coverage(qp, i) >= 0.5]
            native = native[:2]
            if native:
                fused_nat = {i: fused[i] for i in native}
                rest = [i for i in order if i not in native]
                merged = rest[:2] + native[:1] + rest[2:3] + native[1:2] + rest[3:]
                order = merged
        # Ghi chú đối chiếu nguồn (CURATOR_NOTE) dày từ khoá nên dễ chiếm hạng đầu: KHÔNG cho chiếm suất top-k của tư liệu gốc;
        # nếu một ghi chú nằm trong nhóm đầu (2k) thì gắn thêm đúng 1 ghi chú vào CUỐI danh sách để LLM thấy chỗ các nguồn khác nhau.
        notes = [i for i in order[: max(2 * k, 10)] if self.chunks[i]["source_type"] == "CURATOR_NOTE"][:1]
        order = [i for i in order if self.chunks[i]["source_type"] != "CURATOR_NOTE"][:k] + notes
        hits = []
        for rnk, i in enumerate(order, 1):
            cov = self.concept_coverage(qp, i)
            gate = self.gate_info(qp, i)
            hits.append(Hit(chunk_id=self.chunks[i]["chunk_id"], score=float(fused[i]), rank=rnk,
                            components={n: float(sc[i]) for n, sc in comps.items()}, coverage=cov, gate=gate))
        return hits, qp

    def chunk(self, chunk_id: str) -> dict:
        return self.chunks[self.by_id[chunk_id]]

    def expand_with_neighbors(self, chunks: list[dict], n_top: int = 2) -> list[dict]:
        """Bổ sung đoạn liền kề (trước/sau, CÙNG chương/cùng bài, cùng nguồn) của n_top kết quả đầu: một sự kiện thường kéo dài
        qua nhiều trang/chunk. Đoạn lân cận được đặt SAU toàn bộ kết quả truy xuất để khi context chạm giới hạn ký tự,
        chúng bị cắt trước (không đẩy kết quả xếp hạng cao ra ngoài). Không trùng lặp."""
        seen = {c["chunk_id"] for c in chunks}
        extra: list[dict] = []
        for rank, c in enumerate(chunks[:n_top]):
            if c["source_type"] not in ("BOOK", "SECONDARY_ARTICLE"):  # sách và bài viết: đoạn liền kề cùng nguồn có mạch kể liên tục
                continue
            i = self.by_id[c["chunk_id"]]
            for j in (i - 1, i + 1):
                if 0 <= j < len(self.chunks):
                    nb = self.chunks[j]
                    if nb["source_id"] == c["source_id"] and nb.get("chapter_id") == c.get("chapter_id") and nb["chunk_id"] not in seen:
                        seen.add(nb["chunk_id"]); extra.append(nb)
        return list(chunks) + extra


# cụm viết hoa quá phổ biến (xuất hiện ở hầu hết đoạn) – không coi là tên riêng phân biệt
GENERIC_NAME_PHRASES = {"cau hien luong", "hien luong", "ben hai", "song ben hai", "vinh linh", "viet nam", "quang tri", "hiep dinh geneve"}


class ImageIndex:
    """Truy xuất ẢNH THEO METADATA (metadata-based image retrieval): BM25 trên mô tả/tiêu đề/chữ trong ảnh/chủ đề.
    KHÔNG có image embedding (không tuyên bố multimodal embedding)."""

    def __init__(self, images: list[dict]):
        self.images = [im for im in images if im.get("in_gallery", True)]
        self.tokens = [[t for t in tokenize(im["search_text"]) if t not in STOP] for im in self.images]
        self.bm25 = BM25(self.tokens, k1=1.2, b=0.6)

    def search(self, query: str, k: int = 4, min_coverage: float = 0.6, restrict: set[str] | None = None) -> list[tuple[dict, float, float]]:
        """Xếp hạng ảnh theo metadata; chỉ nhận ảnh phủ >= min_coverage các KHÁI NIỆM trong truy vấn (không chỉ khớp từ chung)."""
        qp_exp, _ = expand_query(query)
        toks = [t for t in tokenize(qp_exp) if t not in STOP]
        groups = match_groups(query)
        orig = [t for t in tokenize(fold(query)) if t not in STOP and t not in GENERIC_Q and len(t) > 1]
        if not toks or (not groups and not orig):
            return []
        sc = self.bm25.scores(toks)
        # thưởng CỤM hai từ liền kề của câu hỏi gốc (vd "bờ nam" ≠ "bờ bắc"; tên file thường là cụm mô tả)
        qo = [t for t in tokenize(fold(query)) if t not in STOP]
        qbig = [f"{a} {b}" for a, b in zip(qo, qo[1:])]
        if qbig:
            for i in np.argsort(-sc)[: 40]:
                if sc[i] > 0:
                    n_b = sum(1 for bg in qbig if bg in self.images[i]["search_text"])
                    sc[i] *= (1.0 + 0.6 * n_b / len(qbig)) * (1.5 if n_b == len(qbig) and len(qbig) >= 2 else 1.0)  # khớp trọn cụm mô tả
        out = []
        for i in np.argsort(-sc)[: 40]:
            if sc[i] <= 0:
                continue
            im = self.images[i]
            if restrict is not None and im["image_id"] not in restrict:
                continue
            folded = im["search_text"]
            if groups:
                cov = sum(1 for _, alts in groups if any(a in folded for a in alts)) / len(groups)
            else:  # không có khái niệm glossary: độ phủ theo cụm/token gốc
                cov = sum(1 for t in orig if t in set(self.tokens[i])) / len(orig)
            if cov >= min_coverage:
                out.append((im, float(sc[i]), cov))
        return out[:k]
