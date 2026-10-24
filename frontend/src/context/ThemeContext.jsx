import { createContext, useCallback, useContext, useEffect, useState } from 'react'

export const THEMES = {
  night: { label: 'Чорно-фіолетова' },
  day: { label: 'Біло-синя' },
}

const ThemeContext = createContext(null)

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState(() => document.documentElement.dataset.theme || 'night')

  useEffect(() => {
    document.documentElement.dataset.theme = theme
    try {
      localStorage.setItem('tb-theme', theme)
    } catch {
      /* ігноруємо */
    }
  }, [theme])

  const toggle = useCallback(() => setTheme((t) => (t === 'night' ? 'day' : 'night')), [])

  return (
    <ThemeContext.Provider value={{ theme, setTheme, toggle }}>{children}</ThemeContext.Provider>
  )
}

export const useTheme = () => useContext(ThemeContext)
