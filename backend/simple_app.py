"""
Simple Flask backend for Delhi Digital Twin - No complex dependencies
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

# Mock zones data
ZONES = [
    {'id': 1, 'name': 'Connaught Place', 'base_aqi': 220, 'base_energy': 1500, 'base_heat': 0.6},
    {'id': 2, 'name': 'Karol Bagh', 'base_aqi': 200, 'base_energy': 1600, 'base_heat': 0.5},
    {'id': 3, 'name': 'Dwarka', 'base_aqi': 240, 'base_energy': 1400, 'base_heat': 0.7},
    {'id': 4, 'name': 'Rohini', 'base_aqi': 210, 'base_energy': 1700, 'base_heat': 0.55},
    {'id': 5, 'name': 'Saket', 'base_aqi': 230, 'base_energy': 1550, 'base_heat': 0.52}
]

@app.route('/api/baseline', methods=['GET'])
def get_baseline():
    """Get baseline simulation data"""
    zones = []
    for zone in ZONES:
        # Add some randomness
        zones.append({
            'id': zone['id'],
            'name': zone['name'],
            'aqi': zone['base_aqi'] + random.randint(-10, 10),
            'energy': zone['base_energy'] + random.randint(-100, 100),
            'heat': zone['base_heat'] + random.uniform(-0.05, 0.05)
        })
    
    return jsonify({
        'zones': zones,
        'temperature': 32.5,
        'day': 1,
        'timestamp': '2025-11-15T14:30:00'
    })

@app.route('/api/run', methods=['POST'])
def run_scenario():
    """Run intervention scenario"""
    data = request.json
    intervention_type = data.get('type', 'unknown')
    target_zones = data.get('zones', [])
    
    zones = []
    for zone in ZONES:
        aqi = zone['base_aqi']
        energy = zone['base_energy']
        heat = zone['base_heat']
        
        # Apply interventions to target zones
        if zone['id'] in target_zones:
            if intervention_type == 'green_cover':
                aqi -= 18
                energy -= 12
                heat -= 0.15
            elif intervention_type == 'traffic_ban':
                aqi -= 25
                energy -= 5
                heat -= 0.05
            elif intervention_type == 'retrofit':
                aqi -= 8
                energy -= 20
                heat -= 0.10
            elif intervention_type == 'emergency':
                aqi -= 35
                energy -= 10
                heat -= 0.08
        
        zones.append({
            'id': zone['id'],
            'name': zone['name'],
            'aqi': max(0, aqi + random.randint(-5, 5)),
            'energy': max(0, energy + random.randint(-50, 50)),
            'heat': max(0, heat + random.uniform(-0.02, 0.02))
        })
    
    return jsonify({
        'zones': zones,
        'intervention': intervention_type,
        'affected_zones': target_zones,
        'timestamp': '2025-11-15T14:30:00'
    })

@app.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    """Get AI-generated recommendations"""
    recommendations = [
        {
            'id': 1,
            'name': 'Green Corridors in Zones 3 & 5',
            'type': 'green_cover',
            'zones': [3, 5],
            'impact': {'aqi': -18, 'energy': -12, 'heat': -0.15},
            'score': 48,
            'details': {
                'reasoning': 'Zones 3 and 5 have high AQI and limited green cover. Adding vegetation will improve air quality significantly.',
                'duration': '6-12 months implementation',
                'lives_saved': 150,
                'economic_impact': -50000000,
                'confidence': '85%',
                'implementation_time': '6 months'
            }
        },
        {
            'id': 2,
            'name': 'Truck Ban 6-12 AM in Zone 2',
            'type': 'traffic_ban',
            'zones': [2],
            'impact': {'aqi': -22, 'energy': -3, 'heat': -0.05},
            'score': 47,
            'details': {
                'reasoning': 'Morning rush hour truck traffic significantly contributes to PM2.5 levels in Zone 2.',
                'duration': 'Immediate implementation',
                'lives_saved': 120,
                'economic_impact': -20000000,
                'confidence': '90%',
                'implementation_time': 'Immediate'
            }
        },
        {
            'id': 3,
            'name': 'Reflective Roofs in Zone 1',
            'type': 'retrofit',
            'zones': [1],
            'impact': {'aqi': -5, 'energy': -15, 'heat': -0.30},
            'score': 35,
            'details': {
                'reasoning': 'High building density in Zone 1 creates urban heat island. Reflective surfaces will reduce cooling demand.',
                'duration': '3-6 months',
                'lives_saved': 80,
                'economic_impact': -30000000,
                'confidence': '80%',
                'implementation_time': '3 months'
            }
        }
    ]
    
    return jsonify({
        'recommendations': recommendations,
        'situation_analysis': {
            'overall_aqi': 220,
            'crisis_level': 'moderate',
            'primary_sources': ['Vehicle emissions', 'Construction dust', 'Industrial activity']
        }
    })

@app.route('/api/forecast', methods=['GET'])
def forecast():
    """Get 24-hour AQI forecast"""
    hours = request.args.get('hours', 24, type=int)
    
    forecast_data = []
    base_aqi = 220
    
    for h in range(hours):
        # Simulate daily pattern
        hour_of_day = h % 24
        if 6 <= hour_of_day <= 9 or 17 <= hour_of_day <= 20:
            traffic_factor = 1.2  # Rush hours
        else:
            traffic_factor = 1.0
        
        time_factor = 1 + 0.2 * ((hour_of_day - 12) / 24)  # Gradual increase
        aqi = base_aqi * traffic_factor * time_factor + random.uniform(-15, 15)
        
        forecast_data.append({
            'hour': h,
            'aqi': max(0, aqi),
            'confidence': max(0.5, 0.95 - (h / hours) * 0.4)
        })
    
    return jsonify({'forecast': forecast_data})

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '2.0.0',
        'backend': 'simple',
        'endpoints': ['/api/baseline', '/api/run', '/api/recommendations', '/api/forecast']
    })

@app.route('/')
def index():
    """Root endpoint"""
    return jsonify({
        'name': 'Delhi Digital Twin API',
        'version': '2.0.0',
        'status': 'running',
        'endpoints': {
            'baseline': '/api/baseline',
            'run_scenario': '/api/run',
            'recommendations': '/api/recommendations',
            'forecast': '/api/forecast',
            'health': '/api/health'
        }
    })

if __name__ == '__main__':
    print("=" * 60)
    print(" Delhi Digital Twin - Simple Backend API")
    print("=" * 60)
    print(" Status: Starting...")
    print(" Port: 5000")
    print(" Endpoints:")
    print("   - GET  /api/baseline")
    print("   - POST /api/run")
    print("   - GET  /api/recommendations")
    print("   - GET  /api/forecast")
    print("   - GET  /api/health")
    print("=" * 60)
    
    app.run(debug=True, port=5000, host='0.0.0.0')
