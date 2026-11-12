import { fireEvent, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Route, Routes } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import App from '../App'
import AudioPlayer from '../components/AudioPlayer'
import { splitCitations, pageLabel } from '../lib/citations'
import { CHAT_RESP, IMG, mockFetch, renderApp } from './helpers'
import ImageDetailPage from '../pages/ImageDetail'
import Stories from '../pages/Stories'

const HEALTH = { status: 'ok', llm: { configured: true, model: 'gpt-oss:120b' }, tts: { configured: false, model: 'eleven_flash_v2_5' }, retrieval: { backend: 'hybrid', image_retrieval: 'metadata-based' }, database: { chunks: 604 } }

beforeEach(() => { vi.restoreAllMocks(); vi.unstubAllGlobals(); try { sessionStorage.clear(); localStorage.clear() } catch { /* */ } })

describe('citations util', () => {
  it('splits text and labels', () => {
    expect(splitCitations('A [S1] b [I2][S3].')).toEqual([{ type: 'text', text: 'A ' }, { type: 'cite', label: 'S1' }, { type: 'text', text: ' b ' }, { type: 'cite', label: 'I2' }, { type: 'cite', label: 'S3' }, { type: 'text', text: '.' }])
    expect(splitCitations('không có')).toHaveLength(1)
  })
  it('page label', () => {
    expect(pageLabel({ printed_page: 5, printed_page_end: 7, provision: null }, 'tr.')).toBe('tr.5–7')
    expect(pageLabel({ printed_page: null, printed_page_end: null, provision: 'Chương I, Điều 1' }, 'tr.')).toBe('Chương I, Điều 1')
  })
})

const STORY = { hero: { image_id: 'IMG034', image_url: '/api/images/IMG034/file', title: 'Cầu', note: '' }, chapters: ['ch1', 'ch2', 'ch3', 'ch4'].map((id, i) => ({
  id, period: '1954', image_id: 'BKFIG02', topic_id: 'geneva', timeline_period: '1954-1956',
  title: { vi: `Chương VI ${i}`, en: `Chapter EN ${i}`, zh: `章 ${i}` }, lead: { vi: 'Dẫn', en: 'Lead', zh: '引' }, body: { vi: ['Đoạn một.'], en: ['Para one.'], zh: ['第一段。'] },
  citations: [{ source_id: 'SRC001', source_title: 'Đôi bờ', source_type: 'BOOK', printed_page: 15 + i, provision: null, verified_anchor: true }],
  image: { image_id: 'BKFIG02', title: 'Hội nghị', title_en: 'Conference', title_zh: '会议', caption: null, image_url: '/x', medium_url: '/x?m', kind: 'book_figure', printed_page: 19 } })) }
const EV = (id: string, date: string, period: string, rel = 'illustrates_topic') => ({ event_id: id, date_iso: date, date_label: date, title_vi: 'Sự kiện ' + id, title_en: 'Event ' + id, title_zh: '事件 ' + id,
  summary_vi: 'Tóm tắt ' + id, summary_en: 'Summary ' + id, period, source_id: 'SRC001', source_title: 'Đôi bờ giới tuyến', source_type: 'BOOK', printed_page: 188, provision: null, evidence_snippet: 'bằng chứng',
  verification_status: 'anchor_verified_in_ocr', topic_ids: ['bridgeflag'], images: [{ image_id: 'IMG015', thumb_url: '/t', medium_url: '/m', relation: rel, basis: '' }] })
const HOME_ROUTES = { '/api/story': STORY, '/api/timeline': { items: [EV('E1', '1954-10-08', '1954-1956'), EV('E2', '1959-01-16', '1956-1967', 'illustrates')], note: '' }, '/api/images': { total: 1, items: [IMG('IMG004')] } }

describe('UI-01/02 home storytelling / UI-09 language', () => {
  it('renders hero, four cited chapters, timeline rail, collection, guide; switches language', async () => {
    mockFetch(HOME_ROUTES)
    renderApp(<App />)
    expect(screen.getByRole('heading', { level: 1, name: 'Cầu Hiền Lương' })).toBeInTheDocument()
    expect(screen.getByText('Dòng sông chia cắt – Khát vọng nối liền')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /Bắt đầu hành trình/ })).toHaveAttribute('href', '#story')
    const chapters = await screen.findAllByTestId('story-chapter')
    expect(chapters).toHaveLength(4)
    expect(within(chapters[0]).getByText(/Sách tr\.15/)).toBeInTheDocument()
    expect(within(chapters[0]).getByRole('link', { name: 'Hỏi hướng dẫn viên' })).toHaveAttribute('href', expect.stringContaining('/chat?q='))
    expect(await screen.findByTestId('timeline-rail')).toBeInTheDocument()
    expect(await screen.findByTestId('collection-grid')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Hãy để câu chuyện lịch sử được tiếp tục' })).toBeInTheDocument()
    await userEvent.click(screen.getAllByRole('button', { name: 'EN' })[0])
    expect(await screen.findByRole('heading', { level: 1, name: 'Hiền Lương Bridge' })).toBeInTheDocument()
    expect(screen.getByText('Chapter EN 0')).toBeInTheDocument()
    await userEvent.click(screen.getAllByRole('button', { name: '中文' })[0])
    expect(await screen.findByRole('heading', { level: 1, name: '贤良桥' })).toBeInTheDocument()
    expect(document.documentElement.lang).toBe('zh')
  })

  it('UI-04 timeline rail opens event narration with honest image label and prev/next', async () => {
    mockFetch(HOME_ROUTES)
    renderApp(<App />)
    const rail = await screen.findByTestId('timeline-rail')
    await userEvent.click(within(rail).getByText('Sự kiện E1'))
    const dlg = await screen.findByRole('dialog')
    expect(within(dlg).getByText(/Ảnh minh hoạ theo chủ đề – không phải ảnh chụp tại sự kiện/)).toBeInTheDocument()
    expect(within(dlg).getByText(/tr\.188/)).toBeInTheDocument()
    expect(within(dlg).getByRole('button', { name: /Mốc trước/ })).toBeDisabled()
    await userEvent.click(within(dlg).getByRole('button', { name: /Mốc tiếp theo/ }))
    expect(within(screen.getByRole('dialog')).getByText('Sự kiện E2')).toBeInTheDocument()
    expect(within(screen.getByRole('dialog')).getByText(/Hình trong sách gắn với sự kiện/)).toBeInTheDocument()
    await userEvent.keyboard('{Escape}')
    await waitFor(() => expect(screen.queryByRole('dialog')).toBeNull())
  })

  it('UI-08 long answer renders as paragraphs with bold and citation links', async () => {
    const long = { ...CHAT_RESP, answer: 'Mở đầu câu chuyện năm **1954** [S1].\n\nĐoạn thứ hai kể tiếp diễn biến [S1][S9].\n\n### Ý nghĩa\n\nĐoạn kết.' }
    mockFetch({ '/api/chat': { body: long } })
    renderApp(<App />, { route: '/chat' })
    await userEvent.type(screen.getByLabelText('Hỏi đáp AI'), 'Kể chuyện')
    await userEvent.click(screen.getByRole('button', { name: 'Gửi' }))
    const ra = await screen.findByTestId('rich-answer')
    expect(ra.querySelectorAll('p')).toHaveLength(3)
    expect(within(ra).getByText('1954').tagName).toBe('STRONG')
    expect(within(ra).getByRole('heading', { name: 'Ý nghĩa' })).toBeInTheDocument()
    expect(within(ra).getAllByText('[S1]')[0].closest('a')).toHaveAttribute('href', expect.stringMatching(/#src-\d+-S1/))
    expect(within(ra).queryByText('[S9]')).toBeNull()  // nhãn không có trong nguồn không hiển thị
  })

  it('chat sidebar shows themed questions from the archive', async () => {
    mockFetch({ '/api/chat': { body: CHAT_RESP } })
    renderApp(<App />, { route: '/chat' })
    expect(screen.getByRole('heading', { level: 1, name: 'Hướng dẫn viên AI của bảo tàng' })).toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: 'Vì sao cầu Hiền Lương có hai màu?' }))
    expect(await screen.findByTestId('assistant-message')).toBeInTheDocument()
  })
})

describe('UI-02/03/05 chat', () => {
  it('sends a question, shows answer, citation, page, images', async () => {
    const m = mockFetch({ '/api/chat': { body: CHAT_RESP } })
    renderApp(<App />, { route: '/chat' })
    await userEvent.type(screen.getByLabelText('Hỏi đáp AI'), 'Cột cờ đầu tiên cao bao nhiêu?')
    await userEvent.click(screen.getByRole('button', { name: 'Gửi' }))
    const msg = await screen.findByTestId('assistant-message')
    expect(within(msg).getAllByText(/Cột cờ đầu tiên cao 12 m/).length).toBeGreaterThanOrEqual(1)
    expect(within(msg).getAllByText('[S1]').length).toBeGreaterThanOrEqual(2)  // nhãn trong câu + nhãn trong danh sách nguồn
    expect(within(msg).getByTestId('page-tag')).toHaveTextContent('tr.188')
    expect(within(msg).getByText(/trang PDF 94/)).toBeInTheDocument()
    expect(within(msg).getByAltText('Toàn cảnh cầu')).toHaveAttribute('src', '/api/images/IMG004/file?size=thumb')
    const body = JSON.parse(String(m.calls[0].init?.body))
    expect(body.message).toContain('Cột cờ')
    expect(body.language).toBe('vi')
    expect(body.session_id).toMatch(/^s[a-z0-9]+$/)
  })

  it('UI-08 backend error shows message and retry works', async () => {
    let n = 0
    mockFetch({ '/api/chat': () => (++n === 1 ? { status: 503, body: { error: { code: 'llm_unavailable', message: 'Dịch vụ mô hình AI tạm thời không khả dụng.' } } } : { body: CHAT_RESP }) })
    renderApp(<App />, { route: '/chat' })
    await userEvent.type(screen.getByLabelText('Hỏi đáp AI'), 'xin chào')
    await userEvent.click(screen.getByRole('button', { name: 'Gửi' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('Dịch vụ mô hình AI tạm thời không khả dụng.')
    await userEvent.click(screen.getByRole('button', { name: 'Thử lại' }))
    expect(await screen.findByTestId('assistant-message')).toBeInTheDocument()
  })

  it('network failure is reported', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => { throw new TypeError('failed') }))
    renderApp(<App />, { route: '/chat' })
    await userEvent.type(screen.getByLabelText('Hỏi đáp AI'), 'xin chào')
    await userEvent.click(screen.getByRole('button', { name: 'Gửi' }))
    expect(await screen.findByRole('alert')).toHaveTextContent(/Không kết nối được máy chủ/)
  })

  it('insufficient evidence is flagged and shows no images/audio', async () => {
    mockFetch({ '/api/chat': { body: { ...CHAT_RESP, answer: 'Xin lỗi, chưa đủ căn cứ.', sources: [], insufficient_evidence: true, mode: 'abstain', confidence: 'low' } } })
    renderApp(<App />, { route: '/chat' })
    await userEvent.type(screen.getByLabelText('Hỏi đáp AI'), 'ngoài phạm vi')
    await userEvent.click(screen.getByRole('button', { name: 'Gửi' }))
    const msg = await screen.findByTestId('assistant-message')
    expect(within(msg).getByText('Chưa đủ bằng chứng trong kho tư liệu')).toBeInTheDocument()
    expect(within(msg).queryByTestId('audio-player')).toBeNull()
    expect(within(msg).queryByAltText('Toàn cảnh cầu')).toBeNull()
  })

  it('prefill from ?q and example click', async () => {
    mockFetch({ '/api/chat': { body: CHAT_RESP } })
    renderApp(<App />, { route: '/chat?q=Vụ%20tống%20triệt' })
    expect(screen.getByLabelText('Hỏi đáp AI')).toHaveValue('Vụ tống triệt')
  })

  it('sends selected answer language', async () => {
    const m = mockFetch({ '/api/chat': { body: CHAT_RESP } })
    renderApp(<App />, { route: '/chat' })
    await userEvent.click(screen.getAllByRole('button', { name: 'EN' })[0])
    await userEvent.type(screen.getByRole('textbox'), 'Why?')
    await userEvent.click(screen.getByRole('button', { name: 'Send' }))
    await screen.findByTestId('assistant-message')
    expect(JSON.parse(String(m.calls[0].init?.body)).language).toBe('en')
  })
})

describe('UI-07 audio', () => {
  it('generates audio then plays, pauses, stops and replays', async () => {
    const m = mockFetch({ '/api/narration/generate': { body: { audio_id: 'a'.repeat(40), status: 'ready', audio_url: '/api/narration/' + 'a'.repeat(40), cached: false, segments: 1, language: 'vi' } } })
    const play = vi.spyOn(HTMLMediaElement.prototype, 'play').mockResolvedValue(undefined)
    const pause = vi.spyOn(HTMLMediaElement.prototype, 'pause').mockImplementation(() => undefined)
    renderApp(<AudioPlayer text="Cột cờ cao 12 m [S1]." language="vi" />)
    expect(screen.getByRole('button', { name: 'Phát' })).toBeEnabled()
    expect(screen.getByRole('button', { name: 'Dừng' })).toBeDisabled()
    await userEvent.click(screen.getByRole('button', { name: 'Phát' }))
    await waitFor(() => expect(play).toHaveBeenCalled())
    expect(JSON.parse(String(m.calls[0].init?.body)).text).toBe('Cột cờ cao 12 m [S1].')
    expect(document.querySelector('audio')?.getAttribute('src')).toBe('/api/narration/' + 'a'.repeat(40))
    fireEvent.play(document.querySelector('audio')!)
    await userEvent.click(await screen.findByRole('button', { name: 'Tạm dừng' }))
    expect(pause).toHaveBeenCalled()
    await userEvent.click(screen.getByRole('button', { name: 'Dừng' }))
    await userEvent.click(screen.getByRole('button', { name: 'Phát lại' }))
    expect(play.mock.calls.length).toBeGreaterThanOrEqual(2)
    expect(screen.getByText(/Cột cờ cao 12 m \./)).toBeInTheDocument() // văn bản tương ứng, không có nhãn [S1]
  })

  it('TTS failure shows message and does not throw', async () => {
    mockFetch({ '/api/narration/generate': { status: 503, body: { error: { code: 'tts_quota_exceeded', message: 'Đã hết hạn mức ký tự (quota) ElevenLabs.' } } } })
    renderApp(<AudioPlayer text="abc" language="vi" />)
    await userEvent.click(screen.getByRole('button', { name: 'Phát' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('Đã hết hạn mức ký tự')
    expect(screen.getByRole('button', { name: 'Phát' })).toBeEnabled()
  })
})

describe('UI-10 gallery / UI-04 detail / UI-11 timeline / UI-12 topic', () => {
  it('gallery lists, filters via API params, shows empty state', async () => {
    const m = mockFetch({
      '/api/topics': { items: [{ topic_id: 'bridge', title_vi: 'Cầu', title_en: 'Bridge', title_zh: '桥', description_vi: '', printed_start: 1, printed_end: 2 }] },
      '/api/images': (url: string) => (url.includes('q=zzz') ? { body: { total: 0, items: [] } } : { body: { total: 2, items: [IMG('IMG001'), IMG('IMG002', { duplicate_group: 'DUP-A' })] } }),
    })
    renderApp(<App />, { route: '/gallery' })
    expect(await screen.findByText('2 ảnh')).toBeInTheDocument()
    expect(screen.getByAltText('Ảnh IMG002')).toBeInTheDocument(); expect(screen.getByText(/DUP-A/)).toBeInTheDocument()
    await userEvent.click(screen.getByRole('checkbox', { name: /Ẩn bản trùng/ }))
    await waitFor(() => expect(m.calls.some((c) => c.url.includes('hide_variants=true'))).toBe(true))
    await userEvent.type(screen.getByPlaceholderText(/Tìm trong mô tả/), 'zzz')
    expect(await screen.findByText('Không có ảnh khớp bộ lọc.')).toBeInTheDocument()
  })

  it('opens lightbox on click', async () => {
    mockFetch({ '/api/topics': { items: [] }, '/api/images': { total: 1, items: [IMG('IMG001')] } })
    renderApp(<App />, { route: '/gallery' })
    await userEvent.click(await screen.findByRole('button', { name: /Xem lớn: Ảnh IMG001/ }))
    const dlg = await screen.findByRole('dialog')
    expect(within(dlg).getByRole('img')).toHaveAttribute('src', '/api/images/IMG001/file')
    await userEvent.keyboard('{Escape}')
    await waitFor(() => expect(screen.queryByRole('dialog')).toBeNull())
  })

  it('image detail shows metadata with "Chưa xác định" and link types', async () => {
    mockFetch({ '/api/images/IMG007': { body: { ...IMG('IMG007', { duplicate_group: 'DUP-B' }), visual_description: 'Băng-rôn lớn căng ngang.', historical_context: 'Theo sách tr.81…', people_description: 'Một người mặc cảnh phục; không xác định danh tính.',
      historical_significance: 'Chưa xác định.', related_events: [], related_book_pages: [{ start: 81, end: 81, link_type: 'direct_match_book_figure' }, { start: 183, end: 186, link_type: 'topic_corroborated' }],
      verification_notes: 'SIFT 300 inliers', watermarks: ["Watermark 'LIFE'"], rights_status: 'Chưa xác định', visible_text: ['12T'], related_images: [{ image_id: 'IMG032', relation: 'variant_of_same_photograph', basis: '', confidence: 'high' }],
      related_passages: [{ chunk_id: 'X', printed_page: 81, printed_page_end: 82, chapter: 'Chương 6', excerpt: 'Trước tình hình đó', link_type: 'direct_match_book_figure' }], topics_detail: [{ topic_id: 'bridge', title_vi: 'Cầu', title_en: 'Bridge', title_zh: '桥' }], related_events_detail: [], sha256: 'x', phash: 'y' } } })
    renderApp(<Routes><Route path="/gallery/:id" element={<ImageDetailPage />} /></Routes>, { route: '/gallery/IMG007' })
    expect(await screen.findByRole('heading', { level: 1, name: 'Ảnh IMG007' })).toBeInTheDocument()
    expect(screen.getByText('Băng-rôn lớn căng ngang.')).toBeInTheDocument()
    expect(screen.getAllByText(/Chưa xác định/).length).toBeGreaterThanOrEqual(2)
    expect(screen.getByText('trùng hình in trong sách')).toBeInTheDocument()
    expect(screen.getByText('liên kết theo chủ đề (không chứng minh cùng thời điểm)')).toBeInTheDocument()
    expect(screen.getByText('12T')).toBeInTheDocument(); expect(screen.getByText(/Watermark 'LIFE'/)).toBeInTheDocument()
  })

  it('supplement image shows filename-based title and article caption passage', async () => {
    mockFetch({ '/api/images/IMG043': { body: { ...IMG('IMG043', { kind: 'archive_photo', source: 'Archive_4.zip' }), filename_title: 'O Nhạn - phát thanh viên chính', visual_description: 'Hai phụ nữ trẻ bên micro.',
      historical_context: '', people_description: 'Danh tính CHỈ theo tên file', historical_significance: 'Chưa xác định.', related_events: [], related_book_pages: [], verification_notes: '', watermarks: [], rights_status: 'Chưa xác định',
      related_images: [], related_passages: [{ chunk_id: 'SRC003-L062', source_id: 'SRC003', source_title: 'Về lịch sử cầu Hiền Lương', source_type: 'SECONDARY_ARTICLE', provision: 'dòng 62–65', relation: 'captioned_in_document', printed_page: null, printed_page_end: null, chapter: null, excerpt: '[Chú thích ảnh trong bài: O Nhạn…]', link_type: 'document_caption' }],
      topics_detail: [], related_events_detail: [], sha256: 'x', phash: 'y' } } })
    renderApp(<Routes><Route path="/gallery/:id" element={<ImageDetailPage />} /></Routes>, { route: '/gallery/IMG043' })
    expect(await screen.findByText('O Nhạn - phát thanh viên chính')).toBeInTheDocument()
    expect(screen.getByText('Mô tả ban đầu đi kèm ảnh')).toBeInTheDocument()
    expect(screen.getByText('Chưa xác minh.')).toBeInTheDocument()
    expect(screen.getByText('SRC003 · dòng 62–65')).toBeInTheDocument()
    expect(screen.getByText('chú thích ảnh trong bài viết')).toBeInTheDocument()
  })

  it('chat sources label articles and curator notes', async () => {
    const { default: Sources } = await import('../components/Sources')
    const base = CHAT_RESP.sources[0]
    renderApp(<Sources idPrefix="m" sources={[{ ...base, label: 'S2', source_id: 'SRC003', source_type: 'SECONDARY_ARTICLE', chunk_id: 'SRC003-L083', printed_page: null, printed_page_end: null, pdf_page: null, pdf_page_end: null, provision: 'dòng 83', chapter: null },
      { ...base, label: 'S3', source_id: 'NOTE01', source_type: 'CURATOR_NOTE', chunk_id: 'NOTE-01', printed_page: null, printed_page_end: null, pdf_page: null, pdf_page_end: null, provision: 'ghi chú đối chiếu', chapter: null }]} />)
    expect(screen.getByText('Bài viết (thứ cấp)')).toBeInTheDocument()
    expect(screen.getByText('Ghi chú đối chiếu nguồn')).toBeInTheDocument()
    expect(screen.getByText('dòng 83')).toBeInTheDocument()
  })

  it('stories page renders anecdotes with sources, conflict notes and ask link', async () => {
    const A = { id: 'loa-500w', period: '1960 – nay', topic_id: 'broadcast', image_ids: ['IMG046'], notes: ['NOTE-09'],
      title: { vi: 'Chiếc loa 500W giờ ở đâu?', en: 'Where is the 500 W loudspeaker?', zh: '喇叭在哪里？' }, teaser: { vi: 'Bốn nguồn, bốn địa chỉ.', en: 'Four sources.', zh: '四个来源。' },
      body: { vi: ['Đoạn một.'], en: ['Para one.'], zh: ['第一段。'] },
      citations: [{ source_id: 'SRC001', source_title: 'Đôi bờ', source_type: 'BOOK', printed_page: 116, provision: null, verified_anchor: true },
        { source_id: 'SRC003', source_title: 'Về lịch sử cầu', source_type: 'SECONDARY_ARTICLE', printed_page: null, provision: 'dòng 58', verified_anchor: true },
        { source_id: 'WEB002', source_title: 'Tiếng nói', source_type: 'WEB_ARTICLE', printed_page: null, provision: 'Báo Thanh tra, 2025-06-20', url: 'https://thanhtra.com.vn/x', verified_anchor: null }],
      images: [{ ...IMG('IMG046'), medium_url: '/api/images/IMG046/file?size=medium' }], notes_detail: [{ chunk_id: 'NOTE-09', title: 'Đối chiếu nguồn: nơi lưu giữ chiếc loa 500W hiện nay' }] }
    mockFetch({ '/api/anecdotes': { body: { items: [A], note: '' } } })
    renderApp(<Routes><Route path="/stories" element={<Stories />} /></Routes>, { route: '/stories' })
    expect(await screen.findByRole('heading', { level: 2, name: 'Chiếc loa 500W giờ ở đâu?' })).toBeInTheDocument()
    const src = screen.getByTestId('anecdote-sources')
    expect(src).toHaveTextContent('Sách tr.116'); expect(src).toHaveTextContent('SRC003 · dòng 58')
    expect(within(src).getByRole('link', { name: 'Báo Thanh tra, 2025-06-20' })).toHaveAttribute('href', 'https://thanhtra.com.vn/x')
    expect(screen.getByText(/nơi lưu giữ chiếc loa 500W hiện nay/)).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Hỏi hướng dẫn viên về chuyện này' })).toHaveAttribute('href', `/chat?q=${encodeURIComponent('Chiếc loa 500W giờ ở đâu?')}`)
  })

  it('image detail 404 shows error + back link', async () => {
    mockFetch({ '/api/images/NOPE': { status: 404, body: { detail: 'Không tìm thấy ảnh' } } })
    renderApp(<Routes><Route path="/gallery/:id" element={<ImageDetailPage />} /></Routes>, { route: '/gallery/NOPE' })
    expect(await screen.findByRole('alert')).toHaveTextContent('Không tìm thấy ảnh')
    expect(screen.getByRole('link', { name: /Quay lại thư viện/ })).toBeInTheDocument()
  })

  it('timeline filters by period and shows sources', async () => {
    const ev = (id: string, p: string) => ({ event_id: id, date_iso: '1965-03-19', date_label: '19/3/1965', title_vi: 'Vụ tống triệt', title_en: 'Expulsion', title_zh: '驱逐', summary_vi: 'Tóm tắt', summary_en: 'Summary', period: p, source_id: 'SRC001', source_title: 'Đôi bờ giới tuyến', source_type: 'BOOK',
      printed_page: 194, provision: null, evidence_snippet: 'ngày 19-3-1965', verification_status: 'anchor_verified_in_ocr', topic_ids: [], images: [] })
    const m = mockFetch({ '/api/timeline': (url: string) => ({ body: { items: [ev('E1', url.includes('1954-1956') ? '1954-1956' : '1956-1967')], note: '' } }) })
    renderApp(<App />, { route: '/timeline' })
    expect(await screen.findByText('Vụ tống triệt')).toBeInTheDocument()
    expect(screen.getByText(/Đôi bờ giới tuyến — tr\.194/)).toBeInTheDocument()
    await userEvent.click(screen.getByRole('tab', { name: '1954–1956' }))
    await waitFor(() => expect(m.calls.some((c) => c.url.includes('period=1954-1956'))).toBe(true))
    expect(screen.getByRole('link', { name: 'Hỏi chatbot' })).toHaveAttribute('href', expect.stringContaining('/chat?q='))
  })

  it('topic list and detail render content', async () => {
    mockFetch({
      '/api/topics/bridgeflag': { body: { topic_id: 'bridgeflag', title_vi: 'Cầu và cột cờ', title_en: 'Bridge and flagpoles', title_zh: '桥与旗杆', description_vi: 'Lịch sử cây cầu.', printed_start: 183, printed_end: 193,
        chapters: [{ chapter_id: 'C11', title_vi: 'Cầu và cột cờ Hiền Lương', title_en: 'The bridge', title_zh: '桥', printed_start: 183, printed_end: 193, period_scope: '1928–2005' }], events: [], images: [IMG('IMG004')], passages: [{ chunk_id: 'c1', content: 'Cầu Hiền Lương nằm ở Km735', printed_page: 183, printed_page_end: 183, chapter: 'C11' }], n_passages_total: 40 } },
      '/api/topics': { items: [{ topic_id: 'bridgeflag', title_vi: 'Cầu và cột cờ', title_en: 'Bridge and flagpoles', title_zh: '桥与旗杆', description_vi: 'Lịch sử cây cầu.', printed_start: 183, printed_end: 193, n_events: 20, n_images: 30 }] },
    })
    renderApp(<App />, { route: '/topics' })
    await userEvent.click(await screen.findByRole('link', { name: /Cầu và cột cờ/ }))
    expect(await screen.findByText('Cầu Hiền Lương nằm ở Km735')).toBeInTheDocument()
    expect(screen.getByText('Cầu và cột cờ Hiền Lương')).toBeInTheDocument()
  })

  it('settings persists voice id sanitised', async () => {
    mockFetch({ '/api/health': HEALTH })
    renderApp(<App />, { route: '/settings' })
    const box = await screen.findByRole('textbox')
    await userEvent.type(box, 'AbC<>123')
    expect(box).toHaveValue('AbC123')
    expect(localStorage.getItem('voice_id')).toBe('AbC123')
  })
})

describe('gallery topic chips', () => {
  it('filters by topic chip via API', async () => {
    const m = mockFetch({ '/api/images': { total: 1, items: [IMG('IMG015')] } })
    renderApp(<App />, { route: '/gallery' })
    await screen.findByAltText('Ảnh IMG015')
    await userEvent.click(screen.getByRole('button', { name: 'Cột cờ' }))
    await waitFor(() => expect(m.calls.some((c) => c.url.includes('topic=flagpoles'))).toBe(true))
  })
})
