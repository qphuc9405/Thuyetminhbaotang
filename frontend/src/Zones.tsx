import { useMemo, useState, type ReactNode } from 'react';
import { BookOpen, CalendarDays, ChevronDown, ChevronRight, ChevronUp, ExternalLink, Image as ImageIcon, Landmark } from 'lucide-react';
import NarrationBar from './Narration';
import { useAudio } from './Narration';
import { GuideBubble, NarratorGuide } from './Guide';
import { BackButton, Breadcrumb, Loading, PhotoGrid, Sources, useLoad } from './common';
import { speak } from './audio';
import { narrators } from './guides';
import { pick, tr, useLang, useT, ZONE_TEXT } from './i18n';
import { mgUrl, type Citation, type MgImage, type PlaceZone, type StoryZone } from './mg';
import Lightbox from './Lightbox';

type Common = { onBack: () => void; tools: ReactNode; renderChat: (suggestions: string[], placeholder: string) => ReactNode };
type Item = { key: string; kicker: string; title: string; paras: string[]; cites: Citation[]; image?: MgImage; translated: boolean };

/** Đoạn văn có giới hạn: mặc định 2 đoạn, bấm "Đọc tiếp" để mở hết – chừa chỗ cho người hướng dẫn. */
function Paras({ paras, id }: { paras: string[]; id: string }) {
  const t = useT();
  const [open, setOpen] = useState(false);
  const shown = open ? paras : paras.slice(0, 2);
  return (
    <>
      <div className="exhibit-text" key={id}>{shown.map((p, i) => <p key={i} style={{ animationDelay: `${120 + i * 120}ms` }}>{p}</p>)}</div>
      {paras.length > 2 && (
        <button className="read-more" onClick={() => setOpen(v => !v)} aria-expanded={open}>
          {open ? <><ChevronUp size={16} /> {t('readLess')}</> : <><ChevronDown size={16} /> {t('readMore')}</>}
        </button>
      )}
    </>
  );
}

/* ------------------------------------------------------------------ CẦU / KỲ ĐÀI: câu chuyện */
export function StoryZoneView(p: Common & { zoneId: 'bridge' | 'flag'; background: string }) {
  const lang = useLang();
  const t = useT();
  const audio = useAudio();
  const narrator = narrators[p.zoneId];
  const title = ZONE_TEXT[p.zoneId].title[lang];
  const { data, error, retry } = useLoad<StoryZone>(`/api/zones/${p.zoneId}`);
  const [tab, setTab] = useState<'stories' | 'timeline' | 'photos'>('stories');
  const [sel, setSel] = useState<string>('');
  const [lb, setLb] = useState<number | null>(null);
  const imgById = useMemo(() => new Map((data?.images ?? []).map(i => [i.image_id, i])), [data]);
  const stories: Item[] = useMemo(() => (data?.stories ?? []).map(a => ({
    key: a.id, kicker: a.period, title: pick(a.title, lang) ?? a.title.vi, paras: pick(a.body, lang) ?? a.body.vi, cites: a.citations,
    image: a.image_ids.map(id => imgById.get(id)).find(Boolean) ?? data?.images[0], translated: lang !== 'vi',
  })), [data, imgById, lang]);
  const events: Item[] = useMemo(() => (data?.events ?? []).map(e => ({
    key: e.event_id, kicker: e.date_label, title: pick(e.title_i18n, lang) ?? e.title, paras: [pick(e.summary_i18n, lang) ?? e.summary],
    cites: [{ source_id: e.source_id, source_title: e.source_title, source_type: e.source_id === 'SRC001' ? 'BOOK' : 'OTHER', printed_page: e.printed_page, provision: null, verified_anchor: true }],
    translated: lang !== 'vi',
  })), [data, lang]);
  const all = [...stories, ...events];
  const cur = all.find(x => x.key === sel) ?? stories[0];
  const bg = cur?.image ? mgUrl(cur.image.medium_url ?? cur.image.image_url) : p.background;
  const intro = t(p.zoneId === 'bridge' ? 'bridgeIntro' : 'flagIntro');

  return (
    <main className="zone-page story-zone zone-enter guided">
      <img className="zone-bg kenburns" src={bg} alt="" key={bg} />
      <div className="zone-bg-shade" />
      <header className="zone-header">
        <div className="zone-brand"><span className="zone-logo">{t('brand')}</span><Breadcrumb items={[title, cur?.title ?? '…']} onHome={p.onBack} /></div>
        {p.tools}
      </header>
      <BackButton onClick={p.onBack} label={t('backMap')} />

      {!data ? <Loading error={error} onRetry={retry} /> : cur && (
        <>
          <section className="story-reader" key={`${cur.key}-${lang}`}>
            <p className="story-kicker">{title.toUpperCase()} · {cur.kicker}</p>
            <h1>{cur.title}</h1>
            <p className="story-intro">{intro}</p>
            <Paras paras={cur.paras} id={cur.key} />
            <Sources cites={cur.cites} />
            {cur.translated && <p className="tr-note">{t('translationNote')}</p>}
            <NarrationBar id={`${p.zoneId}-${cur.key}`} text={`${cur.title}. ${cur.paras.join(' ')}`} voiceId={narrator.voice} />
          </section>
          <aside className="story-list-panel">
            <div className="resource-tabs" role="tablist">
              <button role="tab" aria-selected={tab === 'stories'} className={tab === 'stories' ? 'selected' : ''} onClick={() => setTab('stories')}><BookOpen size={16} /> {t('tabStories')}</button>
              <button role="tab" aria-selected={tab === 'timeline'} className={tab === 'timeline' ? 'selected' : ''} onClick={() => setTab('timeline')}><CalendarDays size={16} /> {t('tabTimeline')}</button>
              <button role="tab" aria-selected={tab === 'photos'} className={tab === 'photos' ? 'selected' : ''} onClick={() => setTab('photos')}><ImageIcon size={16} /> {t('tabPhotos')} ({data.images.length})</button>
            </div>
            <div className="story-list-body">
              {tab === 'stories' && stories.map((s, i) => (
                <button key={s.key} className={`story-card ${cur.key === s.key ? 'chosen' : ''}`} onClick={() => setSel(s.key)}>
                  <span className="story-index">0{i + 1}</span><span><small>{s.kicker}</small><strong>{s.title}</strong></span><ChevronRight size={18} />
                </button>
              ))}
              {tab === 'timeline' && <ol className="zone-timeline">{events.map(e => (
                <li key={e.key}><button className={cur.key === e.key ? 'chosen' : ''} onClick={() => setSel(e.key)}><b>{e.kicker}</b><span>{e.title}</span></button></li>
              ))}</ol>}
              {tab === 'photos' && <PhotoGrid images={data.images} className="small" />}
            </div>
          </aside>
          {cur.image && (
            <button className="story-photo-chip" onClick={() => setLb(0)} aria-label={t('enlarge')}>
              <img src={mgUrl(cur.image.thumb_url)} alt="" /><span>{t('enlarge')}</span>
            </button>
          )}
        </>
      )}
      <div className="zone-guide"><NarratorGuide narrator={narrator} /></div>
      <GuideBubble className="zone-bubble" speaking={audio.status === 'playing'} text={`${tr(lang, 'homeHello')} ${intro}.`} />
      <div className="zone-chat">{p.renderChat(ZONE_TEXT[p.zoneId].questions[lang], tr(lang, 'askAbout', { x: title }))}</div>
      {lb !== null && cur?.image && <Lightbox items={[{ src: mgUrl(cur.image.image_url), title: cur.image.title_en && lang === 'en' ? cur.image.title_en : cur.image.title_zh && lang === 'zh' ? cur.image.title_zh : cur.image.title, caption: cur.image.caption, meta: cur.image.image_id }]} index={0} onIndex={() => {}} onClose={() => setLb(null)} />}
    </main>
  );
}

/* ------------------------------------------------------------------ TƯỢNG ĐÀI / NHÀ LIÊN HỢP: ảnh + lịch sử hình thành */
export function PlaceView(p: Common & { zoneId: 'monument' | 'union' }) {
  const lang = useLang();
  const t = useT();
  const audio = useAudio();
  const narrator = narrators[p.zoneId];
  const { data, error, retry } = useLoad<PlaceZone>(`/api/zones/${p.zoneId}`);
  const [i, setI] = useState(0);
  const im = data?.local_images[i];
  const title = data ? pick(data.title_i18n, lang) ?? data.title : ZONE_TEXT[p.zoneId].title[lang];
  const subtitle = data ? pick(data.subtitle_i18n, lang) ?? data.subtitle : '';
  const paras = data ? pick(data.paragraphs_i18n, lang) ?? data.paragraphs : [];
  return (
    <main className="zone-page place-zone zone-enter guided">
      {im && <img className="zone-bg kenburns" src={im.url} alt="" key={im.url} />}
      <div className="zone-bg-shade" />
      <header className="zone-header">
        <div className="zone-brand"><span className="zone-logo">{t('brand')}</span><Breadcrumb items={[title]} onHome={p.onBack} /></div>
        {p.tools}
      </header>
      <BackButton onClick={p.onBack} label={t('backMap')} />
      {!data ? <Loading error={error} onRetry={retry} /> : (
        <>
          <figure className="place-photo" key={im?.url}>
            {im && <img src={im.url} alt={im.title} />}
            <figcaption>{im?.title}<small>{im?.credit}</small></figcaption>
            {data.local_images.length > 1 && <div className="room-alts">{data.local_images.map((x, k) => (
              <button key={x.url} className={k === i ? 'active' : ''} onClick={() => setI(k)} aria-label={x.title}><img src={x.url} alt="" /></button>
            ))}</div>}
          </figure>
          <aside className="exhibit-panel" key={lang}>
            <div className="exhibit-panel-head"><Landmark size={34} aria-hidden="true" /><div><small>{subtitle}</small><h1>{title}</h1></div></div>
            <h2 className="place-h2">{t('history')}</h2>
            <Paras paras={paras} id={`${p.zoneId}-${lang}`} />
            <Sources cites={data.citations} />
            <p className="place-note"><ExternalLink size={13} /> {t('placeNote')}{lang !== 'vi' ? ` ${t('translationNote')}` : ''}</p>
            <NarrationBar id={`place-${p.zoneId}`} text={`${title}. ${paras.join(' ')}`} voiceId={narrator.voice} />
          </aside>
        </>
      )}
      <div className="zone-guide"><NarratorGuide narrator={narrator} /></div>
      <GuideBubble className="zone-bubble" speaking={audio.status === 'playing'} text={`${tr(lang, 'homeHello')} ${subtitle || ZONE_TEXT[p.zoneId].short[lang]}.`}
        onListen={() => { if (data) void speak(`place-${p.zoneId}|${lang}`, `${title}. ${paras.join(' ')}`, lang, narrator.voice); }} />
      <div className="zone-chat">{p.renderChat(ZONE_TEXT[p.zoneId].questions[lang], tr(lang, 'askAbout', { x: title }))}</div>
    </main>
  );
}
