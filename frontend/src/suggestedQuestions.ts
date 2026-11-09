import type { ZoneId } from './data';

// Sample copy: replace these questions when the content for each area is ready.
export const suggestedQuestions: Record<ZoneId | 'home', readonly [string, string, string]> = {
  home: [
    'Khu di tích Vĩ tuyến 17 có gì nổi bật?',
    'Tôi nên bắt đầu tham quan từ đâu?',
    'Tôi có thể tìm hiểu những địa điểm nào?',
  ],
  bridge: [
    'Cầu Hiền Lương có ý nghĩa lịch sử gì?',
    'Sông Bến Hải gắn với câu chuyện nào?',
    'Vì sao cầu Hiền Lương có hai màu?',
  ],
  museum: [
    'Nhà trưng bày giới thiệu những gì?',
    'Những hiện vật nào đáng chú ý?',
    'Các hiện vật kể câu chuyện lịch sử gì?',
  ],
  flag: [
    'Kỳ đài Hiền Lương có ý nghĩa gì?',
    'Lá cờ tại kỳ đài gắn với câu chuyện nào?',
    'Kỳ đài nằm ở đâu trong khu di tích?',
  ],
  monument: [
    'Tượng đài Khát vọng thống nhất có ý nghĩa gì?',
    'Tượng đài thể hiện những hình tượng nào?',
    'Tượng đài nằm ở đâu trong khu di tích?',
  ],
  union: [
    'Nhà liên hiệp có vai trò gì?',
    'Nhà liên hiệp gắn với sự kiện nào?',
    'Có thể tìm hiểu gì tại Nhà liên hiệp?',
  ],
};
