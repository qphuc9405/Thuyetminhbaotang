import { afterEach, vi } from 'vitest';
import { cleanup } from '@testing-library/react';

// jsdom thiếu các API trình duyệt mà ứng dụng dùng → giả lập tối thiểu.
class RO { observe() {} unobserve() {} disconnect() {} }
(globalThis as any).ResizeObserver = RO;
window.matchMedia = window.matchMedia || ((q: string) => ({ matches: false, media: q, onchange: null, addListener() {}, removeListener() {}, addEventListener() {}, removeEventListener() {}, dispatchEvent: () => false })) as any;
Element.prototype.scrollIntoView = function () {};
Element.prototype.scrollTo = function () {} as any;

export const speech = { speak: vi.fn(), cancel: vi.fn(), pause: vi.fn(), resume: vi.fn() };
(window as any).speechSynthesis = speech;
(window as any).SpeechSynthesisUtterance = class { text: string; lang = ''; rate = 1; onstart: any; onend: any; onerror: any; onboundary: any; constructor(t: string) { this.text = t; } };

export const audios: any[] = [];
(window as any).Audio = class {
  src: string; paused = true; muted = false; currentTime = 0; duration = 30; ended = false; preload = '';
  onplaying: any; onpause: any; onended: any; onerror: any; ontimeupdate: any; onloadedmetadata: any;
  constructor(src: string) { this.src = src; audios.push(this); }
  play() { this.paused = false; this.onplaying?.(); return Promise.resolve(); }
  pause() { this.paused = true; }
  load() {}
  removeAttribute() { this.src = ''; }
};

afterEach(() => { cleanup(); vi.restoreAllMocks(); speech.speak.mockClear(); speech.cancel.mockClear(); audios.length = 0; localStorage.clear(); window.location.hash = ''; });
