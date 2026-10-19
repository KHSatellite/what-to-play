import { useEffect, useRef, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { AnimatePresence, motion } from 'framer-motion'
import Page, { fadeUp, stagger } from '../components/Page'
import { api } from '../api'
import { useAuth } from '../auth'
import { useTheme, THEMES } from '../theme'
import { useT, LANGS } from '../i18n'

function PlatformCard({ c, progress, onConnectCode, onImport, onRemove, busy }) {
  const { t, lang } = useT()
  const [code, setCode] = useState('')
  const [open, setOpen] = useState(false)
  const acc = c.account
  const p = progress?.[acc?.id]
  const pct = p && p.total ? Math.round(p.done / p.total * 100) : 0
  const running = p && !p.finished

  const startCode = () => { window.open(c.login_url, '_blank', 'noopener'); setOpen(true) }
  const submitCode = async (e) => { e.preventDefault(); if (!code.trim()) return; await onConnectCode(c.name, code); setCode(''); setOpen(false) }
  const instructions = c.instructions?.[lang] || c.instructions?.tr || c.instructions

  return (
    <div className={`platform-card glass platform-card--${c.name}`}>
      <div className="platform-card__head">
        <div>
          <h3>{c.label}</h3>
          {acc ? (
            <p className="muted">{t('connected')}{acc.last_synced_at ? ` · ${t('last_sync', { d: new Date(acc.last_synced_at).toLocaleString(lang === 'tr' ? 'tr-TR' : 'en-GB') })}` : ` · ${t('not_imported')}`}</p>
          ) : (
            <p className="muted">{instructions}</p>
          )}
        </div>
        <span className={`dot ${acc ? 'dot--on' : ''}`} />
      </div>

      {p && !p.idle && (
        <div className="progress">
          <div className="progress__bar"><motion.div className="progress__fill" animate={{ width: `${pct}%` }} /></div>
          <small>{p.error ? p.error : p.finished
            ? t('imp_done', { t: p.platform_total ?? p.total, i: p.imported, a: p.already ?? 0, s: p.skipped }) + (p.duplicates ? t('imp_dups', { d: p.duplicates }) : '')
            : t('imp_running', { d: p.done, t: p.total })}</small>
          {p.finished && p.skipped_titles?.length > 0 && (
            <details className="skipped">
              <summary>{t('imp_skipped', { n: p.skipped_titles.length })}</summary>
              <ul>{p.skipped_titles.map(x => <li key={x}>{x}</li>)}</ul>
              <small className="muted">{t('imp_skipped_hint')}</small>
            </details>
          )}
        </div>
      )}

      <div className="row platform-card__actions">
        {c.mode === 'redirect' ? (
          <a className="btn btn--sm" href={`/platform-accounts/steam/login?user_id=${c.userId}`}>{acc ? t('reconnect') : t('connect_with', { p: c.label })}</a>
        ) : (
          <button className="btn btn--sm" onClick={startCode} disabled={busy}>{acc ? t('reconnect') : t('connect_with', { p: c.label })}</button>
        )}
        {acc && <button className="btn btn--ghost btn--sm" onClick={() => onImport(acc.id)} disabled={busy || running}>{t('reimport')}</button>}
        {acc && <button className="btn btn--ghost btn--sm danger" onClick={() => onRemove(acc.id, c.label)} disabled={busy || running}>{t('remove')}</button>}
      </div>

      <AnimatePresence>
        {open && c.mode === 'code' && (
          <motion.form className="code-box" onSubmit={submitCode} initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }}>
            <p className="muted small">{instructions} {t('code_hint_link')} <a href={c.login_url} target="_blank" rel="noreferrer">{t('login_page')}</a></p>
            <textarea rows={3} value={code} onChange={e => setCode(e.target.value)} placeholder={t('code_placeholder')} />
            <div className="row">
              <button className="btn btn--sm" disabled={busy || !code.trim()}>{busy ? t('verifying') : t('connect_import')}</button>
              <button type="button" className="btn btn--ghost btn--sm" onClick={() => setOpen(false)}>{t('cancel')}</button>
            </div>
          </motion.form>
        )}
      </AnimatePresence>
    </div>
  )
}

export default function Settings() {
  const { user } = useAuth()
  const { theme, setTheme } = useTheme()
  const { t, lang, setLang } = useT()
  const [sp, setSp] = useSearchParams()
  const [s, setS] = useState({ short_max_hours: 5, medium_max_hours: 15 })
  const [msg, setMsg] = useState('')
  const [conn, setConn] = useState(null)
  const [progress, setProgress] = useState({})
  const [note, setNote] = useState('')
  const [busy, setBusy] = useState(false)
  const timers = useRef({})

  const loadConnectors = () => api('/platform-accounts/connectors').then(setConn).catch(() => {})

  useEffect(() => {
    api(`/users/${user.id}/settings`).then(setS).catch(() => {})
    loadConnectors()
    if (sp.get('steam_error')) setNote(t('steam_err'))
    if (sp.get('steam_connected')) setNote(t('steam_ok'))
    const accId = sp.get('account_id')
    if (accId) poll(accId)
    return () => Object.values(timers.current).forEach(clearTimeout)
  }, [])  // eslint-disable-line

  const poll = async (accId) => {
    try {
      const p = await api(`/platform-accounts/${accId}/import-status`)
      setProgress(prev => ({ ...prev, [accId]: p }))
      if (!p.finished) timers.current[accId] = setTimeout(() => poll(accId), 1500)
      else { loadConnectors(); if (sp.get('account_id')) setSp({}, { replace: true }) }
    } catch { timers.current[accId] = setTimeout(() => poll(accId), 3000) }
  }

  const startImport = (accId) => {
    setProgress(prev => ({ ...prev, [accId]: { total: 0, done: 0, finished: false } }))
    api(`/platform-accounts/${accId}/import`, { method: 'POST' }).catch(e => setProgress(prev => ({ ...prev, [accId]: { ...prev[accId], finished: true, error: e.message } })))
    timers.current[accId] = setTimeout(() => poll(accId), 800)
  }

  const connectCode = async (platform, code) => {
    setBusy(true); setNote('')
    try {
      const acc = await api('/platform-accounts/connect-code', { method: 'POST', body: { platform, code } })
      await loadConnectors()
      setNote(t('connected_importing', { p: platform.toUpperCase() }))
      startImport(acc.id)
    } catch (e) { setNote(e.message) }
    finally { setBusy(false) }
  }

  const remove = async (accId, label) => {
    if (!window.confirm(t('remove_platform_confirm', { p: label }))) return
    setBusy(true)
    try { await api(`/platform-accounts/${accId}`, { method: 'DELETE' }); await loadConnectors() }
    catch (e) { setNote(e.message) }
    finally { setBusy(false) }
  }

  const save = async (e) => {
    e.preventDefault()
    try {
      await api(`/users/${user.id}/settings`, { method: 'PUT', body: { short_max_hours: +s.short_max_hours, medium_max_hours: +s.medium_max_hours } })
      setMsg(t('saved'))
    } catch (ex) { setMsg(ex.message) }
    setTimeout(() => setMsg(''), 2500)
  }

  const manualConnected = (conn?.manual || []).filter(m => m.account)

  return (
    <Page className="settings">
      <motion.div variants={stagger} initial="initial" animate="animate">
        <motion.h1 variants={fadeUp}>{t('settings_title')}</motion.h1>

        <motion.section variants={fadeUp} className="card glass">
          <h2>{t('plat_title')}</h2>
          <p className="muted">{t('plat_sub')}</p>
          {note && <p className="note">{note}</p>}
          {conn === null ? <div className="spinner" /> : (
            <div className="platforms">
              {conn.connectors.map(c => (
                <PlatformCard key={c.name} c={{ ...c, userId: user.id }} progress={progress} busy={busy} onConnectCode={connectCode} onImport={startImport} onRemove={remove} />
              ))}
            </div>
          )}
          <div className="manual-note">
            <h3>{t('manual_title')}</h3>
            <p className="muted">{t('manual_d1')} <Link to="/kutuphane?add=1">{t('manual_link')}</Link> {t('manual_d2')}</p>
            {manualConnected.length > 0 && (
              <div className="row">
                {manualConnected.map(m => <span key={m.name} className="chip chip--on">{m.label}</span>)}
              </div>
            )}
          </div>
        </motion.section>

        <motion.form variants={fadeUp} className="card glass" onSubmit={save}>
          <h2>{t('dur_title')}</h2>
          <p className="muted">{t('dur_sub')}</p>
          <div className="row">
            <label>{t('short_limit')}<input type="number" step="0.5" min="0.5" value={s.short_max_hours} onChange={e => setS({ ...s, short_max_hours: e.target.value })} /></label>
            <label>{t('medium_limit')}<input type="number" step="0.5" min="1" value={s.medium_max_hours} onChange={e => setS({ ...s, medium_max_hours: e.target.value })} /></label>
          </div>
          <div className="row"><button className="btn">{t('save')}</button>{msg && <span className="muted">{msg}</span>}</div>
        </motion.form>

        <motion.section variants={fadeUp} className="card glass">
          <h2>{t('lang_title')}</h2>
          <div className="lang-cards">
            {LANGS.map(l => (
              <button key={l.id} className={`theme-card ${lang === l.id ? 'on' : ''}`} onClick={() => setLang(l.id)}>
                <strong>{l.flag} {l.name}</strong>
              </button>
            ))}
          </div>
        </motion.section>

        <motion.section variants={fadeUp} className="card glass">
          <h2>{t('theme_title')}</h2>
          <div className="themes">
            {THEMES.map(th => (
              <button key={th.id} className={`theme-card theme-card--${th.id} ${theme === th.id ? 'on' : ''}`} onClick={() => setTheme(th.id)}>
                <div className="theme-card__preview"><span /><span /><span /></div>
                <strong>{t(th.name)}</strong><small>{t(th.desc)}</small>
              </button>
            ))}
          </div>
        </motion.section>

        <motion.section variants={fadeUp} className="card glass">
          <h2>{t('account_title')}</h2>
          <p className="muted">{user.username} · {user.email}</p>
        </motion.section>
      </motion.div>
    </Page>
  )
}
