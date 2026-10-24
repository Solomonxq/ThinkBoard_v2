import { useCallback, useEffect, useRef, useState } from 'react'
import { voteSocketUrl } from '../api/client'

const secondsUntil = (iso) => (iso ? Math.max(0, Math.round((new Date(iso) - Date.now()) / 1000)) : 0)

/**
 * Живе голосування за ідею через WebSocket бекенду.
 * Менеджер на бекенді розсилає події всім сокетам дошки,
 * тому фільтруємо повідомлення за idea_id.
 */
export function useVoting(boardId, idea, { onFinished } = {}) {
  const isOpen = !idea.accepted && secondsUntil(idea.voting_ends_at) > 0

  const [state, setState] = useState({
    approve: idea.approve ?? 0,
    reject: idea.reject ?? 0,
    secondsLeft: secondsUntil(idea.voting_ends_at),
    finished: !isOpen,
    accepted: idea.accepted,
    decided: idea.accepted,
    connected: false,
  })
  const [myVote, setMyVote] = useState(null)
  const wsRef = useRef(null)
  const onFinishedRef = useRef(onFinished)
  onFinishedRef.current = onFinished

  useEffect(() => {
    if (!isOpen) return undefined

    const ws = new WebSocket(voteSocketUrl(boardId, idea.id))
    wsRef.current = ws

    ws.onopen = () => setState((s) => ({ ...s, connected: true }))
    ws.onclose = () => setState((s) => ({ ...s, connected: false }))
    ws.onmessage = (e) => {
      let data
      try {
        data = JSON.parse(e.data)
      } catch {
        return
      }
      if (data.idea_id && data.idea_id !== idea.id) return

      switch (data.event) {
        case 'init':
          setState((s) => ({
            ...s,
            approve: data.approve,
            reject: data.reject,
            secondsLeft: data.seconds_left ?? s.secondsLeft,
          }))
          break
        case 'vote_updated':
          setState((s) => ({ ...s, approve: data.approve, reject: data.reject }))
          break
        case 'voting_finished':
          setState((s) => ({
            ...s,
            approve: data.approve,
            reject: data.reject,
            finished: true,
            decided: true,
            accepted: data.accepted,
            secondsLeft: 0,
          }))
          onFinishedRef.current?.(data)
          break
        case 'voting_already_finished':
          setState((s) => ({ ...s, finished: true, decided: true, accepted: data.accepted, secondsLeft: 0 }))
          break
        default:
          break
      }
    }

    return () => {
      ws.onclose = null
      ws.close()
      wsRef.current = null
    }
  }, [boardId, idea.id, isOpen])

  // Локальний таймер, сервер надсилає лише стартове значення
  useEffect(() => {
    if (state.finished) return undefined
    const timer = setInterval(() => {
      setState((s) => ({ ...s, secondsLeft: secondsUntil(idea.voting_ends_at) }))
    }, 1000)
    return () => clearInterval(timer)
  }, [state.finished, idea.voting_ends_at])

  const vote = useCallback((status) => {
    const ws = wsRef.current
    if (!ws || ws.readyState !== WebSocket.OPEN) return false
    ws.send(JSON.stringify({ status }))
    setMyVote(status)
    return true
  }, [])

  return { ...state, myVote, vote }
}
