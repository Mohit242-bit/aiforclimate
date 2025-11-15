import { create } from 'zustand'
import axios from 'axios'

// Configure axios to use backend at port 5000
axios.defaults.baseURL = 'http://127.0.0.1:5000'
axios.defaults.timeout = 10000

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
  emergencyStatus: null,
  emergencyActive: false,
  emergencyResults: null,
  baselineZones: null, // Store baseline before emergency
  showResultsModal: false,

  setTime: (t) => set({ time: t }),
  togglePlay: () => set({ playing: !get().playing }),
  setSpeed: (s) => set({ speed: s }),
  
  // Trigger emergency protocol
  startEmergencyProtocol: async () => {
    // Store baseline zones BEFORE emergency
    const baselineZones = JSON.parse(JSON.stringify(get().zones))
    set({ 
      emergencyActive: true, 
      emergencyStatus: '🚨 INITIATING EMERGENCY PROTOCOL...',
      baselineZones: baselineZones
    })
    
    try {
      // Phase 1: Detect crisis (2-3 seconds)
      set({ emergencyStatus: '🚨 PHASE 1: Detecting AQI anomalies...' })
      await new Promise(r => setTimeout(r, 2000))
      
      // Phase 2: Analyze interventions (2-3 seconds)
      set({ emergencyStatus: '🤖 PHASE 2: Analyzing intervention strategies...' })
      
      const result = await get().runScenario({
        type: 'emergency',
        zones: [1, 2, 3, 4, 5],
        parameters: { severity: 'CRITICAL' }
      })
      
      await new Promise(r => setTimeout(r, 1500))
      
      // Phase 3: Deployment (2-3 seconds)
      set({ emergencyStatus: '⚡ PHASE 3: Deploying emergency measures...' })
      await new Promise(r => setTimeout(r, 1500))
      
      // Calculate lives saved using BASELINE vs RESULT
      const oldAqi = baselineZones.reduce((sum, z) => sum + z.aqi, 0) / baselineZones.length
      const newAqi = result?.zones?.reduce((sum, z) => sum + z.aqi, 0) / (result?.zones?.length || 1) || oldAqi
      const aqiReduction = Math.max(0, oldAqi - newAqi)
      const livesSaved = Math.round(aqiReduction * 2.5)
      
      console.log(`[Emergency] Baseline AQI: ${oldAqi.toFixed(1)}, New AQI: ${newAqi.toFixed(1)}, Reduction: ${aqiReduction.toFixed(1)}`)
      
      const emergencyResults = {
        baselineAqi: Math.round(oldAqi),
        newAqi: Math.round(newAqi),
        aqiReduction: Math.round(aqiReduction),
        livesSaved: livesSaved,
        baselineZones: baselineZones,
        emergencyZones: result?.zones || get().zones
      }
      
      set({ 
        emergencyStatus: `✅ COMPLETE: ${livesSaved} lives saved | AQI reduced by ${Math.round(aqiReduction)} points`,
        zones: result?.zones || get().zones,
        emergencyResults: emergencyResults,
        showResultsModal: true // Show modal
      })
      
      // Trigger graph generation
      console.log('[Emergency] Triggering graph generation...')
      try {
        await axios.post('/api/generate_graphs', {
          baseline: baselineZones,
          emergency: result?.zones,
          timestamp: new Date().toISOString()
        })
        console.log('[Emergency] ✅ Graphs generated successfully')
      } catch (graphErr) {
        console.warn('[Emergency] Graph generation skipped:', graphErr.message)
      }
      
      return result
    } catch (e) {
      console.error('Emergency protocol failed:', e)
      set({ 
        emergencyStatus: `❌ ERROR: ${e.message || 'Protocol failed - backend may be offline'}`
      })
      throw e
    }
  },
  
  resetEmergencyProtocol: () => set({ 
    triggerEmergencyProtocol: false, 
    emergencyActive: false, 
    emergencyStatus: null,
    showResultsModal: false,
    emergencyResults: null
  }),
  
  closeResultsModal: () => set({ showResultsModal: false }),

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
      console.log('[API] GET /api/baseline')
      const res = await axios.get('/api/baseline')
      console.log('[API] Baseline data received:', res.data)
      set({ currentData: res.data, zones: res.data.zones })
    } catch (e) {
      console.warn('[API] Backend not running or fetch failed:', e.message)
      // Keep default local values
    }
  },

  runScenario: async (payload) => {
    try {
      console.log('[API] POST /api/run with payload:', payload)
      const res = await axios.post('/api/run', payload)
      console.log('[API] Response received with', res.data.zones?.length, 'zones')
      
      if (res.data.zones && res.data.zones.length > 0) {
        const avgAqi = res.data.zones.reduce((sum, z) => sum + z.aqi, 0) / res.data.zones.length
        console.log('[API] Average AQI after intervention:', avgAqi.toFixed(1))
      }
      
      // Update zones from response
      if (res.data.zones) {
        set({ currentData: res.data, zones: res.data.zones })
      }
      return res.data
    } catch (e) {
      console.error('[API] Scenario run failed:', e.message)
      console.error('[API] Response data:', e.response?.data)
      
      // If backend is offline, simulate the intervention locally
      if (e.code === 'ECONNREFUSED' || e.response?.status >= 500) {
        console.warn('[API] Backend offline, simulating intervention locally...')
        const currentZones = get().zones
        const intervention_type = payload.type
        
        let aqiReduction = 0
        switch (intervention_type) {
          case 'emergency':
            aqiReduction = 60
            break
          case 'truck_ban':
            aqiReduction = 22
            break
          case 'odd_even':
            aqiReduction = 45
            break
          default:
            aqiReduction = 10
        }
        
        const updatedZones = currentZones.map(z => ({
          ...z,
          aqi: Math.max(50, z.aqi - aqiReduction)
        }))
        
        const localData = {
          zones: updatedZones,
          intervention: intervention_type,
          simulated_locally: true
        }
        
        set({ currentData: localData, zones: updatedZones })
        return localData
      }
      
      throw e
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
