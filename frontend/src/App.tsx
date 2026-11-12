import { useCallback, useEffect, useRef, useState } from 'react';
import { BookOpen, Check, ChevronRight, Copy, Globe2, Image as ImageIcon, MapPin, Maximize, Minimize, Share2, Volume2, VolumeX, X } from 'lucide-react';
import { zones, type Zone, type ZoneId } from './data';
import { mediaByZone } from './media';
import { narrators } from './guides';
import MuseumTopics from './Museum';
import { MapCamera } from './MapCamera';
import { useZoneNavigation } from './useZoneNavigation';
import { suggestedQuestions } from './suggestedQuestions';
import { PlaceView, StoryZoneView } from './Zones';
import ChatDock, { type Talk } from './ChatDock';
import { NarratorGuide } from './Guide';
import { PhotosModal, StoriesModal } from './common';
import { useAudio } from './Narration';
import { playFile, setMuted, speak, stopAll } from './audio';
import { mgChat } from './mg';
import { LangContext, LANGS, tr, ZONE_TEXT, type Lang } from './i18n';

const sessionId = `tm-${Math.random().toString(36).slice(2, 10)}`;
const homeAudioSource = '/audio/home-introduction.mp3';

const savedLang = (): Lang => {
  try { const v = localStorage.getItem('tm-lang'); if (v === 'vi' || v === 'en' || v === 'zh') return v; } catch { /* storage có thể bị chặn */ }
  return 'vi';
};

export default function App() {
  const [homePanel, setHomePanel] = useState<'none' | 'photos' | 'stories'>('none');
  const [lang, setLangState] = useState<Lang>(savedLang);
  const [langMenu, setLangMenu] = useState(false);
  const [fullscreen, setFullscreen] = useState(false);
  const [copied, setCopied] = useState(false);
  const [sharing, setSharing] = useState(false);
  const [talks, setTalks] = useState<Talk[]>([]);
  const [chatBusy, setChatBusy] = useState(false);
  const [query, setQuery] = useState('');
  const [notice, setNotice] = useState('');
  const audio = useAudio();
  const { active, openZone, backHome, mapRef, navigation, busy } = useZoneNavigation<Zone>(zones, {
    onStart: () => resetLocation(),
    onNavigate: () => { resetLocation(); setHomePanel('none'); setNotice(''); },
  });
  const chatRequest = useRef<AbortController | null>(null);
  const copyTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const t = useCallback((k: Parameters<typeof tr>[1], v?: Record<string, string | number>) => tr(lang, k, v), [lang]);

  useEffect(() => { document.documentElement.lang = lang === 'zh' ? 'zh-CN' : lang; }, [lang]);

  /** Rời một khu vực (bất kỳ đường nào): tắt âm thanh, huỷ chat đang chờ, xoá hội thoại. */
  const resetLocation = () => {
    stopAll();
    chatRequest.current?.abort();
    chatRequest.current = null;
    setChatBusy(false);
    setTalks([]);
    setQuery('');
  };

  const setLang = (next: Lang) => {
    setLangMenu(false);
    if (next === lang) return;
    stopAll(); // giọng đang đọc là ngôn ngữ cũ
    setLangState(next);
    try { localStorage.setItem('tm-lang', next); } catch { /* ignore */ }
    setNotice(tr(next, 'langChanged'));
  };

  const playHomeNarration = () => {
    if (lang === 'vi') playFile('home-intro|vi', homeAudioSource);
    else void speak(`home-intro|${lang}`, tr(lang, 'homeIntroText'), lang, narrators.home.voice);
  };

  useEffect(() => () => { stopAll(); chatRequest.current?.abort(); if (copyTimer.current) clearTimeout(copyTimer.current); }, []);

  useEffect(() => {
    if (!langMenu) return;
    const close = (e: MouseEvent) => { if (!(e.target as HTMLElement).closest?.('.lang-switch')) setLangMenu(false); };
    const esc = (e: KeyboardEvent) => { if (e.key === 'Escape') setLangMenu(false); };
    window.addEventListener('mousedown', close); window.addEventListener('keydown', esc);
    return () => { window.removeEventListener('mousedown', close); window.removeEventListener('keydown', esc); };
  }, [langMenu]);

  useEffect(() => {
    if (!notice) return;
    const id = setTimeout(() => setNotice(''), 3200);
    return () => clearTimeout(id);
  }, [notice]);

  useEffect(() => {
    const sync = () => setFullscreen(!!document.fullscreenElement);
    sync();
    document.addEventListener('fullscreenchange', sync);
    return () => document.removeEventListener('fullscreenchange', sync);
  }, []);

  const toggleFullscreen = async () => {
    try {
      if (document.fullscreenElement) await document.exitFullscreen();
      else await document.documentElement.requestFullscreen();
    } catch { setNotice(t('fullscreenFail')); }
  };

  const share = async () => {
    if (sharing) return;
    setSharing(true);
    try {
      if (navigator.share) await navigator.share({ title: active ? ZONE_TEXT[active.id].title[lang] : t('homeTitle'), url: location.href });
      else { await navigator.clipboard.writeText(location.href); setNotice(t('copied')); }
    } catch { /* người dùng huỷ */ } finally { setSharing(false); }
  };

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(location.href);
      setCopied(true); setNotice(t('copied'));
      if (copyTimer.current) clearTimeout(copyTimer.current);
      copyTimer.current = setTimeout(() => setCopied(false), 1800);
    } catch { setNotice(t('copyFail')); }
  };

  const send = async (question = query) => {
    const clean = question.trim();
    if (!clean || chatBusy) return;
    setTalks(cur => [...cur, { role: 'user', text: clean }]);
    setQuery('');
    setChatBusy(true);
    const controller = new AbortController();
    chatRequest.current = controller;
    try {
      const result = await mgChat(clean, lang, sessionId, controller.signal);
      if (controller.signal.aborted) return;
      setTalks(cur => [...cur, {
        role: 'assistant', text: result.answer,
        sources: result.sources.map(s => `[${s.label}] ${s.printed_page ? `${s.source_title} – ${lang === 'zh' ? `第${s.printed_page}页` : lang === 'en' ? `p.${s.printed_page}` : `tr.${s.printed_page}`}` : `${s.source_title}${s.provision ? ` – ${s.provision}` : ''}`}`),
        images: result.images,
      }]);
    } catch {
      if (controller.signal.aborted) return;
      setTalks(cur => [...cur, { role: 'assistant', text: tr(lang, 'chatError'), error: true }]);
    } finally {
      if (chatRequest.current === controller) { chatRequest.current = null; setChatBusy(false); }
    }
  };

  const speechInput = () => {
    const browser = window as typeof window & { SpeechRecognition?: new () => any; webkitSpeechRecognition?: new () => any };
    const Recognition = browser.SpeechRecognition || browser.webkitSpeechRecognition;
    if (!Recognition) { setNotice(t('noSpeechInput')); return; }
    const recognition = new Recognition();
    recognition.lang = LANGS.find(l => l.id === lang)?.speech ?? 'vi-VN';
    recognition.onresult = (event: any) => setQuery(event.results[0][0].transcript);
    recognition.start();
  };

  const renderChat = (suggestions: string[], placeholder: string, className = '') => (
    <ChatDock talks={talks} busy={chatBusy} query={query} setQuery={setQuery} onSend={q => void send(q)} onMic={speechInput}
      onClear={() => { chatRequest.current?.abort(); setChatBusy(false); setTalks([]); }} suggestions={suggestions} placeholder={placeholder} className={className} />
  );

  const curLang = LANGS.find(l => l.id === lang)!;
  const renderTools = (home = false) => (
    <div className={`visit-toolbar ${home ? 'visit-toolbar--home' : 'visit-toolbar--zone'} state-toolbar`} role="group" aria-label={t('tools')}>
      <button onClick={() => setMuted(!audio.muted)} aria-pressed={!audio.muted} data-state={audio.muted ? 'off' : 'on'} aria-label={audio.muted ? t('soundOff') : t('soundOn')} title={audio.muted ? t('soundOff') : t('soundOn')}>
        {audio.muted ? <VolumeX /> : <Volume2 />}<span className="tool-label">{audio.muted ? t('soundOff') : t('soundOn')}</span>
      </button>
      <button onClick={toggleFullscreen} aria-pressed={fullscreen} aria-label={fullscreen ? t('exitFullscreen') : t('fullscreen')} title={fullscreen ? t('exitFullscreen') : t('fullscreen')}>
        {fullscreen ? <Minimize /> : <Maximize />}<span className="tool-label">{fullscreen ? t('exitFullscreen') : t('fullscreen')}</span>
      </button>
      <span className="lang-switch">
        <button onClick={() => setLangMenu(v => !v)} aria-haspopup="menu" aria-expanded={langMenu} aria-label={`${t('language')}: ${curLang.label}`} title={`${t('language')}: ${curLang.label}`}>
          <Globe2 /><span className="lang-short">{curLang.short}</span><span className="tool-label">{curLang.label}</span>
        </button>
        {langMenu && (
          <span className="toolbar-language-menu" role="menu" aria-label={t('language')}>
            {LANGS.map(l => (
              <button key={l.id} role="menuitemradio" aria-checked={l.id === lang} className={l.id === lang ? 'on' : ''} onClick={() => setLang(l.id)}>
                <b>{l.short}</b><span>{l.label}</span>{l.id === lang && <Check size={15} />}
              </button>
            ))}
          </span>
        )}
      </span>
      <button onClick={share} disabled={sharing} aria-busy={sharing} aria-label={t('share')} title={t('share')}><Share2 /><span className="tool-label">{t('share')}</span></button>
      <button onClick={copy} data-state={copied ? 'success' : 'idle'} aria-label={copied ? t('copied') : t('copy')} title={copied ? t('copied') : t('copy')}>
        {copied ? <Check /> : <Copy />}<span className="tool-label" aria-live="polite">{copied ? t('copied') : t('copy')}</span>
      </button>
    </div>
  );

  const toast = notice && <button className="notice toast" onClick={() => setNotice('')} key={notice}>{notice}<X size={16} /></button>;
  const zt = (id: ZoneId) => ZONE_TEXT[id];

  let page;
  if (!active) {
    page = (
      <main className={`home-page ${lang !== 'vi' ? 'tr' : ''} ${busy ? 'camera-busy' : ''}`} data-phase={navigation.phase} aria-busy={busy} {...(busy ? { inert: '' } : {})}>
        <header className="adaptive-home-heading"><span>{t('homeKicker')}</span><h1>{t('homeTitle')}</h1><p>{t('homeLead')}</p></header>
        {renderTools(true)}
        <MapCamera zone={navigation.zone} phase={navigation.phase} stageRef={mapRef} alt={zones.map(z => zt(z.id).title[lang]).join(', ')}>
          <div className="home-hitboxes">
            {zones.map(zone => (
              <button key={zone.id} data-zone={zone.id} className={`hotspot ${zone.id} home-place-card`} onClick={() => openZone(zone)} aria-label={t('explore', { x: zt(zone.id).title[lang] })}>
                <img src={mediaByZone[zone.id].hero.url} alt="" />
                <span className="home-place-card-text"><strong>{zt(zone.id).title[lang]}</strong><span>{zt(zone.id).short[lang]}</span></span>
                <ChevronRight className="home-place-arrow" size={16} aria-hidden="true" />
              </button>
            ))}
            {zones.map(zone => (
              <button key={`pin-${zone.id}`} className={`home-map-pin ${zone.id} ${navigation.zone?.id === zone.id ? 'pin-active' : ''}`} style={{ left: `${zone.hotspot.x}%`, top: `${zone.hotspot.y}%` }}
                onClick={() => openZone(zone)} aria-label={zt(zone.id).title[lang]} title={zt(zone.id).title[lang]}>
                <MapPin aria-hidden="true" />
              </button>
            ))}
          </div>
        </MapCamera>
        <NarratorGuide narrator={narrators.home} className="home-soldier-guide" />
        <button className="home-guide-bubble" onClick={playHomeNarration} aria-label={t('homeIntro')}>
          <span><strong>{t('homeHello')}</strong>{t('homeBubble')}</span>
          <span className="home-guide-sound" aria-hidden="true"><i /><i /><i /><i /></span>
        </button>
        <nav className="adaptive-destinations" aria-label={t('chooseDestination')}>
          {zones.map(zone => (
            <button key={zone.id} data-zone={zone.id} onClick={() => openZone(zone)}>
              <img src={mediaByZone[zone.id].hero.url} alt="" loading="lazy" />
              <span><strong>{zt(zone.id).title[lang]}</strong><small>{zt(zone.id).short[lang]}</small></span>
              <ChevronRight size={20} aria-hidden="true" />
            </button>
          ))}
        </nav>
        <div className="home-bottom-hitboxes">
          <button onClick={() => setHomePanel('photos')} aria-label={t('photos')}><ImageIcon /><span>{t('photos')}</span></button>
          <button onClick={() => setHomePanel('stories')} aria-label={t('stories')}><BookOpen /><span>{t('stories')}</span></button>
        </div>
        {renderChat(lang === 'vi' ? [...suggestedQuestions.home] : [], t('askPlaceholder'), 'home-chat')}
        {homePanel === 'photos' && <PhotosModal onClose={() => setHomePanel('none')} />}
        {homePanel === 'stories' && <StoriesModal onClose={() => setHomePanel('none')} voice={narrators.home.voice} />}
      </main>
    );
  } else {
    const common = { onBack: backHome, tools: renderTools(), renderChat: (s: string[], ph: string) => renderChat(s, ph) };
    page = (
      <>
        {active.id === 'museum' && <MuseumTopics {...common} />}
        {(active.id === 'bridge' || active.id === 'flag') && <StoryZoneView {...common} zoneId={active.id} background={mediaByZone[active.id].hero.url} />}
        {(active.id === 'monument' || active.id === 'union') && <PlaceView {...common} zoneId={active.id} />}
      </>
    );
  }
  return <LangContext.Provider value={lang}>{page}{toast}</LangContext.Provider>;
}

