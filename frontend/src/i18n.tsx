import { createContext, useContext } from 'react';
import type { ZoneId } from './data';

export type Lang = 'vi' | 'en' | 'zh';
export const LANGS: { id: Lang; label: string; short: string; speech: string }[] = [
  { id: 'vi', label: 'Tiếng Việt', short: 'VI', speech: 'vi-VN' },
  { id: 'en', label: 'English', short: 'EN', speech: 'en-US' },
  { id: 'zh', label: '中文', short: '中', speech: 'zh-CN' },
];

const D = {
  brand: { vi: 'VĨ TUYẾN 17 · DI SẢN SỐ', en: '17TH PARALLEL · DIGITAL HERITAGE', zh: '十七度线 · 数字遗产' },
  map: { vi: 'Bản đồ tổng quan', en: 'Site map', zh: '总览地图' },
  backMap: { vi: 'Quay lại bản đồ', en: 'Back to the map', zh: '返回地图' },
  backHall: { vi: 'Quay lại gian trưng bày', en: 'Back to the hall', zh: '返回展厅' },
  crumbs: { vi: 'Vị trí', en: 'Location', zh: '位置' },
  tools: { vi: 'Công cụ tham quan', en: 'Visit tools', zh: '参观工具' },
  soundOn: { vi: 'Tắt âm thanh', en: 'Mute', zh: '静音' },
  soundOff: { vi: 'Bật âm thanh', en: 'Unmute', zh: '打开声音' },
  fullscreen: { vi: 'Toàn màn hình', en: 'Full screen', zh: '全屏' },
  exitFullscreen: { vi: 'Thoát toàn màn hình', en: 'Exit full screen', zh: '退出全屏' },
  language: { vi: 'Ngôn ngữ', en: 'Language', zh: '语言' },
  share: { vi: 'Chia sẻ', en: 'Share', zh: '分享' },
  copy: { vi: 'Sao chép liên kết', en: 'Copy link', zh: '复制链接' },
  copied: { vi: 'Đã sao chép liên kết.', en: 'Link copied.', zh: '链接已复制。' },
  copyFail: { vi: 'Không thể sao chép liên kết.', en: 'Could not copy the link.', zh: '无法复制链接。' },
  fullscreenFail: { vi: 'Không thể mở chế độ toàn màn hình trên trình duyệt này.', en: 'Full screen is not available in this browser.', zh: '此浏览器无法全屏。' },
  langChanged: { vi: 'Đã chuyển sang Tiếng Việt', en: 'Switched to English', zh: '已切换为中文' },
  // chat
  askPlaceholder: { vi: 'Hỏi tôi về di tích Vĩ tuyến 17…', en: 'Ask me about the 17th Parallel site…', zh: '向我提问十七度线遗址…' },
  askAbout: { vi: 'Hỏi về {x}…', en: 'Ask about {x}…', zh: '询问关于{x}…' },
  askLabel: { vi: 'Câu hỏi tra cứu tư liệu', en: 'Question about the archive', zh: '资料查询问题' },
  voiceInput: { vi: 'Nhập bằng giọng nói', en: 'Speak your question', zh: '语音输入' },
  send: { vi: 'Gửi câu hỏi', en: 'Send', zh: '发送' },
  searching: { vi: 'Đang soạn câu trả lời từ tư liệu…', en: 'Preparing an answer from the archive…', zh: '正在根据资料生成回答…' },
  chatError: { vi: 'Chưa kết nối được kho tư liệu museum-guide. Hãy chạy backend museum-guide và thử lại.', en: 'Could not reach the museum-guide archive. Please start the museum-guide backend and try again.', zh: '无法连接museum-guide资料库。请启动museum-guide后端后重试。' },
  sources: { vi: 'Nguồn', en: 'Sources', zh: '来源' },
  sourcesFull: { vi: 'Nguồn tư liệu', en: 'Sources', zh: '资料来源' },
  suggestions: { vi: 'Gợi ý câu hỏi', en: 'Try asking', zh: '推荐问题' },
  chatHistory: { vi: 'Hội thoại', en: 'Conversation', zh: '对话' },
  hideChat: { vi: 'Thu gọn hội thoại', en: 'Collapse conversation', zh: '收起对话' },
  showChat: { vi: 'Mở hội thoại', en: 'Open conversation', zh: '展开对话' },
  clearChat: { vi: 'Xoá hội thoại', en: 'Clear conversation', zh: '清除对话' },
  imagesInAnswer: { vi: 'Ảnh tư liệu liên quan – chạm để xem lớn', en: 'Related archive photos – tap to enlarge', zh: '相关档案照片——点击放大' },
  noSpeechInput: { vi: 'Trình duyệt chưa hỗ trợ nhập câu hỏi bằng giọng nói.', en: 'This browser does not support voice input.', zh: '此浏览器不支持语音输入。' },
  // common
  loading: { vi: 'Đang tải tư liệu…', en: 'Loading…', zh: '正在加载…' },
  retry: { vi: 'Tải lại', en: 'Retry', zh: '重试' },
  loadError: { vi: 'Không tải được tư liệu từ kho museum-guide ({x}). Hãy kiểm tra backend museum-guide đang chạy.', en: 'Could not load data from the museum-guide archive ({x}). Please check that the museum-guide backend is running.', zh: '无法从museum-guide资料库加载数据（{x}）。请确认museum-guide后端正在运行。' },
  close: { vi: 'Đóng', en: 'Close', zh: '关闭' },
  prev: { vi: 'Trước', en: 'Previous', zh: '上一张' },
  next: { vi: 'Sau', en: 'Next', zh: '下一张' },
  zoomIn: { vi: 'Phóng to', en: 'Zoom in', zh: '放大' },
  zoomOut: { vi: 'Thu nhỏ', en: 'Zoom out', zh: '缩小' },
  zoomReset: { vi: 'Vừa khung', en: 'Fit', zh: '适应窗口' },
  enlarge: { vi: 'Xem lớn', en: 'Enlarge', zh: '放大查看' },
  readMore: { vi: 'Đọc tiếp', en: 'Read more', zh: '继续阅读' },
  readLess: { vi: 'Thu gọn', en: 'Show less', zh: '收起' },
  translationNote: { vi: '', en: 'English text translated by the project team.', zh: '中文内容由项目组翻译。' },
  // narration
  play: { vi: 'Phát thuyết minh', en: 'Play narration', zh: '播放解说' },
  pause: { vi: 'Tạm dừng thuyết minh', en: 'Pause narration', zh: '暂停解说' },
  narrationLoading: { vi: 'Đang chuẩn bị giọng đọc…', en: 'Preparing the voice…', zh: '正在准备语音…' },
  browserVoice: { vi: 'Đang dùng giọng đọc của trình duyệt (chưa kết nối được ElevenLabs).', en: 'Using the browser voice (ElevenLabs not available).', zh: '正在使用浏览器语音（ElevenLabs不可用）。' },
  tapToPlay: { vi: 'Chạm nút phát để nghe thuyết minh.', en: 'Tap play to hear the narration.', zh: '点击播放按钮收听解说。' },
  noVoice: { vi: 'Trình duyệt chưa hỗ trợ đọc thuyết minh.', en: 'This browser cannot read the narration aloud.', zh: '此浏览器无法朗读解说。' },
  // guide
  guideSpeaking: { vi: 'đang thuyết minh', en: 'is speaking', zh: '正在讲解' },
  hideBubble: { vi: 'Ẩn lời hướng dẫn', en: 'Hide the guide', zh: '隐藏讲解' },
  showBubble: { vi: 'Hiện lời hướng dẫn', en: 'Show the guide', zh: '显示讲解' },
  listenAgain: { vi: 'Nghe lại', en: 'Listen again', zh: '再听一遍' },
  // home
  homeKicker: { vi: 'DI TÍCH ĐÔI BỜ HIỀN LƯƠNG – BẾN HẢI', en: 'HIEN LUONG – BEN HAI RELIC SITE', zh: '贤良—边海两岸遗址' },
  homeTitle: { vi: 'Vĩ tuyến 17', en: 'The 17th Parallel', zh: '十七度线' },
  homeLead: { vi: 'Chọn một điểm đến để nghe thuyết minh và khám phá tư liệu.', en: 'Choose a place to hear its story and explore the archive.', zh: '选择一个地点，收听解说并浏览资料。' },
  homeHello: { vi: 'Xin chào!', en: 'Hello!', zh: '您好！' },
  homeBubble: { vi: 'Mình là chú bộ đội hướng dẫn ảo của di tích Vĩ tuyến 17. Hãy chạm vào các điểm đến để khám phá nhé!', en: "I'm the virtual guide of the 17th Parallel site. Tap a place on the map to explore!", zh: '我是十七度线遗址的虚拟讲解员。点击地图上的地点开始探索吧！' },
  homeIntro: { vi: 'Nghe giới thiệu tổng quan khu di tích', en: 'Hear an introduction to the site', zh: '收听遗址总体介绍' },
  homeIntroText: {
    vi: 'Chào mừng bạn đến với khu di tích đôi bờ Hiền Lương – Bến Hải. Năm 1954, Hiệp định Genève lấy vĩ tuyến 17 – dòng sông Bến Hải – làm giới tuyến quân sự tạm thời. Hãy chạm vào Cầu Hiền Lương, Nhà trưng bày, Kỳ đài, Tượng đài hay Nhà liên hợp để nghe câu chuyện của từng nơi.',
    en: 'Welcome to the Hien Luong – Ben Hai relic site. In 1954 the Geneva Agreement took the 17th parallel – the Ben Hai river – as a provisional military demarcation line. Tap the bridge, the exhibition hall, the flag tower, the monument or the joint commission house to hear each story.',
    zh: '欢迎来到贤良—边海两岸遗址。1954年，日内瓦协定以北纬17度线——边海河——为临时军事分界线。点击贤良桥、展厅、旗台、纪念碑或联合委员会会所，收听每个地方的故事。',
  },
  photos: { vi: 'Hình ảnh tư liệu', en: 'Archive photos', zh: '档案图片' },
  stories: { vi: 'Câu chuyện lịch sử', en: 'Historical stories', zh: '历史故事' },
  seePhotos: { vi: 'Xem ảnh địa điểm', en: 'See photos', zh: '查看图片' },
  hearStory: { vi: 'Nghe câu chuyện', en: 'Hear the story', zh: '收听故事' },
  chooseDestination: { vi: 'Chọn địa điểm tham quan', en: 'Choose a place to visit', zh: '选择参观地点' },
  explore: { vi: 'Khám phá {x}', en: 'Explore {x}', zh: '探索{x}' },
  // zones
  tabStories: { vi: 'Câu chuyện', en: 'Stories', zh: '故事' },
  tabTimeline: { vi: 'Dòng thời gian', en: 'Timeline', zh: '时间线' },
  tabPhotos: { vi: 'Ảnh', en: 'Photos', zh: '图片' },
  history: { vi: 'Lịch sử hình thành', en: 'History', zh: '形成历史' },
  placeNote: { vi: 'Ảnh khu vực lấy từ bộ ảnh của dự án; nội dung lịch sử tổng hợp từ các trang báo, cổng di sản và sách đã ghi nguồn.', en: 'Photos come from the project image set; the history is compiled from the cited newspapers, heritage portal and book.', zh: '地点图片来自项目图库；历史内容综合自所注明的报刊、遗产门户网站和书籍。' },
  bridgeIntro: { vi: 'Cây cầu chứng kiến hơn hai mươi năm chia cắt', en: 'A bridge that witnessed more than twenty years of division', zh: '见证二十多年分隔的桥' },
  flagIntro: { vi: 'Chọi cờ và những người may, vá cờ trên vĩ tuyến', en: 'The flag contest and the people who sewed and mended the flags', zh: '斗旗，以及缝补国旗的人们' },
  bookPage: { vi: 'Sách “Đôi bờ giới tuyến” tr.{x}', en: 'Book “Đôi bờ giới tuyến” p.{x}', zh: '《分界线两岸》第{x}页' },
  // hall
  hallHint: { vi: 'Chạm vào một hiện vật để phóng to và nghe kể chuyện', en: 'Tap an exhibit to zoom in and hear its story', zh: '点击展品即可放大并收听故事' },
  exhibits: { vi: 'Hiện vật trưng bày', en: 'Exhibits', zh: '展品' },
  relatedPhotos: { vi: 'Ảnh tư liệu liên quan', en: 'Related archive photos', zh: '相关档案照片' },
  noArchivePhoto: { vi: 'Chưa có ảnh tư liệu riêng cho hiện vật này – hãy hỏi trợ lý ở thanh chat để tìm thêm.', en: 'No archive photo for this exhibit yet – ask the assistant in the chat bar to find more.', zh: '此展品暂无专门的档案照片——可在聊天栏向助手查询更多。' },
  exhibitOf: { vi: 'Hiện vật {a}/{b}', en: 'Exhibit {a}/{b}', zh: '展品 {a}/{b}' },
  allPhotos: { vi: 'Tất cả ảnh tư liệu trong kho', en: 'All archive photos', zh: '资料库全部照片' },
  allStories: { vi: 'Những mẩu chuyện thú vị', en: 'Remarkable stories', zh: '趣味小故事' },
  askThis: { vi: 'Hỏi thêm về hiện vật này', en: 'Ask more about this exhibit', zh: '进一步询问此展品' },
  qMore: { vi: 'Kể thêm về “{x}”', en: 'Tell me more about “{x}”', zh: '再讲讲“{x}”' },
  qWhy: { vi: '“{x}” gắn với sự kiện nào?', en: 'Which events is “{x}” linked to?', zh: '“{x}”与哪些事件有关？' },
  // nhà trưng bày theo chủ đề
  topicNo: { vi: 'Chủ đề {x}', en: 'Topic {x}', zh: '主题{x}' },
  topicsNav: { vi: 'Hành trình tham quan', en: 'Visit journey', zh: '参观路线' },
  roomHint: { vi: 'Chạm vào một chủ đề hoặc hiện vật để bắt đầu', en: 'Tap a topic or an exhibit to begin', zh: '点击一个主题或展品开始参观' },
  roomGreeting: { vi: 'Chào mừng bạn đến Nhà trưng bày Vĩ tuyến 17! Phòng được chia thành bốn chủ đề theo dòng lịch sử, từ Hiệp định Giơ-ne-vơ năm 1954 đến ngày giải phóng Quảng Trị năm 1972. Hãy chạm vào một chủ đề để bắt đầu nhé.', en: 'Welcome to the 17th Parallel Exhibition Hall! The room is divided into four topics in historical order, from the 1954 Geneva Agreement to the liberation of Quang Tri in 1972. Tap a topic to begin.', zh: '欢迎来到十七度线展厅！展厅按历史顺序分为四个主题，从1954年日内瓦协定到1972年广治解放。请点击一个主题开始参观。' },
  backRoom: { vi: 'Về phòng trưng bày', en: 'Back to the hall', zh: '返回展厅' },
  itemsOfTopic: { vi: 'Hiện vật trong chủ đề', en: 'Exhibits in this topic', zh: '本主题展品' },
  needsSource: { vi: 'Cần bổ sung nguồn', en: 'Source needed', zh: '需补充来源' },
  needsSourceLong: { vi: 'Hiện vật này có trong danh mục nhưng chưa có đủ tư liệu gốc. Nội dung dưới đây chỉ gồm phần đã có nguồn.', en: 'This exhibit is on the list but lacks original documentation. The text below includes only what is sourced.', zh: '此展品列在清单中，但原始资料不足。以下内容仅包含有来源的部分。' },
  archivePhotos: { vi: 'Hình ảnh tư liệu', en: 'Archive photos', zh: '档案图片' },
  photoAtSource: { vi: 'Xem ảnh tại bài báo nguồn', en: 'See photos in the source article', zh: '在来源文章中查看照片' },
  illustration: { vi: 'Không gian và hiện vật vẽ trong ảnh là hình minh hoạ.', en: 'The room and objects in the picture are illustrations.', zh: '画面中的空间和展品为示意图。' },
  enterTopic: { vi: 'Vào chủ đề', en: 'Enter topic', zh: '进入主题' },
  itemOf: { vi: '{a}/{b}', en: '{a}/{b}', zh: '{a}/{b}' },
  introTitle: { vi: 'Tượng Chủ tịch Hồ Chí Minh', en: 'Statue of President Ho Chi Minh', zh: '胡志明主席雕像' },
  qTopic: { vi: 'Tóm tắt chủ đề “{x}”', en: 'Summarise the topic “{x}”', zh: '概括主题“{x}”' },
} as const;

export type Key = keyof typeof D;
export const KEYS = Object.keys(D) as Key[];

export function tr(lang: Lang, key: Key, vars?: Record<string, string | number>): string {
  let s: string = D[key][lang] || D[key].vi;
  if (vars) for (const [k, v] of Object.entries(vars)) s = s.split(`{${k}}`).join(String(v));
  return s;
}

/** Chọn bản dịch từ object {vi, en, zh}; thiếu thì lùi về vi. */
export function pick<T>(m: Partial<Record<Lang, T>> | null | undefined, lang: Lang): T | undefined {
  if (!m) return undefined;
  return (m[lang] ?? m.vi) as T | undefined;
}

export const ZONE_TEXT: Record<ZoneId, { title: Record<Lang, string>; short: Record<Lang, string>; questions: Record<Lang, string[]> }> = {
  bridge: {
    title: { vi: 'Cầu Hiền Lương', en: 'Hien Luong Bridge', zh: '贤良桥' },
    short: { vi: 'Cây cầu lịch sử trên sông Bến Hải', en: 'The historic bridge over the Ben Hai', zh: '边海河上的历史名桥' },
    questions: {
      vi: ['Vì sao cầu Hiền Lương có hai màu?', 'Cầu Hiền Lương bị đánh sập năm nào?'],
      en: ['Why did the Hien Luong bridge have two colours?', 'When was the Hien Luong bridge destroyed?'],
      zh: ['贤良桥为什么有两种颜色？', '贤良桥是哪一年被炸毁的？'],
    },
  },
  museum: {
    title: { vi: 'Nhà trưng bày Vĩ tuyến 17', en: '17th Parallel Exhibition Hall', zh: '十七度线展厅' },
    short: { vi: 'Không gian tư liệu, hình ảnh và hiện vật', en: 'Documents, photos and exhibits', zh: '资料、图片与展品' },
    questions: {
      vi: ['Cuộc đấu loa ở Hiền Lương diễn ra thế nào?', 'Chiếc loa 500W bây giờ ở đâu?'],
      en: ['How did the loudspeaker contest at Hien Luong unfold?', 'Where is the 500 W loudspeaker today?'],
      zh: ['贤良的“斗喇叭”是怎样进行的？', '那只500瓦的喇叭现在在哪里？'],
    },
  },
  flag: {
    title: { vi: 'Kỳ đài Hiền Lương', en: 'Hien Luong Flag Tower', zh: '贤良旗台' },
    short: { vi: 'Cột cờ và cuộc chọi cờ hai bờ', en: 'The flagpole and the flag contest', zh: '旗杆与两岸斗旗' },
    questions: {
      vi: ['Kể chuyện chọi cờ ở Hiền Lương', 'Ai đã may và vá cờ Hiền Lương?'],
      en: ['Tell me about the flag contest at Hien Luong', 'Who sewed and mended the Hien Luong flags?'],
      zh: ['讲讲贤良的斗旗故事', '是谁缝补了贤良的国旗？'],
    },
  },
  monument: {
    title: { vi: 'Tượng đài Khát vọng thống nhất', en: 'Aspiration for Reunification Monument', zh: '渴望统一纪念碑' },
    short: { vi: 'Thông điệp về hòa bình và đoàn tụ', en: 'A message of peace and reunion', zh: '和平与团圆的寄托' },
    questions: {
      vi: ['Tượng đài Khát vọng thống nhất có ý nghĩa gì?', 'Khu vực bờ Nam được tôn tạo khi nào?'],
      en: ['What does the Aspiration for Reunification monument mean?', 'When was the south bank restored?'],
      zh: ['渴望统一纪念碑有什么意义？', '南岸是什么时候修复的？'],
    },
  },
  union: {
    title: { vi: 'Nhà liên hợp', en: 'Joint Commission House', zh: '联合委员会会所' },
    short: { vi: 'Nơi họp của Ủy ban Liên hợp hai bên', en: 'Meeting place of the joint commission', zh: '双方联合委员会的会议地点' },
    questions: {
      vi: ['Ban Liên hiệp khu phi quân sự làm việc thế nào?', 'Tổ Quốc tế 76 là gì?'],
      en: ['How did the demilitarized-zone joint commission work?', 'What was International Team 76?'],
      zh: ['非军事区联合委员会是怎样工作的？', '国际监察第76小组是什么？'],
    },
  },
};

export const LangContext = createContext<Lang>('vi');
export function useLang() { return useContext(LangContext); }
export function useT() {
  const lang = useLang();
  return (key: Key, vars?: Record<string, string | number>) => tr(lang, key, vars);
}
