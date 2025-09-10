import React, { useEffect } from 'react'
import { useSimulationStore } from '../store/simulationStore'

function ControlPanel() {
  const { 
    currentIntervention, 
    applyIntervention, 
    getRecommendations, 
    recommendations,
    runScenario 
  } = useSimulationStore()

  useEffect(() => {
    getRecommendations()
  }, [])

  const handleApplyIntervention = async (intervention) => {
    applyIntervention(intervention)
    
    // Simulate the intervention
    const result = await runScenario({
      type: intervention.type,
      zones: intervention.zones,
      parameters: intervention.parameters || {}
    })
    
    console.log('Intervention applied:', result)
  }

  return (
    <div className="controls-panel">
      <h2 style={{ marginBottom: '20px', fontSize: '24px', fontWeight: '600' }}>
        AI Interventions
      </h2>
      
      <div style={{ marginBottom: '30px' }}>
        <h3 style={{ fontSize: '16px', opacity: 0.7, marginBottom: '15px' }}>
          Recommended Actions
        </h3>
        
        {recommendations.map(rec => (
          <div 
            key={rec.id} 
            className="intervention-card"
            onClick={() => handleApplyIntervention(rec)}
            style={{
              border: currentIntervention?.id === rec.id ? '2px solid #667eea' : undefined
            }}
          >
            <h4 style={{ fontSize: '16px', marginBottom: '8px' }}>{rec.name}</h4>
            <div style={{ display: 'flex', gap: '15px', fontSize: '14px', opacity: 0.8 }}>
              <span>AQI: {rec.impact.aqi > 0 ? '+' : ''}{rec.impact.aqi}</span>
              <span>Energy: {rec.impact.energy > 0 ? '+' : ''}{rec.impact.energy}%</span>
            </div>
          </div>
        ))}
      </div>
      
      <div style={{ marginBottom: '20px' }}>
        <h3 style={{ fontSize: '16px', opacity: 0.7, marginBottom: '15px' }}>
          Quick Actions
        </h3>
        
        <button 
          className="button-3d"
          onClick={() => handleApplyIntervention({
            id: 'emergency',
            type: 'emergency',
            name: 'Emergency Response',
            zones: [1, 2, 3, 4, 5]
          })}
        >
          🚨 Emergency AQI Response
        </button>
        
        <button 
          className="button-3d"
          style={{ background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)' }}
          onClick={() => handleApplyIntervention({
            id: 'green',
            type: 'green_cover',
            name: 'Add Green Spaces',
            zones: [3, 5]
          })}
        >
          🌳 Add Green Corridors
        </button>
        
        <button 
          className="button-3d"
          style={{ background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)' }}
          onClick={() => handleApplyIntervention({
            id: 'traffic',
            type: 'traffic_ban',
            name: 'Traffic Control',
            zones: [1, 2]
          })}
        >
          🚗 Restrict Traffic Flow
        </button>
      </div>
      
      <div style={{ 
        borderTop: '1px solid rgba(255,255,255,0.1)', 
        paddingTop: '20px',
        marginTop: '20px' 
      }}>
        <h3 style={{ fontSize: '14px', opacity: 0.5, marginBottom: '10px' }}>
          Simulation Settings
        </h3>
        
        <div style={{ marginBottom: '15px' }}>
          <label style={{ fontSize: '14px', display: 'block', marginBottom: '5px' }}>
            Weather Scenario
          </label>
          <select style={{
            width: '100%',
            padding: '8px',
            background: 'rgba(255,255,255,0.1)',
            border: '1px solid rgba(255,255,255,0.2)',
            borderRadius: '5px',
            color: 'white'
          }}>
            <option>Normal</option>
            <option>Heatwave</option>
            <option>Monsoon</option>
            <option>Winter Smog</option>
          </select>
        </div>
        
        <div>
          <label style={{ fontSize: '14px', display: 'block', marginBottom: '5px' }}>
            Farm Fire Intensity
          </label>
          <input 
            type="range" 
            min="0" 
            max="100" 
            defaultValue="30"
            style={{ width: '100%' }}
          />
        </div>
      </div>
    </div>
  )
}

export default ControlPanel
