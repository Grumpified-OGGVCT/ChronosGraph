import { useEffect, useRef, useState, useCallback } from 'react'

export default function useWebSocket(url = 'ws://localhost:8000/ws') {
  const ws = useRef(null)
  const [status, setStatus] = useState('disconnected')
  const [lastMessage, setLastMessage] = useState(null)
  const listeners = useRef(new Map())

  const connect = useCallback(() => {
    ws.current = new WebSocket(url)
    ws.current.onopen = () => setStatus('connected')
    ws.current.onclose = () => {
      setStatus('disconnected')
      setTimeout(connect, 3000) // auto-reconnect
    }
    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data)
      setLastMessage(data)
      const handler = listeners.current.get(data.type)
      if (handler) handler(data)
    }
  }, [url])

  useEffect(() => {
    connect()
    return () => ws.current?.close()
  }, [connect])

  const on = useCallback((type, handler) => {
    listeners.current.set(type, handler)
    return () => listeners.current.delete(type)
  }, [])

  return { status, lastMessage, on }
}
