import { createContext, useContext, useMemo, useState, type ReactNode } from 'react'
import type { Lang } from '../api/client'
import { readLS, writeLS } from '../i18n'

export interface AppSettings { answerLang: Lang | 'auto'; voiceId: string }
interface Ctx extends AppSettings { setAnswerLang: (l: Lang | 'auto') => void; setVoiceId: (v: string) => void }
const C = createContext<Ctx | null>(null)

export function SettingsProvider({ children }: { children: ReactNode }) {
  const [answerLang, setA] = useState<Lang | 'auto'>(() => { const v = readLS('answer_lang'); return v === 'vi' || v === 'en' || v === 'zh' ? v : 'auto' })
  const [voiceId, setV] = useState<string>(() => readLS('voice_id') ?? '')
  const value = useMemo<Ctx>(() => ({ answerLang, voiceId, setAnswerLang: (l) => { setA(l); writeLS('answer_lang', l) }, setVoiceId: (v) => { setV(v); writeLS('voice_id', v) } }), [answerLang, voiceId])
  return <C.Provider value={value}>{children}</C.Provider>
}
export function useSettings(): Ctx {
  const c = useContext(C)
  if (!c) throw new Error('SettingsProvider missing')
  return c
}
