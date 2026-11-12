import { useEffect, useRef, useState, type PointerEvent as RPointerEvent, type WheelEvent as RWheelEvent } from 'react';
import { createPortal } from 'react-dom';
import { ChevronLeft, ChevronRight, Minus, Plus, Scan, X } from 'lucide-react';
import { useT } from './i18n';

export type LbItem = { src: string; title: string; caption?: string | null; meta?: string | null };

/** Xem ảnh lớn: phóng to (cuộn chuột / chụm hai ngón / nút), kéo để di chuyển, trước/sau, Esc để đóng. */
export default function Lightbox({ items, index, onClose, onIndex }: { items: LbItem[]; index: number; onClose: () => void; onIndex: (i: number) => void }) {
  const t = useT();
  const [z, setZ] = useState(1);
  const [off, setOff] = useState({ x: 0, y: 0 });
  const [loaded, setLoaded] = useState(false);
  const drag = useRef<{ x: number; y: number; ox: number; oy: number } | null>(null);
  const pts = useRef(new Map<number, { x: number; y: number }>());
  const pinch = useRef<{ d: number; z: number } | null>(null);
  const closeBtn = useRef<HTMLButtonElement>(null);
  const it = items[index];
  const n = items.length;

  useEffect(() => { setZ(1); setOff({ x: 0, y: 0 }); setLoaded(false); }, [index]);
  useEffect(() => { closeBtn.current?.focus(); }, []);
  useEffect(() => {
    const k = (e: KeyboardEvent) => {
      if (e.key === 'Escape') { e.stopPropagation(); onClose(); }
      else if (e.key === 'ArrowRight' && n > 1) onIndex((index + 1) % n);
      else if (e.key === 'ArrowLeft' && n > 1) onIndex((index - 1 + n) % n);
      else if (e.key === '+' || e.key === '=') setZ(v => Math.min(5, v * 1.25));
      else if (e.key === '-') setZ(v => Math.max(1, v / 1.25));
    };
    window.addEventListener('keydown', k, true);
    return () => window.removeEventListener('keydown', k, true);
  }, [index, n, onClose, onIndex]);
  useEffect(() => { if (z === 1) setOff({ x: 0, y: 0 }); }, [z]);

  const onWheel = (e: RWheelEvent) => { setZ(v => Math.min(5, Math.max(1, v * (e.deltaY < 0 ? 1.15 : 1 / 1.15)))); };
  const down = (e: RPointerEvent) => {
    (e.target as Element).setPointerCapture?.(e.pointerId);
    pts.current.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (pts.current.size === 2) {
      const [a, b] = [...pts.current.values()];
      pinch.current = { d: Math.hypot(a.x - b.x, a.y - b.y), z };
      drag.current = null;
    } else drag.current = { x: e.clientX, y: e.clientY, ox: off.x, oy: off.y };
  };
  const move = (e: RPointerEvent) => {
    if (!pts.current.has(e.pointerId)) return;
    pts.current.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (pinch.current && pts.current.size === 2) {
      const [a, b] = [...pts.current.values()];
      setZ(Math.min(5, Math.max(1, pinch.current.z * Math.hypot(a.x - b.x, a.y - b.y) / pinch.current.d)));
    } else if (drag.current && z > 1) {
      setOff({ x: drag.current.ox + e.clientX - drag.current.x, y: drag.current.oy + e.clientY - drag.current.y });
    }
  };
  const up = (e: RPointerEvent) => { pts.current.delete(e.pointerId); if (pts.current.size < 2) pinch.current = null; if (!pts.current.size) drag.current = null; };

  if (!it) return null;
  return createPortal(
    <div className="lightbox lb2" role="dialog" aria-modal="true" aria-label={it.title} onClick={onClose}>
      <div className="lb-top" onClick={e => e.stopPropagation()}>
        {n > 1 && <span className="lb-count">{index + 1} / {n}</span>}
        <div className="lb-zoom">
          <button onClick={() => setZ(v => Math.max(1, v / 1.25))} aria-label={t('zoomOut')} title={t('zoomOut')} disabled={z <= 1}><Minus size={18} /></button>
          <span>{Math.round(z * 100)}%</span>
          <button onClick={() => setZ(v => Math.min(5, v * 1.25))} aria-label={t('zoomIn')} title={t('zoomIn')} disabled={z >= 5}><Plus size={18} /></button>
          <button onClick={() => setZ(1)} aria-label={t('zoomReset')} title={t('zoomReset')}><Scan size={18} /></button>
        </div>
        <button ref={closeBtn} className="lightbox-close" onClick={onClose} aria-label={t('close')} title={t('close')}><X /></button>
      </div>
      {n > 1 && <button className="lb-nav prev" onClick={e => { e.stopPropagation(); onIndex((index - 1 + n) % n); }} aria-label={t('prev')}><ChevronLeft size={30} /></button>}
      <figure onClick={e => e.stopPropagation()} key={index}>
        <div className={`lb-img-wrap ${z > 1 ? 'zoomed' : ''}`} onWheel={onWheel} onPointerDown={down} onPointerMove={move} onPointerUp={up} onPointerCancel={up}
          onDoubleClick={() => setZ(v => (v > 1 ? 1 : 2.2))}>
          {!loaded && <span className="zone-spinner lb-spinner" aria-hidden="true" />}
          <img src={it.src} alt={it.title} draggable={false} onLoad={() => setLoaded(true)} onError={() => setLoaded(true)}
            style={{ transform: `translate(${off.x}px, ${off.y}px) scale(${z})`, opacity: loaded ? 1 : 0 }} />
        </div>
        <figcaption><strong>{it.title}</strong>{it.caption && <span>{it.caption}</span>}{it.meta && <small>{it.meta}</small>}</figcaption>
      </figure>
      {n > 1 && <button className="lb-nav next" onClick={e => { e.stopPropagation(); onIndex((index + 1) % n); }} aria-label={t('next')}><ChevronRight size={30} /></button>}
    </div>,
    document.body,
  );
}
