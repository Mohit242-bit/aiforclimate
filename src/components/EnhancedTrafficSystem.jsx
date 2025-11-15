import React, { useRef, useMemo, useEffect } from 'react'
import { useFrame } from '@react-three/fiber'
import { Box, Sphere } from '@react-three/drei'
import * as THREE from 'three'

/**
 * ENHANCED TRAFFIC SYSTEM
 * - Larger vehicles (3-4x bigger)
 * - Visible exhaust emissions
 * - Smooth movement along roads
 * - Multiple vehicle types with distinct colors
 */

// Define road paths matching the actual road network
// Main roads: 12 units wide at x=0 and z=0
// Secondary roads: 8 units wide at x/z = ±30, ±60
const ROAD_PATHS = {
  // Main East-West road (12 units wide centered at z=0)
  // Lane 1: z = +3 (northbound lane)
  mainEastWest1: {
    start: [-100, 0.8, 3],
    end: [100, 0.8, 3],
    lanes: 2,
    laneWidth: 3
  },
  // Lane 2: z = -3 (southbound lane)
  mainEastWest2: {
    start: [100, 0.8, -3],
    end: [-100, 0.8, -3],
    lanes: 2,
    laneWidth: 3
  },
  
  // Main North-South road (12 units wide centered at x=0)
  // Lane 1: x = +3 (eastbound lane)
  mainNorthSouth1: {
    start: [3, 0.8, -100],
    end: [3, 0.8, 100],
    lanes: 2,
    laneWidth: 3
  },
  // Lane 2: x = -3 (westbound lane)
  mainNorthSouth2: {
    start: [-3, 0.8, 100],
    end: [-3, 0.8, -100],
    lanes: 2,
    laneWidth: 3
  },
  
  // Secondary East-West roads (8 units wide)
  // Road at z = -60
  secondary1EW1: {
    start: [-100, 0.8, -60 + 2],
    end: [100, 0.8, -60 + 2],
    lanes: 1,
    laneWidth: 2
  },
  secondary1EW2: {
    start: [100, 0.8, -60 - 2],
    end: [-100, 0.8, -60 - 2],
    lanes: 1,
    laneWidth: 2
  },
  // Road at z = -30
  secondary2EW1: {
    start: [-100, 0.8, -30 + 2],
    end: [100, 0.8, -30 + 2],
    lanes: 1,
    laneWidth: 2
  },
  secondary2EW2: {
    start: [100, 0.8, -30 - 2],
    end: [-100, 0.8, -30 - 2],
    lanes: 1,
    laneWidth: 2
  },
  // Road at z = +30
  secondary3EW1: {
    start: [-100, 0.8, 30 + 2],
    end: [100, 0.8, 30 + 2],
    lanes: 1,
    laneWidth: 2
  },
  secondary3EW2: {
    start: [100, 0.8, 30 - 2],
    end: [-100, 0.8, 30 - 2],
    lanes: 1,
    laneWidth: 2
  },
  // Road at z = +60
  secondary4EW1: {
    start: [-100, 0.8, 60 + 2],
    end: [100, 0.8, 60 + 2],
    lanes: 1,
    laneWidth: 2
  },
  secondary4EW2: {
    start: [100, 0.8, 60 - 2],
    end: [-100, 0.8, 60 - 2],
    lanes: 1,
    laneWidth: 2
  },
  
  // Secondary North-South roads (8 units wide)
  // Road at x = -60
  secondary1NS1: {
    start: [-60 + 2, 0.8, -100],
    end: [-60 + 2, 0.8, 100],
    lanes: 1,
    laneWidth: 2
  },
  secondary1NS2: {
    start: [-60 - 2, 0.8, 100],
    end: [-60 - 2, 0.8, -100],
    lanes: 1,
    laneWidth: 2
  },
  // Road at x = -30
  secondary2NS1: {
    start: [-30 + 2, 0.8, -100],
    end: [-30 + 2, 0.8, 100],
    lanes: 1,
    laneWidth: 2
  },
  secondary2NS2: {
    start: [-30 - 2, 0.8, 100],
    end: [-30 - 2, 0.8, -100],
    lanes: 1,
    laneWidth: 2
  },
  // Road at x = +30
  secondary3NS1: {
    start: [30 + 2, 0.8, -100],
    end: [30 + 2, 0.8, 100],
    lanes: 1,
    laneWidth: 2
  },
  secondary3NS2: {
    start: [30 - 2, 0.8, 100],
    end: [30 - 2, 0.8, -100],
    lanes: 1,
    laneWidth: 2
  },
  // Road at x = +60
  secondary4NS1: {
    start: [60 + 2, 0.8, -100],
    end: [60 + 2, 0.8, 100],
    lanes: 1,
    laneWidth: 2
  },
  secondary4NS2: {
    start: [60 - 2, 0.8, 100],
    end: [60 - 2, 0.8, -100],
    lanes: 1,
    laneWidth: 2
  }
}

// Vehicle types - MUCH LARGER AND MORE VISIBLE
const VEHICLE_TYPES = {
  car: {
    size: [4.5, 2.2, 3], // Much bigger
    speed: 18,
    color: '#3b82f6', // Blue
    acceleration: 2.5,
    emission: 0.4,
    pollutionColor: '#94a3b8'
  },
  bus: {
    size: [9, 3.5, 3.5], // Much bigger
    speed: 12,
    color: '#10b981', // Green
    acceleration: 1.2,
    emission: 0.6,
    pollutionColor: '#64748b'
  },
  truck: {
    size: [8, 3.5, 3.2], // Much bigger
    speed: 10,
    color: '#f59e0b', // Amber
    acceleration: 1,
    emission: 1, // Trucks pollute most
    pollutionColor: '#8b5cf6' // Purple smoke
  },
  auto: {
    size: [3.5, 2, 2.5], // Much bigger
    speed: 15,
    color: '#fbbf24', // Yellow
    acceleration: 2,
    emission: 0.3,
    pollutionColor: '#94a3b8'
  },
  taxi: {
    size: [4.2, 2, 2.8],
    speed: 16,
    color: '#eab308', // Yellow-green (Delhi taxi)
    acceleration: 2.2,
    emission: 0.35,
    pollutionColor: '#94a3b8'
  },
  suv: {
    size: [5, 2.8, 3.2],
    speed: 17,
    color: '#6366f1', // Indigo
    acceleration: 2,
    emission: 0.5,
    pollutionColor: '#a78bfa'
  }
}

// Exhaust smoke particle - OPTIMIZED
function ExhaustSmoke({ position, color, delay = 0, emission }) {
  const smokeRef = useRef()
  
  useFrame((state) => {
    if (smokeRef.current) {
      const time = state.clock.elapsedTime + delay
      // Simple rise
      const life = (time % 2) / 2
      smokeRef.current.position.y = position[1] + life * 3
      smokeRef.current.position.x = position[0] - life * 2
      
      // Fade only
      smokeRef.current.material.opacity = (1 - life) * emission * 0.4
    }
  })
  
  return (
    <Sphere
      ref={smokeRef}
      args={[0.6, 8, 8]} // Reduced geometry
      position={position}
    >
      <meshBasicMaterial // Changed to basic for performance
        color={color}
        transparent
        opacity={0.4}
        depthWrite={false}
      />
    </Sphere>
  )
}

// Individual vehicle with exhaust
function EnhancedVehicle({ path, type = 'car', startProgress = 0, laneOffset = 0 }) {
  const meshRef = useRef()
  const progress = useRef(startProgress)
  const currentSpeed = useRef(0)
  const vehicleType = VEHICLE_TYPES[type]
  const [exhaustPosition, setExhaustPosition] = React.useState([0, 0, 0])
  
  // Calculate position along path
  const getPositionOnPath = (t) => {
    const start = new THREE.Vector3(...path.start)
    const end = new THREE.Vector3(...path.end)
    
    // Interpolate between start and end
    const position = start.lerp(end, t)
    
    // Add small lane offset (stay within lane width)
    const direction = new THREE.Vector3().subVectors(end, start).normalize()
    const perpendicular = new THREE.Vector3(-direction.z, 0, direction.x)
    // Keep lane offset small and within the lane
    const safeOffset = Math.max(-path.laneWidth * 0.3, Math.min(path.laneWidth * 0.3, laneOffset))
    position.add(perpendicular.multiplyScalar(safeOffset))
    
    return position
  }
  
  useFrame((state, delta) => {
    if (!meshRef.current) return
    
    // Random slowdown for realistic traffic
    const hasObstacle = Math.random() > 0.97
    const targetSpeed = hasObstacle ? 0 : vehicleType.speed
    const acceleration = hasObstacle ? -4 : vehicleType.acceleration
    
    // Update speed
    currentSpeed.current += acceleration * delta
    currentSpeed.current = Math.max(0, Math.min(targetSpeed, currentSpeed.current))
    
    // Update progress
    progress.current += (currentSpeed.current * delta) / 150
    if (progress.current >= 1) progress.current = 0
    
    // Calculate position
    const position = getPositionOnPath(progress.current)
    meshRef.current.position.copy(position)
    
    // Update exhaust position
    setExhaustPosition([position.x, position.y, position.z])
    
    // Look at direction of travel
    const nextPosition = getPositionOnPath(Math.min(1, progress.current + 0.01))
    meshRef.current.lookAt(nextPosition)
  })
  
  return (
    <group>
      <group ref={meshRef}>
        {/* Vehicle body - LARGE */}
        <Box args={vehicleType.size} castShadow receiveShadow>
          <meshStandardMaterial 
            color={vehicleType.color} 
            metalness={0.7} 
            roughness={0.3}
            emissive={vehicleType.color}
            emissiveIntensity={0.1}
          />
        </Box>
        
        {/* Windshield/Windows */}
        <Box 
          args={[vehicleType.size[0] * 0.7, vehicleType.size[1] * 0.6, vehicleType.size[2] * 0.95]} 
          position={[0, vehicleType.size[1] * 0.35, 0]}
        >
          <meshStandardMaterial 
            color="#0f172a" 
            metalness={0.9} 
            roughness={0.1}
            transparent
            opacity={0.8}
          />
        </Box>
        
        {/* BRIGHT Headlights */}
        <Sphere args={[0.25]} position={[vehicleType.size[0]/2, -0.2, vehicleType.size[2]/2.5]}>
          <meshStandardMaterial 
            emissive="#ffffff" 
            emissiveIntensity={5} 
            color="#ffffff"
          />
        </Sphere>
        <Sphere args={[0.25]} position={[vehicleType.size[0]/2, -0.2, -vehicleType.size[2]/2.5]}>
          <meshStandardMaterial 
            emissive="#ffffff" 
            emissiveIntensity={5} 
            color="#ffffff"
          />
        </Sphere>
        
        {/* Headlight beams */}
        <pointLight 
          position={[vehicleType.size[0]/2 + 1, 0, 0]} 
          intensity={0.8} 
          distance={15} 
          color="#ffffff" 
        />
        
        {/* BRIGHT Tail lights */}
        <Sphere args={[0.2]} position={[-vehicleType.size[0]/2, -0.2, vehicleType.size[2]/2.5]}>
          <meshStandardMaterial 
            emissive="#ef4444" 
            emissiveIntensity={4} 
            color="#ef4444"
          />
        </Sphere>
        <Sphere args={[0.2]} position={[-vehicleType.size[0]/2, -0.2, -vehicleType.size[2]/2.5]}>
          <meshStandardMaterial 
            emissive="#ef4444" 
            emissiveIntensity={4} 
            color="#ef4444"
          />
        </Sphere>
        
        {/* Wheels */}
        {[
          [vehicleType.size[0]/2 - 0.8, -vehicleType.size[1]/2, vehicleType.size[2]/2],
          [vehicleType.size[0]/2 - 0.8, -vehicleType.size[1]/2, -vehicleType.size[2]/2],
          [-vehicleType.size[0]/2 + 0.8, -vehicleType.size[1]/2, vehicleType.size[2]/2],
          [-vehicleType.size[0]/2 + 0.8, -vehicleType.size[1]/2, -vehicleType.size[2]/2]
        ].map((pos, idx) => (
          <Sphere key={idx} args={[0.4]} position={pos}>
            <meshStandardMaterial color="#1e293b" roughness={0.9} />
          </Sphere>
        ))}
        
        {/* Roof details for specific vehicles */}
        {type === 'taxi' && (
          <Box args={[1, 0.3, 0.8]} position={[0, vehicleType.size[1]/2 + 0.15, 0]}>
            <meshStandardMaterial 
              color="#000000" 
              emissive="#fbbf24"
              emissiveIntensity={0.5}
            />
          </Box>
        )}
        
        {/* Pollution indicator for trucks */}
        {type === 'truck' && (
          <Sphere args={[1.2]} position={[-vehicleType.size[0]/2 - 0.5, 1, 0]}>
            <meshStandardMaterial
              color="#dc2626"
              transparent
              opacity={0.4}
              emissive="#dc2626"
              emissiveIntensity={0.6}
            />
          </Sphere>
        )}
      </group>
      
      {/* VISIBLE EXHAUST SMOKE - REDUCED */}
      {[0, 1].map(i => (
        <ExhaustSmoke
          key={i}
          position={[
            exhaustPosition[0] - vehicleType.size[0]/2 - 1,
            exhaustPosition[1] + 0.5,
            exhaustPosition[2]
          ]}
          color={vehicleType.pollutionColor}
          delay={i * 0.5}
          emission={vehicleType.emission}
        />
      ))}
    </group>
  )
}

// Traffic signal at intersection
function TrafficSignal({ position }) {
  const [state, setState] = React.useState('green')
  
  useEffect(() => {
    const interval = setInterval(() => {
      setState(prev => {
        if (prev === 'green') return 'yellow'
        if (prev === 'yellow') return 'red'
        return 'green'
      })
    }, 5000) // Change every 5 seconds
    
    return () => clearInterval(interval)
  }, [])
  
  return (
    <group position={position}>
      {/* Signal pole */}
      <Box args={[0.3, 8, 0.3]} position={[0, 4, 0]}>
        <meshStandardMaterial color="#1e293b" metalness={0.8} />
      </Box>
      
      {/* Signal box */}
      <Box args={[0.8, 2.5, 0.4]} position={[0, 7.5, 0]}>
        <meshStandardMaterial color="#1e293b" />
      </Box>
      
      {/* Red light */}
      <Sphere args={[0.3]} position={[0, 8.3, 0.3]}>
        <meshStandardMaterial 
          color="#ef4444"
          emissive="#ef4444" 
          emissiveIntensity={state === 'red' ? 3 : 0.1}
        />
      </Sphere>
      
      {/* Yellow light */}
      <Sphere args={[0.3]} position={[0, 7.5, 0.3]}>
        <meshStandardMaterial 
          color="#fbbf24"
          emissive="#fbbf24" 
          emissiveIntensity={state === 'yellow' ? 3 : 0.1}
        />
      </Sphere>
      
      {/* Green light */}
      <Sphere args={[0.3]} position={[0, 6.7, 0.3]}>
        <meshStandardMaterial 
          color="#10b981"
          emissive="#10b981" 
          emissiveIntensity={state === 'green' ? 3 : 0.1}
        />
      </Sphere>
      
      {/* Light glow */}
      {state === 'red' && (
        <pointLight position={[0, 8.3, 0.5]} color="#ef4444" intensity={1} distance={20} />
      )}
      {state === 'green' && (
        <pointLight position={[0, 6.7, 0.5]} color="#10b981" intensity={1} distance={20} />
      )}
    </group>
  )
}

// Main enhanced traffic system - OPTIMIZED
function EnhancedTrafficSystem() {
  const vehicleCount = 25 // Reduced for performance
  
  const vehicles = useMemo(() => {
    const vehicleList = []
    const paths = Object.entries(ROAD_PATHS)
    const vehicleTypes = Object.keys(VEHICLE_TYPES)
    
    for (let i = 0; i < vehicleCount; i++) {
      const [pathName, path] = paths[i % paths.length]
      const vehicleType = vehicleTypes[Math.floor(Math.random() * vehicleTypes.length)]
      
      // Small lane offset to keep vehicles within their lane
      const laneOffset = (Math.random() - 0.5) * (path.laneWidth * 0.4)
      
      vehicleList.push({
        id: i,
        path: path,
        type: vehicleType,
        startProgress: Math.random(),
        laneOffset: laneOffset
      })
    }
    
    return vehicleList
  }, [vehicleCount])
  
  return (
    <group>
      {/* All vehicles */}
      {vehicles.map(vehicle => (
        <EnhancedVehicle
          key={vehicle.id}
          path={vehicle.path}
          type={vehicle.type}
          startProgress={vehicle.startProgress}
          laneOffset={vehicle.laneOffset}
        />
      ))}
      
      {/* Traffic signals - REDUCED */}
      <TrafficSignal position={[0, 0, 0]} />
      <TrafficSignal position={[40, 0, 40]} />
      <TrafficSignal position={[-40, 0, -40]} />
    </group>
  )
}

export default EnhancedTrafficSystem
