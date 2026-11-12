import { useEffect, useMemo, useState, type ReactNode } from 'react';
import { createPortal } from 'react-dom';
import { ArrowLeft, BookOpen, ChevronRight, Home, Images, Maximize2, X } from 'lucide-react';
import Lightbox, { type LbItem } from './Lightbox';
import NarrationBar from './Narration';
import { stopAll } from './audio';
import { citeLabel, imgTitle, mgGet, mgUrl, uniqueCites, type Anecdote, type Citation, type MgImage } from './mg';
import { pick, useLang, useT } from './i18n';

export function Breadcrumb({ items, onHome }: { items: string[]; onHome: () => void }) {
  const t = useT();
  return (
    <nav className="zone-crumb" aria-label={t('crumbs')}>
      <button onClick={onHome}><Home size={15} /> {t('map')}</button>
      {items.map((x, i) => <span key={i}> / <span aria-current={i === items.length - 1 ? 'page' : undefined}>{x}</span></span>)}
    </nav>
  );
}

export function Sources({ cites }: { cites: Citation[] }) {
  const t = useT();
  const lang = useLang();
  if (!cites.length) return null;
  return (
    <p className="zone-sources">
      <BookOpen size={18} aria-hidden="true" />
      <span>
        <strong>{t('sourcesFull')}: </strong>
        {uniqueCites(cites).map((c, i) => (
          <span key={i}>{i ? ' · ' : ''}{c.url ? <a href={c.url} target="_blank" rel="noreferrer" title={c.source_title}>{citeLabel(c, lang)}</a> : <span title={c.source_title}>{citeLabel(c, lang)}</span>}</span>
        ))}
      </span>
    </p>
  );
}

export function Loading({ error, onRetry }: { error: string; onRetry: () => void }) {
  const t = useT();
  return error
    ? <div className="zone-state" role="alert"><p>{error}</p><button onClick={onRetry}>{t('retry')}</button></div>
    : <div className="zone-state" role="status"><span className="zone-spinner" />{t('loading')}</div>;
}

export function useLoad<T>(path: string | null) {
  const t = useT();
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState('');
  const [n, setN] = useState(0);
  useEffect(() => {
    if (!path) return;
    const c = new AbortController();
    setData(null); setError('');
    mgGet<T>(path, c.signal).then(setData).catch(e => { if (!c.signal.aborted) setError(t('loadError', { x: (e as Error).message })); });
    return () => c.abort();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [path, n]);
  return { data, error, retry: () => setN(x => x + 1) };
}

export function BackButton({ onClick, label }: { onClick: () => void; label: string }) {
  return <button className="zone-back" onClick={onClick}><ArrowLeft size={18} /> {label}</button>;
}

/** Hộp thoại nổi dùng chung (hiện ra mềm, đóng bằng Esc / bấm nền). */
export function Modal({ title, icon, onClose, children, wide = false }: { title: string; icon?: ReactNode; onClose: () => void; children: ReactNode; wide?: boolean }) {
  const t = useT();
  useEffect(() => {
    const k = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', k);
    return () => window.removeEventListener('keydown', k);
  }, [onClose]);
  return createPortal(
    <div className="modal-veil" onClick={onClose}>
      <section className={`modal-card ${wide ? 'wide' : ''}`} role="dialog" aria-modal="true" aria-label={title} onClick={e => e.stopPropagation()}>
        <header className="modal-head">{icon}<h2>{title}</h2><button onClick={onClose} aria-label={t('close')} title={t('close')} autoFocus><X size={20} /></button></header>
        <div className="modal-body">{children}</div>
      </section>
    </div>,
    document.body,
  );
}

export const toLb = (ims: MgImage[], lang: ReturnType<typeof useLang>): LbItem[] =>
  ims.map(im => ({ src: mgUrl(im.image_url), title: imgTitle(im, lang), caption: im.caption, meta: [im.image_id, im.time_period].filter(Boolean).join(' · ') }));

/** Lưới ảnh có thể bấm xem lớn. */
export function PhotoGrid({ images, className = '' }: { images: MgImage[]; className?: string }) {
  const lang = useLang();
  const t = useT();
  const [i, setI] = useState<number | null>(null);
  return (
    <>
      <div className={`photo-grid ${className}`}>
        {images.map((im, k) => (
          <button key={im.image_id} onClick={() => setI(k)} aria-label={`${t('enlarge')}: ${imgTitle(im, lang)}`} style={{ animationDelay: `${Math.min(k, 12) * 35}ms` }}>
            <img src={mgUrl(im.thumb_url)} alt={imgTitle(im, lang)} loading="lazy" />
            <span className="photo-zoom" aria-hidden="true"><Maximize2 size={14} /></span>
            <span className="photo-cap">{imgTitle(im, lang)}</span>
          </button>
        ))}
      </div>
      {i !== null && <Lightbox items={toLb(images, lang)} index={i} onIndex={setI} onClose={() => setI(null)} />}
    </>
  );
}

export function PhotosModal({ onClose }: { onClose: () => void }) {
  const t = useT();
  const { data, error, retry } = useLoad<{ items: MgImage[] }>('/api/images?hide_variants=true&limit=200');
  return (
    <Modal title={t('allPhotos')} icon={<Images size={22} />} onClose={onClose} wide>
      {!data ? <Loading error={error} onRetry={retry} /> : <PhotoGrid images={data.items} />}
    </Modal>
  );
}

export function StoriesModal({ onClose, voice }: { onClose: () => void; voice?: string }) {
  const t = useT();
  const lang = useLang();
  const { data, error, retry } = useLoad<{ items: Anecdote[] }>('/api/anecdotes');
  const [sel, setSel] = useState<string | null>(null);
  const cur = useMemo(() => data?.items.find(a => a.id === sel), [data, sel]);
  const close = () => { if (sel) stopAll(); onClose(); };
  return (
    <Modal title={t('allStories')} icon={<BookOpen size={22} />} onClose={close} wide>
      {!data ? <Loading error={error} onRetry={retry} /> : !cur ? (
        <div className="story-grid">
          {data.items.map((a, k) => (
            <button key={a.id} className="story-tile" onClick={() => setSel(a.id)} style={{ animationDelay: `${k * 40}ms` }}>
              {a.images?.[0] && <img src={mgUrl(a.images[0].thumb_url)} alt="" loading="lazy" />}
              <span><small>{a.period}</small><strong>{pick(a.title, lang)}</strong><em>{pick(a.teaser, lang)}</em></span>
              <ChevronRight size={18} />
            </button>
          ))}
        </div>
      ) : (
        <article className="story-read">
          <button className="story-back" onClick={() => { stopAll(); setSel(null); }}><ArrowLeft size={16} /> {t('allStories')}</button>
          <small>{cur.period}</small>
          <h3>{pick(cur.title, lang)}</h3>
          <div className="exhibit-text">{(pick(cur.body, lang) ?? []).map((p, i) => <p key={i}>{p}</p>)}</div>
          {!!cur.images?.length && <PhotoGrid images={cur.images} className="small" />}
          <Sources cites={cur.citations} />
          {lang !== 'vi' && <p className="tr-note">{t('translationNote')}</p>}
          <NarrationBar id={`story-${cur.id}`} text={`${pick(cur.title, lang)}. ${(pick(cur.body, lang) ?? []).join(' ')}`} voiceId={voice} />
        </article>
      )}
    </Modal>
  );
}
