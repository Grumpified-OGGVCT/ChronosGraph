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
    <div className="filter-panel">
      <h3>
        Filters
        <button className="icon-btn" onClick={onClose}>✕</button>
      </h3>

      <div className="filter-section">
        <label>Entity Types</label>
        {(metadata.entity_types || ['Person','Organization','Concept','Event','Location']).map(type => (
          <label key={type} className="filter-checkbox">
            <input type="checkbox"
              checked={filters.types.length === 0 || filters.types.includes(type)}
              onChange={() => toggleType(type)} />
            <span className="type-dot" style={{background: TYPE_COLORS[type] || 'var(--text-muted)'}} />
            {type}
          </label>
        ))}
      </div>

      <div className="filter-section">
        <label>Min Confidence: <span className="filter-value">{(filters.confidence * 100).toFixed(0)}%</span></label>
        <input type="range" className="filter-slider" min="0" max="1" step="0.05"
          value={filters.confidence}
          onChange={e => onChange({ ...filters, confidence: parseFloat(e.target.value) })} />
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
