# Delhi Digital Twin - Technical Documentation 🛠️

Complete technical specifications, architecture details, and implementation information.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                  FRONTEND (React + Three.js)                     │
│  Port: 3000 | Framework: Vite 5.4.20                            │
│  • CitySceneImproved.jsx - Main 3D visualization                │
│  • PolicyControlPanel.jsx - Emergency protocol control           │
│  • CameraPresets.jsx - CCTV camera system                       │
│  • simulationStore.js - Zustand state management                │
└────────────────────────┬────────────────────────────────────────┘
                         │ axios/fetch API calls
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND API (Flask)                           │
│  Port: 5000 | Framework: Flask + Flask-CORS                     │
│  • /api/health - Health check                                  │
│  • /api/baseline - Get zone metrics                             │
│  • /api/run - Execute simulation                                │
│  • /api/recommendations - AI suggestions                        │
│  • /api/corridor/* - Detailed endpoints                         │
└────────────────────────┬────────────────────────────────────────┘
                         │ Python model imports
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  SIMULATION ENGINE (Python)                      │
│  • corridor_network.py (545 lines) - Graph & routing            │
│  • traffic_simulator.py (385 lines) - BPR congestion model      │
│  • emissions.py (430 lines) - PM2.5 & AQI calculation           │
│  • interventions.py (420 lines) - Policy testing engine         │
└────────────────────────┬────────────────────────────────────────┘
                         │ CSV file reading
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     DATA LAYER (CSV Files)                       │
│  • corridor_segments.csv (30 segments)                          │
│  • intersections.csv (40 intersections)                         │
│  • od_matrix.csv (129 origin-destination pairs)                │
│  • city_zones.csv (5 zones with metadata)                       │
│  • traffic.csv, weather.csv (historical data)                   │
└─────────────────────────────────────────────────────────────────┘
```

## Frontend Architecture

### React Component Structure

```
src/
├── App.jsx                          - Main entry, app layout
├── components/
│   ├── CitySceneImproved.jsx       - 3D rendering (Three.js)
│   ├── CitySceneRealistic.jsx      - Alternative realistic view
│   ├── PolicyControlPanel.jsx      - Right panel with emergency button
│   ├── ControlPanel.jsx            - General controls
│   ├── InfoPanel.jsx               - Left panel showing metrics
│   ├── CameraPresets.jsx           - CCTV camera system (11 presets)
│   ├── CameraControls.jsx          - Camera movement utilities
│   ├── CameraManager.jsx           - Camera state management
│   ├── PlaybackController.jsx      - Simulation playback
│   ├── Timeline.jsx                - Time scrubber
│   ├── Legend.jsx                  - Map legend
│   ├── PollutionVisualization.jsx  - Heatmap rendering
│   ├── EnhancedTrafficSystem.jsx   - Vehicle animation
│   ├── ClimateVisualization.jsx    - Climate data overlay
│   ├── ImpactResultsModal.jsx      - Results popup
│   └── TrafficSystem.jsx           - Traffic rendering
├── store/
│   └── simulationStore.js          - Zustand state management
├── models/
│   ├── corridor_network.py         - Python model (imported)
│   ├── traffic_simulator.py        - Python model (imported)
│   ├── emissions.py                - Python model (imported)
│   └── interventions.py            - Python model (imported)
├── index.css                       - Global styles
└── main.jsx                        - App bootstrap
```

### Key Components

#### CitySceneImproved.jsx
- Main 3D visualization using Three.js + react-three-fiber
- Renders:
  - 30 road segments
  - 40 intersections
  - 3 landmarks (India Gate, Lotus Temple, Red Fort)
  - 5 zone boundaries
  - Animated vehicles
  - AQI heatmap overlay
- Features:
  - OrbitControls for camera movement
  - Post-processing (Bloom, DOF effects)
  - 60 FPS performance target
  - Real-time AQI color coding

#### PolicyControlPanel.jsx
- Located on right side of screen
- Contains:
  - `🚨 EMERGENCY PROTOCOL ALPHA` button
  - Emergenc status display
  - Live status messages during execution
  - Emergency protocol status: Detecting → Analyzing → Deploying
- Functions:
  - `startEmergencyProtocol()` - Initiates 3-phase response
  - `applyIntervention()` - Updates zone metrics
  - Real-time state updates with animations

#### simulationStore.js (Zustand State)
```javascript
// Key state properties:
- simulationData: Current zone metrics
- emergencyActive: Emergency protocol running state
- emergencyStatus: Current phase (Detecting/Analyzing/Deploying)
- emergencyResults: Protocol results
- selectedZone: Currently selected zone
- cameraPreset: Active camera view
- interventions: Applied intervention list

// Key methods:
- startEmergencyProtocol() - Async 3-phase protocol
- applyIntervention(type, zones) - Apply intervention
- updateSimulation(data) - Update metrics
- resetSimulation() - Restore baseline
```

### Emergency Protocol Flow

**Phase 1: Detection (Async, 2-3 seconds)**
```javascript
// Detects AQI spike across zones
emergencyStatus = "Detecting AQI anomalies...";
// Analyzes zone-level AQI increase
// Identifies priority zones (highest AQI first)
```

**Phase 2: Analysis (Async, 2-3 seconds)**
```javascript
// Evaluates intervention strategies
emergencyStatus = "Analyzing intervention strategies...";
// Calculates impact per intervention
// Prioritizes by effectiveness
```

**Phase 3: Deployment (Async, 2-3 seconds)**
```javascript
// Executes interventions
emergencyStatus = "Deploying emergency measures...";
// Calls /api/run with type: 'emergency'
// Updates all zone metrics
// Shows real-time AQI changes
```

## Backend API

### Flask Application (backend/app.py)

**Initialization:**
```python
from flask import Flask, jsonify, request
from flask_cors import CORS
from src.models.corridor_network import CorridorNetwork
from src.models.traffic_simulator import TrafficSimulator
from src.models.emissions import EmissionsModel
from src.models.interventions import InterventionEngine

app = Flask(__name__)
CORS(app)

# Initialize models on startup
corridor_network = CorridorNetwork()
traffic_simulator = TrafficSimulator(corridor_network)
emissions_model = EmissionsModel()
intervention_engine = InterventionEngine(corridor_network)
```

### API Endpoints

#### 1. GET /api/health
**Purpose:** Backend health check

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-11-15T10:30:00Z"
}
```

#### 2. GET /api/baseline
**Purpose:** Get current zone metrics (baseline scenario)

**Response:**
```json
{
  "zones": [
    {
      "id": "Z01",
      "name": "Connaught Place",
      "aqi": 328,
      "pm25": 185,
      "no2": 95,
      "speed": 45,
      "traffic": 8750,
      "energy": 125,
      "heat_island": 3.2,
      "health_impact": 450
    },
    // ... more zones
  ]
}
```

#### 3. POST /api/run
**Purpose:** Execute simulation with intervention

**Request Body:**
```json
{
  "intervention": "truck_ban|odd_even|lane_addition|signal_tuning|dynamic_rerouting|emergency",
  "zones": [1, 2, 3, 4, 5],
  "parameters": {
    "truck_ban_start": 6,
    "truck_ban_end": 12
  }
}
```

**Response:**
```json
{
  "baseline": { /* baseline metrics */ },
  "intervention": { /* intervention metrics */ },
  "impact": {
    "aqi_reduction": 145,
    "speed_improvement": 18.5,
    "traffic_reduction": 47.2,
    "lives_saved": 362
  }
}
```

#### 4. GET /api/recommendations
**Purpose:** Get AI policy recommendations

**Response:**
```json
{
  "recommendations": [
    {
      "rank": 1,
      "intervention": "Truck Ban (6-12 AM)",
      "confidence": 0.89,
      "aqi_reduction": 63,
      "lives_saved": 158,
      "cost": 50000,
      "roi": 3.16,
      "timeline": "immediate"
    },
    // ... more recommendations
  ]
}
```

#### 5. GET /api/corridor/zones/<zone_id>
**Purpose:** Get detailed zone information

**Response:**
```json
{
  "zone_id": "Z01",
  "segments": [1, 2, 3, 5, 6],
  "aqi": 328,
  "traffic_volume": 8750,
  "avg_speed": 45,
  "pm25": 185,
  "no2": 95
}
```

#### 6. POST /api/corridor/intervention
**Purpose:** Apply specific intervention

**Request Body:**
```json
{
  "intervention_type": "truck_ban",
  "zones": [1, 2],
  "start_time": 6,
  "end_time": 12
}
```

## Simulation Models

### 1. corridor_network.py (545 lines)

**CorridorNetwork Class:**

```python
class CorridorNetwork:
    def __init__(self):
        self.segments = {}      # 30 segments
        self.intersections = {} # 40 intersections
        self.graph = nx.DiGraph()  # NetworkX graph
        self.od_matrix = {}     # 129 origin-destination pairs
        self.load_data()
    
    def load_data(self):
        """Load segments, intersections, OD pairs from CSV"""
        # Reads corridor_segments.csv, intersections.csv, od_matrix.csv
    
    def add_segment(self, segment_id, origin, destination, length, lanes):
        """Add road segment to network"""
        self.graph.add_edge(origin, destination, segment_id=segment_id)
    
    def shortest_path(self, origin, destination):
        """Dijkstra shortest path"""
        return nx.shortest_path(self.graph, origin, destination)
    
    def get_segment_flow(self, segment_id):
        """Get current flow (vehicles/hour) on segment"""
    
    def get_topology_stats(self):
        """Return network statistics"""
        # Returns: segments, intersections, zones, total_length_km, etc.
```

**Key Data:**
- 30 segments: Ring Road, NH8, Delhi-Gurgaon Expressway, local streets
- 40 intersections: Each with signal timing (cycle, green_time)
- 8 zones: Connaught Place, Karol Bagh, Dwarka, Rohini, Saket, etc.
- 129 OD pairs: Source-destination combinations

### 2. traffic_simulator.py (385 lines)

**TrafficSimulator Class:**

```python
class TrafficSimulator:
    def __init__(self, corridor_network):
        self.network = corridor_network
        self.baseline_flow = 43850  # vehicles/hour
    
    def calculate_speed(self, segment_id):
        """BPR Model: Speed = FreeSpeed / (1 + 0.15 * (v/c)^4)"""
        flow = self.network.get_segment_flow(segment_id)
        capacity = segment_data['capacity']
        v_c_ratio = flow / capacity
        free_speed = segment_data['free_speed']
        speed = free_speed / (1 + 0.15 * (v_c_ratio ** 4))
        return speed
    
    def calculate_travel_time(self, segment_id, distance):
        """Travel time = distance / speed (in minutes)"""
        speed = self.calculate_speed(segment_id)
        travel_time = distance / speed * 60
        return travel_time
    
    def simulate_baseline(self):
        """Run baseline traffic simulation"""
        results = {}
        for segment in self.network.segments:
            results[segment] = {
                'flow': flow,
                'speed': self.calculate_speed(segment),
                'travel_time': self.calculate_travel_time(segment, distance)
            }
        return results
    
    def apply_intervention(self, intervention_type, zones):
        """Modify flow based on intervention"""
        # truck_ban: reduce heavy vehicles
        # odd_even: reduce total vehicles by 50%
        # lane_addition: increase capacity
        # signal_tuning: improve flow
```

**BPR Congestion Model:**
```
Speed = FreeSpeed / (1 + 0.15 * (v/c)^4)

Where:
- v/c = volume/capacity ratio
- When v/c = 1.0 (at capacity): Speed = FreeSpeed / 1.15
- When v/c = 1.5 (overcapacity): Speed drops significantly
```

**Baseline Metrics:**
- Total Traffic: 43,850 vehicles/hour
- Average Speed: 54.2 km/h
- Average Travel Time: 4.4 minutes per segment
- Capacity Utilization: 85-95% on major corridors

### 3. emissions.py (430 lines)

**EmissionsModel Class:**

```python
class EmissionsModel:
    def __init__(self):
        # Emission factors (g/km) by vehicle type
        self.emission_factors = {
            'car': 0.5,      # Petrol cars
            'truck': 2.5,    # Heavy vehicles
            'bus': 1.8,      # Public transport
            'auto': 0.6      # Auto-rickshaws
        }
        self.baseline_pm25 = {}
    
    def calculate_emissions(self, segment_id, flow, vehicle_types):
        """Calculate PM2.5 from vehicle flow"""
        total_emissions = 0
        for vehicle_type, count in vehicle_types.items():
            emissions = count * self.emission_factors[vehicle_type]
            total_emissions += emissions
        return total_emissions
    
    def gaussian_dispersion(self, emission, distance):
        """Model pollutant spread using Gaussian plume"""
        concentration = emission / (distance ** 2)
        return concentration
    
    def calculate_aqi(self, pm25_concentration):
        """Convert PM2.5 to AQI"""
        # AQI calculation based on CPCB standards
        if pm25 <= 30:
            aqi = (pm25 / 30) * 50          # Good (0-50)
        elif pm25 <= 60:
            aqi = 50 + ((pm25 - 30) / 30) * 50   # Moderate (51-100)
        # ... more ranges
        return aqi
    
    def get_zone_aqi(self, zone_id):
        """Get zone-level AQI (aggregate nearby segments)"""
        zone_segments = self.network.get_zone_segments(zone_id)
        zone_aqi = np.mean([segment['aqi'] for segment in zone_segments])
        return zone_aqi
```

**Baseline AQI Range:**
- Zone 1 (Connaught Place): 328
- Zone 2 (Karol Bagh): 315
- Zone 3 (Dwarka): 342 (highest)
- Zone 4 (Rohini): 305
- Zone 5 (Saket): 320
- Average: 321 (Hazardous level)

### 4. interventions.py (420 lines)

**InterventionEngine Class:**

```python
class InterventionEngine:
    def __init__(self, corridor_network):
        self.network = corridor_network
        self.interventions = {}
        self.baseline_state = None
    
    def truck_ban(self, zones, start_hour=6, end_hour=12):
        """Ban heavy vehicles 6-12 AM in specific zones"""
        # Reduces emissions by 40-50% (trucks are 50% of emissions)
        # Expected AQI reduction: 22 points
    
    def odd_even(self, zones):
        """Odd-even traffic rule - 50% vehicle reduction"""
        # Reduces total traffic flow by 50%
        # Expected AQI reduction: 45 points
        # Expected speed improvement: +20-30%
    
    def lane_addition(self, segment_ids, lanes_to_add=1):
        """Add lanes to increase capacity"""
        # Increases capacity by lanes_to_add * lane_capacity
        # Expected speed improvement: +10-15%
    
    def signal_tuning(self, intersection_ids):
        """Optimize signal timing"""
        # Adjusts cycle time and green phase
        # Expected speed improvement: +5-10%
    
    def dynamic_rerouting(self, od_pairs):
        """Redistribute traffic across alternate routes"""
        # Uses Dijkstra to find least-congested paths
        # Expected speed improvement: +8-12%
    
    def emergency_protocol(self, zones):
        """Combine all interventions for maximum impact"""
        # Activates: truck ban + odd_even + dynamic_rerouting
        # Expected AQI reduction: 60 points
        # Expected speed improvement: +31%
    
    def calculate_impact(self, baseline, intervention):
        """Calculate intervention effectiveness"""
        aqi_reduction = baseline['aqi'] - intervention['aqi']
        speed_improvement = (intervention['speed'] - baseline['speed']) / baseline['speed']
        lives_saved = aqi_reduction * 2.5
        return {'aqi_reduction': aqi_reduction, 'lives_saved': lives_saved}
    
    def rollback(self):
        """Restore to baseline state"""
        # Reverts all active interventions
```

**Intervention Results:**

| Intervention | AQI Reduction | Speed Gain | Lives Saved |
|---|---|---|---|
| Truck Ban | -22 | +5% | 55 |
| Odd-Even | -45 | +15% | 113 |
| Lane Addition | -8 | +8% | 20 |
| Signal Tuning | -5 | +3% | 12 |
| Dynamic Rerouting | -10 | +8% | 25 |
| Emergency (all) | -60 | +31% | 150 |

## State Management (Zustand)

### simulationStore.js

```javascript
import create from 'zustand';

const useSimulationStore = create((set) => ({
  // State
  simulationData: null,
  emergencyActive: false,
  emergencyStatus: null,
  emergencyResults: null,
  selectedZone: null,
  cameraPreset: 'overview',
  interventions: [],
  
  // Actions
  startEmergencyProtocol: async () => {
    set({ emergencyActive: true });
    
    // Phase 1: Detection
    set({ emergencyStatus: 'Detecting AQI anomalies...' });
    await sleep(2000);
    
    // Phase 2: Analysis
    set({ emergencyStatus: 'Analyzing intervention strategies...' });
    await sleep(2000);
    
    // Phase 3: Deployment
    set({ emergencyStatus: 'Deploying emergency measures...' });
    const response = await fetch('/api/run', {
      method: 'POST',
      body: JSON.stringify({
        intervention: 'emergency',
        zones: [1, 2, 3, 4, 5]
      })
    });
    const results = await response.json();
    set({ 
      emergencyResults: results,
      emergencyStatus: 'Complete: ' + results.impact.lives_saved + ' lives saved'
    });
  },
  
  applyIntervention: (type, zones) => {
    // Apply intervention and update state
  },
  
  updateSimulation: (data) => {
    set({ simulationData: data });
  }
}));
```

## Data Files

### corridor_segments.csv
```csv
segment_id,name,origin_intersection,destination_intersection,zone_id,length_km,lanes,free_speed_kmh,capacity_vph
1,Ring Road North,I1,I2,Z01,2.5,4,80,2200
2,Ring Road East,I2,I3,Z02,3.1,4,80,2200
...
30,Local Street 10,I39,I40,Z05,1.8,2,40,800
```

### intersections.csv
```csv
intersection_id,name,lat,lng,signal_cycle,green_phase_ns,green_phase_ew
1,Connaught Place,28.6315,77.1863,120,60,60
2,Karol Bagh,28.6425,77.2100,120,50,70
...
40,Delhi Gate,28.6395,77.2430,120,55,65
```

### od_matrix.csv
```csv
origin,destination,demand_per_hour
I1,I10,450
I1,I15,320
I1,I20,280
...
(129 total OD pairs)
```

### city_zones.csv
```csv
zone_id,zone_name,latitude,longitude,population,area_sqkm,boundary_type
Z01,Connaught Place,28.6315,77.1863,85000,12.5,business
Z02,Karol Bagh,28.6425,77.2100,120000,18.2,residential
Z03,Dwarka,28.5900,77.0475,200000,35.0,mixed
Z04,Rohini,28.7855,77.0470,150000,28.0,residential
Z05,Saket,28.5200,77.1870,95000,16.5,residential
```

## Performance Metrics

### Simulation Performance
- **Baseline Run:** <1 second
- **Intervention Run:** 1-2 seconds
- **Emergency Protocol:** 6-8 seconds (3 phases)
- **API Response Time:** <200ms average

### UI Performance
- **Frame Rate:** 60 FPS (3D scene)
- **Memory Usage:** ~150 MB (frontend + backend)
- **Bundle Size:** 2.5 MB (minified)

### Data Coverage
- **Segments:** 30 (covering major corridors)
- **Intersections:** 40 (with signal timing)
- **OD Pairs:** 129 (realistic demand)
- **Zones:** 5 major zones
- **Network:** 74.9 km total length, 108 total lanes

## Emergency Protocol Sequence

### Trigger
- User clicks `🚨 EMERGENCY PROTOCOL ALPHA` button

### Phase 1: Detection (2-3 seconds)
```python
# Backend
zones_with_high_aqi = [z for z in zones if aqi[z] > 300]
priority_zones = sorted(zones_with_high_aqi, key=aqi, reverse=True)

# Frontend state update
emergencyStatus = "Detecting AQI anomalies..."
# UI shows status with animation
```

### Phase 2: Analysis (2-3 seconds)
```python
# Backend
best_interventions = []
for intervention in ['truck_ban', 'odd_even', 'dynamic_rerouting']:
    impact = simulate_intervention(intervention, priority_zones)
    best_interventions.append({
        'type': intervention,
        'aqi_reduction': impact['aqi_reduction'],
        'effectiveness': impact['effectiveness_score']
    })

# Frontend state update
emergencyStatus = "Analyzing intervention strategies..."
```

### Phase 3: Deployment (2-3 seconds)
```python
# Backend
# Apply emergency intervention (combination of all measures)
results = {
    'aqi': updated_aqi_values,
    'speed': updated_speed_values,
    'traffic': updated_traffic_values,
    'lives_saved': estimate_lives_saved(aqi_reduction),
    'timeline': 'completed'
}

# Frontend state update
emergencyStatus = "Deploying emergency measures..."
# Then shows: "Complete: 362 lives saved"
# UI updates show all new metrics
```

## Integration Points

### Frontend → Backend Communication
- Uses `axios` for HTTP requests
- CORS enabled on backend
- Default base URL: `http://127.0.0.1:5000`

### Backend → Python Models
- Imports models directly: `from src.models import *`
- Models loaded on app startup
- In-memory computation (no database)

### Data Flow for Emergency Protocol

```
User clicks button
    ↓
Store: startEmergencyProtocol()
    ↓
Set emergencyActive = true
    ↓
Display "Detecting..." (2s)
    ↓
Display "Analyzing..." (2s)
    ↓
POST /api/run with type='emergency'
    ↓
Backend simulates intervention
    ↓
Returns impact metrics
    ↓
Frontend updates all zone AQIs
    ↓
Display "Complete: X lives saved"
    ↓
User sees real-time changes in 3D scene
```

## Visualization Outputs

### Generated Files
- `emergency_protocol_complete.html` - Main dashboard
- `interactive_dashboard.html` - 4-panel Plotly charts
- `impact_metrics.html` - Key metrics focused
- `pollutant_analysis.html` - PM2.5 & NO2 comparison
- `emergency_protocol_analysis.png` - Static 300 DPI image

### Charts Generated
1. AQI Comparison (baseline vs emergency)
2. AQI Reduction per zone
3. Speed Improvement analysis
4. Speed Improvement percentage
5. Traffic Volume comparison
6. Traffic Reduction percentage
7. Health Impact Score
8. Pollutant Level Analysis

## Deployment Checklist

- [ ] Verify all CSV files in `data/` directory
- [ ] Backend: `python backend/app.py` running
- [ ] Frontend: `npm run dev` running
- [ ] API endpoints responding (check `/api/health`)
- [ ] 3D scene rendering at 60 FPS
- [ ] Emergency protocol button functional
- [ ] Visualizations generated in `visualization_outputs/`

---

**Version:** 1.0  
**Last Updated:** 2025-11-15  
**Complexity:** Advanced (5500+ lines of code)
