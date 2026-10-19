import { motion } from 'framer-motion'
import { usePlayLater } from '../playLater'
import { useT } from '../i18n'

export const cardVariants = {
  initial: { opacity: 0, y: 28, scale: 0.96 },
  animate: { opacity: 1, y: 0, scale: 1, transition: { duration: 0.45, ease: [0.22, 1, 0.36, 1] } },
  exit: { opacity: 0, scale: 0.9, transition: { duration: 0.2 } },
}

export const PLATFORM_LABELS = {
  steam: 'Steam', epic: 'Epic', gog: 'GOG', ubisoft: 'Ubisoft', ea: 'EA', rockstar: 'Rockstar',
  battlenet: 'Battle.net', xbox: 'Xbox', playstation: 'PlayStation', nintendo: 'Nintendo', other: 'Diğer',
}

export function PlatformBadges({ platforms = [], source = 'library' }) {
  const { t } = useT()
  if (source === 'rawg') return <span className="badge badge--rawg">{t('badge_rawg')}</span>
  return (
    <span className="badges">
      {platforms.map(p => <span key={p} className={`badge badge--${p}`}>{PLATFORM_LABELS[p] || p}</span>)}
    </span>
  )
}

export function PlayLaterButton({ game, className = '' }) {
  const pl = usePlayLater()
  const { t } = useT()
  if (!pl || (!game.id && !game.rawg_id)) return null
  const on = pl.has(game)
  const inline = className.includes('pl-btn--inline')
  return (
    <button
      className={`pl-btn ${on ? 'on' : ''} ${className}`}
      title={on ? t('pl_remove') : t('pl_add')}
      onClick={e => { e.stopPropagation(); pl.toggle(game) }}
    >
      {on ? '★' : '☆'}{inline && <span> {on ? t('pl_in') : t('pl_label')}</span>}
    </button>
  )
}

export default function GameCard({ game, highlight = false, dim = false, onClick }) {
  const { t } = useT()
  const platforms = game.platforms?.length ? game.platforms : game.platform ? [game.platform] : []
  return (
    <motion.article
      variants={cardVariants}
      className={`gcard ${highlight ? 'gcard--hot' : ''} ${dim ? 'gcard--dim' : ''}`}
      whileHover={{ y: -6 }}
      onClick={onClick}
    >
      <div className="gcard__img">
        {game.cover_image_url ? <img src={game.cover_image_url} alt="" loading="lazy" /> : <div className="gcard__ph" />}
        <PlatformBadges platforms={platforms} source={game.source} />
        <PlayLaterButton game={game} />
      </div>
      <div className="gcard__body">
        <h4 title={game.title}>{game.title}</h4>
        <div className="gcard__meta">
          <span>{game.estimated_hours ? t('hours_approx', { h: game.estimated_hours }) : t('hours_unknown')}</span>
          {game.link && <a href={game.link} target="_blank" rel="noreferrer" onClick={e => e.stopPropagation()}>{t('open')}</a>}
        </div>
      </div>
    </motion.article>
  )
}
