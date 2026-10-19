import { createContext, useContext, useEffect, useState } from 'react'

export const THEMES = [
  { id: 'mix', name: 'theme_mix', desc: 'theme_mix_d' },
  { id: 'playstation', name: 'theme_ps', desc: 'theme_ps_d' },
  { id: 'netflix', name: 'theme_nf', desc: 'theme_nf_d' },
  { id: 'neon', name: 'theme_neon', desc: 'theme_neon_d' },
]

const KEY = 'ne_oynasam_theme'
const ThemeCtx = createContext(null)

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState(() => localStorage.getItem(KEY) || 'mix')
  useEffect(() => {
    document.documentElement.dataset.theme = theme
    localStorage.setItem(KEY, theme)
  }, [theme])
  return <ThemeCtx.Provider value={{ theme, setTheme }}>{children}</ThemeCtx.Provider>
}

export const useTheme = () => useContext(ThemeCtx)
