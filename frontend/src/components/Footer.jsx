import { useT } from '../i18n'

const CONTACT = {
  email: 'hanbaba.kadir8@gmail.com',
  github: 'https://github.com/KHSatellite',
}

export default function Footer() {
  const { t } = useT()
  return (
    <footer className="footer" id="iletisim">
      <div className="footer__grid">
        <div>
          <div className="brand">NE<span>OYNASAM</span></div>
          <p className="muted">{t('brand_sub')}</p>
        </div>
        <div>
          <h4>{t('footer_contact')}</h4>
          <a href={`mailto:${CONTACT.email}`} className="footer__link">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="5" width="18" height="14" rx="2" /><path d="m3 7 9 6 9-6" /></svg>
            {CONTACT.email}
          </a>
          <a href={CONTACT.github} target="_blank" rel="noreferrer" className="footer__link">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M12 .5C5.7.5.5 5.7.5 12c0 5.1 3.3 9.4 7.9 10.9.6.1.8-.3.8-.6v-2c-3.2.7-3.9-1.4-3.9-1.4-.5-1.3-1.3-1.7-1.3-1.7-1-.7.1-.7.1-.7 1.2.1 1.8 1.2 1.8 1.2 1 1.8 2.7 1.3 3.4 1 .1-.8.4-1.3.7-1.6-2.6-.3-5.3-1.3-5.3-5.7 0-1.3.5-2.3 1.2-3.1-.1-.3-.5-1.5.1-3.1 0 0 1-.3 3.2 1.2a11 11 0 0 1 5.8 0c2.2-1.5 3.2-1.2 3.2-1.2.6 1.6.2 2.8.1 3.1.8.8 1.2 1.8 1.2 3.1 0 4.4-2.7 5.4-5.3 5.7.4.4.8 1.1.8 2.2v3.2c0 .3.2.7.8.6 4.6-1.5 7.9-5.8 7.9-10.9C23.5 5.7 18.3.5 12 .5z" /></svg>
            github.com/KHSatellite
          </a>
        </div>
        <div>
          <h4>{t('footer_sources')}</h4>
          <a className="footer__link" href="https://rawg.io" target="_blank" rel="noreferrer">{t('footer_rawg')}</a>
          <a className="footer__link" href="https://store.steampowered.com" target="_blank" rel="noreferrer">Steam</a>
        </div>
      </div>
      <div className="footer__bottom">© {new Date().getFullYear()} Ne Oynasam · {t('footer_note')}</div>
    </footer>
  )
}
