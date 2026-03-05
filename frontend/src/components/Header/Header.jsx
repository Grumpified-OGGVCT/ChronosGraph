import React, { useState } from 'react'
import InputBar from './InputBar'
import SearchBar from './SearchBar'
import StatusIndicator from './StatusIndicator'

export default function Header({ systemStatus, wsStatus, progress, onSearch, onToggleErrors, onToggleFilters, showFilters, showErrorLog }) {
  return (
    <header className="app-header">
      <div className="logo">
        <span className="logo-icon" aria-hidden="true">◉</span>
        <h1>ChronosGraph</h1>
      </div>
      <InputBar />
      <SearchBar onResults={onSearch} />
      <StatusIndicator status={systemStatus} wsStatus={wsStatus} progress={progress} />
      <div className="header-controls">
        <button
          className="icon-btn"
          onClick={onToggleFilters}
          title="Filters"
          aria-label="Toggle Filters"
          aria-expanded={showFilters}
          aria-controls="filter-panel"
        >
          <span aria-hidden="true">☰</span>
        </button>
        <button
          className="icon-btn"
          onClick={onToggleErrors}
          title="Error Log"
          aria-label="Toggle Error Log"
          aria-expanded={showErrorLog}
          aria-controls="error-log-modal"
        >
          <span aria-hidden="true">🔔</span>
        </button>
      </div>
    </header>
  )
}
