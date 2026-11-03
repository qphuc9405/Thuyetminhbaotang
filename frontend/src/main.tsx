import { useEffect, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import {
  ArrowLeft, ArrowRight, BookOpen, Check, ChevronRight, Copy,
  ExternalLink, Globe2, Image as ImageIcon, MapPinned, Maximize,
  Mic, Minimize, Play, Send, Share2,
  Volume2, VolumeX, X, Video as VideoIcon,
} from 'lucide-react';
import { zones, type Exhibit, type Zone } from './data';
import { mediaByZone, type Photo } from './media';
import './style.css';

type Tab = 'story' | 'photos' | 'videos';
type HomePanel = 'none' | 'photos' | 'stories';
type VoiceState = 'idle' | 'playing';
type Talk = { role: 'user' | 'assistant'; text: string; sources?: string[] };

const supportsSpeech = 'speechSynthesis' in window;
const homeIntro = 'Xin chào! Mình là chú bộ đội hướng dẫn ảo của di tích Vĩ tuyến 17. Khu di tích đôi bờ Hiền Lương – Bến Hải lưu giữ những câu chuyện về thời kỳ chia cắt và khát vọng thống nhất. Hãy chọn Cầu Hiền Lương, Nhà trưng bày, Kỳ đài Hiền Lương hoặc Tượng đài Khát vọng thống nhất để cùng khám phá.';

function SoldierGuide({ voiceState, hasSpeechBoundary, mouthOpen, className = '' }: {
  voiceState: VoiceState;
  hasSpeechBoundary: boolean;
  mouthOpen: boolean;
  className?: string;
}) {
  return (
    <div className={`soldier-guide ${className} ${voiceState === 'playing' ? 'is-speaking' : ''} ${hasSpeechBoundary ? 'has-speech-boundary' : ''} ${mouthOpen ? 'mouth-open' : ''}`} role="img" aria-label={`Chú bộ đội hướng dẫn ảo${voiceState === 'playing' ? ' đang thuyết minh' : ''}`}>
      <div className="soldier-sprite" aria-hidden="true">
        <img className="soldier-pose" src="/soldier-guide-present.png" alt="" />
        <img className="soldier-mouth" src="/soldier-guide-speaking.png" alt="" />
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
  const [selectedExhibit, setSelectedExhibit] = useState<Exhibit | null>(null);
  const [lightbox, setLightbox] = useState<Photo | null>(null);
  const [voiceState, setVoiceState] = useState<VoiceState>('idle');
  const [muted, setMuted] = useState(false);
  const [lang, setLang] = useState<'vi' | 'en'>('vi');
  const [fullscreen, setFullscreen] = useState(false);
  const [copied, setCopied] = useState(false);
  const [talks, setTalks] = useState<Talk[]>([]);
  const [chatBusy, setChatBusy] = useState(false);
  const [query, setQuery] = useState('');
  const [notice, setNotice] = useState('');
  const [mouthOpen, setMouthOpen] = useState(false);
  const [hasSpeechBoundary, setHasSpeechBoundary] = useState(false);
  const currentSpeech = useRef<SpeechSynthesisUtterance | null>(null);
  const mouthTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const stopNarration = () => {
    currentSpeech.current = null;
    if (mouthTimer.current) clearTimeout(mouthTimer.current);
    mouthTimer.current = null;
    setMouthOpen(false);
    setHasSpeechBoundary(false);
    if (supportsSpeech) window.speechSynthesis.cancel();
    setVoiceState('idle');
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
  };

  const openZone = (zone: Zone) => {
    if (active?.id === zone.id) {
      narrate(zone.script);
      return;
    }
    window.history.pushState({ zone: zone.id }, '', `#${zone.id}`);
    setActive(zone);
    setHomePanel('none');
    setTab('story');
    setSelectedExhibit(null);
    setTalks([]);
    setQuery('');
    setLightbox(null);
  };

  const backHome = () => {
    window.history.pushState({}, '', window.location.pathname + window.location.search);
    stopNarration();
    setActive(null);
    setLightbox(null);
    setTab('story');
  };

  const openExhibit = (exhibit: Exhibit) => {
    setSelectedExhibit(exhibit);
    narrate(`${exhibit.name}. ${exhibit.content}`);
  };

  useEffect(() => () => {
    if (mouthTimer.current) clearTimeout(mouthTimer.current);
    if (supportsSpeech) window.speechSynthesis.cancel();
  }, []);

  useEffect(() => {
    if (active) narrate(active.script);
    else narrate(homeIntro);
  }, [active?.id]);

  useEffect(() => {
    const syncLocation = () => {
      currentSpeech.current = null;
      if (mouthTimer.current) clearTimeout(mouthTimer.current);
      mouthTimer.current = null;
      setMouthOpen(false);
      setHasSpeechBoundary(false);
      if (supportsSpeech) window.speechSynthesis.cancel();
      setVoiceState('idle');
      setActive(zones.find(zone => window.location.hash === `#${zone.id}`) || null);
      setSelectedExhibit(null);
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
    if (!muted) stopNarration();
    setMuted(current => !current);
  };

  const toggleFullscreen = async () => {
    try {
      if (document.fullscreenElement) await document.exitFullscreen();
      else await document.documentElement.requestFullscreen();
      setFullscreen(!!document.fullscreenElement);
    } catch {
      setNotice('Không thể mở chế độ toàn màn hình trên trình duyệt này.');
    }
  };

  const share = async () => {
    try {
      if (navigator.share) {
        await navigator.share({ title: active?.title || 'Vĩ tuyến 17', url: location.href });
      } else {
        await navigator.clipboard.writeText(location.href);
        setNotice('Đã sao chép liên kết để chia sẻ.');
      }
    } catch {
      // Người dùng có thể hủy hộp thoại chia sẻ.
    }
  };

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(location.href);
      setCopied(true);
      setNotice('Đã sao chép liên kết.');
      setTimeout(() => setCopied(false), 1800);
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
    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: clean, zone_id: active?.id }),
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || 'Không thể tra cứu.');
      setTalks(current => [...current, {
        role: 'assistant',
        text: result.answer,
        sources: result.sources.map((source: { title: string; source: string }) =>
          source.source ? `${source.title} · ${source.source}` : source.title
        ),
      }]);
    } catch {
      setTalks(current => [...current, {
        role: 'assistant',
        text: 'Chưa kết nối được kho tư liệu. Hãy chạy backend Python và thử lại.',
      }]);
    } finally {
      setChatBusy(false);
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

  const toolButtons = (
    <div className="tool-buttons">
      <button onClick={toggleAudio} aria-label={muted ? 'Bật âm thanh' : 'Tắt âm thanh'} title={muted ? 'Bật âm thanh' : 'Tắt âm thanh'}>
        {muted ? <VolumeX /> : <Volume2 />}
      </button>
      <button onClick={toggleFullscreen} aria-label="Toàn màn hình" title="Toàn màn hình">
        {fullscreen ? <Minimize /> : <Maximize />}
      </button>
      <button onClick={() => { stopNarration(); setLang(value => value === 'vi' ? 'en' : 'vi'); }} aria-label="Đổi ngôn ngữ giọng đọc" title="Đổi ngôn ngữ giọng đọc">
        <Globe2 /><span className="language-code">{lang.toUpperCase()}</span>
      </button>
      <button onClick={share} aria-label="Chia sẻ" title="Chia sẻ"><Share2 /></button>
      <button onClick={copy} aria-label="Sao chép liên kết" title="Sao chép liên kết">
        {copied ? <Check /> : <Copy />}
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
        <img className="home-image" src="/home-map-clean.png" alt="Bản đồ minh họa khu di tích Vĩ tuyến 17" />
        <SoldierGuide voiceState={voiceState} hasSpeechBoundary={hasSpeechBoundary} mouthOpen={mouthOpen} className="home-soldier-guide" />
        <button className="home-guide-bubble" onClick={() => narrate(homeIntro)} aria-label="Nghe lại giới thiệu tổng quan khu di tích">
          <span><strong>Xin chào!</strong>Mình là chú bộ đội hướng dẫn ảo của di tích Vĩ tuyến 17. Hãy chạm vào các điểm đến để khám phá nhé!</span>
          <span className="home-guide-sound" aria-hidden="true"><i /><i /><i /><i /></span>
        </button>
        <div className="home-hitboxes">
          {zones.map(zone => (
            <button key={zone.id} className={`hotspot ${zone.id}`} onClick={() => openZone(zone)} aria-label={`Khám phá ${zone.title}`} />
          ))}
        </div>
        <div className="home-top-hitboxes" aria-label="Công cụ bản đồ">
          <button onClick={toggleAudio} aria-label={muted ? 'Bật âm thanh' : 'Tắt âm thanh'} title={muted ? 'Bật âm thanh' : 'Tắt âm thanh'} />
          <button onClick={toggleFullscreen} aria-label="Toàn màn hình" title="Toàn màn hình" />
          <button onClick={() => {
            stopNarration();
            const next = lang === 'vi' ? 'en' : 'vi';
            setLang(next);
            setNotice(next === 'vi' ? 'Giọng đọc: Tiếng Việt' : 'Giọng đọc: Tiếng Anh');
          }} aria-label="Đổi ngôn ngữ giọng đọc" title="Đổi ngôn ngữ giọng đọc" />
          <button onClick={share} aria-label="Chia sẻ" title="Chia sẻ" />
          <button onClick={copy} aria-label="Sao chép liên kết" title="Sao chép liên kết" />
        </div>
        <div className="home-bottom-hitboxes">
          <button onClick={() => setHomePanel(value => value === 'photos' ? 'none' : 'photos')} aria-label="Hình ảnh tư liệu" />
          <button onClick={() => setHomePanel(value => value === 'stories' ? 'none' : 'stories')} aria-label="Câu chuyện lịch sử" />
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
        <button className="back-button" onClick={backHome}><ArrowLeft size={19} /> <span>Bản đồ</span></button>
        <div className="explore-identity"><span>VĨ TUYẾN 17</span><strong>{active.title}</strong></div>
        <nav className="zone-nav" aria-label="Các điểm đến">
          {zones.map(zone => (
            <button key={zone.id} className={zone.id === active.id ? 'active' : ''} onClick={() => openZone(zone)}>
              {zone.title}
            </button>
          ))}
        </nav>
        {toolButtons}
      </header>

      <div className="explore-layout">
        <section className="place-story">
          <div className="story-topline"><MapPinned size={17} /> KHÁM PHÁ ĐỊA ĐIỂM · 0{activeIndex + 1}/04</div>
          <h1>{active.title}</h1>
          <p className="place-short">{active.short}</p>
          <p className="place-description">{active.description}</p>
          <button className="next-place" onClick={() => openZone(nextZone)}>
            <span>Điểm tiếp theo <strong>{nextZone.title}</strong></span><ArrowRight size={19} />
          </button>
          <SoldierGuide voiceState={voiceState} hasSpeechBoundary={hasSpeechBoundary} mouthOpen={mouthOpen} />
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
                <p className="resource-intro">Chọn một chủ đề để nghe thuyết minh và đọc nội dung.</p>
                {active.exhibits.map((exhibit, index) => (
                  <button key={exhibit.id} className={`story-card ${selectedExhibit?.id === exhibit.id ? 'chosen' : ''}`} onClick={() => openExhibit(exhibit)}>
                    <span className="story-index">0{index + 1}</span>
                    <span><small>{exhibit.type}</small><strong>{exhibit.name}</strong><em>{exhibit.caption}</em></span>
                    <ChevronRight size={20} />
                  </button>
                ))}
                {selectedExhibit && <p className="exhibit-detail">{selectedExhibit.content}</p>}
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
