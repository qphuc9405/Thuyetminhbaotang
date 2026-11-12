import { useEffect, useRef, useState } from 'react'
import { api, ApiError, type Lang } from '../api/client'
import { useI18n } from '../i18n'

type State = 'idle' | 'loading' | 'ready' | 'error'
const fmt = (s: number) => (isFinite(s) ? `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, '0')}` : '0:00')

/** Trình phát thuyết minh: tạo audio qua /api/narration/generate (có cache ở backend), Play/Pause, tiến trình, dừng, phát lại. */
export default function AudioPlayer({ text, language, voiceId }: { text: string; language: Lang; voiceId?: string }) {
  const { t } = useI18n()
  const audio = useRef<HTMLAudioElement | null>(null)
  const [state, setState] = useState<State>('idle')
  const [src, setSrc] = useState<string | null>(null)
  const [playing, setPlaying] = useState(false)
  const [cur, setCur] = useState(0)
  const [dur, setDur] = useState(0)
  const [err, setErr] = useState('')

  useEffect(() => { setState('idle'); setSrc(null); setPlaying(false); setCur(0) }, [text, language, voiceId])

  const ensure = async (): Promise<string | null> => {
    if (src) return src
    setState('loading'); setErr('')
    try {
      const n = await api.narrate(text, language, voiceId || undefined)
      setSrc(n.audio_url); setState('ready'); return n.audio_url
    } catch (e) {
      setState('error'); setErr(e instanceof ApiError ? e.message : String(e)); return null
    }
  }
  const play = async () => {
    const u = await ensure(); if (!u) return
    const a = audio.current; if (!a) return
    if (a.getAttribute('src') !== u) a.setAttribute('src', u)
    try { await a.play(); setPlaying(true) } catch { setState('error'); setErr(t('audio_error')) }
  }
  const pause = () => { audio.current?.pause(); setPlaying(false) }
  const stop = () => { const a = audio.current; if (a) { a.pause(); a.currentTime = 0 } setPlaying(false); setCur(0) }
  const replay = async () => { const a = audio.current; if (a && src) { a.currentTime = 0; try { await a.play(); setPlaying(true) } catch { /* bỏ qua */ } } else await play() }

  return (
    <div className="rounded border border-rule bg-paper p-2 text-sm" data-testid="audio-player">
      <div className="flex flex-wrap items-center gap-2">
        {playing
          ? <button className="btn" onClick={pause} aria-label={t('audio_pause')}>⏸ {t('audio_pause')}</button>
          : <button className="btn btn-primary" onClick={play} disabled={state === 'loading'} aria-label={t('audio_play')}>▶ {t('chat_listen')}</button>}
        <button className="btn" onClick={stop} disabled={state !== 'ready'} aria-label={t('audio_stop')}>⏹ {t('audio_stop')}</button>
        <button className="btn" onClick={replay} disabled={state !== 'ready'} aria-label={t('audio_replay')}>↺ {t('audio_replay')}</button>
        <input type="range" min={0} max={dur || 1} step={0.1} value={cur} aria-label="progress" disabled={state !== 'ready'} className="min-w-[120px] flex-1"
          onChange={(e) => { const a = audio.current; if (a) { a.currentTime = Number(e.target.value); setCur(Number(e.target.value)) } }} />
        <span className="tabular-nums text-xs text-sepia">{fmt(cur)} / {fmt(dur)}</span>
      </div>
      {state === 'loading' && <p role="status" className="mt-1 text-sepia">{t('audio_loading')}</p>}
      {state === 'error' && <p role="alert" className="mt-1 text-oxblood">{t('audio_error')} — {err}</p>}
      <details className="mt-1 text-xs text-sepia"><summary>{t('audio_text')}</summary><p className="mt-1 whitespace-pre-wrap">{text.replace(/\[(S|I)\d+\]/g, '')}</p></details>
      <audio ref={audio} onTimeUpdate={(e) => setCur(e.currentTarget.currentTime)} onLoadedMetadata={(e) => setDur(e.currentTarget.duration)}
        onEnded={() => { setPlaying(false); setCur(0) }} onPause={() => setPlaying(false)} onPlay={() => setPlaying(true)} preload="none" />
    </div>
  )
}
