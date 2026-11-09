import { useEffect, useRef, useState } from 'react';

export const CAMERA_MOTION = {
  duration: 900,
  easing: 'cubic-bezier(.65, 0, .35, 1)',
  fadeDuration: 220,
} as const;

export type CameraZone = {
  id: string;
  title: string;
  href: string;
  camera: { x: number; y: number; zoom: number };
};
type Phase = 'idle' | 'zooming' | 'return-setup' | 'returning';
type Navigation<Z> = { phase: Phase; zone: Z | null };

export function useZoneNavigation<Z extends CameraZone>(zones: Z[], callbacks: {
  onStart: () => void;
  onNavigate: (zone: Z | null, tab: 'story' | 'photos') => void;
}) {
  const fromLocation = () => zones.find(zone => zone.href === window.location.hash.split('/')[0]) || null;
  const [active, setActive] = useState<Z | null>(fromLocation);
  const [navigation, setNavigation] = useState<Navigation<Z>>({ phase: 'idle', zone: null });
  const activeRef = useRef(active);
  const callbacksRef = useRef(callbacks);
  callbacksRef.current = callbacks;
  const zonesRef = useRef(zones);
  zonesRef.current = zones;
  const locked = useRef(false);
  const lastZone = useRef(active);
  const lastHash = useRef(window.location.hash);
  const timer = useRef<ReturnType<typeof setTimeout>>();
  const frames = useRef<number[]>([]);
  const targetTab = useRef<'story' | 'photos'>('story');
  const focusOnMap = useRef<string | null>(null);
  const mapRef = useRef<HTMLDivElement>(null);

  const cancel = () => {
    clearTimeout(timer.current);
    frames.current.forEach(cancelAnimationFrame);
    frames.current = [];
    locked.current = false;
  };
  const reducedMotion = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const commit = (zone: Z | null, tab: 'story' | 'photos' = 'story') => {
    activeRef.current = zone;
    setActive(zone);
    callbacksRef.current.onNavigate(zone, tab);
  };
  const finishEntry = (zone: Z) => {
    cancel();
    window.history.pushState({ zone: zone.id }, '', zone.href);
    lastHash.current = window.location.hash;
    lastZone.current = zone;
    setNavigation({ phase: 'idle', zone: null });
    commit(zone, targetTab.current);
    window.scrollTo({ top: 0, behavior: 'instant' });
  };
  const revealHome = (zone: Z | null) => {
    focusOnMap.current = zone?.id || null;
    commit(null);
    if (zone && !reducedMotion()) {
      locked.current = true;
      setNavigation({ phase: 'return-setup', zone });
    } else {
      setNavigation({ phase: 'idle', zone: null });
    }
  };
  const openZone = (zone: Z, tab: 'story' | 'photos' = 'story') => {
    if (locked.current || activeRef.current?.id === zone.id) return;
    cancel();
    targetTab.current = tab;
    if (activeRef.current || reducedMotion()) {
      callbacksRef.current.onStart();
      finishEntry(zone);
      return;
    }
    locked.current = true;
    callbacksRef.current.onStart();
    // Cards on a small screen can be below the map; show the camera before zooming.
    mapRef.current?.scrollIntoView({ block: 'center', behavior: 'instant' });
    setNavigation({ phase: 'zooming', zone });
  };
  const backHome = () => {
    if (locked.current) return;
    const previous = activeRef.current;
    cancel();
    callbacksRef.current.onStart();
    window.history.pushState({}, '', window.location.pathname + window.location.search);
    lastHash.current = window.location.hash;
    revealHome(previous || lastZone.current);
  };

  useEffect(() => {
    if (navigation.phase === 'zooming' && navigation.zone) {
      timer.current = setTimeout(() => finishEntry(navigation.zone!), CAMERA_MOTION.duration);
    } else if (navigation.phase === 'return-setup') {
      // Two paints make the remounted map's initial zoom visible before zooming out.
      mapRef.current?.scrollIntoView({ block: 'center', behavior: 'instant' });
      frames.current.push(requestAnimationFrame(() => {
        frames.current.push(requestAnimationFrame(() => {
          setNavigation(current => ({ ...current, phase: 'returning' }));
        }));
      }));
    } else if (navigation.phase === 'returning') {
      timer.current = setTimeout(() => {
        cancel();
        setNavigation({ phase: 'idle', zone: null });
      }, CAMERA_MOTION.duration);
    } else if (navigation.phase === 'idle' && !activeRef.current && focusOnMap.current) {
      const buttons = mapRef.current?.closest('main')?.querySelectorAll<HTMLButtonElement>(
        `[data-zone="${focusOnMap.current}"]`,
      );
      Array.from(buttons || []).find(button => button.getClientRects().length > 0)?.focus({ preventScroll: true });
      focusOnMap.current = null;
    }
    return () => {
      clearTimeout(timer.current);
      frames.current.forEach(cancelAnimationFrame);
      frames.current = [];
    };
  }, [navigation.phase, navigation.zone, active]);

  useEffect(() => {
    const syncLocation = () => {
      if (lastHash.current === window.location.hash) return;
      lastHash.current = window.location.hash;
      const previous = activeRef.current;
      const zone = zonesRef.current.find(item => item.href === window.location.hash.split('/')[0]) || null;
      if (zone && previous?.id === zone.id) return;
      cancel();
      callbacksRef.current.onStart();
      if (zone) {
        lastZone.current = zone;
        setNavigation({ phase: 'idle', zone: null });
        commit(zone);
        window.scrollTo({ top: 0, behavior: 'instant' });
      } else revealHome(previous || lastZone.current);
    };
    const preference = window.matchMedia('(prefers-reduced-motion: reduce)');
    const onPreference = () => {
      if (!preference.matches) return;
      if (navigation.phase === 'zooming' && navigation.zone) finishEntry(navigation.zone);
      else if (locked.current) {
        cancel();
        setNavigation({ phase: 'idle', zone: null });
      }
    };
    window.addEventListener('popstate', syncLocation);
    window.addEventListener('hashchange', syncLocation);
    preference.addEventListener('change', onPreference);
    return () => {
      window.removeEventListener('popstate', syncLocation);
      window.removeEventListener('hashchange', syncLocation);
      preference.removeEventListener('change', onPreference);
    };
  }, [navigation]);

  useEffect(() => () => cancel(), []);
  return { active, openZone, backHome, mapRef, navigation, busy: navigation.phase !== 'idle' };
}
