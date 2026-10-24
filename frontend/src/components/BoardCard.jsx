import { Link } from 'react-router-dom'
import { pluralUk } from '../utils'

export default function BoardCard({ board, isOwner, onToggleFavorite }) {
  const members = board.members?.length ?? 0

  return (
    <Link to={`/boards/${board.id}`} className="card board-card">
      <div className="board-card-top">
        <span className={`badge ${board.access ? 'badge-public' : 'badge-private'}`}>
          {board.access ? 'Публічна' : 'Приватна'}
        </span>
        {isOwner && <span className="badge badge-owner">Власник</span>}
        <button
          className={`star ${board.is_favorite ? 'on' : ''}`}
          title={board.is_favorite ? 'Прибрати з обраних' : 'Додати в обрані'}
          aria-pressed={board.is_favorite}
          onClick={(e) => {
            e.preventDefault()
            onToggleFavorite(board)
          }}
        >
          ★
        </button>
      </div>
      <h3 className="board-card-title">{board.board_name}</h3>
      <p className="board-card-desc">{board.description}</p>
      <div className="board-card-meta">
        <span>
          💡 {board.ideas_count} {pluralUk(board.ideas_count, ['ідея', 'ідеї', 'ідей'])}
        </span>
        <span>
          👥 {members} {pluralUk(members, ['учасник', 'учасники', 'учасників'])}
        </span>
      </div>
    </Link>
  )
}
