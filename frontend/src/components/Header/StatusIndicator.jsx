import React from 'react'

export default function StatusIndicator({ status, wsStatus, progress }) {
  const effectiveStatus = wsStatus === 'disconnected' ? 'disconnected' : status

  const labels = {
    idle: 'System Ready',
    active: 'Processing',
    queue: 'Queued',
    disconnected: 'Offline'
  }

  return (
    <div className="status-indicator">
      <span className={`status-dot ${effectiveStatus}`}></span>
      <span>{labels[effectiveStatus] || 'Ready'}</span>
      {progress && (
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${(progress.chunk / progress.total) * 100}%` }} />
        </div>
      )}
      {progress && (
        <span style={{fontSize:'11px',color:'var(--accent)'}}>
          {progress.chunk}/{progress.total}
        </span>
      )}
    </div>
  )
}
