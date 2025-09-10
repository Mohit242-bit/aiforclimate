import React, { useRef, useMemo, useEffect, useState } from 'react'
import { useFrame } from '@react-three/fiber'
import { Box, Sphere, Plane, Text } from '@react-three/drei'
import * as THREE from 'three'
import { useSimulationStore } from '../store/simulationStore'

// Single building component
function Building({ position, height, width, depth, color, aqi }) {
  const meshRef = useRef()
  const [hovered, setHovered] = useState(false)
  
  // Remove the animation that makes buildings move
  // Buildings should be static and solid
  
  // Color based on AQI
  const buildingColor = useMemo(() => {
    if (aqi < 100) return '#4ade80' // Green
    if (aqi < 200) return '#facc15' // Yellow
    if (aqi < 300) return '#fb923c' // Orange
    return '#ef4444' // Red
  }, [aqi])
  
  return (
    <group position={position}>
      <Box
        ref={meshRef}
        args={[width, height, depth]}
        castShadow
        receiveShadow
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
      >
        <meshStandardMaterial 
          color={hovered ? '#667eea' : buildingColor}
          metalness={0.5}
          roughness={0.5}
          emissive={buildingColor}
          emissiveIntensity={hovered ? 0.5 : 0.1}
        />
      </Box>
      
      {/* Windows */}
      {Array.from({ length: Math.floor(height / 3) }).map((_, i) => (
        <Box
          key={i}
          position={[width / 2 + 0.01, -height / 2 + 2 + i * 3, 0]}
          args={[0.02, 1.5, depth * 0.8]}
        >
          <meshStandardMaterial
            color="#ffffff"
            emissive="#ffffff"
            emissiveIntensity={0.5}
            opacity={0.8}
            transparent
          />
        </Box>
      ))}
    </group>
  )
}

// Traffic particles
function TrafficFlow({ start, end, density = 10 }) {
  const particlesRef = useRef()
  const particles = useMemo(() => {
    return Array.from({ length: density }, () => ({
      position: new THREE.Vector3(
        start[0] + Math.random() * (end[0] - start[0]),
        0.5,
        start[2] + Math.random() * (end[2] - start[2])
      ),
      velocity: Math.random() * 0.5 + 0.5
    }))
  }, [start, end, density])
  
  useFrame((state) => {
    if (particlesRef.current) {
      particles.forEach((particle, i) => {
        particle.position.x += (end[0] - start[0]) * 0.01 * particle.velocity
        particle.position.z += (end[2] - start[2]) * 0.01 * particle.velocity
        
        // Reset position when reaching end
        if (Math.abs(particle.position.x - end[0]) < 1) {
          particle.position.x = start[0]
          particle.position.z = start[2]
        }
      })
    }
  })
  
  return (
    <group ref={particlesRef}>
      {particles.map((particle, i) => (
        <Sphere key={i} position={[particle.position.x, particle.position.y, particle.position.z]} args={[0.2]}>
          <meshStandardMaterial color="#fbbf24" emissive="#fbbf24" emissiveIntensity={0.5} />
        </Sphere>
      ))}
    </group>
  )
}

// Pollution cloud
function PollutionCloud({ position, intensity, radius = 10 }) {
  const cloudRef = useRef()
  
  useFrame((state) => {
    if (cloudRef.current) {
      cloudRef.current.rotation.y = state.clock.elapsedTime * 0.05
      cloudRef.current.scale.x = 1 + Math.sin(state.clock.elapsedTime * 0.5) * 0.1
      cloudRef.current.scale.z = 1 + Math.cos(state.clock.elapsedTime * 0.5) * 0.1
    }
  })
  
  const color = useMemo(() => {
    if (intensity < 0.3) return '#10b981'
    if (intensity < 0.6) return '#f59e0b'
    return '#ef4444'
  }, [intensity])
  
  return (
    <Sphere
      ref={cloudRef}
      position={position}
      args={[radius, 32, 32]}
    >
      <meshStandardMaterial
        color={color}
        transparent
        opacity={intensity * 0.3}
        depthWrite={false}
      />
    </Sphere>
  )
}

// Green spaces
function Park({ position, size }) {
  return (
    <group position={position}>
      <Plane args={[size, size]} rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <meshStandardMaterial color="#22c55e" />
      </Plane>
      
      {/* Trees */}
      {Array.from({ length: 5 }).map((_, i) => (
        <group key={i} position={[
          (Math.random() - 0.5) * size * 0.8,
          2,
          (Math.random() - 0.5) * size * 0.8
        ]}>
          <Box args={[0.5, 3, 0.5]}>
            <meshStandardMaterial color="#7c3aed" />
          </Box>
          <Sphere position={[0, 2.5, 0]} args={[1.5]}>
            <meshStandardMaterial color="#22c55e" />
          </Sphere>
        </group>
      ))}
    </group>
  )
}

// Main city scene
function CityScene() {
  const { zones, currentIntervention } = useSimulationStore()
  
  // Delhi zones layout (simplified)
  const zonePositions = [
    { id: 1, name: 'Connaught Place', pos: [0, 0, 0], buildings: 8 },
    { id: 2, name: 'Karol Bagh', pos: [-20, 0, -20], buildings: 6 },
    { id: 3, name: 'Dwarka', pos: [30, 0, -30], buildings: 10 },
    { id: 4, name: 'Rohini', pos: [-30, 0, 20], buildings: 7 },
    { id: 5, name: 'Saket', pos: [20, 0, 20], buildings: 5 }
  ]
  
  return (
    <group>
      {/* Ground plane */}
      <Plane 
        args={[200, 200]} 
        rotation={[-Math.PI / 2, 0, 0]} 
        position={[0, -0.1, 0]}
        receiveShadow
      >
        <meshStandardMaterial color="#1a1a2e" />
      </Plane>
      
      {/* Roads grid */}
      {[-40, -20, 0, 20, 40].map((x) => (
        <Box key={`road-x-${x}`} position={[x, 0.01, 0]} args={[1, 0.02, 100]}>
          <meshStandardMaterial color="#374151" />
        </Box>
      ))}
      {[-40, -20, 0, 20, 40].map((z) => (
        <Box key={`road-z-${z}`} position={[0, 0.01, z]} args={[100, 0.02, 1]}>
          <meshStandardMaterial color="#374151" />
        </Box>
      ))}
      
      {/* Zones with buildings */}
      {zonePositions.map((zone) => {
        const zoneData = zones.find(z => z.id === zone.id) || {}
        const aqi = zoneData.aqi || 150
        
        return (
          <group key={zone.id}>
            {/* Zone label */}
            <Text
              position={[zone.pos[0], 15, zone.pos[2]]}
              fontSize={2}
              color="white"
              anchorX="center"
              anchorY="middle"
            >
              {zone.name}
            </Text>
            
            {/* Buildings in zone */}
            {Array.from({ length: zone.buildings }).map((_, i) => {
              const angle = (i / zone.buildings) * Math.PI * 2
              const radius = 8
              const height = 5 + Math.random() * 15
              
              return (
                <Building
                  key={`${zone.id}-${i}`}
                  position={[
                    zone.pos[0] + Math.cos(angle) * radius,
                    height / 2,
                    zone.pos[2] + Math.sin(angle) * radius
                  ]}
                  height={height}
                  width={2 + Math.random() * 2}
                  depth={2 + Math.random() * 2}
                  aqi={aqi}
                />
              )
            })}
            
            {/* Pollution cloud */}
            <PollutionCloud
              position={[zone.pos[0], 10, zone.pos[2]]}
              intensity={aqi / 500}
              radius={10}
            />
            
            {/* Parks (if green cover intervention) */}
            {currentIntervention?.type === 'green_cover' && currentIntervention.zones.includes(zone.id) && (
              <Park position={[zone.pos[0] + 10, 0, zone.pos[2] + 10]} size={8} />
            )}
          </group>
        )
      })}
      
      {/* Traffic flows */}
      <TrafficFlow start={[-40, 0, 0]} end={[40, 0, 0]} density={15} />
      <TrafficFlow start={[0, 0, -40]} end={[0, 0, 40]} density={15} />
      
      {/* Sun/Moon */}
      <Sphere position={[50, 50, -50]} args={[5]}>
        <meshStandardMaterial
          color="#fbbf24"
          emissive="#fbbf24"
          emissiveIntensity={2}
        />
      </Sphere>
    </group>
  )
}

export default CityScene
