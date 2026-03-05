import React from 'react'

const TYPE_COLORS = {
  Person: 'var(--type-person)',
  Organization: 'var(--type-organization)',
  Concept: 'var(--type-concept)',
  Event: 'var(--type-event)',
  Location: 'var(--type-location)',
}

export default function FilterPanel({ metadata, filters, onChange, onClose }) {
  const toggleType = (type) => {
    const types = filters.types.includes(type)
      ? filters.types.filter(t => t !== type)
      : [...filters.types, type]
    onChange({ ...filters, types })
  }

  return (
    <div className="filter-panel" id="filter-panel" role="region" aria-labelledby="filter-panel-title">
      <h3 id="filter-panel-title">
        Filters
        <button className="icon-btn" onClick={onClose} aria-label="Close filters">
          <span aria-hidden="true">✕</span>
        </button>
      </h3>

      <div className="filter-section" role="group" aria-labelledby="entity-types-label">
        <div id="entity-types-label" className="filter-label" style={{display:'block',fontSize:'11px',fontWeight:500,color:'var(--text-muted)',textTransform:'uppercase',letterSpacing:'0.5px',marginBottom:'8px'}}>
          Entity Types
        </div>
        {(metadata.entity_types || ['Person','Organization','Concept','Event','Location']).map(type => (
          <label key={type} className="filter-checkbox">
            <input type="checkbox"
              checked={filters.types.length === 0 || filters.types.includes(type)}
              onChange={() => toggleType(type)} />
            <span className="type-dot" style={{background: TYPE_COLORS[type] || 'var(--text-muted)'}} aria-hidden="true" />
            {type}
          </label>
        ))}
      </div>

      <div className="filter-section">
        <label htmlFor="confidence-slider" style={{display:'block',fontSize:'11px',fontWeight:500,color:'var(--text-muted)',textTransform:'uppercase',letterSpacing:'0.5px',marginBottom:'8px'}}>
          Min Confidence: <span className="filter-value">{(filters.confidence * 100).toFixed(0)}%</span>
        </label>
        <input
          id="confidence-slider"
          type="range"
          className="filter-slider"
          min="0"
          max="1"
          step="0.05"
          value={filters.confidence}
          onChange={e => onChange({ ...filters, confidence: parseFloat(e.target.value) })}
          aria-valuemin="0"
          aria-valuemax="100"
          aria-valuenow={(filters.confidence * 100).toFixed(0)}
          aria-valuetext={`${(filters.confidence * 100).toFixed(0)} percent`}
        />
      </div>

      {filters.types.length > 0 && (
        <button onClick={() => onChange({ ...filters, types: [] })}
          style={{background:'transparent',border:'1px solid var(--border)',color:'var(--text-muted)',
                  borderRadius:'var(--radius)',padding:'6px 12px',fontSize:'12px',cursor:'pointer',width:'100%'}}>
          Clear All Filters
        </button>
      )}
    </div>
  )
}
