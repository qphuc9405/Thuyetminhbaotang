import { render } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import type { ReactElement } from 'react'
import { I18nProvider } from '../i18n'
import { SettingsProvider } from '../lib/settings'
import type { Lang } from '../api/client'

export function renderApp(ui: ReactElement, { route = '/', lang = 'vi' as Lang } = {}) {
  return render(<I18nProvider initial={lang}><SettingsProvider><MemoryRouter initialEntries={[route]}>{ui}</MemoryRouter></SettingsProvider></I18nProvider>)
}

type Handler = (url: string, init?: RequestInit) => { status?: number; body: unknown } | Promise<{ status?: number; body: unknown }>
export function mockFetch(routes: Record<string, Handler | unknown>) {
  const calls: { url: string; init?: RequestInit }[] = []
  const f = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input); calls.push({ url, init })
    const key = Object.keys(routes).find((k) => url.startsWith(k))
    if (!key) return new Response(JSON.stringify({ error: { code: 'nf', message: 'no route ' + url } }), { status: 404 })
    const r = routes[key]
    const wrapped = r !== null && typeof r === 'object' && 'body' in (r as object)
    const out = typeof r === 'function' ? await (r as Handler)(url, init) : wrapped ? (r as { status?: number; body: unknown }) : { body: r }
    return new Response(JSON.stringify(out.body), { status: out.status ?? 200, headers: { 'Content-Type': 'application/json' } })
  })
  vi.stubGlobal('fetch', f)
  return { calls, f }
}

export const IMG = (id: string, extra = {}) => ({ image_id: id, filename: id + '.jpg', kind: 'archive_photo', title: 'Ảnh ' + id, title_en: 'Photo ' + id, title_zh: '图 ' + id, image_url: `/api/images/${id}/file`, thumb_url: `/api/images/${id}/file?size=thumb`,
  time_period: 'Chưa xác định', estimated_date: 'Chưa xác định', location: 'Cầu Hiền Lương', location_confidence: 'high', confidence_level: 'high', related_book_topics: ['bridge'], duplicate_group: null, similar_scene_group: null,
  printed_page: null, caption: null, width: 960, height: 640, source: 'Archive_2.zip', keywords: [], main_objects: [], visible_text: [], ...extra })

export const CHAT_RESP = {
  answer: 'Cột cờ đầu tiên cao 12 m [S1].', language: 'vi', confidence: 'high', insufficient_evidence: false, mode: 'llm', warnings: [], retrieval: { backend: 'hybrid', glossary_hits: [] },
  sources: [{ label: 'S1', source_id: 'SRC001', source_title: 'Đôi bờ giới tuyến (1954–1967)', source_type: 'BOOK', chunk_id: 'SRC001-0445', pdf_page: 94, pdf_page_end: 94, printed_page: 188, printed_page_end: 188,
    provision: null, chapter: 'Cầu và cột cờ Hiền Lương', content: 'Ngày 8-10-1954, ta dựng cột cờ đầu tiên cao 12m', verification_status: 'ocr_unverified', cited: true }],
  images: [{ image_id: 'IMG004', title: 'Toàn cảnh cầu', title_en: 'View of the bridge', title_zh: '大桥全景', image_url: '/api/images/IMG004/file', thumb_url: '/api/images/IMG004/file?size=thumb', caption: null, time_period: 'Chưa xác định' }],
}
