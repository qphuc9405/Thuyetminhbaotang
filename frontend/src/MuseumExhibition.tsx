import { useEffect, useState, type CSSProperties, type ReactNode } from 'react';
import { ArrowRight } from 'lucide-react';
import { DestinationScene, type SceneImage } from './DestinationScene';
import { museumExhibits, museumRoom } from './museumExhibits';
import { mediaByZone } from './media';
import './museum.css';

type MuseumDocument = { id: string; title: string; content: string; source: string; category: string };
type Props = {
  tools: ReactNode;
  chat: ReactNode;
  narrator: ReactNode;
  notice: string;
  onDismissNotice: () => void;
  onBackMap: () => void;
  documents: MuseumDocument[];
  loading: boolean;
  error: string;
  onRetry: () => void;
  initialPanel?: 'story' | 'photos';
};

export function MuseumExhibition(props: Props) {
  const readRoute = () => museumExhibits.find(item => `#museum/${item.id}` === window.location.hash) || null;
  const [selected, setSelected] = useState(readRoute);
  useEffect(() => {
    const sync = () => setSelected(readRoute());
    window.addEventListener('hashchange', sync);
    window.addEventListener('popstate', sync);
    return () => {
      window.removeEventListener('hashchange', sync);
      window.removeEventListener('popstate', sync);
    };
  }, []);

  const title = selected?.title || 'Nhà trưng bày Vĩ tuyến 17';
  const image: SceneImage = selected?.image ? {
    src: selected.image.src, alt: selected.title, width: selected.image.width, height: selected.image.height,
  } : {
    src: museumRoom, alt: selected ? `Cận cảnh ${selected.title} trong phòng trưng bày minh họa` : 'Không gian Nhà trưng bày Vĩ tuyến 17',
    width: 1672, height: 941, crop: selected?.crop,
  };
  const intro = props.documents[0];
  const overview = <>
    {selected ? <>
      <p className="scene-summary">{selected.summary}</p>
      {selected.paragraphs.map(paragraph => <p key={paragraph}>{paragraph}</p>)}
      <h3>Chi tiết để quan sát</h3>
      <ul>{selected.details.map(detail => <li key={detail}>{detail}</li>)}</ul>
      <small>{selected.image ? 'Ảnh tham khảo do bạn cung cấp.' : 'Hình ảnh và mô tả từ không gian minh họa.'}</small>
    </> : <>
      <p>{intro?.content || 'Khám phá các hiện vật, mô hình và câu chuyện trong Nhà trưng bày Vĩ tuyến 17.'}</p>
      {intro?.source && <small>Nguồn: {intro.source}</small>}
      {props.loading && <p role="status">Đang tải tư liệu…</p>}
      {props.error && <div role="alert"><p>{props.error}</p><button onClick={props.onRetry}>Tải lại tư liệu</button></div>}
    </>}
    <h3>Lộ trình tham quan</h3>
    <nav className="scene-exhibit-links" aria-label="Chọn chủ đề hoặc hiện vật">
      {museumExhibits.map((item, index) => <a key={item.id} href={`#museum/${item.id}`} aria-current={selected?.id === item.id ? 'page' : undefined}><span>{String(index + 1).padStart(2, '0')}</span>{item.title}<ArrowRight size={15} /></a>)}
    </nav>
  </>;
  const photos = selected ? [{
    title: selected.image ? selected.title : `Vị trí ${selected.title} trong phòng trưng bày`,
    url: selected.image?.src || museumRoom,
    credit: selected.image ? 'Ảnh tham khảo do bạn cung cấp' : 'Không gian minh họa của dự án',
  }, { title: 'Tổng quan phòng trưng bày', url: museumRoom, credit: 'Không gian minh họa của dự án' }] : [
    { title: 'Bên trong Nhà trưng bày', url: museumRoom, credit: 'Không gian minh họa của dự án' },
    ...mediaByZone.museum.photos,
  ];

  return <DestinationScene key={selected?.id || 'museum'} title={title} image={image} tools={props.tools} chat={props.chat} narrator={selected ? props.narrator : null} artworkLayout={!selected}
    notice={props.notice} onDismissNotice={props.onDismissNotice} overview={overview} photos={photos}
    onBack={selected ? () => { window.location.hash = '#museum'; } : props.onBackMap}
    backLabel={selected ? 'Về Nhà trưng bày' : 'Về bản đồ'} initialPanel={selected?.topic ? 'overview' : !selected && props.initialPanel === 'photos' ? 'photos' : undefined}
    imageOverlay={!selected ? <>
      <nav className="museum-room-links" aria-label="Bốn chủ đề và các hiện vật trong phòng">
        {museumExhibits.map(item => <a key={item.id} className="museum-room-hitbox" href={`#museum/${item.id}`}
          style={{ left: `${item.point.x}%`, top: `${item.point.y}%` } as CSSProperties}
          aria-label={`${item.topic ? `Chủ đề ${item.topic}: ` : 'Khám phá '}${item.title}`} title={item.title}>
          <span>{item.title}</span>
        </a>)}
      </nav>
      <nav className="museum-topic-timeline" aria-label="Hành trình theo dòng lịch sử Vĩ tuyến 17">
        {museumExhibits.filter(item => item.topic).map(item => <a key={item.id} href={`#museum/${item.id}`} aria-label={`Chủ đề ${item.topic}: ${item.title}`} title={item.title}>
          <span className="museum-topic-number">{item.topic}</span><span><strong>{item.shortTitle}</strong><small>{item.title}</small></span>
        </a>)}
      </nav>
    </> : undefined}
  />;
}
