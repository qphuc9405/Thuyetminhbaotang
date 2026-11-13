import { describe, expect, it, vi } from 'vitest';
import { act, fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import App from '../App';
import NarrationBar from '../Narration';
import { getAudio, speak, stopAll } from '../audio';
import { tr, type Key } from '../i18n';
import { audios, speech } from './setup';

const cite = { source_id: 'SRC001', source_title: 'Đôi bờ giới tuyến (1954–1967)', source_type: 'BOOK', printed_page: 188, provision: null, verified_anchor: true };
const img = (id: string) => ({ image_id: id, title: `Ảnh ${id}`, title_en: `Photo ${id}`, title_zh: `照片 ${id}`, caption: null, kind: 'archive_photo', image_url: `/api/images/${id}/file`, thumb_url: `/api/images/${id}/file?size=thumb` });
const item = (id: string, vi: string, en: string, zh: string, x: number) => ({
  id, x, y: 50, zoom: 2, side: 'r', label: { vi, en, zh }, documented: true, citations: [cite], images: [img('IMG040')],
  paragraphs: { vi: ['Đoạn một.', 'Đoạn hai.', 'Đoạn ba.'], en: ['One.', 'Two.', 'Three.'], zh: ['一。', '二。', '三。'] },
});
const titem = (id: string, vi: string, en: string, zh: string, extra: Record<string, unknown> = {}) => ({
  id, label: { vi, en, zh }, citations: [cite], images: [img('IMG040')], room: [40, 50], scene: null, needs_source: false, needs_note: null, links: [], documented: true,
  paragraphs: { vi: [`${vi} – đoạn một.`, 'Đoạn hai.', 'Đoạn ba.'], en: ['One.', 'Two.', 'Three.'], zh: ['一。', '二。', '三。'] }, ...extra,
});
const topic = (no: number, vi: string, zh: string, items: ReturnType<typeof titem>[]) => ({
  id: `topic-${no}`, no, short: { vi, en: `T${no}`, zh }, title: { vi: `Tiêu đề ${vi}`, en: `Title ${no}`, zh: `标题${zh}` }, subtitle: { vi: 'Phụ đề', en: 'Sub', zh: '副标题' },
  room: [10 + no * 18, 30], focus: [10 + no * 18, 50, 1.5], scene: null, items, cover: null,
});
const HALL = {
  zone_id: 'museum', kind: 'exhibition', title: 'Nhà trưng bày Vĩ tuyến 17', groups: {}, n_exhibits: 1,
  hall: { background: '/museum-hall.webp', width: 1672, height: 736, greeting: { vi: '' }, note: { vi: '' }, items: [] },
  topics: {
    background: '/museum-room.webp', width: 1672, height: 725, note: '', needs_label: { vi: 'Cần bổ sung nguồn', en: 'Source needed', zh: '需补充来源' },
    intro: { id: 'khanh-tiet', label: { vi: 'Tượng Chủ tịch Hồ Chí Minh', en: 'Statue of President Ho Chi Minh', zh: '胡志明主席雕像' }, room: [52, 36], focus: [52, 40, 1.8],
      paragraphs: { vi: ['Giới thiệu một.', 'Giới thiệu hai.'], en: ['Intro.', 'Two.'], zh: ['介绍。', '二。'] }, citations: [cite], images: [img('IMG035')] },
    topics: [
      topic(1, 'Chia cắt', '分隔', [titem('hiep-dinh', 'Văn bản Hiệp định', 'Agreement text', '协定文本'),
        titem('thong-hanh', 'Giấy thông hành', 'Passes', '通行证', { needs_source: true, images: [], needs_note: { vi: 'Chưa có ảnh giấy thông hành.', en: 'No photo.', zh: '无照片。' } })]),
      topic(2, 'Lũy thép', '钢铁堡垒', [titem('dia-dao', 'Dụng cụ đào địa đạo', 'Tunnel tools', '挖地道工具'), titem('choi-loa', 'Cuộc chiến chọi loa', 'Loudspeaker contest', '斗喇叭')]),
      topic(3, 'Khát vọng thống nhất', '统一的渴望', [titem('choi-co', 'Chọi cờ', 'Flag contest', '斗旗')]),
      topic(4, 'Giải phóng – Hồi sinh', '解放与新生', [titem('sum-hop', 'Đôi bờ sum họp', 'Reunited', '团圆', { images: [], links: [{ source_id: 'WEB019', title: 'Bài', publisher: 'Báo Nhân Dân', url: 'https://example.org/a', access_status: 'read_full_article' }] })]),
    ],
    artifacts: [{ id: 'choi-loa', topic: 'topic-2', room: [86, 73], label: { vi: 'Loa phát thanh', en: 'Loudspeaker', zh: '广播喇叭' } }],
  },
};
const BRIDGE = {
  zone_id: 'bridge', kind: 'story', title: 'Cầu Hiền Lương', images: [img('IMG004')],
  events: [{ event_id: 'EV01', date_label: '1928', title: 'Xây cầu', summary: 'Tóm tắt', printed_page: 183, source_id: 'SRC001', source_title: 'Sách', title_i18n: { vi: 'Xây cầu', en: 'Bridge built', zh: '建桥' }, summary_i18n: { vi: 'Tóm tắt', en: 'Summary', zh: '摘要' } }],
  stories: [{ id: 'cau-hai-mau', period: '1958–1959', title: { vi: 'Cây cầu hai màu sơn', en: 'The two-coloured bridge', zh: '两色桥' }, teaser: { vi: '', en: '', zh: '' }, body: { vi: ['Thân bài.'], en: ['Body.'], zh: ['正文。'] }, citations: [cite], image_ids: ['IMG004'] }],
};
const CHAT = { answer: 'Câu trả lời có ảnh.', mode: 'llm', insufficient_evidence: false, sources: [{ label: 'S1', source_title: 'Sách', source_type: 'BOOK', printed_page: 114, provision: null }], images: [img('IMG041'), img('IMG042')] };

function mockFetch(opts: { tts?: 'ok' | 'down' } = {}) {
  return vi.spyOn(globalThis, 'fetch').mockImplementation(async (input: any, init?: any) => {
    const url = String(input);
    const json = (b: unknown, status = 200) => new Response(JSON.stringify(b), { status, headers: { 'Content-Type': 'application/json' } });
    if (url.endsWith('/api/zones/museum')) return json(HALL);
    if (url.endsWith('/api/zones/bridge')) return json(BRIDGE);
    if (url.endsWith('/api/chat')) return json(CHAT);
    if (url.endsWith('/api/narration/generate')) {
      return opts.tts === 'ok' ? json({ audio_url: '/api/narration/' + 'a'.repeat(40) }) : json({ error: { code: 'elevenlabs_key_missing' } }, 503);
    }
    if (init?.method === 'POST') return json({}, 404);
    return json({ items: [] });
  });
}

describe('i18n', () => {
  it('mọi chuỗi giao diện đều có đủ vi / en / zh (và tên các khu vực)', async () => {
    const { KEYS, ZONE_TEXT } = await import('../i18n');
    expect(KEYS.length).toBeGreaterThan(80);
    for (const k of KEYS) for (const l of ['en', 'zh'] as const) expect(tr(l, k).length, `${k}/${l}`).toBeGreaterThan(0);
    for (const k of KEYS.filter(k => k !== 'translationNote')) expect(tr('vi', k).length, k).toBeGreaterThan(0);
    for (const z of Object.values(ZONE_TEXT)) for (const l of ['vi', 'en', 'zh'] as const) { expect(z.title[l]).toBeTruthy(); expect(z.questions[l].length).toBe(2); }
    expect(tr('zh', 'askAbout', { x: '铜星' })).toContain('铜星');
  });
});

describe('bộ điều khiển âm thanh', () => {
  it('báo thiếu khóa và thử lại ngay khi ElevenLabs đã sẵn sàng', async () => {
    const fetchMock = mockFetch({ tts: 'down' });
    render(<NarrationBar id="retry" text="Kiểm tra kết nối giọng đọc." />);
    expect((await screen.findByRole('status')).textContent).toContain('Chưa cấu hình khóa ElevenLabs');
    expect(getAudio().ttsError).toBe('elevenlabs_key_missing');
    fetchMock.mockResolvedValue(new Response(JSON.stringify({ audio_url: '/api/narration/' + 'b'.repeat(40) }), { status: 200 }));
    fireEvent.click(screen.getByRole('button', { name: 'Thử lại ElevenLabs' }));
    await waitFor(() => expect(getAudio().engine).toBe('eleven'));
    expect(fetchMock).toHaveBeenCalledTimes(2);
    expect(getAudio().ttsError).toBeNull();
    expect(screen.queryByRole('status')).toBeNull();
    stopAll();
  });

  it('lỗi 503 tạm thời không ngăn lần kết nối tiếp theo', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch')
      .mockResolvedValueOnce(new Response(JSON.stringify({ error: { code: 'tts_timeout' } }), { status: 503 }))
      .mockResolvedValueOnce(new Response(JSON.stringify({ audio_url: '/api/narration/' + 'c'.repeat(40) }), { status: 200 }));
    await speak('timeout', 'Thử lại sau lỗi tạm thời.', 'vi');
    expect(getAudio().ttsError).toBe('tts_timeout');
    await speak('timeout', 'Thử lại sau lỗi tạm thời.', 'vi');
    expect(fetchMock).toHaveBeenCalledTimes(2);
    expect(getAudio().engine).toBe('eleven');
    stopAll();
  });

  it('không có khoá ElevenLabs → lùi về giọng trình duyệt đúng ngôn ngữ; stopAll() dừng hẳn', async () => {
    mockFetch({ tts: 'down' });
    await speak('k1', '你好', 'zh');
    expect(speech.speak).toHaveBeenCalledTimes(1);
    expect(speech.speak.mock.calls[0][0].lang).toBe('zh-CN');
    stopAll();
    expect(speech.cancel).toHaveBeenCalled();
    expect(getAudio().status).toBe('idle');
  });
  it('có ElevenLabs → phát tệp mp3 từ museum-guide; lời mới dừng lời cũ', async () => {
    mockFetch({ tts: 'ok' });
    await speak('a', 'xin chào', 'vi');
    expect(audios).toHaveLength(1);
    expect(audios[0].src).toMatch(/^\/mg\/api\/narration\/a{40}$/);
    expect(getAudio().engine).toBe('eleven');
    await speak('b', 'tạm biệt', 'vi');
    expect(audios[0].paused).toBe(true);
    expect(getAudio().key).toBe('b');
    stopAll();
    expect(audios[1].paused).toBe(true);
  });
});

describe('Nhà trưng bày theo 4 chủ đề', () => {
  it('phòng chính có 4 chủ đề; bấm chủ đề → phóng vào trang chủ đề; Esc về phòng thì tắt tiếng; về bản đồ cũng tắt tiếng', async () => {
    mockFetch();
    window.location.hash = '#museum';
    render(<App />);
    const pins = await screen.findAllByRole('button', { name: /^Chủ đề \d: / });
    expect(pins).toHaveLength(4);
    expect(screen.getByRole('navigation', { name: 'Hành trình tham quan' })).toBeTruthy();
    expect(screen.getByRole('img', { name: /Nữ chiến sĩ hướng dẫn/ })).toBeTruthy();
    fireEvent.click(pins[0]);
    const panel = await screen.findByRole('complementary', { name: 'Văn bản Hiệp định' }, { timeout: 3000 });
    expect(window.location.hash).toBe('#museum/topic-1');
    expect(within(panel).getByText('Văn bản Hiệp định – đoạn một.')).toBeTruthy();
    expect(within(panel).queryByText('Đoạn ba.')).toBeNull();
    fireEvent.click(within(panel).getByRole('button', { name: /Đọc tiếp/ }));
    expect(within(panel).getByText('Đoạn ba.')).toBeTruthy();
    // danh sách bên trái: hiện vật chưa có tư liệu gắn nhãn
    const list = screen.getByRole('navigation', { name: 'Hiện vật trong chủ đề' });
    const pass = within(list).getByRole('button', { name: /Giấy thông hành/ });
    expect(within(pass).getByText('Cần bổ sung nguồn')).toBeTruthy();
    fireEvent.click(pass);
    const p2 = await screen.findByRole('complementary', { name: 'Giấy thông hành' });
    expect(within(p2).getByText(/Chưa có ảnh giấy thông hành/)).toBeTruthy();
    expect(window.location.hash).toBe('#museum/topic-1/thong-hanh');
    expect(screen.getByRole('img', { name: /Nữ chiến sĩ hướng dẫn/ })).toBeTruthy();
    expect(screen.getByRole('textbox', { name: /Câu hỏi tra cứu/ })).toBeTruthy();
    speech.cancel.mockClear();
    fireEvent.keyDown(window, { key: 'Escape' });
    expect(speech.cancel).toHaveBeenCalled();
    expect(await screen.findAllByRole('button', { name: /^Chủ đề \d: / })).toHaveLength(4);
    speech.cancel.mockClear();
    fireEvent.click(screen.getByRole('button', { name: /Quay lại bản đồ/ }));
    expect(speech.cancel).toHaveBeenCalled();
    expect(getAudio().status).toBe('idle');
  });

  it('bấm hiện vật lớn trong phòng (loa) → mở đúng chủ đề và hiện vật; thanh hành trình chuyển chủ đề', async () => {
    mockFetch();
    window.location.hash = '#museum';
    render(<App />);
    fireEvent.click(await screen.findByRole('button', { name: 'Loa phát thanh' }));
    expect(await screen.findByRole('complementary', { name: 'Cuộc chiến chọi loa' }, { timeout: 3000 })).toBeTruthy();
    expect(window.location.hash).toBe('#museum/topic-2/choi-loa');
    const strip = screen.getByRole('navigation', { name: 'Hành trình tham quan' });
    expect(within(strip).getByRole('button', { name: /Lũy thép/ }).getAttribute('aria-current')).toBe('true');
    fireEvent.click(within(strip).getByRole('button', { name: /Giải phóng – Hồi sinh/ }));
    const p4 = await screen.findByRole('complementary', { name: 'Đôi bờ sum họp' });
    expect(within(p4).getByRole('link', { name: /Xem ảnh tại bài báo nguồn/ }).getAttribute('href')).toBe('https://example.org/a');
    fireEvent.click(within(screen.getByRole('navigation', { name: 'Hành trình tham quan' })).getByRole('button', { name: /Tượng Chủ tịch Hồ Chí Minh/ }));
    expect(await screen.findByRole('complementary', { name: 'Tượng Chủ tịch Hồ Chí Minh' })).toBeTruthy();
    expect(window.location.hash).toBe('#museum/gioi-thieu');
  });

  it('Back của trình duyệt trong nhà trưng bày: từ chủ đề về phòng, tắt tiếng', async () => {
    mockFetch();
    window.location.hash = '#museum/topic-3';
    render(<App />);
    expect(await screen.findByRole('complementary', { name: 'Chọi cờ' })).toBeTruthy();
    speech.cancel.mockClear();
    await act(async () => { window.history.pushState({}, '', '#museum'); window.dispatchEvent(new PopStateEvent('popstate')); });
    expect(speech.cancel).toHaveBeenCalled();
    expect(await screen.findAllByRole('button', { name: /^Chủ đề \d: / })).toHaveLength(4);
  });

  it('đổi sang tiếng Trung: chủ đề, nhãn, ô chat và nút đều đổi theo', async () => {
    mockFetch();
    window.location.hash = '#museum';
    render(<App />);
    await screen.findAllByRole('button', { name: /^Chủ đề \d: / });
    fireEvent.click(screen.getByRole('button', { name: /Ngôn ngữ/ }));
    fireEvent.click(screen.getByRole('menuitemradio', { name: /中文/ }));
    expect(await screen.findAllByRole('button', { name: /^主题\d: / })).toHaveLength(4);
    expect(screen.getByRole('button', { name: '广播喇叭' })).toBeTruthy();
    expect(screen.getByPlaceholderText('询问关于十七度线展厅…')).toBeTruthy();
    expect(screen.getByRole('button', { name: /返回地图/ })).toBeTruthy();
    expect(localStorage.getItem('tm-lang')).toBe('zh');
  });

  it('chat trả lời có ảnh: hiện ảnh rõ, bấm để xem lớn, Esc để đóng', async () => {
    mockFetch();
    window.location.hash = '#museum';
    render(<App />);
    await screen.findAllByRole('button', { name: /^Chủ đề \d: / });
    const input = screen.getByRole('textbox', { name: /Câu hỏi tra cứu/ });
    fireEvent.change(input, { target: { value: 'Đấu loa?' } });
    fireEvent.click(screen.getByRole('button', { name: 'Gửi câu hỏi' }));
    expect(await screen.findByText('Câu trả lời có ảnh.')).toBeTruthy();
    const thumbs = screen.getAllByRole('button', { name: /Xem lớn: Ảnh IMG04/ });
    expect(thumbs).toHaveLength(2);
    fireEvent.click(thumbs[1]);
    const dlg = await screen.findByRole('dialog', { name: 'Ảnh IMG042' });
    expect(within(dlg).getByText('2 / 2')).toBeTruthy();
    fireEvent.keyDown(window, { key: 'Escape' });
    await waitFor(() => expect(screen.queryByRole('dialog')).toBeNull());
  });
});

describe('Các khu khác', () => {
  it('khu Cầu có người hướng dẫn, thanh chat và câu chuyện theo ngôn ngữ', async () => {
    mockFetch();
    localStorage.setItem('tm-lang', 'en');
    window.location.hash = '#bridge';
    render(<App />);
    expect(await screen.findByRole('heading', { name: 'The two-coloured bridge' })).toBeTruthy();
    expect(screen.getByRole('img', { name: /Soldier guide at Hien Luong Bridge/ })).toBeTruthy();
    expect(screen.getByPlaceholderText('Ask about Hien Luong Bridge…')).toBeTruthy();
    speech.cancel.mockClear();
    await act(async () => { window.history.pushState({}, '', '/'); window.dispatchEvent(new PopStateEvent('popstate')); });
    expect(speech.cancel).toHaveBeenCalled(); // Back của trình duyệt cũng tắt tiếng
  });
});
