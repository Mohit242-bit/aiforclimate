import { create } from 'zustand'
import axios from 'axios'

export const useSimulationStore = create((set, get) => ({
  time: 0,
  playing: false,
  speed: 1,
  zones: [
    { id: 1, name: 'Connaught Place', aqi: 220, energy: 1500, heat: 0.6 },
    { id: 2, name: 'Karol Bagh', aqi: 200, energy: 1600, heat: 0.5 },
    { id: 3, name: 'Dwarka', aqi: 240, energy: 1400, heat: 0.7 },
    { id: 4, name: 'Rohini', aqi: 210, energy: 1700, heat: 0.55 },
    { id: 5, name: 'Saket', aqi: 230, energy: 1550, heat: 0.52 }
  ],
  currentIntervention: null,
  recommendations: [],
  currentData: null,
  cameraRef: null,
  controlsRef: null,
  currentCameraPreset: 'overview',
  
  // Emergency protocol state
  triggerEmergencyProtocol: false,

  setTime: (t) => set({ time: t }),
  togglePlay: () => set({ playing: !get().playing }),
  setSpeed: (s) => set({ speed: s }),
  
  // Trigger emergency protocol
  startEmergencyProtocol: () => set({ triggerEmergencyProtocol: true }),
  resetEmergencyProtocol: () => set({ triggerEmergencyProtocol: false }),

  // Camera control methods
  setCameraRef: (ref) => set({ cameraRef: ref }),
  setControlsRef: (ref) => set({ controlsRef: ref }),
  setCurrentCameraPreset: (preset) => set({ currentCameraPreset: preset }),

  applyIntervention: (intervention) => {
    set({ currentIntervention: intervention })
    
    // Apply intervention effects to zones
    if (intervention && intervention.zones && intervention.zones.length > 0) {
      const currentZones = get().zones
      const updatedZones = currentZones.map(zone => {
        if (intervention.zones.includes(zone.id)) {
          // Apply AQI reduction based on intervention type
          let aqiReduction = 0
          switch (intervention.type) {
            case 'truck_restriction':
            case 'truck_ban':
              aqiReduction = 22
              break
            case 'green_cover':
              aqiReduction = 18
              break
            case 'signal_optimization':
              aqiReduction = 12
              break
            case 'retrofit':
              aqiReduction = 15
              break
            default:
              aqiReduction = 10
          }
          
          return {
            ...zone,
            aqi: Math.max(50, zone.aqi - aqiReduction) // Minimum AQI of 50
          }
        }
        return zone
      })
      
      set({ zones: updatedZones })
      console.log(`Applied intervention: ${intervention.name}`, updatedZones)
    }
  },

  fetchSimulationData: async () => {
    try {
      const res = await axios.get('/api/baseline')
      const data = res.data
      set({ currentData: data, zones: data.zones })
    } catch (e) {
      // Fallback to local values
      console.warn('Backend not running, using local data')
    }
  },

  runScenario: async (payload) => {
    try {
      const res = await axios.post('/api/run', payload)
      set({ currentData: res.data, zones: res.data.zones })
      return res.data
    } catch (e) {
      console.error('Scenario run failed', e)
    }
  },

  getRecommendations: async () => {
    try {
      const res = await axios.get('/api/recommendations')
      set({ recommendations: res.data.recommendations })
    } catch (e) {
      console.warn('Using mock recommendations')
      set({ recommendations: [
        { id: 1, name: 'Green Corridors in Zones 3 & 5', impact: { aqi: -18, energy: -12, heat: -0.7 }, type: 'green_cover', zones: [3, 5] },
        { id: 2, name: 'Truck Ban 6–12 AM in Zone 2', impact: { aqi: -22, energy: -3, heat: -0.1 }, type: 'traffic_ban', zones: [2] },
        { id: 3, name: 'Reflective Roofs in Zone 1', impact: { aqi: -5, energy: -15, heat: -0.3 }, type: 'retrofit', zones: [1] },
      ] })
    }
  }
}))
