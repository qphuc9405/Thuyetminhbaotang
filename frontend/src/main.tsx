import { useEffect, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import {
  BookOpen, Check, ChevronRight, Copy,
  Globe2, Image as ImageIcon, Maximize,
  MapPin, Mic, Minimize, Send, Share2,
  X,
} from 'lucide-react';
import { zones } from './data';
import { mediaByZone } from './media';
import { DestinationScene } from './DestinationScene';
import { NarratorWidget } from './NarratorWidget';
import './style.css';
import './responsive.css';
import './camera.css';
import { useZoneNavigation } from './useZoneNavigation';
import { MapCamera } from './MapCamera';
import { MuseumExhibition } from './MuseumExhibition';
import { suggestedQuestions } from './suggestedQuestions';

type Tab = 'story' | 'photos';
type HomePanel = 'none' | 'photos' | 'stories';
type Document = { id: string; title: string; content: string; source: string; category: string; zone_id: string };
type Talk = { role: 'user' | 'assistant'; text: string; sources?: string[] };

function App() {
  const { active, openZone, backHome, mapRef, navigation, busy } = useZoneNavigation(zones, {
    onStart: () => resetLocation(),
    onNavigate: (_zone, nextTab) => {
      resetLocation();
      setHomePanel('none');
      setTab(nextTab);
      setNotice('');
    },
  });
  const [tab, setTab] = useState<Tab>('story');
  const [homePanel, setHomePanel] = useState<HomePanel>('none');
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loadingDocuments, setLoadingDocuments] = useState(false);
  const [documentError, setDocumentError] = useState('');
  const [documentAttempt, setDocumentAttempt] = useState(0);
  const [fullscreen, setFullscreen] = useState(false);
  const [copied, setCopied] = useState(false);
  const [sharing, setSharing] = useState(false);
  const [talks, setTalks] = useState<Talk[]>([]);
  const [chatOpen, setChatOpen] = useState(false);
  const [chatBusy, setChatBusy] = useState(false);
  const chatInput = useRef<HTMLInputElement>(null);
  const [query, setQuery] = useState('');
  const [notice, setNotice] = useState('');
  const chatRequest = useRef<AbortController | null>(null);
  const documentRequest = useRef<AbortController | null>(null);
  const resetLocation = () => {
    chatRequest.current?.abort();
    chatRequest.current = null;
    documentRequest.current?.abort();
    documentRequest.current = null;
    setChatBusy(false);
    setTalks([]);
    setChatOpen(false);
    setQuery('');
    setDocuments([]);
  };
  const copyTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => () => {
    chatRequest.current?.abort();
    documentRequest.current?.abort();
    if (copyTimer.current) clearTimeout(copyTimer.current);
  }, []);

  useEffect(() => {
    if (!active) {
      setLoadingDocuments(false);
      setDocumentError('');
      return;
    }
    const controller = new AbortController();
    documentRequest.current = controller;
    setLoadingDocuments(true);
    setDocumentError('');
    void (async () => {
      try {
        const response = await fetch(`/api/narration?zone_id=${active.id}`, { signal: controller.signal });
        const result = await response.json();
        if (!response.ok) throw new Error(result.error);
        if (controller.signal.aborted) return;
        const localDocuments = result.documents as Document[];
        setDocuments(localDocuments);
        if (!localDocuments.length) setDocumentError('Địa điểm này chưa có tư liệu.');
      } catch {
        if (!controller.signal.aborted) setDocumentError('Không tải được tư liệu. Hãy kiểm tra backend và thử lại.');
      } finally {
        if (!controller.signal.aborted) setLoadingDocuments(false);
      }
    })();
    return () => controller.abort();
  }, [active?.id, documentAttempt]);

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
    setChatOpen(true);
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
    recognition.lang = 'vi-VN';
    recognition.onresult = (event: any) => setQuery(event.results[0][0].transcript);
    recognition.start();
  };

  const fullscreenLabel = fullscreen ? 'Toàn màn hình' : 'Màn hình thường';
  const copyLabel = copied ? 'Đã sao chép' : 'Sao chép liên kết';

  const renderTools = (home = false) => (
    <div className={`${home ? 'home-top-hitboxes' : 'tool-buttons'} state-toolbar`} role="group" aria-label="Công cụ tham quan">
      <button onClick={toggleFullscreen} aria-pressed={fullscreen} aria-label={`${fullscreenLabel}. ${fullscreen ? 'Thoát toàn màn hình' : 'Mở toàn màn hình'}`} title={fullscreen ? 'Thoát toàn màn hình' : 'Mở toàn màn hình'}>
        {fullscreen ? <Minimize /> : <Maximize />}<span className="tool-label">{fullscreenLabel}</span>
      </button>
      <button onClick={() => setNotice('Giao diện và tư liệu bằng tiếng Việt.')} aria-label="Ngôn ngữ: Tiếng Việt" title="Ngôn ngữ: Tiếng Việt">
        <Globe2 /><span className="tool-label">Tiếng Việt</span>
      </button>
      <button onClick={share} disabled={sharing} aria-busy={sharing} aria-label={sharing ? 'Đang chia sẻ' : 'Chia sẻ'} title="Chia sẻ"><Share2 /><span className="tool-label">{sharing ? 'Đang chia sẻ…' : 'Chia sẻ'}</span></button>
      <button onClick={copy} data-state={copied ? 'success' : 'idle'} aria-label={copyLabel} title={copyLabel}>
        {copied ? <Check /> : <Copy />}<span className="tool-label" aria-live="polite">{copyLabel}</span>
      </button>
    </div>
  );

  const closeChat = () => {
    setChatOpen(false);
    chatInput.current?.focus({ preventScroll: true });
  };

  const questionSuggestions = (
    <div className="chat-suggestions" role="group" aria-label="Gợi ý câu hỏi">
      <span>Gợi ý câu hỏi</span>
      <div className="chat-suggestion-buttons">
        {suggestedQuestions[active?.id || 'home'].map(question => (
          <button type="button" key={question} disabled={chatBusy} onClick={() => { void send(question); }}>{question}</button>
        ))}
      </div>
    </div>
  );

  const chat = (
    <section className={`chat-dock ${query ? 'has-query' : ''}`} aria-label="Tra cứu tư liệu" onKeyDown={event => {
      if (event.key === 'Escape' && chatOpen) { event.stopPropagation(); closeChat(); }
    }}>
      {chatOpen && talks.length > 0 && (
        <div className="chat-history">
          <header className="chat-history-header">
            <strong>Hỏi đáp tư liệu</strong>
            <button type="button" onClick={closeChat} aria-label="Đóng hội thoại" title="Đóng hội thoại"><X size={20} aria-hidden="true" /></button>
          </header>
          <div className="chat-messages" aria-live="polite">
          {talks.map((talk, index) => (
            <div className={`chat-bubble ${talk.role}`} key={index}>
              <p>{talk.text}</p>
              {!!talk.sources?.length && <small>Nguồn: {talk.sources.join('; ')}</small>}
            </div>
          ))}
          {chatBusy && <div className="chat-bubble assistant"><p>Đang tìm trong tư liệu…</p></div>}
          {questionSuggestions}
          </div>
        </div>
      )}
      {!chatOpen && questionSuggestions}
      <form className="chat-form" onSubmit={event => { event.preventDefault(); void send(); }}>
        <button type="button" onClick={speechInput} aria-label="Nhập bằng giọng nói" title="Nhập bằng giọng nói"><Mic /></button>
        <input
          ref={chatInput}
          value={query}
          onClick={() => { if (talks.length) setChatOpen(true); }}
          onChange={event => setQuery(event.target.value)}
          placeholder={active?.id === 'museum' ? 'Hỏi tôi về hiện vật trong Nhà trưng bày…' : active ? `Hỏi về ${active.title}…` : 'Hỏi tôi về di tích Vĩ tuyến 17…'}
          aria-label="Câu hỏi tra cứu tư liệu"
        />
        <button type="submit" className="send-button" disabled={chatBusy || !query.trim()} aria-label="Gửi câu hỏi"><Send /></button>
      </form>
    </section>
  );

  if (!active) {
    return (
      <main className={`home-page ${busy ? 'camera-busy' : ''}`} aria-busy={busy} {...(busy ? { inert: '' } : {})}>
        <header className="adaptive-home-heading"><span>DI TÍCH ĐÔI BỜ HIỀN LƯƠNG – BẾN HẢI</span><h1>Vĩ tuyến 17</h1><p>Chọn một điểm đến để khám phá hiện vật và tư liệu.</p></header>
        {renderTools(true)}
        <MapCamera zone={navigation.zone} phase={navigation.phase} stageRef={mapRef}>
          <div className="home-hitboxes">
            {zones.map(zone => (
              <button key={zone.id} data-zone={zone.id} className={`hotspot ${zone.id} home-place-card`} onClick={() => openZone(zone)} aria-label={`Khám phá ${zone.title}`}>
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
        </MapCamera>
        <NarratorWidget />
        <nav className="adaptive-destinations" aria-label="Chọn địa điểm tham quan">
          {zones.map(zone => (
            <button key={zone.id} data-zone={zone.id} onClick={() => openZone(zone)}>
              <img src={mediaByZone[zone.id].hero.url} alt="" loading="lazy" />
              <span><strong>{zone.title}</strong><small>{zone.id === 'museum' ? 'Cạnh đường chính · đối diện khu Kỳ đài' : zone.short}</small></span>
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
                <button key={zone.id} onClick={() => openZone(zone, homePanel === 'photos' ? 'photos' : 'story')}>
                  <img src={mediaByZone[zone.id].hero.url} alt="" />
                  <span>{zone.title}<small>{homePanel === 'photos' ? 'Xem ảnh địa điểm' : 'Đọc câu chuyện'}</small></span>
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

  if (active.id === 'museum') {
    return <MuseumExhibition tools={renderTools()} chat={chat} narrator={<NarratorWidget />} notice={notice}
      onDismissNotice={() => setNotice('')} onBackMap={backHome}
      documents={documents} loading={loadingDocuments} error={documentError}
      onRetry={() => setDocumentAttempt(attempt => attempt + 1)} initialPanel={tab === 'photos' ? 'photos' : 'story'}
    />;
  }

  const media = mediaByZone[active.id];
  return <DestinationScene key={active.id} title={active.title}
    image={{ src: media.hero.url, alt: media.hero.title }} tools={renderTools()} chat={chat} narrator={<NarratorWidget />}
    notice={notice} onDismissNotice={() => setNotice('')} onBack={backHome} photos={media.photos}
    initialPanel={tab === 'photos' ? 'photos' : undefined}
    overview={<>
      <p>{documents[0]?.content || active.description}</p>
      {documents[0]?.source && <small>Nguồn: {documents[0].source}</small>}
      {loadingDocuments && <p role="status">Đang tải tư liệu…</p>}
      {documentError && <div role="alert"><p>{documentError}</p><button onClick={() => setDocumentAttempt(attempt => attempt + 1)}>Tải lại tư liệu</button></div>}
      {documents.slice(1).map(document => <details key={document.id}><summary>{document.title}</summary><p>{document.content}</p><small>Nguồn: {document.source || 'Chưa ghi nguồn'}</small></details>)}
    </>}
  />;
}

createRoot(document.getElementById('root')!).render(<App />);
