import React, { useRef, useEffect, useState } from 'react'
import { useThree, useFrame } from '@react-three/fiber'
import { OrbitControls, FlyControls, FirstPersonControls, PointerLockControls } from '@react-three/drei'
import { useSimulationStore } from '../store/simulationStore'
import * as THREE from 'three'

function CameraControls() {
  const { camera, gl } = useThree()
  const [controlMode, setControlMode] = useState('orbit')
  const [isLocked, setIsLocked] = useState(false)
  const controlsRef = useRef()
  
  // Movement state for FPS mode
  const movement = useRef({
    forward: false,
    backward: false,
    left: false,
    right: false,
    speed: 20
  })

  // Store control mode in global state
  useEffect(() => {
    const store = useSimulationStore.getState()
    store.setControlMode = (mode) => {
      setControlMode(mode)
      
      // Reset camera for different modes
      if (mode === 'fps') {
        camera.position.set(0, 5, 50)
        camera.lookAt(0, 5, 0)
      } else if (mode === 'fly') {
        camera.position.set(50, 30, 50)
      }
    }
  }, [camera])

  // Keyboard controls for FPS mode
  useEffect(() => {
    if (controlMode !== 'fps') return

    const handleKeyDown = (e) => {
      switch(e.code) {
        case 'KeyW':
        case 'ArrowUp':
          movement.current.forward = true
          break
        case 'KeyS': 
        case 'ArrowDown':
          movement.current.backward = true
          break
        case 'KeyA':
        case 'ArrowLeft':
          movement.current.left = true
          break
        case 'KeyD':
        case 'ArrowRight':
          movement.current.right = true
          break
        case 'ShiftLeft':
          movement.current.speed = 40
          break
      }
    }

    const handleKeyUp = (e) => {
      switch(e.code) {
        case 'KeyW':
        case 'ArrowUp':
          movement.current.forward = false
          break
        case 'KeyS':
        case 'ArrowDown':
          movement.current.backward = false
          break
        case 'KeyA':
        case 'ArrowLeft':
          movement.current.left = false
          break
        case 'KeyD':
        case 'ArrowRight':
          movement.current.right = false
          break
        case 'ShiftLeft':
          movement.current.speed = 20
          break
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    window.addEventListener('keyup', handleKeyUp)

    return () => {
      window.removeEventListener('keydown', handleKeyDown)
      window.removeEventListener('keyup', handleKeyUp)
    }
  }, [controlMode])

  // Update camera position for FPS mode
  useFrame((state, delta) => {
    if (controlMode !== 'fps' || !isLocked) return

    const speed = movement.current.speed * delta
    const direction = new THREE.Vector3()
    
    camera.getWorldDirection(direction)
    direction.y = 0
    direction.normalize()

    const right = new THREE.Vector3()
    right.crossVectors(direction, camera.up).normalize()

    if (movement.current.forward) {
      camera.position.addScaledVector(direction, speed)
    }
    if (movement.current.backward) {
      camera.position.addScaledVector(direction, -speed)
    }
    if (movement.current.left) {
      camera.position.addScaledVector(right, -speed)
    }
    if (movement.current.right) {
      camera.position.addScaledVector(right, speed)
    }

    // Keep camera at human eye level
    camera.position.y = Math.max(2, Math.min(100, camera.position.y))
  })

  // Render different control types based on mode
  if (controlMode === 'orbit') {
    return (
      <OrbitControls
        ref={controlsRef}
        enablePan={true}
        enableZoom={true}
        enableRotate={true}
        minDistance={5}
        maxDistance={200}
        maxPolarAngle={Math.PI * 0.85}
        minPolarAngle={0.1}
        panSpeed={1.5}
        rotateSpeed={0.8}
        zoomSpeed={1.2}
        target={[0, 0, 0]}
        // Enable damping for smoother movement
        enableDamping={true}
        dampingFactor={0.05}
        // Allow underground navigation
        screenSpacePanning={true}
        // Mouse buttons
        mouseButtons={{
          LEFT: THREE.MOUSE.ROTATE,
          MIDDLE: THREE.MOUSE.DOLLY,
          RIGHT: THREE.MOUSE.PAN
        }}
      />
    )
  }

  if (controlMode === 'fly') {
    return (
      <FlyControls
        movementSpeed={30}
        rollSpeed={0.5}
        dragToLook={true}
        autoForward={false}
      />
    )
  }

  if (controlMode === 'fps') {
    return (
      <PointerLockControls
        onLock={() => setIsLocked(true)}
        onUnlock={() => setIsLocked(false)}
        selector="#fps-button"
      />
    )
  }

  return null
}

// Navigation mode selector UI
export function NavigationModeSelector() {
  const [currentMode, setCurrentMode] = useState('orbit')

  const modes = [
    { id: 'orbit', name: 'Orbit View', icon: '🔄', description: 'Rotate around the city' },
    { id: 'fly', name: 'Fly Mode', icon: '✈️', description: 'Free flight navigation' },
    { id: 'fps', name: 'Walk Mode', icon: '🚶', description: 'First-person exploration' }
  ]

  const handleModeChange = (mode) => {
    setCurrentMode(mode)
    const store = useSimulationStore.getState()
    if (store.setControlMode) {
      store.setControlMode(mode)
    }

    // Show instructions for FPS mode
    if (mode === 'fps') {
      alert('Click to lock pointer. Use WASD or Arrow keys to move. Hold Shift to run. Press ESC to unlock.')
    }
  }

  return (
    <div style={{
      position: 'absolute',
      top: '20px',
      left: '50%',
      transform: 'translateX(-50%)',
      zIndex: 100,
      display: 'flex',
      gap: '10px',
      background: 'rgba(0, 0, 0, 0.8)',
      backdropFilter: 'blur(10px)',
      padding: '10px',
      borderRadius: '15px',
      border: '1px solid rgba(255, 255, 255, 0.1)'
    }}>
      {modes.map(mode => (
        <button
          key={mode.id}
          id={mode.id === 'fps' ? 'fps-button' : undefined}
          onClick={() => handleModeChange(mode.id)}
          style={{
            background: currentMode === mode.id 
              ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
              : 'rgba(255, 255, 255, 0.1)',
            border: 'none',
            borderRadius: '10px',
            padding: '10px 15px',
            color: 'white',
            cursor: 'pointer',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '5px',
            transition: 'all 0.3s',
            minWidth: '80px'
          }}
          title={mode.description}
        >
          <span style={{ fontSize: '20px' }}>{mode.icon}</span>
          <span style={{ fontSize: '11px' }}>{mode.name}</span>
        </button>
      ))}
      
      {/* Navigation help */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        padding: '0 10px',
        borderLeft: '1px solid rgba(255, 255, 255, 0.2)',
        color: 'rgba(255, 255, 255, 0.7)',
        fontSize: '11px'
      }}>
        {currentMode === 'orbit' && '🖱️ Left: Rotate | Right: Pan | Scroll: Zoom'}
        {currentMode === 'fly' && '🖱️ Drag to look | WASD: Move | Q/E: Up/Down'}
        {currentMode === 'fps' && '🖱️ Click to start | WASD: Move | Shift: Run'}
      </div>
    </div>
  )
}

export default CameraControls
