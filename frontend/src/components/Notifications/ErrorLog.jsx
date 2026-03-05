import React, { useState, useEffect, useCallback } from 'react'
import { getErrors, retryError } from '../../services/api'

export default function ErrorLog({ onClose }) {
  const [errors, setErrors] = useState([])
  const [retrying, setRetrying] = useState(null)

  useEffect(() => {
    getErrors().then(r => setErrors(r.data)).catch(() => {})
  }, [])

  const handleRetry = useCallback(async (id) => {
    setRetrying(id)
    try {
      await retryError(id)
      setErrors(prev => prev.filter(e => e.id !== id))
    } catch (err) {
      console.error('Retry failed:', err)
    } finally {
      setRetrying(null)
    }
  }, [])

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  return (
    <div className="modal-overlay" onClick={onClose} aria-hidden="true">
      <div className="modal" onClick={e => e.stopPropagation()} role="dialog" aria-modal="true" aria-labelledby="error-log-title" id="error-log-modal">
        <div className="modal-header">
          <h3 id="error-log-title"><span aria-hidden="true">🔔</span> Error Log</h3>
          <button className="icon-btn" onClick={onClose} aria-label="Close error log">
            <span aria-hidden="true">✕</span>
          </button>
        </div>
        <div className="modal-body">
          {errors.length === 0 ? (
            <p style={{color:'var(--text-muted)',textAlign:'center',padding:'20px'}}>No errors recorded</p>
          ) : errors.map(err => (
            <div key={err.id} className="error-row" role="alert">
              <span style={{color:'var(--error)'}} aria-hidden="true">⚠</span>
              <span className="error-msg">{err.message}</span>
              {err.retryable && (
                <button className="retry-btn" disabled={retrying === err.id} aria-disabled={retrying === err.id}
                  onClick={() => handleRetry(err.id)}>
                  {retrying === err.id ? 'Retrying...' : 'Retry'}
                </button>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
