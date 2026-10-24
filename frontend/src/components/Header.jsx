import { useEffect, useRef, useState } from 'react'
import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import ThemeToggle from './ThemeToggle'
import { Avatar } from './ui'

export default function Header() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [menuOpen, setMenuOpen] = useState(false)
  const menuRef = useRef(null)

  useEffect(() => {
    if (!menuOpen) return undefined
    const close = (e) => !menuRef.current?.contains(e.target) && setMenuOpen(false)
    document.addEventListener('mousedown', close)
    return () => document.removeEventListener('mousedown', close)
  }, [menuOpen])

  const handleLogout = () => {
    logout()
    setMenuOpen(false)
    navigate('/login')
  }

  return (
    <header className="topbar">
      <div className="topbar-inner">
        <Link to={user ? '/boards' : '/login'} className="brand">
          <span className="brand-mark">◆</span>
          <span>
            Think<b>Board</b>
          </span>
        </Link>

        {user && (
          <nav className="topnav">
            <NavLink to="/boards">Дошки</NavLink>
            <NavLink to="/profile">Профіль</NavLink>
          </nav>
        )}

        <div className="topbar-right">
          <ThemeToggle />
          {user && (
            <div className="user-menu" ref={menuRef}>
              <button className="user-chip" onClick={() => setMenuOpen((o) => !o)} aria-expanded={menuOpen}>
                <Avatar user={user} size={30} />
                <span className="user-chip-name">{user.username}</span>
              </button>
              {menuOpen && (
                <div className="dropdown">
                  <div className="dropdown-head">
                    <b>{user.username}</b>
                    <span className="muted">{user.email}</span>
                  </div>
                  <Link to="/profile" onClick={() => setMenuOpen(false)}>
                    Налаштування профілю
                  </Link>
                  <Link to={`/u/${user.username}`} onClick={() => setMenuOpen(false)}>
                    Публічна сторінка
                  </Link>
                  <button onClick={handleLogout} className="danger-text">
                    Вийти
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
