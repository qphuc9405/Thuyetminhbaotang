import { useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { api, type Anecdote, type AnecdoteCitation } from '../api/client'
import { ErrorBox, Loading } from '../components/StateViews'
import { useI18n } from '../i18n'
import { useAsync } from '../lib/useAsync'
import { useReveal } from '../lib/useReveal'

export function citeLabel(c: AnecdoteCitation, t: (k: string) => string): string {
  if (c.source_type === 'BOOK') return `${t('chat_book')} ${t('chat_page')}${c.printed_page}`
  if (c.source_type === 'WEB_ARTICLE') return c.provision || c.source_id
  return `${c.source_id} · ${c.provision ?? ''}`
}

function uniqueCites(cs: AnecdoteCitation[]): AnecdoteCitation[] {
  const seen = new Set<string>()
  return cs.filter((c) => { const k = `${c.source_id}|${c.printed_page}|${c.provision}`; if (seen.has(k)) return false; seen.add(k); return true })
}

function Story({ a, i }: { a: Anecdote; i: number }) {
  const { t, lang, pick } = useI18n()
  const ref = useReveal<HTMLElement>()
  const [main, ...rest] = a.images
  const flip = i % 2 === 1
  return (
    <article ref={ref} id={a.id} className="reveal grid scroll-mt-20 gap-8 py-14 md:grid-cols-12 md:gap-12" data-testid="anecdote">
      <figure className={`md:col-span-5 ${flip ? 'md:order-2' : ''}`}>
        {main && (
          <Link to={`/gallery/${main.image_id}`} className="block overflow-hidden bg-ink">
            <img src={main.medium_url} alt={pick({ vi: main.title, en: main.title_en, zh: main.title_zh })} loading="lazy" className="archival aspect-[4/3] w-full object-cover transition duration-700 hover:scale-[1.02]" />
          </Link>
        )}
        {main && <figcaption className="mt-2 text-xs text-earth">{pick({ vi: main.title, en: main.title_en, zh: main.title_zh })} · {main.image_id}</figcaption>}
        {rest.length > 0 && (
          <div className="mt-3 grid grid-cols-3 gap-2">
            {rest.map((im) => (
              <Link key={im.image_id} to={`/gallery/${im.image_id}`} className="block overflow-hidden bg-ink" title={pick({ vi: im.title, en: im.title_en, zh: im.title_zh })}>
                <img src={im.thumb_url} alt={pick({ vi: im.title, en: im.title_en, zh: im.title_zh })} loading="lazy" className="archival h-20 w-full object-cover opacity-90 hover:opacity-100" />
              </Link>
            ))}
          </div>
        )}
      </figure>
      <div className={`md:col-span-7 ${flip ? 'md:order-1' : ''}`}>
        <div className="flex items-baseline gap-4">
          <span className="font-serif text-5xl leading-none text-flag/90">{String(i + 1).padStart(2, '0')}</span>
          <span className="eyebrow">{a.period}</span>
        </div>
        <h2 className="mt-3 text-3xl leading-tight sm:text-4xl">{a.title[lang]}</h2>
        <p className="mt-4 font-serif text-xl italic leading-relaxed text-ink2">{a.teaser[lang]}</p>
        <div className="mt-5 space-y-4 text-[16.5px] leading-[1.8] text-ink2">{a.body[lang].map((p, k) => <p key={k}>{p}</p>)}</div>
        {a.notes_detail.length > 0 && (
          <aside className="mt-6 border-l-2 border-flag bg-card px-4 py-3 text-sm" aria-label={t('an_notes')}>
            <p className="font-semibold text-flag">{t('an_notes')}</p>
            <ul className="mt-1 list-disc pl-5 text-ink2">{a.notes_detail.map((n) => <li key={n.chunk_id}>{n.title.replace(/^Đối chiếu nguồn:\s*/, '')} <span className="text-xs text-earth">({n.chunk_id})</span></li>)}</ul>
          </aside>
        )}
        <p className="mt-5 text-xs leading-relaxed text-earth" data-testid="anecdote-sources">
          <span className="font-semibold">{t('an_sources')}:</span>{' '}
          {uniqueCites(a.citations).map((c, k) => (
            <span key={k}>{k ? ' · ' : ''}{c.url ? <a className="underline" href={c.url} target="_blank" rel="noreferrer" title={c.source_title}>{citeLabel(c, t)}</a> : <span title={c.source_title}>{citeLabel(c, t)}</span>}</span>
          ))}
        </p>
        <div className="mt-6 flex flex-wrap gap-2">
          <Link className="btn btn-primary" to={`/chat?q=${encodeURIComponent(a.title[lang])}`}>{t('an_ask')}</Link>
          <Link className="btn" to={`/topics/${a.topic_id}`}>{t('story_more')}</Link>
        </div>
      </div>
    </article>
  )
}

export default function Stories() {
  const { t, lang } = useI18n()
  const { data, error, loading, reload } = useAsync(() => api.anecdotes(), [])
  const loc = useLocation()
  useEffect(() => {
    if (data && loc.hash) document.getElementById(decodeURIComponent(loc.hash.slice(1)))?.scrollIntoView?.({ behavior: 'smooth', block: 'start' })
  }, [data, loc.hash])
  return (
    <div className="mx-auto max-w-7xl px-5 pt-10">
      <p className="eyebrow">{t('an_eyebrow')}</p>
      <h1 className="mt-3 max-w-3xl text-4xl leading-tight sm:text-5xl">{t('an_title')}</h1>
      <p className="mt-4 max-w-2xl text-ink2">{t('an_intro')}</p>
      {loading ? <Loading /> : error ? <ErrorBox message={error} onRetry={reload} /> : (
        <>
          <nav className="mt-8 flex flex-wrap gap-2" aria-label={t('an_title')}>
            {data?.items.map((a, i) => <a key={a.id} href={`#${a.id}`} className="tag hover:border-flag hover:text-flag">{String(i + 1).padStart(2, '0')} · {a.title[lang]}</a>)}
          </nav>
          <div className="divide-y divide-rule">{data?.items.map((a, i) => <Story key={a.id} a={a} i={i} />)}</div>
        </>
      )}
      <p className="pb-10 text-xs italic text-earth">{t('an_note')}</p>
    </div>
  )
}
