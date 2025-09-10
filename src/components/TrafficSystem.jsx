import React, { useRef, useMemo, useEffect } from 'react'
import { useFrame } from '@react-three/fiber'
import { Box, Sphere } from '@react-three/drei'
import * as THREE from 'three'

// Define road paths as straight segments and curves
const ROAD_PATHS = {
  // Main East-West road through center
  mainEastWest: {
    type: 'straight',
    start: [-100, 0.5, 0],
    end: [100, 0.5, 0],
    lanes: 2,
    direction: 'bidirectional'
  },
  // Main North-South road through center
  mainNorthSouth: {
    type: 'straight',
    start: [0, 0.5, -100],
    end: [0, 0.5, 100],
    lanes: 2,
    direction: 'bidirectional'
  },
  // Secondary roads
  secondaryEast1: {
    type: 'straight',
    start: [-100, 0.5, -30],
    end: [100, 0.5, -30],
    lanes: 1,
    direction: 'bidirectional'
  },
  secondaryEast2: {
    type: 'straight',
    start: [-100, 0.5, 30],
    end: [100, 0.5, 30],
    lanes: 1,
    direction: 'bidirectional'
  },
  secondaryNorth1: {
    type: 'straight',
    start: [-30, 0.5, -100],
    end: [-30, 0.5, 100],
    lanes: 1,
    direction: 'bidirectional'
  },
  secondaryNorth2: {
    type: 'straight',
    start: [30, 0.5, -100],
    end: [30, 0.5, 100],
    lanes: 1,
    direction: 'bidirectional'
  },
  // Connecting roads
  connector1: {
    type: 'straight',
    start: [-70, 0.5, -70],
    end: [-30, 0.5, -30],
    lanes: 1,
    direction: 'oneway'
  },
  connector2: {
    type: 'straight',
    start: [70, 0.5, -70],
    end: [30, 0.5, -30],
    lanes: 1,
    direction: 'oneway'
  },
  connector3: {
    type: 'straight',
    start: [-70, 0.5, 70],
    end: [-30, 0.5, 30],
    lanes: 1,
    direction: 'oneway'
  },
  connector4: {
    type: 'straight',
    start: [70, 0.5, 70],
    end: [30, 0.5, 30],
    lanes: 1,
    direction: 'oneway'
  }
}

// Vehicle types with different characteristics
const VEHICLE_TYPES = {
  car: {
    size: [2, 0.8, 1],
    speed: 15,
    color: '#3b82f6',
    acceleration: 2
  },
  bus: {
    size: [4, 1.5, 1.5],
    speed: 10,
    color: '#10b981',
    acceleration: 1
  },
  truck: {
    size: [3.5, 1.2, 1.2],
    speed: 8,
    color: '#f59e0b',
    acceleration: 0.8
  },
  auto: {
    size: [1.5, 1, 0.8],
    speed: 12,
    color: '#fbbf24',
    acceleration: 1.5
  }
}

// Individual vehicle component
function Vehicle({ path, type = 'car', startProgress = 0, laneOffset = 0 }) {
  const meshRef = useRef()
  const progress = useRef(startProgress)
  const currentSpeed = useRef(0)
  const vehicleType = VEHICLE_TYPES[type]
  
  // Calculate position along path
  const getPositionOnPath = (t) => {
    const start = new THREE.Vector3(...path.start)
    const end = new THREE.Vector3(...path.end)
    
    // Linear interpolation for straight roads
    const position = start.lerp(end, t)
    
    // Add lane offset perpendicular to road direction
    const direction = new THREE.Vector3().subVectors(end, start).normalize()
    const perpendicular = new THREE.Vector3(-direction.z, 0, direction.x)
    position.add(perpendicular.multiplyScalar(laneOffset))
    
    return position
  }
  
  // Check for nearby vehicles (simple collision avoidance)
  const checkNearbyVehicles = () => {
    // Simplified - in production, would check actual vehicle positions
    return Math.random() > 0.95 // 5% chance of "detecting" vehicle ahead
  }
  
  useFrame((state, delta) => {
    if (!meshRef.current) return
    
    // Check for obstacles
    const hasObstacle = checkNearbyVehicles()
    
    // Adjust speed based on obstacles
    const targetSpeed = hasObstacle ? 0 : vehicleType.speed
    const acceleration = hasObstacle ? -3 : vehicleType.acceleration
    
    // Update speed with acceleration
    currentSpeed.current += acceleration * delta
    currentSpeed.current = Math.max(0, Math.min(targetSpeed, currentSpeed.current))
    
    // Update progress along path
    progress.current += (currentSpeed.current * delta) / 100
    
    // Reset if reached end (loop)
    if (progress.current >= 1) {
      progress.current = 0
    }
    
    // Calculate position
    const position = getPositionOnPath(progress.current)
    meshRef.current.position.copy(position)
    
    // Calculate rotation to face direction
    const nextPosition = getPositionOnPath(Math.min(1, progress.current + 0.01))
    meshRef.current.lookAt(nextPosition)
  })
  
  return (
    <group ref={meshRef}>
      {/* Vehicle body */}
      <Box args={vehicleType.size} castShadow>
        <meshStandardMaterial color={vehicleType.color} metalness={0.6} roughness={0.4} />
      </Box>
      
      {/* Windows */}
      <Box args={[vehicleType.size[0] * 0.6, vehicleType.size[1] * 0.5, vehicleType.size[2] * 0.9]} 
           position={[0, vehicleType.size[1] * 0.3, 0]}>
        <meshStandardMaterial color="#1e293b" metalness={0.8} roughness={0.2} />
      </Box>
      
      {/* Headlights */}
      <Sphere args={[0.08]} position={[vehicleType.size[0]/2, 0, vehicleType.size[2]/3]}>
        <meshStandardMaterial emissive="#ffffff" emissiveIntensity={2} />
      </Sphere>
      <Sphere args={[0.08]} position={[vehicleType.size[0]/2, 0, -vehicleType.size[2]/3]}>
        <meshStandardMaterial emissive="#ffffff" emissiveIntensity={2} />
      </Sphere>
      
      {/* Tail lights */}
      <Sphere args={[0.06]} position={[-vehicleType.size[0]/2, 0, vehicleType.size[2]/3]}>
        <meshStandardMaterial emissive="#ef4444" emissiveIntensity={1} />
      </Sphere>
      <Sphere args={[0.06]} position={[-vehicleType.size[0]/2, 0, -vehicleType.size[2]/3]}>
        <meshStandardMaterial emissive="#ef4444" emissiveIntensity={1} />
      </Sphere>
    </group>
  )
}

// Traffic intersection with signals
function TrafficIntersection({ position }) {
  const [signalState, setSignalState] = React.useState('northSouth') // 'northSouth' or 'eastWest'
  
  useEffect(() => {
    const interval = setInterval(() => {
      setSignalState(prev => prev === 'northSouth' ? 'eastWest' : 'northSouth')
    }, 10000) // Change every 10 seconds
    
    return () => clearInterval(interval)
  }, [])
  
  return (
    <group position={position}>
      {/* Traffic light poles */}
      {[
        [5, 0, 5],
        [-5, 0, 5],
        [5, 0, -5],
        [-5, 0, -5]
      ].map((pos, idx) => (
        <group key={idx} position={pos}>
          <Box args={[0.2, 6, 0.2]} position={[0, 3, 0]}>
            <meshStandardMaterial color="#1e293b" />
          </Box>
          
          {/* Signal lights */}
          <group position={[0, 5, 0]}>
            {/* Red light */}
            <Sphere args={[0.3]} position={[0, 0.8, 0]}>
              <meshStandardMaterial 
                emissive="#ef4444" 
                emissiveIntensity={
                  (idx < 2 && signalState === 'eastWest') || 
                  (idx >= 2 && signalState === 'northSouth') ? 2 : 0.1
                } 
              />
            </Sphere>
            
            {/* Green light */}
            <Sphere args={[0.3]} position={[0, 0, 0]}>
              <meshStandardMaterial 
                emissive="#10b981" 
                emissiveIntensity={
                  (idx < 2 && signalState === 'northSouth') || 
                  (idx >= 2 && signalState === 'eastWest') ? 2 : 0.1
                } 
              />
            </Sphere>
          </group>
        </group>
      ))}
      
      {/* Zebra crossing */}
      {[-3, -1, 1, 3].map(offset => (
        <React.Fragment key={offset}>
          <Box args={[1, 0.01, 8]} position={[offset, 0.05, 0]}>
            <meshStandardMaterial color="#ffffff" />
          </Box>
          <Box args={[8, 0.01, 1]} position={[0, 0.05, offset]}>
            <meshStandardMaterial color="#ffffff" />
          </Box>
        </React.Fragment>
      ))}
    </group>
  )
}

// Main traffic system component
function TrafficSystem() {
  const vehicleCount = 30
  
  // Generate vehicles on different roads
  const vehicles = useMemo(() => {
    const vehicleList = []
    const paths = Object.entries(ROAD_PATHS)
    const vehicleTypes = Object.keys(VEHICLE_TYPES)
    
    for (let i = 0; i < vehicleCount; i++) {
      const [pathName, path] = paths[i % paths.length]
      const vehicleType = vehicleTypes[Math.floor(Math.random() * vehicleTypes.length)]
      
      // Determine lane offset based on road type
      let laneOffset = 0
      if (path.lanes === 2) {
        laneOffset = Math.random() > 0.5 ? 2 : -2
      }
      
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
      {/* Vehicles */}
      {vehicles.map(vehicle => (
        <Vehicle
          key={vehicle.id}
          path={vehicle.path}
          type={vehicle.type}
          startProgress={vehicle.startProgress}
          laneOffset={vehicle.laneOffset}
        />
      ))}
      
      {/* Traffic intersections with signals */}
      <TrafficIntersection position={[0, 0, 0]} />
      <TrafficIntersection position={[30, 0, 30]} />
      <TrafficIntersection position={[-30, 0, 30]} />
      <TrafficIntersection position={[30, 0, -30]} />
      <TrafficIntersection position={[-30, 0, -30]} />
      
      {/* Street markings */}
      <StreetMarkings />
    </group>
  )
}

// Street markings component
function StreetMarkings() {
  return (
    <group>
      {/* Lane dividers for main roads */}
      {Array.from({ length: 20 }).map((_, i) => (
        <React.Fragment key={i}>
          {/* East-West lane markers */}
          <Box 
            args={[3, 0.02, 0.2]} 
            position={[-90 + i * 10, 0.02, 0]}
          >
            <meshStandardMaterial color="#fbbf24" emissive="#fbbf24" emissiveIntensity={0.2} />
          </Box>
          
          {/* North-South lane markers */}
          <Box 
            args={[0.2, 0.02, 3]} 
            position={[0, 0.02, -90 + i * 10]}
          >
            <meshStandardMaterial color="#fbbf24" emissive="#fbbf24" emissiveIntensity={0.2} />
          </Box>
        </React.Fragment>
      ))}
    </group>
  )
}

export default TrafficSystem
