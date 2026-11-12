// Câu hỏi gợi ý xây dựng từ những chủ đề THỰC SỰ có trong kho tư liệu (chương sách + văn kiện Genève).
import type { Lang } from '../api/client'

export interface Theme { key: string; label: Record<Lang, string>; q: Record<Lang, string[]> }

export const THEMES: Theme[] = [
  { key: 'geneva', label: { vi: 'Genève & vĩ tuyến 17', en: 'Geneva & the 17th parallel', zh: '日内瓦与十七度线' }, q: {
    vi: ['Vì sao vĩ tuyến 17 trở thành giới tuyến quân sự tạm thời?', 'Hiệp định ngày 20/7/1954 và Tuyên bố cuối cùng ngày 21/7/1954 khác nhau thế nào?'],
    en: ['Why did the 17th parallel become the provisional military demarcation line?', 'How does the 20 July 1954 Agreement differ from the 21 July 1954 Final Declaration?'],
    zh: ['为什么十七度线成为临时军事分界线？', '1954年7月20日的协定与7月21日的最后宣言有何不同？'] } },
  { key: 'bridge', label: { vi: 'Cầu Hiền Lương', en: 'The Hiền Lương bridge', zh: '贤良桥' }, q: {
    vi: ['Cầu Hiền Lương được phân chia như thế nào?', 'Vì sao cầu Hiền Lương có hai màu?'],
    en: ['How was the Hiền Lương bridge divided?', 'Why was the bridge painted in two colours?'],
    zh: ['贤良桥是如何被分割的？', '贤良桥为什么有两种颜色？'] } },
  { key: 'flag', label: { vi: 'Cột cờ Hiền Lương', en: 'The flagpoles', zh: '贤良旗杆' }, q: {
    vi: ['Vì sao lá cờ trên cột cờ Hiền Lương có ý nghĩa đặc biệt?', 'Việc bảo vệ lá cờ ở Hiền Lương khó khăn ra sao?'],
    en: ['Why did the flag at Hiền Lương carry special meaning?', 'How hard was it to protect the flag at Hiền Lương?'],
    zh: ['贤良旗杆上的旗帜为何意义特殊？', '守护贤良的旗帜有多艰难？'] } },
  { key: 'life', label: { vi: 'Đời sống hai bờ', en: 'Life on both banks', zh: '两岸生活' }, q: {
    vi: ['Người dân hai miền liên lạc với nhau bằng cách nào khi đất nước bị chia cắt?', 'Cuộc “đấu loa” ở hai bờ Bến Hải là gì?'],
    en: ['How did people in the two zones keep in touch while the country was divided?', 'What was the loudspeaker contest across the Bến Hải river?'],
    zh: ['国家分裂期间，两地人民如何保持联系？', '边海河两岸的“广播对喊”是怎么回事？'] } },
  { key: 'story', label: { vi: 'Nghe kể chuyện', en: 'Hear the story', zh: '听故事' }, q: {
    vi: ['Hãy kể cho tôi nghe câu chuyện về Cầu Hiền Lương từ năm 1954 đến 1967.', 'Vụ tống triệt ba nhân vật hòa bình ngày 19-3-1965 đã diễn ra như thế nào?'],
    en: ['Tell me the story of the Hiền Lương bridge from 1954 to 1967.', 'What happened during the expulsion of three peace activists on 19 March 1965?'],
    zh: ['请讲述1954至1967年贤良桥的故事。', '1965年3月19日三位和平人士被“驱逐”事件是怎样发生的？'] } },
  { key: 'anecdote', label: { vi: 'Mẩu chuyện thú vị', en: 'Fascinating stories', zh: '趣味小故事' }, q: {
    vi: ['Kể cho tôi nghe chuyện chọi cờ ở hai đầu cầu Hiền Lương.', 'Chiếc loa 500W ở Hiền Lương bây giờ ở đâu?'],
    en: ['Tell me about the flagpole duel at the two ends of the Hiền Lương bridge.', 'Where is the 500 W loudspeaker from Hiền Lương today?'],
    zh: ['给我讲讲贤良桥两端的旗杆之争。', '贤良的500瓦大喇叭现在在哪里？'] } },
]
