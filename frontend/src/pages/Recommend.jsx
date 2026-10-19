import { useEffect, useRef, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { AnimatePresence, motion } from 'framer-motion'
import Page, { fadeUp, stagger } from '../components/Page'
import GameCard, { PLATFORM_LABELS, PlayLaterButton } from '../components/GameCard'
import Modal from '../components/Modal'
import { api } from '../api'
import { useAuth } from '../auth'
import { useT } from '../i18n'

export default function Recommend() {
  const { user } = useAuth()
  const { t } = useT()
  const [sp] = useSearchParams()
  const [cats, setCats] = useState([])
  const [duration, setDuration] = useState('')
  const [cat, setCat] = useState('')
  const [results, setResults] = useState(null)
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState('')
  const [spin, setSpin] = useState(-1)
  const [picked, setPicked] = useState(null)
  const spinning = useRef(false)
  const DURATIONS = [['', 'dur_any'], ['short', 'dur_short'], ['medium', 'dur_medium'], ['long', 'dur_long']]

  useEffect(() => { api('/categories/').then(setCats).catch(() => setErr(t('cats_fail'))) }, [])  // eslint-disable-line
  useEffect(() => { if (sp.get('random')) fullyRandom() }, [])  // eslint-disable-line

  const fetchSuggestions = async () => {
    setBusy(true); setErr(''); setResults(null); setSpin(-1)
    const q = new URLSearchParams()
    if (cat) q.set('category_id', cat)
    if (duration) q.set('duration', duration)
    try { setResults(await api(`/users/${user.id}/suggestions/combined?${q}`)) }
    catch (e) { setErr(e.message) }
    finally { setBusy(false) }
  }

  const fullyRandom = async () => {
    setErr('')
    try {
      const g = await api(`/users/${user.id}/suggestions/random`)
      setPicked({ ...g, mode: 'random' })
    } catch (e) { setErr(e.status === 404 ? t('rec_no_library') : e.message) }
  }

  const pickFromResults = () => {
    if (!results?.length || spinning.current) return
    spinning.current = true
    const target = Math.floor(Math.random() * results.length)
    const rounds = results.length * 2 + target
    let i = 0
    const tick = () => {
      setSpin(i % results.length)
      const progress = i / rounds
      const delay = 40 + progress * progress * 260
      i++
      if (i <= rounds) setTimeout(tick, delay)
      else {
        spinning.current = false
        setTimeout(() => setPicked({ ...results[target], mode: 'results' }), 350)
      }
    }
    tick()
  }

  const modeLabel = (m) => m === 'random' ? t('mode_random') : m === 'results' ? t('mode_from_results') : t('pick')
  const platformsOf = (g) => (g.platforms?.length ? g.platforms : [g.platform]).filter(Boolean).map(p => PLATFORM_LABELS[p] || p).join(', ')

  return (
    <Page className="rec">
      <motion.div variants={stagger} initial="initial" animate="animate">
        <motion.h1 variants={fadeUp}>{t('rec_title_1')} <span className="grad">{t('rec_title_2')}</span></motion.h1>
        <motion.div variants={fadeUp} className="filters glass">
          <div className="filters__group">
            <label>{t('rec_time')}</label>
            <div className="pills">
              {DURATIONS.map(([v, k]) => (
                <button key={v} className={`pill ${duration === v ? 'on' : ''}`} onClick={() => setDuration(v)}>{t(k)}</button>
              ))}
            </div>
          </div>
          <div className="filters__group">
            <label>{t('rec_category')}</label>
            <select value={cat} onChange={e => setCat(e.target.value)}>
              <option value="">{t('all')}</option>
              {cats.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </div>
          <div className="filters__actions">
            <button className="btn" onClick={fetchSuggestions} disabled={busy}>{busy ? t('rec_busy') : t('rec_btn')}</button>
            <button className="btn btn--ghost" onClick={fullyRandom} title={t('rec_random_title')}>{t('rec_random')}</button>
          </div>
        </motion.div>
        {err && <p className="err">{err}</p>}
      </motion.div>

      {busy && <div className="grid grid--4">{Array.from({ length: 20 }).map((_, i) => <div key={i} className="skeleton" />)}</div>}

      <AnimatePresence>
        {results && (
          <motion.section initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <div className="section-head">
              <h2>{results.length ? t('rec_count', { n: results.length }) : t('rec_none')}</h2>
              {results.length > 1 && (
                <button className="btn btn--sm" onClick={pickFromResults} disabled={spinning.current}>{t('rec_pick')}</button>
              )}
            </div>
            {results.length === 0 && <p className="muted">{t('rec_none_hint')}</p>}
            <motion.div className="grid grid--4" variants={stagger} initial="initial" animate="animate">
              {results.map((g, i) => (
                <GameCard key={`${g.source}-${g.id || g.title}`} game={g} highlight={spin === i} dim={spin >= 0 && spin !== i} onClick={() => setPicked(g)} />
              ))}
            </motion.div>
          </motion.section>
        )}
      </AnimatePresence>

      <Modal open={!!picked} onClose={() => { setPicked(null); setSpin(-1) }}>
        {picked && (
          <div className="pick">
            <p className="eyebrow">{modeLabel(picked.mode)}</p>
            {picked.cover_image_url && <img src={picked.cover_image_url} alt="" />}
            <h2>{picked.title}</h2>
            <p className="muted">{picked.estimated_hours ? t('approx_hours', { h: picked.estimated_hours }) : ''} · {picked.source === 'rawg' ? t('badge_rawg') : `${t('in_library')} (${platformsOf(picked)})`}</p>
            <div className="row">
              {picked.link && <a className="btn" href={picked.link} target="_blank" rel="noreferrer">{t('play_or_view')}</a>}
              <PlayLaterButton game={picked} className="pl-btn--inline" />
              {picked.mode === 'random' && <button className="btn btn--ghost" onClick={fullyRandom}>{t('spin_again')}</button>}
              {picked.mode === 'results' && <button className="btn btn--ghost" onClick={() => { setPicked(null); setTimeout(pickFromResults, 200) }}>{t('pick_again')}</button>}
            </div>
          </div>
        )}
      </Modal>
    </Page>
  )
}
