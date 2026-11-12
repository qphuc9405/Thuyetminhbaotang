import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../api/client'
import Lightbox from '../components/Lightbox'
import { ErrorBox, Loading } from '../components/StateViews'
import { useI18n } from '../i18n'
import { useAsync } from '../lib/useAsync'

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return <div className="mb-5"><dt className="eyebrow">{label}</dt><dd className="mt-1 text-[15.5px] leading-relaxed text-ink2">{children}</dd></div>
}

export default function ImageDetailPage() {
  const { id = '' } = useParams()
  const { t, pick, lang } = useI18n()
  const { data: d, error, loading, reload } = useAsync(() => api.image(id), [id])
  const [big, setBig] = useState(false)
  if (loading) return <Loading />
  if (error || !d) return <div className="space-y-3"><ErrorBox message={error ?? 'Not found'} onRetry={reload} /><Link className="btn" to="/gallery">{t('img_back')}</Link></div>
  const title = pick({ vi: d.title, en: d.title_en, zh: d.title_zh })
  return (
    <article>
      <Link className="btn mb-3" to="/gallery">← {t('img_back')}</Link>
      <p className="eyebrow">{d.kind === "book_figure" ? t("gal_book") : d.kind === "contemporary_photo" ? t("gal_contemporary") : t("gal_archive")}</p>
      <h1 className="mb-2 mt-2 max-w-4xl text-4xl leading-tight">{title}</h1>
      <p className="mb-4 flex flex-wrap gap-1 text-xs"><span className="tag">{d.image_id}</span><span className="tag">{d.filename ?? ''}</span>
        <span className="tag">{t('img_conf')}: {d.confidence_level}</span>{d.duplicate_group && <span className="tag">{d.duplicate_group}</span>}</p>
      <div className="grid gap-10 lg:grid-cols-[1.2fr_1fr]">
        <div className="lg:sticky lg:top-20 lg:self-start">
          <button className="block w-full overflow-hidden bg-ink" onClick={() => setBig(true)} aria-label={t('gal_open')}><img src={d.image_url} alt={title} className="archival w-full" /></button>
          {d.caption && <p className="mt-2 text-sm italic text-sepia">{d.caption}</p>}
          {d.related_images.length > 0 && (
            <section className="mt-4"><h2 className="mb-1 text-base">{t('img_dup')}</h2>
              <ul className="flex flex-wrap gap-2">{d.related_images.map((r) => (
                <li key={r.image_id + r.relation}><Link to={`/gallery/${r.image_id}`} className="block w-24 text-xs"><img src={`/api/images/${r.image_id}/file?size=thumb`} alt={r.image_id} className="h-16 w-24 rounded border border-rule object-cover" />
                  <span className="block">{r.image_id}</span><span className="block text-[10px] text-sepia">{r.relation.replace(/_/g, ' ')}</span></Link></li>))}</ul></section>)}
        </div>
        <dl className="museum-label">
          {d.filename_title && <Field label={t('img_fn_title')}>{d.filename_title}<span className="block text-xs italic text-sepia">{t('img_fn_note')}</span></Field>}
          <Field label={t('img_visual')}>{d.visual_description}{lang !== 'vi' && <span className="block text-xs italic text-sepia">{t('img_desc_note')}</span>}</Field>
          <Field label={t('img_context')}>{d.historical_context}</Field>
          <Field label={t('img_location')}>{d.location} <span className="tag">{d.location_confidence}</span></Field>
          <Field label={t('img_time')}>{d.time_period === 'Chưa xác định' ? t('not_determined') : d.time_period} · {t('img_date')}: {d.estimated_date === 'Chưa xác định' ? t('not_determined') : d.estimated_date}</Field>
          <Field label={t('img_text')}>{d.visible_text.length ? <ul className="list-disc pl-5">{d.visible_text.map((x) => <li key={x}>{x}</li>)}</ul> : '—'}</Field>
          <Field label={t('img_people')}>{d.people_description || '—'}</Field>
          <Field label={t('img_source')}>{d.source} {d.watermarks.length > 0 && <span className="block text-xs text-sepia">{t('img_watermarks')}: {d.watermarks.join('; ')}</span>}<span className="block text-xs text-sepia">{t('img_rights')}: {d.rights_status}</span></Field>
          <Field label={t('img_pages')}>{d.related_book_pages.length ? <ul className="list-disc pl-5">{d.related_book_pages.map((p, i) => (
            <li key={i}>{t('chat_page')}{p.start === p.end ? p.start : `${p.start}–${p.end}`} <span className="tag">{p.link_type === 'topic_corroborated' ? t('img_link_topic') : t('img_link_direct')}</span></li>))}</ul> : '—'}</Field>
          <Field label={t('img_topics')}><div className="flex flex-wrap gap-1">{d.topics_detail.map((x) => <Link key={x.topic_id} to={`/topics/${x.topic_id}`} className="tag underline">{pick({ vi: x.title_vi, en: x.title_en, zh: x.title_zh })}</Link>)}</div></Field>
          <Field label={t('img_notes')}><span className="text-sm text-sepia">{d.verification_notes}</span></Field>
        </dl>
      </div>
      {d.related_passages.length > 0 && (
        <section className="mt-6"><h2 className="mb-2 text-xl">{t('img_passages')}</h2>
          <ul className="space-y-2">{d.related_passages.map((p) => (
            <li key={p.chunk_id} className="card p-3 text-sm"><div className="mb-1 flex flex-wrap gap-2"><span className="tag">{p.printed_page != null ? `${t('chat_page')}${p.printed_page}${p.printed_page_end && p.printed_page_end !== p.printed_page ? `–${p.printed_page_end}` : ''}` : `${p.source_id ?? ''} · ${p.provision ?? ''}`}</span>
              {p.relation === 'captioned_in_document' && <span className="tag">{t('img_link_caption')}</span>}{p.printed_page == null && p.source_title && <span className="text-xs text-sepia">{p.source_title}</span>}
              {p.chapter && <span className="text-xs text-sepia">{p.chapter}</span>}</div>{p.excerpt}…</li>))}</ul></section>)}
      {big && <Lightbox src={d.image_url} alt={title} caption={d.caption ?? undefined} onClose={() => setBig(false)} />}
    </article>
  )
}
