import React, { useState, useEffect } from 'react'
import { useSimulationStore } from '../store/simulationStore'

function ImpactResultsModal({ show, onClose, intervention }) {
  const { zones, compareBeforeAfter } = useSimulationStore()
  const [impactData, setImpactData] = useState(null)

  useEffect(() => {
    if (show && intervention) {
      // Calculate impact
      const before = intervention.beforeData || {}
      const after = zones

      const impact = {
        aqiReduction: calculateAverageChange(before, after, 'aqi'),
        energySavings: calculateAverageChange(before, after, 'energy'),
        trafficImprovement: calculateAverageChange(before, after, 'traffic_flow'),
        affectedZones: intervention.zones || [],
        interventionName: intervention.name || 'Unknown Intervention',
        livesProtected: Math.floor(Math.abs(calculateAverageChange(before, after, 'aqi')) * 2.5),
        economicImpact: calculateEconomicImpact(intervention)
      }

      setImpactData(impact)
    }
  }, [show, intervention, zones])

  const calculateAverageChange = (before, after, metric) => {
    if (!before.zones || !after || after.length === 0) return 0
    
    const beforeAvg = before.zones.reduce((sum, z) => sum + (z[metric] || 0), 0) / before.zones.length
    const afterAvg = after.reduce((sum, z) => sum + (z[metric] || 0), 0) / after.length
    
    return beforeAvg - afterAvg // Positive = improvement
  }

  const calculateEconomicImpact = (intervention) => {
    // Simplified economic calculation
    const type = intervention.type
    const zones = intervention.zones?.length || 1
    
    const impacts = {
      'truck_restriction': -500000 * zones, // Daily loss
      'traffic_ban': -300000 * zones,
      'green_cover': 200000 * zones, // Long-term benefit
      'emergency': -800000 * zones
    }
    
    return impacts[type] || 0
  }

  if (!show || !impactData) return null

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0, 0, 0, 0.85)',
      backdropFilter: 'blur(10px)',
      zIndex: 2000,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      animation: 'fadeIn 0.3s ease-out'
    }}>
      <div style={{
        background: 'linear-gradient(135deg, rgba(10, 10, 30, 0.98) 0%, rgba(30, 30, 50, 0.98) 100%)',
        border: '2px solid rgba(102, 126, 234, 0.5)',
        borderRadius: '20px',
        padding: '40px',
        maxWidth: '900px',
        maxHeight: '90vh',
        overflow: 'auto',
        boxShadow: '0 25px 80px rgba(0, 0, 0, 0.9)',
        animation: 'slideUp 0.4s ease-out',
        color: 'white'
      }}>
        {/* Header */}
        <div style={{ marginBottom: '30px', textAlign: 'center' }}>
          <div style={{
            fontSize: '42px',
            marginBottom: '10px'
          }}>✅</div>
          <h2 style={{
            fontSize: '32px',
            fontWeight: 'bold',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            marginBottom: '10px'
          }}>
            Impact Analysis Complete
          </h2>
          <p style={{ fontSize: '18px', opacity: 0.8 }}>
            {impactData.interventionName}
          </p>
        </div>

        {/* Key Metrics Grid */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(2, 1fr)',
          gap: '20px',
          marginBottom: '30px'
        }}>
          {/* AQI Reduction */}
          <div style={{
            background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%)',
            border: '2px solid rgba(16, 185, 129, 0.3)',
            borderRadius: '15px',
            padding: '25px',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '14px', opacity: 0.7, marginBottom: '10px' }}>
              AQI REDUCTION
            </div>
            <div style={{
              fontSize: '48px',
              fontWeight: 'bold',
              color: '#10b981'
            }}>
              -{impactData.aqiReduction.toFixed(0)}
            </div>
            <div style={{ fontSize: '12px', opacity: 0.6, marginTop: '5px' }}>
              Average across zones
            </div>
            {/* Mini bar chart */}
            <div style={{
              marginTop: '15px',
              height: '6px',
              background: 'rgba(255,255,255,0.1)',
              borderRadius: '3px',
              overflow: 'hidden'
            }}>
              <div style={{
                width: `${Math.min(100, (impactData.aqiReduction / 100) * 100)}%`,
                height: '100%',
                background: 'linear-gradient(90deg, #10b981, #34d399)',
                transition: 'width 1s ease-out'
              }} />
            </div>
          </div>

          {/* Lives Protected */}
          <div style={{
            background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(37, 99, 235, 0.1) 100%)',
            border: '2px solid rgba(59, 130, 246, 0.3)',
            borderRadius: '15px',
            padding: '25px',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '14px', opacity: 0.7, marginBottom: '10px' }}>
              LIVES PROTECTED
            </div>
            <div style={{
              fontSize: '48px',
              fontWeight: 'bold',
              color: '#3b82f6'
            }}>
              ~{impactData.livesProtected}
            </div>
            <div style={{ fontSize: '12px', opacity: 0.6, marginTop: '5px' }}>
              Estimated daily impact
            </div>
            <div style={{
              marginTop: '15px',
              height: '6px',
              background: 'rgba(255,255,255,0.1)',
              borderRadius: '3px',
              overflow: 'hidden'
            }}>
              <div style={{
                width: `${Math.min(100, (impactData.livesProtected / 200) * 100)}%`,
                height: '100%',
                background: 'linear-gradient(90deg, #3b82f6, #60a5fa)',
                transition: 'width 1s ease-out 0.2s'
              }} />
            </div>
          </div>

          {/* Traffic Impact */}
          <div style={{
            background: 'linear-gradient(135deg, rgba(251, 191, 36, 0.1) 0%, rgba(245, 158, 11, 0.1) 100%)',
            border: '2px solid rgba(251, 191, 36, 0.3)',
            borderRadius: '15px',
            padding: '25px',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '14px', opacity: 0.7, marginBottom: '10px' }}>
              TRAFFIC CHANGE
            </div>
            <div style={{
              fontSize: '48px',
              fontWeight: 'bold',
              color: impactData.trafficImprovement > 0 ? '#10b981' : '#fbbf24'
            }}>
              {impactData.trafficImprovement > 0 ? '-' : '+'}{Math.abs(impactData.trafficImprovement).toFixed(0)}%
            </div>
            <div style={{ fontSize: '12px', opacity: 0.6, marginTop: '5px' }}>
              {impactData.trafficImprovement > 0 ? 'Reduced congestion' : 'Increased congestion'}
            </div>
            <div style={{
              marginTop: '15px',
              height: '6px',
              background: 'rgba(255,255,255,0.1)',
              borderRadius: '3px',
              overflow: 'hidden'
            }}>
              <div style={{
                width: `${Math.min(100, Math.abs(impactData.trafficImprovement))}%`,
                height: '100%',
                background: impactData.trafficImprovement > 0 
                  ? 'linear-gradient(90deg, #10b981, #34d399)'
                  : 'linear-gradient(90deg, #fbbf24, #fcd34d)',
                transition: 'width 1s ease-out 0.4s'
              }} />
            </div>
          </div>

          {/* Economic Impact */}
          <div style={{
            background: 'linear-gradient(135deg, rgba(168, 85, 247, 0.1) 0%, rgba(147, 51, 234, 0.1) 100%)',
            border: '2px solid rgba(168, 85, 247, 0.3)',
            borderRadius: '15px',
            padding: '25px',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '14px', opacity: 0.7, marginBottom: '10px' }}>
              ECONOMIC IMPACT
            </div>
            <div style={{
              fontSize: '38px',
              fontWeight: 'bold',
              color: impactData.economicImpact < 0 ? '#ef4444' : '#10b981'
            }}>
              {impactData.economicImpact < 0 ? '-' : '+'}₹{(Math.abs(impactData.economicImpact) / 1000000).toFixed(1)}M
            </div>
            <div style={{ fontSize: '12px', opacity: 0.6, marginTop: '5px' }}>
              Daily {impactData.economicImpact < 0 ? 'cost' : 'benefit'}
            </div>
            <div style={{
              marginTop: '15px',
              height: '6px',
              background: 'rgba(255,255,255,0.1)',
              borderRadius: '3px',
              overflow: 'hidden'
            }}>
              <div style={{
                width: `${Math.min(100, (Math.abs(impactData.economicImpact) / 1000000) * 10)}%`,
                height: '100%',
                background: impactData.economicImpact < 0
                  ? 'linear-gradient(90deg, #ef4444, #f87171)'
                  : 'linear-gradient(90deg, #10b981, #34d399)',
                transition: 'width 1s ease-out 0.6s'
              }} />
            </div>
          </div>
        </div>

        {/* Visual Comparison Chart */}
        <div style={{
          background: 'rgba(0, 0, 0, 0.3)',
          borderRadius: '15px',
          padding: '25px',
          marginBottom: '25px'
        }}>
          <h3 style={{ fontSize: '20px', marginBottom: '20px', opacity: 0.9 }}>
            📊 Zone-wise AQI Comparison
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {impactData.affectedZones.slice(0, 5).map((zoneId, idx) => {
              const zone = zones.find(z => z.id === zoneId)
              const beforeAQI = intervention.beforeData?.zones?.find(z => z.id === zoneId)?.aqi || 250
              const afterAQI = zone?.aqi || 200
              const reduction = beforeAQI - afterAQI

              return (
                <div key={zoneId} style={{ 
                  animation: `slideInRight 0.5s ease-out ${idx * 0.1}s both` 
                }}>
                  <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    marginBottom: '8px',
                    fontSize: '14px'
                  }}>
                    <span>Zone {zoneId}</span>
                    <span style={{ color: reduction > 0 ? '#10b981' : '#fbbf24' }}>
                      {reduction > 0 ? '↓' : '↑'} {Math.abs(reduction).toFixed(0)} AQI
                    </span>
                  </div>
                  <div style={{
                    display: 'flex',
                    gap: '10px',
                    alignItems: 'center'
                  }}>
                    {/* Before bar */}
                    <div style={{ flex: 1 }}>
                      <div style={{
                        height: '24px',
                        background: 'linear-gradient(90deg, #ef4444, #dc2626)',
                        borderRadius: '4px',
                        width: `${(beforeAQI / 500) * 100}%`,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'flex-end',
                        paddingRight: '8px',
                        fontSize: '12px',
                        fontWeight: 'bold'
                      }}>
                        {beforeAQI.toFixed(0)}
                      </div>
                    </div>
                    {/* Arrow */}
                    <span style={{ fontSize: '20px' }}>→</span>
                    {/* After bar */}
                    <div style={{ flex: 1 }}>
                      <div style={{
                        height: '24px',
                        background: afterAQI < 200 
                          ? 'linear-gradient(90deg, #10b981, #34d399)'
                          : 'linear-gradient(90deg, #fbbf24, #fcd34d)',
                        borderRadius: '4px',
                        width: `${(afterAQI / 500) * 100}%`,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'flex-end',
                        paddingRight: '8px',
                        fontSize: '12px',
                        fontWeight: 'bold'
                      }}>
                        {afterAQI.toFixed(0)}
                      </div>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Action Message */}
        <div style={{
          background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%)',
          border: '2px solid rgba(102, 126, 234, 0.4)',
          borderRadius: '15px',
          padding: '20px',
          marginBottom: '25px',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '10px' }}>
            💡 Let's Build on This Success!
          </div>
          <div style={{ fontSize: '14px', opacity: 0.8, lineHeight: '1.6' }}>
            This intervention shows promising results. Consider implementing it for longer durations
            or combining it with other policies for even better outcomes.
          </div>
        </div>

        {/* Action Buttons */}
        <div style={{
          display: 'flex',
          gap: '15px',
          justifyContent: 'center'
        }}>
          <button
            onClick={() => {
              // Apply similar intervention to more zones
              alert('🎯 Expanding intervention to additional zones...')
            }}
            style={{
              padding: '15px 30px',
              borderRadius: '12px',
              border: 'none',
              background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
              color: 'white',
              fontSize: '16px',
              fontWeight: 'bold',
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              boxShadow: '0 4px 15px rgba(16, 185, 129, 0.3)'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-2px)'
              e.currentTarget.style.boxShadow = '0 6px 20px rgba(16, 185, 129, 0.5)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)'
              e.currentTarget.style.boxShadow = '0 4px 15px rgba(16, 185, 129, 0.3)'
            }}
          >
            🚀 Scale Up Policy
          </button>
          
          <button
            onClick={onClose}
            style={{
              padding: '15px 30px',
              borderRadius: '12px',
              border: '2px solid rgba(255, 255, 255, 0.3)',
              background: 'rgba(255, 255, 255, 0.1)',
              color: 'white',
              fontSize: '16px',
              fontWeight: 'bold',
              cursor: 'pointer',
              transition: 'all 0.3s ease'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.2)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)'
            }}
          >
            Close
          </button>
        </div>
      </div>

      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        @keyframes slideUp {
          from {
            opacity: 0;
            transform: translateY(50px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        @keyframes slideInRight {
          from {
            opacity: 0;
            transform: translateX(-30px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }
      `}</style>
    </div>
  )
}

export default ImpactResultsModal
