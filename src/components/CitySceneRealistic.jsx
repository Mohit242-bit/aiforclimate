import React, { useRef, useMemo, useState, useEffect } from 'react'
import { useFrame, useLoader } from '@react-three/fiber'
import { Box, Sphere, Plane, Text, Cloud, Sky, Stars, Float } from '@react-three/drei'
import * as THREE from 'three'
import { useSimulationStore } from '../store/simulationStore'

// Realistic building with detailed architecture
function RealisticBuilding({ position, height, width, depth, aqi, type = 'commercial' }) {
  const meshRef = useRef()
  const [hovered, setHovered] = useState(false)
  
  // Color based on AQI - more subtle gradients
  const buildingColor = useMemo(() => {
    if (aqi < 100) return new THREE.Color('#34d399') // Green
    if (aqi < 150) return new THREE.Color('#86efac') // Light Green
    if (aqi < 200) return new THREE.Color('#fde047') // Yellow
    if (aqi < 250) return new THREE.Color('#fbbf24') // Amber
    if (aqi < 300) return new THREE.Color('#fb923c') // Orange
    return new THREE.Color('#ef4444') // Red
  }, [aqi])
  
  const baseColor = useMemo(() => {
    const colors = {
      commercial: '#8b9dc3',
      residential: '#a8b2c1',
      office: '#94a3b8',
      industrial: '#64748b'
    }
    return colors[type] || '#94a3b8'
  }, [type])
  
  return (
    <group position={position}>
      {/* Main building structure */}
      <Box
        ref={meshRef}
        args={[width, height, depth]}
        castShadow
        receiveShadow
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
      >
        <meshStandardMaterial 
          color={hovered ? '#667eea' : baseColor}
          metalness={0.3}
          roughness={0.7}
        />
      </Box>
      
      {/* Building top - AQI indicator */}
      <Box
        position={[0, height/2 + 0.5, 0]}
        args={[width * 0.8, 1, depth * 0.8]}
      >
        <meshStandardMaterial
          color={buildingColor}
          emissive={buildingColor}
          emissiveIntensity={0.3}
        />
      </Box>
      
      {/* Windows grid */}
      {Array.from({ length: Math.floor(height / 4) }).map((_, floorIndex) => (
        <group key={floorIndex}>
          {Array.from({ length: Math.floor(width / 2) }).map((_, windowIndex) => (
            <Box
              key={`${floorIndex}-${windowIndex}`}
              position={[
                -width/2 + 1 + windowIndex * 2,
                -height/2 + 2 + floorIndex * 4,
                depth/2 + 0.01
              ]}
              args={[1.2, 2, 0.1]}
            >
              <meshStandardMaterial
                color="#1e293b"
                metalness={0.8}
                roughness={0.2}
                emissive={aqi > 200 ? '#fbbf24' : '#60a5fa'}
                emissiveIntensity={0.2}
              />
            </Box>
          ))}
        </group>
      ))}
      
      {/* Rooftop details */}
      <Box position={[width * 0.3, height/2 + 1, depth * 0.3]} args={[1, 2, 1]}>
        <meshStandardMaterial color="#475569" />
      </Box>
      <Box position={[-width * 0.3, height/2 + 0.5, -depth * 0.3]} args={[2, 1, 2]}>
        <meshStandardMaterial color="#475569" />
      </Box>
    </group>
  )
}

// Straight road segment with lane markings (used for connectors)
function Road({ start, end, width = 4 }) {
  const length = Math.sqrt(
    Math.pow(end[0] - start[0], 2) + 
    Math.pow(end[2] - start[2], 2)
  )
  const angle = Math.atan2(end[2] - start[2], end[0] - start[0])
  const midpoint = [
    (start[0] + end[0]) / 2,
    0.01,
    (start[2] + end[2]) / 2
  ]
  
  return (
    <group position={midpoint} rotation={[0, angle, 0]}>
      {/* Road surface */}
      <Box args={[length, 0.05, width]}>
        <meshStandardMaterial color="#1e293b" roughness={0.9} />
      </Box>
      {/* Center lane marking */}
      <Box position={[0, 0.06, 0]} args={[length, 0.01, 0.2]}>
        <meshStandardMaterial color="#fbbf24" emissive="#fbbf24" emissiveIntensity={0.2} />
      </Box>
      {/* Side markings */}
      <Box position={[0, 0.06, width/2 - 0.2]} args={[length, 0.01, 0.1]}>
        <meshStandardMaterial color="#ffffff" />
      </Box>
      <Box position={[0, 0.06, -width/2 + 0.2]} args={[length, 0.01, 0.1]}>
        <meshStandardMaterial color="#ffffff" />
      </Box>
    </group>
  )
}

// Path-based road rendered as many thin boxes to follow curves
function PathRoad({ curve, width = 6, segments = 64 }) {
  const points = useMemo(() => curve.getSpacedPoints(segments), [curve, segments])
  const roadSegments = []
  for (let i = 0; i < points.length - 1; i++) {
    const p1 = points[i]
    const p2 = points[i + 1]
    const dx = p2.x - p1.x
    const dz = p2.z - p1.z
    const len = Math.sqrt(dx*dx + dz*dz)
    const angle = Math.atan2(dz, dx)
    const mid = [(p1.x + p2.x)/2, 0.01, (p1.z + p2.z)/2]
    roadSegments.push({ mid, len, angle })
  }
  return (
    <group>
      {roadSegments.map((seg, i) => (
        <group key={i} position={seg.mid} rotation={[0, seg.angle, 0]}>
          <Box args={[seg.len, 0.05, width]}>
            <meshStandardMaterial color="#1e293b" roughness={0.95} />
          </Box>
          <Box position={[0, 0.06, 0]} args={[seg.len, 0.01, 0.15]}>
            <meshStandardMaterial color="#fbbf24" emissive="#fbbf24" emissiveIntensity={0.15} />
          </Box>
        </group>
      ))}
    </group>
  )
}

// Animated vehicles
function Vehicle({ path, speed = 1, color = '#ef4444' }) {
  const meshRef = useRef()
  const progress = useRef(Math.random())
  
  useFrame((state, delta) => {
    if (meshRef.current) {
      progress.current = (progress.current + delta * speed * 0.1) % 1
      const point = path.getPointAt(progress.current)
      meshRef.current.position.set(point.x, 0.3, point.z)
      
      // Orient vehicle along path
      const tangent = path.getTangentAt(progress.current)
      meshRef.current.lookAt(
        point.x + tangent.x,
        0.3,
        point.z + tangent.z
      )
    }
  })
  
  return (
    <group ref={meshRef}>
      {/* Vehicle body */}
      <Box args={[1, 0.4, 0.5]} castShadow>
        <meshStandardMaterial color={color} metalness={0.6} roughness={0.4} />
      </Box>
      {/* Headlights */}
      <Sphere args={[0.05]} position={[0.5, 0, 0.2]}>
        <meshStandardMaterial emissive="#ffffff" emissiveIntensity={1} />
      </Sphere>
      <Sphere args={[0.05]} position={[0.5, 0, -0.2]}>
        <meshStandardMaterial emissive="#ffffff" emissiveIntensity={1} />
      </Sphere>
    </group>
  )
}

// Pollution visualization with volumetric effect
function PollutionCloud({ position, intensity, radius = 15 }) {
  const cloudRef = useRef()
  const particlesRef = useRef()
  
  useFrame((state) => {
    if (cloudRef.current) {
      // Gentle rotation for realistic cloud movement
      cloudRef.current.rotation.y = state.clock.elapsedTime * 0.02
      // Subtle pulsing
      const pulse = 1 + Math.sin(state.clock.elapsedTime * 0.5) * 0.05
      cloudRef.current.scale.setScalar(pulse)
    }
  })
  
  const color = useMemo(() => {
    if (intensity < 0.3) return new THREE.Color('#10b981')
    if (intensity < 0.6) return new THREE.Color('#f59e0b')
    return new THREE.Color('#dc2626')
  }, [intensity])
  
  // Create particle system for more realistic pollution
  const particles = useMemo(() => {
    const temp = []
    for (let i = 0; i < 50; i++) {
      const angle = (i / 50) * Math.PI * 2
      const r = radius * (0.5 + Math.random() * 0.5)
      temp.push({
        position: [
          Math.cos(angle) * r,
          Math.random() * 10,
          Math.sin(angle) * r
        ],
        size: 0.5 + Math.random() * 1
      })
    }
    return temp
  }, [radius])
  
  return (
    <group position={position} ref={cloudRef}>
      {/* Main pollution cloud */}
      <Sphere args={[radius, 16, 16]}>
        <meshStandardMaterial
          color={color}
          transparent
          opacity={intensity * 0.2}
          depthWrite={false}
        />
      </Sphere>
      
      {/* Particle effects */}
      {particles.map((particle, i) => (
        <Sphere
          key={i}
          position={particle.position}
          args={[particle.size]}
        >
          <meshStandardMaterial
            color={color}
            transparent
            opacity={intensity * 0.15}
            depthWrite={false}
          />
        </Sphere>
      ))}
    </group>
  )
}

// Realistic park with trees and grass
function Park({ position, size }) {
  return (
    <group position={position}>
      {/* Grass field */}
      <Plane args={[size, size]} rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <meshStandardMaterial color="#22c55e" roughness={1} />
      </Plane>
      
      {/* Trees in natural arrangement */}
      {Array.from({ length: 8 }).map((_, i) => {
        const angle = (i / 8) * Math.PI * 2 + Math.random() * 0.5
        const distance = size * 0.3 + Math.random() * size * 0.2
        return (
          <group 
            key={i} 
            position={[
              Math.cos(angle) * distance,
              0,
              Math.sin(angle) * distance
            ]}
          >
            {/* Tree trunk */}
            <Box args={[0.8, 4, 0.8]} position={[0, 2, 0]} castShadow>
              <meshStandardMaterial color="#8b4513" roughness={1} />
            </Box>
            {/* Tree crown - multiple spheres for realism */}
            <Sphere position={[0, 5, 0]} args={[2.5]} castShadow>
              <meshStandardMaterial color="#065f46" roughness={0.8} />
            </Sphere>
            <Sphere position={[1, 5.5, 0]} args={[2]} castShadow>
              <meshStandardMaterial color="#047857" roughness={0.8} />
            </Sphere>
            <Sphere position={[-1, 5.5, 0]} args={[2]} castShadow>
              <meshStandardMaterial color="#059669" roughness={0.8} />
            </Sphere>
          </group>
        )
      })}
      
      {/* Park benches */}
      {[0, 90, 180, 270].map((rotation, i) => (
        <Box
          key={i}
          position={[
            Math.cos(rotation * Math.PI / 180) * size * 0.4,
            0.3,
            Math.sin(rotation * Math.PI / 180) * size * 0.4
          ]}
          args={[2, 0.6, 0.8]}
          rotation={[0, rotation * Math.PI / 180, 0]}
        >
          <meshStandardMaterial color="#7c3aed" />
        </Box>
      ))}
      
      {/* Walking path */}
      <Plane 
        args={[size * 0.8, 1]} 
        rotation={[-Math.PI / 2, 0, 0]} 
        position={[0, 0.02, 0]}
      >
        <meshStandardMaterial color="#cbd5e1" roughness={1} />
      </Plane>
    </group>
  )
}

// Delhi monument landmarks
function Landmark({ type, position }) {
  if (type === 'india-gate') {
    return (
      <group position={position}>
        {/* Simplified India Gate */}
        <Box args={[15, 20, 3]} position={[0, 10, 0]} castShadow>
          <meshStandardMaterial color="#dc9f5f" metalness={0.2} roughness={0.8} />
        </Box>
        <Box args={[8, 12, 4]} position={[0, 6, 0]}>
          <meshStandardMaterial color="#1e293b" />
        </Box>
      </group>
    )
  }
  
  if (type === 'metro') {
    return (
      <group position={position}>
        {/* Metro station */}
        <Box args={[10, 3, 20]} position={[0, 1.5, 0]} castShadow>
          <meshStandardMaterial color="#3b82f6" metalness={0.6} roughness={0.3} />
        </Box>
        <Box args={[1, 8, 1]} position={[-4, 4, -8]} castShadow>
          <meshStandardMaterial color="#64748b" />
        </Box>
        <Box args={[1, 8, 1]} position={[4, 4, -8]} castShadow>
          <meshStandardMaterial color="#64748b" />
        </Box>
      </group>
    )
  }
  
  return null
}

// Stubble burning smoke plume from northwest
function StubbleBurningPlume({ intensity = 0.8, active = true }) {
  const plumeRef = useRef()
  const cloudsRef = useRef([])
  
  useFrame((state) => {
    if (!active || !plumeRef.current) return
    
    // Animate plume drifting from NW to SE
    const time = state.clock.elapsedTime
    plumeRef.current.position.x = -120 + Math.sin(time * 0.05) * 10 + time * 0.5
    plumeRef.current.position.z = -100 + Math.cos(time * 0.03) * 5 + time * 0.3
    
    // Reset position when it drifts too far
    if (plumeRef.current.position.x > 50) {
      plumeRef.current.position.x = -120
      plumeRef.current.position.z = -100
    }
    
    // Subtle rotation for realistic smoke movement
    plumeRef.current.rotation.y = Math.sin(time * 0.02) * 0.1
  })
  
  if (!active) return null
  
  return (
    <group ref={plumeRef} position={[-120, 15, -100]}>
      {/* Main smoke cloud using drei Cloud */}
      <Cloud
        opacity={intensity * 0.4}
        speed={0.4}
        width={80}
        depth={60}
        segments={20}
      >
        <meshLambertMaterial color="#8b7355" />
      </Cloud>
      
      {/* Additional volumetric smoke layers */}
      {[0, 20, 40].map((offset, i) => (
        <group key={i} position={[offset, i * 5, offset * 0.5]}>
          <Sphere args={[25 + i * 10, 16, 16]}>
            <meshStandardMaterial
              color={i === 0 ? '#8b6914' : '#a0826d'}
              transparent
              opacity={intensity * (0.3 - i * 0.05)}
              depthWrite={false}
            />
          </Sphere>
          
          {/* Particle effects for smoke */}
          {Array.from({ length: 15 }).map((_, j) => {
            const angle = (j / 15) * Math.PI * 2
            const radius = 20 + i * 8 + Math.random() * 10
            return (
              <Sphere
                key={j}
                position={[
                  Math.cos(angle) * radius,
                  Math.random() * 10 - 5,
                  Math.sin(angle) * radius
                ]}
                args={[3 + Math.random() * 2]}
              >
                <meshStandardMaterial
                  color="#8b7355"
                  transparent
                  opacity={intensity * 0.2}
                  depthWrite={false}
                />
              </Sphere>
            )
          })}
        </group>
      ))}
      
      {/* Ground-level haze */}
      <Plane args={[100, 80]} rotation={[-Math.PI / 2, 0, Math.PI / 4]} position={[20, 0, 20]}>
        <meshStandardMaterial
          color="#8b6914"
          transparent
          opacity={intensity * 0.15}
          depthWrite={false}
          side={THREE.DoubleSide}
        />
      </Plane>
      
      {/* Warning text */}
      <Text
        position={[0, 40, 0]}
        fontSize={3}
        color="#ff6b6b"
        anchorX="center"
        anchorY="middle"
        outlineWidth={0.3}
        outlineColor="black"
      >
        STUBBLE BURNING SMOKE
      </Text>
      <Text
        position={[0, 36, 0]}
        fontSize={1.5}
        color="#fbbf24"
        anchorX="center"
        anchorY="middle"
      >
        Wind: NW → SE | PM2.5 +200
      </Text>
    </group>
  )
}

// Main realistic city scene
function CitySceneRealistic() {
  const { zones, currentIntervention, time } = useSimulationStore()
  const [stubbleBurning, setStubbleBurning] = useState(false)
  
  // Check if it's stubble burning season (Oct-Nov) or if crisis mode
  useEffect(() => {
    const avgAQI = zones.reduce((sum, z) => sum + z.aqi, 0) / zones.length
    const crisis = avgAQI > 300
    const currentMonth = new Date().getMonth()
    const isStubbleSeason = currentMonth === 9 || currentMonth === 10 // Oct-Nov
    setStubbleBurning(crisis || isStubbleSeason)
  }, [zones])
  
  // Delhi zones with realistic layout
  const zoneLayout = [
    { 
      id: 1, 
      name: 'Connaught Place', 
      position: [0, 0, 0], 
      buildings: [
        { pos: [5, 0, 5], height: 25, width: 4, depth: 4, type: 'commercial' },
        { pos: [-5, 0, 5], height: 30, width: 5, depth: 4, type: 'office' },
        { pos: [5, 0, -5], height: 20, width: 4, depth: 5, type: 'commercial' },
        { pos: [-5, 0, -5], height: 35, width: 6, depth: 5, type: 'office' },
        { pos: [10, 0, 0], height: 28, width: 4, depth: 4, type: 'commercial' },
        { pos: [-10, 0, 0], height: 22, width: 4, depth: 4, type: 'commercial' },
        { pos: [0, 0, 10], height: 26, width: 5, depth: 4, type: 'office' },
        { pos: [0, 0, -10], height: 32, width: 5, depth: 5, type: 'office' }
      ]
    },
    { 
      id: 2, 
      name: 'Karol Bagh', 
      position: [-40, 0, -30],
      buildings: [
        { pos: [3, 0, 3], height: 15, width: 3, depth: 3, type: 'residential' },
        { pos: [-3, 0, 3], height: 18, width: 3, depth: 3, type: 'residential' },
        { pos: [3, 0, -3], height: 12, width: 3, depth: 3, type: 'residential' },
        { pos: [-3, 0, -3], height: 20, width: 4, depth: 3, type: 'commercial' },
        { pos: [7, 0, 0], height: 16, width: 3, depth: 3, type: 'residential' },
        { pos: [-7, 0, 0], height: 14, width: 3, depth: 3, type: 'residential' }
      ]
    },
    { 
      id: 3, 
      name: 'Dwarka', 
      position: [50, 0, -40],
      buildings: [
        { pos: [4, 0, 4], height: 22, width: 4, depth: 4, type: 'residential' },
        { pos: [-4, 0, 4], height: 25, width: 4, depth: 4, type: 'residential' },
        { pos: [4, 0, -4], height: 20, width: 4, depth: 4, type: 'residential' },
        { pos: [-4, 0, -4], height: 28, width: 5, depth: 4, type: 'commercial' },
        { pos: [8, 0, 0], height: 24, width: 4, depth: 4, type: 'residential' },
        { pos: [-8, 0, 0], height: 26, width: 4, depth: 4, type: 'residential' },
        { pos: [0, 0, 8], height: 30, width: 5, depth: 4, type: 'office' },
        { pos: [0, 0, -8], height: 18, width: 4, depth: 4, type: 'residential' },
        { pos: [12, 0, 6], height: 21, width: 3, depth: 3, type: 'residential' },
        { pos: [-12, 0, -6], height: 19, width: 3, depth: 3, type: 'residential' }
      ]
    },
    { 
      id: 4, 
      name: 'Rohini', 
      position: [-50, 0, 30],
      buildings: [
        { pos: [3, 0, 3], height: 18, width: 3, depth: 3, type: 'residential' },
        { pos: [-3, 0, 3], height: 16, width: 3, depth: 3, type: 'residential' },
        { pos: [3, 0, -3], height: 20, width: 4, depth: 3, type: 'commercial' },
        { pos: [-3, 0, -3], height: 15, width: 3, depth: 3, type: 'residential' },
        { pos: [6, 0, 0], height: 22, width: 4, depth: 4, type: 'residential' },
        { pos: [-6, 0, 0], height: 17, width: 3, depth: 3, type: 'residential' },
        { pos: [0, 0, 6], height: 19, width: 3, depth: 3, type: 'residential' }
      ]
    },
    { 
      id: 5, 
      name: 'Saket', 
      position: [40, 0, 30],
      buildings: [
        { pos: [4, 0, 4], height: 28, width: 5, depth: 4, type: 'commercial' },
        { pos: [-4, 0, 4], height: 24, width: 4, depth: 4, type: 'office' },
        { pos: [4, 0, -4], height: 20, width: 4, depth: 4, type: 'commercial' },
        { pos: [-4, 0, -4], height: 26, width: 4, depth: 4, type: 'residential' },
        { pos: [8, 0, 0], height: 30, width: 5, depth: 5, type: 'office' }
      ]
    }
  ]
  
// Create ring road and radial paths for vehicles and roads
  const { ringPaths, radialPaths } = useMemo(() => {
    // Helper to build a closed ring (approx ring road) as CatmullRomCurve3
    const makeRing = (radiusX, radiusZ, points = 16) => {
      const pts = []
      for (let i = 0; i < points; i++) {
        const t = (i / points) * Math.PI * 2
        pts.push(new THREE.Vector3(Math.cos(t) * radiusX, 0, Math.sin(t) * radiusZ))
      }
      // Close loop by repeating first few points
      pts.push(pts[0].clone())
      return new THREE.CatmullRomCurve3(pts, true, 'centripetal')
    }
    const outerRing = makeRing(80, 65, 24)
    const innerRing = makeRing(55, 45, 20)

    // Radial paths from outer ring to center
    const radials = [0, Math.PI/4, Math.PI/2, (3*Math.PI)/4, Math.PI, (5*Math.PI)/4, (3*Math.PI)/2, (7*Math.PI)/4].map(theta => {
      const start = new THREE.Vector3(Math.cos(theta) * 80, 0, Math.sin(theta) * 65)
      const end = new THREE.Vector3(0, 0, 0)
      return new THREE.CatmullRomCurve3([start, new THREE.Vector3(Math.cos(theta)*40, 0, Math.sin(theta)*32), end], false, 'centripetal')
    })

    return { ringPaths: [outerRing, innerRing], radialPaths: radials }
  }, [])
  
  // Calculate if it's day or night based on time
  const isDayTime = time >= 6 && time <= 18
  
  return (
    <group>
      {/* Sky and atmosphere */}
      <Sky
        distance={450000}
        sunPosition={[0, isDayTime ? 1 : -1, 0]}
        inclination={isDayTime ? 0 : 1}
        azimuth={0.25}
      />
      
      {!isDayTime && <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade />}
      
      {/* Ground with texture */}
      <Plane 
        args={[300, 300]} 
        rotation={[-Math.PI / 2, 0, 0]} 
        position={[0, -0.1, 0]}
        receiveShadow
      >
        <meshStandardMaterial color="#1e293b" roughness={1} />
      </Plane>
      
      {/* Ring roads rendered along curves */}
      {ringPaths.map((curve, i) => (
        <PathRoad key={`ring-${i}`} curve={curve} width={i === 0 ? 10 : 8} segments={96} />
      ))}

      {/* Radial roads to center */}
      {radialPaths.map((curve, i) => (
        <PathRoad key={`radial-${i}`} curve={curve} width={6} segments={40} />
      ))}
      
      {/* Zones with buildings */}
      {zoneLayout.map((zone) => {
        const zoneData = zones.find(z => z.id === zone.id) || { aqi: 150 }
        
        return (
          <group key={zone.id} position={zone.position}>
            {/* Zone name display */}
            <Text
              position={[0, 40, 0]}
              fontSize={3}
              color="white"
              anchorX="center"
              anchorY="middle"
              outlineWidth={0.2}
              outlineColor="black"
            >
              {zone.name}
            </Text>
            
            {/* Zone AQI display */}
            <Text
              position={[0, 36, 0]}
              fontSize={2}
              color={zoneData.aqi > 200 ? '#ef4444' : '#fbbf24'}
              anchorX="center"
              anchorY="middle"
            >
              AQI: {Math.round(zoneData.aqi)}
            </Text>
            
            {/* Buildings in zone */}
            {zone.buildings.map((building, i) => (
              <RealisticBuilding
                key={`${zone.id}-${i}`}
                position={building.pos}
                height={building.height}
                width={building.width}
                depth={building.depth}
                aqi={zoneData.aqi}
                type={building.type}
              />
            ))}
            
            {/* Pollution cloud - positioned higher and more transparent */}
            {zoneData.aqi > 150 && (
              <PollutionCloud
                position={[0, 25, 0]}
                intensity={Math.min(zoneData.aqi / 500, 1)}
                radius={20}
              />
            )}
            
            {/* Parks for green intervention */}
            {currentIntervention?.type === 'green_cover' && 
             currentIntervention.zones.includes(zone.id) && (
              <Park position={[15, 0, 15]} size={12} />
            )}
          </group>
        )
      })}
      
      {/* Traffic vehicles on ring roads */}
      {ringPaths.map((path, i) => (
        <group key={`traffic-ring-${i}`}>
          {Array.from({ length: 12 }).map((_, j) => (
            <Vehicle
              key={`vehicle-ring-${i}-${j}`}
              path={path}
              speed={0.6 + Math.random() * 0.6}
              color={['#ef4444', '#3b82f6', '#fbbf24', '#10b981'][(i + j) % 4]}
            />
          ))}
        </group>
      ))}

      {/* Traffic vehicles on radials */}
      {radialPaths.map((path, i) => (
        <group key={`traffic-radial-${i}`}>
          {Array.from({ length: 4 }).map((_, j) => (
            <Vehicle
              key={`vehicle-radial-${i}-${j}`}
              path={path}
              speed={0.5 + Math.random() * 0.3}
              color={['#ef4444', '#3b82f6', '#fbbf24', '#10b981'][(i + j) % 4]}
            />
          ))}
        </group>
      ))}
      
      {/* Stubble burning plume from Punjab (Northwest) */}
      <StubbleBurningPlume 
        active={stubbleBurning} 
        intensity={stubbleBurning ? 0.8 : 0.3}
      />
      
      {/* Landmarks */}
      <Landmark type="india-gate" position={[0, 0, -50]} />
      <Landmark type="metro" position={[-30, 0, 20]} />
      
      {/* Directional lights for realistic shadows */}
      <directionalLight
        position={[50, 50, 25]}
        intensity={isDayTime ? 1 : 0.3}
        castShadow
        shadow-mapSize={[2048, 2048]}
        shadow-camera-left={-100}
        shadow-camera-right={100}
        shadow-camera-top={100}
        shadow-camera-bottom={-100}
      />
      
      {/* Ambient lighting */}
      <ambientLight intensity={isDayTime ? 0.5 : 0.1} />
      
      {/* Street lights for night time */}
      {!isDayTime && (
        <>
          {[-40, 0, 40].map((x) => 
            [-40, 0, 40].map((z) => (
              <pointLight
                key={`street-${x}-${z}`}
                position={[x, 8, z]}
                intensity={0.5}
                color="#fbbf24"
                distance={20}
              />
            ))
          )}
        </>
      )}
    </group>
  )
}

export default CitySceneRealistic
