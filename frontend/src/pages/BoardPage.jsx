import { useCallback, useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { api } from '../api/client'
import IdeaCard from '../components/IdeaCard'
import { Avatar, EmptyState, Field, Modal, Spinner } from '../components/ui'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'

const DURATIONS = [
  { label: '5 хв', minutes: 5 },
  { label: '15 хв', minutes: 15 },
  { label: '1 год', minutes: 60 },
  { label: '6 год', minutes: 360 },
  // бекенд дозволяє максимум 1 добу, лишаємо хвилину запасу
  { label: '24 год', minutes: 24 * 60 - 1 },
]

export default function BoardPage() {
  const { boardId } = useParams()
  const { user } = useAuth()
  const toast = useToast()
  const navigate = useNavigate()
  const [board, setBoard] = useState(null)
  const [error, setError] = useState('')
  const [tab, setTab] = useState('live')
  const [modal, setModal] = useState(null)

  const load = useCallback(async () => {
    try {
      setBoard(await api.boards.get(boardId))
    } catch (err) {
      setError(err.message)
    }
  }, [boardId])

  useEffect(() => {
    setBoard(null)
    setError('')
    load()
  }, [load])

  // Після завершення голосування бекенд видаляє відхилені ідеї — перезавантажуємо дошку
  const handleFinished = useCallback(
    (result) => {
      toast.info(result.accepted ? 'Ідею прийнято 🎉' : 'Ідею відхилено')
      setTimeout(load, 1500)
    },
    [load, toast]
  )

  if (error) {
    return (
      <EmptyState
        icon="⚠"
        title="Не вдалося відкрити дошку"
        text={error}
        action={
          <Link className="btn btn-primary" to="/boards">
            До списку дошок
          </Link>
        }
      />
    )
  }
  if (!board) return <Spinner />

  const isOwner = board.owner_id === user.id
  const isMember = board.members.some((m) => m.id === user.id)
  const live = board.ideas.filter((i) => !i.accepted)
  const accepted = board.ideas.filter((i) => i.accepted)
  const shown = tab === 'live' ? live : accepted

  const toggleFavorite = async () => {
    const next = !board.is_favorite
    setBoard({ ...board, is_favorite: next })
    try {
      await api.boards.favorite(board.id, next)
    } catch (err) {
      setBoard((b) => ({ ...b, is_favorite: !next }))
      toast.error(err.message)
    }
  }

  const deleteIdea = async (idea) => {
    if (!window.confirm(`Видалити ідею «${idea.title}»?`)) return
    try {
      await api.ideas.remove(board.id, idea.id)
      setBoard((b) => ({ ...b, ideas: b.ideas.filter((i) => i.id !== idea.id) }))
      toast.success('Ідею видалено')
    } catch (err) {
      toast.error(err.message)
    }
  }

  const removeMember = async (member) => {
    if (!window.confirm(`Видалити ${member.username} з дошки?`)) return
    try {
      await api.boards.removeMember(board.id, member.id)
      setBoard((b) => ({ ...b, members: b.members.filter((m) => m.id !== member.id) }))
      toast.success('Учасника видалено')
    } catch (err) {
      toast.error(err.message)
    }
  }

  const deleteBoard = async () => {
    if (!window.confirm(`Видалити дошку «${board.board_name}» назавжди?`)) return
    try {
      await api.boards.remove(board.id)
      toast.success('Дошку видалено')
      navigate('/boards')
    } catch (err) {
      toast.error(err.message)
    }
  }

  return (
    <div className="page">
      <Link to="/boards" className="back-link">
        ← Усі дошки
      </Link>

      <div className="board-hero card">
        <div className="board-hero-main">
          <div className="badges">
            <span className={`badge ${board.access ? 'badge-public' : 'badge-private'}`}>
              {board.access ? 'Публічна' : 'Приватна'}
            </span>
            {isOwner && <span className="badge badge-owner">Ти власник</span>}
          </div>
          <h1>{board.board_name}</h1>
          <p className="muted">{board.description}</p>
        </div>
        <div className="board-hero-actions">
          <button className={`btn btn-ghost star-btn ${board.is_favorite ? 'on' : ''}`} onClick={toggleFavorite}>
            ★ {board.is_favorite ? 'В обраних' : 'В обрані'}
          </button>
          {isMember && (
            <button className="btn btn-primary" onClick={() => setModal('idea')}>
              + Ідея
            </button>
          )}
        </div>
      </div>

      <div className="board-layout">
        <section>
          <div className="tabs" role="tablist">
            <button role="tab" aria-selected={tab === 'live'} className={tab === 'live' ? 'active' : ''} onClick={() => setTab('live')}>
              Голосування <span className="count">{live.length}</span>
            </button>
            <button
              role="tab"
              aria-selected={tab === 'accepted'}
              className={tab === 'accepted' ? 'active' : ''}
              onClick={() => setTab('accepted')}
            >
              Прийняті <span className="count">{accepted.length}</span>
            </button>
          </div>

          {shown.length === 0 ? (
            <EmptyState
              icon={tab === 'live' ? '💡' : '🏆'}
              title={tab === 'live' ? 'Немає активних ідей' : 'Ще жодної прийнятої ідеї'}
              text={tab === 'live' ? 'Запропонуй щось — і команда проголосує' : 'Тут з’являться ідеї, які набрали більшість'}
            />
          ) : (
            <div className="ideas">
              {shown.map((idea) => (
                <IdeaCard
                  key={idea.id}
                  idea={idea}
                  boardId={board.id}
                  canVote={isMember}
                  canDelete={idea.user_id === user.id}
                  onDelete={deleteIdea}
                  onFinished={handleFinished}
                />
              ))}
            </div>
          )}
        </section>

        <aside className="card members">
          <div className="members-head">
            <h3>Учасники · {board.members.length}</h3>
            {isOwner && (
              <button className="btn btn-ghost btn-sm" onClick={() => setModal('member')}>
                + Додати
              </button>
            )}
          </div>
          <ul>
            {board.members.map((m) => (
              <li key={m.id}>
                <Link to={`/u/${m.username}`} className="member">
                  <Avatar user={m} size={32} />
                  <span>
                    <b>{m.username}</b>
                    {m.id === board.owner_id && <span className="muted small block">власник</span>}
                  </span>
                </Link>
                {isOwner && m.id !== user.id && (
                  <button className="icon-btn" title="Видалити з дошки" onClick={() => removeMember(m)}>
                    ✕
                  </button>
                )}
              </li>
            ))}
          </ul>
          {isOwner && (
            <button className="btn btn-danger-ghost btn-block" onClick={deleteBoard}>
              Видалити дошку
            </button>
          )}
        </aside>
      </div>

      {modal === 'idea' && (
        <CreateIdeaModal
          boardId={board.id}
          onClose={() => setModal(null)}
          onCreated={(idea) => {
            setBoard((b) => ({ ...b, ideas: [{ ...idea, author: user.username, approve: 0, reject: 0 }, ...b.ideas] }))
            setTab('live')
          }}
        />
      )}
      {modal === 'member' && (
        <AddMemberModal
          boardId={board.id}
          onClose={() => setModal(null)}
          onAdded={(member) => setBoard((b) => ({ ...b, members: [...b.members, member] }))}
        />
      )}
    </div>
  )
}

function CreateIdeaModal({ boardId, onClose, onCreated }) {
  const toast = useToast()
  const [form, setForm] = useState({ title: '', description: '', minutes: 60 })
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  const submit = async (e) => {
    e.preventDefault()
    setBusy(true)
    setError('')
    try {
      const idea = await api.ideas.create(boardId, {
        title: form.title,
        description: form.description,
        voting_ends_at: new Date(Date.now() + form.minutes * 60_000).toISOString(),
      })
      toast.success('Ідею додано, голосування почалось')
      onCreated(idea)
      onClose()
    } catch (err) {
      setError(err.message)
      setBusy(false)
    }
  }

  return (
    <Modal title="Нова ідея" onClose={onClose}>
      <form onSubmit={submit} className="form">
        <Field label="Заголовок">
          <input
            autoFocus
            required
            minLength={3}
            maxLength={100}
            value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
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
        <div className="field">
          <span className="field-label">Тривалість голосування</span>
          <div className="chips">
            {DURATIONS.map((d) => (
              <button
                type="button"
                key={d.minutes}
                className={`chip ${form.minutes === d.minutes ? 'active' : ''}`}
                onClick={() => setForm({ ...form, minutes: d.minutes })}
              >
                {d.label}
              </button>
            ))}
          </div>
        </div>
        {error && <div className="alert">{error}</div>}
        <div className="modal-foot">
          <button type="button" className="btn btn-ghost" onClick={onClose}>
            Скасувати
          </button>
          <button className="btn btn-primary" disabled={busy}>
            {busy ? 'Додаю…' : 'Запустити голосування'}
          </button>
        </div>
      </form>
    </Modal>
  )
}

function AddMemberModal({ boardId, onClose, onAdded }) {
  const toast = useToast()
  const [username, setUsername] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  const submit = async (e) => {
    e.preventDefault()
    setBusy(true)
    setError('')
    try {
      const profile = await api.profile.get(username.trim())
      await api.boards.addMember(boardId, profile.id)
      onAdded({ id: profile.id, username: profile.username, avatar_url: profile.avatar_url })
      toast.success(`${profile.username} тепер на дошці`)
      onClose()
    } catch (err) {
      setError(err.status === 404 ? 'Користувача не знайдено' : err.message)
      setBusy(false)
    }
  }

  return (
    <Modal title="Додати учасника" onClose={onClose}>
      <form onSubmit={submit} className="form">
        <Field label="Ім'я користувача" hint="Точний username людини, яку запрошуєш">
          <input autoFocus required value={username} onChange={(e) => setUsername(e.target.value)} placeholder="username" />
        </Field>
        {error && <div className="alert">{error}</div>}
        <div className="modal-foot">
          <button type="button" className="btn btn-ghost" onClick={onClose}>
            Скасувати
          </button>
          <button className="btn btn-primary" disabled={busy}>
            {busy ? 'Додаю…' : 'Додати'}
          </button>
        </div>
      </form>
    </Modal>
  )
}
