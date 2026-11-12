import { createContext, useContext, useMemo, useState, type ReactNode } from 'react'
import type { Lang } from '../api/client'

type Dict = Record<string, string>
const vi: Dict = {
  hero_eyebrow: 'Bảo tàng số · Quảng Trị · 1954–1967', hero_title: 'Cầu Hiền Lương', hero_tagline: 'Dòng sông chia cắt – Khát vọng nối liền',
  hero_sub: 'Một dòng sông, một cây cầu, hai bờ giới tuyến – và câu chuyện về khát vọng thống nhất đất nước, kể lại qua tư liệu, hình ảnh và lời thuyết minh.',
  hero_start: 'Bắt đầu hành trình', hero_ask: 'Trò chuyện với hướng dẫn viên', hero_photo: 'Ảnh: cầu Hiền Lương (trùng hình in tr.187 của sách). Năm chụp chưa xác định.', hero_scroll: 'Cuộn để bắt đầu',
  story_eyebrow: 'Câu chuyện', story_title: 'Bốn chương của một dòng sông', story_intro: 'Mỗi chương dưới đây được viết từ những trang sách và văn kiện đang trưng bày; số trang được ghi ngay bên dưới.',
  story_chapter: 'Chương', story_more: 'Khám phá chủ đề', story_timeline: 'Xem trên dòng thời gian', story_ask: 'Hỏi hướng dẫn viên', story_sources: 'Tư liệu', story_note: 'Văn dẫn chuyện do nhóm biên soạn từ các trang được trích.',
  tlp_eyebrow: 'Dòng thời gian', tlp_title: 'Từ Genève đến ngày xoá bỏ giới tuyến', tlp_all: 'Toàn bộ dòng thời gian', tlp_hint: 'Kéo ngang hoặc dùng nút mũi tên để đi qua các mốc', tlp_prev: 'Cuộn về trước', tlp_next: 'Cuộn tiếp',
  col_eyebrow: 'Hiện vật số', col_title: 'Phòng trưng bày ảnh tư liệu', col_intro: 'Ảnh lưu trữ về cây cầu, cột cờ, cổng chào, khẩu hiệu và loa phát thanh hai bờ; cùng các hình in trong sách. Mỗi ảnh ghi rõ điều nhìn thấy và mức độ chắc chắn.', col_all: 'Vào phòng trưng bày',
  guide_eyebrow: 'Hướng dẫn viên AI', guide_title: 'Hãy để câu chuyện lịch sử được tiếp tục', guide_body: 'Hỏi bằng tiếng Việt, English hoặc 中文. Hướng dẫn viên kể lại dựa trên tư liệu đang trưng bày, ghi nguồn và số trang, và nói rõ khi tư liệu chưa đủ.', guide_you_can: 'Bạn có thể hỏi về', guide_start: 'Bắt đầu trò chuyện',
  ev_illustrative: 'Ảnh minh hoạ theo chủ đề – không phải ảnh chụp tại sự kiện', ev_direct: 'Hình trong sách gắn với sự kiện', ev_prev: 'Mốc trước', ev_next: 'Mốc tiếp theo', ev_close: 'Đóng', ev_topic: 'Xem chủ đề', ev_open: 'Xem thuyết minh', ev_of: 'trên',
  tl_intro: 'Các mốc dưới đây đều có trích dẫn trang sách hoặc điều khoản văn kiện; không có mốc nào được thêm vào để lấp chỗ trống.',
  per_pre: 'Con đường đến Genève', per_pre_desc: 'Bối cảnh quốc tế dẫn tới Hội nghị Genève và lịch sử cây cầu trước năm 1954.',
  per_p1: 'Thi hành Hiệp định Genève', per_p1_desc: 'Theo cách phân kỳ của sách, cuộc đấu tranh thực hiện Hiệp định ở khu phi quân sự kéo dài từ 7-1954 đến 7-1956.',
  per_p2: 'Những năm chia cắt', per_p2_desc: 'Sau tháng 7-1956 cuộc tổng tuyển cử không diễn ra (theo sách); đôi bờ bước vào những năm sơn cầu, đấu cờ, đấu loa và bom đạn, cho đến năm 1967.',
  chat_guide_title: 'Hướng dẫn viên AI của bảo tàng', chat_guide_intro: 'Tôi thuyết minh dựa trên tư liệu đang trưng bày: cuốn sách “Đôi bờ giới tuyến (1954–1967)”, bộ ảnh lưu trữ và các văn kiện Genève. Mỗi thông tin đều kèm nguồn và số trang; khi tư liệu không đủ, tôi sẽ nói rõ.',
  chat_themes: 'Gợi ý theo chủ đề', chat_view_sources: 'Xem nguồn tư liệu', chat_view_timeline: 'Dòng thời gian', chat_view_gallery: 'Phòng trưng bày', chat_guide_name: 'Hướng dẫn viên',
  gal_intro: 'Bộ sưu tập gồm 34 ảnh lưu trữ (Archive_2), 16 ảnh bổ sung (Archive_4: 10 ảnh tư liệu, 6 ảnh di tích/hiện vật ngày nay) và 12 hình in trong sách. Thông tin đi kèm ảnh bổ sung được ghi rõ là chưa xác minh. Năm chụp chưa xác định trừ khi chú thích ghi rõ; nhân vật trong ảnh không được định danh.',
  gt_bridge: 'Cầu', gt_flagpoles: 'Cột cờ', gt_gate: 'Cổng chào', gt_slogan_wall: 'Khẩu hiệu', gt_loudspeakers: 'Loa phát thanh', gt_banner_diem: 'Băng-rôn bờ Nam', gt_geneva: 'Genève', gt_dmz: 'Khu phi quân sự', gt_postcard: 'Bưu thiếp', gt_police: 'Công an, cảnh sát',
  menu: 'Menu',
  appName: 'Hướng dẫn viên bảo tàng AI', tagline: 'Cầu Hiền Lương – Vĩ tuyến 17 và đôi bờ giới tuyến (1954–1967)',
  nav_home: 'Giới thiệu', nav_chat: 'Hỏi đáp AI', nav_gallery: 'Thư viện ảnh', nav_timeline: 'Dòng thời gian', nav_stories: 'Chuyện kể', an_eyebrow: 'Ngoài dòng thời gian', an_title: 'Những mẩu chuyện thú vị', an_intro: 'Những câu chuyện nhỏ mà sống động ở đôi bờ Hiền Lương: cuộc chiến màu sơn, chọi cờ, đấu loa, những lá cờ được vá trong đêm… Mỗi chuyện được kể lại từ sách, bài viết và báo chí, kèm nguồn; chỗ các nguồn ghi khác nhau được nói rõ.', an_all: 'Đọc tất cả mẩu chuyện', an_read: 'Đọc chuyện', an_sources: 'Nguồn', an_notes: 'Các nguồn ghi khác nhau', an_ask: 'Hỏi hướng dẫn viên về chuyện này', an_note: 'Văn kể do nhóm biên soạn từ các nguồn được trích; bản tiếng Anh/Trung là bản dịch của nhóm.', an_web: 'Báo trực tuyến', an_unverified_web: 'nguồn web – chưa đối chiếu bản in', an_back: 'Về đầu trang', nav_topics: 'Chủ đề', nav_settings: 'Cài đặt',
  home_intro: 'Đặt câu hỏi bằng tiếng Việt, English hoặc 中文, nhận câu trả lời dựa trên tư liệu có dẫn nguồn và số trang, xem ảnh liên quan và nghe thuyết minh.',
  home_scope_title: 'Phạm vi và nguyên tắc', home_scope_1: 'Nguồn nền tảng: sách “Đôi bờ giới tuyến (1954–1967)” của TS. Hoàng Chí Hiếu (bản scan, văn bản qua OCR có thể sai dấu).',
  home_scope_2: 'Tách giai đoạn 1954–1956 và 1956–1967; không gán ảnh/sự kiện cho giai đoạn nếu không có bằng chứng.',
  home_scope_3: 'Tư liệu ngoài (văn kiện Genève) được lưu riêng và ghi rõ loại nguồn; giới tuyến quân sự tạm thời không phải biên giới quốc gia.',
  home_scope_4: 'Năm chụp và danh tính nhân vật trong ảnh ghi “Chưa xác định” khi ảnh không đủ bằng chứng.',
  home_examples: 'Thử hỏi', home_go_chat: 'Bắt đầu hỏi đáp', home_go_gallery: 'Xem thư viện ảnh', home_go_timeline: 'Xem dòng thời gian', home_status: 'Trạng thái hệ thống',
  chat_placeholder: 'Nhập câu hỏi, ví dụ: Cuộc chiến sơn cầu ở Hiền Lương diễn ra thế nào?', chat_send: 'Gửi', chat_thinking: 'Đang tra cứu tư liệu…', chat_empty: 'Chưa có câu hỏi nào. Hãy chọn một câu hỏi gợi ý hoặc tự nhập.',
  chat_sources: 'Nguồn tham khảo', chat_images: 'Ảnh liên quan', chat_listen: 'Nghe thuyết minh', chat_page: 'tr.', chat_pdf: 'trang PDF', chat_book: 'Sách', chat_external: 'Văn kiện/tham khảo ngoài', chat_article: 'Bài viết (thứ cấp)', chat_web: 'Báo trực tuyến', chat_note: 'Ghi chú đối chiếu nguồn', gal_contemporary: 'Ảnh di tích/hiện vật ngày nay', img_fn_title: 'Mô tả ban đầu đi kèm ảnh', img_fn_note: 'Chưa xác minh.', img_link_caption: 'chú thích ảnh trong bài viết',
  chat_conf: 'Độ tin cậy', chat_conf_high: 'cao', chat_conf_medium: 'trung bình', chat_conf_low: 'thấp', chat_insufficient: 'Chưa đủ bằng chứng trong kho tư liệu',
  chat_fallback: 'Mô hình AI không khả dụng – chỉ hiển thị đoạn tư liệu liên quan', chat_warn: 'Lưu ý kiểm chứng', chat_clear: 'Xoá hội thoại', chat_unverified: 'Văn bản OCR chưa được biên tập viên kiểm tra',
  chat_error: 'Không gửi được câu hỏi', chat_retry: 'Thử lại',
  audio_play: 'Phát', audio_pause: 'Tạm dừng', audio_stop: 'Dừng', audio_replay: 'Phát lại', audio_loading: 'Đang tạo giọng nói…', audio_error: 'Không tạo được giọng nói (chatbot vẫn hoạt động)', audio_text: 'Nội dung đang đọc',
  gal_title: 'Thư viện ảnh lịch sử', gal_search: 'Tìm trong mô tả, chữ trong ảnh…', gal_topic: 'Chủ đề', gal_all: 'Tất cả', gal_kind: 'Loại', gal_archive: 'Ảnh tư liệu (ZIP)', gal_book: 'Hình trong sách', gal_hide: 'Ẩn bản trùng', gal_count: 'ảnh', gal_empty: 'Không có ảnh khớp bộ lọc.', gal_open: 'Xem lớn', gal_close: 'Đóng',
  img_visual: 'Mô tả những gì nhìn thấy', img_context: 'Bối cảnh lịch sử (theo sách/nguồn đã kiểm chứng)', img_location: 'Địa điểm', img_time: 'Thời gian', img_date: 'Năm chụp ước tính', img_text: 'Chữ xuất hiện trong ảnh', img_people: 'Nhân vật',
  img_source: 'Nguồn', img_pages: 'Trang sách liên quan', img_topics: 'Chủ đề liên quan', img_notes: 'Ghi chú xác minh', img_conf: 'Độ chắc chắn', img_dup: 'Ảnh liên quan/bản khác', img_rights: 'Quyền sử dụng', img_back: 'Quay lại thư viện',
  img_desc_note: 'Mô tả chi tiết hiện chỉ có bằng tiếng Việt.', img_passages: 'Đoạn tư liệu liên quan', img_link_direct: 'trùng hình in trong sách', img_link_topic: 'liên kết theo chủ đề (không chứng minh cùng thời điểm)', img_watermarks: 'Watermark nhìn thấy',
  tl_title: 'Dòng thời gian', tl_all: 'Tất cả', tl_p1: '1954–1956', tl_p2: '1956–1967', tl_pre: 'Trước 1954', tl_source: 'Nguồn', tl_ask: 'Hỏi chatbot', tl_empty: 'Không có sự kiện.', tl_note: 'Chỉ gồm sự kiện có trích dẫn trang sách hoặc điều khoản văn kiện.', tl_evidence: 'Bằng chứng OCR',
  tp_title: 'Chủ đề lịch sử', tp_events: 'sự kiện', tp_images: 'ảnh', tp_chapters: 'Chương liên quan', tp_passages: 'Trích đoạn sách (OCR)', tp_back: 'Quay lại chủ đề', tp_pages: 'trang sách in',
  set_title: 'Cài đặt', set_ui_lang: 'Ngôn ngữ giao diện', set_answer_lang: 'Ngôn ngữ trả lời', set_auto: 'Tự nhận diện theo câu hỏi', set_voice: 'Mã giọng đọc ElevenLabs (tuỳ chọn)', set_voice_hint: 'Để trống để dùng giọng mặc định theo ngôn ngữ. Gói Free chỉ dùng được giọng premade.',
  set_health: 'Trạng thái dịch vụ', set_llm: 'Mô hình AI', set_tts: 'Giọng nói', set_configured: 'đã cấu hình', set_missing: 'chưa cấu hình', set_retrieval: 'Truy xuất',
  loading: 'Đang tải…', error_generic: 'Đã xảy ra lỗi', retry: 'Thử lại', not_determined: 'Chưa xác định',
}
const en: Dict = {
  ...vi,
  hero_eyebrow: 'Digital museum · Quảng Trị · 1954–1967', hero_title: 'Hiền Lương Bridge', hero_tagline: 'A river that divided – a longing to reunite',
  hero_sub: 'One river, one bridge, two banks of a demarcation line – and the story of a nation longing to be whole again, told through documents, photographs and narration.',
  hero_start: 'Begin the journey', hero_ask: 'Talk to the guide', hero_photo: 'Photo: Hiền Lương bridge (same as the figure on p.187 of the book). Date not determined.', hero_scroll: 'Scroll to begin',
  story_eyebrow: 'The story', story_title: 'Four chapters of a river', story_intro: 'Each chapter below is written from the book pages and documents on display; page numbers are shown underneath.',
  story_chapter: 'Chapter', story_more: 'Explore the topic', story_timeline: 'See on the timeline', story_ask: 'Ask the guide', story_sources: 'Sources', story_note: 'Narrative written by the team from the cited pages; English translation by the team.',
  tlp_eyebrow: 'Timeline', tlp_title: 'From Geneva to the end of the demarcation line', tlp_all: 'Full timeline', tlp_hint: 'Swipe or use the arrow buttons to move through the milestones', tlp_prev: 'Scroll back', tlp_next: 'Scroll forward',
  col_eyebrow: 'Digital collection', col_title: 'The photographic archive', col_intro: 'Archive photos of the bridge, flagpoles, gateway, slogans and loudspeakers of both banks, plus figures printed in the book. Each records what is visible and how certain we are.', col_all: 'Enter the gallery',
  guide_eyebrow: 'AI museum guide', guide_title: 'Let the story continue', guide_body: 'Ask in Vietnamese, English or 中文. The guide narrates from the documents on display, cites sources and pages, and says so when the archive is not enough.', guide_you_can: 'You can ask about', guide_start: 'Start the conversation',
  ev_illustrative: 'Illustrative photo of the same subject – not taken at this event', ev_direct: 'Book figure tied to this event', ev_prev: 'Previous', ev_next: 'Next', ev_close: 'Close', ev_topic: 'Open topic', ev_open: 'Read the narration', ev_of: 'of',
  tl_intro: 'Every milestone below cites a book page or a document provision; none has been added just to fill a gap.',
  per_pre: 'The road to Geneva', per_pre_desc: 'The international background to the Geneva Conference and the bridge before 1954.',
  per_p1: 'Implementing the Geneva Agreement', per_p1_desc: 'In the book\'s periodisation, the struggle to implement the Agreement in the DMZ ran from July 1954 to July 1956.',
  per_p2: 'The years of division', per_p2_desc: 'After July 1956 the general elections did not take place (according to the book); the banks entered years of painting the bridge, flag and loudspeaker contests and bombing, until 1967.',
  chat_guide_title: 'The museum\'s AI guide', chat_guide_intro: 'I narrate from the documents on display: the book “Đôi bờ giới tuyến (1954–1967)”, the photo archive and the Geneva texts. Every fact comes with its source and page; when the archive is not enough, I will tell you.',
  chat_themes: 'Suggested by theme', chat_view_sources: 'View sources', chat_view_timeline: 'Timeline', chat_view_gallery: 'Gallery', chat_guide_name: 'Guide',
  gal_intro: 'The collection holds 34 archive photos (Archive_2), 16 supplementary photos (Archive_4: 10 historical, 6 present-day site/exhibit photos) and 12 figures printed in the book. Descriptions supplied with the supplementary photos are marked unverified. Dates are not determined unless a caption states them; people in photos are not identified.',
  gt_bridge: 'Bridge', gt_flagpoles: 'Flagpoles', gt_gate: 'Gateway', gt_slogan_wall: 'Slogans', gt_loudspeakers: 'Loudspeakers', gt_banner_diem: 'Southern banners', gt_geneva: 'Geneva', gt_dmz: 'DMZ', gt_postcard: 'Postcards', gt_police: 'Police',
  menu: 'Menu',
  appName: 'AI Museum Guide', tagline: 'Hien Luong Bridge – the 17th parallel and the two banks of the demarcation line (1954–1967)',
  nav_home: 'Introduction', nav_chat: 'Ask the AI', nav_gallery: 'Photo gallery', nav_timeline: 'Timeline', nav_stories: 'Stories', an_eyebrow: 'Beyond the timeline', an_title: 'Fascinating stories', an_intro: 'Small but vivid stories from the two banks of Hien Luong: the paint war, the flagpole duel, the loudspeaker contest, flags mended overnight… Each is retold from the book, articles and newspapers, with sources; where sources disagree, we say so.', an_all: 'Read all stories', an_read: 'Read story', an_sources: 'Sources', an_notes: 'Where the sources disagree', an_ask: 'Ask the guide about this story', an_note: 'Stories written by the project team from the cited sources; English/Chinese versions are team translations.', an_web: 'Online newspaper', an_unverified_web: 'web source – not checked against print', an_back: 'Back to top', nav_topics: 'Topics', nav_settings: 'Settings',
  home_intro: 'Ask in Vietnamese, English or 中文 and get answers grounded in the archive with sources and page numbers, related photos and spoken narration.',
  home_scope_title: 'Scope and principles', home_scope_1: 'Core source: the book “Đôi bờ giới tuyến (1954–1967)” by Dr. Hoàng Chí Hiếu (scanned; text comes from OCR and may contain diacritic errors).',
  home_scope_2: '1954–1956 and 1956–1967 are kept apart; no photo or event is assigned to a period without evidence.',
  home_scope_3: 'External documents (Geneva texts) are stored separately and labelled by source type; the provisional military demarcation line is not a national border.',
  home_scope_4: 'Photo dates and identities of people are shown as “Not determined” when the image offers no evidence.',
  home_examples: 'Try asking', home_go_chat: 'Start asking', home_go_gallery: 'Browse the gallery', home_go_timeline: 'View the timeline', home_status: 'System status',
  chat_placeholder: 'Type a question, e.g. How was the bridge painting contest at Hien Luong fought?', chat_send: 'Send', chat_thinking: 'Searching the archive…', chat_empty: 'No questions yet. Pick a suggestion or type your own.',
  chat_sources: 'Sources', chat_images: 'Related photos', chat_listen: 'Listen', chat_page: 'p.', chat_pdf: 'PDF page', chat_book: 'Book', chat_external: 'External document/reference', chat_article: 'Article (secondary)', chat_web: 'Online newspaper', chat_note: 'Source-comparison note', gal_contemporary: 'Present-day site/exhibit photos', img_fn_title: 'Original description supplied with the photo', img_fn_note: 'Not verified.', img_link_caption: 'photo caption in an article',
  chat_conf: 'Confidence', chat_conf_high: 'high', chat_conf_medium: 'medium', chat_conf_low: 'low', chat_insufficient: 'Not enough evidence in the archive',
  chat_fallback: 'AI model unavailable – showing relevant passages only', chat_warn: 'Verification notes', chat_clear: 'Clear conversation', chat_unverified: 'OCR text not yet reviewed by an editor',
  chat_error: 'Could not send the question', chat_retry: 'Retry',
  audio_play: 'Play', audio_pause: 'Pause', audio_stop: 'Stop', audio_replay: 'Replay', audio_loading: 'Generating speech…', audio_error: 'Could not generate speech (the chatbot still works)', audio_text: 'Text being read',
  gal_title: 'Historical photo gallery', gal_search: 'Search descriptions, text in photos…', gal_topic: 'Topic', gal_all: 'All', gal_kind: 'Type', gal_archive: 'Archive photos (ZIP)', gal_book: 'Figures from the book', gal_hide: 'Hide duplicates', gal_count: 'images', gal_empty: 'No images match the filters.', gal_open: 'View large', gal_close: 'Close',
  img_visual: 'What is visible', img_context: 'Historical context (from the book / verified sources)', img_location: 'Location', img_time: 'Period', img_date: 'Estimated date', img_text: 'Text visible in the photo', img_people: 'People',
  img_source: 'Source', img_pages: 'Related book pages', img_topics: 'Related topics', img_notes: 'Verification notes', img_conf: 'Confidence', img_dup: 'Related/variant images', img_rights: 'Usage rights', img_back: 'Back to gallery',
  img_desc_note: 'Detailed descriptions are currently available in Vietnamese only.', img_passages: 'Related passages', img_link_direct: 'same figure printed in the book', img_link_topic: 'topic link (does not prove the same moment)', img_watermarks: 'Visible watermarks',
  tl_title: 'Timeline', tl_all: 'All', tl_p1: '1954–1956', tl_p2: '1956–1967', tl_pre: 'Before 1954', tl_source: 'Source', tl_ask: 'Ask the chatbot', tl_empty: 'No events.', tl_note: 'Only events with a book page citation or a document provision are listed.', tl_evidence: 'OCR evidence',
  tp_title: 'Historical topics', tp_events: 'events', tp_images: 'images', tp_chapters: 'Related chapters', tp_passages: 'Book excerpts (OCR)', tp_back: 'Back to topics', tp_pages: 'printed pages',
  set_title: 'Settings', set_ui_lang: 'Interface language', set_answer_lang: 'Answer language', set_auto: 'Detect from the question', set_voice: 'ElevenLabs voice ID (optional)', set_voice_hint: 'Leave empty for the default voice per language. The Free plan can only use premade voices.',
  set_health: 'Service status', set_llm: 'AI model', set_tts: 'Speech', set_configured: 'configured', set_missing: 'not configured', set_retrieval: 'Retrieval',
  loading: 'Loading…', error_generic: 'Something went wrong', retry: 'Retry', not_determined: 'Not determined',
}
const zh: Dict = {
  ...en,
  hero_eyebrow: '数字博物馆 · 广治 · 1954–1967', hero_title: '贤良桥', hero_tagline: '一河分隔，两岸盼合',
  hero_sub: '一条河、一座桥、分界线两岸——以及一个民族渴望重新统一的故事，透过史料、照片与讲解娓娓道来。',
  hero_start: '开始探索', hero_ask: '与讲解员对话', hero_photo: '照片：贤良桥（与书中第187页插图相同）。拍摄年份未确定。', hero_scroll: '向下滚动开始',
  story_eyebrow: '故事', story_title: '一条河的四个篇章', story_intro: '以下每一章都依据展出的书页和文件写成，页码标注在下方。',
  story_chapter: '第', story_more: '探索专题', story_timeline: '在时间线上查看', story_ask: '询问讲解员', story_sources: '资料', story_note: '叙述由团队依据所引页面撰写；中文为团队翻译。',
  tlp_eyebrow: '时间线', tlp_title: '从日内瓦到分界线消除', tlp_all: '完整时间线', tlp_hint: '左右滑动或使用箭头按钮浏览各个节点', tlp_prev: '向前', tlp_next: '向后',
  col_eyebrow: '数字藏品', col_title: '历史照片展厅', col_intro: '有关桥梁、旗杆、牌楼、标语和两岸广播的档案照片，以及书中插图。每张照片都注明可见内容与把握程度。', col_all: '进入展厅',
  guide_eyebrow: 'AI 讲解员', guide_title: '让历史故事继续讲下去', guide_body: '可用越南语、English 或中文提问。讲解员依据展出资料讲述，注明出处与页码，资料不足时会如实说明。', guide_you_can: '您可以询问', guide_start: '开始对话',
  ev_illustrative: '同一主题的示意照片——并非事件现场拍摄', ev_direct: '与该事件相关的书中插图', ev_prev: '上一节点', ev_next: '下一节点', ev_close: '关闭', ev_topic: '查看专题', ev_open: '阅读讲解', ev_of: '/',
  tl_intro: '以下每个节点都引用了书页或文件条款，没有为填补空白而添加任何节点。',
  per_pre: '通往日内瓦之路', per_pre_desc: '日内瓦会议的国际背景，以及1954年以前的桥梁历史。',
  per_p1: '执行日内瓦协议', per_p1_desc: '按书中的分期，非军事区执行协议的斗争从1954年7月持续到1956年7月。',
  per_p2: '分隔的岁月', per_p2_desc: '1956年7月以后普选未能举行（据书中所述）；两岸进入涂漆、旗杆之争、广播对喊与轰炸的年代，直至1967年。',
  chat_guide_title: '博物馆 AI 讲解员', chat_guide_intro: '我依据展出的资料进行讲解：《分界线两岸（1954–1967）》一书、档案照片和日内瓦文件。每条信息都附出处与页码；资料不足时我会如实说明。',
  chat_themes: '按主题推荐', chat_view_sources: '查看资料来源', chat_view_timeline: '时间线', chat_view_gallery: '展厅', chat_guide_name: '讲解员',
  gal_intro: '藏品包括34张档案照片（Archive_2）、16张补充照片（Archive_4：10张历史照片、6张今日遗迹/展品照片）和12幅书中插图。补充照片随附的说明标注为未核实。除说明注明外，拍摄年份未确定；照片中的人物不作身份认定。',
  gt_bridge: '桥', gt_flagpoles: '旗杆', gt_gate: '牌楼', gt_slogan_wall: '标语', gt_loudspeakers: '广播喇叭', gt_banner_diem: '南岸横幅', gt_geneva: '日内瓦', gt_dmz: '非军事区', gt_postcard: '明信片', gt_police: '警察',
  menu: '菜单',
  appName: 'AI 博物馆讲解员', tagline: '贤良桥——十七度线与分界线两岸（1954–1967）',
  nav_home: '简介', nav_chat: 'AI 问答', nav_gallery: '图片库', nav_timeline: '时间线', nav_stories: '故事', an_eyebrow: '时间线之外', an_title: '趣味小故事', an_intro: '贤良两岸生动的小故事：油漆之争、旗杆之争、广播对喊、连夜缝补的旗帜……每个故事都根据书籍、文章和报刊讲述并附来源；来源不一致之处会明确说明。', an_all: '阅读全部故事', an_read: '阅读故事', an_sources: '来源', an_notes: '各来源记载不一之处', an_ask: '向讲解员询问这个故事', an_note: '故事由项目组根据所引来源编写；英文/中文为项目组翻译。', an_web: '网络报刊', an_unverified_web: '网络来源——未与印刷版核对', an_back: '回到顶部', nav_topics: '专题', nav_settings: '设置',
  home_intro: '可用越南语、English 或中文提问，获得基于史料、附出处与页码的回答，并查看相关图片、收听语音讲解。',
  home_scope_title: '范围与原则', home_scope_1: '核心资料：黄志孝博士《分界线两岸（1954–1967）》（扫描件，文字来自 OCR，可能有声调错误）。',
  home_scope_2: '严格区分 1954–1956 与 1956–1967 两个阶段；没有证据不将图片或事件归入某阶段。',
  home_scope_3: '日内瓦文件等外部资料单独存放并标注类型；临时军事分界线不是国界。', home_scope_4: '图片无足够证据时，拍摄年份与人物身份标为“未确定”。',
  home_examples: '试着提问', home_go_chat: '开始提问', home_go_gallery: '浏览图片库', home_go_timeline: '查看时间线', home_status: '系统状态',
  chat_placeholder: '输入问题，例如：贤良桥的“涂漆之争”是怎么回事？', chat_send: '发送', chat_thinking: '正在检索资料…', chat_empty: '还没有提问。可选择建议问题或自行输入。',
  chat_sources: '参考来源', chat_images: '相关图片', chat_listen: '收听讲解', chat_page: '第', chat_pdf: 'PDF 页', chat_book: '书籍', chat_external: '外部文件/参考', chat_article: '文章（二手资料）', chat_web: '网络报刊', chat_note: '来源对照说明', gal_contemporary: '今日遗迹/展品照片', img_fn_title: '图片随附的原始说明', img_fn_note: '未经核实。', img_link_caption: '文章中的图片说明',
  chat_conf: '可信度', chat_conf_high: '高', chat_conf_medium: '中', chat_conf_low: '低', chat_insufficient: '资料库中证据不足',
  chat_fallback: 'AI 模型不可用——仅显示相关段落', chat_warn: '核验提示', chat_clear: '清除对话', chat_unverified: 'OCR 文本尚未经编辑核对', chat_error: '无法发送问题', chat_retry: '重试',
  audio_play: '播放', audio_pause: '暂停', audio_stop: '停止', audio_replay: '重播', audio_loading: '正在生成语音…', audio_error: '无法生成语音（聊天仍可使用）', audio_text: '正在朗读的文本',
  gal_title: '历史图片库', gal_search: '搜索描述或图中文字…', gal_topic: '专题', gal_all: '全部', gal_kind: '类型', gal_archive: '档案照片（ZIP）', gal_book: '书中插图', gal_hide: '隐藏重复版本', gal_count: '张图片', gal_empty: '没有符合条件的图片。', gal_open: '查看大图', gal_close: '关闭',
  img_visual: '画面所见', img_context: '历史背景（依据书籍/已核实资料）', img_location: '地点', img_time: '时期', img_date: '估计拍摄日期', img_text: '图中文字', img_people: '人物', img_source: '来源', img_pages: '相关书页', img_topics: '相关专题',
  img_notes: '核验说明', img_conf: '把握程度', img_dup: '相关/其他版本', img_rights: '使用权限', img_back: '返回图片库', img_desc_note: '详细描述目前仅有越南语。', img_passages: '相关书中段落', img_link_direct: '与书中印刷图片相同',
  img_link_topic: '按专题关联（不证明同一时刻）', img_watermarks: '可见水印',
  tl_title: '时间线', tl_all: '全部', tl_p1: '1954–1956', tl_p2: '1956–1967', tl_pre: '1954年前', tl_source: '来源', tl_ask: '问聊天机器人', tl_empty: '没有事件。', tl_note: '仅列出有书页引用或文件条款支撑的事件。', tl_evidence: 'OCR 证据',
  tp_title: '历史专题', tp_events: '个事件', tp_images: '张图片', tp_chapters: '相关章节', tp_passages: '书中摘录（OCR）', tp_back: '返回专题', tp_pages: '印刷页',
  set_title: '设置', set_ui_lang: '界面语言', set_answer_lang: '回答语言', set_auto: '按问题自动识别', set_voice: 'ElevenLabs 语音 ID（可选）', set_voice_hint: '留空则使用各语言默认语音。免费套餐只能使用预置语音。',
  set_health: '服务状态', set_llm: 'AI 模型', set_tts: '语音', set_configured: '已配置', set_missing: '未配置', set_retrieval: '检索',
  loading: '加载中…', error_generic: '出错了', retry: '重试', not_determined: '未确定',
}
export const DICTS: Record<Lang, Dict> = { vi, en, zh }

interface Ctx { lang: Lang; setLang: (l: Lang) => void; t: (k: string) => string; pick: (o: { vi?: string | null; en?: string | null; zh?: string | null }) => string }
const I18nCtx = createContext<Ctx | null>(null)

function readLS(k: string): string | null { try { return localStorage.getItem(k) } catch { return null } }
function writeLS(k: string, v: string) { try { localStorage.setItem(k, v) } catch { /* bỏ qua: storage có thể không khả dụng */ } }

export function I18nProvider({ children, initial }: { children: ReactNode; initial?: Lang }) {
  const stored = readLS('ui_lang') as Lang | null
  const [lang, setLangState] = useState<Lang>(initial ?? (stored && ['vi', 'en', 'zh'].includes(stored) ? stored : 'vi'))
  const value = useMemo<Ctx>(() => ({
    lang,
    setLang: (l) => { setLangState(l); writeLS('ui_lang', l); document.documentElement.lang = l },
    t: (k) => DICTS[lang][k] ?? vi[k] ?? k,
    pick: (o) => (lang === 'en' ? o.en || o.vi : lang === 'zh' ? o.zh || o.vi : o.vi) || '',
  }), [lang])
  return <I18nCtx.Provider value={value}>{children}</I18nCtx.Provider>
}
export function useI18n(): Ctx {
  const c = useContext(I18nCtx)
  if (!c) throw new Error('I18nProvider missing')
  return c
}
export { readLS, writeLS }
