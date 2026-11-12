import type { ZoneId } from './data';
import type { Lang } from './i18n';

export type Narrator = {
  id: ZoneId | 'home';
  label: Record<Lang, string>;
  present: string;
  speaking: string;
  mouthX: string;
  mouthY: string;
  /** voice_id ElevenLabs (giọng premade) – hợp với giới tính nhân vật */
  voice: string;
};

// Giọng premade của ElevenLabs (dùng được với gói Free qua API): Sarah (nữ), George (nam).
export const VOICE_FEMALE = 'EXAVITQu4vr4xnSDxMaL';
export const VOICE_MALE = 'JBFqnCBsd6RMkjVDRZzb';

// Mọi nhân vật dùng chung tư thế giới thiệu và nhịp hoạt ảnh; chỉ khác hình và vị trí mặt nạ miệng.
const soldierGirl = { present: '/guides/flag-present.png', speaking: '/guides/flag-speaking.png', mouthX: '40.5%', mouthY: '32.5%', voice: VOICE_FEMALE };
const aoDai = { present: '/guides/museum-present.png', speaking: '/guides/museum-speaking.png', mouthX: '40.4%', mouthY: '31.5%', voice: VOICE_FEMALE };
const soldier = { present: '/soldier-guide-present.png', speaking: '/soldier-guide-speaking.png', mouthX: '40%', mouthY: '31.5%', voice: VOICE_MALE };

export const narrators: Record<ZoneId | 'home', Narrator> = {
  home: { id: 'home', label: { vi: 'Chú bộ đội hướng dẫn ảo', en: 'Virtual soldier guide', zh: '虚拟解放军讲解员' }, ...soldier },
  bridge: { id: 'bridge', label: { vi: 'Chú bộ đội hướng dẫn tại Cầu Hiền Lương', en: 'Soldier guide at Hien Luong Bridge', zh: '贤良桥解放军讲解员' }, ...soldier },
  museum: { id: 'museum', label: { vi: 'Nữ chiến sĩ hướng dẫn tại Nhà trưng bày Vĩ tuyến 17', en: 'Woman soldier guide at the 17th Parallel Exhibition Hall', zh: '十七度线展厅女战士讲解员' }, ...soldierGirl },
  flag: { id: 'flag', label: { vi: 'Nữ chiến sĩ hướng dẫn tại Kỳ đài Hiền Lương', en: 'Woman soldier guide at the Flag Tower', zh: '贤良旗台女战士讲解员' }, ...soldierGirl },
  union: { id: 'union', label: { vi: 'Hướng dẫn viên tại Nhà liên hợp', en: 'Guide at the Joint Commission House', zh: '联合委员会会所讲解员' }, ...aoDai },
  monument: {
    id: 'monument', label: { vi: 'Người thuyết minh tại Tượng đài Khát vọng thống nhất', en: 'Guide at the Reunification Monument', zh: '统一纪念碑讲解员' },
    present: '/guides/monument-present.png', speaking: '/guides/monument-speaking.png', mouthX: '39.6%', mouthY: '30.5%', voice: VOICE_MALE,
  },
};
