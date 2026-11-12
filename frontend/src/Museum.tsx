import { useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState, type CSSProperties, type PointerEvent as RPointerEvent, type ReactNode } from 'react';
import { AlertTriangle, BookOpen, ChevronDown, ChevronLeft, ChevronRight, ChevronUp, ExternalLink, FileText, Image as ImageIcon, Info, Landmark, MapPin } from 'lucide-react';
import NarrationBar, { useAudio } from './Narration';
import { GuideBubble, NarratorGuide } from './Guide';
import { BackButton, Breadcrumb, Loading, PhotoGrid, PhotosModal, Sources, StoriesModal, useLoad } from './common';
import { speak, stopAll } from './audio';
import { narrators } from './guides';
import { pick, tr, useLang, useT, ZONE_TEXT, type Lang } from './i18n';
import { mgUrl, type L3, type MuseumZone, type Topic, type TopicItem, type TopicsHall } from './mg';

export type MuseumProps = {
  onBack: () => void;
  tools: ReactNode;
  renderChat: (suggestions: string[], placeholder: string) => ReactNode;
};

const ZOOM_MS = 900;
const narrator = narrators.museum;
const ROOM_RATIO = 1672 / 725;
type Target = { x: number; y: number; s: number } | null;
type Route = { topic: string | null; item: string | null; intro: boolean };

/** #museum, #museum/gioi-thieu, #museum/topic-2, #museum/topic-2/choi-loa */
const parseRoute = (): Route => {
  const [, a = '', b = ''] = window.location.hash.replace(/^#/, '').split('?')[0].split('/');
  if (a === 'gioi-thieu') return { topic: null, item: null, intro: true };
  return { topic: a.startsWith('topic-') ? a : null, item: b || null, intro: false };
};
const routeHash = (r: Route) => (r.intro ? '#museum/gioi-thieu' : r.topic ? `#museum/${r.topic}${r.item ? `/${r.item}` : ''}` : '#museum');

const useReduce = () => useMemo(() => window.matchMedia?.('(prefers-reduced-motion: reduce)').matches ?? false, []);
const L = (m: L3 | null | undefined, lang: Lang) => (m ? pick(m, lang) ?? m.vi : '');

/** Kích thước vùng xem (theo dõi khi đổi cỡ cửa sổ). */
function useViewport(ref: React.RefObject<HTMLElement>, dep: unknown) {
  const [vp, setVp] = useState({ w: 1280, h: 640 });
  useLayoutEffect(() => {
    const el = ref.current;
    if (!el) return;
    const update = () => setVp({ w: el.clientWidth, h: el.clientHeight });
    update();
    const ro = typeof ResizeObserver !== 'undefined' ? new ResizeObserver(update) : null;
    ro?.observe(el);
    window.addEventListener('resize', update);
    return () => { ro?.disconnect(); window.removeEventListener('resize', update); };
  }, [dep]);
  return vp;
}

/**
 * Camera trên một ảnh nền phủ kín (cover): đưa điểm (x%, y%) về giữa phần nhìn thấy
 * (trừ cột danh sách bên trái / panel bên phải), giữ ảnh phủ kín phần nhìn thấy.
 */
function camera(vp: { w: number; h: number }, ratio: number, target: Target, inset = { l: 0, r: 0, b: 0 }, pan: number | null = null) {
  let H = vp.h, W = H * ratio;
  if (W < vp.w) { W = vp.w; H = W / ratio; }
  const minPan = Math.min(0, vp.w - W);
  if (!target) {
    const x = pan === null ? minPan / 2 : Math.max(minPan, Math.min(0, pan));
    return { W, H, x, y: (vp.h - H) / 2, s: 1, minPan };
  }
  const s = target.s;
  const visL = inset.l, visR = vp.w - inset.r, visB = vp.h - inset.b;
  const cx = (visL + visR) / 2, cy = visB / 2;
  let x = cx - s * (target.x / 100) * W;
  let y = cy - s * (target.y / 100) * H;
  x = Math.max(visR - s * W, Math.min(0, x));
  y = Math.max(vp.h - s * H, Math.min(0, y));
  return { W, H, x, y, s, minPan };
}

/** Ô ảnh cắt từ ảnh nền tại một điểm (dùng cho thẻ chủ đề / hiện vật chưa có ảnh tư liệu). */
/** Cuộn một hàng/cột chứa phần tử đang chọn vào giữa – không làm cuộn cả trang. */
function centerIn(row: HTMLElement | null | undefined, smooth: boolean) {
  const el = row?.querySelector<HTMLElement>('[aria-current="true"]');
  if (!row || !el) return;
  const horiz = row.scrollWidth > row.clientWidth + 2;
  const opts: ScrollToOptions = horiz
    ? { left: el.offsetLeft - (row.clientWidth - el.offsetWidth) / 2 }
    : { top: el.offsetTop - (row.clientHeight - el.offsetHeight) / 2 };
  row.scrollTo?.({ ...opts, behavior: smooth ? 'smooth' : 'auto' });
}

const crop = (src: string, x: number, y: number, z = 3): CSSProperties => ({
  backgroundImage: `url(${src})`, backgroundSize: `${z * 100}% auto`, backgroundPosition: `${x}% ${y}%`, backgroundRepeat: 'no-repeat',
});

export default function MuseumTopics(props: MuseumProps) {
  const { data, error, retry } = useLoad<MuseumZone>('/api/zones/museum');
  const [route, setRoute] = useState<Route>(parseRoute);
  const [entering, setEntering] = useState<string | null>(null); // đang phóng tới chủ đề
  const [returning, setReturning] = useState<string | null>(null); // vừa rời chủ đề, lùi camera
  const reduce = useReduce();
  const timer = useRef<ReturnType<typeof setTimeout>>();
  const hallData = data?.topics;
  const routeRef = useRef(route);
  routeRef.current = route;

  useEffect(() => {
    const sync = () => {
      if (!window.location.hash.startsWith('#museum')) return;
      setEntering(null);
      const next = parseRoute();
      if (routeRef.current.topic && next.topic !== routeRef.current.topic) stopAll();
      setRoute(next);
    };
    window.addEventListener('popstate', sync);
    return () => { window.removeEventListener('popstate', sync); clearTimeout(timer.current); };
  }, []);

  const go = useCallback((r: Route, mode: 'push' | 'replace' = 'push') => {
    const h = routeHash(r);
    if (window.location.hash !== h) (mode === 'push' ? history.pushState : history.replaceState).call(history, history.state, '', h);
    setRoute(r);
  }, []);

  const openTopic = (id: string, item: string | null = null) => {
    if (entering) return;
    stopAll();
    if (route.topic || reduce) { go({ topic: id, item, intro: false }); return; }
    setEntering(id);
    timer.current = setTimeout(() => { setEntering(null); go({ topic: id, item, intro: false }); }, ZOOM_MS);
  };
  const toRoom = (intro = false) => {
    const from = route.topic;
    stopAll();
    go({ topic: null, item: null, intro });
    if (from && !reduce && !intro) {
      setReturning(from);
      timer.current = setTimeout(() => setReturning(null), ZOOM_MS + 60);
    }
  };

  if (!hallData) {
    return (
      <main className="zone-page hall-page zone-enter">
        <header className="zone-header hall-header">
          <div className="zone-brand"><span className="zone-logo">{tr('vi', 'brand')}</span></div>{props.tools}
        </header>
        <Loading error={error} onRetry={retry} />
      </main>
    );
  }
  const topic = hallData.topics.find(t => t.id === route.topic) ?? null;
  if (topic) {
    return <TopicView key={topic.id} {...props} hall={hallData} topic={topic} itemId={route.item}
      onItem={id => go({ topic: topic.id, item: id, intro: false }, 'replace')}
      onTopic={id => (id === 'khanh-tiet' ? toRoom(true) : openTopic(id))} onRoom={() => toRoom()} />;
  }
  return <RoomView {...props} hall={hallData} intro={route.intro} entering={entering} returning={returning}
    onIntro={open => go({ topic: null, item: null, intro: open }, open ? 'push' : 'replace')} onTopic={openTopic} />;
}

/* ===================================================================== phòng chính */
function RoomView({ onBack, tools, renderChat, hall, intro, entering, returning, onIntro, onTopic }: MuseumProps & {
  hall: TopicsHall; intro: boolean; entering: string | null; returning: string | null;
  onIntro: (open: boolean) => void; onTopic: (id: string, item?: string | null) => void;
}) {
  const lang = useLang();
  const t = useT();
  const audio = useAudio();
  const reduce = useReduce();
  const viewport = useRef<HTMLDivElement>(null);
  const strip = useRef<HTMLDivElement>(null);
  const vp = useViewport(viewport, true);
  const [pan, setPan] = useState<number | null>(null);
  const [dragging, setDragging] = useState(false);
  const [hover, setHover] = useState<string | null>(null);
  const [modal, setModal] = useState<'photos' | 'stories' | null>(null);
  const [expanded, setExpanded] = useState(false);
  const [settle, setSettle] = useState(false);
  const [instant, setInstant] = useState(!!returning);
  const drag = useRef<{ x: number; p: number; moved: boolean } | null>(null);
  const mobile = vp.w < 760;
  const panelW = mobile ? 0 : Math.min(vp.w * 0.34, 470);
  const title = ZONE_TEXT.museum.title[lang];

  const enteringTopic = hall.topics.find(x => x.id === (entering ?? returning));
  const target: Target = enteringTopic && (entering || instant)
    ? { x: enteringTopic.focus[0], y: enteringTopic.focus[1], s: enteringTopic.focus[2] }
    : intro ? { x: hall.intro.focus[0], y: hall.intro.focus[1], s: mobile ? 1.5 : hall.intro.focus[2] } : null;
  const cam = camera(vp, ROOM_RATIO, target, { l: 0, r: intro && !mobile ? panelW + 36 : 0, b: 0 }, pan);

  // rời chủ đề: dựng camera ở chủ đề (không chuyển động) rồi lùi về toàn cảnh
  useEffect(() => {
    if (!returning) return;
    const a = requestAnimationFrame(() => requestAnimationFrame(() => setInstant(false)));
    return () => cancelAnimationFrame(a);
  }, [returning]);
  // ghim chỉ hiện lại khi camera đã đứng yên
  const first = useRef(true);
  useEffect(() => {
    if (first.current && !returning) { first.current = false; return; }
    first.current = false;
    if (reduce) return;
    setSettle(true);
    const id = setTimeout(() => setSettle(false), ZOOM_MS);
    return () => clearTimeout(id);
  }, [intro, returning, reduce]);

  // lời chào của người hướng dẫn (lần đầu vào phòng)
  const greeting = t('roomGreeting');
  const playGreeting = useCallback(() => { void speak(`room-greeting|${lang}`, greeting, lang, narrator.voice); }, [greeting, lang]);
  useEffect(() => {
    const k = `tm-room-greeted-${lang}`;
    try { if (sessionStorage.getItem(k)) return; sessionStorage.setItem(k, '1'); } catch { /* ignore */ }
    if (!audio.muted && !intro) playGreeting();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [lang]);

  useEffect(() => {
    const k = (e: KeyboardEvent) => {
      const tag = (e.target as HTMLElement)?.tagName;
      if (tag === 'INPUT' || tag === 'TEXTAREA' || modal || document.querySelector('.lightbox, .lb2')) return;
      if (e.key === 'Escape' && intro) { stopAll(); onIntro(false); }
    };
    window.addEventListener('keydown', k);
    return () => window.removeEventListener('keydown', k);
  });

  const down = (e: RPointerEvent) => { if (target || cam.minPan === 0) return; drag.current = { x: e.clientX, p: cam.x, moved: false }; };
  const move = (e: RPointerEvent) => {
    const d = drag.current; if (!d) return;
    const dx = e.clientX - d.x;
    if (Math.abs(dx) > 6) { d.moved = true; setDragging(true); }
    if (d.moved) setPan(d.p + dx);
  };
  const up = () => { setDragging(false); setTimeout(() => { drag.current = null; }, 0); };
  const click = (fn: () => void) => () => { if (!drag.current?.moved) fn(); };

  const busy = !!entering;
  const showPins = !target && !settle && !busy;
  const proj = (x: number, y: number) => ({ left: cam.x + cam.s * (x / 100) * cam.W, top: cam.y + cam.s * (y / 100) * cam.H });
  const stageStyle: CSSProperties = {
    width: cam.W, height: cam.H,
    transform: `translate3d(${cam.x}px, ${cam.y}px, 0) scale(${cam.s})`,
    transition: dragging || reduce || instant ? 'none' : `transform ${ZOOM_MS}ms cubic-bezier(.65,0,.35,1)`,
  };
  const introParas = pick(hall.intro.paragraphs, lang) ?? [];
  const shown = expanded ? introParas : introParas.slice(0, 2);
  const suggestions = ZONE_TEXT.museum.questions[lang];
  const speaking = audio.status === 'playing';
  const focusIntro = intro ? proj(hall.intro.focus[0], hall.intro.focus[1]) : null;

  return (
    <main className={`zone-page hall-page mt-room zone-enter ${intro ? 'is-detail' : 'is-overview'} ${busy ? 'is-entering' : ''}`} data-lang={lang} aria-busy={busy}>
      <div className={`hall-viewport ${cam.minPan < 0 && !target ? 'can-pan' : ''} ${dragging ? 'dragging' : ''}`} ref={viewport}
        onPointerDown={down} onPointerMove={move} onPointerUp={up} onPointerCancel={up} onPointerLeave={up}>
        <div className="hall-stage" style={stageStyle}>
          <img className="hall-bg" src={hall.background} alt={t('illustration')} draggable={false} />
        </div>
        {focusIntro && <div className="hall-vignette" style={{ ['--fx' as string]: `${focusIntro.left}px`, ['--fy' as string]: `${focusIntro.top}px` }} aria-hidden="true" />}
      </div>
      {busy && <div className="mt-veil" aria-hidden="true" />}

      <div className={`hall-pins ${showPins ? '' : 'hidden'}`} aria-label={t('topicsNav')}>
        {hall.topics.map((tp, k) => {
          // Chỉ hiển thị icon: tiêu đề chủ đề đã có trên ảnh nền.
          const p = proj(tp.room[0], 43);
          return (
            <button key={tp.id} className={`mt-topic-pin ${hover === tp.id ? 'hover' : ''}`} style={{ ...p, animationDelay: `${250 + k * 90}ms` }}
              onClick={click(() => onTopic(tp.id))} onMouseEnter={() => setHover(tp.id)} onMouseLeave={() => setHover(null)}
              aria-label={`${t('topicNo', { x: tp.no })}: ${L(tp.title, lang)}`} tabIndex={showPins ? 0 : -1}>
              <MapPin size={23} aria-hidden="true" />
            </button>
          );
        })}
        {[{ id: hall.intro.id, room: hall.intro.room, label: hall.intro.label, intro: true, topic: '' }, ...hall.artifacts.map(a => ({ ...a, intro: false }))].map((a, k) => {
          // Đặt nút tượng gần trần nhà, phía trên bảng tên và khuôn mặt.
          const p = proj(a.room[0], a.intro ? 14 : a.room[1]);
          const label = a.intro ? t('introTitle') : L(a.label, lang);
          const side = p.left > vp.w - (mobile ? 150 : 240) ? 'left' : '';
          return (
            <button key={a.id} className={`hall-pin ${a.intro ? 'mt-intro-pin' : side} ${hover === a.id ? 'hover' : ''}`} style={{ ...p, animationDelay: `${650 + k * 70}ms` }}
              onClick={click(() => (a.intro ? onIntro(true) : onTopic(a.topic, a.id)))} onMouseEnter={() => setHover(a.id)} onMouseLeave={() => setHover(null)}
              aria-label={label} tabIndex={showPins ? 0 : -1}>
              <span className="hall-pin-glow" aria-hidden="true" />
              <span className="hall-pin-icon" aria-hidden="true">{a.intro ? <Landmark size={17} /> : <MapPin size={18} />}</span>
              <span className="hall-pin-label">{label}</span>
            </button>
          );
        })}
      </div>

      <header className="zone-header hall-header">
        <div className="zone-brand"><span className="zone-logo">{t('brand')}</span><Breadcrumb items={intro ? [title, t('introTitle')] : [title]} onHome={onBack} /></div>
        {tools}
      </header>
      <div className="hall-back">
        {intro ? <BackButton onClick={() => { stopAll(); onIntro(false); }} label={t('backRoom')} /> : <BackButton onClick={onBack} label={t('backMap')} />}
      </div>

      <div className={`hall-guide ${intro ? 'small' : ''}`}><NarratorGuide narrator={narrator} /></div>
      {!intro && !busy && <GuideBubble className="hall-bubble" text={greeting} speaking={speaking} onListen={playGreeting} autoHide={14000} />}
      {!intro && !busy && <p className="hall-hint" key={lang}><Info size={15} /> {t('roomHint')}</p>}

      {intro && (
        <aside className="hall-panel" aria-label={t('introTitle')}>
          <div className="exhibit-panel-head">
            <Landmark size={30} aria-hidden="true" />
            <div><small>{title}</small><h1>{t('introTitle')}</h1></div>
          </div>
          <div className="hall-panel-body">
            <div className="exhibit-text">{shown.map((p, i) => <p key={`${lang}-${i}`} style={{ animationDelay: `${180 + i * 120}ms` }}>{p}</p>)}</div>
            {introParas.length > 2 && (
              <button className="read-more" onClick={() => setExpanded(v => !v)} aria-expanded={expanded}>
                {expanded ? <><ChevronUp size={16} /> {t('readLess')}</> : <><ChevronDown size={16} /> {t('readMore')}</>}
              </button>
            )}
            <div className="mt-intro-topics">
              {hall.topics.map(tp => (
                <button key={tp.id} onClick={() => onTopic(tp.id)}>
                  <span className="mt-topic-no" aria-hidden="true">{tp.no}</span>
                  <span><strong>{L(tp.title, lang)}</strong><small>{L(tp.subtitle, lang)}</small></span>
                  <ChevronRight size={18} />
                </button>
              ))}
            </div>
            <h2 className="panel-h2"><ImageIcon size={16} /> {t('archivePhotos')}</h2>
            <PhotoGrid images={hall.intro.images} className="small" />
            <Sources cites={hall.intro.citations} />
            {lang !== 'vi' && <p className="tr-note">{t('translationNote')}</p>}
          </div>
          <NarrationBar id="room-intro" text={`${t('introTitle')}. ${introParas.join(' ')}`} voiceId={narrator.voice} />
        </aside>
      )}

      <div className="hall-bottom">
        <div className="hall-actions">
          <button className="hall-action" onClick={() => setModal('photos')}><ImageIcon size={20} /><span>{t('photos')}</span></button>
          <div className="hall-chat">{renderChat(suggestions, tr(lang, 'askAbout', { x: title }))}</div>
          <button className="hall-action" onClick={() => setModal('stories')}><BookOpen size={20} /><span>{t('stories')}</span></button>
        </div>
        <TopicStrip hall={hall} current={intro ? 'khanh-tiet' : entering} stripRef={strip}
          onPick={id => (id === 'khanh-tiet' ? onIntro(!intro) : onTopic(id))} />
      </div>

      {modal === 'photos' && <PhotosModal onClose={() => setModal(null)} />}
      {modal === 'stories' && <StoriesModal onClose={() => setModal(null)} voice={narrator.voice} />}
    </main>
  );
}

/** Thanh hành trình: Tượng Chủ tịch Hồ Chí Minh + 4 chủ đề. */
function TopicStrip({ hall, current, onPick, stripRef, compact = false }: {
  hall: TopicsHall; current: string | null; onPick: (id: string) => void; stripRef?: React.RefObject<HTMLDivElement>; compact?: boolean;
}) {
  const lang = useLang();
  const t = useT();
  const cards = [
    { id: 'khanh-tiet', no: 0, label: t('introTitle'), sub: '', style: crop(hall.background, hall.intro.focus[0], hall.intro.focus[1] - 6, 3.2) },
    ...hall.topics.map(tp => ({ id: tp.id, no: tp.no, label: L(tp.short, lang), sub: t('topicNo', { x: tp.no }), style: crop(hall.background, tp.focus[0], tp.focus[1] - 4, 3) })),
  ];
  useEffect(() => {
    centerIn(stripRef?.current, true);
  }, [current, stripRef]);
  return (
    <nav className={`mt-strip ${compact ? 'compact' : ''}`} aria-label={t('topicsNav')}>
      <div className="mt-strip-row" ref={stripRef}>
        {cards.map((c, k) => (
          <button key={c.id} className="mt-card" aria-current={current === c.id} onClick={() => onPick(c.id)} style={{ animationDelay: `${k * 50}ms` }}>
            <span className="mt-card-img" style={c.style} aria-hidden="true">{c.no ? <i>{c.no}</i> : null}</span>
            <span className="mt-card-text">{c.sub && <small>{c.sub}</small>}<strong>{c.label}</strong></span>
          </button>
        ))}
      </div>
    </nav>
  );
}

/* ===================================================================== trang chủ đề */
function TopicView({ onBack, tools, renderChat, hall, topic, itemId, onItem, onTopic, onRoom }: MuseumProps & {
  hall: TopicsHall; topic: Topic; itemId: string | null; onItem: (id: string) => void; onTopic: (id: string) => void; onRoom: () => void;
}) {
  const lang = useLang();
  const t = useT();
  const reduce = useReduce();
  const viewport = useRef<HTMLDivElement>(null);
  const strip = useRef<HTMLDivElement>(null);
  const list = useRef<HTMLDivElement>(null);
  const vp = useViewport(viewport, topic.id);
  const [expanded, setExpanded] = useState(false);
  const [hover, setHover] = useState<string | null>(null);
  const items = topic.items;
  const cur: TopicItem = items.find(i => i.id === itemId) ?? items[0];
  const idx = items.indexOf(cur);
  const mobile = vp.w < 700 || window.innerWidth < 760;
  const panelW = mobile ? 0 : Math.min(vp.w * 0.31, 440);
  const listW = mobile ? 0 : Math.min(250, vp.w * 0.19);

  // ảnh cảnh: ảnh riêng của chủ đề (nếu có) hoặc phòng chính nhìn gần vào góc chủ đề
  const scene = topic.scene;
  const src = scene?.src ?? hall.background;
  const ratio = scene ? scene.width / scene.height : ROOM_RATIO;
  const pt = (it: TopicItem) => (scene ? it.scene : it.room);
  const base: Target = scene ? { x: 50, y: 50, s: 1 } : { x: topic.focus[0], y: topic.focus[1], s: topic.focus[2] };
  const p = pt(cur);
  const target: Target = p ? { x: p[0], y: p[1], s: (base?.s ?? 1) * (scene ? 1.04 : 1.12) } : base;
  const inset = { l: mobile ? 0 : listW + 30, r: mobile ? 0 : panelW + 34, b: mobile ? 0 : 118 };
  const cam = camera(vp, ratio, target, inset);
  const proj = (x: number, y: number) => ({ left: cam.x + cam.s * (x / 100) * cam.W, top: cam.y + cam.s * (y / 100) * cam.H });

  const paras = pick(cur.paragraphs, lang) ?? [];
  const shown = expanded ? paras : paras.slice(0, 2);
  const label = (x: TopicItem) => L(x.label, lang);
  const title = ZONE_TEXT.museum.title[lang];
  const step = (d: number) => { setExpanded(false); onItem(items[(idx + d + items.length) % items.length].id); };
  useEffect(() => setExpanded(false), [cur.id]);
  useEffect(() => {
    centerIn(list.current, !reduce);
  }, [cur.id, reduce]);
  useEffect(() => {
    const k = (e: KeyboardEvent) => {
      const tag = (e.target as HTMLElement)?.tagName;
      if (tag === 'INPUT' || tag === 'TEXTAREA' || document.querySelector('.modal-veil, .lightbox, .lb2')) return;
      if (e.key === 'Escape') onRoom();
      if (e.key === 'ArrowDown' || e.key === 'ArrowRight') { e.preventDefault(); step(1); }
      if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') { e.preventDefault(); step(-1); }
    };
    window.addEventListener('keydown', k);
    return () => window.removeEventListener('keydown', k);
  });

  const thumb = (it: TopicItem): CSSProperties | null => {
    if (it.images[0]) return { backgroundImage: `url(${mgUrl(it.images[0].thumb_url)})`, backgroundSize: 'cover', backgroundPosition: 'center' };
    const q = pt(it);
    return q ? crop(src, q[0], q[1], scene ? 4 : 6) : null;
  };
  const suggestions = [tr(lang, 'qMore', { x: label(cur) }), tr(lang, 'qTopic', { x: L(topic.short, lang) })];
  const stageStyle: CSSProperties = {
    width: cam.W, height: cam.H,
    transform: `translate3d(${cam.x}px, ${cam.y}px, 0) scale(${cam.s})`,
    transition: reduce ? 'none' : `transform ${ZOOM_MS}ms cubic-bezier(.65,0,.35,1)`,
  };
  const needs = cur.needs_source;
  const visL = inset.l - 10, visR = vp.w - inset.r + 10;

  return (
    <main className="zone-page mt-page zone-enter" data-lang={lang} data-topic={topic.id}>
      <div className="mt-viewport" ref={viewport}>
        <div className="hall-stage" style={stageStyle}>
          <img className="hall-bg" src={src} alt={t('illustration')} draggable={false} />
        </div>
        <div className="mt-scene-shade" aria-hidden="true" />
        <div className="mt-item-pins">
          {items.map((it, k) => {
            const q = pt(it);
            if (!q) return null;
            const s = proj(q[0], q[1]);
            if (!mobile && (s.left < visL || s.left > visR || s.top > vp.h - 205 || s.top < 70)) return null;
            if (s.left < 0 || s.left > vp.w || s.top < 0 || s.top > vp.h) return null;
            return (
              <button key={it.id} className={`mt-item-pin ${it.id === cur.id ? 'on' : ''} ${hover === it.id ? 'hover' : ''} ${s.left + 44 + label(it).length * (lang === 'zh' ? 13 : 7.4) > (mobile ? vp.w : visR) ? 'flip' : ''}`} style={{ ...s, animationDelay: `${400 + k * 60}ms` }}
                onClick={() => onItem(it.id)} onMouseEnter={() => setHover(it.id)} onMouseLeave={() => setHover(null)} aria-label={label(it)} aria-current={it.id === cur.id}>
                <span>{k + 1}</span><em>{label(it)}</em>
              </button>
            );
          })}
        </div>
      </div>

      <header className="zone-header hall-header">
        <div className="zone-brand"><span className="zone-logo">{t('brand')}</span>
          <Breadcrumb items={[title, `${t('topicNo', { x: topic.no })}: ${L(topic.short, lang)}`]} onHome={onBack} /></div>
        {tools}
      </header>
      <div className="mt-back"><BackButton onClick={onRoom} label={t('backRoom')} /></div>

      <section className="mt-banner" aria-label={L(topic.title, lang)}>
        <small>{t('topicNo', { x: topic.no })}</small>
        <h1>{L(topic.title, lang)}</h1>
        <p>{L(topic.subtitle, lang)}</p>
      </section>

      <nav className="mt-list" aria-label={t('itemsOfTopic')}>
        <h2>{t('itemsOfTopic')}</h2>
        <div className="mt-list-row" ref={list}>
          {items.map((it, k) => {
            const th = thumb(it);
            return (
              <button key={it.id} className="mt-list-item" aria-current={it.id === cur.id} onClick={() => onItem(it.id)} style={{ animationDelay: `${120 + k * 60}ms` }}
                onMouseEnter={() => setHover(it.id)} onMouseLeave={() => setHover(null)}>
                <span className="mt-list-thumb" style={th ?? undefined} aria-hidden="true">{!th && <FileText size={22} />}</span>
                <span className="mt-list-text"><strong>{label(it)}</strong>{it.needs_source && <em className="mt-badge"><AlertTriangle size={11} /> {t('needsSource')}</em>}</span>
              </button>
            );
          })}
        </div>
      </nav>

      <div className="mt-guide"><NarratorGuide narrator={narrator} /></div>

      <aside className="mt-panel" key={`${cur.id}-${lang}`} aria-label={label(cur)}>
        <div className="mt-panel-head">
          <BookOpen size={26} aria-hidden="true" />
          <div><small>{t('topicNo', { x: topic.no })} · {t('itemOf', { a: idx + 1, b: items.length })}</small><h2>{label(cur)}</h2></div>
          <span className="hall-panel-nav">
            <button onClick={() => step(-1)} aria-label={t('prev')} title={t('prev')}><ChevronLeft size={18} /></button>
            <button onClick={() => step(1)} aria-label={t('next')} title={t('next')}><ChevronRight size={18} /></button>
          </span>
        </div>
        <div className="mt-panel-body">
          {needs && (
            <div className="mt-needs" role="note">
              <AlertTriangle size={18} aria-hidden="true" />
              <p><strong>{t('needsSource')}.</strong> {L(cur.needs_note, lang) || t('needsSourceLong')}</p>
            </div>
          )}
          <div className="exhibit-text">{shown.map((x, i) => <p key={i} style={{ animationDelay: `${160 + i * 110}ms` }}>{x}</p>)}</div>
          {paras.length > 2 && (
            <button className="read-more" onClick={() => setExpanded(v => !v)} aria-expanded={expanded}>
              {expanded ? <><ChevronUp size={16} /> {t('readLess')}</> : <><ChevronDown size={16} /> {t('readMore')}</>}
            </button>
          )}
          <h3 className="panel-h2"><ImageIcon size={16} /> {t('archivePhotos')}</h3>
          {cur.images.length ? <PhotoGrid images={cur.images} className="small" /> : !cur.links.length && <p className="panel-empty">{t('noArchivePhoto')}</p>}
          {!!cur.links.length && (
            <ul className="mt-links">
              {cur.links.map(l => (
                <li key={l.source_id}><a href={l.url} target="_blank" rel="noreferrer"><ExternalLink size={14} /> {t('photoAtSource')}: <span>{l.publisher}</span></a></li>
              ))}
            </ul>
          )}
          <Sources cites={cur.citations} />
          <p className="tr-note">{t('illustration')}{lang !== 'vi' ? ` ${t('translationNote')}` : ''}</p>
        </div>
        <NarrationBar id={`topic-${cur.id}`} text={`${label(cur)}. ${paras.join(' ')}`} voiceId={narrator.voice} />
      </aside>

      <div className="mt-bottom">
        <div className="mt-chat">{renderChat(suggestions, tr(lang, 'askAbout', { x: label(cur) }))}</div>
        <TopicStrip hall={hall} current={topic.id} stripRef={strip} compact onPick={id => (id === topic.id ? undefined : onTopic(id))} />
      </div>
    </main>
  );
}
