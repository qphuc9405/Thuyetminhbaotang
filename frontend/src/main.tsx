import { useEffect, useRef, useState, type CSSProperties } from 'react';
import { createRoot } from 'react-dom/client';
import {
  ArrowLeft, ArrowRight, BookOpen, Check, ChevronRight, Copy,
  ExternalLink, Globe2, Image as ImageIcon, MapPinned, Maximize,
  MapPin, Mic, Minimize, Play, Send, Share2,
  Volume2, VolumeX, X, Video as VideoIcon,
} from 'lucide-react';
import { zones, type Zone } from './data';
import { mediaByZone, type Photo } from './media';
import { narrators, type Narrator } from './guides';
import './style.css';
import './responsive.css';

type Tab = 'story' | 'photos' | 'videos';
type HomePanel = 'none' | 'photos' | 'stories';
type VoiceState = 'idle' | 'playing' | 'paused';
type Document = { id: string; title: string; content: string; source: string; category: string; zone_id: string };
type Talk = { role: 'user' | 'assistant'; text: string; sources?: string[] };

const supportsSpeech = 'speechSynthesis' in window;
const homeAudioSource = '/audio/home-introduction.mp3';

function NarratorGuide({ voiceState, hasSpeechBoundary, mouthOpen, narrator = narrators.bridge, className = '' }: {
  voiceState: VoiceState;
  hasSpeechBoundary: boolean;
  mouthOpen: boolean;
  narrator?: Narrator;
  className?: string;
}) {
  return (
    <div className={`soldier-guide ${className} ${voiceState === 'playing' ? 'is-speaking' : ''} ${hasSpeechBoundary ? 'has-speech-boundary' : ''} ${mouthOpen ? 'mouth-open' : ''}`} data-narrator={narrator.id} style={{ '--mouth-x': narrator.mouthX, '--mouth-y': narrator.mouthY } as CSSProperties} role="img" aria-label={`${narrator.label}${voiceState === 'playing' ? ' đang thuyết minh' : ''}`}>
      <div className="soldier-sprite" aria-hidden="true">
        <img className="soldier-pose" src={narrator.present} alt="" />
        <img className="soldier-mouth" src={narrator.speaking} alt="" />
      </div>
    </div>
  );
}

function App() {
  const [active, setActive] = useState<Zone | null>(() =>
    zones.find(zone => window.location.hash === `#${zone.id}`) || null
  );
  const [tab, setTab] = useState<Tab>('story');
  const [homePanel, setHomePanel] = useState<HomePanel>('none');
  const [selectedExhibit, setSelectedExhibit] = useState<Document | null>(null);
  const [lightbox, setLightbox] = useState<Photo | null>(null);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loadingNarration, setLoadingNarration] = useState(false);
  const [narrationError, setNarrationError] = useState('');
  const [narrationAttempt, setNarrationAttempt] = useState(0);
  const [voiceState, setVoiceState] = useState<VoiceState>('idle');
  const [muted, setMuted] = useState(false);
  const [lang, setLang] = useState<'vi' | 'en'>('vi');
  const [fullscreen, setFullscreen] = useState(false);
  const [copied, setCopied] = useState(false);
  const [sharing, setSharing] = useState(false);
  const [talks, setTalks] = useState<Talk[]>([]);
  const [chatBusy, setChatBusy] = useState(false);
  const [query, setQuery] = useState('');
  const [notice, setNotice] = useState('');
  const [mouthOpen, setMouthOpen] = useState(false);
  const [hasSpeechBoundary, setHasSpeechBoundary] = useState(false);
  const locationZone = useRef(active?.id);
  const chatRequest = useRef<AbortController | null>(null);
  const narrationRequest = useRef<AbortController | null>(null);
  const resetLocation = () => {
    chatRequest.current?.abort();
    chatRequest.current = null;
    narrationRequest.current?.abort();
    narrationRequest.current = null;
    setChatBusy(false);
    setTalks([]);
    setQuery('');
    setDocuments([]);
    setSelectedExhibit(null);
    setLightbox(null);
    stopNarration();
  };
  const currentSpeech = useRef<SpeechSynthesisUtterance | null>(null);
  const homeAudio = useRef<HTMLAudioElement | null>(null);
  const mouthTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const copyTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const stopNarration = () => {
    const audio = homeAudio.current;
    homeAudio.current = null;
    if (audio) {
      audio.onplaying = null;
      audio.onended = null;
      audio.onerror = null;
      audio.pause();
      audio.currentTime = 0;
    }
    currentSpeech.current = null;
    if (mouthTimer.current) clearTimeout(mouthTimer.current);
    mouthTimer.current = null;
    setMouthOpen(false);
    setHasSpeechBoundary(false);
    if (supportsSpeech) window.speechSynthesis.cancel();
    setVoiceState('idle');
  };

  const playHomeNarration = () => {
    if (homeAudio.current && !homeAudio.current.paused) return;
    if (muted) return;
    const audio = homeAudio.current || new Audio(homeAudioSource);
    homeAudio.current = audio;
    audio.onplaying = () => {
      if (homeAudio.current !== audio) return;
      setNotice('');
      setVoiceState('playing');
    };
    audio.onended = () => {
      if (homeAudio.current === audio) stopNarration();
    };
    audio.onerror = () => {
      if (homeAudio.current !== audio) return;
      stopNarration();
      setNotice('Không tải được bài thuyết minh. Chạm vào lời chào để thử lại.');
    };
    void audio.play().catch((error: DOMException) => {
      if (homeAudio.current !== audio || error.name === 'AbortError') return;
      setVoiceState('idle');
      setNotice(error.name === 'NotAllowedError'
        ? 'Chạm vào lời chào để nghe bài thuyết minh.'
        : 'Không phát được bài thuyết minh. Chạm vào lời chào để thử lại.');
    });
  };

  const narrate = (text: string) => {
    stopNarration();
    if (!supportsSpeech) {
      setNotice('Trình duyệt này chưa hỗ trợ thuyết minh bằng giọng nói.');
      return;
    }
    if (muted || !text) return;
    const speech = new SpeechSynthesisUtterance(text);
    speech.lang = lang === 'vi' ? 'vi-VN' : 'en-US';
    speech.rate = 0.94;
    currentSpeech.current = speech;
    speech.onstart = () => { if (currentSpeech.current === speech) setVoiceState('playing'); };
    speech.onboundary = () => {
      if (currentSpeech.current !== speech) return;
      setHasSpeechBoundary(true);
      setMouthOpen(true);
      if (mouthTimer.current) clearTimeout(mouthTimer.current);
      mouthTimer.current = setTimeout(() => setMouthOpen(false), 155);
    };
    const finish = () => {
      if (currentSpeech.current !== speech) return;
      currentSpeech.current = null;
      if (mouthTimer.current) clearTimeout(mouthTimer.current);
      mouthTimer.current = null;
      setMouthOpen(false);
      setHasSpeechBoundary(false);
      setVoiceState('idle');
    };
    speech.onend = finish;
    speech.onerror = finish;
    window.speechSynthesis.speak(speech);
    // cancel() can leave the global synthesizer paused after replay/navigation.
    window.speechSynthesis.resume();
  };

  const openZone = (zone: Zone) => {
    if (active?.id === zone.id) return;
    resetLocation();
    locationZone.current = zone.id;
    window.history.pushState({ zone: zone.id }, '', `#${zone.id}`);
    setActive(zone);
    setHomePanel('none');
    setTab('story');
  };

  const backHome = () => {
    resetLocation();
    locationZone.current = undefined;
    window.history.pushState({}, '', window.location.pathname + window.location.search);
    setActive(null);
    setTab('story');
  };

  const openExhibit = (exhibit: Document) => {
    setSelectedExhibit(exhibit);
    if (!currentSpeech.current) narrate(`${exhibit.title}. ${exhibit.content}`);
  };

  useEffect(() => () => {
    const audio = homeAudio.current;
    homeAudio.current = null;
    if (audio) {
      audio.onplaying = null;
      audio.onended = null;
      audio.onerror = null;
      audio.pause();
    }
    chatRequest.current?.abort();
    narrationRequest.current?.abort();
    if (mouthTimer.current) clearTimeout(mouthTimer.current);
    if (copyTimer.current) clearTimeout(copyTimer.current);
    if (supportsSpeech) window.speechSynthesis.cancel();
  }, []);

  const narrateLatest = useRef(narrate);
  narrateLatest.current = narrate;
  const playHomeLatest = useRef(playHomeNarration);
  playHomeLatest.current = playHomeNarration;
  useEffect(() => {
    if (!active) {
      setLoadingNarration(false);
      setNarrationError('');
      playHomeLatest.current();
      return;
    }
    const controller = new AbortController();
    narrationRequest.current = controller;
    setLoadingNarration(true);
    setNarrationError('');
    void (async () => {
      try {
        const response = await fetch(`/api/narration?zone_id=${active.id}`, { signal: controller.signal });
        const result = await response.json();
        if (!response.ok) throw new Error(result.error);
        if (controller.signal.aborted) return;
        setDocuments(result.documents);
        const intro = result.documents[0] as Document | undefined;
        if (intro) {
          setSelectedExhibit(intro);
          narrateLatest.current(`${intro.title}. ${intro.content}`);
        } else setNarrationError('Địa điểm này chưa có tư liệu thuyết minh.');
      } catch {
        if (!controller.signal.aborted) setNarrationError('Không tải được tư liệu thuyết minh. Hãy kiểm tra backend và thử lại.');
      } finally {
        if (!controller.signal.aborted) setLoadingNarration(false);
      }
    })();
    return () => controller.abort();
  }, [active?.id, narrationAttempt]);

  useEffect(() => {
    const syncLocation = () => {
      const zone = zones.find(item => window.location.hash === `#${item.id}`);
      if (locationZone.current === zone?.id) return;
      locationZone.current = zone?.id;
      resetLocation();
      setActive(zone || null);
      setHomePanel('none');
      setTab('story');
    };
    window.addEventListener('popstate', syncLocation);
    window.addEventListener('hashchange', syncLocation);
    return () => {
      window.removeEventListener('popstate', syncLocation);
      window.removeEventListener('hashchange', syncLocation);
    };
  }, []);

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setLightbox(null);
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, []);

  const toggleAudio = () => {
    if (homeAudio.current) homeAudio.current.muted = !muted;
    if (currentSpeech.current && supportsSpeech) {
      if (muted) {
        window.speechSynthesis.resume();
        setVoiceState('playing');
      } else {
        window.speechSynthesis.pause();
        setVoiceState('paused');
        setMouthOpen(false);
      }
    }
    setMuted(current => !current);
  };

  const toggleFullscreen = async () => {
    try {
      if (document.fullscreenElement) await document.exitFullscreen();
      else await document.documentElement.requestFullscreen();
    } catch {
      setNotice('Không thể mở chế độ toàn màn hình trên trình duyệt này.');
    }
  };

  useEffect(() => {
    const syncFullscreen = () => setFullscreen(!!document.fullscreenElement);
    syncFullscreen();
    document.addEventListener('fullscreenchange', syncFullscreen);
    return () => document.removeEventListener('fullscreenchange', syncFullscreen);
  }, []);

  const share = async () => {
    if (sharing) return;
    setSharing(true);
    try {
      if (navigator.share) {
        await navigator.share({ title: active?.title || 'Vĩ tuyến 17', url: location.href });
      } else {
        await navigator.clipboard.writeText(location.href);
        setNotice('Đã sao chép liên kết để chia sẻ.');
      }
    } catch {
      // Người dùng có thể hủy hộp thoại chia sẻ.
    } finally {
      setSharing(false);
    }
  };

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(location.href);
      setCopied(true);
      setNotice('Đã sao chép liên kết.');
      if (copyTimer.current) clearTimeout(copyTimer.current);
      copyTimer.current = setTimeout(() => setCopied(false), 1800);
    } catch {
      setNotice('Không thể sao chép liên kết.');
    }
  };

  const send = async (question = query) => {
    const clean = question.trim();
    if (!clean || chatBusy) return;
    setTalks(current => [...current, { role: 'user', text: clean }]);
    setQuery('');
    setChatBusy(true);
    const controller = new AbortController();
    chatRequest.current = controller;
    try {
      const response = await fetch('/api/chat', {
        signal: controller.signal,
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: clean, zone_id: active?.id }),
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || 'Không thể tra cứu.');
      if (controller.signal.aborted) return;
      setTalks(current => [...current, {
        role: 'assistant',
        text: result.answer,
        sources: result.sources.map((source: { title: string; source: string }) =>
          source.source ? `${source.title} · ${source.source}` : source.title
        ),
      }]);
    } catch {
      if (controller.signal.aborted) return;
      setTalks(current => [...current, {
        role: 'assistant',
        text: 'Chưa kết nối được kho tư liệu. Hãy chạy backend Python và thử lại.',
      }]);
    } finally {
      if (chatRequest.current === controller) {
        chatRequest.current = null;
        setChatBusy(false);
      }
    }
  };

  const speechInput = () => {
    const browser = window as typeof window & {
      SpeechRecognition?: new () => any;
      webkitSpeechRecognition?: new () => any;
    };
    const Recognition = browser.SpeechRecognition || browser.webkitSpeechRecognition;
    if (!Recognition) {
      setNotice('Trình duyệt chưa hỗ trợ nhập câu hỏi bằng giọng nói.');
      return;
    }
    const recognition = new Recognition();
    recognition.lang = lang === 'vi' ? 'vi-VN' : 'en-US';
    recognition.onresult = (event: any) => setQuery(event.results[0][0].transcript);
    recognition.start();
  };

  const audioLabel = muted ? 'Âm thanh tắt' : 'Âm thanh bật';
  const fullscreenLabel = fullscreen ? 'Toàn màn hình' : 'Màn hình thường';
  const languageLabel = lang === 'vi' ? 'Tiếng Việt' : 'English';
  const copyLabel = copied ? 'Đã sao chép' : 'Sao chép liên kết';
  const changeLanguage = () => {
    const next = lang === 'vi' ? 'en' : 'vi';
    setLang(next);
    setNotice(next === 'vi' ? 'Giọng đọc: Tiếng Việt' : 'Giọng đọc: Tiếng Anh');
  };

  const renderTools = (home = false) => (
    <div className={`${home ? 'home-top-hitboxes' : 'tool-buttons'} state-toolbar`} role="group" aria-label="Công cụ tham quan">
      <button onClick={toggleAudio} aria-pressed={!muted} data-state={muted ? 'off' : 'on'} aria-label={`${audioLabel}. ${muted ? 'Bật âm thanh' : 'Tắt âm thanh'}`} title={muted ? 'Bật âm thanh' : 'Tắt âm thanh'}>
        {muted ? <VolumeX /> : <Volume2 />}<span className="tool-label">{audioLabel}</span>
      </button>
      <button onClick={toggleFullscreen} aria-pressed={fullscreen} aria-label={`${fullscreenLabel}. ${fullscreen ? 'Thoát toàn màn hình' : 'Mở toàn màn hình'}`} title={fullscreen ? 'Thoát toàn màn hình' : 'Mở toàn màn hình'}>
        {fullscreen ? <Minimize /> : <Maximize />}<span className="tool-label">{fullscreenLabel}</span>
      </button>
      <button onClick={changeLanguage} aria-label={`Giọng đọc ${languageLabel}. Chuyển sang ${lang === 'vi' ? 'tiếng Anh' : 'tiếng Việt'}`} title={`Đổi giọng đọc sang ${lang === 'vi' ? 'tiếng Anh' : 'tiếng Việt'}`}>
        <Globe2 /><span className="tool-label">{languageLabel}</span>
      </button>
      <button onClick={share} disabled={sharing} aria-busy={sharing} aria-label={sharing ? 'Đang chia sẻ' : 'Chia sẻ'} title="Chia sẻ"><Share2 /><span className="tool-label">{sharing ? 'Đang chia sẻ…' : 'Chia sẻ'}</span></button>
      <button onClick={copy} data-state={copied ? 'success' : 'idle'} aria-label={copyLabel} title={copyLabel}>
        {copied ? <Check /> : <Copy />}<span className="tool-label" aria-live="polite">{copyLabel}</span>
      </button>
    </div>
  );

  const chat = (
    <section className={`chat-dock ${query ? 'has-query' : ''}`} aria-label="Tra cứu tư liệu">
      {talks.length > 0 && (
        <div className="chat-history" aria-live="polite">
          {talks.map((talk, index) => (
            <div className={`chat-bubble ${talk.role}`} key={index}>
              <p>{talk.text}</p>
              {!!talk.sources?.length && <small>Nguồn: {talk.sources.join('; ')}</small>}
            </div>
          ))}
          {chatBusy && <div className="chat-bubble assistant"><p>Đang tìm trong tư liệu…</p></div>}
        </div>
      )}
      <form className="chat-form" onSubmit={event => { event.preventDefault(); void send(); }}>
        <span className="chat-icon"><BookOpen size={20} /></span>
        <input
          value={query}
          onChange={event => setQuery(event.target.value)}
          placeholder={active ? `Hỏi về ${active.title}…` : 'Hỏi tôi về di tích Vĩ tuyến 17…'}
          aria-label="Câu hỏi tra cứu tư liệu"
        />
        <button type="button" onClick={speechInput} aria-label="Nhập bằng giọng nói" title="Nhập bằng giọng nói"><Mic /></button>
        <button type="submit" className="send-button" disabled={chatBusy || !query.trim()} aria-label="Gửi câu hỏi"><Send /></button>
      </form>
    </section>
  );

  if (!active) {
    return (
      <main className="home-page">
        <header className="adaptive-home-heading"><span>DI TÍCH ĐÔI BỜ HIỀN LƯƠNG – BẾN HẢI</span><h1>Vĩ tuyến 17</h1><p>Chọn một điểm đến để nghe thuyết minh và khám phá tư liệu.</p></header>
        {renderTools(true)}
        <div className="home-map-stage">
          <img className="home-image" src="/home-map-sharp.png" fetchPriority="high" decoding="async" alt="Bản đồ năm điểm tham quan khu di tích Vĩ tuyến 17: Cầu Hiền Lương, Nhà trưng bày, Kỳ đài, Tượng đài và Nhà liên hiệp." />
          <div className="home-hitboxes">
            {zones.map(zone => (
              <button key={zone.id} className={`hotspot ${zone.id} home-place-card`} onClick={() => openZone(zone)} aria-label={`Khám phá ${zone.title}`}>
                  <img src={mediaByZone[zone.id].hero.url} alt="" />
                  <span className="home-place-card-text">
                    <strong>{zone.title}</strong>
                    <span>{zone.short}</span>
                  </span>
                  <ChevronRight className="home-place-arrow" size={16} aria-hidden="true" />
              </button>
            ))}
            {zones.map(zone => (
              <button key={`pin-${zone.id}`} className={`home-map-pin ${zone.id}`} style={{ left: `${zone.hotspot.x}%`, top: `${zone.hotspot.y}%` }} onClick={() => openZone(zone)} aria-label={`Vị trí ${zone.title}`} title={zone.title}>
                <MapPin aria-hidden="true" />
              </button>
            ))}
          </div>
        </div>
        <NarratorGuide voiceState={voiceState} hasSpeechBoundary={hasSpeechBoundary} mouthOpen={mouthOpen} className="home-soldier-guide" />
        <button className="home-guide-bubble" onClick={() => playHomeNarration()} aria-label="Nghe giới thiệu tổng quan khu di tích">
          <span><strong>Xin chào!</strong>Mình là chú bộ đội hướng dẫn ảo của di tích Vĩ tuyến 17. Hãy chạm vào các điểm đến để khám phá nhé!</span>
          <span className="home-guide-sound" aria-hidden="true"><i /><i /><i /><i /></span>
        </button>
        <nav className="adaptive-destinations" aria-label="Chọn địa điểm tham quan">
          {zones.map(zone => (
            <button key={zone.id} onClick={() => openZone(zone)}>
              <img src={mediaByZone[zone.id].hero.url} alt="" loading="lazy" />
              <span><strong>{zone.title}</strong><small>{zone.id === 'museum' ? 'Bờ Nam · bên trái Tượng đài' : zone.short}</small></span>
              <ChevronRight size={20} aria-hidden="true" />
            </button>
          ))}
        </nav>
        <div className="home-bottom-hitboxes">
          <button onClick={() => setHomePanel(value => value === 'photos' ? 'none' : 'photos')} aria-label="Hình ảnh tư liệu" aria-expanded={homePanel === 'photos'}><ImageIcon /><span>Hình ảnh tư liệu</span></button>
          <button onClick={() => setHomePanel(value => value === 'stories' ? 'none' : 'stories')} aria-label="Câu chuyện lịch sử" aria-expanded={homePanel === 'stories'}><BookOpen /><span>Câu chuyện lịch sử</span></button>
        </div>
        {homePanel !== 'none' && (
          <aside className="home-floating-panel">
            <div className="home-panel-heading">
              <strong>{homePanel === 'photos' ? 'Hình ảnh tư liệu' : 'Câu chuyện lịch sử'}</strong>
              <button onClick={() => setHomePanel('none')} aria-label="Đóng"><X size={18} /></button>
            </div>
            <div className="home-panel-content">
              {zones.map(zone => (
                <button key={zone.id} onClick={() => { openZone(zone); if (homePanel === 'photos') setTab('photos'); }}>
                  <img src={mediaByZone[zone.id].hero.url} alt="" />
                  <span>{zone.title}<small>{homePanel === 'photos' ? 'Xem ảnh địa điểm' : 'Nghe câu chuyện'}</small></span>
                  <ChevronRight size={17} />
                </button>
              ))}
            </div>
          </aside>
        )}
        {chat}
        {notice && <button className="notice" onClick={() => setNotice('')}>{notice}<X size={16} /></button>}
      </main>
    );
  }

  const media = mediaByZone[active.id];
  const activeIndex = zones.findIndex(zone => zone.id === active.id);
  const nextZone = zones[(activeIndex + 1) % zones.length];

  return (
    <main className="explore-page">
      <img className="explore-background" src={media.hero.url} alt={media.hero.title} />
      <div className="explore-overlay" />
      <header className="explore-header">
        <button className="back-button" onClick={backHome} aria-label="Về bản đồ"><ArrowLeft size={19} /> <span>Bản đồ</span></button>
        <div className="explore-identity"><span>VĨ TUYẾN 17</span><strong>{active.title}</strong></div>
        <nav className="zone-nav" aria-label="Các điểm đến">
          {zones.map(zone => (
            <button key={zone.id} className={zone.id === active.id ? 'active' : ''} aria-current={zone.id === active.id ? 'page' : undefined} onClick={() => openZone(zone)}>
              {zone.title}
            </button>
          ))}
        </nav>
        {renderTools()}
      </header>

      <div className="explore-layout">
        <section className="place-story">
          <div className="story-topline"><MapPinned size={17} /> KHÁM PHÁ ĐỊA ĐIỂM · {String(activeIndex + 1).padStart(2, '0')}/{String(zones.length).padStart(2, '0')}</div>
          <h1>{active.title}</h1>
          <p className="place-short">{active.short}</p>
          <p className="place-description">{documents[0]?.content || (loadingNarration ? 'Đang tải tư liệu…' : narrationError)}</p>
          <button className="next-place" onClick={() => openZone(nextZone)}>
            <span>Điểm tiếp theo <strong>{nextZone.title}</strong></span><ArrowRight size={19} />
          </button>
          <NarratorGuide key={active.id} narrator={narrators[active.id]} voiceState={voiceState} hasSpeechBoundary={hasSpeechBoundary} mouthOpen={mouthOpen} />
        </section>

        <section className="resource-panel" aria-label="Tư liệu địa điểm">
          <div className="resource-heading"><span className="section-kicker">KHÁM PHÁ THÊM</span><strong>Tư liệu về địa điểm</strong></div>
          <div className="resource-tabs" role="tablist" aria-label="Loại tư liệu">
            <button role="tab" aria-selected={tab === 'story'} className={tab === 'story' ? 'selected' : ''} onClick={() => setTab('story')}><BookOpen size={17} /> Câu chuyện</button>
            <button role="tab" aria-selected={tab === 'photos'} className={tab === 'photos' ? 'selected' : ''} onClick={() => setTab('photos')}><ImageIcon size={17} /> Hình ảnh</button>
            <button role="tab" aria-selected={tab === 'videos'} className={tab === 'videos' ? 'selected' : ''} onClick={() => setTab('videos')}><VideoIcon size={17} /> Video</button>
          </div>
          <div className="resource-content">
            {tab === 'story' && (
              <div className="story-list">
                <p className="resource-intro">Chọn một chủ đề để đọc nội dung. Bài thuyết minh đang phát sẽ tiếp tục đến hết.</p>
                {loadingNarration && <p role="status">Đang tải tư liệu…</p>}
                {narrationError && (
                  <div role="alert">
                    <p>{narrationError}</p>
                    <button type="button" onClick={() => setNarrationAttempt(attempt => attempt + 1)}>Tải lại tư liệu</button>
                  </div>
                )}
                {documents.map((exhibit, index) => (
                  <button key={exhibit.id} className={`story-card ${selectedExhibit?.id === exhibit.id ? 'chosen' : ''}`} onClick={() => openExhibit(exhibit)}>
                    <span className="story-index">0{index + 1}</span>
                    <span><small>{exhibit.category}</small><strong>{exhibit.title}</strong><em>{exhibit.source}</em></span>
                    <ChevronRight size={20} />
                  </button>
                ))}
                {selectedExhibit && <p className="exhibit-detail">{selectedExhibit.content}<small className="narration-source">Nguồn: {selectedExhibit.source || 'Chưa ghi nguồn'}</small></p>}
              </div>
            )}
            {tab === 'photos' && (
              <div className="photo-grid">
                {media.photos.map(photo => (
                  <div className="photo-card" key={photo.url}>
                    <button onClick={() => setLightbox(photo)} aria-label={`Xem lớn: ${photo.title}`}>
                      <img src={photo.url} alt={photo.title} loading="lazy" onError={event => { event.currentTarget.onerror = null; event.currentTarget.src = media.hero.url; }} />
                      <span><ImageIcon size={16} /> Xem ảnh</span>
                    </button>
                    <strong>{photo.title}</strong>
                    <small>{photo.credit}</small>
                    {photo.source && <a href={photo.source} target="_blank" rel="noreferrer">Nguồn ảnh <ExternalLink size={12} /></a>}
                  </div>
                ))}
              </div>
            )}
            {tab === 'videos' && (
              <div className="video-list">
                <p className="resource-intro">Video mở trên trang của đơn vị phát hành.</p>
                {media.videos.map(video => (
                  <a className="video-card" key={video.url} href={video.url} target="_blank" rel="noreferrer">
                    <span className="video-play"><Play fill="currentColor" size={20} /></span>
                    <span><small>{video.publisher} · VIDEO TƯ LIỆU</small><strong>{video.title}</strong><em>{video.description}</em></span>
                    <ExternalLink size={17} />
                  </a>
                ))}
              </div>
            )}
          </div>
        </section>
      </div>

      <div className="explore-bottom">
        <div className="quick-questions">
          <span>GỢI Ý CÂU HỎI</span>
          <button onClick={() => void send(`${active.title} có ý nghĩa gì?`)}>Địa điểm này có ý nghĩa gì?</button>
          <button onClick={() => void send(`Có hiện vật nào ở ${active.title}?`)}>Có hiện vật nào nổi bật?</button>
        </div>
        {chat}
      </div>

      {lightbox && (
        <div className="lightbox" role="dialog" aria-modal="true" aria-label={lightbox.title} onClick={() => setLightbox(null)}>
          <button className="lightbox-close" onClick={() => setLightbox(null)} aria-label="Đóng ảnh"><X /></button>
          <figure onClick={event => event.stopPropagation()}>
            <img
              src={lightbox.url}
              alt={lightbox.title}
              onError={event => { event.currentTarget.onerror = null; event.currentTarget.src = media.hero.url; }}
            />
            <figcaption>{lightbox.title} <small>{lightbox.credit}</small></figcaption>
          </figure>
        </div>
      )}
      {notice && <button className="notice" onClick={() => setNotice('')}>{notice}<X size={16} /></button>}
    </main>
  );
}

createRoot(document.getElementById('root')!).render(<App />);
