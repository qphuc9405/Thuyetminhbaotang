// Tách chuỗi trả lời thành các đoạn text và nhãn trích dẫn [S1], [I2]...
export type Part = { type: 'text'; text: string } | { type: 'cite'; label: string }
export function splitCitations(text: string): Part[] {
  const out: Part[] = []
  const re = /\[(S\d+|I\d+)\]/g
  let last = 0, m: RegExpExecArray | null
  while ((m = re.exec(text))) {
    if (m.index > last) out.push({ type: 'text', text: text.slice(last, m.index) })
    out.push({ type: 'cite', label: m[1] })
    last = m.index + m[0].length
  }
  if (last < text.length) out.push({ type: 'text', text: text.slice(last) })
  return out
}
export function pageLabel(s: { printed_page: number | null; printed_page_end: number | null; provision: string | null }, prefix: string): string {
  if (s.printed_page == null) return s.provision ?? '—'
  return s.printed_page_end && s.printed_page_end !== s.printed_page ? `${prefix}${s.printed_page}–${s.printed_page_end}` : `${prefix}${s.printed_page}`
}
