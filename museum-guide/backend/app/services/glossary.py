"""Từ điển thuật ngữ đa ngôn ngữ (vi/en/zh) cho mở rộng truy vấn.

LÝ DO: môi trường phát triển không tải được model embedding đa ngôn ngữ, nên truy vấn tiếng Anh/Trung
cần được ánh xạ sang thuật ngữ tiếng Việt của kho tri thức. Mỗi mục: (khoá, vi[], en[], zh[]).
Đây là bảng thuật ngữ do nhóm phát triển biên soạn (tên riêng & thuật ngữ lịch sử), KHÔNG phải nội dung lịch sử.
"""
from __future__ import annotations

from .text_utils import fold

GLOSSARY = [
    ("hienluong", ["hiền lương", "cầu hiền lương", "hien luong"], ["hien luong", "hien luong bridge", "bridge"], ["贤良", "贤良桥", "桥"]),
    ("benhai", ["bến hải", "sông bến hải", "sông hiền lương"], ["ben hai", "ben hai river", "river"], ["边海", "边海河", "河"]),
    ("parallel17", ["vĩ tuyến 17", "vĩ tuyến", "vi tuyen 17"], ["17th parallel", "seventeenth parallel", "parallel"], ["十七度线", "北纬17度", "17度线"]),
    ("geneva", ["hội nghị genève", "hiệp định genève", "genève", "giơnevơ", "geneve", "geneva"], ["geneva", "geneva conference", "geneva accords", "geneva agreement"], ["日内瓦", "日内瓦协议", "日内瓦会议"]),
    ("demarcation", ["giới tuyến quân sự tạm thời", "giới tuyến"], ["military demarcation line", "demarcation line", "provisional", "demarcation"], ["军事分界线", "临时军事分界线", "分界线"]),
    ("dmz", ["khu phi quân sự"], ["demilitarized zone", "dmz", "demilitarised"], ["非军事区"]),
    ("division", ["chia cắt", "chia đôi đất nước"], ["divided", "division", "partition", "divide", "split"], ["分裂", "分割", "划分", "分治"]),
    ("flagpole", ["cột cờ", "kỳ đài", "lá cờ", "đấu cờ"], ["flagpole", "flag pole", "flag", "flags", "flag duel"], ["旗杆", "旗帜", "国旗", "旗"]),
    ("paint", ["sơn cầu", "hai màu", "cuộc chiến sơn cầu"], ["paint", "painted", "two colors", "two colours", "painting the bridge"], ["涂漆", "刷漆", "两种颜色"]),
    ("loudspeaker", ["phát thanh", "loa", "đấu loa", "phóng thanh"], ["loudspeaker", "loudspeakers", "broadcast", "broadcasting", "radio", "propaganda"], ["广播", "扩音器", "喇叭", "播音"]),
    ("relic", ["di tích", "phục dựng", "phục chế", "phục hồi", "di tích quốc gia đặc biệt", "nhà trưng bày"], ["relic site", "heritage site", "restored", "restoration", "reconstructed", "memorial site", "museum exhibit"], ["遗迹", "遗址", "修复", "复建", "纪念地"]),
    ("announcer", ["phát thanh viên", "o nhạn"], ["announcer", "radio announcer", "broadcaster"], ["播音员"]),
    ("postcard", ["bưu thiếp", "trao đổi bưu thiếp"], ["postcard", "postcards", "mail", "postal"], ["明信片", "邮政"]),
    ("secretline", ["đường dây liên lạc bí mật", "liên lạc bí mật"], ["secret liaison", "secret communication", "secret line", "clandestine"], ["秘密联络线", "秘密交通线"]),
    ("migration", ["di cư", "cưỡng ép di cư"], ["migration", "exodus", "forced migration", "refugees", "migrate"], ["迁移", "移民", "难民", "强迫迁移"]),
    ("police", ["công an", "cảnh sát", "đồn công an"], ["police", "public security", "security force"], ["公安", "警察"]),
    ("icc", ["tổ quốc tế", "ủy ban quốc tế", "ủy hội quốc tế"], ["international commission", "icc", "control commission"], ["国际委员会", "国际监察委员会"]),
    ("jointcommittee", ["ủy ban liên hiệp", "ban liên hiệp"], ["joint commission", "joint committee"], ["联合委员会", "联合委员"]),
    ("election", ["tổng tuyển cử", "thống nhất đất nước", "tái thống nhất"], ["general elections", "election", "elections", "reunification", "unification", "unify"], ["大选", "选举", "统一", "重新统一"]),
    ("diem", ["ngô đình diệm", "chính quyền sài gòn"], ["ngo dinh diem", "diem", "saigon government", "saigon regime"], ["吴廷琰", "西贡政权", "西贡当局"]),
    ("peacefigures", ["tống triệt", "ba nhân vật hòa bình"], ["expelled", "deported", "peace movement", "three peace"], ["驱逐", "和平运动", "三位和平人士"]),
    ("k8", ["kế hoạch k.8", "sơ tán"], ["k.8 plan", "evacuation", "evacuated"], ["K.8计划", "疏散"]),
    ("dienbienphu", ["điện biên phủ"], ["dien bien phu"], ["奠边府"]),
    ("france", ["pháp"], ["france", "french"], ["法国", "法军"]),
    ("us", ["mỹ", "hoa kỳ"], ["united states", "american", "americans", "u.s."], ["美国", "美军"]),
    ("vinhlinh", ["vĩnh linh"], ["vinh linh"], ["永灵"]),
    ("giolinh", ["gio linh"], ["gio linh"], ["嘉灵"]),
    ("cuatung", ["cửa tùng"], ["cua tung"], ["门松", "咸松"]),
    ("question_why", [], ["why", "reason"], ["为什么", "为何", "原因"]),
    ("year1965", ["1965"], ["1965"], ["1965"]),
    ("people_life", ["cuộc sống", "đời sống", "nhân dân", "đồng bào", "gia đình", "chồng bắc vợ nam"], ["daily life", "civilians", "families", "residents"], ["生活", "百姓", "家庭", "人民"]),
    ("vietnam", ["việt nam", "nước việt nam"], ["vietnam", "viet nam", "vietnamese"], ["越南"]),
    ("agreement", ["hiệp định"], ["agreement", "accord", "accords", "treaty"], ["协议", "协定"]),
]

_INDEX = [(k, [fold(x) for x in vi], [fold(x) for x in en], zh) for k, vi, en, zh in GLOSSARY]


def match_groups(query: str) -> list[tuple[str, list[str]]]:
    """Các nhóm khái niệm glossary khớp truy vấn: [(khoá, [cụm đã bỏ dấu (vi + en)])]. Dùng để đo độ phủ theo KHÁI NIỆM."""
    f = fold(query)
    out = []
    for key, vi_f, en_f, zh in _INDEX:
        if key == "question_why":
            continue
        matched = any(t and (f"{t}" in f) for t in en_f if len(t) > 2) or any(z in query for z in zh) or any(t and t in f for t in vi_f if len(t) > 3)
        if matched:
            out.append((key, [t for t in vi_f + en_f if len(t) >= 3]))
    return out


def expand_query(query: str) -> tuple[str, list[str]]:
    """Trả về (folded_query_mở_rộng, danh_sách_khoá_glossary_khớp). Chỉ THÊM từ vi; không bỏ từ gốc."""
    f = fold(query)
    hits: list[str] = []
    extra: list[str] = []
    for key, vi_f, en_f, zh in _INDEX:
        matched = any(t and (f"{t}" in f) for t in en_f if len(t) > 2) or any(z in query for z in zh) or any(
            t and t in f for t in vi_f if len(t) > 3
        )
        if matched and key not in ("question_why",):
            hits.append(key)
            extra.extend(vi_f + en_f)
    return (f + " " + " ".join(extra)).strip(), hits
