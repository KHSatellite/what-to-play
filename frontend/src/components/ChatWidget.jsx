import { useEffect, useRef, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { getToken } from '../api'
import { useAuth } from '../auth'
import { useT } from '../i18n'

function wsUrl(lang) {
  const proto = window.location.protocol === 'https:' ? 'wss' : 'ws'
  const tok = getToken()
  const q = new URLSearchParams({ lang })
  if (tok) q.set('token', tok)
  return `${proto}://${window.location.host}/ws/chat?${q}`
}

function linkify(text) {
  return text.split(/(https?:\/\/\S+)/g).map((part, i) =>
    /^https?:\/\//.test(part) ? <a key={i} href={part} target="_blank" rel="noreferrer">{part.replace(/^https?:\/\//, '').slice(0, 40)}…</a> : part,
  )
}

export default function ChatWidget() {
  const { user } = useAuth()
  const { t, lang } = useT()
  const QUICK = [t('chat_q1'), t('chat_q2'), t('chat_q3'), t('chat_q4'), t('chat_q5')]
  const [open, setOpen] = useState(false)
  const [msgs, setMsgs] = useState([])
  const [text, setText] = useState('')
  const [typing, setTyping] = useState(false)
  const [unread, setUnread] = useState(0)
  const ws = useRef(null)
  const listRef = useRef(null)
  const openRef = useRef(false)

  const connect = () => {
    if (ws.current && ws.current.readyState <= 1) return
    const sock = new WebSocket(wsUrl(lang))
    sock.onmessage = (e) => {
      let data; try { data = JSON.parse(e.data) } catch { data = { from: 'bot', text: e.data } }
      setTyping(false)
      setMsgs(m => [...m, { ...data, t: Date.now() }])
      if (!openRef.current) setUnread(u => u + 1)
    }
    sock.onclose = () => { ws.current = null }
    ws.current = sock
  }

  // kullanıcı ya da dil değişince bağlantıyı yenile ki bot kimliği ve dili doğru olsun
  useEffect(() => {
    if (ws.current) { ws.current.close(); ws.current = null }
    setMsgs([])
    if (openRef.current) connect()
  }, [user?.id, lang])  // eslint-disable-line

  useEffect(() => { openRef.current = open; if (open) { setUnread(0); connect() } }, [open])  // eslint-disable-line
  useEffect(() => { listRef.current?.scrollTo({ top: 1e9, behavior: 'smooth' }) }, [msgs, typing])

  const send = (value) => {
    const v = (value ?? text).trim()
    if (!v) return
    if (!ws.current || ws.current.readyState !== 1) {
      connect()
      setTimeout(() => send(v), 400)
      return
    }
    setMsgs(m => [...m, { from: 'me', text: v, t: Date.now() }])
    setTyping(true)
    ws.current.send(v)
    setText('')
  }

  return (
    <>
      <button className={`chat-fab ${open ? 'chat-fab--open' : ''}`} onClick={() => setOpen(o => !o)} aria-label="Asistan">
        {open ? '×' : (
          <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z" />
          </svg>
        )}
        {!open && unread > 0 && <span className="chat-fab__badge">{unread}</span>}
      </button>

      <AnimatePresence>
        {open && (
          <motion.div className="chat-panel glass" initial={{ opacity: 0, y: 20, scale: 0.96 }} animate={{ opacity: 1, y: 0, scale: 1 }} exit={{ opacity: 0, y: 20, scale: 0.96 }} transition={{ duration: 0.2 }}>
            <div className="chat-panel__head">
              <div className="chat-avatar">🎮</div>
              <div>
                <strong>{t('chat_title')}</strong>
                <small className="muted">{user ? t('chat_hello', { name: user.username }) : t('chat_guest')} · {t('chat_fast')}</small>
              </div>
            </div>
            <div className="chat-panel__list" ref={listRef}>
              {msgs.map((m, i) => (
                <div key={m.t + '-' + i} className={`chat-msg chat-msg--${m.from}`}>{linkify(m.text)}</div>
              ))}
              {typing && <div className="chat-msg chat-msg--bot chat-typing"><span /><span /><span /></div>}
            </div>
            <div className="chat-panel__quick">
              {QUICK.map(q => <button key={q} className="pill" onClick={() => send(q)}>{q}</button>)}
            </div>
            <form className="chat-panel__input" onSubmit={e => { e.preventDefault(); send() }}>
              <input value={text} onChange={e => setText(e.target.value)} placeholder={t('chat_placeholder')} autoFocus />
              <button className="btn btn--sm" disabled={!text.trim()}>{t('send')}</button>
            </form>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}
