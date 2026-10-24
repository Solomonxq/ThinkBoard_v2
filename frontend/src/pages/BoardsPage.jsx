import { useCallback, useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import BoardCard from '../components/BoardCard'
import { EmptyState, Field, Modal, Spinner } from '../components/ui'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'

const FILTERS = [
  { key: 'all', label: 'Усі' },
  { key: 'mine', label: 'Мої' },
  { key: 'shared', label: 'Спільні' },
  { key: 'fav', label: 'Обрані' },
]

export default function BoardsPage() {
  const { user } = useAuth()
  const toast = useToast()
  const [boards, setBoards] = useState(null)
  const [filter, setFilter] = useState('all')
  const [query, setQuery] = useState('')
  const [creating, setCreating] = useState(false)

  const load = useCallback(async () => {
    try {
      setBoards(await api.boards.list())
    } catch (err) {
      toast.error(err.message)
      setBoards([])
    }
  }, [toast])

  useEffect(() => {
    load()
  }, [load])

  const visible = useMemo(() => {
    if (!boards) return []
    const q = query.trim().toLowerCase()
    return boards.filter((b) => {
      if (filter === 'mine' && b.owner_id !== user.id) return false
      if (filter === 'shared' && b.owner_id === user.id) return false
      if (filter === 'fav' && !b.is_favorite) return false
      return !q || b.board_name.toLowerCase().includes(q) || b.description.toLowerCase().includes(q)
    })
  }, [boards, filter, query, user.id])

  const toggleFavorite = async (board) => {
    const next = !board.is_favorite
    setBoards((list) => list.map((b) => (b.id === board.id ? { ...b, is_favorite: next } : b)))
    try {
      await api.boards.favorite(board.id, next)
    } catch (err) {
      setBoards((list) => list.map((b) => (b.id === board.id ? { ...b, is_favorite: !next } : b)))
      toast.error(err.message)
    }
  }

  const stats = boards && {
    total: boards.length,
    mine: boards.filter((b) => b.owner_id === user.id).length,
    ideas: boards.reduce((sum, b) => sum + b.ideas_count, 0),
  }

  return (
    <div className="page">
      <div className="page-head">
        <div>
          <span className="eyebrow">Привіт, {user.username}</span>
          <h1>Твої дошки</h1>
        </div>
        <button className="btn btn-primary" onClick={() => setCreating(true)}>
          + Нова дошка
        </button>
      </div>

      {stats && (
        <div className="stats">
          <div className="stat">
            <span className="stat-value">{stats.total}</span>
            <span className="stat-label">дошок</span>
          </div>
          <div className="stat">
            <span className="stat-value">{stats.mine}</span>
            <span className="stat-label">створено тобою</span>
          </div>
          <div className="stat">
            <span className="stat-value">{stats.ideas}</span>
            <span className="stat-label">ідей загалом</span>
          </div>
        </div>
      )}

      <div className="toolbar">
        <div className="tabs" role="tablist">
          {FILTERS.map((f) => (
            <button
              key={f.key}
              role="tab"
              aria-selected={filter === f.key}
              className={filter === f.key ? 'active' : ''}
              onClick={() => setFilter(f.key)}
            >
              {f.label}
            </button>
          ))}
        </div>
        <input
          className="search"
          type="search"
          placeholder="Пошук дошки…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </div>

      {!boards ? (
        <Spinner />
      ) : visible.length === 0 ? (
        <EmptyState
          icon="◆"
          title={boards.length ? 'Нічого не знайдено' : 'Поки що жодної дошки'}
          text={boards.length ? 'Спробуй інший фільтр або запит' : 'Створи першу дошку та запроси команду'}
          action={
            !boards.length && (
              <button className="btn btn-primary" onClick={() => setCreating(true)}>
                Створити дошку
              </button>
            )
          }
        />
      ) : (
        <div className="grid">
          {visible.map((b) => (
            <BoardCard key={b.id} board={b} isOwner={b.owner_id === user.id} onToggleFavorite={toggleFavorite} />
          ))}
        </div>
      )}

      {creating && <CreateBoardModal onClose={() => setCreating(false)} />}
    </div>
  )
}

function CreateBoardModal({ onClose }) {
  const toast = useToast()
  const navigate = useNavigate()
  const [form, setForm] = useState({ board_name: '', description: '', access: false })
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  const submit = async (e) => {
    e.preventDefault()
    setBusy(true)
    setError('')
    try {
      const board = await api.boards.create(form)
      toast.success('Дошку створено')
      navigate(`/boards/${board.id}`)
    } catch (err) {
      setError(err.message)
      setBusy(false)
    }
  }

  return (
    <Modal title="Нова дошка" onClose={onClose}>
      <form onSubmit={submit} className="form">
        <Field label="Назва" hint={`${form.board_name.length}/25`}>
          <input
            autoFocus
            required
            minLength={3}
            maxLength={25}
            value={form.board_name}
            onChange={(e) => setForm({ ...form, board_name: e.target.value })}
          />
        </Field>
        <Field label="Опис" hint={`${form.description.length}/500`}>
          <textarea
            required
            maxLength={500}
            rows={4}
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
          />
        </Field>
        <label className="switch-row">
          <input
            type="checkbox"
            checked={form.access}
            onChange={(e) => setForm({ ...form, access: e.target.checked })}
          />
          <span className="switch" />
          <span>
            <b>Публічна дошка</b>
            <span className="muted small block">Її видно у твоєму публічному профілі</span>
          </span>
        </label>
        {error && <div className="alert">{error}</div>}
        <div className="modal-foot">
          <button type="button" className="btn btn-ghost" onClick={onClose}>
            Скасувати
          </button>
          <button className="btn btn-primary" disabled={busy}>
            {busy ? 'Створюю…' : 'Створити'}
          </button>
        </div>
      </form>
    </Modal>
  )
}
