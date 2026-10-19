import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import Page, { fadeUp, stagger } from '../components/Page'
import GameCard, { PLATFORM_LABELS, PlayLaterButton } from '../components/GameCard'
import Modal from '../components/Modal'
import { api } from '../api'
import { usePlayLater } from '../playLater'
import { useT } from '../i18n'

export default function PlayLater() {
  const { ids } = usePlayLater()
  const { t } = useT()
  const [items, setItems] = useState(null)
  const [picked, setPicked] = useState(null)

  useEffect(() => { api('/play-later/').then(setItems).catch(() => setItems([])) }, [ids.size])  // eslint-disable-line

  const shown = (items || []).filter(g => ids.has(g.id))
  const pickRandom = () => shown.length && setPicked({ ...shown[Math.floor(Math.random() * shown.length)], mode: 'list' })

  return (
    <Page className="pl">
      <motion.div variants={stagger} initial="initial" animate="animate">
        <motion.div variants={fadeUp} className="section-head">
          <div>
            <h1>{t('later_title_1')} <span className="grad">{t('later_title_2')}</span></h1>
            <p className="muted">{t('later_sub')}</p>
          </div>
          {shown.length > 1 && <button className="btn btn--sm" onClick={pickRandom}>{t('later_random')}</button>}
        </motion.div>
      </motion.div>

      {items === null ? <div className="spinner" /> : shown.length === 0 ? (
        <div className="empty glass">
          <h3>{t('later_empty_t')}</h3>
          <p className="muted">{t('later_empty_d')}</p>
          <div className="row"><Link to="/oyun-oner" className="btn">{t('act_recommend_t')}</Link><Link to="/kutuphane" className="btn btn--ghost">{t('nav_library')}</Link></div>
        </div>
      ) : (
        <motion.div className="grid grid--4" variants={stagger} initial="initial" animate="animate">
          {shown.map(g => <GameCard key={g.id} game={g} onClick={() => setPicked(g)} />)}
        </motion.div>
      )}

      <Modal open={!!picked} onClose={() => setPicked(null)}>
        {picked && (
          <div className="pick">
            <p className="eyebrow">{picked.mode ? t('mode_from_list') : (picked.platforms?.length ? picked.platforms.map(p => PLATFORM_LABELS[p] || p).join(' · ') : t('badge_rawg'))}</p>
            {picked.cover_image_url && <img src={picked.cover_image_url} alt="" />}
            <h2>{picked.title}</h2>
            <p className="muted">{picked.estimated_hours ? t('approx_hours', { h: picked.estimated_hours }) : ''}{picked.source === 'rawg' ? ` · ${t('not_in_library')}` : ''}</p>
            <div className="row">
              {picked.link && <a className="btn" href={picked.link} target="_blank" rel="noreferrer">{t('play_or_view')}</a>}
              <PlayLaterButton game={picked} className="pl-btn--inline" />
              {picked.mode && <button className="btn btn--ghost" onClick={pickRandom}>{t('again')}</button>}
            </div>
          </div>
        )}
      </Modal>
    </Page>
  )
}
