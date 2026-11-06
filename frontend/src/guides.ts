import type { ZoneId } from './data';

export type Narrator = {
  id: ZoneId;
  label: string;
  present: string;
  speaking: string;
  mouthX: string;
  mouthY: string;
};

// Every character uses the same presentation pose and animation timings.
// Only the artwork and the mouth-mask position vary with the character.
export const narrators: Record<ZoneId, Narrator> = {
  union: {
    id: 'union', label: 'Hướng dẫn viên tại Nhà liên hiệp',
    present: '/guides/museum-present.png', speaking: '/guides/museum-speaking.png',
    mouthX: '40.4%', mouthY: '31.5%',
  },
  bridge: {
    id: 'bridge', label: 'Chú bộ đội hướng dẫn tại Cầu Hiền Lương',
    present: '/soldier-guide-present.png', speaking: '/soldier-guide-speaking.png',
    mouthX: '40%', mouthY: '31.5%',
  },
  museum: {
    id: 'museum', label: 'Nữ hướng dẫn viên Nhà trưng bày Vĩ tuyến 17',
    present: '/guides/museum-present.png', speaking: '/guides/museum-speaking.png',
    mouthX: '40.4%', mouthY: '31.5%',
  },
  flag: {
    id: 'flag', label: 'Nữ chiến sĩ hướng dẫn tại Kỳ đài Hiền Lương',
    present: '/guides/flag-present.png', speaking: '/guides/flag-speaking.png',
    mouthX: '40.5%', mouthY: '32.5%',
  },
  monument: {
    id: 'monument', label: 'Người thuyết minh tại Tượng đài Khát vọng thống nhất',
    present: '/guides/monument-present.png', speaking: '/guides/monument-speaking.png',
    mouthX: '39.6%', mouthY: '30.5%',
  },
};
