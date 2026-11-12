import { Link } from 'react-router-dom'
import { api } from '../api/client'
import { ErrorBox, Loading } from '../components/StateViews'
import { useI18n } from '../i18n'
import { useAsync } from '../lib/useAsync'

export default function Topics() {
  const { t, pick } = useI18n()
  const { data, error, loading, reload } = useAsync(() => api.topics(), [])
  if (loading) return <Loading />
  if (error || !data) return <ErrorBox message={error ?? ''} onRetry={reload} />
  return (
    <div>
      <h1 className="mb-3 text-2xl">{t('tp_title')}</h1>
      <ul className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {data.items.map((x) => (
          <li key={x.topic_id}><Link to={`/topics/${x.topic_id}`} className="card block h-full p-4 hover:bg-paper">
            <h2 className="text-lg text-oxblood">{pick({ vi: x.title_vi, en: x.title_en, zh: x.title_zh })}</h2>
            <p className="mt-1 text-sm">{x.description_vi}</p>
            <p className="mt-2 text-xs text-sepia">{x.printed_start}–{x.printed_end} · {x.n_events ?? 0} {t('tp_events')} · {x.n_images ?? 0} {t('tp_images')}</p></Link></li>
        ))}
      </ul>
    </div>
  )
}
