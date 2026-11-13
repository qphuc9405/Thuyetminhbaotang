// Bộ điều khiển âm thanh DUY NHẤT của ứng dụng: chỉ một tiếng phát tại một thời điểm.
// Ưu tiên giọng ElevenLabs qua museum-guide (/api/narration/generate, có cache phía server);
// nếu backend báo không có khoá / lỗi mạng thì lùi về giọng đọc của trình duyệt (speechSynthesis).
// stopAll() được gọi ở MỌI lối thoát khu vực (về bản đồ, đổi khu, Back của trình duyệt, đóng tab).
import { MG } from './mg';
import { LANGS, type Lang } from './i18n';

export type Engine = 'eleven' | 'browser' | 'file';
export type AudioStatus = 'idle' | 'loading' | 'playing' | 'paused';
export type AudioState = {
  status: AudioStatus; key: string | null; pos: number; dur: number; engine: Engine | null;
  /** 0..1 – độ mở miệng giả lập cho nhân vật hướng dẫn */
  level: number; blocked: boolean; fallback: boolean; muted: boolean;
  ttsError: string | null;
};

const IDLE: AudioState = { status: 'idle', key: null, pos: 0, dur: 0, engine: null, level: 0, blocked: false, fallback: false, muted: false, ttsError: null };
let state: AudioState = IDLE;
const subs = new Set<(s: AudioState) => void>();
const set = (p: Partial<AudioState>) => { state = { ...state, ...p }; subs.forEach(f => f(state)); };

export const getAudio = () => state;
export function subscribe(f: (s: AudioState) => void) { subs.add(f); return () => { subs.delete(f); }; }

let el: HTMLAudioElement | null = null;
let utter: SpeechSynthesisUtterance | null = null;
let fetchCtl: AbortController | null = null;
let token = 0;
let mouth: ReturnType<typeof setInterval> | null = null;
let muted = false;
const urlCache = new Map<string, string>();
const supportsSpeech = typeof window !== 'undefined' && 'speechSynthesis' in window;
const CHARS_PER_SEC = 13.5;
/** tốc độ đọc ước tính (ký tự/giây) – tiếng Trung đọc ít ký tự hơn mỗi giây */
export const cps = (lang: Lang) => (lang === 'zh' ? 4.2 : CHARS_PER_SEC);

function startMouth() {
  stopMouth();
  mouth = setInterval(() => { if (state.status === 'playing') set({ level: state.level > 0.3 ? 0.1 : 0.55 + Math.random() * 0.45 }); }, 140);
}
function stopMouth() { if (mouth) clearInterval(mouth); mouth = null; if (state.level) set({ level: 0 }); }

function releaseElement() {
  if (!el) return;
  el.onplaying = el.onpause = el.onended = el.onerror = el.ontimeupdate = el.onloadedmetadata = null;
  el.pause();
  el.removeAttribute('src');
  try { el.load(); } catch { /* jsdom */ }
  el = null;
}

/** Dừng mọi âm thanh đang phát hoặc đang chuẩn bị. */
export function stopAll() {
  token++;
  fetchCtl?.abort(); fetchCtl = null;
  releaseElement();
  if (utter) { utter.onend = utter.onerror = utter.onboundary = utter.onstart = null; utter = null; }
  if (supportsSpeech) { try { window.speechSynthesis.cancel(); } catch { /* ignore */ } }
  stopMouth();
  state = { ...IDLE, muted }; subs.forEach(f => f(state));
}

export function setMuted(m: boolean) {
  muted = m;
  set({ muted: m });
  if (m) pause();
  else resume();
}
export const isMuted = () => muted;

export function pause() {
  if (state.status !== 'playing' && state.status !== 'loading') return;
  if (el) el.pause();
  else if (supportsSpeech && utter) window.speechSynthesis.pause();
  stopMouth();
  set({ status: 'paused' });
}

export function resume() {
  if (state.status !== 'paused' || muted) return;
  if (el) { void el.play().catch(() => set({ blocked: true })); return; }
  if (supportsSpeech && utter) { window.speechSynthesis.resume(); set({ status: 'playing', blocked: false }); startMouth(); }
}

function playElement(my: number, key: string, url: string, engine: Engine, onFail?: () => void) {
  const a = new Audio(url);
  el = a;
  a.preload = 'auto';
  a.muted = false;
  a.onloadedmetadata = () => { if (my === token && Number.isFinite(a.duration)) set({ dur: a.duration }); };
  a.ontimeupdate = () => { if (my === token && a.duration) set({ pos: a.currentTime / a.duration, dur: a.duration }); };
  a.onplaying = () => { if (my !== token) return; set({ status: 'playing', blocked: false, engine }); startMouth(); };
  a.onpause = () => { if (my === token && !a.ended && state.status === 'playing') { stopMouth(); set({ status: 'paused' }); } };
  a.onended = () => { if (my !== token) return; stopMouth(); releaseElement(); set({ status: 'idle', pos: 1, level: 0 }); };
  a.onerror = () => { if (my !== token) return; releaseElement(); if (onFail) onFail(); else stopAll(); };
  set({ key, engine, status: 'loading', pos: 0 });
  if (muted) { set({ status: 'paused' }); return; }
  void a.play().catch((e: DOMException) => {
    if (my !== token || e.name === 'AbortError') return;
    // Trình duyệt chặn tự phát (chưa có thao tác của người dùng) → chờ người dùng bấm phát.
    set({ status: 'paused', blocked: e.name === 'NotAllowedError' });
  });
}

function speakBrowser(my: number, key: string, text: string, lang: Lang) {
  if (!supportsSpeech) { set({ status: 'idle', key: null }); return; }
  window.speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text);
  u.lang = LANGS.find(l => l.id === lang)?.speech ?? 'vi-VN';
  u.rate = 0.95;
  utter = u;
  set({ key, engine: 'browser', status: 'loading', pos: 0, dur: text.length / cps(lang), fallback: true });
  u.onstart = () => { if (my === token) { set({ status: 'playing' }); startMouth(); } };
  u.onboundary = e => { if (my === token) set({ pos: e.charIndex / Math.max(1, text.length) }); };
  const end = () => { if (my !== token) return; utter = null; stopMouth(); set({ status: 'idle', pos: 1 }); };
  u.onend = end; u.onerror = end;
  if (muted) { set({ status: 'paused' }); }
  window.speechSynthesis.speak(u);
  if (muted) window.speechSynthesis.pause(); else window.speechSynthesis.resume();
}

/** Đọc một đoạn văn. key dùng để biết thanh thuyết minh nào đang phát. */
export async function speak(key: string, text: string, lang: Lang, voiceId?: string) {
  stopAll();
  const my = token;
  const clean = text.replace(/\s+/g, ' ').trim().slice(0, 7900);
  if (!clean) return;
  set({ key, status: 'loading', pos: 0, dur: clean.length / cps(lang), engine: null, fallback: false });
  const ck = `${lang}|${voiceId ?? ''}|${clean}`;
  let url = urlCache.get(ck);
  if (!url) {
    const ctl = new AbortController();
    fetchCtl = ctl;
    try {
      const r = await fetch(`${MG}/api/narration/generate`, {
        method: 'POST', signal: ctl.signal, headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: clean, language: lang, ...(voiceId ? { voice_id: voiceId } : {}) }),
      });
      if (my !== token) return;
      if (r.ok) {
        const j = await r.json() as { audio_url?: string };
        if (j.audio_url) { url = `${MG}${j.audio_url}`; urlCache.set(ck, url); }
      } else {
        const j = await r.json().catch(() => null) as { error?: { code?: string } } | null;
        if (my !== token) return;
        set({ ttsError: j?.error?.code ?? 'tts_network_error' });
      }
    } catch {
      if (my !== token) return;
      set({ ttsError: 'tts_network_error' });
    } finally {
      if (fetchCtl === ctl) fetchCtl = null;
    }
  }
  if (my !== token) return;
  if (url) playElement(my, key, url, 'eleven', () => { if (my === token) speakBrowser(my, key, clean, lang); });
  else speakBrowser(my, key, clean, lang);
}

/** Phát một tệp âm thanh có sẵn (vd. bài giới thiệu trang chủ). */
export function playFile(key: string, url: string) {
  stopAll();
  playElement(token, key, url, 'file');
}

/** Phát/tạm dừng cho đúng thanh thuyết minh có key này. */
export function toggle(key: string, text: string, lang: Lang, voiceId?: string) {
  if (state.key === key) {
    if (state.status === 'playing' || state.status === 'loading') { pause(); return; }
    if (state.status === 'paused') { if (muted) setMuted(false); else resume(); return; }
  }
  if (muted) { muted = false; set({ muted: false }); }
  void speak(key, text, lang, voiceId);
}

if (typeof window !== 'undefined') {
  window.addEventListener('pagehide', stopAll);
}
