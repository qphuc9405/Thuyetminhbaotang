import { useEffect, useState, type CSSProperties } from 'react';
import { MessageCircle, RotateCcw, X } from 'lucide-react';
import type { Narrator } from './guides';
import { useAudio } from './Narration';
import { pick, useLang, useT } from './i18n';

/** Nhân vật hướng dẫn: nhún nhẹ và mấp máy môi khi bất kỳ thuyết minh nào đang phát. */
export function NarratorGuide({ narrator, className = '' }: { narrator: Narrator; className?: string }) {
  const a = useAudio();
  const lang = useLang();
  const t = useT();
  const speaking = a.status === 'playing';
  return (
    <div className={`soldier-guide ${className} ${speaking ? 'is-speaking has-speech-boundary' : ''} ${speaking && a.level > 0.3 ? 'mouth-open' : ''}`}
      data-narrator={narrator.id} style={{ '--mouth-x': narrator.mouthX, '--mouth-y': narrator.mouthY } as CSSProperties}
      role="img" aria-label={`${pick(narrator.label, lang)}${speaking ? ` ${t('guideSpeaking')}` : ''}`}>
      <div className="soldier-sprite" aria-hidden="true">
        <img className="soldier-pose" src={narrator.present} alt="" />
        <img className="soldier-mouth" src={narrator.speaking} alt="" />
      </div>
    </div>
  );
}

/** Bong bóng lời hướng dẫn: hiện chữ dần, thu gọn được, có nút nghe lại. */
export function GuideBubble({ text, onListen, className = '', speaking, autoHide }: { text: string; onListen?: () => void; className?: string; speaking?: boolean; autoHide?: number }) {
  const t = useT();
  const [open, setOpen] = useState(true);
  const [n, setN] = useState(0);
  useEffect(() => {
    setOpen(true);
    const reduce = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
    if (reduce) { setN(text.length); return; }
    setN(0);
    const id = setInterval(() => setN(x => { if (x >= text.length) { clearInterval(id); return x; } return x + 2; }), 18);
    return () => clearInterval(id);
  }, [text]);
  // tự thu gọn sau một lúc (khi không đọc) để không che hiện vật
  useEffect(() => {
    if (!autoHide || !open || speaking) return;
    const id = setTimeout(() => setOpen(false), autoHide);
    return () => clearTimeout(id);
  }, [autoHide, open, speaking, text]);
  if (!open) {
    return (
      <button className={`guide-bubble-min ${className}`} onClick={() => setOpen(true)} aria-label={t('showBubble')} title={t('showBubble')}>
        <MessageCircle size={20} />{speaking && <span className="guide-dots" aria-hidden="true"><i /><i /><i /></span>}
      </button>
    );
  }
  return (
    <div className={`guide-bubble ${className} ${speaking ? 'is-speaking' : ''}`} role="note">
      <p aria-live="polite">{text.slice(0, n)}<span className="guide-caret" aria-hidden="true" style={{ opacity: n < text.length ? 1 : 0 }}>▍</span></p>
      <div className="guide-bubble-actions">
        {onListen && <button onClick={onListen} title={t('listenAgain')} aria-label={t('listenAgain')}><RotateCcw size={15} /><span>{t('listenAgain')}</span></button>}
        <span className="guide-sound" aria-hidden="true"><i /><i /><i /><i /></span>
        <button className="guide-bubble-close" onClick={() => setOpen(false)} aria-label={t('hideBubble')} title={t('hideBubble')}><X size={15} /></button>
      </div>
    </div>
  );
}
