import { useLayoutEffect, useRef, useState, type CSSProperties, type ReactNode, type RefObject } from 'react';
import { CAMERA_MOTION, type CameraZone } from './useZoneNavigation';

type Props = {
  zone: CameraZone | null;
  phase: 'idle' | 'zooming' | 'return-setup' | 'returning';
  stageRef: RefObject<HTMLDivElement>;
  children: ReactNode;
  alt?: string;
};

// Convert percentages of the original artwork into the painted image's coordinates.
// This accounts for cover/contain crops, object-position, and the mobile toolbar crop.
export function imagePoint(image: HTMLImageElement, x: number, y: number) {
  const css = getComputedStyle(image);
  const width = image.clientWidth;
  const height = image.clientHeight;
  const naturalWidth = image.naturalWidth || 1672;
  const naturalHeight = image.naturalHeight || 941;
  let paintedWidth = width;
  let paintedHeight = height;
  if (css.objectFit === 'cover' || css.objectFit === 'contain') {
    const scale = (css.objectFit === 'cover' ? Math.max : Math.min)(width / naturalWidth, height / naturalHeight);
    paintedWidth = naturalWidth * scale;
    paintedHeight = naturalHeight * scale;
  }
  const [positionX = '50%', positionY = '50%'] = css.objectPosition.split(' ');
  const offset = (value: string, space: number) => value.endsWith('%') ? parseFloat(value) / 100 * space : parseFloat(value) || 0;
  const left = image.offsetLeft + offset(positionX, width - paintedWidth);
  const top = image.offsetTop + offset(positionY, height - paintedHeight);
  return { x: left + paintedWidth * x / 100, y: top + paintedHeight * y / 100, left, top, width: paintedWidth, height: paintedHeight };
}

export function MapCamera({ zone, phase, stageRef, children, alt }: Props) {
  const imageRef = useRef<HTMLImageElement>(null);
  const [transform, setTransform] = useState('translate(0px, 0px) scale(1)');
  const zoomed = phase === 'zooming' || phase === 'return-setup';
  const update = () => {
    const image = imageRef.current;
    const stage = stageRef.current;
    if (!image || !stage || !zone || !zoomed) {
      setTransform('translate(0px, 0px) scale(1)');
      return;
    }
    const point = imagePoint(image, zone.camera.x, zone.camera.y);
    const scale = zone.camera.zoom;
    const clamp = (value: number, min: number, max: number) => Math.max(min, Math.min(max, value));
    // Keep the artwork covering the viewport near the map's edges.
    const tx = clamp(stage.clientWidth / 2 - point.x * scale, stage.clientWidth - (point.left + point.width) * scale, -point.left * scale);
    const ty = clamp(stage.clientHeight / 2 - point.y * scale, stage.clientHeight - (point.top + point.height) * scale, -point.top * scale);
    setTransform(`translate(${tx}px, ${ty}px) scale(${scale})`);
  };
  useLayoutEffect(() => {
    update();
    const observer = new ResizeObserver(update);
    if (stageRef.current) observer.observe(stageRef.current);
    if (imageRef.current) observer.observe(imageRef.current);
    return () => observer.disconnect();
  }, [zone, zoomed]);
  const style = {
    '--camera-duration': `${CAMERA_MOTION.duration}ms`,
    '--camera-easing': CAMERA_MOTION.easing,
    transform,
  } as CSSProperties;
  return (
    <div className="home-map-stage" ref={stageRef} data-camera-phase={phase}>
      <div className={`home-map-camera ${phase === 'return-setup' ? 'camera-no-transition' : ''}`} style={style}>
        <img ref={imageRef} onLoad={update} className="home-image" src="/home-map-clean-toolbar.png" {...{ fetchpriority: 'high' }} decoding="async" alt={alt || 'Bản đồ năm điểm tham quan khu di tích Vĩ tuyến 17'} />
        <svg className="home-title-plaque" viewBox="0 0 450 98" preserveAspectRatio="none" role="img" aria-labelledby="home-title-label">
          <title id="home-title-label">Di tích quốc gia đặc biệt Vĩ tuyến 17 — Nơi khát vọng thống nhất non sông</title>
          <defs>
            <linearGradient id="home-title-gold" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0" stopColor="#fff4c9" />
              <stop offset=".48" stopColor="#f7d78a" />
              <stop offset="1" stopColor="#d6a648" />
            </linearGradient>
          </defs>
          <svg width="450" height="98" viewBox="0 128 2172 464" preserveAspectRatio="none" aria-hidden="true">
            <defs>
              <clipPath id="home-title-panel-shape">
                <path d="M0 129 H1920 L1951 131 L1981 135 L2001 140 L2027 150 L2058 170 L2087 200 L2114 250 L2126 300 L2136 350 L2145 400 L2154 450 L2163 500 L2171 550 L2172 592 H0 Z" />
              </clipPath>
            </defs>
            <image href="/home-title-panel.png" width="2172" height="724" clipPath="url(#home-title-panel-shape)" />
          </svg>
          <g fill="url(#home-title-gold)" textAnchor="middle" fontFamily="Georgia, 'Times New Roman', serif">
            <text x="272" y="19" fontSize="14" fontWeight="700" textLength="270" lengthAdjust="spacingAndGlyphs">DI TÍCH QUỐC GIA ĐẶC BIỆT</text>
            <text x="272" y="63" fontSize="46" textLength="310" lengthAdjust="spacingAndGlyphs">VĨ TUYẾN 17</text>
            <text x="257" y="89" fontSize="15" fontWeight="700" textLength="338" lengthAdjust="spacingAndGlyphs">NƠI KHÁT VỌNG THỐNG NHẤT NON SÔNG</text>
          </g>
        </svg>
        {children}
      </div>
    </div>
  );
}
