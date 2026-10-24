import { THEMES, useTheme } from '../context/ThemeContext'

const icons = {
  night: (
    <svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true">
      <path fill="currentColor" d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z" />
    </svg>
  ),
  day: (
    <svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true">
      <circle cx="12" cy="12" r="4.5" fill="currentColor" />
      <path
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"
      />
    </svg>
  ),
}

export default function ThemeToggle() {
  const { theme, setTheme } = useTheme()

  return (
    <div className="theme-toggle" role="radiogroup" aria-label="Тема сайту">
      {Object.entries(THEMES).map(([key, { label }]) => (
        <button
          key={key}
          type="button"
          role="radio"
          aria-checked={theme === key}
          title={label}
          className={theme === key ? 'active' : ''}
          onClick={() => setTheme(key)}
        >
          {icons[key]}
        </button>
      ))}
    </div>
  )
}
