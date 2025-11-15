from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)
CORS(app)

# Try to import existing modules, but don't fail if they're missing
try:
    from src.simulation import load_data, compute_energy_demand, compute_aqi, compute_heat_island
    HAS_SIMULATION = True
except:
    HAS_SIMULATION = False
    print("[INFO] Running with mock data - simulation modules not loaded")

try:
    from corridor_api import corridor_api, init_corridor_models
    app.register_blueprint(corridor_api)
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    corridor_network, corridor_simulator, corridor_intervention, corridor_emissions = init_corridor_models(base_path)
    print("[OK] Corridor models initialized")
    print(f"[OK] Network: {len(corridor_network.segment_data)} segments, {len(corridor_network.intersection_data)} intersections")
    print(f"[OK] Topology: {corridor_network.get_network_topology()}")
    HAS_CORRIDOR = True
except Exception as e:
    print(f"[INFO] Corridor models not available: {e}")
    HAS_CORRIDOR = False
    corridor_network = None
    corridor_simulator = None
    corridor_emissions = None

# Mock data cache - HIGHER BASELINE AQI for better contrast
MOCK_ZONES = [
    {'id': 1, 'name': 'Connaught Place', 'aqi': 328, 'energy': 1500, 'heat': 0.6, 'traffic_flow': 8750, 'speed': 45},
    {'id': 2, 'name': 'Karol Bagh', 'aqi': 315, 'energy': 1600, 'heat': 0.5, 'traffic_flow': 7200, 'speed': 48},
    {'id': 3, 'name': 'Dwarka', 'aqi': 342, 'energy': 1400, 'heat': 0.7, 'traffic_flow': 9100, 'speed': 42},
    {'id': 4, 'name': 'Rohini', 'aqi': 305, 'energy': 1700, 'heat': 0.55, 'traffic_flow': 6800, 'speed': 50},
    {'id': 5, 'name': 'Saket', 'aqi': 320, 'energy': 1550, 'heat': 0.52, 'traffic_flow': 7500, 'speed': 46}
]

# Cache for models
models_cache = {}

@app.route('/api/baseline', methods=['GET'])
def get_baseline():
    """Get baseline simulation data - integrates real corridor infrastructure"""
    
    # Try to use corridor simulation if available
    if HAS_CORRIDOR and corridor_simulator and corridor_emissions:
        try:
            print("[INFO] Running baseline corridor simulation...")
            # Run corridor simulation
            baseline_results = corridor_simulator.run_simulation('baseline')
            
            # Get zone-level AQI from emissions model
            zone_aqi_list = corridor_emissions.compute_all_zones_aqi()
            
            # Get zone traffic aggregation
            zone_traffic = baseline_results.get('zones', {})
            
            # Format for frontend
            results = []
            for zone_aqi in zone_aqi_list:
                zone_id = zone_aqi['zone_id']
                zone_traffic_data = zone_traffic.get(zone_id, {})
                
                results.append({
                    'id': int(zone_id.replace('Z', '').lstrip('0') or 1),
                    'name': f"Zone {zone_id}",
                    'zone_id': zone_id,
                    'aqi': float(zone_aqi['total_aqi']),
                    'energy': 1500 + zone_traffic_data.get('total_flow', 0) * 0.1,  # Energy scales with traffic
                    'heat': 0.5 + zone_traffic_data.get('total_flow', 0) * 0.0001,  # Heat island effect
                    'traffic_flow': float(zone_traffic_data.get('total_flow', 0)),
                    'avg_speed': float(zone_traffic_data.get('avg_speed', 0)),
                    'pm25_grams': float(zone_aqi.get('pm25_grams', 0)),
                    'nox_grams': float(zone_aqi.get('nox_grams', 0)),
                    'daily_vehicles': int(zone_aqi.get('total_daily_vehicles', 0)),
                })
            
            print(f"[OK] Baseline simulation complete: {len(results)} zones")
            return jsonify({
                'zones': results,
                'temperature': 32,
                'day': 1,
                'source': 'corridor_simulation',
                'total_vehicles': baseline_results.get('total_vehicles', 0),
                'segments_count': baseline_results.get('segments_count', 0),
            })
        except Exception as e:
            print(f"[ERROR] Corridor simulation failed: {e}")
            import traceback
            traceback.print_exc()
            # Fall through to mock data
    
    # Fallback to old simulation or mock data
    if HAS_SIMULATION:
        try:
            zones, weather, traffic = load_data()
            day = 1
            temp = weather.loc[weather['day'] == day, 'temperature'].values[0]
            
            results = []
            for i, zone in zones.iterrows():
                tflow = traffic[(traffic['zone_id'] == zone['zone_id']) & (traffic['day'] == day)]['traffic_flow'].values[0]
                energy = compute_energy_demand(zone, temp)
                aqi = compute_aqi(zone, tflow, {'temperature': temp})
                heat = compute_heat_island(zone)
                
                results.append({
                    'id': int(zone['zone_id']),
                    'name': f"Zone {int(zone['zone_id'])}",
                    'aqi': float(aqi),
                    'energy': float(energy),
                    'heat': float(heat),
                    'traffic_flow': float(tflow)
                })
            
            return jsonify({
                'zones': results,
                'temperature': float(temp),
                'day': day,
                'source': 'legacy_simulation'
            })
        except Exception as e:
            print(f"[ERROR] Simulation failed: {e}")
            return jsonify({
                'zones': MOCK_ZONES,
                'temperature': 32,
                'day': 1,
                'source': 'mock_data'
            })
    else:
        return jsonify({
            'zones': MOCK_ZONES,
            'temperature': 32,
            'day': 1,
            'source': 'mock_data'
        })

@app.route('/api/run', methods=['POST'])
def run_scenario():
    """Run intervention scenario"""
    data = request.json
    intervention_type = data.get('type', 'baseline')
    target_zones = data.get('zones', [1, 2, 3, 4, 5])
    parameters = data.get('parameters', {})
    
    print(f"[API] Running scenario: type={intervention_type}, zones={target_zones}")
    
    # Try with simulation functions if available
    if HAS_SIMULATION:
        try:
            zones, weather, traffic = load_data()
            day = 1
            temp = weather.loc[weather['day'] == day, 'temperature'].values[0]
            
            # Apply interventions
            zones_copy = zones.copy()
            traffic_copy = traffic.copy()
            
            for zone_id in target_zones:
                try:
                    idx = zones_copy[zones_copy['zone_id'] == zone_id].index[0]
                    
                    if intervention_type == 'green_cover':
                        zones_copy.at[idx, 'green_cover'] = min(0.30, zones_copy.at[idx, 'green_cover'] + 0.10)
                    elif intervention_type == 'traffic_ban':
                        traffic_copy.loc[(traffic_copy['zone_id'] == zone_id) & (traffic_copy['day'] == day), 'traffic_flow'] *= 0.7
                    elif intervention_type == 'truck_ban':
                        traffic_copy.loc[(traffic_copy['zone_id'] == zone_id) & (traffic_copy['day'] == day), 'traffic_flow'] *= 0.78
                    elif intervention_type == 'odd_even':
                        traffic_copy.loc[(traffic_copy['zone_id'] == zone_id) & (traffic_copy['day'] == day), 'traffic_flow'] *= 0.55
                    elif intervention_type == 'retrofit':
                        zones_copy.at[idx, 'avg_building_age'] = max(15, zones_copy.at[idx, 'avg_building_age'] - 10)
                    elif intervention_type == 'emergency':
                        # Emergency response: aggressive traffic reduction + industrial curtailment
                        traffic_copy.loc[(traffic_copy['zone_id'] == zone_id) & (traffic_copy['day'] == day), 'traffic_flow'] *= 0.40
                        zones_copy.at[idx, 'industrial_activity'] *= 0.60
                        zones_copy.at[idx, 'green_cover'] = min(0.25, zones_copy.at[idx, 'green_cover'] + 0.05)
                        print(f"[Emergency] Applied to zone {zone_id}: 60% traffic cut, 40% industrial cut")
                except Exception as e:
                    print(f"[WARN] Error applying intervention to zone {zone_id}: {e}")
            
            # Compute new values
            results = []
            for i, zone in zones_copy.iterrows():
                tflow = traffic_copy[(traffic_copy['zone_id'] == zone['zone_id']) & (traffic_copy['day'] == day)]['traffic_flow'].values
                if len(tflow) > 0:
                    tflow = tflow[0]
                else:
                    tflow = zone.get('traffic_flow', 1000)
                    
                energy = compute_energy_demand(zone, temp)
                aqi = compute_aqi(zone, tflow, {'temperature': temp})
                heat = compute_heat_island(zone)
                
                results.append({
                    'id': int(zone['zone_id']),
                    'name': f"Zone {int(zone['zone_id'])}",
                    'aqi': float(aqi),
                    'energy': float(energy),
                    'heat': float(heat),
                    'traffic_flow': float(tflow)
                })
            
            response = {
                'zones': results,
                'intervention': intervention_type,
                'affected_zones': target_zones,
                'timestamp': str(pd.Timestamp.now())
            }
            
            print(f"[API] Response: {len(results)} zones updated")
            return jsonify(response)
        except Exception as e:
            print(f"[ERROR] Simulation failed: {e}, falling back to mock data")
            import traceback
            traceback.print_exc()
    
    # Fallback to mock data with reductions
    print(f"[API] Using mock data for intervention: {intervention_type}")
    results = []
    for zone in MOCK_ZONES:
        zone_copy = zone.copy()
        if zone['id'] in target_zones:
            if intervention_type == 'emergency':
                # Apply significant reductions for emergency
                zone_copy['aqi'] = max(50, zone['aqi'] * 0.82)  # 18% AQI reduction
                zone_copy['traffic_flow'] = zone['traffic_flow'] * 0.48  # 52% traffic reduction
                zone_copy['speed'] = min(70, zone['speed'] * 1.29)  # 29% speed improvement
                print(f"[Mock Emergency] Zone {zone['id']}: {zone['aqi']} -> {zone_copy['aqi']:.0f}")
        results.append(zone_copy)
    
    avg_aqi = sum(z['aqi'] for z in results) / len(results)
    print(f"[API] Mock response - Average AQI: {avg_aqi:.1f}")
    
    return jsonify({
        'zones': results,
        'intervention': intervention_type,
        'affected_zones': target_zones,
        'source': 'mock_data'
    })

@app.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    """Get AI-generated recommendations using advanced policy engine"""
    zones, weather, traffic = load_data()
    
    # Get current AQI levels
    current_aqi = {}
    day = 1
    temp = weather.loc[weather['day'] == day, 'temperature'].values[0]
    for i, zone in zones.iterrows():
        tflow = traffic[(traffic['zone_id'] == zone['zone_id']) & (traffic['day'] == day)]['traffic_flow'].values[0]
        aqi = compute_aqi(zone, tflow, {'temperature': temp})
        current_aqi[int(zone['zone_id'])] = float(aqi)
    
    # Get traffic congestion levels
    traffic_levels = {}
    for i, zone in zones.iterrows():
        tflow = traffic[(traffic['zone_id'] == zone['zone_id']) & (traffic['day'] == day)]['traffic_flow'].values[0]
        traffic_levels[int(zone['zone_id'])] = min(1.0, tflow / 1500)  # Normalize to 0-1
    
    # Check for stubble burning (seasonal - October-November)
    import datetime
    current_month = datetime.datetime.now().month
    stubble_burning = current_month in [10, 11]
    
    # Use the advanced policy engine
    policy_data = {
        "aqi": current_aqi,
        "weather": {
            "temperature": float(temp),
            "stubble_burning_active": stubble_burning,
            "wind_speed": 5.0,
            "wind_direction": 315
        },
        "traffic": traffic_levels
    }
    
    result = get_policy_recommendations(policy_data)
    
    # Format for frontend compatibility
    formatted_recs = []
    for rec in result['recommendations']:
        formatted_recs.append({
            'id': rec['id'],
            'name': rec['name'],
            'type': rec['name'].lower().replace(' ', '_'),
            'zones': rec['zones'],
            'impact': {
                'aqi': -rec['expected_outcome']['aqi_reduction'],
                'energy': -10,  # Placeholder
                'heat': -0.1
            },
            'details': {
                'reasoning': rec['reasoning'],
                'duration': rec['duration'],
                'lives_saved': rec['expected_outcome']['lives_saved'],
                'economic_impact': rec['expected_outcome']['economic_impact'],
                'confidence': f"{rec['confidence'] * 100:.0f}%",
                'implementation_time': rec['expected_outcome']['implementation_time']
            }
        })
    
    return jsonify({
        'recommendations': formatted_recs,
        'situation': result['situation_analysis']
    })
    
    # Generate and evaluate interventions
    interventions = [
        {'type': 'green_cover', 'zones': [3, 5], 'impact': {'aqi': -18, 'energy': -12, 'heat': -0.15}},
        {'type': 'traffic_ban', 'zones': [1, 2], 'impact': {'aqi': -25, 'energy': -5, 'heat': -0.05}},
        {'type': 'retrofit', 'zones': [4], 'impact': {'aqi': -8, 'energy': -20, 'heat': -0.10}},
        {'type': 'emergency', 'zones': [1, 2, 3], 'impact': {'aqi': -35, 'energy': -10, 'heat': -0.08}}
    ]
    
    recommendations = []
    for i, interv in enumerate(interventions):
        rec = {
            'id': i + 1,
            'name': f"{interv['type'].replace('_', ' ').title()} in Zones {', '.join(map(str, interv['zones']))}",
            'type': interv['type'],
            'zones': interv['zones'],
            'impact': interv['impact'],
            'score': abs(interv['impact']['aqi']) * 2 + abs(interv['impact']['energy'])
        }
        recommendations.append(rec)
    
    # Sort by score
    recommendations.sort(key=lambda x: x['score'], reverse=True)
    
    return jsonify({'recommendations': recommendations[:3]})

@app.route('/api/forecast', methods=['GET'])
def forecast():
    """Get 24-hour AQI forecast"""
    hours = request.args.get('hours', 24, type=int)
    
    # Generate mock forecast data
    base_aqi = 220
    forecast_data = []
    
    for h in range(hours):
        # Simulate daily pattern
        hour_factor = 1 + 0.3 * np.sin((h - 6) * np.pi / 12)  # Peak at noon
        traffic_factor = 1 + 0.2 * (1 if 7 <= h <= 9 or 17 <= h <= 19 else 0)  # Rush hours
        
        aqi = base_aqi * hour_factor * traffic_factor + np.random.normal(0, 10)
        forecast_data.append({
            'hour': h,
            'aqi': max(0, aqi),
            'confidence': 0.85 - (h / hours) * 0.3  # Confidence decreases with time
        })
    
    return jsonify({'forecast': forecast_data})

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'version': '1.0.0'})

@app.route('/api/generate_graphs', methods=['POST'])
def generate_graphs():
    """Generate visualization graphs after emergency protocol and return as base64"""
    data = request.json
    print("[API] Graph generation requested")
    
    try:
        # Import the graph generator
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from src.graph_generator import generate_graphs as gen_graphs
        
        # Get baseline and emergency zones from request
        baseline_zones = data.get('baseline_zones', [])
        emergency_zones = data.get('emergency_zones', [])
        
        print(f"[Graph] Generating graphs for {len(baseline_zones)} baseline zones and {len(emergency_zones)} emergency zones")
        
        # Generate graphs as base64
        if baseline_zones and emergency_zones:
            graphs = gen_graphs(baseline_zones, emergency_zones)
            print(f"[Graph] Generated {len(graphs)} graphs")
            
            return jsonify({
                'status': 'success',
                'graphs': graphs,
                'message': 'Graphs generated successfully'
            })
        else:
            print("[Graph] Missing baseline or emergency zones data")
            return jsonify({
                'status': 'error',
                'message': 'Missing baseline or emergency zones data',
                'graphs': {}
            }), 400
    except Exception as e:
        print(f"[Graph] Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': str(e),
            'graphs': {}
        }), 500

if __name__ == '__main__':
    print("Starting Delhi Digital Twin Backend API...")
    app.run(debug=True, port=5000)
