import { useEffect, useMemo, useRef, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import Page, { fadeUp, stagger } from '../components/Page'
import GameCard, { PLATFORM_LABELS, PlayLaterButton } from '../components/GameCard'
import Modal from '../components/Modal'
import { api } from '../api'
import { useAuth } from '../auth'
import { useT } from '../i18n'

function AddGameModal({ open, onClose, platforms, onAdded }) {
  const { t } = useT()
  const [platform, setPlatform] = useState('')
  const [q, setQ] = useState('')
  const [results, setResults] = useState([])
  const [busy, setBusy] = useState(false)
  const [msg, setMsg] = useState('')
  const timer = useRef(null)

  useEffect(() => { if (open && !platform && platforms.length) setPlatform(platforms[0].name) }, [open, platforms, platform])

  useEffect(() => {
    clearTimeout(timer.current)
    if (q.trim().length < 2) { setResults([]); return }
    timer.current = setTimeout(async () => {
      setBusy(true)
      try { setResults(await api(`/platform-accounts/rawg-search?q=${encodeURIComponent(q.trim())}`)) }
      catch { setResults([]) }
      finally { setBusy(false) }
    }, 350)
    return () => clearTimeout(timer.current)
  }, [q])

  const add = async (g) => {
    setMsg('')
    try {
      await api('/platform-accounts/manual-add', { method: 'POST', body: { platform, rawg_id: g.rawg_id } })
      setMsg(t('added', { title: g.title }))
      onAdded()
    } catch (e) { setMsg(e.message) }
  }

  return (
    <Modal open={open} onClose={onClose}>
      <h2>{t('add_title')}</h2>
      <p className="muted small">{t('add_sub')}</p>
      <div className="row">
        <select value={platform} onChange={e => setPlatform(e.target.value)}>
          {platforms.map(p => <option key={p.name} value={p.name}>{p.label}</option>)}
        </select>
        <input autoFocus placeholder={t('add_placeholder')} value={q} onChange={e => setQ(e.target.value)} style={{ flex: 1 }} />
      </div>
      {msg && <p className="note">{msg}</p>}
      <div className="search-list">
        {busy && <div className="spinner" />}
        {!busy && results.map(g => (
          <div key={g.rawg_id} className="search-item">
            {g.cover_image_url ? <img src={g.cover_image_url} alt="" /> : <div className="search-item__ph" />}
            <div className="search-item__body">
              <strong>{g.title}</strong>
              <small className="muted">{g.released ? g.released.slice(0, 4) : ''}{g.estimated_hours ? ` · ${t('hours_approx', { h: g.estimated_hours })}` : ''}</small>
            </div>
            <button className="btn btn--sm" onClick={() => add(g)}>{t('add_btn')}</button>
          </div>
        ))}
        {!busy && q.trim().length >= 2 && results.length === 0 && <p className="muted">{t('no_results')}</p>}
      </div>
    </Modal>
  )
}

export default function Library() {
  const { user } = useAuth()
  const { t } = useT()
  const [sp, setSp] = useSearchParams()
  const [lib, setLib] = useState(null)
  const [q, setQ] = useState('')
  const [filter, setFilter] = useState('all')
  const [cat, setCat] = useState('')
  const [plat, setPlat] = useState('')
  const [manualPlatforms, setManualPlatforms] = useState([])
  const [adding, setAdding] = useState(!!sp.get('add'))
  const [picked, setPicked] = useState(null)

  const load = () => api(`/users/${user.id}/library-overview`).then(setLib).catch(() => setLib([]))
  useEffect(() => {
    load()
    api('/platform-accounts/connectors').then(c => setManualPlatforms(c.manual)).catch(() => {})
  }, [user.id])  // eslint-disable-line

  const cats = useMemo(() => [...new Set((lib || []).flatMap(g => g.categories || []))].sort(), [lib])
  const plats = useMemo(() => [...new Set((lib || []).flatMap(g => g.platforms || []))].sort(), [lib])
  const shown = useMemo(() => (lib || []).filter(g =>
    (filter === 'all' || (filter === 'done') === g.completed) &&
    (!cat || (g.categories || []).includes(cat)) &&
    (!plat || (g.platforms || []).includes(plat)) &&
    g.title.toLowerCase().includes(q.toLowerCase())
  ), [lib, q, filter, cat, plat])

  const toggleDone = async (g) => {
    const completed = !g.completed
    setLib(l => l.map(x => x.game_id === g.game_id ? { ...x, completed } : x))
    try { await Promise.all(g.entries.map(e => api(`/library-entries/${e.entry_id}`, { method: 'PUT', body: { completed } }))) }
    catch { load() }
  }

  const removeEntry = async (g) => {
    if (!window.confirm(t('remove_confirm', { title: g.title, p: g.platforms.map(p => PLATFORM_LABELS[p] || p).join(', ') }))) return
    setLib(l => l.filter(x => x.game_id !== g.game_id))
    try { await Promise.all(g.entries.map(e => api(`/library-entries/${e.entry_id}`, { method: 'DELETE' }))) } catch { load() }
  }

  const closeAdd = () => { setAdding(false); if (sp.get('add')) setSp({}, { replace: true }) }

  return (
    <Page className="lib">
      <motion.div variants={stagger} initial="initial" animate="animate">
        <motion.div variants={fadeUp} className="section-head">
          <h1>{t('lib_title')}</h1>
          <div className="row">
            {lib && <span className="muted">{t('lib_count', { a: shown.length, b: lib.length })}</span>}
            <button className="btn btn--sm" onClick={() => setAdding(true)}>{t('add_game')}</button>
          </div>
        </motion.div>
        <motion.div variants={fadeUp} className="filters glass filters--lib">
          <input placeholder={t('search_game')} value={q} onChange={e => setQ(e.target.value)} />
          <select value={plat} onChange={e => setPlat(e.target.value)}>
            <option value="">{t('all_platforms')}</option>
            {plats.map(p => <option key={p} value={p}>{PLATFORM_LABELS[p] || p}</option>)}
          </select>
          <select value={cat} onChange={e => setCat(e.target.value)}>
            <option value="">{t('all_categories')}</option>
            {cats.map(c => <option key={c} value={c}>{c}</option>)}
          </select>
          <div className="pills">
            {[['all', 'filt_all'], ['todo', 'filt_todo'], ['done', 'filt_done']].map(([v, k]) => (
              <button key={v} className={`pill ${filter === v ? 'on' : ''}`} onClick={() => setFilter(v)}>{t(k)}</button>
            ))}
          </div>
        </motion.div>
      </motion.div>

      {lib === null ? <div className="spinner" /> : lib.length === 0 ? (
        <div className="empty glass">
          <h3>{t('lib_empty_t')}</h3>
          <p className="muted">{t('lib_empty_d')}</p>
          <div className="row"><Link to="/settings" className="btn">{t('connect_platform')}</Link><button className="btn btn--ghost" onClick={() => setAdding(true)}>{t('add_game_plain')}</button></div>
        </div>
      ) : (
        <motion.div className="grid grid--4" variants={stagger} initial="initial" animate="animate">
          {shown.map(g => (
            <div key={g.game_id} className="lib__item">
              <GameCard game={{ ...g, id: g.game_id, source: 'library' }} dim={g.completed} onClick={() => setPicked({ ...g, id: g.game_id })} />
              <div className="row">
                <button className={`chip ${g.completed ? 'chip--on' : ''}`} onClick={() => toggleDone(g)}>{g.completed ? t('is_done') : t('mark_done')}</button>
                <button className="chip chip--ghost" onClick={() => removeEntry(g)} title={t('remove')}>{t('remove')}</button>
              </div>
            </div>
          ))}
        </motion.div>
      )}

      <AddGameModal open={adding} onClose={closeAdd} platforms={manualPlatforms} onAdded={load} />

      <Modal open={!!picked} onClose={() => setPicked(null)}>
        {picked && (
          <div className="pick">
            <p className="eyebrow">{(picked.platforms || []).map(p => PLATFORM_LABELS[p] || p).join(' · ')}</p>
            {picked.cover_image_url && <img src={picked.cover_image_url} alt="" />}
            <h2>{picked.title}</h2>
            <p className="muted">{picked.estimated_hours ? t('approx_hours', { h: picked.estimated_hours }) : ''}{picked.categories?.length ? ` · ${picked.categories.join(', ')}` : ''}</p>
            <div className="row">
              {picked.link && <a className="btn" href={picked.link} target="_blank" rel="noreferrer">{t('play_or_view')}</a>}
              <PlayLaterButton game={picked} className="pl-btn--inline" />
              <button className="btn btn--ghost" onClick={() => { toggleDone(picked); setPicked({ ...picked, completed: !picked.completed }) }}>{picked.completed ? t('undo_done') : t('mark_done')}</button>
            </div>
          </div>
        )}
      </Modal>
    </Page>
  )
}
