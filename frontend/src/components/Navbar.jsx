import { useEffect, useRef, useState } from 'react'
import { Link, NavLink, useNavigate } from 'react-router-dom'
import { AnimatePresence, motion } from 'framer-motion'
import { useAuth } from '../auth'
import { useTheme, THEMES } from '../theme'
import { useT, LANGS } from '../i18n'

export default function Navbar() {
  const { user, logout } = useAuth()
  const { theme, setTheme } = useTheme()
  const { t, lang, setLang } = useT()
  const [open, setOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)
  const ref = useRef(null)
  const nav = useNavigate()

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 12)
    onScroll()
    window.addEventListener('scroll', onScroll)
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  useEffect(() => {
    const onDoc = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false) }
    document.addEventListener('mousedown', onDoc)
    return () => document.removeEventListener('mousedown', onDoc)
  }, [])

  const doLogout = () => { setOpen(false); nav('/'); logout() }

  return (
    <header className={`nav ${scrolled ? 'nav--scrolled' : ''}`}>
      <Link to="/" className="brand">NE<span>OYNASAM</span></Link>
      <nav className="nav-links">
        {user ? (
          <>
            <NavLink to="/panel">{t('nav_panel')}</NavLink>
            <NavLink to="/oyun-oner">{t('nav_recommend')}</NavLink>
            <NavLink to="/kutuphane">{t('nav_library')}</NavLink>
            <NavLink to="/sonra-oyna">{t('nav_later')}</NavLink>
          </>
        ) : (
          <>
            <button className="lang-btn" onClick={() => setLang(lang === 'tr' ? 'en' : 'tr')} title={t('language')}>{lang === 'tr' ? '🇬🇧 EN' : '🇹🇷 TR'}</button>
            <NavLink to="/login">{t('nav_login')}</NavLink>
            <Link to="/register" className="btn btn--sm">{t('nav_register')}</Link>
          </>
        )}
      </nav>
      {user && (
        <div className="avatar-wrap" ref={ref}>
          <button className="avatar" onClick={() => setOpen(o => !o)} aria-label="Menu">
            {user.username.slice(0, 1).toUpperCase()}
          </button>
          <AnimatePresence>
            {open && (
              <motion.div className="dropdown" initial={{ opacity: 0, y: -8, scale: 0.96 }} animate={{ opacity: 1, y: 0, scale: 1 }} exit={{ opacity: 0, y: -8, scale: 0.96 }} transition={{ duration: 0.18 }}>
                <div className="dropdown__head">
                  <strong>{user.username}</strong>
                  <small>{user.email}</small>
                </div>
                <Link to="/panel" onClick={() => setOpen(false)}>{t('nav_panel')}</Link>
                <Link to="/kutuphane" onClick={() => setOpen(false)}>{t('nav_library')}</Link>
                <Link to="/sonra-oyna" onClick={() => setOpen(false)}>{t('nav_later')}</Link>
                <Link to="/settings" onClick={() => setOpen(false)}>{t('nav_settings')}</Link>
                <div className="dropdown__themes">
                  <small>{t('theme')}</small>
                  <div>
                    {THEMES.map(th => (
                      <button key={th.id} className={`theme-dot theme-dot--${th.id} ${theme === th.id ? 'active' : ''}`} title={t(th.name)} onClick={() => setTheme(th.id)} />
                    ))}
                  </div>
                </div>
                <div className="dropdown__themes">
                  <small>{t('language')}</small>
                  <div>
                    {LANGS.map(l => <button key={l.id} className={`lang-btn ${lang === l.id ? 'on' : ''}`} onClick={() => setLang(l.id)}>{l.flag} {l.id.toUpperCase()}</button>)}
                  </div>
                </div>
                <button className="dropdown__logout" onClick={doLogout}>{t('nav_logout')}</button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      )}
    </header>
  )
}
