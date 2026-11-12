import type { SourceRef } from '../api/client'
import { useI18n } from '../i18n'
import { pageLabel } from '../lib/citations'

export default function Sources({ sources, idPrefix }: { sources: SourceRef[]; idPrefix: string }) {
  const { t } = useI18n()
  if (!sources.length) return null
  return (
    <section aria-label={t('chat_sources')} className="mt-3">
      <h4 className="mb-1 text-sm font-semibold text-sepia">{t('chat_sources')}</h4>
      <ol className="space-y-2">
        {sources.map((s) => (
          <li key={s.chunk_id} id={`${idPrefix}-${s.label}`} className="rounded border border-rule bg-paper p-2 text-sm">
            <div className="flex flex-wrap items-center gap-2">
              <span className="font-mono text-xs font-bold text-oxblood">[{s.label}]</span>
              <span className="font-medium">{s.source_title}</span>
              <span className="tag">{s.source_type === 'BOOK' ? t('chat_book') : s.source_type === 'SECONDARY_ARTICLE' ? t('chat_article') : s.source_type === 'WEB_ARTICLE' ? t('chat_web') : s.source_type === 'CURATOR_NOTE' ? t('chat_note') : t('chat_external')}</span>
              <span className="tag" data-testid="page-tag">{s.printed_page != null ? `${t('chat_page')}${pageLabel(s, '').trim()}` : pageLabel(s, '')}</span>
              {s.pdf_page != null && <span className="tag">{t('chat_pdf')} {s.pdf_page}{s.pdf_page_end && s.pdf_page_end !== s.pdf_page ? `–${s.pdf_page_end}` : ''}</span>}
              {!s.cited && <span className="tag">—</span>}
            </div>
            {s.chapter && <p className="text-xs text-sepia">{s.chapter}</p>}
            <p className="mt-1 whitespace-pre-wrap text-xs text-ink/80">{s.content.length > 380 ? s.content.slice(0, 380) + '…' : s.content}</p>
            {s.verification_status?.includes('ocr') && <p className="mt-1 text-[11px] italic text-sepia">{t('chat_unverified')}</p>}
          </li>
        ))}
      </ol>
    </section>
  )
}
