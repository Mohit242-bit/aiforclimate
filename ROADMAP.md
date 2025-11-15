#  Delhi Digital Twin - Implementation Roadmap

## Executive Summary
Build a **realistic, corridor-based traffic and AQI simulator** for Delhi that uses real road infrastructure, supports policy interventions (truck bans, lane additions, signal tuning), and couples traffic with energy/heat/AQI models.

**Timeline:** 12-16 days (iterative, parallel where possible)  
**Effort:** Medium-High (3-4 developers optimal)  
**Tech Stack:** Python (backend), React/Vite (frontend), Flask (API)  

---

##  PHASE BREAKDOWN

###  PHASE 0: FOUNDATION & DATA PREP (Days 1-2)

#### 0.1 Extract Delhi Corridor Data from Google Maps API
**Timeline:** 1 day  
**Effort:** Low  
**Status:**  Not Started

**Tasks:**
- Set up Google Maps API credentials (Routes + Directions API)
- Define key Delhi corridors (10-15 segments)
- Extract route geometry, distances, turns for each corridor
- Parse response  intermediate JSON format
- Validate extracted data (coordinates, distances make sense)

#### 0.2 Create Data Schemas & CSV Templates
**Timeline:** 0.5 day  
**Effort:** Low  
**Status:**  Not Started

**Schemas:**

**corridor_segments.csv:**
segment_id,from_intersection,to_intersection,length_km,lanes,speed_limit,is_one_way,zone_id,road_type,road_name
RR_001,INT_001,INT_002,2.5,4,60,0,1,primary,Ring Road West
RR_002,INT_002,INT_003,1.8,4,60,0,1,primary,Ring Road West

**intersections.csv:**
intersection_id,lat,lon,has_signal,cycle_time,green_time,road_name
INT_001,28.6139,77.2090,1,120,45,Ring Road & Pusa Road
INT_002,28.6152,77.2105,1,120,45,Ring Road & Delhi University

**od_matrix.csv:**
origin_intersection,dest_intersection,vehicles_per_hour,vehicle_type
INT_001,INT_010,500,car
INT_001,INT_010,150,truck

---

##  PHASE 1: CORRIDOR NETWORK ENGINE (Days 3-5)

#### 1.1 Build CorridorNetwork Class
**Timeline:** 2 days  
**Effort:** Medium  
**Status:**  Not Started

Code Location: src/models/corridor_network.py

Core Methods:
- Segment loader (from CSV)
- Intersection loader (from CSV)
- OD matrix loader
- Directed graph builder (networkx)
- Adjacency list creation
- Topology validation

#### 1.2 Implement Routing Engine (Dijkstra/A*)
**Timeline:** 1 day  
**Effort:** Low-Medium  
**Status:**  Not Started

Tasks:
- Implement Dijkstra's algorithm
- Implement A* with heuristic (lat/lon distance)
- Handle turn restrictions
- Support multiple OD pairs
- Return full path + total distance + time estimate

---

##  PHASE 2: TRAFFIC SIMULATION ENGINE (Days 6-8)

#### 2.1 Implement Macroscopic Traffic Flow Model
**Timeline:** 2 days  
**Effort:** Medium-High  
**Status:**  Not Started

Core Logic:
- Lane capacity constraints (vehicles/lane/hour)
- Speed-flow relationship (BPR curve or linear)
- Queue buildup at intersections
- Signal-based flow control
- Congestion feedback

#### 2.2 Implement Signal Timing & Queue Logic
**Timeline:** 1 day  
**Effort:** Low-Medium  
**Status:**  Not Started

Tasks:
- Implement signal cycles (red/green times)
- Implement queue buildup at signals
- Implement saturation flow
- Compute delay from signals
- Support signal timing changes

---

##  PHASE 3: AQI/ENERGY/HEAT COUPLING (Days 9-10)

#### 3.1 Update Simulation Engines to Use Real Corridor Flows
**Timeline:** 1 day  
**Effort:** Low  
**Status:**  Not Started

Tasks:
- Modify src/simulation.py to read flows from TrafficSimulator
- Replace synthetic traffic_flow with real corridor aggregation
- Update zone-level metrics (sum segment flows)

#### 3.2 Implement Emissions & Pollutant Dispersion
**Timeline:** 1 day  
**Effort:** Low-Medium  
**Status:**  Not Started

Tasks:
- Create src/models/emissions.py
- Compute segment-level emissions (vehicles  emission_factor)
- Implement simplified Gaussian plume for downwind dispersion
- Map emissions to zone-level pollution

---

##  PHASE 4: INTERVENTION ENGINE & API (Days 11-12)

#### 4.1 Implement Intervention Logic
**Timeline:** 1 day  
**Effort:** Low-Medium  
**Status:**  Not Started

Intervention types:
- Lane addition/removal
- Signal timing changes
- Segment closures
- Diversions/reroutes
- Traffic bans (time-based)

#### 4.2 Update Flask API Endpoints
**Timeline:** 1 day  
**Effort:** Low  
**Status:**  Not Started

New Endpoints:
- /api/corridor/baseline - baseline corridor data
- /api/corridor/run - run scenario with interventions
- /api/corridor/intervention - apply specific intervention
- /api/corridor/reroute - get rerouted paths after closure

---

##  PHASE 5: INTEGRATION & TESTING (Days 13-14)

#### 5.1 Integrate with Existing Policy Engine
**Timeline:** 0.5 day  
**Effort:** Low  
**Status:**  Not Started

#### 5.2 Write Unit Tests
**Timeline:** 1 day  
**Effort:** Medium  
**Status:**  Not Started

Test Coverage:
- CorridorNetwork graph construction
- Routing (Dijkstra)
- Traffic simulation (flows, speeds)
- Interventions (lane, signal, closure)
- API endpoints

#### 5.3 End-to-End Demo
**Timeline:** 0.5 day  
**Effort:** Low  
**Status:**  Not Started

---

##  PHASE 6: VISUALIZATION & FRONTEND (Days 15-16)

#### 6.1 Update Frontend to Show Corridor Data
**Timeline:** 1 day  
**Effort:** Medium  
**Status:**  Not Started

Tasks:
- Update src/App.jsx to show corridor network
- Add interactive map visualization
- Show segment-level traffic flows
- Show AQI heatmaps by zone
- Allow intervention input
- Display before/after comparison

#### 6.2 Create Demo Dashboard
**Timeline:** 0.5 day  
**Effort:** Low  
**Status:**  Not Started

---

##  FINAL DELIVERABLES

### Code Artifacts
src/models/corridor_network.py  Graph + routing
src/models/traffic_simulator.py  Flow simulation
src/models/emissions.py  CO2 & AQI
src/models/interventions.py  Policy changes
backend/corridor_api.py  New endpoints
tests/test_*.py  Unit tests

### Data Artifacts
data/corridor_segments.csv (50-100 rows)
data/intersections.csv (30-50 rows)
data/od_matrix.csv (100-200 rows)

---

##  TIMELINE SUMMARY

| Phase | Days | Status |
|-------|------|--------|
| Foundation | 1-2 |  Not Started |
| Corridor Network | 3-5 |  Not Started |
| Traffic Simulation | 6-8 |  Not Started |
| AQI/Energy Coupling | 9-10 |  Not Started |
| Interventions & API | 11-12 |  Not Started |
| Integration & Testing | 13-14 |  Not Started |
| Visualization | 15-16 |  Not Started |
| TOTAL | 16 days |  Not Started |

**Start:** Today  
**Target Completion:** 16 days (with 3-4 developers)

---

##  QUICK START

Action Items (Next 1 hour):
- Read this roadmap thoroughly
- Identify team roles
- Get Google Maps API key
- Create Phase 0 task tickets
- Start corridor extraction

Let's build this! 
