import { useEffect, useMemo, useState } from 'react';
import { Loader2, Pause, Play, Volume2, VolumeX } from 'lucide-react';
import { cps, getAudio, setMuted, speak, subscribe, toggle, type AudioState } from './audio';
import { useLang, useT } from './i18n';

export function useAudio(): AudioState {
  const [s, setS] = useState(getAudio);
  useEffect(() => subscribe(setS), []);
  return s;
}

const fmt = (s: number) => `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(Math.floor(s % 60)).padStart(2, '0')}`;

/** Thanh thuyết minh: giọng ElevenLabs (qua museum-guide), lùi về giọng trình duyệt khi không có. */
export default function NarrationBar({ id, text, voiceId, autoPlay = true, compact = false }: {
  id: string; text: string; voiceId?: string; autoPlay?: boolean; compact?: boolean;
}) {
  const lang = useLang();
  const t = useT();
  const a = useAudio();
  const key = `${id}|${lang}`;
  const mine = a.key === key;
  const status = mine ? a.status : 'idle';
  const pos = mine ? a.pos : 0;
  const total = mine && a.dur ? a.dur : Math.max(1, text.length / cps(lang));
  const bars = useMemo(() => Array.from({ length: 48 }, (_, i) => 0.25 + 0.75 * Math.abs(Math.sin(i * 1.7) * Math.cos(i * 0.6))), []);

  useEffect(() => {
    if (autoPlay && text && !getAudio().muted) void speak(key, text, lang, voiceId);
    // Không dừng âm thanh khi unmount ở đây: lối thoát khu vực gọi stopAll() tập trung,
    // còn đổi hiện vật thì speak() mới tự dừng tiếng cũ.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key, text]);

  const playing = status === 'playing';
  const loading = status === 'loading';
  return (
    <div className={`narration-bar ${compact ? 'compact' : ''}`} data-state={status}
      title={mine && a.engine === 'browser' && a.fallback ? t('browserVoice') : mine && a.blocked ? t('tapToPlay') : undefined}>
      <button className="narration-play" onClick={() => toggle(key, text, lang, voiceId)} aria-label={playing || loading ? t('pause') : t('play')} title={playing || loading ? t('pause') : t('play')}>
        {loading ? <Loader2 size={20} className="spin" /> : playing ? <Pause size={20} fill="currentColor" /> : <Play size={20} fill="currentColor" />}
      </button>
      <div className="narration-wave" aria-hidden="true">
        {bars.map((h, i) => <i key={i} style={{ height: `${h * 100}%`, animationDelay: `${(i % 9) * 70}ms` }} className={i / bars.length <= pos ? 'done' : ''} />)}
      </div>
      <span className="narration-time">{fmt(pos * total)} / {fmt(total)}</span>
      <button className="narration-mute" onClick={() => setMuted(!a.muted)} aria-label={a.muted ? t('soundOff') : t('soundOn')} title={a.muted ? t('soundOff') : t('soundOn')}>
        {a.muted ? <VolumeX size={20} /> : <Volume2 size={20} />}
      </button>
      {mine && loading && <small className="narration-note">{t('narrationLoading')}</small>}
      {mine && a.blocked && <small className="narration-note">{t('tapToPlay')}</small>}
      {mine && a.engine === 'browser' && a.fallback && <small className="narration-note subtle">{t('browserVoice')}</small>}
    </div>
  );
}
