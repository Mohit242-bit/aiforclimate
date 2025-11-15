import React, { useEffect, useState } from 'react'
import { useSimulationStore } from '../store/simulationStore'

function PolicyControlPanel() {
  const { 
    currentIntervention, 
    applyIntervention, 
    getRecommendations, 
    recommendations,
    runScenario,
    zones,
    startEmergencyProtocol,
    emergencyActive,
    emergencyStatus
  } = useSimulationStore()
  
  const [situation, setSituation] = useState(null)
  const [selectedRec, setSelectedRec] = useState(null)
  const [showDetails, setShowDetails] = useState(false)

  useEffect(() => {
    fetchRecommendations()
  }, [])

  const fetchRecommendations = async () => {
    const data = await getRecommendations()
    if (data?.situation) {
      setSituation(data.situation)
    }
  }

  const handleApplyIntervention = async (rec) => {
    setSelectedRec(rec)
    applyIntervention({
      id: rec.id,
      type: rec.type,
      name: rec.name,
      zones: rec.zones
    })
    
    // Simulate the intervention
    const result = await runScenario({
      type: rec.type,
      zones: rec.zones,
      parameters: rec.details || {}
    })
    
    console.log('Policy applied:', rec.name, result)
  }
  
  // Calculate total current AQI
  const avgAQI = zones.reduce((sum, z) => sum + z.aqi, 0) / zones.length

  return (
    <div className="controls-panel" style={{ 
      maxWidth: '400px',
      maxHeight: '85vh',
      overflowY: 'auto',
      overflowX: 'hidden'
    }}>
      {/* Header with Crisis Status */}
      <div style={{ 
        background: situation?.severity === 'CRITICAL' ? 
          'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)' : 
          situation?.severity === 'WARNING' ?
          'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)' :
          'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        margin: '-20px -20px 20px -20px',
        padding: '20px',
        borderRadius: '15px 15px 0 0'
      }}>
        <h2 style={{ marginBottom: '10px', fontSize: '24px', fontWeight: '600' }}>
          🚨 AI Policy Engine
        </h2>
        <div style={{ fontSize: '14px', opacity: 0.9 }}>
          Status: <strong>{situation?.severity || 'ANALYZING'}</strong>
        </div>
        <div style={{ fontSize: '12px', opacity: 0.8, marginTop: '5px' }}>
          Primary Source: {situation?.primary_source?.replace('_', ' ').toUpperCase() || 'DETECTING'}
        </div>
      </div>
      
      {/* Current Situation Analysis */}
      <div style={{ 
        background: 'rgba(255,255,255,0.05)', 
        padding: '15px', 
        borderRadius: '10px',
        marginBottom: '20px' 
      }}>
        <h3 style={{ fontSize: '16px', marginBottom: '15px', color: '#f59e0b' }}>
          📊 Current Situation
        </h3>
        
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
          <div style={{ 
            background: 'rgba(239,68,68,0.1)', 
            padding: '10px', 
            borderRadius: '8px',
            border: '1px solid rgba(239,68,68,0.3)'
          }}>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#ef4444' }}>
              {Math.round(avgAQI)}
            </div>
            <div style={{ fontSize: '11px', opacity: 0.7 }}>Average AQI</div>
          </div>
          
          <div style={{ 
            background: 'rgba(245,158,11,0.1)', 
            padding: '10px', 
            borderRadius: '8px',
            border: '1px solid rgba(245,158,11,0.3)'
          }}>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#f59e0b' }}>
              {situation?.crisis_zones?.length || 0}
            </div>
            <div style={{ fontSize: '11px', opacity: 0.7 }}>Crisis Zones</div>
          </div>
        </div>
        
        {situation?.crisis_zones?.length > 0 && (
          <div style={{ marginTop: '10px', fontSize: '12px', color: '#ef4444' }}>
            ⚠️ Critical zones: {situation.crisis_zones.map(z => `Zone ${z}`).join(', ')}
          </div>
        )}
      </div>
      
      {/* AI Recommendations */}
      <div style={{ marginBottom: '20px' }}>
        <h3 style={{ 
          fontSize: '16px', 
          marginBottom: '15px',
          display: 'flex',
          alignItems: 'center',
          gap: '10px'
        }}>
          <span>🤖 AI Recommendations</span>
          <span style={{ 
            fontSize: '10px', 
            background: '#10b981', 
            padding: '2px 8px', 
            borderRadius: '10px' 
          }}>
            REAL-TIME
          </span>
        </h3>
        
        {recommendations.map((rec, index) => (
          <div 
            key={rec.id} 
            className="intervention-card"
            onClick={() => handleApplyIntervention(rec)}
            style={{
              border: selectedRec?.id === rec.id ? '2px solid #667eea' : '1px solid rgba(255,255,255,0.1)',
              background: selectedRec?.id === rec.id ? 'rgba(102,126,234,0.1)' : 'rgba(255,255,255,0.05)',
              marginBottom: '15px',
              cursor: 'pointer',
              position: 'relative'
            }}
          >
            {/* Priority Badge */}
            <div style={{
              position: 'absolute',
              top: '10px',
              right: '10px',
              background: index === 0 ? '#ef4444' : index === 1 ? '#f59e0b' : '#3b82f6',
              padding: '4px 8px',
              borderRadius: '5px',
              fontSize: '10px',
              fontWeight: 'bold'
            }}>
              P{index + 1}
            </div>
            
            <h4 style={{ fontSize: '16px', marginBottom: '10px', paddingRight: '40px' }}>
              {rec.name}
            </h4>
            
            {/* Impact Metrics */}
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(3, 1fr)', 
              gap: '10px',
              marginBottom: '10px' 
            }}>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#10b981' }}>
                  {rec.impact.aqi}
                </div>
                <div style={{ fontSize: '10px', opacity: 0.7 }}>AQI</div>
              </div>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#3b82f6' }}>
                  {rec.details?.lives_saved || 0}
                </div>
                <div style={{ fontSize: '10px', opacity: 0.7 }}>Lives</div>
              </div>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#fbbf24' }}>
                  {rec.details?.confidence || '85%'}
                </div>
                <div style={{ fontSize: '10px', opacity: 0.7 }}>Confidence</div>
              </div>
            </div>
            
            {/* Details */}
            {rec.details && (
              <div style={{ 
                borderTop: '1px solid rgba(255,255,255,0.1)', 
                paddingTop: '10px',
                fontSize: '12px',
                opacity: 0.8
              }}>
                <div style={{ marginBottom: '5px' }}>
                  💡 {rec.details.reasoning}
                </div>
                <div style={{ display: 'flex', gap: '15px', fontSize: '11px' }}>
                  <span>⏱️ {rec.details.implementation_time}</span>
                  <span>💰 {rec.details.economic_impact}</span>
                  <span>📍 Zones: {rec.zones.join(', ')}</span>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
      
      {/* Emergency Protocol Button */}
      {!emergencyActive && (
        <div style={{ marginBottom: '20px' }}>
          <button 
            className="button-3d"
            style={{ 
              width: '100%',
              background: 'linear-gradient(135deg, #ef4444 0%, #991b1b 100%)',
              fontSize: '16px',
              padding: '15px',
              fontWeight: 'bold',
              animation: 'pulse 2s infinite'
            }}
            onClick={() => {
              console.log('🚨 Emergency Protocol Triggered')
              startEmergencyProtocol()
            }}
          >
            🚨 EMERGENCY PROTOCOL ALPHA
          </button>
          <div style={{ fontSize: '11px', opacity: 0.6, marginTop: '5px', textAlign: 'center' }}>
            Activate multi-intervention crisis response
          </div>
        </div>
      )}
      
      {/* Emergency Status Display */}
      {emergencyActive && (
        <div style={{ 
          marginBottom: '20px',
          padding: '15px',
          background: 'linear-gradient(135deg, rgba(239,68,68,0.2) 0%, rgba(153,27,27,0.2) 100%)',
          border: '2px solid #ef4444',
          borderRadius: '10px',
          animation: 'pulse 1s infinite'
        }}>
          <div style={{ fontSize: '14px', fontWeight: 'bold', marginBottom: '10px' }}>
            🚨 EMERGENCY PROTOCOL ACTIVE
          </div>
          <div style={{ fontSize: '12px', lineHeight: '1.6' }}>
            {emergencyStatus || 'Running emergency simulations...'}
          </div>
          <div style={{ marginTop: '10px', fontSize: '11px', opacity: 0.8 }}>
            <div>✓ Analyzing AQI levels</div>
            <div>✓ Deploying interventions</div>
            <div>✓ Computing impact...</div>
          </div>
        </div>
      )}
      
      {/* Quick Actions */}
      <div style={{ marginBottom: '20px' }}>
        <h3 style={{ fontSize: '14px', opacity: 0.7, marginBottom: '10px' }}>
          Quick Policy Actions
        </h3>
        
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
          <button 
            className="button-3d"
            style={{ 
              background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
              fontSize: '14px',
              padding: '10px'
            }}
            onClick={() => handleApplyIntervention({
              id: 'truck_ban',
              type: 'truck_restriction',
              name: 'Truck Ban',
              zones: [1, 2, 3, 4, 5],
              impact: { aqi: -70 },
              details: { reasoning: 'Immediate reduction in heavy vehicle emissions' }
            })}
          >
            🚛 Truck Ban
          </button>
          
          <button 
            className="button-3d"
            style={{ 
              background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
              fontSize: '14px',
              padding: '10px'
            }}
            onClick={() => handleApplyIntervention({
              id: 'odd_even',
              type: 'odd_even',
              name: 'Odd-Even',
              zones: [1, 2, 3, 4, 5],
              impact: { aqi: -45 },
              details: { reasoning: 'Reduce traffic volume by 40%' }
            })}
          >
            🚗 Odd-Even
          </button>
          
          <button 
            className="button-3d"
            style={{ 
              background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
              fontSize: '14px',
              padding: '10px'
            }}
            onClick={() => handleApplyIntervention({
              id: 'green',
              type: 'green_corridor',
              name: 'Green Corridor',
              zones: [3, 5],
              impact: { aqi: -35 },
              details: { reasoning: 'Long-term sustainable solution' }
            })}
          >
            🌳 Green Zone
          </button>
          
          <button 
            className="button-3d"
            style={{ 
              background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
              fontSize: '14px',
              padding: '10px'
            }}
            onClick={() => handleApplyIntervention({
              id: 'metro',
              type: 'public_transport',
              name: 'Free Metro',
              zones: [1, 2, 3, 4, 5],
              impact: { aqi: -40 },
              details: { reasoning: 'Incentivize public transport usage' }
            })}
          >
            🚇 Free Metro
          </button>
        </div>
      </div>
      
      {/* Exposure Management */}
      <div style={{ 
        borderTop: '1px solid rgba(255,255,255,0.1)', 
        paddingTop: '20px' 
      }}>
        <h3 style={{ fontSize: '14px', opacity: 0.7, marginBottom: '10px' }}>
          👥 Citizen Exposure Management
        </h3>
        
        <div style={{ fontSize: '12px', lineHeight: '1.8' }}>
          <div style={{ 
            padding: '8px', 
            background: 'rgba(239,68,68,0.1)', 
            borderRadius: '5px',
            marginBottom: '8px'
          }}>
            🏫 <strong>School Advisory:</strong> Outdoor activities suspended in zones {situation?.crisis_zones?.join(', ') || 'None'}
          </div>
          <div style={{ 
            padding: '8px', 
            background: 'rgba(245,158,11,0.1)', 
            borderRadius: '5px',
            marginBottom: '8px'
          }}>
            🚌 <strong>Safe Travel:</strong> Best hours 10 AM - 4 PM, avoid rush hours
          </div>
          <div style={{ 
            padding: '8px', 
            background: 'rgba(59,130,246,0.1)', 
            borderRadius: '5px'
          }}>
            👴 <strong>Vulnerable Groups:</strong> Stay indoors, use air purifiers
          </div>
        </div>
      </div>
      
      {/* Real-time Monitoring */}
      <div style={{ 
        marginTop: '20px',
        padding: '10px',
        background: 'rgba(16,185,129,0.1)',
        borderRadius: '10px',
        border: '1px solid rgba(16,185,129,0.3)',
        fontSize: '12px',
        textAlign: 'center'
      }}>
        <strong>🔄 System Status:</strong> AI monitoring active | 
        <span style={{ color: '#10b981' }}> Next update in 5 mins</span>
      </div>
    </div>
  )
}

export default PolicyControlPanel
