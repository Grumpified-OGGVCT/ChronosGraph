import React, { useState, useCallback } from 'react'
import { searchEntities } from '../../services/api'

export default function SearchBar({ onResults }) {
  const [query, setQuery] = useState('')

  const handleSearch = useCallback(async (e) => {
    e.preventDefault()
    if (!query.trim()) { onResults(null); return }
    try {
      const { data } = await searchEntities(query.trim())
      onResults(data)
    } catch (err) {
      console.error('Search failed:', err)
      onResults(null)
    }
  }, [query, onResults])

  const handleClear = useCallback(() => {
    setQuery('')
    onResults(null)
  }, [onResults])

  return (
    <form className="search-bar" onSubmit={handleSearch} role="search" aria-label="Search entities">
      <label htmlFor="search-input" className="sr-only">Search query</label>
      <span className="search-icon" aria-hidden="true">🔍</span>
      <input
        id="search-input"
        type="search"
        value={query}
        onChange={e => setQuery(e.target.value)}
        placeholder="Search entities..."
      />
      {query && (
        <button
          type="button"
          onClick={handleClear}
          aria-label="Clear search"
          style={{
            background: 'transparent',
            border: 'none',
            color: 'var(--text-muted)',
            cursor: 'pointer'
          }}
        >
          <span aria-hidden="true">✕</span>
        </button>
      )}
    </form>
  )
}
