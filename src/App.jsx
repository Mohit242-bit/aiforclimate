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
  const [showLeftPanel, setShowLeftPanel] = useState(false)
  const [showRightPanel, setShowRightPanel] = useState(false)
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
          shadowMapType: THREE.PCFSoftShadowMap,
          pixelRatio: window.devicePixelRatio
        }}
        dpr={[1, 2]}
      >
        <Suspense fallback={null}>
          {/* Lighting - ENHANCED for better visibility */}
          {/* Strong ambient light to see everything clearly */}
          <ambientLight intensity={0.6} />

          {/* Sun light - BRIGHTER */}
          <directionalLight
            position={[100, 150, 100]}
            intensity={1.2}
            castShadow
            shadow-mapSize={[4096, 4096]}
            shadow-camera-left={-250}
            shadow-camera-right={250}
            shadow-camera-top={250}
            shadow-camera-bottom={-250}
            shadow-bias={-0.0001}
          />

          {/* Fill lights - STRONGER */}
          <hemisphereLight skyColor={'#e0e7ff'} groundColor={'#1e293b'} intensity={0.4} />
          
          {/* City glow lights - MORE VISIBLE */}
          <pointLight position={[-50, 40, -50]} intensity={0.6} color="#fbbf24" distance={100} />
          <pointLight position={[50, 40, 50]} intensity={0.6} color="#60a5fa" distance={100} />
          <pointLight position={[-50, 40, 50]} intensity={0.5} color="#a78bfa" distance={100} />
          <pointLight position={[50, 40, -50]} intensity={0.5} color="#fb923c" distance={100} />
          
          {/* Environment */}
          <Environment preset="city" />
          <fog attach="fog" args={['#1a1a2e', 50, 200]} />
          
          {/* Camera Manager - Captures camera reference */}
          <CameraManager />
          
          {/* 3D City - Improved Version with Interactive Buildings */}
          <CitySceneImproved />
          
          {/* Enhanced Camera Controls with Multiple Modes */}
          <CameraControls />
          
          {/* Post-processing Effects - REDUCED for clarity */}
          <EffectComposer>
            <Bloom 
              intensity={0.15}
              luminanceThreshold={0.9}
              luminanceSmoothing={0.7}
              mipmapBlur
            />
            {/* Depth of Field DISABLED for clarity - was making scene blurry */}
            <Vignette offset={0.1} darkness={0.15} />
          </EffectComposer>
        </Suspense>
        
        {/* Performance Stats */}
        <Stats />
      </Canvas>
      
      {/* Left Panel Toggle (Info Panel) */}
      <button
        onClick={() => setShowLeftPanel(!showLeftPanel)}
        style={{
          position: 'absolute',
          top: '20px',
          left: showLeftPanel ? '340px' : '20px',
          zIndex: 1100,
          width: '50px',
          height: '50px',
          borderRadius: '50%',
          border: 'none',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          fontSize: '24px',
          cursor: 'pointer',
          boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
          transition: 'all 0.3s ease',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.transform = 'scale(1.1)';
          e.currentTarget.style.boxShadow = '0 6px 20px rgba(102, 126, 234, 0.5)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = 'scale(1)';
          e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.3)';
        }}
      >
        ☰
      </button>

      {/* Right Panel Toggle (AI Panel) */}
      <button
        onClick={() => setShowRightPanel(!showRightPanel)}
        style={{
          position: 'absolute',
          top: '20px',
          right: showRightPanel ? '420px' : '20px',
          zIndex: 1100,
          padding: '12px 20px',
          borderRadius: '25px',
          border: 'none',
          background: 'linear-gradient(135deg, #764ba2 0%, #667eea 100%)',
          color: 'white',
          fontSize: '14px',
          fontWeight: 'bold',
          cursor: 'pointer',
          boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
          transition: 'all 0.3s ease',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.transform = 'scale(1.05)';
          e.currentTarget.style.boxShadow = '0 6px 20px rgba(118, 75, 162, 0.5)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = 'scale(1)';
          e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.3)';
        }}
      >
        {showRightPanel ? '✕ Close AI' : '🤖 AI Panel'}
      </button>
      
      {/* UI Overlays */}
      <NavigationModeSelector />
      {showLeftPanel && <InfoPanel />}
      {/* UI Overlays */}
      <NavigationModeSelector />
      {showLeftPanel && <InfoPanel />}
      {showRightPanel && <PolicyControlPanel />}
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
