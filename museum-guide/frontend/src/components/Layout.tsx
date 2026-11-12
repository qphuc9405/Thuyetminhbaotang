import { useState } from 'react'
import { NavLink, Outlet, useLocation } from 'react-router-dom'
import { useI18n } from '../i18n'
import type { Lang } from '../api/client'

const LANGS: { code: Lang; label: string }[] = [{ code: 'vi', label: 'VI' }, { code: 'en', label: 'EN' }, { code: 'zh', label: '中文' }]

export default function Layout() {
  const { t, lang, setLang } = useI18n()
  const [open, setOpen] = useState(false)
  const { pathname } = useLocation()
  const onHome = pathname === '/'
  const link = ({ isActive }: { isActive: boolean }) => `block px-2 py-1 text-[13px] tracking-wide transition-colors ${isActive ? 'text-white underline decoration-flag decoration-2 underline-offset-[6px]' : 'text-white/75 hover:text-white'}`
  const nav = (
    <>
      <NavLink to="/" end className={link} onClick={() => setOpen(false)}>{t('nav_home')}</NavLink>
      <NavLink to="/timeline" className={link} onClick={() => setOpen(false)}>{t('nav_timeline')}</NavLink>
      <NavLink to="/stories" className={link} onClick={() => setOpen(false)}>{t('nav_stories')}</NavLink>
      <NavLink to="/gallery" className={link} onClick={() => setOpen(false)}>{t('nav_gallery')}</NavLink>
      <NavLink to="/topics" className={link} onClick={() => setOpen(false)}>{t('nav_topics')}</NavLink>
      <NavLink to="/chat" className={link} onClick={() => setOpen(false)}>{t('nav_chat')}</NavLink>
      <NavLink to="/settings" className={link} onClick={() => setOpen(false)}>{t('nav_settings')}</NavLink>
    </>
  )
  return (
    <div className="min-h-screen">
      <header className={`${onHome ? 'absolute' : 'sticky'} inset-x-0 top-0 z-40 ${onHome ? 'bg-gradient-to-b from-ink/80 to-transparent' : 'bg-ink'}`}>
        <div className="mx-auto flex max-w-7xl items-center gap-6 px-5 py-3">
          <NavLink to="/" className="font-serif text-lg leading-tight text-white">{t('hero_title')}<span className="block text-[10px] font-sans uppercase tracking-[0.25em] text-white/60">1954 – 1967</span></NavLink>
          <nav aria-label="Main" className="hidden flex-1 items-center gap-2 md:flex">{nav}</nav>
          <div className="ml-auto flex gap-1" role="group" aria-label="Language">
            {LANGS.map((l) => (
              <button key={l.code} aria-pressed={lang === l.code} onClick={() => setLang(l.code)}
                className={`px-2 py-1 text-xs font-semibold ${lang === l.code ? 'bg-flag text-white' : 'text-white/70 hover:text-white'}`}>{l.label}</button>
            ))}
          </div>
          <button className="text-white md:hidden" aria-expanded={open} aria-label={t('menu')} onClick={() => setOpen((x) => !x)}>☰</button>
        </div>
        {open && <nav aria-label="Mobile" className="space-y-1 bg-ink px-5 pb-4 md:hidden">{nav}</nav>}
      </header>
      <main className={onHome ? '' : 'mx-auto max-w-7xl px-5 py-8'}><Outlet /></main>
      <footer className="mt-16 bg-ink px-5 py-10 text-sm text-white/60">
        <div className="mx-auto max-w-7xl">
          <p className="font-serif text-white">{t('hero_title')} · {t('hero_tagline')}</p>
          <p className="mt-2 max-w-3xl text-xs">{t('home_scope_1')} {t('home_scope_4')}</p>
        </div>
      </footer>
    </div>
  )
}
