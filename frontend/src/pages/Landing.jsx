import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { motion, useScroll, useTransform, useMotionValue, useInView, animate } from 'framer-motion'
import Page, { fadeUp, stagger } from '../components/Page'
import { api } from '../api'
import { useAuth } from '../auth'
import { useT } from '../i18n'

const FALLBACK = Array.from({ length: 12 }, (_, i) => ({ title: `Game ${i + 1}`, cover_image_url: null }))

function Counter({ to, label }) {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-80px' })
  const mv = useMotionValue(0)
  const [val, setVal] = useState(0)
  useEffect(() => {
    if (!inView) return
    const c = animate(mv, to, { duration: 1.6, ease: 'easeOut', onUpdate: v => setVal(Math.round(v)) })
    return c.stop
  }, [inView, to, mv])
  return (
    <div className="stat" ref={ref}>
      <div className="stat__num">{val.toLocaleString()}</div>
      <div className="stat__label">{label}</div>
    </div>
  )
}

function Boxes({ games }) {
  const ref = useRef(null)
  const { scrollYProgress } = useScroll({ target: ref, offset: ['start end', 'end start'] })
  const rot = useTransform(scrollYProgress, [0, 1], [-30, 390])
  const covers = (games.length ? games : FALLBACK).slice(0, 6)
  return (
    <div className="boxes" ref={ref}>
      <motion.div className="boxes__ring" style={{ rotateY: rot }}>
        {covers.map((g, i) => (
          <div key={i} className="box" style={{ transform: `rotateY(${i * 60}deg) translateZ(230px)` }}>
            {g.cover_image_url ? <img src={g.cover_image_url} alt="" /> : <div className="box__ph">{g.title}</div>}
            <div className="box__spine" />
          </div>
        ))}
      </motion.div>
      <div className="boxes__glow" />
    </div>
  )
}

function Marquee({ items, reverse }) {
  const list = [...items, ...items]
  return (
    <div className={`marquee ${reverse ? 'marquee--rev' : ''}`}>
      <div className="marquee__track">
        {list.map((g, i) => (
          <a key={i} className="marquee__item" href={g.link || '#'} target={g.link ? '_blank' : undefined} rel="noreferrer">
            {g.cover_image_url ? <img src={g.cover_image_url} alt="" loading="lazy" /> : <div className="box__ph">{g.title}</div>}
            <span>{g.title}</span>
          </a>
        ))}
      </div>
    </div>
  )
}

export default function Landing() {
  const { user } = useAuth()
  const { t } = useT()
  const [data, setData] = useState({ games: [], stats: { games: 0, categories: 0, users: 0 } })
  useEffect(() => { api('/public/showcase', { auth: false }).then(setData).catch(() => {}) }, [])
  const games = data.games || []
  const STEPS = [1, 2, 3].map(n => ({ n: `0${n}`, t: t(`step${n}_t`), d: t(`step${n}_d`) }))
  const FEATURES = [1, 2, 3, 4].map(n => ({ t: t(`f${n}_t`), d: t(`f${n}_d`) }))

  return (
    <Page className="landing">
      <section className="hero">
        <motion.div className="hero__text" variants={stagger} initial="initial" animate="animate">
          <motion.p variants={fadeUp} className="eyebrow">{t('hero_eyebrow')}</motion.p>
          <motion.h1 variants={fadeUp}>{t('hero_title_1')}<br /><span className="grad">{t('hero_title_2')}</span></motion.h1>
          <motion.p variants={fadeUp} className="lead">{t('hero_lead')}</motion.p>
          <motion.div variants={fadeUp} className="hero__cta">
            <Link to={user ? '/oyun-oner' : '/register'} className="btn btn--lg">{user ? t('hero_cta_user') : t('hero_cta_guest')}</Link>
            <a href="#nasil" className="btn btn--ghost btn--lg">{t('hero_how')}</a>
          </motion.div>
        </motion.div>
        <Boxes games={games} />
      </section>

      <section className="showcase">
        <div className="section-head"><h2>{t('showcase_title')}</h2><p className="muted">{t('showcase_sub')}</p></div>
        <Marquee items={games.length ? games.slice(0, 12) : FALLBACK} />
        <Marquee items={games.length ? games.slice(12, 24) : FALLBACK} reverse />
      </section>

      <section className="steps" id="nasil">
        <div className="section-head"><h2>{t('steps_title')}</h2></div>
        <div className="steps__grid">
          {STEPS.map((s, i) => (
            <motion.div key={s.n} className="step glass" initial={{ opacity: 0, y: 40 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, margin: '-60px' }} transition={{ delay: i * 0.12, duration: 0.55 }}>
              <div className="step__n">{s.n}</div>
              <h3>{s.t}</h3>
              <p>{s.d}</p>
            </motion.div>
          ))}
        </div>
      </section>

      <section className="features">
        <div className="section-head"><h2>{t('features_title')}</h2></div>
        <div className="features__grid">
          {FEATURES.map((f, i) => (
            <motion.div key={f.t} className="feature glass" initial={{ opacity: 0, scale: 0.94 }} whileInView={{ opacity: 1, scale: 1 }} viewport={{ once: true }} transition={{ delay: i * 0.08 }}>
              <h3>{f.t}</h3><p>{f.d}</p>
            </motion.div>
          ))}
        </div>
        <div className="stats">
          <Counter to={data.stats?.games || 0} label={t('stat_games')} />
          <Counter to={data.stats?.categories || 0} label={t('stat_categories')} />
          <Counter to={data.stats?.users || 0} label={t('stat_users')} />
        </div>
      </section>

      <section className="cta-band glass">
        <h2>{t('cta_title')}</h2>
        <Link to={user ? '/oyun-oner' : '/register'} className="btn btn--lg">{user ? t('hero_cta_user') : t('cta_guest')}</Link>
      </section>
    </Page>
  )
}
