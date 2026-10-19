import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import { api } from './api'
import { useAuth } from './auth'

const Ctx = createContext(null)

// "Sonra oyna" listesindeki game_id'leri tek yerde tutar; kartlardaki yıldız anında güncellenir
export function PlayLaterProvider({ children }) {
  const { user } = useAuth()
  // game_id set'i + rawg_id → game_id eşlemesi (RAWG kartlarının henüz game_id'si yok)
  const [ids, setIds] = useState(new Set())
  const [byRawg, setByRawg] = useState(new Map())

  const apply = (rows) => {
    setIds(new Set(rows.map(r => r.game_id)))
    setByRawg(new Map(rows.filter(r => r.rawg_id != null).map(r => [r.rawg_id, r.game_id])))
  }
  const refresh = useCallback(async () => {
    if (!user) { apply([]); return }
    try { apply(await api('/play-later/ids')) } catch { /* sessiz */ }
  }, [user])
  useEffect(() => { refresh() }, [refresh])

  const resolveId = (game) => game.id || (game.rawg_id != null ? byRawg.get(game.rawg_id) : null)
  const has = (game) => { const id = resolveId(game); return !!id && ids.has(id) }

  const toggle = async (game) => {
    const id = resolveId(game)
    if (id && ids.has(id)) {
      setIds(s => { const n = new Set(s); n.delete(id); return n })
      await api(`/play-later/${id}`, { method: 'DELETE' }).catch(refresh)
      return false
    }
    const r = await api('/play-later/', { method: 'POST', body: { game_id: game.id || null, rawg_id: game.rawg_id || null } })
    setIds(s => new Set(s).add(r.game_id))
    if (game.rawg_id != null) setByRawg(m => new Map(m).set(game.rawg_id, r.game_id))
    return true
  }

  return <Ctx.Provider value={{ ids, has, toggle, refresh }}>{children}</Ctx.Provider>
}

export const usePlayLater = () => useContext(Ctx)
