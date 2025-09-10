import { useEffect } from 'react'
import { useThree } from '@react-three/fiber'
import { useSimulationStore } from '../store/simulationStore'

function CameraManager() {
  const { camera } = useThree()
  
  useEffect(() => {
    // Store camera reference in global store
    const { setCameraRef } = useSimulationStore.getState()
    setCameraRef(camera)
    
    return () => {
      // Clean up on unmount
      setCameraRef(null)
    }
  }, [camera])
  
  return null
}

export default CameraManager
