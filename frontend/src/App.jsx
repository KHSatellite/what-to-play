import { useEffect, useRef } from 'react'
import { Routes, Route, useLocation, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useAuth } from './auth'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import ChatWidget from './components/ChatWidget'
import { pageVariants } from './components/Page'
import Landing from './pages/Landing'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Recommend from './pages/Recommend'
import Library from './pages/Library'
import Settings from './pages/Settings'
import PlayLater from './pages/PlayLater'

const Spinner = () => <div className="center-screen"><div className="spinner" /></div>

// Yönlendirme tek seferlik effect ile; sadece hâlâ kendi rotasındaysa tetiklenir (çift yönlendirme/döngü yok).
function useGuard(shouldRedirect, to, state) {
  const nav = useNavigate()
  const loc = useLocation()
  const own = useRef(loc.pathname)
  useEffect(() => {
    if (shouldRedirect && loc.pathname === own.current) nav(to, { replace: true, state })
  }, [shouldRedirect, loc.pathname])  // eslint-disable-line
}

function Redirect({ to }) {
  useGuard(true, to)
  return null
}

function Private({ children }) {
  const { user, loading, expired } = useAuth()
  const loc = useLocation()
  const had = useRef(false)
  if (user) had.current = true
  // süre doldu → login (uyarılı); çıkış yaptı → ana sayfa; giriş yapmadan geldi → login
  const to = expired ? '/login?expired=1' : had.current ? '/' : '/login'
  useGuard(!loading && !user, to, { from: loc.pathname })
  return loading || !user ? <Spinner /> : children
}

function Guest({ children }) {
  const { user, loading } = useAuth()
  const loc = useLocation()
  useGuard(!loading && !!user, loc.state?.from || '/panel')
  return loading ? <Spinner /> : children
}

export default function App() {
  const loc = useLocation()
  return (
    <div className="app">
      <div className="bg-orbs" aria-hidden="true"><span /><span /><span /></div>
      <Navbar />
      <main>
        {/* Sayfa değişiminde giriş animasyonu; çıkış animasyonu yok (AnimatePresence, çıkış sırasında
            ağaç yeniden render olursa takılıyor — login/logout tam da bunu yapıyor). */}
        <motion.div key={loc.pathname} variants={pageVariants} initial="initial" animate="animate">
            <Routes location={loc}>
              <Route path="/" element={<Landing />} />
              <Route path="/login" element={<Guest><Login /></Guest>} />
              <Route path="/register" element={<Guest><Register /></Guest>} />
              <Route path="/panel" element={<Private><Dashboard /></Private>} />
              <Route path="/oyun-oner" element={<Private><Recommend /></Private>} />
              <Route path="/kutuphane" element={<Private><Library /></Private>} />
              <Route path="/settings" element={<Private><Settings /></Private>} />
              <Route path="/sonra-oyna" element={<Private><PlayLater /></Private>} />
              <Route path="/oner" element={<Redirect to="/oyun-oner" />} />
              <Route path="*" element={<Redirect to="/" />} />
            </Routes>
        </motion.div>
      </main>
      <Footer />
      <ChatWidget />
    </div>
  )
}
