import React from 'react'
import { useSimulationStore } from '../store/simulationStore'

function InfoPanel() {
  const { zones } = useSimulationStore()
  
  // Calculate averages
  const avgAQI = zones.reduce((sum, z) => sum + z.aqi, 0) / zones.length
  const totalEnergy = zones.reduce((sum, z) => sum + z.energy, 0)
  const avgHeat = zones.reduce((sum, z) => sum + z.heat, 0) / zones.length
  
  const getAQIColor = (aqi) => {
    if (aqi < 100) return '#4ade80'
    if (aqi < 200) return '#facc15'
    if (aqi < 300) return '#fb923c'
    return '#ef4444'
  }
  
  const getAQIStatus = (aqi) => {
    if (aqi < 100) return 'Good'
    if (aqi < 200) return 'Moderate'
    if (aqi < 300) return 'Unhealthy'
    return 'Hazardous'
  }
  
  return (
    <div className="info-panel">
      <h1 style={{ fontSize: '20px', marginBottom: '20px' }}>
        Delhi Digital Twin
      </h1>
      
      <div className="aqi-indicator">
        <div>
          <div className="aqi-value" style={{ color: getAQIColor(avgAQI) }}>
            {Math.round(avgAQI)}
          </div>
          <div className="aqi-label">Average AQI</div>
        </div>
        <div style={{ 
          padding: '5px 15px', 
          background: getAQIColor(avgAQI),
          borderRadius: '20px',
          color: '#000',
          fontWeight: '600'
        }}>
          {getAQIStatus(avgAQI)}
        </div>
      </div>
      
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{totalEnergy}</div>
          <div className="stat-label">Energy (MWh)</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{(avgHeat * 100).toFixed(0)}%</div>
          <div className="stat-label">Heat Island</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">38°C</div>
          <div className="stat-label">Temperature</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">42%</div>
          <div className="stat-label">Humidity</div>
        </div>
      </div>
      
      <div style={{ 
        marginTop: '20px', 
        paddingTop: '20px', 
        borderTop: '1px solid rgba(255,255,255,0.1)' 
      }}>
        <h3 style={{ fontSize: '14px', opacity: 0.7, marginBottom: '10px' }}>
          Live Updates
        </h3>
        <div style={{ fontSize: '12px', opacity: 0.6, lineHeight: '1.6' }}>
          <div>🔴 Zone 3: High pollution detected</div>
          <div>🟡 Zone 1: Traffic congestion</div>
          <div>🟢 Zone 5: Green intervention active</div>
        </div>
      </div>
    </div>
  )
}

export default InfoPanel
