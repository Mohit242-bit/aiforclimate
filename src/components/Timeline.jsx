import React, { useEffect, useRef } from 'react'
import { useSimulationStore } from '../store/simulationStore'

function Timeline() {
  const { time, setTime, playing, togglePlay, speed, setSpeed } = useSimulationStore()
  const intervalRef = useRef()
  
  useEffect(() => {
    if (playing) {
      intervalRef.current = setInterval(() => {
        setTime((time + 1) % 24)
      }, 1000 / speed)
    } else {
      clearInterval(intervalRef.current)
    }
    
    return () => clearInterval(intervalRef.current)
  }, [playing, speed, time, setTime])
  
  const formatTime = (t) => {
    const hour = Math.floor(t)
    const minutes = Math.floor((t - hour) * 60)
    return `${hour.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`
  }
  
  return (
    <div className="timeline">
      <div className="timeline-controls">
        <button className="play-button" onClick={togglePlay}>
          {playing ? (
            <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
              <rect x="6" y="4" width="4" height="16" />
              <rect x="14" y="4" width="4" height="16" />
            </svg>
          ) : (
            <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
              <path d="M8 5v14l11-7z" />
            </svg>
          )}
        </button>
        
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: '18px', fontWeight: '600', marginBottom: '8px' }}>
            {formatTime(time)}
          </div>
          <input
            type="range"
            className="time-slider"
            min="0"
            max="24"
            step="0.25"
            value={time}
            onChange={(e) => setTime(parseFloat(e.target.value))}
          />
        </div>
        
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <span style={{ fontSize: '14px', opacity: 0.7 }}>Speed</span>
          <select 
            value={speed} 
            onChange={(e) => setSpeed(parseFloat(e.target.value))}
            style={{
              background: 'rgba(255,255,255,0.1)',
              border: '1px solid rgba(255,255,255,0.2)',
              borderRadius: '5px',
              color: 'white',
              padding: '5px'
            }}
          >
            <option value="0.5">0.5x</option>
            <option value="1">1x</option>
            <option value="2">2x</option>
            <option value="4">4x</option>
          </select>
        </div>
      </div>
    </div>
  )
}

export default Timeline
