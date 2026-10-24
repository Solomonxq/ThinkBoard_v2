import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../api/client'
import { Avatar, EmptyState, Spinner } from '../components/ui'

export default function PublicProfilePage() {
  const { username } = useParams()
  const [profile, setProfile] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    setProfile(null)
    setError('')
    api.profile
      .get(username)
      .then(setProfile)
      .catch((err) => setError(err.status === 404 ? 'Такого користувача не існує' : err.message))
  }, [username])

  if (error) return <EmptyState icon="?" title="Профіль не знайдено" text={error} />
  if (!profile) return <Spinner />

  const memberOnly = profile.member_of.filter((b) => !profile.boards.some((o) => o.id === b.id))

  return (
    <div className="page narrow">
      <section className="card public-hero">
        <Avatar user={profile} size={112} />
        <div>
          <h1>{profile.username}</h1>
          <p className="muted">{profile.bio || 'Користувач ще нічого не розповів про себе.'}</p>
        </div>
      </section>

      <BoardList title="Публічні дошки" boards={profile.boards} />
      <BoardList title="Бере участь" boards={memberOnly} />
    </div>
  )
}

function BoardList({ title, boards }) {
  return (
    <section className="card">
      <h3>
        {title} <span className="count">{boards.length}</span>
      </h3>
      {boards.length === 0 ? (
        <p className="muted">Поки порожньо</p>
      ) : (
        <ul className="link-list">
          {boards.map((b) => (
            <li key={b.id}>
              <Link to={`/boards/${b.id}`}>
                <span className="brand-mark">◆</span> {b.board_name}
              </Link>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
