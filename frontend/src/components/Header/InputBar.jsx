import React, { useState, useCallback } from 'react'
import { ingestUrl } from '../../services/api'

export default function InputBar() {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = useCallback(async (e) => {
    e.preventDefault()
    if (!url.trim() || loading) return
    setLoading(true)
    try {
      await ingestUrl(url.trim())
      setUrl('')
    } catch (err) {
      console.error('Ingest failed:', err)
    } finally {
      setLoading(false)
    }
  }, [url, loading])

  return (
    <form className="input-bar" onSubmit={handleSubmit} aria-label="Ingest YouTube URL">
      <label htmlFor="url-input" className="sr-only">Paste YouTube URL or playlist</label>
      <input
        id="url-input"
        type="text"
        value={url}
        onChange={e => setUrl(e.target.value)}
        placeholder="Paste YouTube URL or playlist..."
        disabled={loading}
      />
      <button type="submit" disabled={loading || !url.trim()} aria-disabled={loading || !url.trim()}>
        {loading ? (
          <>
            <span aria-hidden="true">⏳</span>
            <span className="sr-only">Processing...</span>
          </>
        ) : 'Process'}
      </button>
    </form>
  )
}
