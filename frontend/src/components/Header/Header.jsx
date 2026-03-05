import React, { useState } from 'react'
import InputBar from './InputBar'
import SearchBar from './SearchBar'
import StatusIndicator from './StatusIndicator'

export default function Header({ systemStatus, wsStatus, progress, onSearch, onToggleErrors, onToggleFilters }) {
  return (
    <header className="app-header">
      <div className="logo">
        <span className="logo-icon">◉</span>
        <h1>ChronosGraph</h1>
      </div>
      <InputBar />
      <SearchBar onResults={onSearch} />
      <StatusIndicator status={systemStatus} wsStatus={wsStatus} progress={progress} />
      <div className="header-controls">
        <button className="icon-btn" onClick={onToggleFilters} title="Filters">☰</button>
        <button className="icon-btn" onClick={onToggleErrors} title="Error Log">🔔</button>
      </div>
    </header>
  )
}
