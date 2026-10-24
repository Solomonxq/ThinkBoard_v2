import { Navigate, Route, Routes, useLocation } from 'react-router-dom'
import Header from './components/Header'
import { EmptyState, Spinner } from './components/ui'
import { useAuth } from './context/AuthContext'
import AuthPage from './pages/AuthPage'
import BoardPage from './pages/BoardPage'
import BoardsPage from './pages/BoardsPage'
import ProfilePage from './pages/ProfilePage'
import PublicProfilePage from './pages/PublicProfilePage'

function RequireAuth({ children }) {
  const { user, loading } = useAuth()
  const location = useLocation()
  if (loading) return <Spinner />
  if (!user) return <Navigate to="/login" replace state={{ from: location.pathname }} />
  return children
}

function GuestOnly({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <Spinner />
  return user ? <Navigate to="/boards" replace /> : children
}

export default function App() {
  return (
    <>
      <div className="bg-glow" aria-hidden="true" />
      <Header />
      <main className="container">
        <Routes>
          <Route path="/" element={<Navigate to="/boards" replace />} />
          <Route path="/login" element={<GuestOnly><AuthPage mode="login" /></GuestOnly>} />
          <Route path="/register" element={<GuestOnly><AuthPage mode="register" /></GuestOnly>} />
          <Route path="/boards" element={<RequireAuth><BoardsPage /></RequireAuth>} />
          <Route path="/boards/:boardId" element={<RequireAuth><BoardPage /></RequireAuth>} />
          <Route path="/profile" element={<RequireAuth><ProfilePage /></RequireAuth>} />
          <Route path="/u/:username" element={<PublicProfilePage />} />
          <Route path="*" element={<EmptyState icon="404" title="Сторінку не знайдено" />} />
        </Routes>
      </main>
    </>
  )
}
