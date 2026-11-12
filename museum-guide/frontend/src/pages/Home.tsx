import { useRef, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api, type ImageItem, type StoryChapter, type TimelineEvent } from '../api/client'
import EventModal from '../components/EventModal'
import { ErrorBox, Loading } from '../components/StateViews'
import { useI18n } from '../i18n'
import { THEMES } from '../lib/questions'
import { useAsync } from '../lib/useAsync'
import { useReveal } from '../lib/useReveal'

// Giữ để tương thích (Chat dùng lại khi chưa có câu hỏi)
export const EXAMPLES: Record<string, string[]> = {
  vi: THEMES.map((x) => x.q.vi[0]), en: THEMES.map((x) => x.q.en[0]), zh: THEMES.map((x) => x.q.zh[0]),
}

// Ảnh được chọn có chủ đích cho phòng trưng bày trang chủ (ưu tiên ảnh độ tin cậy cao, đa dạng chủ đề; mỗi bức một bản)
const FEATURED = ['IMG004', 'BKFIG11', 'IMG007', 'IMG014', 'IMG015', 'IMG024', 'IMG030', 'BKFIG10', 'BKFIG02']

function Hero() {
  const { t } = useI18n()
  return (
    <section className="relative flex min-h-[100svh] items-end overflow-hidden bg-ink text-white" aria-label={t('hero_title')}>
      <img src="/api/images/IMG034/file" alt={t('hero_photo')} className="archival absolute inset-0 h-full w-full object-cover opacity-70 animate-kenburns" />
      <div className="absolute inset-0 bg-gradient-to-t from-ink via-ink/55 to-ink/20" />
      <div className="absolute inset-y-0 left-0 w-full bg-gradient-to-r from-ink/80 via-ink/30 to-transparent" />
      <div className="relative mx-auto w-full max-w-7xl px-5 pb-16 pt-32 sm:pb-24">
        <p className="eyebrow animate-rise text-white/70" style={{ animationDelay: '.1s' }}>{t('hero_eyebrow')}</p>
        <h1 className="mt-4 animate-rise font-serif text-[clamp(3rem,9vw,7.5rem)] font-normal leading-[0.95]" style={{ animationDelay: '.25s' }}>{t('hero_title')}</h1>
        <p className="mt-5 animate-rise font-serif text-[clamp(1.25rem,2.6vw,2rem)] italic text-white/90" style={{ animationDelay: '.45s' }}>{t('hero_tagline')}</p>
        <div className="mt-6 flex animate-rise items-center gap-4" style={{ animationDelay: '.6s' }}>
          <span className="h-px w-16 bg-flag" /><span className="font-serif text-2xl tracking-[0.2em]">1954 – 1967</span>
        </div>
        <p className="mt-6 max-w-xl animate-rise text-[17px] leading-relaxed text-white/80" style={{ animationDelay: '.75s' }}>{t('hero_sub')}</p>
        <div className="mt-8 flex animate-rise flex-wrap gap-3" style={{ animationDelay: '.9s' }}>
          <a href="#story" className="btn btn-primary px-6 py-3 text-[15px]">{t('hero_start')} ↓</a>
          <Link to="/chat" className="btn btn-ghost-light px-6 py-3 text-[15px]">{t('hero_ask')}</Link>
        </div>
        <p className="mt-10 max-w-md text-[11px] text-white/50">{t('hero_photo')}</p>
      </div>
    </section>
  )
}

function Chapter({ ch, i }: { ch: StoryChapter; i: number }) {
  const { t, lang, pick } = useI18n()
  const ref = useReveal<HTMLElement>()
  const flip = i % 2 === 1
  const img = ch.image
  const ask = THEMES.find((x) => x.key === ['geneva', 'bridge', 'life', 'story'][i])?.q[lang][0]
  return (
    <article ref={ref} className="reveal grid items-center gap-8 py-14 md:grid-cols-12 md:gap-12 md:py-20" data-testid="story-chapter">
      <figure className={`md:col-span-6 ${flip ? 'md:order-2' : ''}`}>
        {img && <img src={img.medium_url} alt={pick({ vi: img.title, en: img.title_en, zh: img.title_zh })} loading="lazy" className="archival aspect-[4/3] w-full object-cover shadow-[0_20px_50px_-20px_rgba(28,25,21,.55)]" />}
        {img && <figcaption className="mt-3 text-xs text-earth">{pick({ vi: img.title, en: img.title_en, zh: img.title_zh })}{img.printed_page ? ` · ${t('chat_page')}${img.printed_page}` : ''} · <Link className="underline" to={`/gallery/${img.image_id}`}>{img.image_id}</Link></figcaption>}
      </figure>
      <div className={`md:col-span-6 ${flip ? 'md:order-1' : ''}`}>
        <div className="flex items-baseline gap-4">
          <span className="font-serif text-6xl leading-none text-flag/90">{String(i + 1).padStart(2, '0')}</span>
          <span className="eyebrow">{lang === 'zh' ? `${t('story_chapter')}${i + 1}章` : `${t('story_chapter')} ${i + 1}`} · {ch.period}</span>
        </div>
        <h3 className="mt-4 text-3xl leading-tight sm:text-4xl">{ch.title[lang]}</h3>
        <p className="mt-5 font-serif text-xl italic leading-relaxed text-ink2">{ch.lead[lang]}</p>
        <div className="mt-5 space-y-4 text-[16.5px] leading-[1.8] text-ink2">{ch.body[lang].map((p, k) => <p key={k}>{p}</p>)}</div>
        <p className="mt-5 text-xs text-earth">
          <span className="font-semibold">{t('story_sources')}:</span>{' '}
          {ch.citations.map((c, k) => <span key={k}>{k ? ' · ' : ''}{c.source_type === 'BOOK' ? `${t('chat_book')} ${t('chat_page')}${c.printed_page}` : `${c.source_id} ${c.provision}`}</span>)}
        </p>
        <div className="mt-6 flex flex-wrap gap-2">
          <Link className="btn" to={`/topics/${ch.topic_id}`}>{t('story_more')}</Link>
          <Link className="btn" to={`/timeline?period=${ch.timeline_period}`}>{t('story_timeline')}</Link>
          {ask && <Link className="btn btn-primary" to={`/chat?q=${encodeURIComponent(ask)}`}>{t('story_ask')}</Link>}
        </div>
      </div>
    </article>
  )
}

function TimelinePreview() {
  const { t, pick } = useI18n()
  const { data, error, loading, reload } = useAsync(() => api.timeline(), [])
  const [open, setOpen] = useState<number | null>(null)
  const rail = useRef<HTMLDivElement>(null)
  const events: TimelineEvent[] = (data?.items ?? []).filter((e) => e.date_iso >= '1954')
  const scroll = (d: number) => rail.current?.scrollBy?.({ left: d * 340, behavior: 'smooth' })
  return (
    <section className="bg-ink py-20 text-white" aria-labelledby="tlp">
      <div className="mx-auto max-w-7xl px-5">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div><p className="eyebrow text-white/60">{t('tlp_eyebrow')}</p><h2 id="tlp" className="mt-3 text-4xl">{t('tlp_title')}</h2><p className="mt-2 text-sm text-white/60">{t('tlp_hint')}</p></div>
          <div className="flex gap-2">
            <button className="btn btn-ghost-light" onClick={() => scroll(-1)} aria-label={t('tlp_prev')}>←</button>
            <button className="btn btn-ghost-light" onClick={() => scroll(1)} aria-label={t('tlp_next')}>→</button>
            <Link to="/timeline" className="btn btn-primary">{t('tlp_all')}</Link>
          </div>
        </div>
      </div>
      {loading ? <div className="px-5"><Loading /></div> : error ? <div className="mx-auto max-w-7xl px-5"><ErrorBox message={error} onRetry={reload} /></div> : (
        <div ref={rail} className="no-scrollbar mt-10 flex snap-x snap-mandatory gap-5 overflow-x-auto px-5 pb-4 md:px-[max(1.25rem,calc((100vw-80rem)/2+1.25rem))]" data-testid="timeline-rail">
          {events.map((e, i) => {
            const newPeriod = i === 0 || events[i - 1].period !== e.period
            return (
              <div key={e.event_id} className="flex snap-start items-stretch">
                {newPeriod && <div className="mr-5 flex w-40 shrink-0 flex-col justify-end border-l-2 border-flag pl-4"><p className="eyebrow text-flag">{e.period.replace('-', '–')}</p><p className="mt-2 font-serif text-xl leading-snug">{e.period === '1954-1956' ? t('per_p1') : t('per_p2')}</p></div>}
                <button onClick={() => setOpen(i)} className="group w-72 shrink-0 border-t border-white/20 pt-4 text-left">
                  <span className="font-serif text-3xl text-white">{e.date_label}</span>
                  <div className="mt-3 h-40 overflow-hidden bg-white/5">{e.images[0] ? <img src={e.images[0].thumb_url} alt="" loading="lazy" className="archival h-full w-full object-cover opacity-80 transition duration-500 group-hover:scale-105 group-hover:opacity-100" /> : <div className="flex h-full items-center justify-center font-serif text-5xl text-white/10">{e.date_iso.slice(0, 4)}</div>}</div>
                  <p className="mt-3 font-serif text-lg leading-snug text-white group-hover:text-[#f3c9a8]">{pick({ vi: e.title_vi, en: e.title_en, zh: e.title_zh })}</p>
                  <p className="mt-2 line-clamp-3 text-sm text-white/60">{pick({ vi: e.summary_vi, en: e.summary_en, zh: e.summary_vi })}</p>
                </button>
              </div>
            )
          })}
        </div>
      )}
      {open !== null && <EventModal events={events} index={open} onIndex={setOpen} onClose={() => setOpen(null)} />}
    </section>
  )
}

function Anecdotes() {
  const { t, lang, pick } = useI18n()
  const ref = useReveal<HTMLElement>()
  const { data, error, loading, reload } = useAsync(() => api.anecdotes(), [])
  const items = (data?.items ?? []).slice(0, 6)
  return (
    <section ref={ref} className="reveal mx-auto max-w-7xl px-5 py-20" aria-labelledby="anec">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div className="max-w-2xl"><p className="eyebrow">{t('an_eyebrow')}</p><h2 id="anec" className="mt-3 text-4xl leading-tight">{t('an_title')}</h2><p className="mt-3 text-ink2">{t('an_intro')}</p></div>
        <Link to="/stories" className="btn btn-primary">{t('an_all')} →</Link>
      </div>
      {loading ? <Loading /> : error ? <ErrorBox message={error} onRetry={reload} /> : (
        <div className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-3" data-testid="anecdote-grid">
          {items.map((a, i) => {
            const im = a.images[0]
            return (
              <Link key={a.id} to={`/stories#${a.id}`} className="group block border-t-2 border-ink pt-4">
                <div className="h-48 overflow-hidden bg-ink">{im && <img src={im.medium_url} alt={pick({ vi: im.title, en: im.title_en, zh: im.title_zh })} loading="lazy" className="archival h-full w-full object-cover opacity-90 transition duration-700 group-hover:scale-[1.03] group-hover:opacity-100" />}</div>
                <p className="mt-4 eyebrow">{String(i + 1).padStart(2, '0')} · {a.period}</p>
                <h3 className="mt-2 font-serif text-2xl leading-snug group-hover:text-flag">{a.title[lang]}</h3>
                <p className="mt-2 text-[15px] leading-relaxed text-ink2">{a.teaser[lang]}</p>
                <span className="mt-3 inline-block text-sm text-flag underline-offset-4 group-hover:underline">{t('an_read')} →</span>
              </Link>
            )
          })}
        </div>
      )}
    </section>
  )
}

function Collection() {
  const { t, pick } = useI18n()
  const ref = useReveal<HTMLElement>()
  const { data } = useAsync(() => api.images({ limit: 200 }), [])
  const items = FEATURED.map((id) => data?.items.find((x) => x.image_id === id)).filter(Boolean) as ImageItem[]
  return (
    <section ref={ref} className="reveal mx-auto max-w-7xl px-5 py-20" aria-labelledby="col">
      <div className="grid gap-6 md:grid-cols-12">
        <div className="md:col-span-4"><p className="eyebrow">{t('col_eyebrow')}</p><h2 id="col" className="mt-3 text-4xl leading-tight">{t('col_title')}</h2>
          <p className="mt-4 text-ink2">{t('col_intro')}</p><Link to="/gallery" className="btn btn-primary mt-6">{t('col_all')} →</Link></div>
        <div className="grid grid-cols-2 gap-3 md:col-span-8 md:grid-cols-3" data-testid="collection-grid">
          {items.map((im, i) => (
            <Link key={im.image_id} to={`/gallery/${im.image_id}`} className={`group relative block overflow-hidden bg-ink ${i === 0 ? 'col-span-2 row-span-2' : ''}`}>
              <img src={`/api/images/${im.image_id}/file?size=medium`} alt={pick({ vi: im.title, en: im.title_en, zh: im.title_zh })} loading="lazy" className={`archival w-full object-cover opacity-90 transition duration-700 group-hover:scale-[1.03] group-hover:opacity-100 ${i === 0 ? 'h-full min-h-[18rem]' : 'h-44'}`} />
              <span className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-ink/90 to-transparent p-3 pt-10 text-left text-xs leading-snug text-white">{pick({ vi: im.title, en: im.title_en, zh: im.title_zh })}</span>
            </Link>
          ))}
        </div>
      </div>
    </section>
  )
}

function Guide() {
  const { t, lang } = useI18n()
  const nav = useNavigate()
  const ref = useReveal<HTMLElement>()
  return (
    <section ref={ref} className="reveal bg-river text-white" aria-labelledby="guide">
      <div className="mx-auto grid max-w-7xl gap-10 px-5 py-20 md:grid-cols-2">
        <div><p className="eyebrow text-white/60">{t('guide_eyebrow')}</p><h2 id="guide" className="mt-3 text-4xl leading-tight">{t('guide_title')}</h2>
          <p className="mt-5 text-lg text-white/80">{t('guide_body')}</p><Link to="/chat" className="btn btn-primary mt-8 px-6 py-3">{t('guide_start')} →</Link></div>
        <div>
          <p className="eyebrow text-white/60">{t('guide_you_can')}</p>
          <ul className="mt-4 divide-y divide-white/15 border-y border-white/15">
            {THEMES.map((th) => (
              <li key={th.key}><button onClick={() => nav(`/chat?q=${encodeURIComponent(th.q[lang][0])}`)} className="flex w-full items-baseline justify-between gap-4 py-4 text-left hover:text-[#f3c9a8]">
                <span><span className="block text-xs uppercase tracking-widest text-white/50">{th.label[lang]}</span><span className="font-serif text-lg">{th.q[lang][0]}</span></span><span aria-hidden>→</span></button></li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  )
}

export default function Home() {
  const { t } = useI18n()
  const story = useAsync(() => api.story(), [])
  return (
    <div>
      <Hero />
      <section id="story" className="mx-auto max-w-7xl scroll-mt-16 px-5 pt-20" aria-labelledby="story-title">
        <p className="eyebrow">{t('story_eyebrow')}</p>
        <h2 id="story-title" className="mt-3 max-w-3xl text-4xl leading-tight sm:text-5xl">{t('story_title')}</h2>
        <p className="mt-4 max-w-2xl text-ink2">{t('story_intro')}</p>
        {story.loading ? <Loading /> : story.error ? <ErrorBox message={story.error} onRetry={story.reload} /> : (
          <div className="divide-y divide-rule">{story.data?.chapters.map((ch, i) => <Chapter key={ch.id} ch={ch} i={i} />)}</div>
        )}
        <p className="pb-6 text-xs italic text-earth">{t('story_note')}</p>
      </section>
      <TimelinePreview />
      <Anecdotes />
      <Collection />
      <Guide />
    </div>
  )
}
