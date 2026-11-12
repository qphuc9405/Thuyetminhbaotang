import type { ReactNode } from 'react'
import { useI18n } from '../i18n'

export function Loading({ label }: { label?: string }) {
  const { t } = useI18n()
  return <div role="status" aria-live="polite" className="flex items-center gap-2 p-6 text-sepia"><span className="h-4 w-4 animate-spin rounded-full border-2 border-rule border-t-oxblood" />{label ?? t('loading')}</div>
}
export function EmptyState({ children }: { children: ReactNode }) {
  return <div className="card p-8 text-center text-sepia">{children}</div>
}
export function ErrorBox({ message, onRetry }: { message: string; onRetry?: () => void }) {
  const { t } = useI18n()
  return (
    <div role="alert" className="card border-oxblood/40 bg-[#fbeeea] p-4 text-oxblood">
      <p className="font-medium">{t('error_generic')}</p>
      <p className="text-sm">{message}</p>
      {onRetry && <button className="btn mt-2" onClick={onRetry}>{t('retry')}</button>}
    </div>
  )
}
