import { useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { api, type TimelineEvent } from '../api/client'
import EventModal from '../components/EventModal'
import { EmptyState, ErrorBox, Loading } from '../components/StateViews'
import { useI18n } from '../i18n'
import { useAsync } from '../lib/useAsync'
import { useReveal } from '../lib/useReveal'

// Giữ để tương thích với TopicDetail (danh sách sự kiện dạng thẻ)
export function EventCard({ e }: { e: TimelineEvent }) {
  const { t, pick } = useI18n()
  const title = pick({ vi: e.title_vi, en: e.title_en, zh: e.title_zh })
  return (
    <li className="border-l-2 border-rule pl-4" data-testid="timeline-event">
      <p className="font-serif text-xl text-flag">{e.date_label}</p>
      <h3 className="text-base font-semibold">{title}</h3>
      <p className="mt-1 text-sm text-ink2">{pick({ vi: e.summary_vi, en: e.summary_en, zh: e.summary_vi })}</p>
      <p className="mt-1 text-xs text-earth">{t('tl_source')}: {e.source_title} — {e.printed_page != null ? `${t('chat_page')}${e.printed_page}` : e.provision}</p>
      <Link className="btn mt-2" to={`/chat?q=${encodeURIComponent(title)}`}>{t('tl_ask')}</Link>
    </li>
  )
}

function Row({ e, i, onOpen }: { e: TimelineEvent; i: number; onOpen: (i: number) => void }) {
  const { t, pick } = useI18n()
  const ref = useReveal<HTMLLIElement>()
  const title = pick({ vi: e.title_vi, en: e.title_en, zh: e.title_zh })
  return (
    <li ref={ref} className="reveal relative grid gap-4 pb-12 pl-8 sm:grid-cols-[150px_1fr_220px] sm:gap-8 sm:pl-0" data-testid="timeline-event">
      <span className="absolute left-0 top-2 h-3 w-3 -translate-x-[5px] rounded-full border-2 border-paper bg-flag sm:left-[165px]" aria-hidden />
      <p className="font-serif text-2xl leading-none text-flag sm:pt-1 sm:text-right">{e.date_label}</p>
      <div className="sm:pl-8">
        <h3 className="text-xl leading-snug">{title}</h3>
        <p className="mt-2 text-[15.5px] leading-relaxed text-ink2">{pick({ vi: e.summary_vi, en: e.summary_en, zh: e.summary_vi })}</p>
        <p className="mt-2 text-xs text-earth">{t('tl_source')}: {e.source_title} — {e.printed_page != null ? `${t('chat_page')}${e.printed_page}` : e.provision}</p>
        <div className="mt-3 flex flex-wrap gap-2">
          <button className="btn" onClick={() => onOpen(i)}>{t('ev_open')}</button>
          <Link className="btn" to={`/chat?q=${encodeURIComponent(title)}`}>{t('tl_ask')}</Link>
        </div>
      </div>
      {e.images[0] ? (
        <button onClick={() => onOpen(i)} className="group block overflow-hidden bg-ink" aria-label={`${t('ev_open')}: ${title}`}>
          <img src={e.images[0].thumb_url} alt="" loading="lazy" className="archival h-36 w-full object-cover opacity-90 transition duration-500 group-hover:scale-105" />
        </button>
      ) : <span className="hidden sm:block" />}
    </li>
  )
}

export default function Timeline() {
  const { t } = useI18n()
  const [params] = useSearchParams()
  const [period, setPeriod] = useState(params.get('period') ?? '')
  const [open, setOpen] = useState<number | null>(null)
  const { data, error, loading, reload } = useAsync(() => api.timeline(period || undefined), [period])
  const tabs: [string, string][] = [['', t('tl_all')], ['pre-1954', t('tl_pre')], ['1954-1956', t('tl_p1')], ['1956-1967', t('tl_p2')]]
  const events = data?.items ?? []
  const groups = ['pre-1954', '1954-1956', '1956-1967'].map((p) => ({ p, items: events.map((e, i) => ({ e, i })).filter((x) => x.e.period === p) })).filter((g) => g.items.length)
  const meta: Record<string, [string, string]> = { 'pre-1954': [t('per_pre'), t('per_pre_desc')], '1954-1956': [t('per_p1'), t('per_p1_desc')], '1956-1967': [t('per_p2'), t('per_p2_desc')] }
  return (
    <div>
      <header className="relative left-1/2 -mt-8 mb-12 w-screen -translate-x-1/2 bg-ink py-16 text-white">
        <div className="mx-auto max-w-7xl px-5"><p className="eyebrow text-white/60">{t('tlp_eyebrow')}</p><h1 className="mt-3 text-5xl">{t('tl_title')}</h1>
          <p className="mt-4 max-w-2xl text-white/75">{t('tlp_title')}. {t('tl_intro')}</p>
          <div className="mt-8 flex flex-wrap gap-2" role="tablist">{tabs.map(([v, l]) => (
            <button key={v} role="tab" aria-selected={period === v} onClick={() => setPeriod(v)} className={`btn ${period === v ? 'btn-primary' : 'btn-ghost-light'}`}>{l}</button>))}</div></div>
      </header>
      {loading ? <Loading /> : error ? <ErrorBox message={error} onRetry={reload} /> : !events.length ? <EmptyState>{t('tl_empty')}</EmptyState> : (
        <div className="space-y-6">
          {groups.map((g) => (
            <section key={g.p} aria-labelledby={`per-${g.p}`}>
              <div className="mb-10 grid gap-2 border-b border-rule pb-6 sm:grid-cols-[150px_1fr] sm:gap-8">
                <p className="eyebrow pt-2 text-flag sm:text-right">{g.p === 'pre-1954' ? t('tl_pre') : g.p.replace('-', '–')}</p>
                <div className="sm:pl-8"><h2 id={`per-${g.p}`} className="text-3xl">{meta[g.p][0]}</h2><p className="mt-2 max-w-2xl text-ink2">{meta[g.p][1]}</p></div>
              </div>
              <ol className="relative border-l border-rule sm:border-l-0 sm:before:absolute sm:before:bottom-0 sm:before:left-[165px] sm:before:top-0 sm:before:w-px sm:before:bg-rule">
                {g.items.map(({ e, i }) => <Row key={e.event_id} e={e} i={i} onOpen={setOpen} />)}
              </ol>
            </section>
          ))}
        </div>
      )}
      {open !== null && <EventModal events={events} index={open} onIndex={setOpen} onClose={() => setOpen(null)} />}
    </div>
  )
}
