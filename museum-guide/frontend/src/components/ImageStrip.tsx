import { useState } from 'react'
import { Link } from 'react-router-dom'
import type { ImageRef } from '../api/client'
import { useI18n } from '../i18n'
import Lightbox from './Lightbox'

export default function ImageStrip({ images }: { images: ImageRef[] }) {
  const { t, pick } = useI18n()
  const [open, setOpen] = useState<ImageRef | null>(null)
  if (!images.length) return null
  return (
    <section aria-label={t('chat_images')} className="mt-3">
      <h4 className="mb-1 text-sm font-semibold text-sepia">{t('chat_images')}</h4>
      <div className="flex flex-wrap gap-2">
        {images.map((im) => {
          const title = pick({ vi: im.title, en: im.title_en, zh: im.title_zh })
          return (
            <figure key={im.image_id} className="w-36">
              <button className="block w-full overflow-hidden rounded border border-rule" onClick={() => setOpen(im)} aria-label={`${t('gal_open')}: ${title}`}>
                <img src={im.thumb_url} alt={title} loading="lazy" className="h-24 w-full object-cover" />
              </button>
              <figcaption className="mt-1 text-xs leading-tight"><Link className="underline" to={`/gallery/${im.image_id}`}>{title}</Link></figcaption>
            </figure>
          )
        })}
      </div>
      {open && <Lightbox src={open.image_url} alt={pick({ vi: open.title, en: open.title_en, zh: open.title_zh })} caption={open.caption ?? undefined} onClose={() => setOpen(null)} />}
    </section>
  )
}
