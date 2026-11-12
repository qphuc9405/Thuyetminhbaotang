import type { ZoneId } from './data';

export type Photo = {
  title: string;
  url: string;
  credit: string;
  source?: string;
};

export type Video = {
  title: string;
  publisher: string;
  url: string;
  description: string;
};

const localPhoto = (url: string, title: string, credit: string): Photo => ({
  url,
  title,
  credit,
});

const commons = (filename: string, title: string, credit: string): Photo => ({
  title,
  url: `https://commons.wikimedia.org/wiki/Special:FilePath/${encodeURIComponent(filename)}?width=1200`,
  source: `https://commons.wikimedia.org/wiki/File:${encodeURIComponent(filename)}`,
  credit: `${credit} · Wikimedia Commons · CC BY-SA 3.0`,
});

const bridge3d = localPhoto('/bridge-3d.png', 'Cầu Hiền Lương — cảnh 3D', 'Dựng 3D từ ảnh tham khảo của bạn');
const bridgeOriginal = localPhoto('/bridge-reference.png', 'Cầu Hiền Lương — ảnh tham khảo', 'Ảnh do bạn cung cấp');
const museum3d = localPhoto('/museum-3d.png', 'Nhà trưng bày Vĩ tuyến 17 — cảnh 3D', 'Dựng 3D từ ảnh tham khảo của bạn');
const museumOriginal = localPhoto('/museum-reference.png', 'Nhà trưng bày — ảnh tham khảo', 'Ảnh do bạn cung cấp');
const flag3d = localPhoto('/flag-3d.png', 'Kỳ đài Hiền Lương — cảnh 3D', 'Dựng 3D từ ảnh tham khảo của bạn');
const flagOriginal = localPhoto('/flag-reference.png', 'Kỳ đài — ảnh tham khảo', 'Ảnh do bạn cung cấp');
const monument3d = localPhoto('/monument-3d.png', 'Tượng đài Khát vọng thống nhất — cảnh 3D', 'Dựng 3D từ ảnh tham khảo của bạn');
const monumentOriginal = localPhoto('/monument-reference.png', 'Tượng đài — ảnh tham khảo', 'Ảnh do bạn cung cấp');
const unionOriginal = localPhoto('/union-reference.png', 'Nhà liên hợp — ảnh tham khảo', 'Ảnh do nhóm cung cấp');

export const mediaByZone: Record<ZoneId, { hero: Photo; photos: Photo[]; videos: Video[] }> = {
  union: {
    hero: unionOriginal,
    photos: [
      unionOriginal,
      localPhoto('/home-map-open-forecourt-sharp.png', 'Vị trí Nhà liên hợp trên bản đồ', 'Bản đồ minh họa khu di tích'),
    ],
    videos: [],
  },
  bridge: {
    hero: bridge3d,
    photos: [
      bridge3d,
      bridgeOriginal,
      commons('Cầu Hiền Lương (nhìn từ bờ Nam).JPG', 'Cầu Hiền Lương nhìn từ bờ Nam', 'Bút Chiến'),
    ],
    videos: [
      {
        title: 'Hạ giải, trùng tu di tích lịch sử cầu Hiền Lương',
        publisher: 'VOV1',
        url: 'https://vov1.vov.vn/multimedia/video/ha-giai-trung-tu-di-tich-lich-su-cau-hien-luong-quang-tri-115752.vov',
        description: 'Phóng sự về công tác bảo tồn cây cầu lịch sử.',
      },
      {
        title: 'Vĩ tuyến 17: Chiến tranh nhân dân — Tập 1',
        publisher: 'VTV',
        url: 'https://vtv.vn/video/phim-tai-lieu-vi-tuyen-17-chien-tranh-nhan-dan-tap-1-385091.htm',
        description: 'Phim tài liệu về vùng giới tuyến.',
      },
    ],
  },
  museum: {
    hero: museum3d,
    photos: [
      museum3d,
      museumOriginal,
      commons('Nhà trưng bày Vĩ tuyến 17.JPG', 'Nhà trưng bày Vĩ tuyến 17', 'LÊ TẤN LỘC'),
    ],
    videos: [
      {
        title: 'Vĩ tuyến 17: Chiến tranh nhân dân — Tập 1',
        publisher: 'VTV',
        url: 'https://vtv.vn/video/phim-tai-lieu-vi-tuyen-17-chien-tranh-nhan-dan-tap-1-385091.htm',
        description: 'Phim tài liệu về vùng giới tuyến và tư liệu lịch sử.',
      },
    ],
  },
  flag: {
    hero: flag3d,
    photos: [
      flag3d,
      flagOriginal,
      commons('Cột cờ cầu Hiền Lương, Vĩnh Linh, Quảng Trị.jpeg', 'Cột cờ Hiền Lương', 'Linhcandng'),
    ],
    videos: [
      {
        title: 'Cận cảnh lễ thượng cờ ở đôi bờ Hiền Lương – Bến Hải',
        publisher: 'Tuổi Trẻ',
        url: 'https://tuoitre.vn/video/video-can-canh-le-thuong-co-108m2-o-doi-bo-hien-luong-ben-hai-106454.htm',
        description: 'Video lễ thượng cờ tại kỳ đài Hiền Lương.',
      },
    ],
  },
  monument: {
    hero: monument3d,
    photos: [
      monument3d,
      monumentOriginal,
      commons('Tượng đài Khát vọng thống nhất non sông.JPG', 'Tượng đài Khát vọng thống nhất', 'Bút Chiến'),
    ],
    videos: [
      {
        title: 'Khát vọng thống nhất tại đôi bờ Hiền Lương – Bến Hải',
        publisher: 'VTV',
        url: 'https://vtv.vn/trong-nuoc/khat-vong-thong-nhat-tai-hien-sinh-dong-cuoc-chien-dau-o-hai-bo-hien-luong-ben-hai-20190430062153743.htm',
        description: 'Chương trình tái hiện ký ức và khát vọng thống nhất.',
      },
    ],
  },
};
