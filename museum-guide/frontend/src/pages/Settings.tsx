import { api, type Lang } from '../api/client'
import { ErrorBox, Loading } from '../components/StateViews'
import { useI18n } from '../i18n'
import { useAsync } from '../lib/useAsync'
import { useSettings } from '../lib/settings'

export default function Settings() {
  const { t, lang, setLang } = useI18n()
  const { answerLang, setAnswerLang, voiceId, setVoiceId } = useSettings()
  const h = useAsync(() => api.health(), [])
  return (
    <div className="mx-auto max-w-2xl space-y-5">
      <h1 className="text-2xl">{t('set_title')}</h1>
      <div className="card space-y-4 p-4">
        <label className="block text-sm"><span className="mb-1 block font-medium">{t('set_ui_lang')}</span>
          <select className="w-full rounded border border-rule bg-paper px-2 py-1.5" value={lang} onChange={(e) => setLang(e.target.value as Lang)}>
            <option value="vi">Tiếng Việt</option><option value="en">English</option><option value="zh">中文（简体）</option></select></label>
        <label className="block text-sm"><span className="mb-1 block font-medium">{t('set_answer_lang')}</span>
          <select className="w-full rounded border border-rule bg-paper px-2 py-1.5" value={answerLang} onChange={(e) => setAnswerLang(e.target.value as Lang | 'auto')}>
            <option value="auto">{t('set_auto')}</option><option value="vi">Tiếng Việt</option><option value="en">English</option><option value="zh">中文（简体）</option></select></label>
        <label className="block text-sm"><span className="mb-1 block font-medium">{t('set_voice')}</span>
          <input className="w-full rounded border border-rule bg-paper px-2 py-1.5 font-mono" value={voiceId} maxLength={40} pattern="[A-Za-z0-9]*" onChange={(e) => setVoiceId(e.target.value.replace(/[^A-Za-z0-9]/g, ''))} />
          <span className="text-xs text-sepia">{t('set_voice_hint')}</span></label>
      </div>
      <div className="card p-4"><h2 className="mb-2 text-lg">{t('set_health')}</h2>
        {h.loading ? <Loading /> : h.error ? <ErrorBox message={h.error} onRetry={h.reload} /> : h.data && (
          <ul className="space-y-1 text-sm"><li>{t('set_llm')}: <b>{h.data.llm.model}</b> — {h.data.llm.configured ? t('set_configured') : t('set_missing')}</li>
            <li>{t('set_tts')}: <b>{h.data.tts.model}</b> — {h.data.tts.configured ? t('set_configured') : t('set_missing')}</li>
            <li>{t('set_retrieval')}: {h.data.retrieval.backend}; {h.data.retrieval.image_retrieval}</li></ul>)}
      </div>
    </div>
  )
}
