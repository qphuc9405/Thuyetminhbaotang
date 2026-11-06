export type ZoneId = 'bridge' | 'museum' | 'flag' | 'monument' | 'union';

export type Exhibit = {
  id: string;
  name: string;
  type: string;
  content: string;
  caption: string;
};

export type Zone = {
  id: ZoneId;
  title: string;
  short: string;
  description: string;
  script: string;
  accent: string;
  image: string;
  hotspot: {
    // Percentage coordinates on the 1672 × 941 map; the pin tip anchors here.
    x: number;
    y: number;
  };
  exhibits: Exhibit[];
};

export const zones: Zone[] = [
  {
    id: 'bridge',
    title: 'Cầu Hiền Lương',
    short: 'Cây cầu lịch sử trên sông Bến Hải',
    description: 'Cầu Hiền Lương bắc qua sông Bến Hải, gắn với thời kỳ giới tuyến quân sự tạm thời sau Hiệp định Genève năm 1954. Trong không gian tham quan này, khách có thể tìm hiểu những câu chuyện về cây cầu và hai bờ giới tuyến.',
    script: 'Chào mừng bạn đến với khu Cầu Hiền Lương. Cây cầu bắc qua sông Bến Hải là một biểu tượng lịch sử của khát vọng hòa bình và thống nhất. Hãy chọn một tư liệu phía dưới để khám phá thêm.',
    accent: '#d7b26b',
    image: '/home-reference-soldier.png',
    hotspot: {
      x: 32,
      y: 38,
    },
    exhibits: [
      {
        id: 'bridge-1',
        name: 'Cầu sắt lịch sử',
        type: 'Công trình',
        content: 'Tìm hiểu vai trò của cầu Hiền Lương và những lần thay đổi cấu trúc qua các thời kỳ. Ảnh nền giao diện là bản dựng minh họa, không phải ảnh lưu trữ hiện vật.',
        caption: 'Công trình lịch sử',
      },
      {
        id: 'bridge-2',
        name: 'Dòng sông Bến Hải',
        type: 'Địa danh',
        content: 'Sông Bến Hải gắn với giới tuyến quân sự tạm thời tại vĩ tuyến 17. Đây không phải đường biên giới quốc gia vĩnh viễn.',
        caption: 'Không gian địa lý',
      },
      {
        id: 'bridge-3',
        name: 'Câu chuyện đôi bờ',
        type: 'Tư liệu',
        content: 'Những câu chuyện về cuộc sống và khát vọng đoàn tụ của nhân dân hai bờ cần được gắn với tư liệu đã kiểm duyệt khi đưa lên hệ thống chính thức.',
        caption: 'Chủ đề lịch sử',
      },
    ],
  },
  {
    id: 'museum',
    title: 'Nhà trưng bày Vĩ tuyến 17',
    short: 'Không gian tư liệu, hình ảnh và hiện vật',
    description: 'Không gian giới thiệu lịch sử đôi bờ Hiền Lương – Bến Hải qua tài liệu, hình ảnh và hiện vật. Dữ liệu hiện tại chỉ dùng cho bản demo frontend; danh mục hiện vật thực tế cần được bảo tàng xác nhận.',
    script: 'Bạn đang khám phá Nhà trưng bày Vĩ tuyến 17. Không gian này giúp kết nối hiện vật với những câu chuyện về cuộc sống, đấu tranh và khát vọng thống nhất đất nước.',
    accent: '#e8cb92',
    image: '/home-reference-soldier.png',
    hotspot: {
      x: 20.9,
      y: 15.2,
    },
    exhibits: [
      {
        id: 'museum-1',
        name: 'Ảnh tư liệu lịch sử',
        type: 'Hình ảnh',
        content: 'Tư liệu ảnh về đời sống và lịch sử vùng giới tuyến. Cần tải ảnh được cấp quyền và ghi rõ nguồn lưu trữ.',
        caption: 'Bộ sưu tập hình ảnh',
      },
      {
        id: 'museum-2',
        name: 'Hồ sơ và văn bản',
        type: 'Tài liệu',
        content: 'Các bản đồ, văn bản và hồ sơ lịch sử phục vụ nghiên cứu cần được biên mục, số hóa và kiểm duyệt.',
        caption: 'Tài liệu trưng bày',
      },
      {
        id: 'museum-3',
        name: 'Câu chuyện hiện vật',
        type: 'Thuyết minh',
        content: 'Mỗi hiện vật sẽ có kịch bản thuyết minh tiếng Việt, tiếng Anh, ảnh và nguồn tham khảo riêng khi kết nối backend.',
        caption: 'Kịch bản theo hiện vật',
      },
    ],
  },
  {
    id: 'flag',
    title: 'Kỳ đài Hiền Lương',
    short: 'Biểu tượng chủ quyền và khát vọng thống nhất',
    description: 'Kỳ đài Hiền Lương nằm ở bờ Bắc sông Bến Hải. Cột cờ và lá cờ Tổ quốc là những hình ảnh tiêu biểu gắn với ý chí thống nhất non sông.',
    script: 'Chào mừng bạn đến với Kỳ đài Hiền Lương, nơi hình ảnh lá cờ đỏ sao vàng lưu giữ nhiều ký ức lịch sử. Nhấn vào từng chủ đề bên dưới để tiếp tục nghe thuyết minh.',
    accent: '#e2b46b',
    image: '/home-reference-soldier.png',
    hotspot: {
      x: 74,
      y: 70,
    },
    exhibits: [
      {
        id: 'flag-1',
        name: 'Lá cờ Tổ quốc',
        type: 'Biểu tượng',
        content: 'Biểu tượng quốc gia gắn với câu chuyện về kỳ đài Hiền Lương và tinh thần hướng về thống nhất.',
        caption: 'Biểu tượng lịch sử',
      },
      {
        id: 'flag-2',
        name: 'Cấu trúc kỳ đài',
        type: 'Kiến trúc',
        content: 'Cần đối chiếu kích thước và các giai đoạn trùng tu theo hồ sơ quản lý di tích, không sử dụng số liệu chưa được xác minh.',
        caption: 'Công trình phục dựng',
      },
      {
        id: 'flag-3',
        name: 'Ký ức giới tuyến',
        type: 'Câu chuyện',
        content: 'Tìm hiểu ký ức của người dân hai bờ thông qua lời kể và tài liệu đã được cơ quan quản lý kiểm chứng.',
        caption: 'Ký ức lịch sử',
      },
    ],
  },
  {
    id: 'monument',
    title: 'Tượng đài Khát vọng thống nhất',
    short: 'Thông điệp về hòa bình và đoàn tụ',
    description: 'Tượng đài Khát vọng thống nhất thuộc không gian di tích ở bờ Nam sông Bến Hải, thể hiện ước vọng đoàn tụ của dân tộc trong những năm chia cắt.',
    script: 'Bạn đang đến với Tượng đài Khát vọng thống nhất. Công trình lưu giữ thông điệp về sự đoàn tụ, hòa bình và ý chí thống nhất của nhân dân Việt Nam.',
    accent: '#dcb87b',
    image: '/home-reference-soldier.png',
    hotspot: {
      x: 34.3,
      y: 10.8,
    },
    exhibits: [
      {
        id: 'monument-1',
        name: 'Tượng đài và quảng trường',
        type: 'Kiến trúc',
        content: 'Tổng quan kiến trúc và bố cục quảng trường tại bờ Nam. Dữ liệu về tác giả, kích thước và niên đại cần được đối chiếu hồ sơ di tích.',
        caption: 'Không gian tưởng niệm',
      },
      {
        id: 'monument-2',
        name: 'Khát vọng đoàn tụ',
        type: 'Chủ đề',
        content: 'Chủ đề lịch sử thể hiện mong muốn hòa bình và thống nhất của người dân hai miền.',
        caption: 'Giá trị tinh thần',
      },
      {
        id: 'monument-3',
        name: 'Ảnh khu di tích',
        type: 'Hình ảnh',
        content: 'Bộ sưu tập hình ảnh hiện tại và qua các thời kỳ sẽ được cập nhật trong hệ thống quản trị.',
        caption: 'Tư liệu hình ảnh',
      },
    ],
  },
  {
    id: 'union',
    title: 'Nhà liên hiệp',
    short: 'Khám phá khu vực Nhà liên hiệp',
    description: 'Khu vực Nhà liên hiệp được đánh dấu trên bản đồ tham quan.',
    script: '',
    accent: '#e8cb92',
    image: '/union-reference.png',
    hotspot: { x: 53.8, y: 49.6 },
    exhibits: [],
  },
];
