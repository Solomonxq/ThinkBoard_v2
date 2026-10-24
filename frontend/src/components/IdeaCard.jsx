import { Link } from 'react-router-dom'
import { useToast } from '../context/ToastContext'
import { useVoting } from '../hooks/useVoting'
import { formatCountdown, formatDate } from '../utils'

export default function IdeaCard({ idea, boardId, canVote, canDelete, onDelete, onFinished }) {
  const toast = useToast()
  const v = useVoting(boardId, idea, { onFinished })
  const total = v.approve + v.reject
  const approvePct = total ? Math.round((v.approve / total) * 100) : 50

  const ended = v.finished || v.secondsLeft <= 0

  let status
  if (v.decided && v.accepted) status = { cls: 'accepted', text: 'Прийнято' }
  else if (v.decided) status = { cls: 'rejected', text: 'Відхилено' }
  else if (ended) status = { cls: 'pending', text: 'Підрахунок…' }
  else status = { cls: 'live', text: formatCountdown(v.secondsLeft) }

  const handleVote = (value) => {
    if (!v.vote(value)) toast.error("Немає з'єднання з голосуванням")
  }

  return (
    <article className={`card idea-card ${status.cls}`}>
      <header className="idea-head">
        <div>
          <h4>{idea.title}</h4>
          <div className="idea-meta">
            {idea.author && <Link to={`/u/${idea.author}`}>@{idea.author}</Link>}
            <span>· {formatDate(idea.created_at)}</span>
          </div>
        </div>
        <span className={`idea-status status-${status.cls}`}>
          {status.cls === 'live' && <span className="pulse" />}
          {status.text}
        </span>
      </header>

      {idea.description && <p className="idea-desc">{idea.description}</p>}

      <div className="vote-bar" aria-label={`За: ${v.approve}, проти: ${v.reject}`}>
        <div className="vote-bar-approve" style={{ width: `${approvePct}%` }} />
      </div>
      <div className="vote-counts">
        <span className="approve-text">👍 {v.approve}</span>
        <span className="muted">{total} голос(ів)</span>
        <span className="reject-text">{v.reject} 👎</span>
      </div>

      <footer className="idea-actions">
        {!ended && canVote && (
          <>
            <button
              className={`btn btn-approve ${v.myVote === true ? 'chosen' : ''}`}
              onClick={() => handleVote(true)}
              disabled={!v.connected}
            >
              За
            </button>
            <button
              className={`btn btn-reject ${v.myVote === false ? 'chosen' : ''}`}
              onClick={() => handleVote(false)}
              disabled={!v.connected}
            >
              Проти
            </button>
          </>
        )}
        {!ended && !canVote && <span className="muted small">Голосувати можуть лише учасники дошки</span>}
        {canDelete && (
          <button className="btn btn-ghost btn-sm push-right" onClick={() => onDelete(idea)}>
            Видалити
          </button>
        )}
      </footer>
    </article>
  )
}
