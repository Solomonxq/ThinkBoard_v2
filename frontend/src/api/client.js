const BASE = '/api'
const STORAGE_KEY = 'tb-tokens'

let tokens = readTokens()
let refreshPromise = null
let onUnauthorized = () => {}

function readTokens() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) || null
  } catch {
    return null
  }
}

export function getTokens() {
  return tokens
}

export function setTokens(next) {
  tokens = next ? { access_token: next.access_token, refresh_token: next.refresh_token } : null
  try {
    if (tokens) localStorage.setItem(STORAGE_KEY, JSON.stringify(tokens))
    else localStorage.removeItem(STORAGE_KEY)
  } catch {
    /* сховище недоступне — токени лишаться в пам'яті */
  }
}

export function setUnauthorizedHandler(fn) {
  onUnauthorized = fn
}

export class ApiError extends Error {
  constructor(message, status) {
    super(message)
    this.status = status
  }
}

function formatDetail(body, status) {
  const detail = body?.detail ?? body?.error
  if (Array.isArray(detail)) {
    return detail.map((d) => `${(d.loc || []).slice(1).join('.')}: ${d.msg}`).join('; ')
  }
  if (typeof detail === 'string') return detail
  if (status === 429) return 'Забагато запитів, спробуй трохи пізніше'
  return `Помилка ${status}`
}

async function refreshTokens() {
  if (!tokens?.refresh_token) return false
  if (!refreshPromise) {
    refreshPromise = fetch(`${BASE}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: tokens.refresh_token }),
    })
      .then(async (res) => {
        if (!res.ok) return false
        setTokens(await res.json())
        return true
      })
      .catch(() => false)
      .finally(() => {
        refreshPromise = null
      })
  }
  return refreshPromise
}

async function request(path, { method = 'GET', body, form, auth = true, retry = true } = {}) {
  const headers = {}
  if (body !== undefined) headers['Content-Type'] = 'application/json'
  if (auth && tokens?.access_token) headers.Authorization = `Bearer ${tokens.access_token}`

  const res = await fetch(BASE + path, {
    method,
    headers,
    body: form ?? (body !== undefined ? JSON.stringify(body) : undefined),
  })

  if (res.status === 401 && auth && retry) {
    if (await refreshTokens()) return request(path, { method, body, form, auth, retry: false })
    setTokens(null)
    onUnauthorized()
  }

  if (!res.ok) {
    let data = null
    try {
      data = await res.json()
    } catch {
      /* тіло не JSON */
    }
    throw new ApiError(formatDetail(data, res.status), res.status)
  }

  if (res.status === 204) return null
  const text = await res.text()
  return text ? JSON.parse(text) : null
}

export const api = {
  auth: {
    login: (email, password) =>
      request('/auth/login', { method: 'POST', body: { email, password }, auth: false }),
    register: (data) => request('/auth/register', { method: 'POST', body: data, auth: false }),
    me: () => request('/auth/me'),
  },
  boards: {
    list: () => request('/boards/'),
    get: (id) => request(`/boards/${id}`),
    create: (data) => request('/boards/create', { method: 'POST', body: data }),
    remove: (id) => request(`/boards/${id}`, { method: 'DELETE' }),
    favorite: (id, on) => request(`/boards/${id}/favorite`, { method: on ? 'POST' : 'DELETE' }),
    addMember: (id, userId) =>
      request(`/boards/${id}/members`, { method: 'POST', body: { user_id: userId } }),
    removeMember: (id, userId) => request(`/boards/${id}/members/${userId}`, { method: 'DELETE' }),
  },
  ideas: {
    create: (boardId, data) =>
      request(`/boards/${boardId}/ideas/create`, { method: 'POST', body: data }),
    remove: (boardId, ideaId) =>
      request(`/boards/${boardId}/ideas/delete/${ideaId}`, { method: 'DELETE' }),
  },
  profile: {
    me: () => request('/profile/me'),
    update: (data) => request('/profile/me', { method: 'PATCH', body: data }),
    uploadAvatar: (file) => {
      const form = new FormData()
      form.append('file', file)
      return request('/profile/me/avatar', { method: 'POST', form })
    },
    remove: () => request('/profile/me', { method: 'DELETE' }),
    get: (username) => request(`/profile/${encodeURIComponent(username)}`),
  },
}

export function voteSocketUrl(boardId, ideaId) {
  const proto = window.location.protocol === 'https:' ? 'wss' : 'ws'
  const token = encodeURIComponent(tokens?.access_token || '')
  return `${proto}://${window.location.host}${BASE}/boards/${boardId}/ideas/${ideaId}/vote/ws?token=${token}`
}
