import React from 'react'

export default function Toast({ id, level, message, onDismiss }) {
  const icons = { success: '✅', warning: '⚠️', error: '❌' }
  return (
    <div className={`toast ${level}`} onClick={onDismiss}>
      <span className="toast-icon">{icons[level] || 'ℹ️'}</span>
      <span>{message}</span>
    </div>
  )
}
