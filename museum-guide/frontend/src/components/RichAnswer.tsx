import type { ReactNode } from 'react'
import { useI18n } from '../i18n'
import { splitCitations } from '../lib/citations'

/** Trình bày câu trả lời dài: tách đoạn (\n\n), tiêu đề "### " (ít khi dùng), **in đậm**, nhãn [S#] thành chỉ số trên dẫn tới thẻ nguồn. */
function inline(text: string, labels: Set<string>, msgId: number, key: string, citeLabel: string): ReactNode[] {
  const out: ReactNode[] = []
  splitCitations(text).forEach((p, i) => {
    if (p.type === 'cite') {
      if (labels.has(p.label)) out.push(<a key={`${key}c${i}`} href={`#src-${msgId}-${p.label}`} className="ml-0.5 align-super text-[10px] font-semibold text-flag no-underline hover:underline" aria-label={`${citeLabel} ${p.label}`}>[{p.label}]</a>)
      return
    }
    p.text.split(/(\*\*[^*]+\*\*)/g).forEach((seg, j) => {
      if (!seg) return
      if (seg.startsWith('**') && seg.endsWith('**')) out.push(<strong key={`${key}b${i}-${j}`}>{seg.slice(2, -2)}</strong>)
      else out.push(<span key={`${key}t${i}-${j}`}>{seg}</span>)
    })
  })
  return out
}

export default function RichAnswer({ text, labels, msgId }: { text: string; labels: Set<string>; msgId: number }) {
  const { t } = useI18n()
  const blocks = text.replace(/\r/g, '').split(/\n{2,}/).map((b) => b.trim()).filter(Boolean)
  return (
    <div className="prose-guide max-w-prose2 text-[17px] leading-[1.8] text-ink2" data-testid="rich-answer">
      {blocks.map((b, i) => {
        if (b.startsWith('### ')) return <h3 key={i}>{b.slice(4)}</h3>
        return <p key={i}>{inline(b.replace(/\n/g, ' '), labels, msgId, String(i), t('chat_sources'))}</p>
      })}
    </div>
  )
}
