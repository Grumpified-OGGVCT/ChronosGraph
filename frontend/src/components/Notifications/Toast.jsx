import React from 'react'

export default function Toast({ id, level, message, onDismiss }) {
  const icons = { success: '✅', warning: '⚠️', error: '❌' }
  const role = level === 'error' ? 'alert' : 'status'

  return (
    <div className={`toast ${level}`} onClick={onDismiss} role={role} aria-live="polite">
      <span className="toast-icon" aria-hidden="true">{icons[level] || 'ℹ️'}</span>
      <span>{message}</span>
      <span className="sr-only">Click to dismiss</span>
    </div>
  )
}
