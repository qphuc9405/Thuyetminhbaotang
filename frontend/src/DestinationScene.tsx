import { useEffect, useRef, useState, type CSSProperties, type ReactNode } from 'react';
import { ArrowLeft, BookOpen, Image, X } from 'lucide-react';
import type { Photo } from './media';
import './destination-scene.css';

export type SceneImage = {
  src: string;
  alt: string;
  width?: number;
  height?: number;
  crop?: { x: number; y: number; width: number; height: number };
};
type Props = {
  title: string;
  image: SceneImage;
  tools: ReactNode;
  chat: ReactNode;
  narrator?: ReactNode;
  overview: ReactNode;
  photos: Photo[];
  onBack: () => void;
  backLabel?: string;
  notice: string;
  onDismissNotice: () => void;
  imageOverlay?: ReactNode;
  initialPanel?: 'photos' | 'overview';
  artworkLayout?: boolean;
};

export function DestinationScene(props: Props) {
  const [panel, setPanel] = useState<'photos' | 'overview' | null>(props.initialPanel || null);
  const [expandedPhoto, setExpandedPhoto] = useState<Photo | null>(null);
  const [dimensions, setDimensions] = useState({ width: props.image.width || 1672, height: props.image.height || 941 });
  const dialog = useRef<HTMLDialogElement>(null);
  const heading = useRef<HTMLHeadingElement>(null);
  const title = props.title;
  useEffect(() => { heading.current?.focus({ preventScroll: true }); }, [title]);
  useEffect(() => {
    if (panel && !dialog.current?.open) dialog.current?.showModal();
    if (!panel && dialog.current?.open) dialog.current.close();
    setExpandedPhoto(null);
  }, [panel]);

  const crop = props.image.crop;
  const ratio = crop ? dimensions.width * crop.width / (dimensions.height * crop.height) : dimensions.width / dimensions.height;
  const artStyle = crop ? { width: `${10000 / crop.width}%`, height: `${10000 / crop.height}%`, left: `${-100 * crop.x / crop.width}%`, top: `${-100 * crop.y / crop.height}%` } : undefined;
  const openPanel = (next: 'photos' | 'overview') => { setExpandedPhoto(null); setPanel(next); };

  const controls = <>
    <header className="scene-header">
      <button className="scene-back" onClick={props.onBack} aria-label={props.backLabel || 'Về bản đồ'} title={props.backLabel || 'Về bản đồ'}><ArrowLeft size={20} /><span>{props.backLabel || 'Bản đồ'}</span></button>
      <h1 className="scene-title" ref={heading} tabIndex={-1}>{props.title}</h1>
      <div className="scene-tools">{props.tools}</div>
      {props.notice && <button className="scene-notice" onClick={props.onDismissNotice} aria-label={`Đóng thông báo: ${props.notice}`}><span>{props.notice}</span><X size={15} /></button>}
    </header>
    <div className="scene-space"><div className="scene-narrator">{props.narrator}</div></div>
    <div className="scene-widgets" role="group" aria-label="Tiện ích tham quan">
      <button className="scene-widget-button" onClick={() => openPanel('photos')} aria-haspopup="dialog"><Image size={20} /><span>{props.artworkLayout ? 'Hình ảnh tư liệu' : 'Hình ảnh'}</span></button>
      <div className="scene-chat">{props.chat}</div>
      <button className="scene-widget-button" onClick={() => openPanel('overview')} aria-haspopup="dialog"><BookOpen size={20} /><span>{props.artworkLayout ? 'Mở lộ trình tham quan' : 'Mô tả tổng quan'}</span></button>
    </div>
  </>;

  return <main className={`destination-scene${props.artworkLayout ? ' museum-room' : ''}`} style={{ '--scene-ratio': ratio, '--scene-image': `url("${props.image.src}")` } as CSSProperties}>
    <div className="scene-background" aria-hidden="true" />
    <div className="scene-picture">
      <div className="scene-artwork">
        <img className="scene-main-image" src={props.image.src} alt={props.image.alt} style={artStyle} fetchPriority="high" onLoad={event => {
          const image = event.currentTarget;
          setDimensions({ width: image.naturalWidth, height: image.naturalHeight });
        }} />
        {props.imageOverlay}
        {props.artworkLayout && controls}
      </div>
    </div>
    {!props.artworkLayout && controls}
    <dialog ref={dialog} className="scene-dialog" onCancel={event => { event.preventDefault(); setPanel(null); }} onClick={event => { if (event.target === event.currentTarget) setPanel(null); }} aria-labelledby="scene-dialog-title">
      <header className="scene-dialog-header"><div><small>{props.title}</small><h2 id="scene-dialog-title">{panel === 'photos' ? 'Hình ảnh' : 'Mô tả tổng quan'}</h2></div><button autoFocus onClick={() => setPanel(null)} aria-label="Đóng widget"><X size={20} /></button></header>
      {panel === 'overview' ? <div className="scene-overview">{props.overview}</div> : expandedPhoto ? <div className="scene-photo-expanded">
        <button className="scene-text-button" onClick={() => setExpandedPhoto(null)}><ArrowLeft size={16} /> Danh sách hình ảnh</button>
        <figure><img src={expandedPhoto.url} alt={expandedPhoto.title} /><figcaption>{expandedPhoto.title}<small>{expandedPhoto.credit}</small>{expandedPhoto.source && <a href={expandedPhoto.source} target="_blank" rel="noreferrer">Nguồn ảnh</a>}</figcaption></figure>
      </div> : <div className="scene-photos">
        {props.photos.map(photo => <figure key={photo.url}><button onClick={() => setExpandedPhoto(photo)} aria-label={`Xem lớn: ${photo.title}`}><img src={photo.url} alt={photo.title} loading="lazy" onError={event => { if (event.currentTarget.getAttribute('src') !== props.image.src) event.currentTarget.src = props.image.src; }} /></button><figcaption>{photo.title}<small>{photo.credit}</small>{photo.source && <a href={photo.source} target="_blank" rel="noreferrer">Nguồn ảnh</a>}</figcaption></figure>)}
      </div>}
    </dialog>
  </main>;
}
