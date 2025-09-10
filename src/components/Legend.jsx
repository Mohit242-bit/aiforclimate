import React from 'react'

function Legend() {
  const items = [
    { color: '#4ade80', label: 'Good (0-100)' },
    { color: '#facc15', label: 'Moderate (100-200)' },
    { color: '#fb923c', label: 'Unhealthy (200-300)' },
    { color: '#ef4444', label: 'Hazardous (300+)' }
  ]
  
  return (
    <div className="legend">
      <h3 style={{ fontSize: '14px', marginBottom: '12px', opacity: 0.7 }}>
        AQI Levels
      </h3>
      {items.map((item, i) => (
        <div key={i} className="legend-item">
          <div 
            className="legend-color" 
            style={{ background: item.color }}
          />
          <span style={{ fontSize: '12px' }}>{item.label}</span>
        </div>
      ))}
    </div>
  )
}

export default Legend
