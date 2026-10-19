import { useState } from 'react'
import { Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import Page from '../components/Page'
import { useAuth } from '../auth'
import { useT } from '../i18n'

export default function Register() {
  const { register } = useAuth()
  const { t } = useT()
  const [step, setStep] = useState(0)
  const [f, setF] = useState({ username: '', email: '', password: '', short_max_hours: 5, medium_max_hours: 15 })
  const [err, setErr] = useState('')
  const [busy, setBusy] = useState(false)
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value })

  const next = (e) => {
    e.preventDefault()
    if (f.password.length < 8) return setErr(t('pw_min'))
    setErr(''); setStep(1)
  }

  const submit = async (e) => {
    e.preventDefault()
    setBusy(true); setErr('')
    try {
      await register({ ...f, short_max_hours: +f.short_max_hours, medium_max_hours: +f.medium_max_hours })
    } catch (ex) { setErr(ex.message || t('register_fail')); setStep(0) }
    finally { setBusy(false) }
  }

  return (
    <Page className="auth">
      <motion.div className="auth__card glass" layoutId="authcard">
        <div className="auth__steps"><span className={step === 0 ? 'on' : 'done'} /><span className={step === 1 ? 'on' : ''} /></div>
        <AnimatePresence mode="wait">
          {step === 0 ? (
            <motion.form key="s0" onSubmit={next} initial={{ opacity: 0, x: 30 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -30 }} transition={{ duration: 0.25 }}>
              <h1>{t('register_title')}</h1>
              <p className="muted">{t('register_sub')}</p>
              <label>{t('username')}<input value={f.username} onChange={set('username')} minLength={3} required autoFocus /></label>
              <label>{t('email')}<input type="email" value={f.email} onChange={set('email')} required /></label>
              <label>{t('password')}<input type="password" value={f.password} onChange={set('password')} minLength={8} required /></label>
              {err && <p className="err">{err}</p>}
              <button className="btn btn--block">{t('continue')}</button>
              <p className="auth__alt">{t('have_account')} <Link to="/login">{t('nav_login')}</Link></p>
            </motion.form>
          ) : (
            <motion.form key="s1" onSubmit={submit} initial={{ opacity: 0, x: 30 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -30 }} transition={{ duration: 0.25 }}>
              <h1>{t('register_step2_title')}</h1>
              <p className="muted">{t('register_step2_sub')}</p>
              <label>{t('short_max')}<input type="number" step="0.5" min="0.5" value={f.short_max_hours} onChange={set('short_max_hours')} required /></label>
              <label>{t('medium_max')}<input type="number" step="0.5" min="1" value={f.medium_max_hours} onChange={set('medium_max_hours')} required /></label>
              {err && <p className="err">{err}</p>}
              <div className="row">
                <button type="button" className="btn btn--ghost" onClick={() => setStep(0)}>{t('back')}</button>
                <button className="btn" disabled={busy}>{busy ? t('creating') : t('create_account')}</button>
              </div>
            </motion.form>
          )}
        </AnimatePresence>
      </motion.div>
    </Page>
  )
}
