import React, { useRef, useMemo } from 'react'
import { useFrame } from '@react-three/fiber'
import { Sphere, Html, Float, Box } from '@react-three/drei'
import * as THREE from 'three'

/**
 * POLLUTION VISUALIZATION SYSTEM
 * Makes air quality HIGHLY VISIBLE through:
 * - Large animated smoke clouds
 * - Floating pollution particles
 * - AQI indicators
 * - Color-coded haze layers
 */

// Animated pollution cloud - OPTIMIZED FOR PERFORMANCE
function PollutionCloud({ position, aqi, size = 30 }) {
  const cloudRef = useRef()
  
  const color = useMemo(() => {
    if (aqi > 300) return '#dc2626' // Red - Hazardous
    if (aqi > 200) return '#f97316' // Orange - Very Poor
    if (aqi > 150) return '#fb923c' // Light Orange - Poor
    return '#fbbf24' // Yellow - Moderate
  }, [aqi])
  
  const opacity = useMemo(() => {
    return Math.min(0.25, (aqi - 100) / 600) // Further reduced opacity
  }, [aqi])
  
  useFrame((state) => {
    if (cloudRef.current) {
      // Very slow rotation - skip every other frame
      if (state.clock.elapsedTime % 2 < 1) {
        cloudRef.current.rotation.y = state.clock.elapsedTime * 0.01
      }
    }
  })
  
  return (
    <Sphere
      ref={cloudRef}
      args={[size, 12, 12]} // Further reduced geometry
      position={position}
    >
      <meshBasicMaterial // Basic material for better performance
        color={color}
        transparent
        opacity={opacity}
        depthWrite={false}
      />
    </Sphere>
  )
}

// Ground-level haze layer
function HazeLayer({ position, aqi, size = 60 }) {
  const hazeRef = useRef()
  
  const color = useMemo(() => {
    if (aqi > 250) return '#ef4444'
    if (aqi > 200) return '#fb923c'
    return '#fbbf24'
  }, [aqi])
  
  const opacity = useMemo(() => {
    return Math.min(0.6, (aqi - 100) / 300)
  }, [aqi])
  
  useFrame((state) => {
    if (hazeRef.current) {
      // Slow undulation
      hazeRef.current.position.y = 8 + Math.sin(state.clock.elapsedTime * 0.2) * 1
    }
  })
  
  return (
    <mesh
      ref={hazeRef}
      position={[position[0], 8, position[2]]}
      rotation={[-Math.PI / 2, 0, 0]}
    >
      <planeGeometry args={[size, size, 32, 32]} />
      <meshStandardMaterial
        color={color}
        transparent
        opacity={opacity}
        emissive={color}
        emissiveIntensity={0.4}
        side={THREE.DoubleSide}
      />
    </mesh>
  )
}

// Individual floating smoke particle - OPTIMIZED
function SmokeParticle({ position, size, color, delay = 0 }) {
  const particleRef = useRef()
  
  useFrame((state) => {
    if (particleRef.current) {
      const time = state.clock.elapsedTime + delay
      // Simple float up
      particleRef.current.position.y = position[1] + (time % 5) * 2
      // Fade out as it rises
      const life = (time % 5) / 5
      particleRef.current.material.opacity = (1 - life) * 0.3
    }
  })
  
  return (
    <Sphere
      ref={particleRef}
      args={[size, 8, 8]} // Reduced geometry
      position={position}
    >
      <meshBasicMaterial // Changed to basic for performance
        color={color}
        transparent
        opacity={0.3}
        depthWrite={false}
      />
    </Sphere>
  )
}

// AQI Indicator floating above zone
function AQIIndicator({ position, aqi, zoneName }) {
  const color = useMemo(() => {
    if (aqi > 300) return 'rgba(220, 38, 38, 0.95)' // Red
    if (aqi > 250) return 'rgba(249, 115, 22, 0.95)' // Orange
    if (aqi > 200) return 'rgba(251, 146, 60, 0.95)' // Light Orange
    if (aqi > 150) return 'rgba(251, 191, 36, 0.95)' // Yellow
    return 'rgba(34, 197, 94, 0.95)' // Green
  }, [aqi])
  
  const status = useMemo(() => {
    if (aqi > 300) return '☠️ HAZARDOUS'
    if (aqi > 250) return '🆘 SEVERE'
    if (aqi > 200) return '⚠️ VERY POOR'
    if (aqi > 150) return '😷 POOR'
    return '✅ MODERATE'
  }, [aqi])
  
  return (
    <Html
      position={[position[0], 38, position[2]]}
      center
      distanceFactor={15}
    >
      <div style={{
        background: color,
        padding: '12px 24px',
        borderRadius: '25px',
        fontSize: '20px',
        fontWeight: 'bold',
        color: 'white',
        border: '4px solid white',
        boxShadow: '0 0 30px rgba(0,0,0,0.7), 0 0 60px ' + color,
        textAlign: 'center',
        minWidth: '140px',
        animation: 'pulse 2s infinite'
      }}>
        <div style={{ fontSize: '14px', opacity: 0.9, marginBottom: '5px' }}>
          {zoneName}
        </div>
        <div style={{ fontSize: '32px', fontWeight: '900' }}>
          {aqi}
        </div>
        <div style={{ fontSize: '16px', marginTop: '5px', opacity: 0.95 }}>
          {status}
        </div>
      </div>
      <style>{`
        @keyframes pulse {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.05); }
        }
      `}</style>
    </Html>
  )
}

// Traffic pollution indicator - shows pollution from roads
function TrafficPollution({ startPos, endPos, density = 0.6 }) {
  const particles = useMemo(() => {
    const count = Math.floor(density * 10)
    return Array.from({ length: count }, (_, i) => {
      const t = i / count
      return {
        id: i,
        position: [
          startPos[0] + (endPos[0] - startPos[0]) * t + (Math.random() - 0.5) * 5,
          2 + Math.random() * 3,
          startPos[2] + (endPos[2] - startPos[2]) * t + (Math.random() - 0.5) * 5
        ],
        size: 0.5 + Math.random() * 1,
        delay: Math.random() * 5
      }
    })
  }, [startPos, endPos, density])
  
  return (
    <group>
      {particles.map(particle => (
        <SmokeParticle
          key={particle.id}
          position={particle.position}
          size={particle.size}
          color="#8b5cf6"
          delay={particle.delay}
        />
      ))}
    </group>
  )
}

// Main pollution visualization component
function PollutionVisualization({ zones, cityLayout }) {
  return (
    <group>
      {/* Zone-based pollution */}
      {zones.map((zone, idx) => {
        if (zone.aqi < 100) return null // No visualization for good air quality
        
        const position = cityLayout[idx]?.position || [0, 0, 0]
        const particleCount = Math.floor(zone.aqi / 15) // More particles for worse AQI
        
        return (
          <group key={`zone-pollution-${idx}`}>
            {/* Large animated pollution cloud */}
            <PollutionCloud position={[position[0], 15, position[2]]} aqi={zone.aqi} />
            
            {/* Ground-level haze */}
            <HazeLayer position={position} aqi={zone.aqi} />
            
            {/* Floating smoke particles - REDUCED COUNT */}
            {Array.from({ length: Math.min(5, Math.floor(particleCount / 3)) }).map((_, i) => (
              <SmokeParticle
                key={i}
                position={[
                  position[0] + (Math.random() - 0.5) * 30,
                  5 + Math.random() * 15,
                  position[2] + (Math.random() - 0.5) * 30
                ]}
                size={2 + Math.random()}
                color={zone.aqi > 250 ? '#dc2626' : zone.aqi > 200 ? '#f97316' : '#fbbf24'}
                delay={Math.random() * 5}
              />
            ))}
            
            {/* AQI Indicator */}
            <AQIIndicator
              position={position}
              aqi={zone.aqi}
              zoneName={zone.name || `Zone ${zone.id}`}
            />
            
            {/* Removed extra severe pollution effect for performance */}
          </group>
        )
      })}
      
      {/* Traffic-related pollution - REDUCED */}
      <TrafficPollution startPos={[-100, 0, 0]} endPos={[100, 0, 0]} density={0.3} />
      <TrafficPollution startPos={[0, 0, -100]} endPos={[0, 0, 100]} density={0.3} />
      
      {/* Pollution legend in 3D space */}
      <Html position={[-90, 50, -90]} center distanceFactor={20}>
        <div style={{
          background: 'rgba(0, 0, 0, 0.85)',
          backdropFilter: 'blur(10px)',
          padding: '15px 20px',
          borderRadius: '15px',
          border: '2px solid rgba(255, 255, 255, 0.3)',
          minWidth: '200px'
        }}>
          <div style={{ color: 'white', fontSize: '16px', fontWeight: 'bold', marginBottom: '10px' }}>
            🌫️ AIR QUALITY
          </div>
          <div style={{ color: '#10b981', fontSize: '14px', marginBottom: '5px' }}>
            ✅ Good: 0-100
          </div>
          <div style={{ color: '#fbbf24', fontSize: '14px', marginBottom: '5px' }}>
            😷 Moderate: 100-150
          </div>
          <div style={{ color: '#fb923c', fontSize: '14px', marginBottom: '5px' }}>
            ⚠️ Poor: 150-200
          </div>
          <div style={{ color: '#f97316', fontSize: '14px', marginBottom: '5px' }}>
            🆘 Very Poor: 200-300
          </div>
          <div style={{ color: '#dc2626', fontSize: '14px' }}>
            ☠️ Hazardous: 300+
          </div>
        </div>
      </Html>
    </group>
  )
}

export default PollutionVisualization
