import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import { api, getTokens, setTokens, setUnauthorizedHandler } from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(Boolean(getTokens()))

  const loadUser = useCallback(async () => {
    if (!getTokens()) {
      setUser(null)
      setLoading(false)
      return null
    }
    try {
      const me = await api.profile.me()
      setUser(me)
      return me
    } catch {
      setUser(null)
      return null
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    setUnauthorizedHandler(() => setUser(null))
    loadUser()
  }, [loadUser])

  const login = async (email, password) => {
    setTokens(await api.auth.login(email, password))
    return loadUser()
  }

  const register = async (data) => {
    setTokens(await api.auth.register(data))
    return loadUser()
  }

  const logout = () => {
    setTokens(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, setUser, loading, login, register, logout, reload: loadUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
