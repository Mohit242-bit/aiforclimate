import React, { useRef, useMemo, useState } from 'react'
import { useFrame } from '@react-three/fiber'
import { Sphere, Box, Cylinder, Plane, Text } from '@react-three/drei'
import * as THREE from 'three'

// Carbon Emission Clouds - Visual representation of CO2 emissions
function CarbonCloud({ position, intensity, type = 'mixed' }) {
  const cloudRef = useRef()
  
  useFrame((state) => {
    if (cloudRef.current) {
      cloudRef.current.rotation.y = state.clock.elapsedTime * 0.1
      cloudRef.current.position.y = position[1] + Math.sin(state.clock.elapsedTime * 0.5) * 2
    }
  })

  const colors = {
    'traffic': '#1f2937', // Dark gray for vehicle emissions
    'industry': '#7c2d12', // Brown for industrial emissions
    'buildings': '#374151', // Gray for building emissions
    'mixed': '#0f172a' // Very dark for mixed emissions
  }

  return (
    <group>
      <Sphere
        ref={cloudRef}
        position={position}
        args={[intensity * 8, 16, 16]}
      >
        <meshStandardMaterial
          color={colors[type]}
          transparent
          opacity={intensity * 0.4}
          depthWrite={false}
        />
      </Sphere>
      
      {/* CO2 particles rising */}
      {Array.from({ length: Math.floor(intensity * 20) }).map((_, i) => (
        <Sphere
          key={i}
          position={[
            position[0] + (Math.random() - 0.5) * 15,
            position[1] + Math.random() * 20,
            position[2] + (Math.random() - 0.5) * 15
          ]}
          args={[0.3, 8, 8]}
        >
          <meshStandardMaterial
            color={colors[type]}
            transparent
            opacity={0.3}
            emissive={colors[type]}
            emissiveIntensity={0.2}
          />
        </Sphere>
      ))}
    </group>
  )
}

// Solar Panel Arrays - Visual representation of renewable energy
function SolarPanelArray({ position, capacity_mw }) {
  const panelCount = Math.min(20, Math.floor(capacity_mw / 5))
  
  return (
    <group position={position}>
      {Array.from({ length: panelCount }).map((_, i) => (
        <group
          key={i}
          position={[
            (i % 5) * 3 - 6,
            0.2,
            Math.floor(i / 5) * 2 - 3
          ]}
          rotation={[0, Math.PI / 4, 0]}
        >
          <Box args={[2, 0.1, 3]}>
            <meshStandardMaterial
              color="#1e3a8a"
              metalness={0.8}
              roughness={0.2}
              emissive="#3b82f6"
              emissiveIntensity={0.3}
            />
          </Box>
          {/* Support structure */}
          <Box position={[0, -0.5, 0]} args={[0.2, 1, 0.2]}>
            <meshStandardMaterial color="#6b7280" />
          </Box>
        </group>
      ))}
      
      {/* Energy flow visualization */}
      <Cylinder position={[0, 5, 0]} args={[0.5, 0.5, 10]}>
        <meshStandardMaterial
          color="#fbbf24"
          transparent
          opacity={0.6}
          emissive="#fbbf24"
          emissiveIntensity={0.8}
        />
      </Cylinder>
    </group>
  )
}

// Wind Turbines for wind energy visualization
function WindTurbine({ position, capacity_mw }) {
  const turbineRef = useRef()
  const bladeRef = useRef()
  
  useFrame((state) => {
    if (bladeRef.current) {
      bladeRef.current.rotation.z += 0.1 // Spinning blades
    }
  })

  if (capacity_mw < 1) return null

  return (
    <group position={position}>
      {/* Tower */}
      <Cylinder position={[0, 10, 0]} args={[0.5, 0.8, 20]}>
        <meshStandardMaterial color="#e5e7eb" />
      </Cylinder>
      
      {/* Nacelle */}
      <Box position={[0, 20, 0]} args={[3, 1.5, 1]}>
        <meshStandardMaterial color="#9ca3af" />
      </Box>
      
      {/* Blades */}
      <group ref={bladeRef} position={[0, 20, 0]}>
        {[0, 120, 240].map((angle, i) => (
          <Box
            key={i}
            position={[
              Math.cos((angle * Math.PI) / 180) * 7,
              Math.sin((angle * Math.PI) / 180) * 7,
              0
            ]}
            rotation={[0, 0, (angle * Math.PI) / 180]}
            args={[0.2, 12, 0.5]}
          >
            <meshStandardMaterial color="#f3f4f6" />
          </Box>
        ))}
      </group>
      
      {/* Energy generation effect */}
      <Sphere position={[0, 25, 0]} args={[2]}>
        <meshStandardMaterial
          color="#10b981"
          transparent
          opacity={0.3}
          emissive="#10b981"
          emissiveIntensity={0.6}
        />
      </Sphere>
    </group>
  )
}

// Green Infrastructure - Trees, parks, green roofs
function GreenInfrastructure({ type, position, effectiveness }) {
  const treeRef = useRef()
  
  useFrame((state) => {
    if (treeRef.current) {
      treeRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.5) * 0.1
    }
  })

  if (type === 'urban_forest') {
    return (
      <group position={position}>
        {Array.from({ length: effectiveness * 10 }).map((_, i) => (
          <group
            key={i}
            ref={i === 0 ? treeRef : null}
            position={[
              (Math.random() - 0.5) * 20,
              0,
              (Math.random() - 0.5) * 20
            ]}
          >
            {/* Tree trunk */}
            <Cylinder position={[0, 3, 0]} args={[0.3, 0.5, 6]}>
              <meshStandardMaterial color="#7c2d12" />
            </Cylinder>
            
            {/* Tree crown */}
            <Sphere position={[0, 7, 0]} args={[2.5 + Math.random()]}>
              <meshStandardMaterial
                color="#22c55e"
                emissive="#16a34a"
                emissiveIntensity={0.2}
              />
            </Sphere>
            
            {/* CO2 absorption effect */}
            <Sphere position={[0, 9, 0]} args={[1]}>
              <meshStandardMaterial
                color="#10b981"
                transparent
                opacity={0.2}
                emissive="#10b981"
                emissiveIntensity={0.3}
              />
            </Sphere>
          </group>
        ))}
      </group>
    )
  }

  if (type === 'green_roofs') {
    return (
      <group position={position}>
        <Plane args={[15, 15]} rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.1, 0]}>
          <meshStandardMaterial
            color="#22c55e"
            emissive="#16a34a"
            emissiveIntensity={0.1}
          />
        </Plane>
        
        {/* Plants on roof */}
        {Array.from({ length: 8 }).map((_, i) => (
          <Sphere
            key={i}
            position={[
              (Math.random() - 0.5) * 12,
              1,
              (Math.random() - 0.5) * 12
            ]}
            args={[0.5]}
          >
            <meshStandardMaterial color="#16a34a" />
          </Sphere>
        ))}
      </group>
    )
  }

  return null
}

// Climate Risk Indicators
function ClimateRiskIndicator({ position, riskType, intensity }) {
  const colors = {
    'heatwave': '#ef4444',
    'flood': '#3b82f6',
    'drought': '#f59e0b',
    'air_quality': '#8b5cf6'
  }

  const icons = {
    'heatwave': '🔥',
    'flood': '🌊', 
    'drought': '🏜️',
    'air_quality': '💨'
  }

  if (intensity < 30) return null

  return (
    <group position={position}>
      <Sphere args={[intensity / 10]} position={[0, intensity / 5, 0]}>
        <meshStandardMaterial
          color={colors[riskType]}
          transparent
          opacity={0.4}
          emissive={colors[riskType]}
          emissiveIntensity={intensity / 100}
        />
      </Sphere>
      
      {/* Warning beacon */}
      <Cylinder args={[0.5, 0.5, intensity / 20]} position={[0, intensity / 10, 0]}>
        <meshStandardMaterial
          color={colors[riskType]}
          emissive={colors[riskType]}
          emissiveIntensity={0.8}
        />
      </Cylinder>
    </group>
  )
}

// Net Zero Progress Bar (3D)
function NetZeroProgressBar({ position, progress, targetYear }) {
  const progressHeight = (progress / 100) * 20

  return (
    <group position={position}>
      {/* Base structure */}
      <Box position={[0, 10, 0]} args={[2, 20, 2]}>
        <meshStandardMaterial
          color="#374151"
          transparent
          opacity={0.3}
        />
      </Box>
      
      {/* Progress fill */}
      <Box position={[0, progressHeight / 2, 0]} args={[1.8, progressHeight, 1.8]}>
        <meshStandardMaterial
          color="#10b981"
          emissive="#10b981"
          emissiveIntensity={0.3}
        />
      </Box>
      
      {/* Target year indicator */}
      <Text
        position={[0, 22, 0]}
        fontSize={2}
        color="#ffffff"
        anchorX="center"
        anchorY="middle"
      >
        Net Zero by {targetYear}
      </Text>
      
      {/* Progress percentage */}
      <Text
        position={[0, -2, 0]}
        fontSize={1.5}
        color="#10b981"
        anchorX="center"
        anchorY="middle"
      >
        {progress.toFixed(1)}%
      </Text>
    </group>
  )
}

export {
  CarbonCloud,
  SolarPanelArray,
  WindTurbine,
  GreenInfrastructure,
  ClimateRiskIndicator,
  NetZeroProgressBar
}