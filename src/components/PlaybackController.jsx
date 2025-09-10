import React, { useState, useEffect, useRef } from 'react'
import { useSimulationStore } from '../store/simulationStore'

function PlaybackController() {
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentStep, setCurrentStep] = useState(0)
  const [showOverlay, setShowOverlay] = useState(false)
  const [overlayMessage, setOverlayMessage] = useState('')
  const intervalRef = useRef()
  
  const { 
    applyIntervention,
    setTime,
    zones
  } = useSimulationStore()

  // Emergency response sequence steps
  const playbackSequence = [
    {
      time: 0,
      message: "🚨 CRISIS DETECTED: AQI > 400 in Multiple Zones",
      duration: 3000,
      action: () => {
        // Highlight crisis zones
        console.log("Crisis detected")
      }
    },
    {
      time: 3,
      message: "🤖 AI ANALYZING: Identifying pollution sources...",
      duration: 2500,
      action: () => {
        // Show AI thinking animation
      }
    },
    {
      time: 6,
      message: "📊 ANALYSIS COMPLETE: Stubble burning (40%) + Traffic (35%)",
      duration: 3000,
      action: () => {
        // Display source breakdown
      }
    },
    {
      time: 9,
      message: "🎯 RECOMMENDATION: Emergency Protocol Alpha",
      duration: 2500,
      action: () => {
        // Highlight recommendation
      }
    },
    {
      time: 12,
      message: "🚛 IMPLEMENTING: Truck ban on ring roads (6 AM - 6 PM)",
      duration: 3000,
      action: () => {
        applyIntervention({
          id: 'truck_ban',
          type: 'truck_restriction',
          name: 'Emergency Truck Ban',
          zones: [1, 2, 3, 4, 5]
        })
      }
    },
    {
      time: 15,
      message: "🏫 IMPLEMENTING: Schools closed in zones 3 & 4",
      duration: 2500,
      action: () => {
        // Update zone status
      }
    },
    {
      time: 18,
      message: "🚇 IMPLEMENTING: Free metro for 24 hours",
      duration: 2500,
      action: () => {
        // Update transport status
      }
    },
    {
      time: 21,
      message: "📉 RESULT: AQI dropping from 450 → 380",
      duration: 3000,
      action: () => {
        // Animate AQI reduction
      }
    },
    {
      time: 24,
      message: "✅ SUCCESS: 35 lives saved, crisis averted!",
      duration: 4000,
      action: () => {
        // Show success animation
      }
    }
  ]

  const startPlayback = () => {
    setIsPlaying(true)
    setCurrentStep(0)
    setShowOverlay(true)
    runSequence()
  }

  const stopPlayback = () => {
    setIsPlaying(false)
    setShowOverlay(false)
    if (intervalRef.current) {
      clearTimeout(intervalRef.current)
    }
  }

  const runSequence = () => {
    if (currentStep >= playbackSequence.length) {
      stopPlayback()
      return
    }

    const step = playbackSequence[currentStep]
    
    // Update time in simulation
    setTime(step.time)
    
    // Show message
    setOverlayMessage(step.message)
    
    // Run action
    if (step.action) {
      step.action()
    }

    // Move to next step after duration
    intervalRef.current = setTimeout(() => {
      setCurrentStep(prev => prev + 1)
      runSequence()
    }, step.duration)
  }

  useEffect(() => {
    if (isPlaying && currentStep < playbackSequence.length) {
      runSequence()
    }
  }, [currentStep, isPlaying])

  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearTimeout(intervalRef.current)
      }
    }
  }, [])

  return (
    <>
      {/* Control Button */}
      <div style={{
        position: 'absolute',
        top: '100px',
        left: '50%',
        transform: 'translateX(-50%)',
        zIndex: 200
      }}>
        {!isPlaying ? (
          <button
            onClick={startPlayback}
            style={{
              background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
              border: 'none',
              borderRadius: '30px',
              color: 'white',
              padding: '15px 30px',
              fontSize: '16px',
              fontWeight: 'bold',
              cursor: 'pointer',
              boxShadow: '0 10px 30px rgba(239, 68, 68, 0.3)',
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              animation: 'pulse 2s infinite'
            }}
          >
            <span style={{ fontSize: '20px' }}>▶️</span>
            DEMO EMERGENCY RESPONSE
          </button>
        ) : (
          <button
            onClick={stopPlayback}
            style={{
              background: 'rgba(0, 0, 0, 0.8)',
              border: '2px solid #ef4444',
              borderRadius: '30px',
              color: 'white',
              padding: '15px 30px',
              fontSize: '16px',
              fontWeight: 'bold',
              cursor: 'pointer'
            }}
          >
            ⏹ STOP PLAYBACK
          </button>
        )}
      </div>

      {/* Message Overlay */}
      {showOverlay && (
        <div style={{
          position: 'absolute',
          top: '200px',
          left: '50%',
          transform: 'translateX(-50%)',
          zIndex: 300,
          animation: 'slideIn 0.5s ease-out'
        }}>
          <div style={{
            background: 'linear-gradient(135deg, rgba(0,0,0,0.95) 0%, rgba(30,30,40,0.95) 100%)',
            border: '2px solid',
            borderImage: 'linear-gradient(135deg, #ef4444, #f59e0b) 1',
            borderRadius: '20px',
            padding: '25px 40px',
            minWidth: '500px',
            textAlign: 'center',
            boxShadow: '0 20px 60px rgba(0,0,0,0.8)'
          }}>
            <div style={{
              fontSize: '24px',
              fontWeight: 'bold',
              color: 'white',
              textShadow: '0 2px 10px rgba(0,0,0,0.5)'
            }}>
              {overlayMessage}
            </div>
            
            {/* Progress bar */}
            <div style={{
              marginTop: '20px',
              background: 'rgba(255,255,255,0.1)',
              borderRadius: '10px',
              height: '6px',
              overflow: 'hidden'
            }}>
              <div style={{
                width: `${((currentStep + 1) / playbackSequence.length) * 100}%`,
                height: '100%',
                background: 'linear-gradient(90deg, #ef4444, #f59e0b)',
                transition: 'width 0.5s ease-out'
              }} />
            </div>
            
            <div style={{
              marginTop: '10px',
              fontSize: '12px',
              opacity: 0.7,
              color: 'white'
            }}>
              Step {currentStep + 1} of {playbackSequence.length}
            </div>
          </div>
        </div>
      )}

      {/* Timeline indicator during playback */}
      {isPlaying && (
        <div style={{
          position: 'absolute',
          bottom: '150px',
          left: '50%',
          transform: 'translateX(-50%)',
          zIndex: 200,
          background: 'rgba(0,0,0,0.8)',
          padding: '10px 20px',
          borderRadius: '20px',
          border: '1px solid rgba(239, 68, 68, 0.5)'
        }}>
          <div style={{ color: 'white', fontSize: '14px', textAlign: 'center' }}>
            <div style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '5px' }}>
              Simulating Hour: {playbackSequence[currentStep]?.time || 0}:00
            </div>
            <div style={{ opacity: 0.7 }}>
              Emergency Response Protocol Active
            </div>
          </div>
        </div>
      )}

      <style>{`
        @keyframes pulse {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.05); }
        }
        
        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translateX(-50%) translateY(-20px);
          }
          to {
            opacity: 1;
            transform: translateX(-50%) translateY(0);
          }
        }
      `}</style>
    </>
  )
}

export default PlaybackController
