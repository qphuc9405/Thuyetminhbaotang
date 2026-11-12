import { useEffect, useRef, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { api, ApiError, type ChatResponse, type Lang } from '../api/client'
import AudioPlayer from '../components/AudioPlayer'
import ImageStrip from '../components/ImageStrip'
import RichAnswer from '../components/RichAnswer'
import Sources from '../components/Sources'
import { useI18n } from '../i18n'
import { THEMES } from '../lib/questions'
import { useSettings } from '../lib/settings'

interface Msg { id: number; role: 'user' | 'assistant'; text: string; resp?: ChatResponse; error?: string; question?: string }
let counter = 0
const sessionId = (() => { try { const k = sessionStorage.getItem('sid'); if (k) return k; const n = 's' + Math.random().toString(36).slice(2, 12); sessionStorage.setItem('sid', n); return n } catch { return 's' + Math.random().toString(36).slice(2, 12) } })()

function Answer({ m, voiceId }: { m: Msg & { resp: ChatResponse }; voiceId?: string }) {
  const { t } = useI18n()
  const r = m.resp
  const labels = new Set(r.sources.map((s) => s.label))
  return (
    <article className="border-l-2 border-flag bg-card px-5 py-6 sm:px-8" data-testid="assistant-message">
      <p className="eyebrow mb-3 text-flag">{t('chat_guide_name')}</p>
      <RichAnswer text={r.answer} labels={labels} msgId={m.id} />
      <div className="mt-4 flex flex-wrap gap-2 text-xs">
        <span className="tag">{t('chat_conf')}: {t('chat_conf_' + r.confidence)}</span>
        {r.insufficient_evidence && <span className="tag border-flag text-flag">{t('chat_insufficient')}</span>}
        {r.mode === 'extractive_fallback' && <span className="tag border-flag text-flag">{t('chat_fallback')}</span>}
      </div>
      {r.warnings.filter((w) => !w.startsWith('llm_error')).length > 0 && (
        <details className="mt-2 text-xs text-earth"><summary className="cursor-pointer">{t('chat_warn')}</summary><ul className="list-disc pl-5">{r.warnings.map((w) => <li key={w}>{w}</li>)}</ul></details>)}
      {!r.insufficient_evidence && <ImageStrip images={r.images} />}
      {r.sources.length > 0 && (
        <details className="mt-4 border-t border-rule pt-3" open={r.mode === 'extractive_fallback'}>
          <summary className="cursor-pointer text-sm font-medium text-earth">{t('chat_view_sources')} ({r.sources.length})</summary>
          <Sources sources={r.sources} idPrefix={`src-${m.id}`} />
        </details>
      )}
      {r.mode !== 'abstain' && (
        <div className="mt-4 flex flex-wrap items-start gap-3">
          <div className="min-w-[260px] flex-1"><AudioPlayer text={r.answer} language={r.language as Lang} voiceId={voiceId} /></div>
          <Link to="/timeline" className="btn">{t('chat_view_timeline')}</Link>
          <Link to="/gallery" className="btn">{t('chat_view_gallery')}</Link>
        </div>
      )}
    </article>
  )
}

export default function Chat() {
  const { t, lang } = useI18n()
  const { answerLang, voiceId } = useSettings()
  const [params, setParams] = useSearchParams()
  const [msgs, setMsgs] = useState<Msg[]>([])
  const [input, setInput] = useState(params.get('q') ?? '')
  const [loading, setLoading] = useState(false)
  const end = useRef<HTMLDivElement>(null)
  useEffect(() => { end.current?.scrollIntoView?.({ behavior: 'smooth', block: 'end' }) }, [msgs, loading])

  const send = async (q: string) => {
    const text = q.trim(); if (!text || loading) return
    setInput(''); if (params.get('q')) setParams({}, { replace: true })
    setMsgs((m) => [...m, { id: ++counter, role: 'user', text }]); setLoading(true)
    try {
      const resp = await api.chat(text, answerLang === 'auto' ? lang : answerLang, sessionId)
      setMsgs((m) => [...m, { id: ++counter, role: 'assistant', text: resp.answer, resp }])
    } catch (e) {
      setMsgs((m) => [...m, { id: ++counter, role: 'assistant', text: '', error: e instanceof ApiError ? e.message : String(e), question: text }])
    } finally { setLoading(false) }
  }

  return (
    <div className="grid gap-8 lg:grid-cols-[320px_1fr]">
      <aside className="lg:sticky lg:top-20 lg:self-start" aria-label={t('chat_guide_title')}>
        <p className="eyebrow">{t('guide_eyebrow')}</p>
        <h1 className="mt-2 text-3xl leading-tight">{t('chat_guide_title')}</h1>
        <p className="mt-3 text-sm leading-relaxed text-ink2">{t('chat_guide_intro')}</p>
        <h2 className="eyebrow mt-8">{t('chat_themes')}</h2>
        <div className="mt-3 space-y-5">
          {THEMES.map((th) => (
            <div key={th.key}>
              <p className="font-serif text-base text-flag">{th.label[lang]}</p>
              <ul className="mt-1 space-y-1">{th.q[lang].map((q) => (
                <li key={q}><button className="w-full border-b border-rule py-1.5 text-left text-sm text-ink2 hover:text-flag disabled:opacity-50" disabled={loading} onClick={() => send(q)}>{q}</button></li>))}</ul>
            </div>
          ))}
        </div>
      </aside>
      <section className="min-w-0">
        <div className="mb-4 flex items-center justify-between"><h2 className="sr-only">{t('nav_chat')}</h2>
          {msgs.length > 0 && <button className="btn ml-auto" onClick={() => setMsgs([])}>{t('chat_clear')}</button>}</div>
        <div className="space-y-6" aria-live="polite">
          {msgs.length === 0 && !loading && (
            <div className="border border-dashed border-rule p-8 text-center"><p className="font-serif text-2xl text-ink2">{t('guide_title')}</p><p className="mt-2 text-sm text-earth">{t('chat_empty')}</p></div>
          )}
          {msgs.map((m) => m.role === 'user' ? (
            <div key={m.id} className="ml-auto max-w-[85%] bg-ink px-5 py-3 font-serif text-[17px] text-white">{m.text}</div>
          ) : m.error ? (
            <div key={m.id} role="alert" className="border-l-2 border-flag bg-[#f6e3df] p-4 text-flag"><p className="font-medium">{t('chat_error')}</p><p className="text-sm">{m.error}</p>
              <button className="btn mt-2" onClick={() => send(m.question!)}>{t('chat_retry')}</button></div>
          ) : m.resp ? <Answer key={m.id} m={m as Msg & { resp: ChatResponse }} voiceId={voiceId} /> : null)}
          {loading && <div role="status" className="flex items-center gap-3 border-l-2 border-rule bg-card px-5 py-4 text-earth"><span className="flex gap-1"><span className="h-1.5 w-1.5 animate-pulse rounded-full bg-flag" /><span className="h-1.5 w-1.5 animate-pulse rounded-full bg-flag [animation-delay:.2s]" /><span className="h-1.5 w-1.5 animate-pulse rounded-full bg-flag [animation-delay:.4s]" /></span>{t('chat_thinking')}</div>}
          <div ref={end} />
        </div>
        <form className="sticky bottom-3 mt-6 flex gap-2 border border-rule bg-card p-2 shadow-lg" onSubmit={(e) => { e.preventDefault(); void send(input) }}>
          <label className="sr-only" htmlFor="q">{t('nav_chat')}</label>
          <input id="q" className="min-w-0 flex-1 bg-paper px-3 py-2.5 outline-none" value={input} maxLength={800} onChange={(e) => setInput(e.target.value)} placeholder={t('chat_placeholder')} />
          <button className="btn btn-primary" disabled={loading || !input.trim()} type="submit">{t('chat_send')}</button>
        </form>
      </section>
    </div>
  )
}
