// Client API: chỉ gọi backend qua đường dẫn tương đối /api (proxy ở dev, cùng origin ở production). Không có khoá bí mật ở frontend.
export type Lang = 'vi' | 'en' | 'zh'

export interface SourceRef {
  label: string; source_id: string; source_title: string; source_type: string; chunk_id: string
  pdf_page: number | null; pdf_page_end: number | null; printed_page: number | null; printed_page_end: number | null
  provision: string | null; chapter: string | null; content: string; verification_status: string; cited: boolean
}
export interface ImageRef { image_id: string; title: string; title_en?: string | null; title_zh?: string | null; image_url: string; thumb_url: string; caption?: string | null; time_period: string }
export interface ChatResponse {
  answer: string; language: Lang; sources: SourceRef[]; images: ImageRef[]; confidence: 'high' | 'medium' | 'low'
  insufficient_evidence: boolean; mode: 'llm' | 'abstain' | 'extractive_fallback'; warnings: string[]
  retrieval: { backend: string; glossary_hits: string[]; profile?: string; target_words?: number[]; n_context_chunks?: number }
}
export interface ImageItem {
  image_id: string; filename: string; kind: string; title: string; title_en: string | null; title_zh: string | null; image_url: string; thumb_url: string; time_period: string; estimated_date: string
  location: string; location_confidence: string; confidence_level: string; related_book_topics: string[]; duplicate_group: string | null; similar_scene_group: string | null
  printed_page: number | null; caption: string | null; width: number; height: number; source: string; keywords: string[]; main_objects: string[]; visible_text: string[]
}
export interface ImageDetail extends ImageItem {
  visual_description: string; historical_context: string; people_description: string; historical_significance: string; related_events: string[]
  related_book_pages: { start: number; end: number; link_type: string }[]; verification_notes: string; watermarks: string[]; rights_status: string
  related_images: { image_id: string; relation: string; basis: string; confidence: string }[]
  related_passages: { chunk_id: string; source_id?: string; source_title?: string; source_type?: string; provision?: string | null; relation?: string | null; printed_page: number | null; printed_page_end: number | null; chapter: string | null; excerpt: string; link_type: string | null }[]
  topics_detail: { topic_id: string; title_vi: string; title_en: string; title_zh: string }[]; related_events_detail: { event_id: string; date_label: string; title_vi: string }[]
  sha256: string | null; phash: string | null; filename_title?: string | null; caption_status?: string | null; source_id?: string | null
}
export interface TimelineEvent {
  event_id: string; date_iso: string; date_label: string; title_vi: string; title_en: string; title_zh: string; summary_vi: string; summary_en: string; period: string
  source_id: string; source_title: string; source_type: string; printed_page: number | null; provision: string | null; evidence_snippet: string; verification_status: string
  topic_ids: string[]; images: { image_id: string; thumb_url: string; medium_url?: string; relation?: string; basis?: string }[]
}
export interface Topic { topic_id: string; title_vi: string; title_en: string; title_zh: string; description_vi: string; printed_start: number | null; printed_end: number | null; n_events?: number; n_images?: number }
export interface TopicDetail extends Topic {
  chapters: { chapter_id: string; title_vi: string; title_en: string; title_zh: string; printed_start: number; printed_end: number; period_scope: string }[]
  events: TimelineEvent[]; images: ImageItem[]; passages: { chunk_id: string; content: string; printed_page: number; printed_page_end: number | null; chapter: string | null }[]; n_passages_total: number
}
export interface Narration { audio_id: string; status: string; audio_url: string; cached: boolean; segments: number; language: Lang }

export interface StoryChapter {
  id: string; period: string; image_id: string; topic_id: string; timeline_period: string
  title: Record<Lang, string>; lead: Record<Lang, string>; body: Record<Lang, string[]>
  citations: { source_id: string; source_title: string; source_type: string; printed_page: number | null; provision: string | null; verified_anchor: boolean }[]
  image: { image_id: string; title: string; title_en: string | null; title_zh: string | null; caption: string | null; image_url: string; medium_url: string; kind: string; printed_page: number | null } | null
}
export interface Story { chapters: StoryChapter[]; hero: { image_id: string; image_url: string; title: string; note: string } | null }

export interface AnecdoteImage { image_id: string; title: string; title_en: string | null; title_zh: string | null; caption: string | null; kind: string; image_url: string; medium_url: string; thumb_url: string; printed_page: number | null; time_period: string }
export interface AnecdoteCitation { source_id: string; source_title: string; source_type: string; printed_page: number | null; provision: string | null; url?: string | null; record_id?: string | null; verified_anchor: boolean | null }
export interface Anecdote {
  id: string; period: string; topic_id: string; image_ids: string[]; notes: string[]
  title: Record<Lang, string>; teaser: Record<Lang, string>; body: Record<Lang, string[]>; citations: AnecdoteCitation[]
  images: AnecdoteImage[]; notes_detail: { chunk_id: string; title: string }[]
}

export class ApiError extends Error {
  constructor(public status: number, public code: string, message: string) { super(message) }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response
  try {
    res = await fetch(path, { headers: { 'Content-Type': 'application/json' }, ...init })
  } catch {
    throw new ApiError(0, 'network_error', 'Không kết nối được máy chủ. Hãy kiểm tra backend đã chạy chưa.')
  }
  if (!res.ok) {
    let code = 'http_error', msg = `Lỗi ${res.status}`
    try { const j = await res.json(); code = j?.error?.code ?? code; msg = j?.error?.message ?? j?.detail ?? msg } catch { /* giữ mặc định */ }
    throw new ApiError(res.status, code, typeof msg === 'string' ? msg : `Lỗi ${res.status}`)
  }
  return res.json() as Promise<T>
}

const qs = (o: Record<string, string | number | boolean | undefined>) => {
  const p = new URLSearchParams()
  Object.entries(o).forEach(([k, v]) => { if (v !== undefined && v !== '' && v !== false) p.set(k, String(v)) })
  const s = p.toString(); return s ? `?${s}` : ''
}

export const api = {
  chat: (message: string, language: Lang | 'auto', session_id: string) => request<ChatResponse>('/api/chat', { method: 'POST', body: JSON.stringify({ message, language, session_id }) }),
  images: (o: { q?: string; topic?: string; kind?: string; hide_variants?: boolean; limit?: number }) => request<{ total: number; items: ImageItem[] }>(`/api/images${qs({ limit: 200, ...o })}`),
  image: (id: string) => request<ImageDetail>(`/api/images/${encodeURIComponent(id)}`),
  topics: () => request<{ items: Topic[] }>('/api/topics'),
  topic: (id: string) => request<TopicDetail>(`/api/topics/${encodeURIComponent(id)}`),
  timeline: (period?: string) => request<{ items: TimelineEvent[]; note: string }>(`/api/timeline${qs({ period })}`),
  story: () => request<Story>('/api/story'),
  anecdotes: () => request<{ items: Anecdote[]; note: string }>('/api/anecdotes'),
  health: () => request<{ status: string; llm: { configured: boolean; model: string }; tts: { configured: boolean; model: string }; retrieval: { backend: string; image_retrieval: string }; database: Record<string, number> }>('/api/health'),
  narrate: (text: string, language: Lang, voice_id?: string) => request<Narration>('/api/narration/generate', { method: 'POST', body: JSON.stringify({ text, language, ...(voice_id ? { voice_id } : {}) }) }),
}
