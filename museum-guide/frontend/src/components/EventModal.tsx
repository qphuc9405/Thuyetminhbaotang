import { useEffect } from 'react'
import { Link } from 'react-router-dom'
import type { TimelineEvent } from '../api/client'
import { useI18n } from '../i18n'

/** Thuyết minh chi tiết một mốc: ảnh (ghi rõ minh hoạ hay trực tiếp), tóm tắt có nguồn, bằng chứng OCR, mốc trước/sau. */
export default function EventModal({ events, index, onIndex, onClose }: { events: TimelineEvent[]; index: number; onIndex: (i: number) => void; onClose: () => void }) {
  const { t, pick } = useI18n()
  const e = events[index]
  useEffect(() => {
    const h = (k: KeyboardEvent) => {
      if (k.key === 'Escape') onClose()
      if (k.key === 'ArrowRight' && index < events.length - 1) onIndex(index + 1)
      if (k.key === 'ArrowLeft' && index > 0) onIndex(index - 1)
    }
    window.addEventListener('keydown', h)
    const prev = document.body.style.overflow; document.body.style.overflow = 'hidden'
    return () => { window.removeEventListener('keydown', h); document.body.style.overflow = prev }
  }, [index, events.length, onClose, onIndex])
  if (!e) return null
  const title = pick({ vi: e.title_vi, en: e.title_en, zh: e.title_zh })
  const img = e.images[0]
  const per = e.period === '1954-1956' ? t('per_p1') : e.period === '1956-1967' ? t('per_p2') : t('per_pre')
  return (
    <div role="dialog" aria-modal="true" aria-label={title} className="fixed inset-0 z-50 flex items-end justify-center bg-ink/70 sm:items-center sm:p-6" onClick={onClose}>
      <article className="relative max-h-[92vh] w-full max-w-4xl overflow-y-auto bg-paper shadow-2xl animate-rise" onClick={(x) => x.stopPropagation()}>
        <div className="grid md:grid-cols-[1.1fr_1fr]">
          <div className="relative bg-ink">
            {img ? (
              <>
                <img src={img.medium_url ?? img.thumb_url} alt={title} className="archival h-64 w-full object-cover md:h-full md:min-h-[420px]" />
                <p className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-ink/90 to-transparent p-3 pt-10 text-[11px] text-white/85">
                  {img.relation === 'illustrates' ? t('ev_direct') : t('ev_illustrative')} · <Link to={`/gallery/${img.image_id}`} className="underline">{img.image_id}</Link>
                </p>
              </>
            ) : <div className="flex h-40 items-center justify-center font-serif text-6xl text-white/20 md:h-full">{e.date_iso.slice(0, 4)}</div>}
          </div>
          <div className="p-6 sm:p-8">
            <p className="eyebrow">{per} · {index + 1} {t('ev_of')} {events.length}</p>
            <p className="mt-3 font-serif text-4xl text-flag">{e.date_label}</p>
            <h2 className="mt-2 text-2xl leading-snug">{title}</h2>
            <p className="mt-4 text-[16px] leading-relaxed text-ink2">{pick({ vi: e.summary_vi, en: e.summary_en, zh: e.summary_vi })}</p>
            <p className="museum-label mt-5 text-xs text-earth">{t('tl_source')}: {e.source_title} — {e.printed_page != null ? `${t('chat_page')}${e.printed_page}` : e.provision}</p>
            {e.evidence_snippet && <details className="mt-3 text-xs text-earth"><summary className="cursor-pointer">{t('tl_evidence')}</summary><p className="mt-1 italic">…{e.evidence_snippet}…</p></details>}
            <div className="mt-6 flex flex-wrap gap-2">
              <Link className="btn btn-primary" to={`/chat?q=${encodeURIComponent(title)}`}>{t('tl_ask')}</Link>
              {e.topic_ids[0] && <Link className="btn" to={`/topics/${e.topic_ids[0]}`}>{t('ev_topic')}</Link>}
            </div>
          </div>
        </div>
        <div className="flex items-center justify-between border-t border-rule px-4 py-3">
          <button className="btn" disabled={index === 0} onClick={() => onIndex(index - 1)}>← {t('ev_prev')}</button>
          <button className="btn" onClick={onClose}>{t('ev_close')}</button>
          <button className="btn" disabled={index >= events.length - 1} onClick={() => onIndex(index + 1)}>{t('ev_next')} →</button>
        </div>
      </article>
    </div>
  )
}
