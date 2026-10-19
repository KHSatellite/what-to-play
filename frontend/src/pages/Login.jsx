import { useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import Page from '../components/Page'
import { useAuth } from '../auth'
import { useT } from '../i18n'

export default function Login() {
  const { login } = useAuth()
  const { t } = useT()
  const [sp] = useSearchParams()
  const [f, setF] = useState({ username: '', password: '' })
  const [err, setErr] = useState(sp.get('expired') ? t('expired') : '')
  const [busy, setBusy] = useState(false)

  const submit = async (e) => {
    e.preventDefault()
    setBusy(true); setErr('')
    try { await login(f.username, f.password) }
    catch (ex) { setErr(ex.message || t('login_fail')) }
    finally { setBusy(false) }
  }

  return (
    <Page className="auth">
      <motion.form className="auth__card glass" onSubmit={submit} layoutId="authcard">
        <h1>{t('login_title')}</h1>
        <p className="muted">{t('login_sub')}</p>
        <label>{t('username')}<input value={f.username} onChange={e => setF({ ...f, username: e.target.value })} autoFocus required /></label>
        <label>{t('password')}<input type="password" value={f.password} onChange={e => setF({ ...f, password: e.target.value })} required /></label>
        {err && <motion.p className="err" initial={{ opacity: 0, x: -6 }} animate={{ opacity: 1, x: 0 }}>{err}</motion.p>}
        <button className="btn btn--block" disabled={busy}>{busy ? t('login_busy') : t('login_btn')}</button>
        <p className="auth__alt">{t('no_account')} <Link to="/register">{t('nav_register')}</Link></p>
      </motion.form>
    </Page>
  )
}
