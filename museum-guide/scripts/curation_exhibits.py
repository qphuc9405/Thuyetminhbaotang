"""GIAN TRƯNG BÀY SỐ (Nhà trưng bày) + nội dung các KHU VỰC trên bản đồ tham quan.

- EXHIBITS: hiện vật/ảnh do nhóm biên soạn. Mỗi hiện vật có 2–3 đoạn thuyết minh viết lại từ nguồn trong kho; trích dẫn sách/bài viết
  có `anchor` để build kiểm tra trong OCR trang in hoặc đúng dòng tệp gốc. Ảnh còn lại của bộ sưu tập được build tự thêm vào
  gian trưng bày, thuyết minh lấy từ metadata đã biên soạn (mô tả hình ảnh + bối cảnh có nguồn).
- PLACES: Tượng đài, Nhà liên hợp – lịch sử hình thành từ nguồn web (diễn giải ngắn, có URL) + sách.
cites: (source_id, trang_in | None, dòng | None, anchor | None)
"""
from __future__ import annotations

GROUPS = {
    "gioi-tuyen": "Giới tuyến & cây cầu",
    "dau-loa": "Cuộc chiến âm thanh",
    "la-co": "Lá cờ trên vĩ tuyến",
    "doi-song": "Đời sống hai bờ",
    "ngay-nay": "Di tích ngày nay",
}

EXHIBITS = [
    dict(id="hoi-nghi-geneve", group="gioi-tuyen", image="IMG035", alt_images=["BKFIG02"],
         title="Hội nghị Genève 1954",
         paras=["Ngày 20-7-1954, Hiệp định đình chỉ chiến sự ở Việt Nam được ký tại Genève, lấy vĩ tuyến 17 – dòng sông Bến Hải – làm giới tuyến quân sự tạm thời. Ngày 21-7-1954, Hội nghị công bố Tuyên bố cuối cùng. Giới tuyến được xác định là tạm thời, không phải biên giới chính trị hay lãnh thổ.",
                "Theo Hiệp định, hai bên giới tuyến có một khu phi quân sự, mỗi bên rộng nhất là 5 km, làm khu đệm để tránh xung đột. Cây cầu Hiền Lương nằm đúng trên con sông ấy và từ đây bước vào một chương lịch sử kéo dài hơn hai mươi năm."],
         cites=[("SRC001", 26, None, "5 ki-lô-mét"), ("DOC001", None, None, None)]),
    dict(id="cau-1952", group="gioi-tuyen", image="IMG038", alt_images=["IMG001"],
         title="Cây cầu do người Pháp xây năm 1952",
         paras=["Cây cầu Hiền Lương đầu tiên được dựng năm 1928, dài 120 m, rộng 2 m. Năm 1952, công binh Pháp bắc lại cầu dài 178 m, gồm 7 nhịp dàn thép, mặt lát ván – chính là cây cầu chứng kiến cuộc chia cắt.",
                "Sau Hiệp định Genève, cây cầu bị chia đôi ở chính giữa, mỗi bên dài 89 m: nửa phía Bắc có 450 tấm ván, nửa phía Nam 444 tấm. Biển tên cầu trong ảnh ghi chiều dài 183,8 m – khác với số liệu trong sách, có thể do cách đo khác nhau."],
         cites=[("SRC001", 183, None, "1928"), ("SRC001", 184, None, "450 tấm"), ("SRC003", None, 18, "450 tấm ván")]),
    dict(id="cau-hai-mau", group="gioi-tuyen", image="BKFIG11", alt_images=["IMG034", "IMG045"],
         title="Cây cầu hai màu sơn",
         paras=["Cuối năm 1958, phía Bắc đề nghị hai bên sơn cầu cùng một màu nhưng không được đáp lại. Ngày 9-11-1958, Đội sơn cầu 337 bắt đầu sơn nửa phía Bắc; cuối tháng 12 phía Nam đưa 45 thợ ra sơn nửa của mình một màu khác. Ngày 16-1-1959 phía Nam sơn xong – từ đó cây cầu mang hai màu.",
                "Theo lời kể của bà Nguyễn Thị Hương, đội trưởng đội sơn cầu, hai bên thay nhau sơn cho đến năm 1960 thì giữ nguyên hai màu: nửa Bắc màu xanh, nửa Nam màu vàng. Ngày nay cây cầu phục chế cũng được sơn lại hai màu xanh – vàng để nhắc nhớ giai đoạn ấy. (Sách “Đôi bờ giới tuyến” ghi màu sơn năm 1958–1959 khác với lời kể này.)"],
         cites=[("SRC001", 185, None, "Đội sơn cầu 337"), ("SRC001", 186, None, "45 thợ"), ("SRC004", None, 25, "năm 1960"), ("SRC003", None, 38, "Tháng 3/2014")]),
    dict(id="toan-canh-1959", group="gioi-tuyen", image="IMG044", alt_images=["IMG029"],
         title="Toàn cảnh cầu Hiền Lương (2-9-1959)",
         paras=["Bức ảnh được bài viết của Minh Vượng chú thích là toàn cảnh cầu Hiền Lương chụp ngày 2-9-1959. Từ trên cao có thể thấy dòng sông, cây cầu dài chạy sang bờ bên kia nơi có cột cờ, và đám đông tập trung ở đầu cầu.",
                "Hai đầu cầu khi ấy là hai đồn: đồn công an Hiền Lương ở bờ Bắc và đồn cảnh sát Xuân Hòa ở bờ Nam. Hai đồn trao đổi thư từ, bưu thiếp và kiểm soát người qua cầu."],
         cites=[("SRC003", None, 22, "2-9-1959"), ("SRC001", 98, None, "bưu thiếp")]),
    dict(id="nam-bac-mot-nha", group="gioi-tuyen", image="IMG036", alt_images=["IMG024", "IMG012", "IMG021"],
         title="“Nam Bắc là một nhà”",
         paras=["Phía sau nhịp cầu thép là tấm biển lớn bờ Bắc: “Nam Bắc là một nhà – Không một lực lượng nào có thể chia cắt được”, bên cạnh cột gắn loa phóng thanh. Bài viết của Minh Vượng chú thích ảnh này là cầu Hiền Lương phía bờ Bắc (1956–1964) với những khẩu hiệu thể hiện khát vọng thống nhất.",
                "Bờ Nam cũng dựng băng-rôn, panô của mình. Hai bờ sông trở thành nơi đối thoại bằng khẩu hiệu, cờ và loa – một cuộc đấu tranh chính trị diễn ra hằng ngày ngay trước mắt người dân hai miền."],
         cites=[("SRC003", None, 28, "khẩu hiệu"), ("SRC001", 114, None, "Sài Gòn thừa nhận")]),
    dict(id="cau-bi-sap", group="gioi-tuyen", image="IMG037",
         title="Cây cầu bị đánh sập",
         paras=["Những nhịp cầu dàn thép gãy đổ xuống mặt sông. Các nguồn ghi khác nhau về thời điểm: sách “Đôi bờ giới tuyến” viết cầu bị đánh sập tháng 9-1966, còn các bài viết (trong đó có chú thích của bức ảnh này) ghi năm 1967.",
                "Sau chiến tranh, năm 1974 một cây cầu bê tông được xây; năm 2001 cầu được phục chế theo nguyên mẫu, mặt lát gỗ lim, và đến nay đang tiếp tục được tu bổ."],
         cites=[("SRC001", 183, None, "9-1966"), ("SRC003", None, 34, "1967"), ("SRC001", 193, None, "1974"), ("SRC003", None, 36, "2001")]),
    dict(id="loa-bo-bac", group="dau-loa", image="IMG041", alt_images=["IMG047", "IMG049", "BKFIG08"],
         title="Cụm loa phát thanh bờ Bắc",
         paras=["Ban đầu bờ Bắc có 5 cụm loa trải dài 1.500 m, mỗi cụm 24 loa 25W; sau bổ sung thêm 8 loa 50W và một loa 250W do Liên Xô sản xuất. Để nuôi dàn loa, có một đường dây điện dài gần 10 km và một trạm tăng âm cách cầu 2,5 km.",
                "Chương trình gồm tin tức, ca nhạc, ngâm thơ, kịch, dân ca. Một báo cáo của chính phía Sài Gòn mà sách trích lại phải thừa nhận: từ ngày 2-9-1956, dọc bờ Bắc có tới 5 chỗ phóng thanh, máy được che kín trong bụi cây."],
         cites=[("SRC003", None, 56, "24 loa"), ("SRC005", None, 18, "6KvA"), ("SRC001", 114, None, "Sài Gòn thừa nhận")]),
    dict(id="loa-bo-nam", group="dau-loa", image="IMG042", alt_images=["IMG030", "IMG048"],
         title="Cụm loa phát thanh bờ Nam",
         paras=["Ở bờ Nam, theo một văn bản năm 1962 của Bộ Công dân vụ Sài Gòn mà sách trích dẫn, hệ thống phóng thanh được thiết lập năm 1956 với 3 trạm: Võ Xá, Hiền Lương, Cát Sơn.",
                "Sách cho biết hệ thống phát thanh của bờ Bắc vượt trội về công suất, khiến loa bờ Nam nhiều lúc không thể hoạt động được. Cuộc đấu kéo dài đến năm 1965, khi chiến tranh lan tới vùng giới tuyến."],
         cites=[("SRC001", 119, None, "Võ Xá"), ("SRC001", 131, None, "không thể hoạt động"), ("SRC004", None, 48, "1965")]),
    dict(id="loa-500w", group="dau-loa", image="IMG046",
         title="Chiếc loa 500W",
         paras=["Năm 1960, phía Bắc trang bị một chiếc loa đường kính 1,72 m, công suất 500W, đặt trên xe để di chuyển dọc bờ sông. Các bài viết kể khi thuận gió tiếng loa vang xa hơn 10 km.",
                "Nơi lưu giữ chiếc loa hiện nay được các nguồn ghi khác nhau: trước Bảo tàng Vĩnh Linh, Nhà trưng bày “Vĩ tuyến 17 và khát vọng thống nhất”, Bảo tàng Báo chí Việt Nam; bức ảnh này ghi là chiếc loa của giới tuyến Hiền Lương – Bến Hải trưng bày ở gian Đài Tiếng nói Việt Nam."],
         cites=[("SRC001", 116, None, "1,72m"), ("SRC003", None, 58, "Bảo tàng Vĩnh Linh"), ("SRC005", None, 20, "500W"), ("WEB002", None, None, None)]),
    dict(id="o-nhan", group="dau-loa", image="IMG043",
         title="O Nhạn – giọng nói qua sông",
         paras=["Bài viết của Minh Vượng chú thích ảnh này là O Nhạn – phát thanh viên chính của Đài Truyền thanh Vĩnh Linh trong thời kỳ đấu loa ở cầu Hiền Lương. (“O” là cách gọi các cô gái ở Quảng Trị.)",
                "Đài Truyền thanh Vĩnh Linh thành lập tháng 7-1955. Những phát thanh viên như O Nhạn đọc tin, ngâm thơ, hát qua dàn loa hướng về bờ Nam – bài viết kể có binh sĩ bên kia thuộc lòng những bài thơ phát qua loa."],
         cites=[("SRC003", None, 62, "O Nhạn"), ("WEB002", None, None, None), ("SRC003", None, 58, "thuộc lòng")]),
    dict(id="hai-cot-co", group="la-co", image="IMG019", alt_images=["IMG015", "IMG018", "IMG020"],
         title="Hai cột cờ đối mặt",
         paras=["Ngày 8-10-1954, phía Bắc dựng cột cờ đầu tiên cao 12 m; bên kia, cờ được cắm trên lô cốt Xuân Hòa cao 15 m. Hai bờ thi nhau nâng cột: 18 m, rồi 25 m (bờ Nam, 1956), 32 m (bờ Bắc, 1957), 35 m (bờ Nam, 1961).",
                "Năm 1962, phía Bắc dựng trụ thép ống cao 38,6 m; sách kể đồng bào bờ Nam ở Dốc Miếu, Kinh Môn cách 6–8 km vẫn nhìn thấy lá cờ."],
         cites=[("SRC001", 188, None, "8-10-1954"), ("SRC001", 188, None, "19-7-1957"), ("SRC001", 189, None, "Dốc Miếu")]),
    dict(id="me-vinh-linh-va-co", group="la-co", image="IMG050",
         title="Mẹ Vĩnh Linh vá cờ",
         paras=["Lá cờ lớn trên cột cao luôn hứng gió biển; sách kể thường mỗi tháng thay cờ một lần nhưng phải vá năm bảy lần. Những bà mẹ Vĩnh Linh đã ngày đêm khâu vá để lá cờ không ngừng bay.",
                "Tiêu biểu là mẹ Ngô Thị Diệm ở thôn Hiền Lương: tuổi cao sức yếu nhưng không chịu đi sơ tán, ngày ngày khâu vá lại từng lá cờ khi cờ mới chưa kịp đưa vào. Ngày 6-12-2007, mẹ được phong tặng danh hiệu Anh hùng Lực lượng vũ trang nhân dân."],
         cites=[("SRC001", 189, None, "năm bảy lần"), ("SRC001", 192, None, "Ngô Thị Diệm"), ("SRC001", 192, None, "6-12-2007")]),
    dict(id="nguoi-may-co", group="la-co", image="IMG013",
         title="122 mét vuông vải đỏ",
         paras=["Ông Nguyễn Đức Lãng, người may cờ cho cột cờ Hiền Lương từ năm 1959, kể một lá cờ rộng khoảng 96 m² cần 122 m² vải đỏ và gần 12 m² vải vàng; mỗi năm ông may gần 30 lá, có lúc phải may trong hầm.",
                "Từ ngày 19-5-1956 đến 8-10-1967, phía Bắc đã dùng tổng cộng 267 lá cờ các loại."],
         cites=[("WEB003", None, None, None), ("SRC001", 189, None, "267 lá cờ")]),
    dict(id="buu-thiep", group="doi-song", image="BKFIG10",
         title="Bưu thiếp năm dòng",
         paras=["Từ ngày 15-5-1955, nhân dân hai miền được trao đổi bưu thiếp qua giới tuyến – nhưng mọi tin tức chỉ được viết trong năm dòng và giới hạn trong chuyện gia đình.",
                "Bưu thiếp đi qua cầu Hiền Lương, nơi hai đồn trao đổi thư từ. Với những gia đình bị chia cắt, mấy dòng chữ ngắn ngủi ấy là một trong số ít cách biết người thân bên kia sông còn bình an."],
         cites=[("SRC001", 155, None, "15-5-1955"), ("SRC001", 155, None, "5 dòng"), ("SRC001", 98, None, "bưu thiếp")]),
    dict(id="doi-bo", group="doi-song", image="IMG010", alt_images=["IMG033", "BKFIG05"],
         title="Gác chung một cây cầu",
         paras=["Mỗi bên có hai đồn ở giới tuyến, mỗi đồn không quá 20 người. Hằng tháng vào ngày chẵn, một tổ ba người phía Bắc mang sổ trực sang bờ Nam, ngày lẻ thì tổ phía Nam sang bờ Bắc.",
                "Ngày ngày gặp nhau, phía Bắc tìm cách vận động cảnh sát bên kia – đến mức chỉ huy các đồn Cát Sơn, Xuân Hòa cấm cảnh sát của mình tiếp xúc, trò chuyện với chiến sĩ bờ Bắc ngoài việc ký biên bản hằng ngày."],
         cites=[("SRC003", None, 44, "ngày chẵn"), ("SRC001", 99, None, "không được tiếp xúc")]),
    dict(id="kien-nghi", group="doi-song", image="BKFIG07",
         title="Gửi kiến nghị cho Tổ Quốc tế",
         paras=["Những ngày có phái đoàn quốc tế đi kiểm tra, học sinh và nhân dân Vĩnh Linh tập trung về cầu Hiền Lương để đưa kiến nghị, gửi thư vào Nam đòi thi hành Hiệp định Genève.",
                "Sách kể các trường còn tổ chức cho học sinh gửi thư vào Nam đòi duy trì mối quan hệ ruột thịt giữa hai miền."],
         cites=[("SRC001", 88, None, "cầu Hiển Lương"), ("SRC001", 87, None, "gửi thư vào Nam")]),
    dict(id="cot-co-ngay-nay", group="ngay-nay", image="IMG040",
         title="Kỳ đài Hiền Lương ngày nay",
         paras=["Cột cờ hiện nay được xây theo mẫu thiết kế năm 1962, cao 38,6 m, bên dưới bổ sung phần đài. Hằng năm, Lễ thượng cờ “Thống nhất non sông” được tổ chức tại đây.",
                "Năm 2025, kỳ đài cùng cầu Hiền Lương và Nhà liên hợp được tu bổ trong dự án Công viên Thống nhất."],
         cites=[("WEB004", None, None, None), ("WEB005", None, None, None)]),
]

# Nguồn web bổ sung cho bản đồ khu vực (đọc 2026-11-06)
WEB_SOURCES_2 = [
    dict(source_id="WEB005", title="Đầu tư, bảo tồn Công viên Thống nhất ở đôi bờ Hiền Lương–Bến Hải (Báo Nhân Dân)", author="Chưa xác định", publisher="Báo Nhân Dân",
         source_type="WEB_ARTICLE", classification="secondary", url="https://nhandan.vn/dau-tu-bao-ton-cong-vien-thong-nhat-o-doi-bo-hien-luong-ben-hai-post909599.html",
         language="vi", document_date="Chưa xác định (2025)", accessed_date="2026-11-06", relevant_content="Dự án tu bổ 2023–2025: cầu, kỳ đài, nhà liên hợp.",
         relevant_provisions=None, access_status="read_search_snippet_only", verification_status="web_paraphrase_unverified", notes="Đọc đoạn trích kết quả tìm kiếm."),
    dict(source_id="WEB006", title="Di tích lịch sử Đôi bờ Hiền Lương – Bến Hải (Cục Di sản văn hóa, dsvh.gov.vn)", author="Cục Di sản văn hóa", publisher="dsvh.gov.vn",
         source_type="WEB_ARTICLE", classification="official_heritage_record", url="https://dsvh.gov.vn/di-tich-lich-su-doi-bo-hien-luong-ben-hai-2974",
         language="vi", document_date="Chưa xác định", accessed_date="2026-11-06", relevant_content="Mô tả Nhà Liên hợp, đồn công an Hiền Lương, cụm di tích.",
         relevant_provisions=None, access_status="read_search_snippet_only", verification_status="web_paraphrase_unverified", notes="Đọc đoạn trích kết quả tìm kiếm."),
    dict(source_id="WEB007", title="Đôi bờ Hiền Lương–Bến Hải: “Nhân chứng lịch sử” về một thời chia cắt (VietNamNet)", author="Chưa xác định", publisher="VietNamNet",
         source_type="WEB_ARTICLE", classification="secondary", url="https://vietnamnet.vn/doi-bo-hien-luong-ben-hai-nhan-chung-lich-su-ve-mot-thoi-chia-cat-800402.html",
         language="vi", document_date="Chưa xác định", accessed_date="2026-11-06", relevant_content="Dự án trùng tu năm 2005 ở bờ Nam: cụm tượng đài, sân lễ hội.",
         relevant_provisions=None, access_status="read_search_snippet_only", verification_status="web_paraphrase_unverified", notes="Đọc đoạn trích kết quả tìm kiếm."),
    dict(source_id="WEB008", title="[Ảnh] Đi dọc đôi bờ Hiền Lương – Bến Hải 70 năm sau hiệp định Geneva (Báo Nhân Dân)", author="Chưa xác định", publisher="Báo Nhân Dân",
         source_type="WEB_ARTICLE", classification="secondary", url="https://nhandan.vn/anh-di-doc-doi-bo-hien-luong-ben-hai-70-nam-sau-hiep-dinh-geneva-post822694.html",
         language="vi", document_date="2024", accessed_date="2026-11-06", relevant_content="Cụm tượng đài Khát vọng thống nhất: diện tích, kích thước, chất liệu.",
         relevant_provisions=None, access_status="read_search_snippet_only", verification_status="web_paraphrase_unverified", notes="Đọc đoạn trích kết quả tìm kiếm."),
]

PLACES = {
    "monument": dict(title="Tượng đài Khát vọng thống nhất", subtitle="Bờ Nam sông Bến Hải",
                     images=[("/monument-3d.png", "Tượng đài – cảnh dựng minh họa", "Ảnh dựng minh họa trong repo, không phải ảnh tư liệu"),
                             ("/monument-reference.png", "Tượng đài – ảnh tham khảo", "Ảnh do nhóm cung cấp (nguồn gốc chưa ghi)")],
                     paras=["Cụm tượng đài “Khát vọng thống nhất” nằm ở bờ Nam sông Bến Hải, phía Đông Quốc lộ 1A, trên diện tích khoảng 2.700 m². Công trình gồm phần bệ đài với mảng phù điêu ghép từ nhiều khối đá, và phần tượng là hình tượng bà mẹ miền Nam cao 7,7 m cùng người con trai cao 5,5 m, tạc bằng đá xanh Thanh Hóa.",
                            "Sau chiến tranh, hệ thống đồn, trạm và giàn loa ở bờ Nam bị tháo bỏ. Trong dự án trùng tu, tôn tạo khu vực đôi bờ cầu Hiền Lương năm 2005, bờ Nam được quy hoạch lại với khuôn viên, sân lễ hội, hồ nước và cụm tượng đài, để đón khách tham quan.",
                            "Tượng đài thể hiện niềm tin của đồng bào miền Nam vào ngày thống nhất đất nước – khát vọng của những gia đình từng chỉ cách nhau một dòng sông mà phải xa cách suốt hơn hai mươi năm."],
                     cites=["WEB008", "WEB007"]),
    "union": dict(title="Nhà liên hợp", subtitle="Nơi họp giao ban của Ủy ban Liên hợp hai bên",
                  images=[("/union-reference.png", "Nhà liên hợp – ảnh tham khảo", "Ảnh do nhóm cung cấp (nguồn gốc chưa ghi)")],
                  paras=["Thi hành Hiệp định Genève, tháng 8-1954 Ban Liên hiệp khu phi quân sự được thành lập, gồm đại diện quân sự hai bên, làm việc dưới sự giám sát của Tổ Quốc tế 76 để giải quyết các vụ việc trong khu phi quân sự. Nhà liên hợp ở bờ Bắc là nơi diễn ra những cuộc họp giao ban ấy.",
                         "Nhà liên hợp ngày nay được xây theo nguyên mẫu nhà Liên hợp trước đây: kiểu nhà sàn bốn mái, mặt tiền hướng ra Quốc lộ 1A. Không gian bên trong chia ba phân khu; khu chính giữa gồm bốn gian liên thông là phòng họp giao ban cũ, nội thất tái hiện một cuộc họp giữa Ủy ban Liên hợp hai miền Bắc – Nam có sự giám sát của Tổ Quốc tế 76.",
                         "Năm 2025, Nhà liên hợp được hạ giải từ mái tới sàn để đánh giá, thay một số cấu kiện gỗ, lan can, tay vịn trong dự án tu bổ Công viên Thống nhất."],
                  cites=["SRC001:49:Ban Liên hiệp khu phi quân sự gồm có", "SRC001:90:Tổ Quốc tế 76", "WEB006", "WEB005"]),
}

# Nội dung khu vực Cầu và Kỳ đài: chọn từ dòng thời gian + mẩu chuyện đã có
BRIDGE_EVENTS = ["EV01", "EV02", "EV-X01", "EV13", "EV14", "EV18", "EV19", "EV23", "EV25", "EV26"]
BRIDGE_ANECDOTES = ["cau-hai-mau", "450-tam-van", "doi-bo", "buu-thiep"]
BRIDGE_IMAGES = ["IMG004", "IMG034", "IMG029", "IMG001", "IMG038", "IMG044", "IMG039", "IMG036", "IMG037", "IMG045", "BKFIG11", "IMG002", "IMG005"]
FLAG_EVENTS = ["EV09", "EV15", "EV17", "EV20", "EV21", "EV27", "EV28"]
FLAG_ANECDOTES = ["choi-co", "nguoi-may-co", "me-diem", "dem-2-8-1967"]
FLAG_IMAGES = ["IMG019", "IMG015", "IMG016", "IMG017", "IMG018", "IMG020", "IMG013", "IMG040", "IMG050"]
