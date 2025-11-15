import React from 'react'
import { useSimulationStore } from '../store/simulationStore'

// Simple bar chart component
function BarChart({ data, title, height = 250 }) {
  const maxValue = Math.max(...data.map(d => d.value))
  const barWidth = 100 / data.length
  const padding = 30
  
  return (
    <div style={{ marginBottom: '20px' }}>
      <h4 style={{ marginBottom: '10px', fontSize: '14px' }}>{title}</h4>
      <svg width="100%" height={height} style={{ border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}>
        {/* Y-axis */}
        <line x1={padding} y1={10} x2={padding} y2={height - 40} stroke="rgba(255,255,255,0.2)" strokeWidth="1" />
        {/* X-axis */}
        <line x1={padding} y1={height - 40} x2="100%" y2={height - 40} stroke="rgba(255,255,255,0.2)" strokeWidth="1" />
        
        {/* Bars */}
        {data.map((item, idx) => {
          const barHeight = (item.value / maxValue) * (height - 60)
          const x = padding + (barWidth * idx * 0.8) + (barWidth * 0.1)
          const y = height - 40 - barHeight
          
          return (
            <g key={idx}>
              <rect
                x={`${padding + (barWidth * idx * 0.8) + (barWidth * 0.1)}%`}
                y={y}
                width={`${barWidth * 0.7}%`}
                height={barHeight}
                fill={item.color || '#667eea'}
                opacity="0.8"
                rx="4"
              />
              <text
                x={`${padding + (barWidth * (idx + 0.5) * 0.8) + (barWidth * 0.1)}%`}
                y={height - 15}
                textAnchor="middle"
                fill="rgba(255,255,255,0.7)"
                fontSize="12"
              >
                {item.label}
              </text>
              <text
                x={`${padding + (barWidth * (idx + 0.5) * 0.8) + (barWidth * 0.1)}%`}
                y={y - 5}
                textAnchor="middle"
                fill="rgba(255,255,255,0.9)"
                fontSize="11"
                fontWeight="bold"
              >
                {item.value}
              </text>
            </g>
          )
        })}
      </svg>
    </div>
  )
}

// Line chart component
function LineChart({ data, title, height = 250 }) {
  const maxValue = Math.max(...data.map(d => d.value))
  const minValue = Math.min(...data.map(d => d.value))
  const range = maxValue - minValue
  const padding = 30
  const graphWidth = 100 - padding * 2
  const graphHeight = height - 60
  
  const points = data.map((item, idx) => {
    const x = padding + (graphWidth * (idx / (data.length - 1)))
    const y = height - 40 - ((item.value - minValue) / range) * graphHeight
    return { x, y, ...item }
  })
  
  const pathData = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ')
  
  return (
    <div style={{ marginBottom: '20px' }}>
      <h4 style={{ marginBottom: '10px', fontSize: '14px' }}>{title}</h4>
      <svg width="100%" height={height} style={{ border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}>
        {/* Y-axis */}
        <line x1={padding} y1={10} x2={padding} y2={height - 40} stroke="rgba(255,255,255,0.2)" strokeWidth="1" />
        {/* X-axis */}
        <line x1={padding} y1={height - 40} x2="100%" y2={height - 40} stroke="rgba(255,255,255,0.2)" strokeWidth="1" />
        
        {/* Line */}
        <path d={pathData} stroke="#667eea" strokeWidth="2.5" fill="none" />
        
        {/* Points */}
        {points.map((p, idx) => (
          <g key={idx}>
            <circle cx={p.x} cy={p.y} r="4" fill="#667eea" opacity="0.8" />
            <text
              x={p.x}
              y={height - 15}
              textAnchor="middle"
              fill="rgba(255,255,255,0.7)"
              fontSize="12"
            >
              {p.label}
            </text>
            <text
              x={p.x}
              y={p.y - 10}
              textAnchor="middle"
              fill="rgba(255,255,255,0.9)"
              fontSize="11"
              fontWeight="bold"
            >
              {p.value}
            </text>
          </g>
        ))}
      </svg>
    </div>
  )
}

function EmergencyResultsModal() {
  const { emergencyResults, showResultsModal, closeResultsModal } = useSimulationStore()

  if (!showResultsModal || !emergencyResults) return null

  const { baselineAqi, newAqi, aqiReduction, livesSaved, baselineZones, emergencyZones, graphs } = emergencyResults

  // Create graph data
  const aqiByZone = baselineZones?.map((zone, idx) => ({
    label: zone.name?.substring(0, 4) || `Z${idx+1}`,
    baseline: Math.round(zone.aqi),
    emergency: Math.round(emergencyZones?.[idx]?.aqi || zone.aqi)
  })) || []

  const aqiReductionData = aqiByZone.map(z => ({
    label: z.label,
    value: z.baseline - z.emergency,
    color: '#10b981'
  }))

  const baselineAqiData = aqiByZone.map(z => ({
    label: z.label,
    value: z.baseline,
    color: '#ef4444'
  }))

  const emergencyAqiData = aqiByZone.map(z => ({
    label: z.label,
    value: z.emergency,
    color: '#10b981'
  }))

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0, 0, 0, 0.85)',
      backdropFilter: 'blur(10px)',
      zIndex: 10000,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      animation: 'fadeIn 0.3s ease-out',
      overflow: 'auto'
    }}>
      <div style={{
        background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
        border: '2px solid rgba(102, 126, 234, 0.5)',
        borderRadius: '20px',
        padding: '40px',
        maxWidth: '1000px',
        width: '95%',
        maxHeight: '95vh',
        overflowY: 'auto',
        boxShadow: '0 20px 60px rgba(0, 0, 0, 0.5)',
        color: 'white',
        animation: 'slideUp 0.4s ease-out',
        margin: 'auto'
      }}>
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '30px' }}>
          <h1 style={{
            fontSize: '36px',
            marginBottom: '10px',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            fontWeight: 'bold'
          }}>
            🚨 Emergency Protocol Complete
          </h1>
          <p style={{ fontSize: '16px', opacity: 0.8 }}>
            Crisis Response Results & Analysis
          </p>
        </div>

        {/* Key Metrics Grid */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
          gap: '20px',
          marginBottom: '30px'
        }}>
          <div style={{
            background: 'rgba(239, 68, 68, 0.1)',
            border: '2px solid rgba(239, 68, 68, 0.3)',
            borderRadius: '15px',
            padding: '20px',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '12px', opacity: 0.7, marginBottom: '8px' }}>Baseline AQI</div>
            <div style={{ fontSize: '38px', fontWeight: 'bold', color: '#ef4444' }}>{baselineAqi}</div>
          </div>

          <div style={{
            background: 'rgba(16, 185, 129, 0.1)',
            border: '2px solid rgba(16, 185, 129, 0.3)',
            borderRadius: '15px',
            padding: '20px',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '12px', opacity: 0.7, marginBottom: '8px' }}>New AQI</div>
            <div style={{ fontSize: '38px', fontWeight: 'bold', color: '#10b981' }}>{newAqi}</div>
          </div>

          <div style={{
            background: 'rgba(59, 130, 246, 0.1)',
            border: '2px solid rgba(59, 130, 246, 0.3)',
            borderRadius: '15px',
            padding: '20px',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '12px', opacity: 0.7, marginBottom: '8px' }}>AQI Reduction</div>
            <div style={{ fontSize: '38px', fontWeight: 'bold', color: '#3b82f6' }}>-{aqiReduction}</div>
          </div>

          <div style={{
            background: 'rgba(245, 158, 11, 0.1)',
            border: '2px solid rgba(245, 158, 11, 0.3)',
            borderRadius: '15px',
            padding: '20px',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '12px', opacity: 0.7, marginBottom: '8px' }}>Lives Saved</div>
            <div style={{ fontSize: '38px', fontWeight: 'bold', color: '#f59e0b' }}>{livesSaved}</div>
          </div>
        </div>

        {/* Graphs Section */}
        <div style={{
          background: 'rgba(255, 255, 255, 0.05)',
          borderRadius: '15px',
          padding: '20px',
          marginBottom: '25px'
        }}>
          <h3 style={{ marginBottom: '20px', fontSize: '20px', color: '#667eea' }}>📊 Professional Analysis Charts</h3>
          
          {graphs && Object.keys(graphs).length > 0 ? (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
              {graphs.aqi_comparison && (
                <div style={{
                  background: 'rgba(255, 255, 255, 0.03)',
                  borderRadius: '10px',
                  padding: '10px',
                  border: '1px solid rgba(255, 255, 255, 0.1)'
                }}>
                  <img 
                    src={graphs.aqi_comparison} 
                    alt="AQI Comparison" 
                    style={{ width: '100%', borderRadius: '8px' }}
                  />
                </div>
              )}
              
              {graphs.aqi_reduction && (
                <div style={{
                  background: 'rgba(255, 255, 255, 0.03)',
                  borderRadius: '10px',
                  padding: '10px',
                  border: '1px solid rgba(255, 255, 255, 0.1)'
                }}>
                  <img 
                    src={graphs.aqi_reduction} 
                    alt="AQI Reduction Impact" 
                    style={{ width: '100%', borderRadius: '8px' }}
                  />
                </div>
              )}
              
              {graphs.percentage_reduction && (
                <div style={{
                  background: 'rgba(255, 255, 255, 0.03)',
                  borderRadius: '10px',
                  padding: '10px',
                  border: '1px solid rgba(255, 255, 255, 0.1)'
                }}>
                  <img 
                    src={graphs.percentage_reduction} 
                    alt="Percentage Reduction" 
                    style={{ width: '100%', borderRadius: '8px' }}
                  />
                </div>
              )}
              
              {graphs.trend_chart && (
                <div style={{
                  background: 'rgba(255, 255, 255, 0.03)',
                  borderRadius: '10px',
                  padding: '10px',
                  border: '1px solid rgba(255, 255, 255, 0.1)'
                }}>
                  <img 
                    src={graphs.trend_chart} 
                    alt="Trend Chart" 
                    style={{ width: '100%', borderRadius: '8px' }}
                  />
                </div>
              )}
            </div>
          ) : (
            // Fallback to SVG charts if matplotlib graphs not available
            <>
              <BarChart 
                data={aqiReductionData} 
                title="AQI Reduction per Zone" 
              />
              
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                <BarChart 
                  data={baselineAqiData} 
                  title="Baseline AQI Levels"
                  height={200}
                />
                <BarChart 
                  data={emergencyAqiData} 
                  title="Emergency Response AQI"
                  height={200}
                />
              </div>
            </>
          )}
        </div>

        {/* Zone-by-Zone Comparison */}
        <div style={{
          background: 'rgba(255, 255, 255, 0.05)',
          borderRadius: '15px',
          padding: '20px',
          marginBottom: '25px'
        }}>
          <h3 style={{ marginBottom: '15px', fontSize: '18px' }}>🗺️ Zone-by-Zone Impact</h3>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', fontSize: '13px' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid rgba(255, 255, 255, 0.1)' }}>
                  <th style={{ padding: '10px', textAlign: 'left' }}>Zone</th>
                  <th style={{ padding: '10px', textAlign: 'center' }}>Before</th>
                  <th style={{ padding: '10px', textAlign: 'center' }}>After</th>
                  <th style={{ padding: '10px', textAlign: 'center' }}>Change</th>
                  <th style={{ padding: '10px', textAlign: 'center' }}>Status</th>
                </tr>
              </thead>
              <tbody>
                {baselineZones?.map((baseline, idx) => {
                  const emergency = emergencyZones?.[idx]
                  const change = baseline.aqi - (emergency?.aqi || baseline.aqi)
                  const changePercent = ((change / baseline.aqi) * 100).toFixed(1)
                  return (
                    <tr key={baseline.id} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.05)' }}>
                      <td style={{ padding: '10px' }}>{baseline.name}</td>
                      <td style={{ padding: '10px', textAlign: 'center', color: '#ef4444', fontWeight: 'bold' }}>
                        {Math.round(baseline.aqi)}
                      </td>
                      <td style={{ padding: '10px', textAlign: 'center', color: '#10b981', fontWeight: 'bold' }}>
                        {Math.round(emergency?.aqi || baseline.aqi)}
                      </td>
                      <td style={{ padding: '10px', textAlign: 'center', color: '#3b82f6', fontWeight: 'bold' }}>
                        -{Math.round(change)} ({changePercent}%)
                      </td>
                      <td style={{ padding: '10px', textAlign: 'center' }}>
                        {change > 30 ? '✅ Excellent' : change > 15 ? '✔️ Good' : '⚠️ Fair'}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Interventions Applied */}
        <div style={{
          background: 'rgba(102, 126, 234, 0.1)',
          border: '1px solid rgba(102, 126, 234, 0.3)',
          borderRadius: '15px',
          padding: '20px',
          marginBottom: '25px'
        }}>
          <h3 style={{ marginBottom: '15px', fontSize: '16px' }}>⚡ Interventions Applied</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px', fontSize: '13px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '18px' }}>✅</span>
              <span>Truck Ban (6-12 AM)</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '18px' }}>✅</span>
              <span>Odd-Even Restrictions</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '18px' }}>✅</span>
              <span>Industrial Curtailment</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '18px' }}>✅</span>
              <span>Dynamic Rerouting</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '18px' }}>✅</span>
              <span>Green Infrastructure</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '18px' }}>✅</span>
              <span>Public Transport Subsidy</span>
            </div>
          </div>
        </div>

        {/* Summary Box */}
        <div style={{
          background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%)',
          border: '2px solid rgba(102, 126, 234, 0.4)',
          borderRadius: '15px',
          padding: '20px',
          marginBottom: '25px',
          textAlign: 'center'
        }}>
          <h3 style={{ marginBottom: '10px', fontSize: '16px' }}>✨ Emergency Response Summary</h3>
          <p style={{ fontSize: '14px', opacity: 0.9, marginBottom: '10px' }}>
            The comprehensive emergency protocol successfully reduced air quality index by <strong>{aqiReduction}</strong> points,
            saving an estimated <strong>{livesSaved}</strong> lives across all zones.
          </p>
          <p style={{ fontSize: '12px', opacity: 0.7 }}>
            All interventions were deployed simultaneously for maximum impact. System returned to monitoring mode.
          </p>
        </div>

        {/* Close Button */}
        <button
          onClick={closeResultsModal}
          style={{
            width: '100%',
            padding: '15px',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            border: 'none',
            borderRadius: '10px',
            color: 'white',
            fontSize: '16px',
            fontWeight: 'bold',
            cursor: 'pointer',
            transition: 'transform 0.2s'
          }}
          onMouseEnter={(e) => e.target.style.transform = 'scale(1.02)'}
          onMouseLeave={(e) => e.target.style.transform = 'scale(1)'}
        >
          ✕ Close & Return to Dashboard
        </button>
      </div>

      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        @keyframes slideUp {
          from {
            opacity: 0;
            transform: translateY(30px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  )
}

export default EmergencyResultsModal
