import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import Page, { fadeUp, stagger } from '../components/Page'
import GameCard from '../components/GameCard'
import { api } from '../api'
import { useAuth } from '../auth'
import { usePlayLater } from '../playLater'
import { useT } from '../i18n'

export default function Dashboard() {
  const { user } = useAuth()
  const { ids: plIds } = usePlayLater()
  const { t } = useT()
  const [lib, setLib] = useState(null)
  const [accounts, setAccounts] = useState([])

  useEffect(() => {
    api(`/users/${user.id}/library-overview`).then(setLib).catch(() => setLib([]))
    api(`/platform-accounts/?user_id=${user.id}`).then(setAccounts).catch(() => {})
  }, [user.id])

  const total = lib?.length ?? 0
  const done = lib?.filter(g => g.completed).length ?? 0
  const hours = Math.round(lib?.reduce((a, g) => a + (g.estimated_hours || 0), 0) ?? 0)
  const hasAny = accounts.length > 0
  const recent = (lib || []).filter(g => !g.completed).slice(0, 8)
  const hour = new Date().getHours()
  const greet = hour < 6 ? t('greet_night') : hour < 12 ? t('greet_morning') : hour < 18 ? t('greet_day') : t('greet_evening')

  return (
    <Page className="dash">
      <motion.div variants={stagger} initial="initial" animate="animate">
        <motion.h1 variants={fadeUp}>{greet}, <span className="grad">{user.username}</span></motion.h1>
        <motion.div variants={fadeUp} className="tiles">
          <div className="tile glass"><div className="tile__num">{total}</div><div className="tile__label">{t('tile_games')}</div></div>
          <Link to="/sonra-oyna" className="tile glass"><div className="tile__num">{plIds.size}</div><div className="tile__label">{t('tile_waiting')}</div></Link>
          <div className="tile glass"><div className="tile__num">{done}</div><div className="tile__label">{t('tile_done')}</div></div>
          <div className="tile glass"><div className="tile__num">{hours.toLocaleString()}</div><div className="tile__label">{t('tile_hours')}</div></div>
        </motion.div>

        <motion.div variants={fadeUp} className="actions">
          <Link to="/oyun-oner" className="action glass action--primary">
            <h3>{t('act_recommend_t')}</h3><p>{t('act_recommend_d')}</p>
          </Link>
          <Link to="/sonra-oyna" className="action glass">
            <h3>{t('act_later_t')}</h3><p>{plIds.size ? t('act_later_d_n', { n: plIds.size }) : t('act_later_d_0')}</p>
          </Link>
          {!hasAny ? (
            <Link to="/settings" className="action glass action--warn">
              <h3>{t('act_connect_t')}</h3><p>{t('act_connect_d')}</p>
            </Link>
          ) : (
            <Link to="/kutuphane" className="action glass">
              <h3>{t('act_library_t')}</h3><p>{t('act_library_d', { n: total })}</p>
            </Link>
          )}
        </motion.div>

        {lib === null ? <div className="spinner" /> : recent.length > 0 && (
          <motion.section variants={fadeUp}>
            <div className="section-head"><h2>{t('shelf_title')}</h2><Link to="/kutuphane" className="muted">{t('all_arrow')}</Link></div>
            <motion.div className="grid grid--4" variants={stagger} initial="initial" animate="animate">
              {recent.map(g => <GameCard key={g.game_id} game={{ ...g, id: g.game_id, source: 'library' }} />)}
            </motion.div>
          </motion.section>
        )}
      </motion.div>
    </Page>
  )
}
