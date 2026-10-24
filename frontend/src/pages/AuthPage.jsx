import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { Field } from '../components/ui'
import { useAuth } from '../context/AuthContext'

export default function AuthPage({ mode }) {
  const isLogin = mode === 'login'
  const { login, register } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [form, setForm] = useState({ email: '', username: '', password: '' })
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const set = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }))

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    setBusy(true)
    try {
      if (isLogin) await login(form.email, form.password)
      else await register({ email: form.email, username: form.username, password: form.password })
      navigate(location.state?.from || '/boards', { replace: true })
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="auth-layout">
      <section className="auth-hero">
        <span className="eyebrow">Колективні рішення в реальному часі</span>
        <h1>
          Збирайте ідеї.
          <br />
          <span className="gradient-text">Голосуйте разом.</span>
        </h1>
        <p className="muted">
          Створюйте дошки для команди, пропонуйте ідеї та вирішуйте долю кожної з них у живому голосуванні з
          таймером.
        </p>
        <ul className="hero-points">
          <li>⚡ Голоси оновлюються миттєво через WebSocket</li>
          <li>⏱ Таймер на кожну ідею — до 24 годин</li>
          <li>🔒 Приватні та публічні дошки</li>
        </ul>
      </section>

      <form className="card auth-card" onSubmit={submit}>
        <h2>{isLogin ? 'Вхід' : 'Реєстрація'}</h2>
        <p className="muted">{isLogin ? 'Раді бачити знову 👋' : 'Створи акаунт за хвилину'}</p>

        <Field label="Email">
          <input type="email" required autoComplete="email" value={form.email} onChange={set('email')} />
        </Field>
        {!isLogin && (
          <Field label="Ім'я користувача" hint="3–25 символів">
            <input
              required
              minLength={3}
              maxLength={25}
              autoComplete="username"
              value={form.username}
              onChange={set('username')}
            />
          </Field>
        )}
        <Field label="Пароль" hint={isLogin ? null : 'Мінімум 4 символи'}>
          <input
            type="password"
            required
            minLength={4}
            autoComplete={isLogin ? 'current-password' : 'new-password'}
            value={form.password}
            onChange={set('password')}
          />
        </Field>

        {error && <div className="alert">{error}</div>}

        <button className="btn btn-primary btn-block" disabled={busy}>
          {busy ? 'Зачекай…' : isLogin ? 'Увійти' : 'Зареєструватися'}
        </button>

        <p className="auth-switch muted">
          {isLogin ? 'Немає акаунта? ' : 'Вже є акаунт? '}
          <Link to={isLogin ? '/register' : '/login'}>{isLogin ? 'Зареєструйся' : 'Увійди'}</Link>
        </p>
      </form>
    </div>
  )
}
