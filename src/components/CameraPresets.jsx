import React, { useRef, useEffect, useState } from 'react'
import { useSimulationStore } from '../store/simulationStore'
import * as THREE from 'three'

function CameraPresets() {
  const controlsRef = useRef()
  const cameraRef = useRef()
  const [menuOpen, setMenuOpen] = useState(false)
  
  // Define CCTV camera positions - EXACT landmark coordinates
  const cameraPresets = {
    overview: {
      name: 'City Overview',
      position: [150, 100, 150],
      target: [0, 0, 0],
      icon: '🏙️'
    },
    connaughtPlace: {
      name: 'Connaught Place',
      position: [40, 40, 40],
      target: [0, 0, 0], // Connaught Place is at center (0,0,0)
      icon: '📍'
    },
    karolBagh: {
      name: 'Karol Bagh', 
      position: [-50, 40, -50],
      target: [-70, 0, -70], // Karol Bagh exact position
      icon: '🏘️'
    },
    dwarka: {
      name: 'Dwarka',
      position: [90, 40, -50],
      target: [70, 0, -70], // Dwarka exact position
      icon: '🏢'
    },
    rohini: {
      name: 'Rohini',
      position: [-50, 40, 90],
      target: [-70, 0, 70], // Rohini exact position
      icon: '🏠'
    },
    saket: {
      name: 'Saket',
      position: [90, 40, 90],
      target: [70, 0, 70], // Saket exact position
      icon: '🛍️'
    },
    trafficView: {
      name: 'Traffic Monitor',
      position: [0, 150, 1],
      target: [0, 0, 0],
      icon: '🚗'
    },
    pollutionView: {
      name: 'Pollution Overview',
      position: [-120, 80, -120],
      target: [0, 20, 0],
      icon: '☁️'
    },
    indiaGate: {
      name: 'India Gate',
      position: [30, 50, -70],
      target: [0, 10, -100], // India Gate exact position at (0, 0, -100)
      icon: '🏛️'
    },
    lotusTemple: {
      name: 'Lotus Temple',
      position: [130, 40, 80],
      target: [100, 10, 50], // Lotus Temple exact position at (100, 0, 50)
      icon: '🪷'
    },
    redFort: {
      name: 'Red Fort',
      position: [-70, 50, -10],
      target: [-100, 10, -30], // Red Fort exact position at (-100, 0, -30)
      icon: '🏰'
    }
  }

  const smoothCameraTransition = (preset) => {
    // Get camera from global store
    const { cameraRef: globalCamera, controlsRef: globalControls } = useSimulationStore.getState()
    const camera = globalCamera
    
    if (!camera) {
      console.warn('Camera not initialized yet, waiting...')
      // Retry after a short delay
      setTimeout(() => smoothCameraTransition(preset), 100)
      return
    }
    
    const startPos = camera.position.clone()
    const endPos = new THREE.Vector3(...preset.position)
    const targetPos = new THREE.Vector3(...preset.target)
    const startTime = Date.now()
    const duration = 2000 // 2 seconds
    
    // Disable orbit controls during transition if available
    if (globalControls && globalControls.enabled !== undefined) {
      globalControls.enabled = false
    }
    
    const animate = () => {
      const elapsed = Date.now() - startTime
      const progress = Math.min(elapsed / duration, 1)
      
      // Easing function (ease-in-out cubic)
      const eased = progress < 0.5
        ? 4 * progress * progress * progress
        : 1 - Math.pow(-2 * progress + 2, 3) / 2
      
      // Interpolate position
      camera.position.lerpVectors(startPos, endPos, eased)
      
      // Look at target smoothly
      camera.lookAt(targetPos)
      
      if (progress < 1) {
        requestAnimationFrame(animate)
      } else {
        // Re-enable controls after animation
        if (globalControls && globalControls.enabled !== undefined) {
          globalControls.enabled = true
          if (globalControls.target) {
            globalControls.target.copy(targetPos)
          }
        }
      }
    }
    
    animate()
  }

  const handlePresetChange = (presetKey) => {
    const preset = cameraPresets[presetKey]
    if (preset) {
      smoothCameraTransition(preset)
    }
  }

  // Store reference to controls if needed
  useEffect(() => {
    const { setControlsRef } = useSimulationStore.getState()
    if (setControlsRef) {
      setControlsRef(controlsRef)
    }
  }, [])

  return (
    <div style={{
      position: 'absolute',
      bottom: '20px',
      right: '20px',
      zIndex: 100,
      display: 'flex',
      flexDirection: 'column',
      gap: '10px',
      alignItems: 'flex-end'
    }}>
      {/* Hamburger Button */}
      <button
        onClick={() => setMenuOpen(!menuOpen)}
        style={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          border: '2px solid rgba(255, 255, 255, 0.3)',
          borderRadius: '50%',
          width: '60px',
          height: '60px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '4px',
          cursor: 'pointer',
          transition: 'all 0.3s',
          boxShadow: '0 4px 15px rgba(102, 126, 234, 0.4)',
          zIndex: 101
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.transform = 'scale(1.1)'
          e.currentTarget.style.boxShadow = '0 6px 20px rgba(102, 126, 234, 0.6)'
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = 'scale(1)'
          e.currentTarget.style.boxShadow = '0 4px 15px rgba(102, 126, 234, 0.4)'
        }}
      >
        <div style={{ fontSize: '24px', color: 'white' }}>📹</div>
        <div style={{ fontSize: '9px', color: 'white', fontWeight: 'bold' }}>CCTV</div>
      </button>

      {/* Camera Menu - Collapsible */}
      {menuOpen && (
      <div style={{
        background: 'rgba(0, 0, 0, 0.9)',
        backdropFilter: 'blur(10px)',
        border: '2px solid rgba(102, 126, 234, 0.5)',
        borderRadius: '15px',
        padding: '15px',
        minWidth: '220px',
        maxHeight: '70vh',
        overflowY: 'auto',
        animation: 'slideIn 0.3s ease-out'
      }}>
        <h3 style={{
          fontSize: '14px',
          fontWeight: '600',
          marginBottom: '15px',
          color: 'white',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <span>📹</span> CCTV Cameras
        </h3>
        
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr',
          gap: '8px'
        }}>
          {Object.entries(cameraPresets).map(([key, preset]) => (
            <button
              key={key}
              onClick={() => handlePresetChange(key)}
              style={{
                background: 'rgba(255, 255, 255, 0.05)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '8px',
                color: 'white',
                padding: '8px 12px',
                fontSize: '12px',
                cursor: 'pointer',
                transition: 'all 0.3s',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                textAlign: 'left'
              }}
              onMouseEnter={(e) => {
                e.target.style.background = 'rgba(102, 126, 234, 0.2)'
                e.target.style.borderColor = '#667eea'
                e.target.style.transform = 'translateX(5px)'
              }}
              onMouseLeave={(e) => {
                e.target.style.background = 'rgba(255, 255, 255, 0.05)'
                e.target.style.borderColor = 'rgba(255, 255, 255, 0.1)'
                e.target.style.transform = 'translateX(0)'
              }}
            >
              <span style={{ fontSize: '16px' }}>{preset.icon}</span>
              <span>{preset.name}</span>
            </button>
          ))}
        </div>

        {/* Quick access buttons */}
        <div style={{
          marginTop: '15px',
          paddingTop: '15px',
          borderTop: '1px solid rgba(255, 255, 255, 0.1)'
        }}>
          <div style={{
            fontSize: '11px',
            opacity: 0.7,
            marginBottom: '8px',
            color: 'white'
          }}>
            Quick Views
          </div>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: '5px'
          }}>
            {['overview', 'trafficView', 'pollutionView'].map((key) => {
              const preset = cameraPresets[key]
              return (
                <button
                  key={key}
                  onClick={() => handlePresetChange(key)}
                  title={preset.name}
                  style={{
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    border: 'none',
                    borderRadius: '5px',
                    color: 'white',
                    padding: '8px',
                    fontSize: '18px',
                    cursor: 'pointer',
                    transition: 'transform 0.2s'
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.transform = 'scale(1.1)'
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.transform = 'scale(1)'
                  }}
                >
                  {preset.icon}
                </button>
              )
            })}
          </div>
        </div>

        {/* Live indicator */}
        <div style={{
          marginTop: '10px',
          display: 'flex',
          alignItems: 'center',
          gap: '5px',
          fontSize: '11px',
          color: '#10b981'
        }}>
          <div style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            background: '#10b981',
            animation: 'pulse 2s infinite'
          }} />
          <span>Live Feed Active</span>
        </div>
      </div>

      )}

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translateY(20px);
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

export default CameraPresets
