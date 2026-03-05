import React from 'react'
import './App.css'

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <div className="logo">
          <span className="logo-icon">◉</span>
          <h1>ChronosGraph</h1>
        </div>
        <div className="status-indicator idle">
          <span className="status-dot"></span>
          System Ready
        </div>
      </header>
      <main className="app-main">
        <div className="placeholder-scene">
          <p>3D Knowledge Graph will render here</p>
          <p className="sub">Phase A: Skeleton ✔️ — Frontend scaffold loaded</p>
        </div>
      </main>
    </div>
  )
}

export default App
