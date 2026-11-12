import { useState } from 'react'
import { Link } from 'react-router-dom'
import { api, type ImageItem } from '../api/client'
import Lightbox from '../components/Lightbox'
import { EmptyState, ErrorBox, Loading } from '../components/StateViews'
import { useI18n } from '../i18n'
import { useAsync } from '../lib/useAsync'

const CHIPS = ['bridge', 'flagpoles', 'gate', 'slogan_wall', 'loudspeakers', 'banner_diem', 'police', 'geneva', 'dmz', 'postcard']

export default function Gallery() {
  const { t, pick } = useI18n()
  const [q, setQ] = useState(''); const [topic, setTopic] = useState(''); const [kind, setKind] = useState(''); const [hide, setHide] = useState(false)
  const [open, setOpen] = useState<ImageItem | null>(null)
  const list = useAsync(() => api.images({ q, topic, kind, hide_variants: hide }), [q, topic, kind, hide])
  return (
    <div>
      <header className="mb-8 grid gap-6 border-b border-rule pb-8 md:grid-cols-12">
        <div className="md:col-span-7"><p className="eyebrow">{t('col_eyebrow')}</p><h1 className="mt-3 text-5xl leading-tight">{t('gal_title')}</h1><p className="mt-4 max-w-2xl text-ink2">{t('gal_intro')}</p></div>
        <div className="space-y-3 md:col-span-5 md:self-end">
          <input aria-label={t('gal_search')} placeholder={t('gal_search')} className="w-full border border-rule bg-card px-3 py-2" value={q} onChange={(e) => setQ(e.target.value)} />
          <div className="flex flex-wrap items-center gap-3 text-sm">
            <select aria-label={t('gal_kind')} className="border border-rule bg-card px-2 py-1.5" value={kind} onChange={(e) => setKind(e.target.value)}>
              <option value="">{t('gal_kind')}: {t('gal_all')}</option><option value="archive_photo">{t('gal_archive')}</option><option value="book_figure">{t('gal_book')}</option><option value="contemporary_photo">{t('gal_contemporary')}</option>
            </select>
            <label className="flex items-center gap-2"><input type="checkbox" checked={hide} onChange={(e) => setHide(e.target.checked)} />{t('gal_hide')}</label>
            {list.data && <span className="ml-auto text-earth">{list.data.total} {t('gal_count')}</span>}
          </div>
        </div>
      </header>
      <div className="mb-8 flex flex-wrap gap-2" role="group" aria-label={t('gal_topic')}>
        <button className={`btn ${topic === '' ? 'btn-primary' : ''}`} aria-pressed={topic === ''} onClick={() => setTopic('')}>{t('gal_all')}</button>
        {CHIPS.map((c) => <button key={c} className={`btn ${topic === c ? 'btn-primary' : ''}`} aria-pressed={topic === c} onClick={() => setTopic(c)}>{t('gt_' + c)}</button>)}
      </div>
      {list.loading ? <Loading /> : list.error ? <ErrorBox message={list.error} onRetry={list.reload} /> : !list.data?.items.length ? <EmptyState>{t('gal_empty')}</EmptyState> : (
        <ul className="columns-1 gap-6 sm:columns-2 lg:columns-3" data-testid="gallery-grid">
          {list.data.items.map((im) => {
            const title = pick({ vi: im.title, en: im.title_en, zh: im.title_zh })
            return (
              <li key={im.image_id} className="mb-8 break-inside-avoid">
                <button className="group block w-full overflow-hidden bg-ink" onClick={() => setOpen(im)} aria-label={`${t('gal_open')}: ${title}`}>
                  <img src={`/api/images/${im.image_id}/file?size=medium`} alt={title} loading="lazy" width={im.width} height={im.height} className="archival h-auto w-full opacity-95 transition duration-700 group-hover:scale-[1.02] group-hover:opacity-100" />
                </button>
                <div className="museum-label mt-3">
                  <Link to={`/gallery/${im.image_id}`} className="font-serif text-[17px] leading-snug hover:text-flag">{title}</Link>
                  <p className="mt-1 text-xs text-earth">{im.image_id}{im.printed_page ? ` · ${t('chat_page')}${im.printed_page}` : ''}{im.kind === 'archive_photo' && im.time_period === 'Chưa xác định' ? ` · ${t('not_determined')}` : ''}{im.duplicate_group ? ` · ${im.duplicate_group}` : ''}</p>
                </div>
              </li>
            )
          })}
        </ul>
      )}
      {open && <Lightbox src={open.image_url} alt={pick({ vi: open.title, en: open.title_en, zh: open.title_zh })} caption={open.caption ?? undefined} onClose={() => setOpen(null)} />}
    </div>
  )
}
