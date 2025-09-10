import React, { useState, useEffect, Suspense } from 'react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls, Environment, Loader, Stats } from '@react-three/drei'
import * as THREE from 'three'
import { EffectComposer, Bloom, DepthOfField, Vignette } from '@react-three/postprocessing'
import CitySceneImproved from './components/CitySceneImproved'
import PolicyControlPanel from './components/PolicyControlPanel'
import InfoPanel from './components/InfoPanel'
import Timeline from './components/Timeline'
import Legend from './components/Legend'
import PlaybackController from './components/PlaybackController'
import CameraPresets from './components/CameraPresets'
import CameraManager from './components/CameraManager'
import CameraControls, { NavigationModeSelector } from './components/CameraControls'
import { useSimulationStore } from './store/simulationStore'

function App() {
  const [loading, setLoading] = useState(true)
  const { currentData, fetchSimulationData } = useSimulationStore()

  useEffect(() => {
    // Initialize simulation data
    fetchSimulationData()
    setTimeout(() => setLoading(false), 2000)
  }, [])

  return (
    <div style={{ width: '100vw', height: '100vh', position: 'relative' }}>
      {/* 3D Scene */}
      <Canvas
        shadows
        camera={{ position: [80, 60, 80], fov: 45, near: 0.1, far: 1000 }}
        gl={{ 
          antialias: true, 
          alpha: false,
          powerPreference: "high-performance",
          shadowMapEnabled: true,
          shadowMapType: THREE.PCFSoftShadowMap
        }}
      >
        <Suspense fallback={null}>
          {/* Lighting */}
          {/* Stabilized lighting setup */}
          <ambientLight intensity={0.4} />

          {/* Sun light */}
          <directionalLight
            position={[100, 120, 100]}
            intensity={0.9}
            castShadow
            shadow-mapSize={[2048, 2048]}
            shadow-camera-left={-200}
            shadow-camera-right={200}
            shadow-camera-top={200}
            shadow-camera-bottom={-200}
          />

          {/* Fill lights to avoid flicker during movement */}
          <hemisphereLight skyColor={'#d1d5db'} groundColor={'#0f172a'} intensity={0.2} />
          
          {/* City glow lights */}
          <pointLight position={[-50, 30, -50]} intensity={0.3} color="#fbbf24" />
          <pointLight position={[50, 30, 50]} intensity={0.3} color="#60a5fa" />
          
          {/* Environment */}
          <Environment preset="city" />
          <fog attach="fog" args={['#1a1a2e', 50, 200]} />
          
          {/* Camera Manager - Captures camera reference */}
          <CameraManager />
          
          {/* 3D City - Improved Version with Interactive Buildings */}
          <CitySceneImproved />
          
          {/* Enhanced Camera Controls with Multiple Modes */}
          <CameraControls />
          
          {/* Post-processing Effects for Realism */}
          <EffectComposer>
            <Bloom 
              intensity={0.3} 
              luminanceThreshold={0.8}
              luminanceSmoothing={0.9}
              mipmapBlur
            />
            <DepthOfField 
              focusDistance={0.02} 
              focalLength={0.1} 
              bokehScale={3}
              height={480}
            />
            <Vignette offset={0.2} darkness={0.3} />
          </EffectComposer>
        </Suspense>
        
        {/* Performance Stats */}
        <Stats />
      </Canvas>
      
      {/* UI Overlays */}
      <NavigationModeSelector />
      <InfoPanel />
      <PolicyControlPanel />
      <Timeline />
      <Legend />
      <PlaybackController />
      <CameraPresets />
      
      {/* Loading Screen */}
      {loading && (
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{ textAlign: 'center' }}>
            <h1 style={{ fontSize: '48px', marginBottom: '20px', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              Delhi Digital Twin
            </h1>
            <p style={{ fontSize: '18px', opacity: 0.7 }}>Initializing 3D Simulation...</p>
            <div style={{ marginTop: '30px' }}>
              <div style={{
                width: '200px',
                height: '4px',
                background: 'rgba(255,255,255,0.1)',
                borderRadius: '2px',
                overflow: 'hidden'
              }}>
                <div style={{
                  width: '50%',
                  height: '100%',
                  background: 'linear-gradient(90deg, #667eea, #764ba2)',
                  animation: 'slide 1.5s infinite'
                }} />
              </div>
            </div>
          </div>
        </div>
      )}
      
      <Loader />
      
      <style>{`
        @keyframes slide {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(200%); }
        }
      `}</style>
    </div>
  )
}

export default App
