from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
import sys
import os

# Add parent directory to path to import simulation modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.simulation import load_data, compute_energy_demand, compute_aqi, compute_heat_island
from src.ai_prescriptive import generate_random_interventions, simulate_interventions, train_surrogate
from policy_engine import get_policy_recommendations, TrafficOptimizer, ExposureAnalyzer

app = Flask(__name__)
CORS(app)

# Cache for models
models_cache = {}

@app.route('/api/baseline', methods=['GET'])
def get_baseline():
    """Get baseline simulation data"""
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
            'heat': float(heat)
        })
    
    return jsonify({
        'zones': results,
        'temperature': float(temp),
        'day': day
    })

@app.route('/api/run', methods=['POST'])
def run_scenario():
    """Run intervention scenario"""
    data = request.json
    intervention_type = data.get('type')
    target_zones = data.get('zones', [])
    parameters = data.get('parameters', {})
    
    zones, weather, traffic = load_data()
    day = 1
    temp = weather.loc[weather['day'] == day, 'temperature'].values[0]
    
    # Apply interventions
    zones_copy = zones.copy()
    traffic_copy = traffic.copy()
    
    for zone_id in target_zones:
        idx = zones_copy[zones_copy['zone_id'] == zone_id].index[0]
        
        if intervention_type == 'green_cover':
            zones_copy.at[idx, 'green_cover'] = min(0.30, zones_copy.at[idx, 'green_cover'] + 0.10)
        elif intervention_type == 'traffic_ban':
            traffic_copy.loc[(traffic_copy['zone_id'] == zone_id) & (traffic_copy['day'] == day), 'traffic_flow'] *= 0.7
        elif intervention_type == 'retrofit':
            zones_copy.at[idx, 'avg_building_age'] = max(15, zones_copy.at[idx, 'avg_building_age'] - 10)
        elif intervention_type == 'emergency':
            # Emergency response: reduce traffic and industrial activity
            traffic_copy.loc[(traffic_copy['zone_id'] == zone_id) & (traffic_copy['day'] == day), 'traffic_flow'] *= 0.5
            zones_copy.at[idx, 'industrial_activity'] *= 0.7
    
    # Compute new values
    results = []
    for i, zone in zones_copy.iterrows():
        tflow = traffic_copy[(traffic_copy['zone_id'] == zone['zone_id']) & (traffic_copy['day'] == day)]['traffic_flow'].values[0]
        energy = compute_energy_demand(zone, temp)
        aqi = compute_aqi(zone, tflow, {'temperature': temp})
        heat = compute_heat_island(zone)
        
        results.append({
            'id': int(zone['zone_id']),
            'name': f"Zone {int(zone['zone_id'])}",
            'aqi': float(aqi),
            'energy': float(energy),
            'heat': float(heat)
        })
    
    return jsonify({
        'zones': results,
        'intervention': intervention_type,
        'affected_zones': target_zones
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

if __name__ == '__main__':
    print("Starting Delhi Digital Twin Backend API...")
    app.run(debug=True, port=5000)
