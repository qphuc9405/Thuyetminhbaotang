export type MuseumExhibit = {
  id: string;
  title: string;
  shortTitle: string;
  category: string;
  point: { x: number; y: number };
  crop: { x: number; y: number; width: number; height: number };
  image?: { src: string; width: number; height: number };
  summary: string;
  paragraphs: string[];
  details: string[];
  topic?: number;
};

export const museumRoom = '/museum/exhibition-room-topics.png';

// All coordinates refer to the supplied 1672 × 941 interface image.
export const museumExhibits: MuseumExhibit[] = [
  {
    id: 'topic-1', topic: 1,
    title: 'Hiệp định Giơ-ne-vơ và giới tuyến tạm thời (1954)', shortTitle: 'Chia cắt', category: 'Chủ đề 1',
    point: { x: 14.4, y: 45.1 },
    crop: { x: 1, y: 7, width: 22, height: 42 },
    summary: 'Khởi đầu của chia cắt – vạch nên Vĩ tuyến 17.',
    paragraphs: ['Chủ đề mở đầu giới thiệu Hiệp định Giơ-ne-vơ năm 1954 và giới tuyến quân sự tạm thời. Không gian trưng bày kết hợp bảng giới thiệu, sơ đồ giới tuyến và các tài liệu về việc qua lại hai miền.', 'Quan sát sơ đồ để nhận biết vị trí giới tuyến và cách bố trí hai vùng Bắc – Nam trong phần trưng bày.'],
    details: ['Bảng Hiệp định Giơ-ne-vơ (1954)', 'Sơ đồ giới tuyến tạm thời', 'Sổ thông hành và giấy phép qua giới tuyến'],
  },
  {
    id: 'topic-2', topic: 2,
    title: 'Vĩnh Linh, lũy thép nơi tuyến đầu', shortTitle: 'Kiên cường bám trụ', category: 'Chủ đề 2',
    point: { x: 34.9, y: 40.8 },
    crop: { x: 24.5, y: 15, width: 20, height: 39 },
    summary: 'Xây dựng hậu phương vững chắc, kiên cường bám trụ, đánh trả mọi âm mưu chia cắt.',
    paragraphs: ['Không gian chủ đề tái hiện hầm trú ẩn cùng cảnh quan và các dụng cụ phục vụ đời sống, lao động trong điều kiện chiến tranh.', 'Các nhóm trưng bày về vũ khí tự tạo, mảnh bom đạn và dụng cụ đào địa đạo gợi mở câu chuyện bám trụ của quân dân Vĩnh Linh.'],
    details: ['Mô hình hầm trú ẩn', 'Vũ khí tự tạo và mảnh bom đạn', 'Dụng cụ đào địa đạo'],
  },
  {
    id: 'topic-3', topic: 3,
    title: 'Khát vọng thống nhất của đồng bào bờ Nam', shortTitle: 'Khát vọng sum họp', category: 'Chủ đề 3',
    point: { x: 68.7, y: 40.5 },
    crop: { x: 59.5, y: 15, width: 19, height: 50 },
    summary: 'Vượt qua chia cắt, gìn giữ niềm tin, hướng về ngày sum họp.',
    paragraphs: ['Chủ đề giới thiệu khát vọng đoàn tụ qua hình ảnh chiếc đò vượt sông, các khung ảnh và những kỷ vật được đặt trong tủ kính.', 'Thư tay, kỷ vật và vật dụng cá nhân tạo nên một góc nhìn gần gũi về con người trong câu chuyện chia cắt và mong đợi ngày thống nhất.'],
    details: ['Đò vượt sông bờ Nam – Vĩnh Linh', 'Ảnh và tài liệu trưng bày', 'Thư tay, kỷ vật và vật dụng cá nhân'],
  },
  {
    id: 'topic-4', topic: 4,
    title: 'Ngày chiến thắng và hồi sinh', shortTitle: 'Thống nhất – Hồi sinh', category: 'Chủ đề 4',
    point: { x: 93.4, y: 47.4 },
    crop: { x: 80, y: 7, width: 19, height: 42 },
    summary: 'Nam – Bắc sum họp, đất nước thống nhất, bước vào công cuộc hàn gắn và xây dựng.',
    paragraphs: ['Góc trưng bày khép lại hành trình với chủ đề ngày chiến thắng, đoàn tụ và hồi sinh. Bức ảnh “Nam – Bắc sum họp (30.4.1975)” là điểm nhấn của khu vực.', 'Cờ và huân huy chương được trưng bày bên cạnh ảnh đoàn tụ, kết nối câu chuyện thống nhất với chặng đường hàn gắn và xây dựng.'],
    details: ['Ảnh Nam – Bắc sum họp (30.4.1975)', 'Cờ và huân huy chương chiến thắng', 'Chủ đề hàn gắn và xây dựng'],
  },
  {
    id: 'mother-and-flag', title: 'Mẹ Vĩnh Linh và cờ', shortTitle: 'Mẹ Vĩnh Linh và cờ', category: 'Tổ hợp hình tượng',
    point: { x: 30.7, y: 62.7 },
    crop: { x: 18.5, y: 46, width: 21.5, height: 32 },
    summary: 'Biểu tượng của niềm tin và khát vọng thống nhất.',
    paragraphs: ['Hình tượng người mẹ ngồi chăm chút lá cờ đỏ sao vàng được đặt trên bệ riêng ở phía trái phòng. Lá cờ trải rộng về phía trước, tạo điểm nhấn màu đỏ trong không gian trưng bày.', 'Quan sát đôi tay, dáng ngồi của người mẹ và ngôi sao trên lá cờ để khám phá những chi tiết của tổ hợp hình tượng.'],
    details: ['Hình tượng người mẹ ngồi bên lá cờ', 'Lá cờ đỏ sao vàng', 'Bệ trưng bày Mẹ Vĩnh Linh và cờ'],
  },
  {
    id: 'loudspeaker', title: 'Loa phát thanh', shortTitle: 'Loa phát thanh', category: 'Thiết bị truyền thanh',
    point: { x: 86.7, y: 56.4 },
    crop: { x: 78, y: 49, width: 15.5, height: 27 },
    summary: 'Tiếng nói của miền Nam hướng về ngày thống nhất.',
    paragraphs: ['Chiếc loa phát thanh có miệng kèn lớn, thân loa và giá đỡ đặt trên bệ riêng ở phía phải phòng.', 'Góc trưng bày gợi mở câu chuyện truyền thanh trong không gian đôi bờ. Bạn có thể quan sát miệng loa, phần thân và các bộ phận gắn phía sau.'],
    details: ['Miệng loa hình kèn', 'Thân loa và giá đỡ', 'Bệ trưng bày riêng ở phía phải phòng'],
  },
  {
    id: 'bronze-star', title: 'Ngôi sao', shortTitle: 'Ngôi sao', category: 'Biểu tượng trưng bày',
    point: { x: 50.8, y: 62.2 },
    crop: { x: 43, y: 50, width: 15, height: 24 },
    summary: 'Biểu tượng của độc lập, thống nhất Tổ quốc.',
    paragraphs: ['Ngôi sao năm cánh màu vàng được đặt ở trung tâm tiền cảnh trong tủ kính. Bệ có nền đỏ và bảng tên “Ngôi sao”.', 'Vị trí giữa phòng giúp ngôi sao trở thành điểm kết nối thị giác giữa hình tượng Mẹ Vĩnh Linh và loa phát thanh.'],
    details: ['Ngôi sao năm cánh màu vàng', 'Tủ kính với nền trưng bày màu đỏ', 'Vị trí trung tâm tiền cảnh'],
  },
];
