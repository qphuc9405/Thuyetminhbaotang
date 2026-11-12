"""Dữ liệu biên soạn cho Knowledge Base: chương (theo MỤC LỤC của sách), chủ đề, nguồn, sự kiện, văn kiện ngoài.

QUY TẮC:
- Mọi sự kiện phải có `page` (số trang IN của sách) và `anchor`: chuỗi PHẢI xuất hiện trong OCR trang đó.
  build_knowledge_base.py kiểm tra anchor; sự kiện không khớp bị gắn cờ `anchor_not_found` (không tự bịa).
- Bản dịch tiêu đề en/zh là bản dịch giao diện của nhóm phát triển, không phải nội dung sách.
- Nội dung văn kiện ngoài (Genève) được DIỄN GIẢI ngắn bằng lời của nhóm, kèm điều khoản; trạng thái xác minh nói rõ
  nguồn xác minh (môi trường không tải được toàn văn - xem PROJECT_STATUS.md).
"""

ACCESSED = "2026-10-30"

SOURCES = [
    dict(source_id="SRC001", title="Đôi bờ giới tuyến (1954–1967)", author="TS. Hoàng Chí Hiếu", publisher="Nhà xuất bản Tổng hợp Thành phố Hồ Chí Minh",
         source_type="BOOK", classification="secondary", url=None, language="vi", document_date="Lời nói đầu ký tháng 7-2014; Lời giới thiệu ký 2014 (PGS.TS Lê Cung)",
         accessed_date=ACCESSED, relevant_content="Nguồn tri thức nền tảng: thiết lập giới tuyến quân sự tạm thời tại vĩ tuyến 17 sau Hiệp định Genève 1954 và các cuộc đấu tranh ở đôi bờ Hiền Lương (1954–1967).",
         relevant_provisions="Toàn bộ 130 trang PDF = 260 trang sách in (mỗi trang PDF là một spread 2 trang)", access_status="accessed (PDF scan, OCR)",
         verification_status="ocr_unverified_manual_review_pending", notes="Bản PDF là ảnh scan độ phân giải thấp (1101x771 px/spread). Văn bản là kết quả OCR Tesseract (vie), có thể sai dấu/ký tự; xem DATASET_DOCUMENTATION.md. Watermark 'tieulun.hopto.org' trên file PDF."),
    dict(source_id="SRC002", title="Archive 2 – bộ ảnh tư liệu giới tuyến Hiền Lương (34 file ảnh)", author="Không xác định", publisher="Không xác định", source_type="ARCHIVAL_PHOTO", classification="primary",
         url=None, language="vi", document_date="Chưa xác định", accessed_date=ACCESSED, relevant_content="34 ảnh về cầu, cổng chào, cột cờ, khẩu hiệu, loa phát thanh ở khu vực giới tuyến.",
         relevant_provisions=None, access_status="accessed (ZIP do người dùng cung cấp)", verification_status="provenance_unverified",
         notes="Ảnh mang watermark 'LIFE' và watermark TikTok (@tt1252hkdthuy, @lyngochungg); một ảnh có chữ 'corbis'. KHÔNG suy ra tác giả/năm chụp/quyền sử dụng. Quyền sử dụng: chưa xác định."),
    dict(source_id="DOC001", title="Agreement on the Cessation of Hostilities in Viet-Nam (Hiệp định đình chỉ chiến sự ở Việt Nam), 20/7/1954", author="Bộ chỉ huy quân đội Pháp và Bộ Tổng tư lệnh Quân đội nhân dân Việt Nam (các bên ký)",
         publisher="Yale Law School – Avalon Project", source_type="HISTORICAL_DOCUMENT", classification="primary", url="https://avalon.law.yale.edu/20th_century/inch001.asp", language="en", document_date="1954-07-20",
         accessed_date=ACCESSED, relevant_content="Chương I: giới tuyến quân sự tạm thời và khu phi quân sự; thời hạn tập kết; quy chế qua lại; quản lý dân sự trong khu phi quân sự.",
         relevant_provisions="Chương I, Điều 1, 2, 3, 6, 7 (đã đối chiếu qua kết quả tìm kiếm của Wikisource/FRUS doc.1035)", access_status="metadata + trích đoạn qua tìm kiếm; KHÔNG tải được toàn văn (host bị chặn)",
         verification_status="partially_verified_via_search_snippets", notes="Ký bởi bộ chỉ huy quân sự Pháp và Việt Minh (Britannica/EBSCO); Nhà nước Việt Nam (Bảo Đại) không ký."),
    dict(source_id="DOC002", title="Final Declaration of the Geneva Conference on the Problem of Restoring Peace in Indo-China (Tuyên bố cuối cùng), 21/7/1954", author="Hội nghị Genève (không có chữ ký của các bên)",
         publisher="Yale Law School – Avalon Project", source_type="HISTORICAL_DOCUMENT", classification="primary", url="https://avalon.law.yale.edu/20th_century/inch005.asp", language="en", document_date="1954-07-21",
         accessed_date=ACCESSED, relevant_content="Điều 6: đường phân định quân sự là tạm thời, không phải ranh giới chính trị hay lãnh thổ; Điều 7: tổng tuyển cử tháng 7/1956 dưới sự giám sát của ủy ban quốc tế; Điều 8: tự do lựa chọn khu vực sinh sống.",
         relevant_provisions="Điều 6, 7, 8 (đối chiếu qua trích đoạn từ Fordham Internet Modern History Sourcebook, CIA Reading Room, tài liệu Wisconsin FRUS)", access_status="metadata + trích đoạn qua tìm kiếm; KHÔNG tải được toàn văn",
         verification_status="partially_verified_via_search_snippets", notes="Tuyên bố không được ký; khác về giá trị pháp lý với Hiệp định đình chỉ chiến sự (DOC001) và các tuyên bố đơn phương."),
    dict(source_id="DOC003", title="FRUS 1952–1954, Vol. XVI (The Geneva Conference), Document 1035: Agreement on the Cessation of Hostilities in Vietnam (IC/42 Rev.2)", author="US Department of State, Office of the Historian",
         publisher="US Government Printing Office (1981); history.state.gov", source_type="HISTORICAL_DOCUMENT", classification="secondary", url="https://history.state.gov/historicaldocuments/frus1952-54v16/d1035", language="en", document_date="1954-07-20 (văn bản); 1981 (ấn bản FRUS)",
         accessed_date=ACCESSED, relevant_content="Bản sao tài liệu do Ban Thư ký quốc tế của Hội nghị chuẩn bị (IC/42 Rev.2), Chương I Điều 1 về đường phân định quân sự tạm thời.",
         relevant_provisions="Chương I, Điều 1–3", access_status="metadata + trích đoạn qua tìm kiếm; KHÔNG tải được toàn văn", verification_status="partially_verified_via_search_snippets", notes="FRUS là ấn phẩm biên tập lại tài liệu ngoại giao Hoa Kỳ."),
    dict(source_id="DOC004", title="FRUS 1952–1954, Vol. XVI, Document 1038: The Final Declaration on Indochina", author="US Department of State, Office of the Historian", publisher="US Government Printing Office (1981); history.state.gov",
         source_type="HISTORICAL_DOCUMENT", classification="secondary", url="https://history.state.gov/historicaldocuments/frus1952-54v16/d1038", language="en", document_date="1954-07-21",
         accessed_date=ACCESSED, relevant_content="Bản Tuyên bố cuối cùng của Hội nghị Genève về Đông Dương theo bản dịch/phát hành của Ban Thư ký (396.1 GE/7–2154).", relevant_provisions="Toàn văn tuyên bố (các đoạn 1–13)",
         access_status="metadata + trích đoạn qua tìm kiếm; KHÔNG tải được toàn văn", verification_status="partially_verified_via_search_snippets", notes=None),
    dict(source_id="DOC005", title="Final Declaration of the Geneva Conference (bản PDF tại UN Peacemaker)", author="Liên Hợp Quốc – Peacemaker", publisher="United Nations Peacemaker", source_type="HISTORICAL_DOCUMENT", classification="primary",
         url="https://peacemaker.un.org/sites/default/files/document/files/2024/05/final20declaration20of20the20geneva20conference20on20the20problem20of20restoring20peace20in20indo.pdf", language="en", document_date="1954-07-21",
         accessed_date=ACCESSED, relevant_content="Nguồn được yêu cầu trong master prompt.", relevant_provisions=None, access_status="CHƯA TRUY CẬP ĐƯỢC (host không nằm trong allowlist của môi trường phát triển)",
         verification_status="not_accessed", notes="Chỉ đăng ký metadata; KHÔNG có bản ghi tri thức nào dựa trực tiếp vào nguồn này."),
    dict(source_id="DOC006", title="FRUS 1952–1954, Vol. XIII Part 2, Document 1073 (Editorial Note on the Geneva Conference conclusion)", author="US Department of State, Office of the Historian", publisher="history.state.gov",
         source_type="HISTORICAL_DOCUMENT", classification="secondary", url="https://history.state.gov/historicaldocuments/frus1952-54v13p2/d1073", language="en", document_date="1954-07-21 (nội dung); ghi chú biên tập",
         accessed_date=ACCESSED, relevant_content="Ghi chú biên tập: Tuyên bố cuối cùng không được ký; tuyên bố đơn phương của Campuchia, Lào, Pháp; tuyên bố của Mỹ (Bedell Smith) và phản đối của phái đoàn Nhà nước Việt Nam.",
         relevant_provisions=None, access_status="trích đoạn qua tìm kiếm", verification_status="partially_verified_via_search_snippets", notes="Nguồn bổ sung ngoài danh sách bắt buộc."),
    dict(source_id="REF001", title="Geneva Accords (Britannica)", author="Encyclopaedia Britannica", publisher="Encyclopaedia Britannica", source_type="REFERENCE_WORK", classification="reference", url="https://www.britannica.com/event/Geneva-Accords", language="en",
         document_date="n/a", accessed_date=ACCESSED, relevant_content="Mô tả bộ 10 văn kiện (3 hiệp định quân sự, 6 tuyên bố đơn phương, Tuyên bố cuối cùng); Tuyên bố cuối cùng không được bên nào ký.", relevant_provisions=None,
         access_status="trích đoạn qua tìm kiếm", verification_status="secondary_reference_snippet", notes="Tài liệu tham khảo (tertiary), không thay thế văn kiện gốc."),
    dict(source_id="REF002", title="Vietnamese Demilitarized Zone (Wikipedia)", author="Wikipedia contributors", publisher="Wikimedia Foundation", source_type="REFERENCE_WORK", classification="reference",
         url="https://en.wikipedia.org/wiki/Vietnamese_Demilitarized_Zone", language="en", document_date="n/a", accessed_date=ACCESSED, relevant_content="Khu phi quân sự rộng khoảng 5 km mỗi bên; ranh giới tạm thời chủ yếu theo sông Bến Hải.",
         relevant_provisions=None, access_status="trích đoạn qua tìm kiếm", verification_status="secondary_reference_snippet", notes="Tài liệu tham khảo mở, dùng để đối chiếu, không dùng làm nguồn chính."),
]

# --- Chương theo MỤC LỤC sách (số trang IN) ---
CHAPTERS = [
    ("C00", "Lời giới thiệu & Lời nói đầu", "Foreword and Preface", "序言与前言", 5, 12, None, "Mở đầu", "intro"),
    ("C01", "Hội nghị Genève (1954) và việc thiết lập giới tuyến quân sự tạm thời ở Việt Nam", "The 1954 Geneva Conference and the provisional military demarcation line in Vietnam", "1954年日内瓦会议与越南临时军事分界线的设立", 15, 33, "Phần 1", "1953–1954", "geneva"),
    ("C02", "Những tên gọi của một dòng sông lịch sử", "The names of a historic river", "一条历史之河的名称", 34, 40, "Phần 1", "Lịch sử các tên gọi sông Hiền Lương/Bến Hải", "river"),
    ("C03", "Sự thiết lập khu phi quân sự – Vĩ tuyến 17 sau Hiệp định Genève 1954", "Establishment of the Demilitarized Zone at the 17th parallel after the 1954 Geneva Agreement", "1954年日内瓦协议后十七度线非军事区的设立", 41, 56, "Phần 1", "1954", "dmz"),
    ("C04", "Lực lượng Công an bảo vệ giới tuyến quân sự tạm thời (1954–1959)", "Public Security forces guarding the provisional demarcation line (1954–1959)", "守卫临时军事分界线的公安力量（1954–1959）", 59, 68, "Phần 2", "1954–1959", "police"),
    ("C05", "Đấu tranh chống Mỹ và chính quyền Sài Gòn cưỡng ép di cư ở khu phi quân sự – Vĩ tuyến 17 những năm sau Hiệp định Genève (1954)", "Struggle against forced migration in the DMZ after the 1954 Geneva Agreement", "非军事区反对强迫迁移的斗争（日内瓦协议后）", 69, 78, "Phần 2", "1954–1955 và sau đó", "migration"),
    ("C06", "Đấu tranh thực hiện Hiệp định Genève ở khu phi quân sự – Vĩ tuyến 17 (7-1954 – 7-1956)", "Struggle to implement the Geneva Agreement in the DMZ (7/1954 – 7/1956)", "非军事区贯彻日内瓦协议的斗争（1954年7月–1956年7月）", 79, 96, "Phần 2", "7-1954 – 7-1956", "implementation"),
    ("C07", "Công tác tranh thủ cảnh sát Sài Gòn của Đồn công an Cửa Tùng, Hiền Lương (1954–1967)", "Winning over Saigon police: the Cua Tung and Hien Luong police posts (1954–1967)", "门松、贤良公安哨所争取西贡警察的工作（1954–1967）", 97, 108, "Phần 2", "1954–1967", "police_outreach"),
    ("C08", "Hệ thống phát thanh tại khu phi quân sự – Vĩ tuyến 17 những năm 1956–1962", "The broadcasting (loudspeaker) system in the DMZ, 1956–1962", "1956–1962年非军事区的广播（扩音）系统", 109, 142, "Phần 2", "1956–1962", "broadcast"),
    ("C09", "Đường dây liên lạc bí mật Bắc – Nam qua giới tuyến quân sự tạm thời (1955–1965)", "Secret North–South liaison lines across the demarcation line (1955–1965)", "跨越临时军事分界线的南北秘密联络线（1955–1965）", 143, 149, "Phần 2", "1955–1965", "secretline"),
    ("C10", "Trao đổi bưu thiếp giữa hai miền Bắc – Nam (5-1955 – 1965)", "Postcard exchange between North and South (5/1955 – 1965)", "南北两方明信片往来（1955年5月–1965）", 150, 182, "Phần 2", "5-1955 – 1965", "postcard"),
    ("C11", "Cầu và cột cờ Hiền Lương", "The Hien Luong bridge and flagpoles", "贤良桥与旗杆", 183, 193, "Phần 2", "1928–2005 (trọng tâm 1954–1967)", "bridgeflag"),
    ("C12", "Vụ “tống triệt” ba nhân vật hòa bình qua cầu Hiền Lương ngày 19-3-1965", "The expulsion of three peace-movement figures across the Hien Luong bridge, 19 March 1965", "1965年3月19日经贤良桥“驱逐”三位和平人士事件", 194, 198, "Phần 2", "1965", "tongtriet"),
    ("C13", "Bến đò Tùng Luật B", "Tung Luat B ferry crossing", "松律B渡口", 199, 208, "Phần 2", "1960–1967", "ferry"),
    ("C14", "Đấu tranh chống gián điệp và biệt kích ở giới tuyến quân sự tạm thời (1960–1964)", "Struggle against spies and commandos at the demarcation line (1960–1964)", "临时军事分界线反间谍与反特工斗争（1960–1964）", 209, 219, "Phần 2", "1960–1964", "espionage"),
    ("C15", "Trận tập kích căn cứ Dốc Miếu", "The raid on the Doc Mieu base", "袭击多庙基地之战", 220, 232, "Phần 2", "1960–1967", "docmieu"),
    ("C16", "Kế hoạch K.8 (1967)", "The K.8 plan (1967)", "K.8计划（1967）", 233, 242, "Phần 2", "1967", "k8"),
    ("C17", "Giải phóng khu phi quân sự Nam, xóa bỏ giới tuyến quân sự tạm thời", "Liberation of the southern DMZ and removal of the provisional demarcation line", "解放南部非军事区，消除临时军事分界线", 243, 256, "Phần 2", "1967", "liberation"),
]

TOPICS = [  # topic_id, vi, en, zh, mô tả (dựa trên tên chương/mục lục), chapter ids
    ("intro", "Mở đầu", "Introduction", "导言", "Lời giới thiệu và lời nói đầu của cuốn sách.", ["C00"]),
    ("geneva", "Hội nghị Genève 1954", "The 1954 Geneva Conference", "1954年日内瓦会议", "Bối cảnh quốc tế và việc thiết lập giới tuyến quân sự tạm thời tại Việt Nam theo sách (chương 1) và các văn kiện Genève.", ["C01"]),
    ("river", "Tên gọi dòng sông Hiền Lương – Bến Hải", "Names of the Hien Luong – Ben Hai river", "贤良—边海河的名称", "Các tên gọi lịch sử của dòng sông.", ["C02"]),
    ("dmz", "Khu phi quân sự – Vĩ tuyến 17", "The Demilitarized Zone at the 17th parallel", "十七度线非军事区", "Quy định và quy hoạch thực tế của khu phi quân sự sau Hiệp định Genève.", ["C03"]),
    ("police", "Lực lượng công an giới tuyến", "Demarcation-line public security forces", "分界线公安力量", "Sự ra đời và phát triển của lực lượng công an bảo vệ giới tuyến; công tác tranh thủ cảnh sát Sài Gòn.", ["C04", "C07"]),
    ("migration", "Di cư và chống cưỡng ép di cư", "Migration and resistance to forced migration", "迁移与反强迫迁移", "Đấu tranh chống cưỡng ép di cư ở khu phi quân sự theo sách (số liệu và quan điểm của sách; chưa đối chiếu nghiên cứu học thuật độc lập).", ["C05"]),
    ("implementation", "Đấu tranh thực hiện Hiệp định Genève (7/1954–7/1956)", "Implementing the Geneva Agreement (7/1954–7/1956)", "贯彻日内瓦协议的斗争（1954.7–1956.7）", "Giai đoạn 1954–1956 theo cách phân kỳ của sách.", ["C06"]),
    ("broadcast", "Đấu loa – hệ thống phát thanh", "The loudspeaker contest: broadcasting system", "“对喊”广播系统", "Hệ thống phát thanh hai bờ Bến Hải những năm 1956–1962.", ["C08"]),
    ("secretline", "Đường dây liên lạc bí mật", "Secret liaison lines", "秘密联络线", "Các tuyến liên lạc bí mật Bắc – Nam.", ["C09"]),
    ("postcard", "Trao đổi bưu thiếp", "Postcard exchange", "明信片往来", "Hình thức trao đổi bưu thiếp giữa hai miền.", ["C10"]),
    ("bridgeflag", "Cầu và cột cờ Hiền Lương", "Hien Luong bridge and flagpoles", "贤良桥与旗杆", "Lịch sử cây cầu, cuộc chiến sơn cầu và cuộc đấu cờ.", ["C11"]),
    ("tongtriet", "Vụ “tống triệt” ngày 19-3-1965", "The expulsion of 19 March 1965", "1965年3月19日“驱逐”事件", "Ba nhân vật phong trào hòa bình bị đưa qua cầu Hiền Lương.", ["C12"]),
    ("late", "Các sự kiện khác tại giới tuyến (1960–1967)", "Other events at the demarcation line (1960–1967)", "分界线其他事件（1960–1967）", "Bến đò Tùng Luật B, chống gián điệp biệt kích, trận Dốc Miếu, kế hoạch K.8, giải phóng khu phi quân sự Nam.", ["C13", "C14", "C15", "C16", "C17"]),
]

def period_of(date_iso: str) -> str:
    y = int(date_iso[:4]); m = int(date_iso[5:7]) if len(date_iso) >= 7 else 1
    if y < 1954: return "pre-1954"
    if (y, m) <= (1956, 7): return "1954-1956"
    return "1956-1967"

# (id, date_iso, label, vi_title, en_title, zh_title, vi_summary, en_summary, page, anchor, topics)
EVENTS = [
 ("EV01", "1928", "1928", "Xây cầu Hiền Lương đầu tiên", "First Hien Luong bridge built", "首座贤良桥建成", "Theo sách, năm 1928 Tri phủ Vĩnh Linh huy động sức dân xây cầu Hiền Lương đầu tiên bằng cọc sắt và gỗ, dài 120 m, rộng 2 m.", "According to the book, in 1928 the Vinh Linh district chief mobilised local labour to build the first Hien Luong bridge (iron piles and timber, 120 m long, 2 m wide).", 183, "nam1928", ["bridgeflag"]),
 ("EV02", "1952", "1952", "Công binh Pháp bắc lại cầu Hiền Lương", "French engineers rebuild the Hien Luong bridge", "法军工兵重建贤良桥", "Theo sách, năm 1952 công binh Pháp bắc lại cầu dài 178 m, 7 nhịp thép, mặt cầu lát gỗ.", "According to the book, in 1952 French engineers rebuilt the bridge: 178 m long, 7 steel spans, timber deck.", 184, "nam1952", ["bridgeflag"]),
 ("EV03", "1953-07-27", "27/7/1953", "Ký Hiệp định đình chiến Triều Tiên", "Korean armistice signed", "朝鲜停战协定签署", "Theo sách, ngày 27-7-1953 Hiệp định đình chiến ở Triều Tiên được ký kết, mở ra xu thế giải quyết xung đột bằng đàm phán và thúc đẩy các nước lớn tìm cách giải quyết vấn đề Đông Dương.", "According to the book, the Korean armistice of 27 July 1953 opened a trend toward negotiated settlements and pushed the great powers to seek a solution for Indochina.", 15, "27-7-1953", ["geneva"]),
 ("EV04", "1954-07-04", "4/7/1954", "Hai đoàn quân sự gặp nhau tại Trung Giã (Thái Nguyên)", "Military delegations meet at Trung Gia", "两军代表在忠嘉会晤", "Theo sách, song song với Hội nghị Genève, từ ngày 4-7-1954 hai đoàn đại biểu của Quân đội nhân dân Việt Nam và Quân đội Liên hiệp Pháp gặp nhau tại Trung Giã (Thái Nguyên) bàn các vấn đề liên quan.", "According to the book, from 4 July 1954 delegations of the Vietnamese People's Army and the French Union forces met at Trung Gia (Thai Nguyen) in parallel with the Geneva Conference.", 44, "4-7-1954", ["geneva"]),
 ("EV05", "1954-07-21", "21/7/1954", "Công bố Tuyên bố cuối cùng của Hội nghị Genève", "Final Declaration of the Geneva Conference issued", "日内瓦会议最后宣言发表", "Theo sách, lúc 15 giờ ngày 21-7-1954 Bản Tuyên bố cuối cùng của Hội nghị Genève được công bố.", "According to the book, the Final Declaration of the Geneva Conference was issued at 15:00 on 21 July 1954. (External sources: the declaration was unsigned.)", 43, "21-7-1954", ["geneva", "dmz"]),
 ("EV06", "1954-08-03", "3/8/1954", "Ký Hiệp nghị thành lập Ủy ban Liên hiệp", "Agreement on the Joint Commission signed", "联合委员会协议签署", "Theo sách, ngày 3-8-1954 Hiệp nghị về việc thành lập Ủy ban Liên hiệp để thi hành Hiệp định Genève được ký kết.", "According to the book, on 3 August 1954 the agreement establishing the Joint Commission to implement the Geneva Agreement was signed.", 44, "3-8-1954", ["dmz", "implementation"]),
 ("EV07", "1954-08-13", "13/8/1954", "Quyết định số 01 của Ủy ban Liên hiệp Trung ương", "Joint Commission Decision No. 01", "联合委员会第01号决定", "Theo sách, ngày 13-8-1954 Ủy ban Liên hiệp Trung ương ra Quyết định số 01 quy định việc vạch giới hạn thực tế của khu phi quân sự, số lượng công an mỗi bên và việc ra vào khu phi quân sự.", "According to the book, on 13 Aug 1954 the Central Joint Commission issued Decision No. 01 on demarcating the DMZ on the ground, police numbers per side and access to the DMZ.", 45, "13-8-1954", ["dmz", "police"]),
 ("EV08", "1954-09-15", "15/9/1954", "Quyết định số 11/QĐ về giới hạn khu phi quân sự", "Decision No. 11/QD on DMZ limits", "关于非军事区界限的第11号决定", "Theo sách, ngày 15-9-1954 Ủy ban Liên hiệp Trung ương ra Quyết định số 11/QĐ quy định về giới hạn của khu phi quân sự ở hai bên giới tuyến quân sự tạm thời.", "According to the book, on 15 Sept 1954 the Central Joint Commission issued Decision No. 11/QD defining the limits of the DMZ on both sides of the provisional line.", 46, "15-9-1954", ["dmz"]),
 ("EV09", "1954-10-08", "8/10/1954", "Dựng cột cờ đầu tiên cao 12 m ở đầu cầu Hiền Lương", "First 12 m flagpole raised at the Hien Luong bridgehead", "贤良桥头立起首根12米旗杆", "Theo sách, ngày 8-10-1954 phía Bắc dựng cột cờ đầu tiên cao 12 m ở sát đầu cầu Hiền Lương, lá cờ rộng 24 m².", "According to the book, on 8 Oct 1954 the northern side raised the first flagpole (12 m) next to the bridgehead, with a 24 m² flag.", 188, "8-10-1954", ["bridgeflag"]),
 ("EV10", "1955-02-21", "21/2/1955", "Hai bên bắt đầu kiểm soát người ra vào khu phi quân sự", "Both sides begin controlling movement in and out of the DMZ", "双方开始管制进出非军事区人员", "Theo sách, đến ngày 21-2-1955 lực lượng công an và cảnh sát của hai bên mới tiến hành kiểm soát người ra vào khu phi quân sự và qua lại giới tuyến.", "According to the book, only by 21 Feb 1955 did the police forces of both sides begin controlling movement into the DMZ and across the demarcation line.", 151, "21-2-1955", ["postcard", "police"]),
 ("EV11", "1955-04-12", "12/4/1955", "Biên bản về việc trao đổi bưu thiếp gia đình", "Minutes on family postcard exchange", "家庭明信片往来会议纪要", "Theo sách, ngày 12-4-1955 hai đoàn chuyên viên bưu điện hai miền lập biên bản về việc trao đổi bưu thiếp gia đình.", "According to the book, on 12 April 1955 postal specialists of the two zones drew up minutes on exchanging family postcards.", 154, "12-4-1955", ["postcard"]),
 ("EV12", "1955-05", "5/1955", "Thiết lập hình thức trao đổi bưu thiếp Bắc – Nam", "Postcard exchange between North and South established", "南北明信片往来机制建立", "Theo sách, trao đổi bưu thiếp được thiết lập vào tháng 5-1955 như một hình thức liên lạc giữa nhân dân hai miền khi đất nước bị chia cắt.", "According to the book, the postcard exchange was set up in May 1955 as a form of contact between people of the two zones.", 150, "thang5-1955", ["postcard"]),
 ("EV13", "1955-06-30", "30/6/1955", "Pháp chuyển giao hệ thống đồn cảnh sát giới tuyến cho chính quyền Ngô Đình Diệm", "France hands the demarcation-line police posts to the Ngo Dinh Diem government", "法国向吴廷琰政权移交分界线警察哨所", "Theo sách, ngày 30-6-1955 Pháp chuyển giao hệ thống đồn cảnh sát giới tuyến cho chính quyền Ngô Đình Diệm; từ đây cuộc đấu tranh nâng cao cột cờ giữa hai bên diễn ra gay gắt hơn.", "According to the book, on 30 June 1955 France handed the line's police posts to the Ngo Dinh Diem government; the flagpole contest then intensified.", 188, "30-6-1955", ["bridgeflag", "police"]),
 ("EV14", "1955-07-17", "17/7/1955", "Hoàn thành việc sơn lại cầu do phía Pháp thực hiện", "French repainting of the bridge completed", "法方完成桥梁重新涂漆", "Theo sách, giữa năm 1955 hai bên thỏa thuận để Tiểu đoàn 26 thuộc Trung đoàn công binh số 4 của Pháp sơn lại cầu; ngày 17-7-1955 công việc hoàn thành.", "According to the book, in mid-1955 it was agreed that a French engineer battalion repaint the bridge; the work was completed on 17 July 1955.", 184, "17-7-1955", ["bridgeflag"]),
 ("EV15", "1956-02", "2/1956", "Chính quyền Ngô Đình Diệm xây cột cờ thép cao 25 m", "Diem government builds a 25 m steel flagpole", "吴廷琰政权建起25米钢旗杆", "Theo sách, tháng 2-1956 chính quyền Ngô Đình Diệm xây cột cờ mới bằng thép cao 25 m, lá cờ rộng 96 m².", "According to the book, in Feb 1956 the Ngo Dinh Diem government built a new 25 m steel flagpole with a 96 m² flag.", 188, "thang2-1956", ["bridgeflag"]),
 ("EV16", "1956-07", "7/1956", "Hạn tổng tuyển cử theo Hiệp định Genève trôi qua", "The Geneva deadline for general elections passes", "日内瓦协议规定的大选期限过去", "Theo sách, sau tháng 7-1956 cuộc tổng tuyển cử tái thống nhất đất nước như quy định của Hiệp định Genève không được Mỹ và chính quyền Sài Gòn thực hiện (đây là nhận định của sách).", "According to the book (its own assessment), after July 1956 the general elections stipulated by the Geneva Agreement were not carried out by the US and the Saigon government.", 150, "sauthang7-1956", ["postcard", "geneva"]),
 ("EV17", "1957-07-19", "19/7/1957", "Khu Vĩnh Linh lắp trụ cờ thép ống cao 32 m", "Vinh Linh area installs a 32 m steel-tube flagpole", "永灵区安装32米钢管旗杆", "Theo sách, ngày 19-7-1957 Khu Vĩnh Linh lắp ráp trụ cờ bằng thép ống cao 32 m, cách đầu cầu khoảng 50 m về phía Bắc, lá cờ rộng 108 m².", "According to the book, on 19 July 1957 Vinh Linh area erected a 32 m steel-tube flagpole about 50 m north of the bridgehead, with a 108 m² flag.", 188, "19-7-1957", ["bridgeflag"]),
 ("EV18", "1958-11-09", "9/11/1958", "Bắt đầu cuộc sơn cầu phía Bắc (Đội sơn cầu 337)", "Northern painting of the bridge begins (Painting Team 337)", "北侧开始涂漆（337涂漆队）", "Theo sách, ngày 9-11-1958 Đội sơn cầu 337 của Ty Giao thông Vĩnh Linh bắt đầu sơn nửa cầu phía Bắc bằng nước sơn nâu đỏ, màu cũ của cầu.", "According to the book, on 9 Nov 1958 Painting Team 337 began painting the northern half in the bridge's old brown-red colour.", 185, "9-11-1958", ["bridgeflag"]),
 ("EV19", "1959-01-16", "16/1/1959", "Sài Gòn hoàn thành sơn nửa cầu phía Nam; cầu có hai màu", "Saigon side finishes painting its half; the bridge has two colours", "西贡方完成南半桥涂漆，桥呈两色", "Theo sách, ngày 16-1-1959 chính quyền Sài Gòn hoàn thành việc sơn nửa cầu phía Nam bằng màu khác (xanh); từ đó cầu Hiền Lương có hai màu.", "According to the book, on 16 Jan 1959 the Saigon authorities finished painting the southern half in a different colour; from then the bridge had two colours.", 186, "16-1-1959", ["bridgeflag"]),
 ("EV20", "1961", "1961", "Phía Nam nâng cột cờ lên 35 m", "The southern side raises its flagpole to 35 m", "南方将旗杆升至35米", "Theo sách, năm 1961 đối phương nâng cột cờ lên 35 m, cao hơn cột cờ phía Bắc lúc đó.", "According to the book, in 1961 the other side raised its pole to 35 m, taller than the northern pole at that time.", 188, "nam1961", ["bridgeflag"]),
 ("EV21", "1962", "1962", "Phía Bắc dựng trụ cờ thép ống cao 38,6 m", "The northern side builds a 38.6 m steel-tube flagpole", "北方建起38.6米钢管旗杆", "Theo sách, năm 1962 phía Bắc xây trụ cờ mới bằng thép ống cao 38,6 m, lá cờ rộng 134 m²; phía Nam không nâng cột cờ thêm.", "According to the book, in 1962 the north built a new 38.6 m steel-tube flagpole with a 134 m² flag; the south did not raise its pole further.", 189, "38,6m", ["bridgeflag"]),
 ("EV22", "1965-02-08", "8/2/1965", "Không quân Mỹ bắt đầu đánh phá Vĩnh Linh", "US air raids on Vinh Linh begin", "美军开始轰炸永灵", "Theo sách, từ ngày 8-2-1965 Mỹ tiến hành chiến tranh phá hoại Vĩnh Linh; cột cờ Hiền Lương trở thành một mục tiêu đánh phá.", "According to the book, from 8 Feb 1965 the US began bombing Vinh Linh; the Hien Luong flagpole became a target.", 190, "8-2-1965", ["bridgeflag", "late"]),
 ("EV23", "1965-03-19", "19/3/1965", "Vụ “tống triệt” ba nhân vật hòa bình qua cầu Hiền Lương", "Three peace-movement figures expelled across the Hien Luong bridge", "三位和平人士经贤良桥被“驱逐”", "Theo sách, ngày 19-3-1965 ba nhân vật của Phong trào Hòa bình ở Sài Gòn bị chính quyền Sài Gòn đưa ra Vĩnh Linh qua cầu Hiền Lương (hồi 12 giờ, theo công điện của phía Sài Gòn).", "According to the book, on 19 March 1965 three figures of the Saigon peace movement were sent across the Hien Luong bridge to Vinh Linh (12:00, per a Saigon-side telegram).", 194, "19-3-1965", ["tongtriet"]),
 ("EV24", "1965-09-17", "17/9/1965", "Máy bay Mỹ ném nhầm vào khu gia binh đồn cảnh sát Xuân Hòa", "US aircraft bomb the Xuan Hoa police families' quarters by mistake", "美机误炸春和警察哨所家属区", "Theo sách, ngày 17-9-1965 sáu máy bay AD.6 ném bom đồn Hiền Lương, bom lạc xuống khu gia binh đồn cảnh sát Xuân Hòa làm chết và bị thương 52 người.", "According to the book, on 17 Sept 1965 six AD-6 aircraft bombed the Hien Luong post; bombs fell on the Xuan Hoa police families' quarters, killing or wounding 52.", 190, "17-9-1965", ["bridgeflag"]),
 ("EV25", "1965-11-13", "13/11/1965", "Bom Mỹ rơi xuống bờ Nam gần cầu Hiền Lương", "US bombs fall on the south bank near the bridge", "美军炸弹落在贤良桥附近南岸", "Theo sách, ngày 13-11-1965 máy bay Mỹ khi oanh tạc khu vực cầu và cột cờ đã ném bom xuống bờ Nam, làm chết một cảnh sát; công văn của tướng Nguyễn Chánh Thi gửi Westmoreland được sách trích.", "According to the book, on 13 Nov 1965 US aircraft raiding the bridge/flagpole area bombed the south bank, killing a policeman; the book cites Gen. Nguyen Chanh Thi's letter to Westmoreland.", 190, "13-11-1965", ["bridgeflag"]),
 ("EV26", "1966-09", "9/1966", "Cầu Hiền Lương bị đánh sập", "The Hien Luong bridge is destroyed", "贤良桥被炸毁", "Theo sách, cầu Hiền Lương là cây cầu nối hai miền cho đến trước khi bị đánh sập vào tháng 9-1966.", "According to the book, the bridge linked the two zones until it was destroyed in September 1966.", 183, "9-1966", ["bridgeflag"]),
 ("EV27", "1967-08-02", "2/8/1967", "Mỹ đánh gãy cột cờ phía Bắc; ta đánh sập cột cờ bờ Nam", "US destroys the northern flagpole; the northern side blows up the southern one", "美军击断北侧旗杆；北方炸毁南岸旗杆", "Theo sách, đến ngày 2-8-1967 Mỹ huy động pháo binh, không quân, hải quân đánh gãy cột cờ của phía Bắc; ngay trong đêm đó phía Bắc đặt bộc phá đánh sập cột cờ ở bờ Nam.", "According to the book, on 2 Aug 1967 US artillery, air and naval forces broke the northern flagpole; that same night the northern side blew up the southern flagpole.", 191, "2-8-1967", ["bridgeflag", "late"]),
 ("EV28", "1967-08-03", "3/8/1967", "Dựng cột cờ gỗ mới ở đồn Hiền Lương", "A new timber flagpole is raised at Hien Luong post", "贤良哨所竖起新木旗杆", "Theo sách, ngày 3-8-1967 đồn công an Hiền Lương dựng lên một cột cờ mới bằng gỗ.", "According to the book, on 3 Aug 1967 Hien Luong police post erected a new timber flagpole.", 192, "3-8-1967", ["bridgeflag", "late"]),
]

# Sự kiện từ văn kiện ngoài (provision thay cho trang)
EXT_EVENTS = [
 ("EV-X01", "1954-07-20", "20/7/1954", "Ký Hiệp định đình chỉ chiến sự ở Việt Nam (Genève)", "Agreement on the Cessation of Hostilities in Viet-Nam signed (Geneva)", "越南停战协定签署（日内瓦）",
  "Hiệp định (ký bởi các bộ chỉ huy quân sự Pháp và Việt Minh) quy định đường phân định quân sự tạm thời với lực lượng Quân đội nhân dân Việt Nam ở phía Bắc và lực lượng Liên hiệp Pháp ở phía Nam, cùng khu phi quân sự rộng không quá 5 km mỗi bên (Chương I, Điều 1).",
  "The agreement, signed by the French and Viet Minh military commands, fixed a provisional military demarcation line with People's Army forces to the north and French Union forces to the south, and a demilitarized zone of no more than 5 km on either side (Chapter I, Article 1).",
  "DOC001", "Chương I, Điều 1", ["geneva", "dmz"]),
]

# Bản ghi tri thức từ văn kiện ngoài: diễn giải của nhóm phát triển, KHÔNG phải toàn văn. (id, source, lang, title, content, provision, date, verification)
EXTERNAL_RECORDS = [
 ("KX001", "DOC001", "vi", "Hiệp định đình chỉ chiến sự 20/7/1954 – Điều 1: đường phân định quân sự tạm thời và khu phi quân sự",
  "Điều 1, Chương I của Hiệp định đình chỉ chiến sự ở Việt Nam (20-7-1954) quy định một đường phân định quân sự TẠM THỜI; sau khi rút quân, lực lượng của Quân đội nhân dân Việt Nam tập kết ở phía Bắc đường này và lực lượng Liên hiệp Pháp ở phía Nam. Hiệp định cũng thiết lập một khu phi quân sự ở hai bên đường phân định, rộng không quá 5 km tính từ đường, làm vùng đệm để tránh các sự cố có thể làm chiến sự tái diễn. (Diễn giải của nhóm phát triển từ trích đoạn văn kiện; không phải toàn văn.)",
  "Chương I, Điều 1", "1954-07-20", "partially_verified_via_search_snippets"),
 ("KX002", "DOC001", "en", "Cessation of Hostilities Agreement (20 July 1954) – Article 1: provisional military demarcation line and DMZ",
  "Article 1 of Chapter I of the Agreement on the Cessation of Hostilities in Viet-Nam (20 July 1954) provides for a PROVISIONAL military demarcation line: after withdrawal, People's Army of Viet-Nam forces regroup north of the line and French Union forces south of it. A demilitarized zone is established on either side of the line, no more than 5 km wide from it, acting as a buffer to avoid incidents that might resume hostilities. (Paraphrase by the development team from document excerpts; not the full text.)",
  "Chapter I, Article 1", "1954-07-20", "partially_verified_via_search_snippets"),
 ("KX003", "DOC001", "vi", "Hiệp định 20/7/1954 – Điều 2, 6, 7: thời hạn tập kết, qua lại giới tuyến, quản lý dân sự khu phi quân sự",
  "Theo Hiệp định đình chỉ chiến sự (20-7-1954): Điều 2 – việc di chuyển lực lượng của mỗi bên về vùng tập kết không quá 300 ngày kể từ ngày hiệp định có hiệu lực; Điều 6 – không ai (quân nhân hay dân thường) được phép vượt đường phân định quân sự tạm thời nếu không được Ủy ban Liên hợp cho phép cụ thể; Điều 7 – việc quản lý dân sự và cứu trợ trong khu phi quân sự ở mỗi bên đường phân định thuộc trách nhiệm của Tổng tư lệnh bên đó. (Diễn giải của nhóm phát triển; chưa đối chiếu toàn văn.)",
  "Chương I, Điều 2, 6, 7", "1954-07-20", "partially_verified_via_search_snippets"),
 ("KX004", "DOC001", "en", "Agreement (20 July 1954) – Articles 2, 6, 7: regroupment period, crossing the line, civil administration of the DMZ",
  "Under the Agreement on the Cessation of Hostilities in Viet-Nam: Article 2 – movement of each party's forces into its regrouping zone must be completed within 300 days of the agreement's entry into force; Article 6 – no person, military or civilian, may cross the provisional military demarcation line unless specifically authorised by the Joint Commission; Article 7 – civil administration and relief in the DMZ on either side of the line is the responsibility of that side's Commander-in-Chief. (Paraphrase; full text not retrieved.)",
  "Chapter I, Articles 2, 6, 7", "1954-07-20", "partially_verified_via_search_snippets"),
 ("KX005", "DOC002", "vi", "Tuyên bố cuối cùng 21/7/1954 – đoạn 6–7: giới tuyến là tạm thời, không phải biên giới; tổng tuyển cử 7/1956",
  "Tuyên bố cuối cùng của Hội nghị Genève (21-7-1954) nêu rằng mục đích chủ yếu của hiệp định liên quan đến Việt Nam là giải quyết các vấn đề quân sự để chấm dứt chiến sự, và đường phân định quân sự là TẠM THỜI, không được hiểu theo bất kỳ cách nào là ranh giới chính trị hay lãnh thổ (đoạn 6). Tuyên bố dự kiến tổng tuyển cử vào tháng 7-1956 dưới sự giám sát của một ủy ban quốc tế (đoạn 7); đoạn 8 nêu việc mọi người được tự do chọn khu vực sinh sống. (Diễn giải của nhóm phát triển; đoạn 8 đối chiếu qua trích đoạn thứ cấp.)",
  "Đoạn 6, 7, 8", "1954-07-21", "partially_verified_via_search_snippets"),
 ("KX006", "DOC002", "en", "Final Declaration (21 July 1954) – paragraphs 6–7: the line is provisional, not a boundary; elections in July 1956",
  "The Final Declaration of the Geneva Conference (21 July 1954) states that the essential purpose of the agreement relating to Viet-Nam is to settle military questions to end hostilities, and that the military demarcation line is provisional and should not in any way be interpreted as a political or territorial boundary (paragraph 6). It foresees general elections in July 1956 under the supervision of an international commission (paragraph 7); paragraph 8 concerns the freedom of everyone to choose in which zone to live. (Paraphrase; paragraph 8 cross-checked via secondary excerpts.)",
  "Paragraphs 6, 7, 8", "1954-07-21", "partially_verified_via_search_snippets"),
 ("KX007", "DOC006", "en", "Legal status: the Final Declaration was unsigned; unilateral statements (US, State of Vietnam)",
  "An editorial note in FRUS records that an unsigned Final Declaration was issued on 21 July 1954, together with unilateral declarations by Cambodia, Laos and France; at the final plenary the US Under Secretary of State Walter Bedell Smith declared that the US took note of the agreements and paragraphs 1–12 and would refrain from the threat or use of force to disturb them, and restated US policy on free elections; the Vietnamese (State of Vietnam) statement protested the partition. (Paraphrase of a FRUS editorial note.)",
  "Editorial note", "1954-07-21", "partially_verified_via_search_snippets"),
 ("KX008", "REF001", "en", "Legal distinction between the Geneva documents",
  "According to Britannica, the Geneva Accords comprise ten documents, none of them treaties binding the participants: three military agreements, six unilateral declarations and the Final Declaration of 21 July 1954, which no party signed. The Agreement on the Cessation of Hostilities in Viet-Nam (20 July 1954) was signed by the French and Viet Minh military commands; it is therefore different in legal character from the unsigned Final Declaration and from individual states' unilateral declarations. (Reference-work summary; secondary.)",
  "Overview", "1954-07-21", "secondary_reference_snippet"),
 ("KX009", "REF002", "en", "The provisional line and the 17th parallel",
  "The provisional military demarcation line is commonly described as 'at the 17th parallel', but it follows the Ben Hai river for much of its course; the DMZ is described as a buffer of about 5 km on either side. The line was explicitly provisional pending elections and is distinct from a national border. (Reference-work summary; secondary; the book's own account of the DMZ delimitation is in chapter 3, printed pp. 41–56.)",
  "Overview", "1954-07-20", "secondary_reference_snippet"),
 ("KX010", "DOC002", "vi", "Phân biệt giá trị pháp lý của các văn kiện Genève",
  "Cần phân biệt: (1) Hiệp định đình chỉ chiến sự ở Việt Nam ngày 20-7-1954, do các bộ chỉ huy quân sự Pháp và Việt Minh ký; (2) Tuyên bố cuối cùng của Hội nghị ngày 21-7-1954, không có chữ ký của bên nào; (3) các tuyên bố đơn phương của từng nước (Campuchia, Lào, Pháp; Mỹ và Nhà nước Việt Nam đưa ra tuyên bố riêng). Không nên coi mọi văn bản về Genève có cùng giá trị pháp lý. Giới tuyến quân sự tạm thời không phải là biên giới quốc gia. (Tổng hợp của nhóm phát triển từ DOC001, DOC002, DOC006, REF001.)",
  "Tổng hợp", "1954-07-21", "partially_verified_via_search_snippets"),
]

# Chú thích hình trong sách: do người phát triển ĐỌC TRỰC TIẾP từ crop; truncated=True nếu chú thích bị cắt
BOOK_FIGURES = {
 "FIG_P010_1": dict(kind="book_figure", title="Toàn cảnh Hội nghị Genève 1954", caption="Toàn cảnh Hội nghị Genève 1954 (Ảnh: Freddy Bertrand)", topics=["geneva"],
                    visual="Ảnh đen trắng chụp từ trên cao một hội trường lớn: các đại biểu ngồi quanh bàn hội nghị hình chữ U/bán nguyệt, nhiều người ở hàng ghế sau và ban công.", context="Hình in trong chương 'Hội nghị Genève (1954)…' của sách; chú thích sách ghi tác giả ảnh Freddy Bertrand."),
 "FIG_P019_1": dict(kind="book_figure", title="Ngã ba sông Hiền Lương nhìn từ không ảnh bờ Nam", caption="Ngã ba sông Hiền Lương nhìn từ không ảnh bờ Nam (Nguồn: www.panoramio.com)", topics=["river"],
                    visual="Ảnh đen trắng chụp từ trên cao: dòng sông rộng chảy rẽ ngã ba, ruộng đồng ở bờ gần, một cây cầu mảnh ở góc phải.", context="Hình in trong chương 'Những tên gọi của một dòng sông lịch sử'."),
 "FIG_P027_1": dict(kind="book_figure", title="Bản đồ khu phi quân sự – Vĩ tuyến 17 năm 1957", caption="Bản đồ khu phi quân sự – Vĩ tuyến 17 năm 1957 (Nguồn: Trung tâm Lưu trữ Quốc gia II, Tp. Hồ Chí Minh, kí hiệu TĐB 664/4; đọc từ chữ dọc cạnh bản đồ, có thể chưa đầy đủ)", topics=["dmz"],
                    visual="Bản đồ nét đen trên nền trắng: đường ranh giới khu phi quân sự, sông ngòi và nhiều địa danh viết tay nhỏ, chữ dọc ở cạnh phải.", context="Hình in trong chương 'Sự thiết lập khu phi quân sự – Vĩ tuyến 17…'."),
 "FIG_P031_1": dict(kind="book_figure", title="Kiểm soát liên hợp tại Cửa Tùng", caption="Kiểm soát liên hợp tại Cửa Tùng (Nguồn: dulichquangtri.gov.vn)", topics=["dmz", "police"],
                    visual="Ảnh đen trắng: một chiếc thuyền buồm kéo lên bãi cát, vài người mặc quần áo sáng màu đứng cạnh thuyền, rừng cây phía sau.", context="Hình in trong chương 'Lực lượng Công an bảo vệ giới tuyến quân sự tạm thời'."),
 "FIG_P041_1": dict(kind="book_figure", title="Âm mưu chia cắt đất nước của Ngô Đình Diệm", caption="Âm mưu chia cắt đất nước của Ngô Đình Diệm (Nguồn: http://s1150.photobucket.com)", topics=["bridge", "banner_diem"],
                    visual="Ảnh đen trắng: băng-rôn 'MUỐN THỐNG NHẤT LÃNH THỔ PHẢI CÓ TỔNG THỐNG NGÔ ĐÌNH DIỆM' trên hai cột, một người mặc cảnh phục đứng ở chòi gác, dốc cầu và thanh chắn, biển '12T'.", context="Hình in ở tr.81, chương 'Đấu tranh thực hiện Hiệp định Genève ở khu phi quân sự'. Trùng với IMG007/IMG032 trong bộ ảnh ZIP."),
 "FIG_P044_1": dict(kind="book_figure", title="Nhân dân Vĩnh Linh gửi kiến nghị cho Tổ Quốc tế 76", caption="Nhân dân Vĩnh Linh gửi kiến nghị cho Tổ Quốc tế 76 (Nguồn: Tư liệu của ông Huỳnh … – chú thích bị cắt trong OCR)", topics=["implementation"],
                    visual="Ảnh đen trắng: nhiều người mặc quân phục hoặc thường phục (có người đội mũ cối) đi trên mặt cầu ván gỗ; tháp canh ở phía xa.", context="Hình in trong chương 'Đấu tranh thực hiện Hiệp định Genève ở khu phi quân sự' (tr.87)."),
 "FIG_P056_1": dict(kind="book_figure", title="Sơ đồ hệ thống phóng thanh Bến Hải (2 bờ Nam Bắc)", caption="Sơ đồ hệ thống loa phát thanh ở đôi bờ Hiền Lương (Nguồn: Trung tâm Lưu trữ Quốc gia … – chú thích bị cắt trong OCR)", topics=["broadcast"],
                    visual="Sơ đồ nét đen: dòng sông uốn khúc, nhiều điểm đánh dấu địa danh hai bờ, ô chú giải ở góc dưới phải, tiêu đề 'HỆ THỐNG PHÓNG THANH BẾN HẢI (2 bờ Nam Bắc)'.", context="Hình in trong chương 'Hệ thống phát thanh tại khu phi quân sự' (tr.112)."),
 "FIG_P068_1": dict(kind="book_figure", title="Đoàn quân nhạc hướng về bờ Nam kỷ niệm 10 năm Hiệp định Genève", caption="Đoàn quân nhạc hướng về bờ Nam biểu diễn nhân dịp kỷ niệm 10 năm ngày ký kết Hiệp định Genève (20-7-1964). Nguồn: tuoitre.vn", topics=["broadcast", "implementation"],
                    visual="Ảnh đen trắng: một đoàn người mặc quân phục sáng đứng thành hàng trên bãi cỏ, có bục/hàng rào ở phía xa.", context="Hình in trong chương 'Hệ thống phát thanh…' (tr.135); chú thích sách nêu ngày 20-7-1964."),
 "FIG_P077_1": dict(kind="book_figure", title="Bưu thiếp trao đổi giữa nhân dân hai miền Nam – Bắc (1955–1965)", caption="Một bưu thiếp trao đổi giữa nhân dân hai miền Nam – Bắc trong những năm 1955 – 1965 (Nguồn: Tư liệu của Nhà sưu tập tem Trần Trọng Khải, ở Thành phố Hồ Chí Minh gửi cho tác giả)", topics=["postcard"],
                    visual="Ảnh bưu thiếp hai mặt trên nền đen: mặt trên có tem/dấu bưu điện và bản đồ Việt Nam nhỏ, dòng chữ 'Đưa thiếp'; mặt dưới là mẫu điền chữ viết tay.", context="Hình in trong chương 'Trao đổi bưu thiếp giữa hai miền Bắc – Nam' (tr.153)."),
 "FIG_P094_1": dict(kind="book_figure", title="Cây cầu Hiền Lương có hai màu", caption="Cây cầu Hiền Lương có hai màu (Nguồn: http://s1150.photobucket.com)", topics=["bridge", "bridgeflag"],
                    visual="Ảnh đen trắng chụp từ cao: cây cầu thép dài bắc qua mặt sông, đầu cầu gần có xe jeep và nhóm người, phía xa là hàng cây và nhà thấp.", context="Hình in ở tr.187, chương 'Cầu và cột cờ Hiền Lương'. Trùng với IMG034 (và cùng cảnh với IMG004) trong bộ ảnh ZIP."),
 "FIG_P099_1": dict(kind="book_figure", title="Đón tiếp ba nhân sĩ trí thức phong trào hòa bình", caption="Đón tiếp ba nhân sĩ trí thức tham gia phong trào hòa bình, bị chính quyền Sài Gòn … (chú thích bị cắt trong OCR)", topics=["tongtriet"],
                    visual="Ảnh đen trắng: một nhóm người, nhiều người mặc vest và quân phục, bước đi về phía máy ảnh trên mặt cầu.", context="Hình in trong chương 'Vụ tống triệt ba nhân vật hòa bình qua cầu Hiền Lương ngày 19-3-1965' (tr.197). Chú thích bị cắt nên không nêu tên người."),
 "FIG_P121_1": dict(kind="book_figure", title="Nhân dân Vĩnh Linh đón học sinh sơ tán theo kế hoạch K.8 trở về", caption="Nhân dân Vĩnh Linh đón học sinh được sơ tán theo kế hoạch K.8 trở về quê hương (chú thích bị cắt trong OCR)", topics=["late"],
                    visual="Ảnh đen trắng: đông người trong công viên/bãi cây, một số người đội nón lá, xe chở đồ đạc.", context="Hình in trong chương 'Giải phóng khu phi quân sự Nam…' (tr.241)."),
 "FIG_P001_1": dict(kind="cover_design", title="Tên sách trên bìa (thiết kế bìa)", caption="", topics=[], visual="Chữ tiêu đề 'ĐÔI BỜ GIỚI TUYẾN (1954 – 1967)' bị cắt ở giữa gáy.", context="Thiết kế bìa sách, không phải ảnh tư liệu lịch sử."),
 "FIG_P130_1": dict(kind="cover_design", title="Bìa sau sách (trích Lời nói đầu)", caption="", topics=[], visual="Nền xanh đậm, đoạn trích văn bản trắng và mã vạch/QR ở góc dưới.", context="Thiết kế bìa sau sách, không phải ảnh tư liệu lịch sử."),
 "FIG_P130_2": dict(kind="cover_design", title="Tên sách trên bìa (thiết kế bìa)", caption="", topics=[], visual="Chữ tiêu đề 'ĐÔI BỜ GIỚI TUYẾN (1954 – 1967)' trên bìa sau, bị cắt.", context="Thiết kế bìa sách, không phải ảnh tư liệu lịch sử."),
}

# ---------------------------------------------------------------------------
# CÂU CHUYỆN TRANG CHỦ (4 chương). Mỗi câu khẳng định lịch sử đều có trích dẫn; "anchors" = chuỗi phải có trong OCR
# trang in tương ứng (build_knowledge_base.py kiểm tra). Văn dẫn chuyện do nhóm biên soạn từ các trang đó, KHÔNG thêm
# tình tiết. Bản en/zh là bản dịch của nhóm phát triển.
# ---------------------------------------------------------------------------
STORY = [
 dict(id="ch1", period="1954", image="BKFIG02", topic="geneva", timeline="1954-1956",
      title=("Một dòng sông trở thành giới tuyến", "A river becomes a demarcation line", "一条河成为分界线"),
      lead=("Mùa hè năm 1954, Hội nghị Genève khép lại cuộc chiến tranh Đông Dương – và một dòng sông hiền hòa ở Quảng Trị bước vào lịch sử.",
            "In the summer of 1954 the Geneva Conference ended the Indochina War – and a quiet river in Quảng Trị entered history.",
            "1954年夏，日内瓦会议结束了印度支那战争——广治省一条平静的河流从此走进了历史。"),
      body=(["Theo cuốn sách, tại Hội nghị Genève, Việt Nam phải chấp nhận lấy vĩ tuyến 17 làm giới tuyến quân sự tạm thời, với thời hạn tổng tuyển cử tái thống nhất đất nước là hai năm.",
             "Hiệp định đình chỉ chiến sự ngày 20-7-1954 quy định một đường phân định quân sự tạm thời và khu phi quân sự rộng không quá 5 km mỗi bên; Tuyên bố cuối cùng ngày 21-7-1954 khẳng định đường ấy không phải là ranh giới chính trị hay lãnh thổ.",
             "Tác giả viết rằng một dòng sông hiền hòa như bao dòng sông khác đã bị chọn làm giới tuyến quân sự tạm thời."],
            ["According to the book, at the Geneva Conference Vietnam had to accept the 17th parallel as a provisional military demarcation line, with general elections for reunification due within two years.",
             "The Agreement on the Cessation of Hostilities of 20 July 1954 set a provisional military demarcation line and a demilitarized zone no wider than 5 km on each side; the Final Declaration of 21 July 1954 stated that the line was not a political or territorial boundary.",
             "As the author puts it, a peaceful river like any other was chosen to become the provisional military demarcation line."],
            ["书中指出，在日内瓦会议上，越南不得不接受以北纬17度线作为临时军事分界线，并规定两年内举行重新统一的普选。",
             "1954年7月20日的停战协定规定了一条临时军事分界线，以及两侧各不超过5公里的非军事区；1954年7月21日的最后宣言强调这条线不是政治或领土边界。",
             "作者写道，一条与其他河流一样平静的河，被选作了临时军事分界线。"]),
      cites=[("SRC001", 15, None, "2 năm"), ("DOC001", None, "Chương I, Điều 1", None), ("DOC002", None, "Đoạn 6", None), ("SRC001", 9, None, "hiền hòa")]),
 dict(id="ch2", period="1952–1959", image="IMG034", topic="bridgeflag", timeline="1956-1967",
      title=("Cây cầu mang hai màu", "The bridge of two colours", "两种颜色的桥"),
      lead=("Dài 178 mét, bảy nhịp thép, mặt lát gỗ – cây cầu Hiền Lương từng nối hai bờ, rồi bị chia đôi bởi một vạch sơn.",
            "178 metres long, seven steel spans, a timber deck – the Hiền Lương bridge once joined two banks, then was split by a line of paint.",
            "全长178米、七个钢跨、木质桥面——贤良桥曾连接两岸，后来却被一道油漆分成两半。"),
      body=(["Cây cầu do công binh Pháp bắc lại năm 1952. Sau Hiệp định Genève, cầu bị chia đôi, mỗi bên dài 89 mét.",
             "Tháng 11-1958, Đội sơn cầu 337 của Ty Giao thông Vĩnh Linh sơn nửa cầu phía Bắc bằng màu nâu đỏ vốn có. Phía Sài Gòn sơn nửa cầu phía Nam bằng màu khác và hoàn thành ngày 16-1-1959; từ đó cầu mang hai màu.",
             "Theo cuốn sách, với nhân dân Việt Nam, cầu Hiền Lương là biểu tượng của nỗi đau chia cắt và khát vọng thống nhất đất nước."],
            ["French engineers rebuilt the bridge in 1952. After the Geneva Agreement it was split in two, each half 89 metres long.",
             "In November 1958 Painting Team 337 of the Vinh Linh transport service painted the northern half in its original brown-red. The Saigon side painted the southern half a different colour, finishing on 16 January 1959; from then on the bridge had two colours.",
             "According to the book, for the Vietnamese people the Hiền Lương bridge became a symbol of the pain of division and the longing for reunification."],
            ["这座桥于1952年由法军工兵重建。日内瓦协议后，桥被一分为二，每侧长89米。",
             "1958年11月，永灵交通处337涂漆队用桥原有的棕红色涂刷北半桥；西贡方面以另一种颜色涂刷南半桥，于1959年1月16日完工，从此桥呈两种颜色。",
             "书中写道，对越南人民而言，贤良桥成为分裂之痛与统一渴望的象征。"]),
      cites=[("SRC001", 184, None, "nam1952"), ("SRC001", 184, None, "89m"), ("SRC001", 185, None, "doi son cau 337"), ("SRC001", 186, None, "16-1-1959"), ("SRC001", 183, None, "bieu tuong")]),
 dict(id="ch3", period="1955–1965", image="IMG015", topic="bridgeflag", timeline="1956-1967",
      title=("Những năm tháng bên bờ giới tuyến", "Years on the banks of the line", "分界线两岸的岁月"),
      lead=("Hai bờ chỉ cách nhau chưa đầy trăm mét, nhưng gia đình phải nhờ bưu thiếp để báo tin, còn tiếng loa và lá cờ trở thành cuộc đối thoại không lời.",
            "The banks were less than a hundred metres apart, yet families had to rely on postcards for news, while loudspeakers and flags became a wordless dialogue.",
            "两岸相距不到一百米，家人却只能靠明信片互通音讯，而广播与旗帜成了无声的对话。"),
      body=(["Lời nói đầu của cuốn sách nhắc đến dòng sông rộng chưa đầy 100 mét và bao gia đình lâm vào cảnh “chồng Bắc vợ Nam”.",
             "Từ tháng 5-1955, trao đổi bưu thiếp trở thành hình thức liên lạc giữa nhân dân hai miền. Những năm 1956–1962, hệ thống phát thanh hai bờ diễn ra cuộc “đấu loa”.",
             "Ở đầu cầu, hai bên thi nhau nâng cao cột cờ: từ cột 12 mét năm 1954 đến trụ thép 38,6 mét năm 1962. Mẹ Ngô Thị Diệm ở thôn Hiền Lương ở lại khâu vá từng lá cờ."],
            ["The book's preface mentions a river less than 100 metres wide and many families split \"husband in the North, wife in the South\".",
             "From May 1955 postcard exchange became the way people of the two zones kept in touch. Between 1956 and 1962 the loudspeaker systems of the two banks fought a \"loudspeaker contest\".",
             "At the bridgehead the two sides kept raising their flagpoles: from a 12-metre pole in 1954 to a 38.6-metre steel mast in 1962. Mother Ngô Thị Diệm of Hiền Lương village stayed behind to mend the flags."],
            ["书的前言提到这条河宽不到100米，许多家庭陷入“丈夫在北、妻子在南”的境地。",
             "自1955年5月起，交换明信片成为南北两地人民联系的方式。1956至1962年间，两岸的广播系统展开了“对喊”。",
             "在桥头，双方竞相加高旗杆：从1954年的12米旗杆到1962年38.6米的钢管旗杆。贤良村的吴氏琰妈妈留下来一针一线地缝补旗帜。"]),
      cites=[("SRC001", 9, None, "100m"), ("SRC001", 150, None, "thang 5-1955"), ("SRC001", 109, None, "1956 - 1962"), ("SRC001", 188, None, "8-10-1954"), ("SRC001", 189, None, "38,6m"), ("SRC001", 192, None, "ngo thi diem")]),
 dict(id="ch4", period="1965–1967", image="BKFIG13", topic="late", timeline="1956-1967",
      title=("Khát vọng thống nhất", "The longing for reunification", "统一的渴望"),
      lead=("Bom đạn trút xuống đôi bờ, cây cầu sụp đổ, cột cờ gãy rồi lại được dựng lên – cho đến ngày đường chia cắt bị xóa bỏ trên thực tế.",
            "Bombs fell on both banks, the bridge collapsed, the flagpole fell and was raised again – until the dividing line was erased in practice.",
            "炸弹落在两岸，大桥坍塌，旗杆倒下又重新竖起——直到分界线在事实上被消除。"),
      body=(["Từ ngày 8-2-1965, Mỹ tiến hành chiến tranh phá hoại Vĩnh Linh, cột cờ Hiền Lương trở thành một mục tiêu đánh phá. Cầu Hiền Lương bị đánh sập vào tháng 9-1966.",
             "Ngày 2-8-1967, cột cờ phía Bắc bị đánh gãy; ngay đêm đó phía Bắc đánh sập cột cờ bờ Nam. Hôm sau, đồn công an Hiền Lương dựng một cột cờ mới bằng gỗ.",
             "Theo lời nói đầu, đến năm 1967, khi khu phi quân sự Nam được giải phóng, đường giới tuyến quân sự tạm thời chia cắt đất nước được xóa bỏ trên thực tế."],
            ["From 8 February 1965 the United States waged an air war on Vinh Linh, and the Hiền Lương flagpole became a target. The bridge was destroyed in September 1966.",
             "On 2 August 1967 the northern flagpole was broken; that same night the northern side blew up the flagpole on the southern bank. The next day the Hiền Lương police post raised a new wooden flagpole.",
             "According to the preface, in 1967, when the southern part of the demilitarized zone was liberated, the provisional demarcation line dividing the country was erased in practice."],
            ["自1965年2月8日起，美国对永灵展开轰炸，贤良旗杆成为攻击目标。贤良桥于1966年9月被炸毁。",
             "1967年8月2日，北岸旗杆被炸断；当夜北方炸毁了南岸旗杆。次日，贤良公安哨所竖起了一根新的木旗杆。",
             "据前言所述，1967年南部非军事区获得解放，分割国家的临时军事分界线在事实上被消除。"]),
      cites=[("SRC001", 190, None, "8-2-1965"), ("SRC001", 183, None, "9-1966"), ("SRC001", 191, None, "2-8-1967"), ("SRC001", 192, None, "3-8-1967"), ("SRC001", 10, None, "1967")]),
]

# Ảnh minh hoạ cho sự kiện timeline: relation "illustrates" = căn cứ trực tiếp (chú thích sách); "illustrates_topic" = ảnh cùng
# chủ đề/địa điểm, KHÔNG phải ảnh chụp tại sự kiện (giao diện phải ghi rõ). Sự kiện không có ảnh phù hợp thì để trống.
EVENT_ILLUSTRATIONS = {
    "EV03": ("FIG_P010_1", "illustrates_topic"), "EV04": ("FIG_P010_1", "illustrates_topic"), "EV05": ("FIG_P010_1", "illustrates_topic"), "EV-X01": ("FIG_P010_1", "illustrates_topic"),
    "EV06": ("FIG_P027_1", "illustrates_topic"), "EV07": ("FIG_P027_1", "illustrates_topic"), "EV08": ("FIG_P027_1", "illustrates_topic"),
    "EV10": ("FIG_P031_1", "illustrates_topic"), "EV11": ("FIG_P077_1", "illustrates_topic"), "EV12": ("FIG_P077_1", "illustrates_topic"), "EV16": ("FIG_P077_1", "illustrates_topic"),
    "EV01": ("IMG029", "illustrates_topic"), "EV02": ("IMG029", "illustrates_topic"), "EV14": ("IMG029", "illustrates_topic"), "EV18": ("IMG029", "illustrates_topic"), "EV26": ("IMG029", "illustrates_topic"),
    "EV09": ("IMG015", "illustrates_topic"), "EV13": ("IMG015", "illustrates_topic"), "EV15": ("IMG015", "illustrates_topic"), "EV17": ("IMG015", "illustrates_topic"),
    "EV20": ("IMG015", "illustrates_topic"), "EV21": ("IMG015", "illustrates_topic"), "EV27": ("IMG015", "illustrates_topic"), "EV28": ("IMG015", "illustrates_topic"),
    "EV23": ("FIG_P099_1", "illustrates"),
}
