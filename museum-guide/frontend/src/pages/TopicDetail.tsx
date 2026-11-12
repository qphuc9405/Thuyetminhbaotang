import { Link, useParams } from 'react-router-dom'
import { api } from '../api/client'
import { ErrorBox, Loading } from '../components/StateViews'
import { useI18n } from '../i18n'
import { useAsync } from '../lib/useAsync'
import { EventCard } from './Timeline'

export default function TopicDetailPage() {
  const { id = '' } = useParams()
  const { t, pick } = useI18n()
  const { data: d, error, loading, reload } = useAsync(() => api.topic(id), [id])
  if (loading) return <Loading />
  if (error || !d) return <div className="space-y-3"><ErrorBox message={error ?? ''} onRetry={reload} /><Link className="btn" to="/topics">{t('tp_back')}</Link></div>
  return (
    <article>
      <Link className="btn mb-3" to="/topics">← {t('tp_back')}</Link>
      <h1 className="text-2xl text-oxblood">{pick({ vi: d.title_vi, en: d.title_en, zh: d.title_zh })}</h1>
      <p className="mb-4 text-sepia">{d.description_vi} <span className="tag">{d.printed_start}–{d.printed_end} {t('tp_pages')}</span></p>
      <section className="mb-6"><h2 className="mb-2 text-xl">{t('tp_chapters')}</h2>
        <ul className="space-y-1 text-sm">{d.chapters.map((c) => <li key={c.chapter_id} className="card p-2"><b>{pick({ vi: c.title_vi, en: c.title_en, zh: c.title_zh })}</b> <span className="tag">{t('chat_page')}{c.printed_start}–{c.printed_end}</span> <span className="text-xs text-sepia">{c.period_scope}</span></li>)}</ul></section>
      {d.events.length > 0 && <section className="mb-6"><h2 className="mb-2 text-xl">{t('tl_title')}</h2><ol className="space-y-3">{d.events.map((e) => <EventCard key={e.event_id} e={e} />)}</ol></section>}
      {d.images.length > 0 && <section className="mb-6"><h2 className="mb-2 text-xl">{t('gal_title')}</h2>
        <ul className="grid grid-cols-3 gap-2 sm:grid-cols-4 lg:grid-cols-6">{d.images.map((i) => <li key={i.image_id}><Link to={`/gallery/${i.image_id}`}><img src={i.thumb_url} alt={pick({ vi: i.title, en: i.title_en, zh: i.title_zh })} className="h-20 w-full rounded border border-rule object-cover" loading="lazy" /></Link></li>)}</ul></section>}
      <section><h2 className="mb-2 text-xl">{t('tp_passages')} <span className="text-sm text-sepia">({d.passages.length}/{d.n_passages_total})</span></h2>
        <ul className="space-y-2">{d.passages.slice(0, 8).map((p) => <li key={p.chunk_id} className="card p-3 text-sm"><span className="tag mb-1">{t('chat_page')}{p.printed_page}{p.printed_page_end && p.printed_page_end !== p.printed_page ? `–${p.printed_page_end}` : ''}</span><p className="whitespace-pre-wrap">{p.content}</p></li>)}</ul></section>
    </article>
  )
}
