import { useEffect, useRef, useState } from 'react';
import { BookOpen, ChevronDown, ChevronUp, Maximize2, Mic, Send, Sparkles, Trash2 } from 'lucide-react';
import Lightbox, { type LbItem } from './Lightbox';
import { imgTitle, mgUrl, type ChatImage } from './mg';
import { useLang, useT } from './i18n';

export type Talk = { role: 'user' | 'assistant'; text: string; sources?: string[]; images?: ChatImage[]; error?: boolean };

/** Thanh chat dùng chung cho mọi khu vực: gợi ý câu hỏi, lịch sử thu gọn được, ảnh trả lời xem lớn được. */
export default function ChatDock({ talks, busy, query, setQuery, onSend, onClear, onMic, suggestions = [], placeholder, className = '' }: {
  talks: Talk[]; busy: boolean; query: string; setQuery: (q: string) => void; onSend: (q?: string) => void; onClear: () => void; onMic: () => void;
  suggestions?: string[]; placeholder: string; className?: string;
}) {
  const t = useT();
  const lang = useLang();
  const [open, setOpen] = useState(true);
  const [elapsed, setElapsed] = useState(0);
  const [lb, setLb] = useState<{ items: LbItem[]; i: number } | null>(null);
  const hist = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setElapsed(0);
    if (!busy) return;
    const start = Date.now();
    const timer = setInterval(() => setElapsed(Math.floor((Date.now() - start) / 1000)), 1000);
    return () => clearInterval(timer);
  }, [busy]);

  useEffect(() => { if (talks.length) setOpen(true); }, [talks.length]);
  useEffect(() => {
    const h = hist.current;
    if (h) h.scrollTo?.({ top: h.scrollHeight, behavior: 'smooth' });
  }, [talks.length, busy, open]);

  const openImages = (imgs: ChatImage[], i: number) => setLb({
    i, items: imgs.map(im => ({ src: mgUrl(im.image_url), title: imgTitle(im, lang), caption: im.caption, meta: [im.image_id, im.time_period].filter(Boolean).join(' · ') })),
  });

  return (
    <section className={`chat-dock2 ${className}`} aria-label={t('askLabel')}>
      {talks.length > 0 && (
        <div className={`chat-panel ${open ? 'open' : 'closed'}`}>
          <div className="chat-panel-head">
            <span><Sparkles size={15} /> {t('chatHistory')} <small>({talks.filter(x => x.role === 'user').length})</small></span>
            <span className="chat-panel-tools">
              <button onClick={onClear} aria-label={t('clearChat')} title={t('clearChat')}><Trash2 size={15} /></button>
              <button onClick={() => setOpen(o => !o)} aria-label={open ? t('hideChat') : t('showChat')} title={open ? t('hideChat') : t('showChat')} aria-expanded={open}>
                {open ? <ChevronDown size={17} /> : <ChevronUp size={17} />}
              </button>
            </span>
          </div>
          {open && (
            <div className="chat-history2" ref={hist} aria-live="polite">
              {talks.map((talk, k) => (
                <div className={`chat-msg ${talk.role} ${talk.error ? 'error' : ''}`} key={k}>
                  <p>{talk.text}</p>
                  {!!talk.images?.length && (
                    <div className="chat-gallery" aria-label={t('imagesInAnswer')}>
                      <small>{t('imagesInAnswer')}</small>
                      <div className={`chat-gallery-grid n${Math.min(talk.images.length, 3)}`}>
                        {talk.images.map((im, i) => (
                          <button key={im.image_id} onClick={() => openImages(talk.images!, i)} aria-label={`${t('enlarge')}: ${imgTitle(im, lang)}`}>
                            <img src={mgUrl(im.thumb_url)} alt={imgTitle(im, lang)} loading="lazy" />
                            <span className="chat-img-zoom" aria-hidden="true"><Maximize2 size={14} /></span>
                            <span className="chat-img-cap">{imgTitle(im, lang)}</span>
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                  {!!talk.sources?.length && <small className="chat-src"><BookOpen size={12} /> {t('sources')}: {talk.sources.join('; ')}</small>}
                </div>
              ))}
              {busy && <div className="chat-msg assistant typing"><span className="typing-dots" aria-label={t('searching')}><i /><i /><i /></span> {t('searching')} <small aria-live="off">{elapsed > 0 ? `${elapsed} s` : ''}</small></div>}
            </div>
          )}
        </div>
      )}
      {suggestions.length > 0 && (
        <div className="chat-suggest" role="group" aria-label={t('suggestions')}>
          <span>{t('suggestions')}</span>
          {suggestions.map(q => <button key={q} onClick={() => onSend(q)} disabled={busy}>{q}</button>)}
        </div>
      )}
      <form className="chat-form2" onSubmit={e => { e.preventDefault(); onSend(); }}>
        <button type="button" className="chat-mic" onClick={onMic} aria-label={t('voiceInput')} title={t('voiceInput')}><Mic size={20} /></button>
        <input value={query} onChange={e => setQuery(e.target.value)} placeholder={placeholder} aria-label={t('askLabel')} maxLength={800} />
        <button type="submit" className="chat-send" disabled={busy || !query.trim()} aria-label={t('send')} title={t('send')}><Send size={19} /></button>
      </form>
      {lb && <Lightbox items={lb.items} index={lb.i} onIndex={i => setLb(v => (v ? { ...v, i } : v))} onClose={() => setLb(null)} />}
    </section>
  );
}
