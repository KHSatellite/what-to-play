import { createContext, useContext, useEffect, useState, useCallback } from 'react'
import { api, getToken, setToken, clearToken } from './api'

const AuthCtx = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(!!getToken())
  const [expired, setExpired] = useState(false)

  const refresh = useCallback(async () => {
    if (!getToken()) { setUser(null); setLoading(false); return }
    try { setUser(await api('/users/me')) }
    catch { setUser(null) }
    finally { setLoading(false) }
  }, [])

  useEffect(() => { refresh() }, [refresh])
  useEffect(() => {
    const onExpired = () => { setExpired(true); setUser(null) }
    window.addEventListener('auth:expired', onExpired)
    return () => window.removeEventListener('auth:expired', onExpired)
  }, [])

  const login = async (username, password) => {
    const { access_token } = await api('/auth/token', { method: 'POST', form: { username, password }, auth: false })
    setToken(access_token)
    setExpired(false)
    await refresh()
  }

  const register = async ({ username, email, password, short_max_hours, medium_max_hours }) => {
    await api('/users/', { method: 'POST', body: { username, email, password }, auth: false })
    await login(username, password)
    const me = await api('/users/me')
    await api(`/users/${me.id}/settings`, { method: 'PUT', body: { short_max_hours, medium_max_hours } })
  }

  const logout = () => { clearToken(); setExpired(false); setUser(null) }

  return <AuthCtx.Provider value={{ user, loading, expired, login, register, logout, refresh }}>{children}</AuthCtx.Provider>
}

export const useAuth = () => useContext(AuthCtx)
