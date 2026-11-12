import { useEffect } from 'react'
import { useI18n } from '../i18n'

export default function Lightbox({ src, alt, caption, onClose }: { src: string; alt: string; caption?: string; onClose: () => void }) {
  const { t } = useI18n()
  useEffect(() => {
    const h = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', h); return () => window.removeEventListener('keydown', h)
  }, [onClose])
  return (
    <div role="dialog" aria-modal="true" aria-label={alt} className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-black/80 p-4" onClick={onClose}>
      <img src={src} alt={alt} className="max-h-[80vh] max-w-full rounded object-contain" onClick={(e) => e.stopPropagation()} />
      {caption && <p className="mt-2 max-w-3xl text-center text-sm text-white">{caption}</p>}
      <button className="btn mt-3" onClick={onClose}>{t('gal_close')}</button>
    </div>
  )
}
