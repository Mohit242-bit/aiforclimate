import React, { useRef, useMemo, useState, useEffect } from 'react'
import { useFrame, useLoader } from '@react-three/fiber'
import { Box, Sphere, Plane, Text, Cloud, Sky, Stars, Float, Html } from '@react-three/drei'
import * as THREE from 'three'
import { useSimulationStore } from '../store/simulationStore'
import EnhancedTrafficSystem from './EnhancedTrafficSystem'
import PollutionVisualization from './PollutionVisualization'

// Performance optimization: Reduce detail on buildings
const PERFORMANCE_MODE = true
const MAX_BUILDINGS = 50 // Reduce from 100+
const BUILDING_LOD_DISTANCE = 150

// Interactive building with proper structure and placement
function InteractiveBuilding({ position, height, width, depth, aqi, type = 'commercial', buildingData }) {
  const meshRef = useRef()
  const [hovered, setHovered] = useState(false)
  const [clicked, setClicked] = useState(false)
  
  // Color based on AQI with smoother gradients
  const buildingColor = useMemo(() => {
    if (aqi < 100) return '#10b981' // Green
    if (aqi < 150) return '#34d399' // Light Green  
    if (aqi < 200) return '#fbbf24' // Yellow
    if (aqi < 250) return '#fb923c' // Orange
    if (aqi < 300) return '#f87171' // Light Red
    return '#dc2626' // Red
  }, [aqi])
  
  const baseColor = useMemo(() => {
    const colors = {
      commercial: '#94a3b8',
      residential: '#cbd5e1',
      office: '#64748b',
      industrial: '#475569',
      landmark: '#818cf8',
      government: '#a78bfa'
    }
    return colors[type] || '#94a3b8'
  }, [type])

  // Subtle animation on hover
  useFrame((state) => {
    if (meshRef.current && hovered) {
      meshRef.current.position.y = Math.sin(state.clock.elapsedTime * 2) * 0.1
    }
  })
  
  return (
    <group position={position}>
      {/* Building base/foundation */}
      <Box
        args={[width + 2, 0.5, depth + 2]}
        position={[0, -0.25, 0]}
        castShadow
        receiveShadow
      >
        <meshStandardMaterial color="#1e293b" roughness={1} />
      </Box>

      {/* Main building structure */}
      <Box
        ref={meshRef}
        args={[width, height, depth]}
        position={[0, height/2, 0]}
        castShadow
        receiveShadow
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
        onClick={() => setClicked(!clicked)}
      >
        <meshStandardMaterial 
          color={hovered ? '#667eea' : baseColor}
          metalness={0.4}
          roughness={0.6}
          emissive={hovered ? '#667eea' : '#000000'}
          emissiveIntensity={hovered ? 0.1 : 0}
        />
      </Box>
      
      {/* AQI indicator band at top */}
      <Box
        position={[0, height + 0.5, 0]}
        args={[width * 0.9, 1, depth * 0.9]}
      >
        <meshStandardMaterial
          color={buildingColor}
          emissive={buildingColor}
          emissiveIntensity={0.5}
        />
      </Box>
      
      {/* Windows with proper spacing - OPTIMIZED */}
      {!PERFORMANCE_MODE && Array.from({ length: Math.min(3, Math.floor(height / 3)) }).map((_, floorIndex) => (
        <group key={floorIndex}>
          {Array.from({ length: Math.min(2, Math.floor(width / 3)) }).map((_, windowIndex) => {
            const windowWidth = 1.5
            const spacing = (width - windowWidth * Math.floor(width / 3)) / (Math.floor(width / 3) + 1)
            return (
              <Box
                key={`${floorIndex}-${windowIndex}`}
                position={[
                  -width/2 + spacing + windowIndex * (windowWidth + spacing) + windowWidth/2,
                  floorIndex * 3 + 1.5,
                  depth/2 + 0.01
                ]}
                args={[windowWidth, 2, 0.05]}
              >
                <meshStandardMaterial
                  color="#60a5fa"
                  emissive="#60a5fa"
                  emissiveIntensity={0.3}
                  transparent
                  opacity={0.7}
                />
              </Box>
            )
          })}
        </group>
      ))}
      
      {/* Rooftop details */}
      {type === 'commercial' && (
        <>
          <Box position={[width * 0.3, height + 1.5, depth * 0.3]} args={[1, 3, 1]}>
            <meshStandardMaterial color="#475569" />
          </Box>
          <Box position={[-width * 0.3, height + 1, -depth * 0.3]} args={[2, 2, 2]}>
            <meshStandardMaterial color="#475569" />
          </Box>
        </>
      )}
      
      {/* Building info popup */}
      {clicked && (
        <Html position={[0, height + 5, 0]} center>
          <div style={{
            background: 'rgba(0, 0, 0, 0.9)',
            backdropFilter: 'blur(10px)',
            padding: '15px',
            borderRadius: '10px',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            minWidth: '200px',
            color: 'white'
          }}>
            <h3 style={{ margin: '0 0 10px 0', fontSize: '16px' }}>
              {buildingData?.name || `${type.charAt(0).toUpperCase() + type.slice(1)} Building`}
            </h3>
            <div style={{ fontSize: '12px', opacity: 0.8 }}>
              <p>Type: {type}</p>
              <p>Height: {height}m</p>
              <p>AQI Level: <span style={{ color: buildingColor }}>{aqi}</span></p>
              {buildingData?.occupancy && <p>Occupancy: {buildingData.occupancy}</p>}
              {buildingData?.energyUse && <p>Energy: {buildingData.energyUse} kWh</p>}
            </div>
          </div>
        </Html>
      )}
    </group>
  )
}

// City block with proper spacing and sidewalks
function CityBlock({ position, blockData, zoneAqi }) {
  return (
    <group position={position}>
      {/* Block ground/sidewalk */}
      <Box
        args={[blockData.width, 0.1, blockData.depth]}
        position={[0, 0, 0]}
        receiveShadow
      >
        <meshStandardMaterial color="#334155" roughness={0.9} />
      </Box>
      
      {/* Sidewalk borders */}
      <Box args={[blockData.width, 0.2, 0.5]} position={[0, 0.1, blockData.depth/2]}>
        <meshStandardMaterial color="#64748b" />
      </Box>
      <Box args={[blockData.width, 0.2, 0.5]} position={[0, 0.1, -blockData.depth/2]}>
        <meshStandardMaterial color="#64748b" />
      </Box>
      <Box args={[0.5, 0.2, blockData.depth]} position={[blockData.width/2, 0.1, 0]}>
        <meshStandardMaterial color="#64748b" />
      </Box>
      <Box args={[0.5, 0.2, blockData.depth]} position={[-blockData.width/2, 0.1, 0]}>
        <meshStandardMaterial color="#64748b" />
      </Box>
      
      {/* Buildings in the block */}
      {blockData.buildings.map((building, idx) => (
        <InteractiveBuilding
          key={idx}
          position={building.pos}
          height={building.height}
          width={building.width}
          depth={building.depth}
          type={building.type}
          aqi={zoneAqi}
          buildingData={building}
        />
      ))}
      
      {/* Street lights */}
      {blockData.streetLights?.map((light, idx) => (
        <group key={idx} position={light.pos}>
          <Box args={[0.2, 5, 0.2]}>
            <meshStandardMaterial color="#1e293b" />
          </Box>
          <Sphere args={[0.3]} position={[0, 5.5, 0]}>
            <meshStandardMaterial 
              emissive="#fbbf24" 
              emissiveIntensity={2}
              color="#fbbf24"
            />
          </Sphere>
          <pointLight position={[0, 5.5, 0]} intensity={0.5} distance={15} color="#fbbf24" />
        </group>
      ))}
      
      {/* Trees/greenery */}
      {blockData.trees?.map((tree, idx) => (
        <group key={idx} position={tree.pos}>
          <Box args={[0.3, 2, 0.3]} position={[0, 1, 0]}>
            <meshStandardMaterial color="#7c2d12" />
          </Box>
          <Sphere args={[1.5]} position={[0, 3, 0]}>
            <meshStandardMaterial color="#22c55e" roughness={1} />
          </Sphere>
        </group>
      ))}
    </group>
  )
}

// Lotus Temple Landmark
function LotusTemple({ position }) {
  const petalCount = 9
  return (
    <group position={position}>
      {/* Base platform */}
      <Box args={[25, 0.5, 25]} position={[0, 0, 0]} receiveShadow>
        <meshStandardMaterial color="#3b82f6" roughness={0.9} />
      </Box>
      
      {/* Lotus petals */}
      {Array.from({ length: petalCount }).map((_, i) => {
        const angle = (i / petalCount) * Math.PI * 2
        return (
          <Box
            key={i}
            args={[2, 15, 8]}
            position={[
              Math.cos(angle) * 8,
              7.5,
              Math.sin(angle) * 8
            ]}
            rotation={[0, angle, Math.PI / 8]}
            castShadow
          >
            <meshStandardMaterial color="#f0f0f0" roughness={0.3} metalness={0.2} />
          </Box>
        )
      })}
      
      {/* Center dome */}
      <Sphere args={[5, 32, 16]} position={[0, 10, 0]} castShadow>
        <meshStandardMaterial color="#f8f8f8" roughness={0.2} metalness={0.3} />
      </Sphere>
      
      {/* Label */}
      <Text
        position={[0, 20, 0]}
        fontSize={1.5}
        color="#ffffff"
        anchorX="center"
        anchorY="middle"
      >
        Lotus Temple
      </Text>
    </group>
  )
}

// Red Fort Landmark
function RedFort({ position }) {
  return (
    <group position={position}>
      {/* Fort walls */}
      <Box args={[40, 12, 2]} position={[0, 6, -15]} castShadow>
        <meshStandardMaterial color="#b91c1c" roughness={0.8} />
      </Box>
      <Box args={[40, 12, 2]} position={[0, 6, 15]} castShadow>
        <meshStandardMaterial color="#b91c1c" roughness={0.8} />
      </Box>
      <Box args={[2, 12, 30]} position={[-20, 6, 0]} castShadow>
        <meshStandardMaterial color="#b91c1c" roughness={0.8} />
      </Box>
      <Box args={[2, 12, 30]} position={[20, 6, 0]} castShadow>
        <meshStandardMaterial color="#b91c1c" roughness={0.8} />
      </Box>
      
      {/* Main gate */}
      <Box args={[8, 15, 3]} position={[0, 7.5, -15]} castShadow>
        <meshStandardMaterial color="#991b1b" roughness={0.7} />
      </Box>
      
      {/* Towers */}
      {[-15, 15].map((x) => (
        <Box key={x} args={[5, 18, 5]} position={[x, 9, -15]} castShadow>
          <meshStandardMaterial color="#7f1d1d" roughness={0.8} />
        </Box>
      ))}
      
      {/* Label */}
      <Text
        position={[0, 20, 0]}
        fontSize={2}
        color="#ffffff"
        anchorX="center"
        anchorY="middle"
      >
        Red Fort
      </Text>
    </group>
  )
}

// India Gate Landmark
function IndiaGate({ position }) {
  return (
    <group position={position}>
      {/* Base platform */}
      <Box args={[30, 0.5, 20]} position={[0, 0, 0]} receiveShadow>
        <meshStandardMaterial color="#22c55e" roughness={1} />
      </Box>
      
      {/* Main arch structure */}
      <group position={[0, 0, 0]}>
        {/* Left pillar */}
        <Box args={[3, 20, 3]} position={[-6, 10, 0]} castShadow>
          <meshStandardMaterial color="#dc2626" roughness={0.5} />
        </Box>
        {/* Right pillar */}
        <Box args={[3, 20, 3]} position={[6, 10, 0]} castShadow>
          <meshStandardMaterial color="#dc2626" roughness={0.5} />
        </Box>
        {/* Top arch */}
        <Box args={[15, 3, 3]} position={[0, 20, 0]} castShadow>
          <meshStandardMaterial color="#dc2626" roughness={0.5} />
        </Box>
        {/* Arch detail */}
        <Box args={[12, 2, 2.5]} position={[0, 16, 0]} castShadow>
          <meshStandardMaterial color="#dc2626" roughness={0.5} />
        </Box>
      </group>
      
      {/* Text label */}
      <Text
        position={[0, 25, 0]}
        fontSize={2}
        color="#ffffff"
        anchorX="center"
        anchorY="middle"
        outlineWidth={0.1}
        outlineColor="black"
      >
        INDIA GATE
      </Text>
      
      {/* Decorative lights */}
      <pointLight position={[0, 15, 5]} intensity={0.5} color="#fbbf24" distance={30} />
      <pointLight position={[0, 15, -5]} intensity={0.5} color="#fbbf24" distance={30} />
    </group>
  )
}

// Improved road system
function RoadNetwork() {
  return (
    <group>
      {/* Main arterial roads */}
      <Box args={[200, 0.05, 12]} position={[0, 0.01, 0]}>
        <meshStandardMaterial color="#0f172a" roughness={0.95} />
      </Box>
      <Box args={[12, 0.05, 200]} position={[0, 0.01, 0]}>
        <meshStandardMaterial color="#0f172a" roughness={0.95} />
      </Box>
      
      {/* Road markings */}
      <Box args={[200, 0.06, 0.3]} position={[0, 0.02, 0]}>
        <meshStandardMaterial color="#fbbf24" emissive="#fbbf24" emissiveIntensity={0.2} />
      </Box>
      <Box args={[0.3, 0.06, 200]} position={[0, 0.02, 0]}>
        <meshStandardMaterial color="#fbbf24" emissive="#fbbf24" emissiveIntensity={0.2} />
      </Box>
      
      {/* Secondary roads */}
      {[-60, -30, 30, 60].map(offset => (
        <React.Fragment key={offset}>
          <Box args={[200, 0.05, 8]} position={[0, 0.01, offset]}>
            <meshStandardMaterial color="#1e293b" roughness={0.95} />
          </Box>
          <Box args={[8, 0.05, 200]} position={[offset, 0.01, 0]}>
            <meshStandardMaterial color="#1e293b" roughness={0.95} />
          </Box>
        </React.Fragment>
      ))}
    </group>
  )
}

// Main improved city scene
function CitySceneImproved() {
  const { zones, time } = useSimulationStore()
  const [currentTime, setCurrentTime] = useState(12)
  
  // Update time for day/night cycle
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTime(prev => (prev + 0.1) % 24)
    }, 100)
    return () => clearInterval(interval)
  }, [])
  
  const isDayTime = currentTime >= 6 && currentTime <= 18
  const lightIntensity = isDayTime ? 1 : 0.3
  
  // Define city layout with proper blocks
  const cityLayout = [
    {
      zone: 'Connaught Place',
      position: [0, 0, 0],
      blocks: [
        {
          position: [20, 0, 20],
          width: 35,
          depth: 35,
          buildings: [
            { pos: [0, 0, 0], height: 30, width: 8, depth: 8, type: 'office', name: 'Central Tower' },
            { pos: [-10, 0, -10], height: 25, width: 6, depth: 6, type: 'commercial', name: 'Shopping Complex' },
            { pos: [10, 0, -10], height: 20, width: 5, depth: 7, type: 'commercial' },
            { pos: [-10, 0, 10], height: 28, width: 7, depth: 6, type: 'office' },
          ],
          streetLights: [
            { pos: [-15, 0, 0] },
            { pos: [15, 0, 0] },
          ],
          trees: [
            { pos: [0, 0, 15] },
            { pos: [0, 0, -15] },
          ]
        },
        {
          position: [-20, 0, -20],
          width: 35,
          depth: 35,
          buildings: [
            { pos: [0, 0, 0], height: 35, width: 10, depth: 8, type: 'government', name: 'Municipal Office' },
            { pos: [10, 0, 10], height: 22, width: 6, depth: 6, type: 'office' },
            { pos: [-10, 0, 10], height: 18, width: 5, depth: 5, type: 'commercial' },
          ],
          streetLights: [
            { pos: [0, 0, 15] },
          ],
          trees: [
            { pos: [12, 0, 0] },
            { pos: [-12, 0, 0] },
          ]
        }
      ]
    },
    {
      zone: 'Karol Bagh',
      position: [-70, 0, -70],
      blocks: [
        {
          position: [0, 0, 0],
          width: 30,
          depth: 30,
          buildings: [
            { pos: [0, 0, 0], height: 15, width: 5, depth: 5, type: 'residential', name: 'Karol Apartments' },
            { pos: [8, 0, 8], height: 12, width: 4, depth: 4, type: 'residential' },
            { pos: [-8, 0, 8], height: 18, width: 6, depth: 5, type: 'commercial' },
            { pos: [8, 0, -8], height: 14, width: 4, depth: 4, type: 'residential' },
            { pos: [-8, 0, -8], height: 16, width: 5, depth: 5, type: 'residential' },
          ],
          streetLights: [
            { pos: [12, 0, 0] },
            { pos: [-12, 0, 0] },
          ],
          trees: [
            { pos: [0, 0, 12] },
            { pos: [0, 0, -12] },
          ]
        }
      ]
    },
    {
      zone: 'Dwarka',
      position: [70, 0, -70],
      blocks: [
        {
          position: [0, 0, 0],
          width: 40,
          depth: 40,
          buildings: [
            { pos: [0, 0, 0], height: 25, width: 8, depth: 8, type: 'residential', name: 'Dwarka Heights' },
            { pos: [12, 0, 12], height: 20, width: 6, depth: 6, type: 'residential' },
            { pos: [-12, 0, 12], height: 22, width: 7, depth: 6, type: 'commercial', name: 'Dwarka Mall' },
            { pos: [12, 0, -12], height: 18, width: 5, depth: 5, type: 'residential' },
            { pos: [-12, 0, -12], height: 28, width: 8, depth: 7, type: 'office' },
          ],
          streetLights: [
            { pos: [15, 0, 15] },
            { pos: [-15, 0, -15] },
          ],
          trees: [
            { pos: [15, 0, -15] },
            { pos: [-15, 0, 15] },
            { pos: [0, 0, 18] },
          ]
        }
      ]
    },
    {
      zone: 'Rohini',
      position: [-70, 0, 70],
      blocks: [
        {
          position: [0, 0, 0],
          width: 35,
          depth: 35,
          buildings: [
            { pos: [0, 0, 0], height: 20, width: 7, depth: 7, type: 'residential', name: 'Rohini Towers' },
            { pos: [10, 0, 10], height: 16, width: 5, depth: 5, type: 'residential' },
            { pos: [-10, 0, 10], height: 14, width: 4, depth: 5, type: 'residential' },
            { pos: [10, 0, -10], height: 18, width: 6, depth: 5, type: 'commercial' },
            { pos: [-10, 0, -10], height: 15, width: 5, depth: 4, type: 'residential' },
          ],
          streetLights: [
            { pos: [0, 0, 15] },
            { pos: [0, 0, -15] },
          ],
          trees: [
            { pos: [13, 0, 0] },
            { pos: [-13, 0, 0] },
            { pos: [0, 0, 0] },
          ]
        }
      ]
    },
    {
      zone: 'Saket',
      position: [70, 0, 70],
      blocks: [
        {
          position: [0, 0, 0],
          width: 35,
          depth: 35,
          buildings: [
            { pos: [0, 0, 0], height: 30, width: 9, depth: 8, type: 'commercial', name: 'Select City Walk' },
            { pos: [12, 0, 10], height: 24, width: 6, depth: 6, type: 'office' },
            { pos: [-12, 0, 10], height: 20, width: 5, depth: 6, type: 'residential' },
            { pos: [10, 0, -10], height: 26, width: 7, depth: 6, type: 'office' },
          ],
          streetLights: [
            { pos: [15, 0, 0] },
            { pos: [-15, 0, 0] },
          ],
          trees: [
            { pos: [0, 0, 13] },
            { pos: [0, 0, -13] },
          ]
        }
      ]
    }
  ]
  
  return (
    <group>
      {/* Dynamic sky based on time */}
      <Sky
        distance={450000}
        sunPosition={[
          Math.cos((currentTime / 24) * Math.PI * 2 - Math.PI/2) * 100,
          Math.sin((currentTime / 24) * Math.PI * 2 - Math.PI/2) * 100,
          0
        ]}
        inclination={0}
        azimuth={0.25}
        mieCoefficient={0.005}
        mieDirectionalG={0.8}
        rayleigh={isDayTime ? 2 : 0.1}
        turbidity={10}
      />
      
      {/* Stars for night time */}
      {!isDayTime && <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade />}
      
      {/* Ground plane */}
      <Plane 
        args={[400, 400]} 
        rotation={[-Math.PI / 2, 0, 0]} 
        position={[0, -0.1, 0]}
        receiveShadow
      >
        <meshStandardMaterial color="#0f172a" roughness={1} />
      </Plane>
      
      {/* Road network */}
      <RoadNetwork />
      
      {/* Delhi Landmarks */}
      <IndiaGate position={[0, 0, -100]} />
      <LotusTemple position={[100, 0, 50]} />
      <RedFort position={[-100, 0, -30]} />
      
      {/* City zones with blocks */}
      {cityLayout.map((zone, zoneIdx) => {
        const zoneData = zones.find(z => z.name === zone.zone) || { aqi: 150 }
        
        return (
          <group key={zoneIdx} position={zone.position}>
            {/* Zone label */}
            <Text
              position={[0, 50, 0]}
              fontSize={4}
              color="white"
              anchorX="center"
              anchorY="middle"
              outlineWidth={0.3}
              outlineColor="black"
            >
              {zone.zone}
            </Text>
            
            {/* AQI display */}
            <Text
              position={[0, 45, 0]}
              fontSize={3}
              color={zoneData.aqi > 200 ? '#ef4444' : '#fbbf24'}
              anchorX="center"
              anchorY="middle"
            >
              AQI: {zoneData.aqi}
            </Text>
            
            {/* City blocks */}
            {zone.blocks.map((block, blockIdx) => (
              <CityBlock
                key={blockIdx}
                position={block.position}
                blockData={block}
                zoneAqi={zoneData.aqi}
              />
            ))}
          </group>
        )
      })}
      
      {/* ENHANCED POLLUTION VISUALIZATION - Highly Visible */}
      <PollutionVisualization zones={zones} cityLayout={cityLayout} />
      
      {/* ENHANCED TRAFFIC SYSTEM - Larger Vehicles with Exhaust */}
      <EnhancedTrafficSystem />
    </group>
  )
}

// Import statement for TrafficSystem would go at the top of the file
// For now, we'll import it dynamically

export default CitySceneImproved
