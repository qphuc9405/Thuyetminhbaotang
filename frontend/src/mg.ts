// Lớp nối sang API của museum-guide (kho tư liệu có trích nguồn + chatbot RAG).
// Vite chuyển tiếp /mg/* -> http://127.0.0.1:8077/* (xem vite.config.ts; đổi bằng biến MG_API).
import { tr, type Lang } from './i18n';

export const MG = '/mg';
export const mgUrl = (path: string | null | undefined) => (path ? `${MG}${path}` : '');

export type L3<T = string> = { vi: T; en?: T; zh?: T };
export type Citation = {
  source_id: string; source_title: string; source_type: string;
  printed_page: number | null; provision: string | null; url?: string | null; verified_anchor: boolean | null;
};
export type MgImage = {
  image_id: string; title: string; title_en?: string | null; title_zh?: string | null; caption: string | null; kind: string; time_period?: string;
  image_url: string; medium_url?: string; thumb_url: string;
};
export type Anecdote = {
  id: string; period: string; title: L3; teaser: L3; body: L3<string[]>; citations: Citation[]; image_ids: string[]; images?: MgImage[];
};
export type ZoneEvent = {
  event_id: string; date_label: string; title: string; summary: string; printed_page: number | null; source_id: string; source_title: string;
  title_i18n?: L3; summary_i18n?: L3;
};
export type StoryZone = { kind: 'story'; title: string; events: ZoneEvent[]; stories: Anecdote[]; images: MgImage[] };
export type PlaceZone = {
  kind: 'place'; title: string; subtitle: string; paragraphs: string[]; citations: Citation[];
  title_i18n?: L3; subtitle_i18n?: L3; paragraphs_i18n?: L3<string[]>;
  local_images: { url: string; title: string; credit: string }[];
};
export type HallItem = {
  id: string; x: number; y: number; zoom: number; side?: 'l' | 'r'; label: L3; paragraphs: L3<string[]>; citations: Citation[]; images: MgImage[]; documented: boolean;
};
export type Hall = { background: string; width: number; height: number; items: HallItem[]; greeting: L3; note: L3 };
export type WebLink = { source_id: string; title: string; publisher: string; url: string; access_status: string };
export type TopicItem = {
  id: string; label: L3; paragraphs: L3<string[]>; citations: Citation[]; images: MgImage[];
  room: [number, number] | null; scene: [number, number] | null;
  needs_source: boolean; needs_note: L3 | null; links: WebLink[]; documented: boolean;
};
export type Topic = {
  id: string; no: number; short: L3; title: L3; subtitle: L3; room: [number, number]; focus: [number, number, number];
  scene: { src: string; width: number; height: number } | null; items: TopicItem[]; cover: MgImage | null;
};
export type TopicsHall = {
  background: string; width: number; height: number;
  intro: { id: string; label: L3; room: [number, number]; focus: [number, number, number]; paragraphs: L3<string[]>; citations: Citation[]; images: MgImage[] };
  topics: Topic[]; artifacts: { id: string; topic: string; room: [number, number]; label: L3 }[]; needs_label: L3; note: string;
};
export type MuseumZone = { kind: 'exhibition'; title: string; groups: Record<string, string>; n_exhibits: number; hall: Hall; topics: TopicsHall };
export type ChatImage = { image_id: string; title: string; title_en?: string | null; title_zh?: string | null; thumb_url: string; image_url: string; caption?: string | null; time_period?: string };
export type ChatResult = {
  answer: string; mode: string; insufficient_evidence: boolean;
  sources: { label: string; source_title: string; source_type: string; printed_page: number | null; provision: string | null }[];
  images: ChatImage[];
};

export async function mgGet<T>(path: string, signal?: AbortSignal): Promise<T> {
  const r = await fetch(`${MG}${path}`, { signal });
  if (!r.ok) throw new Error(`${r.status}`);
  return r.json() as Promise<T>;
}

export async function mgChat(message: string, language: Lang, sessionId: string, signal?: AbortSignal): Promise<ChatResult> {
  const r = await fetch(`${MG}/api/chat`, {
    method: 'POST', signal, headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, language, session_id: sessionId }),
  });
  if (!r.ok) throw new Error(`${r.status}`);
  return r.json() as Promise<ChatResult>;
}

/** Tên ảnh theo ngôn ngữ (thiếu bản dịch thì dùng tên tiếng Việt). */
export function imgTitle(im: { title: string; title_en?: string | null; title_zh?: string | null }, lang: Lang): string {
  return (lang === 'en' && im.title_en) || (lang === 'zh' && im.title_zh) || im.title;
}

export function citeLabel(c: Citation, lang: Lang = 'vi'): string {
  if (c.source_type === 'BOOK' && c.printed_page) return tr(lang, 'bookPage', { x: c.printed_page });
  if (c.source_type === 'WEB_ARTICLE') return c.provision || c.source_title;
  if (c.provision) return `${c.source_id} · ${c.provision}`;
  return c.source_title || c.source_id;
}

export function uniqueCites(cs: Citation[]): Citation[] {
  const seen = new Set<string>();
  return cs.filter(c => { const k = `${c.source_id}|${c.printed_page}|${c.provision}`; if (seen.has(k)) return false; seen.add(k); return true; });
}
