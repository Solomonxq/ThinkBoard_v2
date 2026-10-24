import { useRef, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import { Avatar, Field, Modal } from '../components/ui'
import { useAuth } from '../context/AuthContext'
import { THEMES, useTheme } from '../context/ThemeContext'
import { useToast } from '../context/ToastContext'

export default function ProfilePage() {
  const { user, setUser, logout } = useAuth()
  const { theme, setTheme } = useTheme()
  const toast = useToast()
  const navigate = useNavigate()
  const fileRef = useRef(null)
  const [form, setForm] = useState({ username: user.username, bio: user.bio || '' })
  const [busy, setBusy] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [confirmDelete, setConfirmDelete] = useState(false)

  const dirty = form.username !== user.username || form.bio !== (user.bio || '')

  const save = async (e) => {
    e.preventDefault()
    setBusy(true)
    try {
      const patch = {}
      if (form.username !== user.username) patch.username = form.username
      if (form.bio !== (user.bio || '')) patch.bio = form.bio
      const updated = await api.profile.update(patch)
      setUser({ ...user, ...updated })
      toast.success('Профіль збережено')
    } catch (err) {
      toast.error(err.message)
    } finally {
      setBusy(false)
    }
  }

  const uploadAvatar = async (e) => {
    const file = e.target.files?.[0]
    e.target.value = ''
    if (!file) return
    if (file.size > 5 * 1024 * 1024) {
      toast.error('Файл завеликий, максимум 5 МБ')
      return
    }
    setUploading(true)
    try {
      const updated = await api.profile.uploadAvatar(file)
      setUser({ ...user, avatar_url: updated.avatar_url })
      toast.success('Аватар оновлено')
    } catch (err) {
      toast.error(err.message)
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="page narrow">
      <div className="page-head">
        <div>
          <span className="eyebrow">Налаштування</span>
          <h1>Профіль</h1>
        </div>
        <Link className="btn btn-ghost" to={`/u/${user.username}`}>
          Переглянути публічно
        </Link>
      </div>

      <section className="card profile-card">
        <div className="avatar-edit">
          <Avatar user={user} size={96} />
          <div>
            <b>{user.username}</b>
            <span className="muted block">{user.email}</span>
            <button className="btn btn-ghost btn-sm" onClick={() => fileRef.current?.click()} disabled={uploading}>
              {uploading ? 'Завантажую…' : 'Змінити аватар'}
            </button>
            <input ref={fileRef} type="file" accept="image/png,image/jpeg,image/webp" hidden onChange={uploadAvatar} />
          </div>
        </div>

        <form className="form" onSubmit={save}>
          <Field label="Ім'я користувача" hint="3–25 символів">
            <input
              required
              minLength={3}
              maxLength={25}
              value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })}
            />
          </Field>
          <Field label="Про себе" hint={`${form.bio.length}/500`}>
            <textarea rows={4} maxLength={500} value={form.bio} onChange={(e) => setForm({ ...form, bio: e.target.value })} />
          </Field>
          <div className="form-actions">
            <button className="btn btn-primary" disabled={!dirty || busy}>
              {busy ? 'Зберігаю…' : 'Зберегти'}
            </button>
          </div>
        </form>
      </section>

      <section className="card">
        <h3>Тема оформлення</h3>
        <div className="theme-cards">
          {Object.entries(THEMES).map(([key, { label }]) => (
            <button key={key} className={`theme-card theme-card-${key} ${theme === key ? 'active' : ''}`} onClick={() => setTheme(key)}>
              <span className="theme-preview">
                <span />
                <span />
                <span />
              </span>
              {label}
            </button>
          ))}
        </div>
      </section>

      <section className="card danger-zone">
        <h3>Небезпечна зона</h3>
        <p className="muted">Видалення акаунта прибере всі твої дошки, ідеї та голоси. Відновити не вийде.</p>
        <button className="btn btn-danger" onClick={() => setConfirmDelete(true)}>
          Видалити акаунт
        </button>
      </section>

      {confirmDelete && (
        <DeleteAccountModal
          username={user.username}
          onClose={() => setConfirmDelete(false)}
          onDeleted={() => {
            logout()
            navigate('/register')
          }}
        />
      )}
    </div>
  )
}

function DeleteAccountModal({ username, onClose, onDeleted }) {
  const toast = useToast()
  const [value, setValue] = useState('')
  const [busy, setBusy] = useState(false)

  const submit = async (e) => {
    e.preventDefault()
    setBusy(true)
    try {
      await api.profile.remove()
      toast.success('Акаунт видалено')
      onDeleted()
    } catch (err) {
      toast.error(err.message)
      setBusy(false)
    }
  }

  return (
    <Modal title="Видалити акаунт?" onClose={onClose}>
      <form className="form" onSubmit={submit}>
        <p className="muted">
          Щоб підтвердити, введи свій username: <b>{username}</b>
        </p>
        <input value={value} onChange={(e) => setValue(e.target.value)} autoFocus />
        <div className="modal-foot">
          <button type="button" className="btn btn-ghost" onClick={onClose}>
            Скасувати
          </button>
          <button className="btn btn-danger" disabled={value !== username || busy}>
            Видалити назавжди
          </button>
        </div>
      </form>
    </Modal>
  )
}
