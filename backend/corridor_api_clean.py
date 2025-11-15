"""
Flask API endpoints for corridor-based traffic simulation with real infrastructure.
"""

from flask import Blueprint, request, jsonify, send_file
import os
import json
import pandas as pd
from io import BytesIO, StringIO
import numpy as np
from src.models import CorridorNetwork, TrafficSimulator, InterventionEngine, EmissionsModel

# Create blueprint
corridor_api = Blueprint('corridor', __name__, url_prefix='/api/corridor')

# Global instances (will be initialized in app startup)
network = None
simulator = None
intervention_engine = None
emissions_model = None

def init_corridor_models(base_path):
    """Initialize corridor models from CSV files."""
    global network, simulator, intervention_engine, emissions_model
    
    data_path = os.path.join(base_path, 'data')
    segments_csv = os.path.join(data_path, 'corridor_segments.csv')
    intersections_csv = os.path.join(data_path, 'intersections.csv')
    od_matrix_csv = os.path.join(data_path, 'od_matrix.csv')
    
    # Initialize models
    network = CorridorNetwork(segments_csv, intersections_csv, od_matrix_csv)
    simulator = TrafficSimulator(network)
    intervention_engine = InterventionEngine(network, simulator)
    emissions_model = EmissionsModel(simulator)
    
    return network, simulator, intervention_engine, emissions_model

@corridor_api.route('/baseline', methods=['GET'])
def get_baseline():
    """Get baseline traffic and emissions results."""
    global simulator, emissions_model
    
    if simulator is None:
        return jsonify({'error': 'Simulator not initialized'}), 500
    
    # Run baseline simulation
    baseline_results = simulator.run_simulation('baseline')
    
    # Compute AQI
    zone_aqi = emissions_model.compute_all_zones_aqi()
    
    return jsonify({
        'scenario': 'baseline',
        'total_vehicles': baseline_results['total_vehicles'],
        'segments_count': len(baseline_results['segments']),
        'zones_aqi': zone_aqi,
        'zone_traffic': baseline_results['zones'],
    }), 200

@corridor_api.route('/run', methods=['POST'])
def run_scenario():
    """
    Run traffic simulation with optional interventions and infrastructure changes.
    
    Request JSON example:
    {
        "scenario_name": "truck_ban_test",
        "interventions": [...],
        "infrastructure": {
            "segment_changes": [{"segment_id": "SEG001", "lanes": 4}],
            "signal_changes": [{"intersection_id": "INT005", "green_time_delta": 15}],
            "segment_closures": ["SEG008"]
        }
    }
    """
    global simulator, intervention_engine, emissions_model, network
    
    if simulator is None:
        return jsonify({'error': 'Simulator not initialized'}), 500
    
    data = request.get_json()
    scenario_name = data.get('scenario_name', 'custom')
    interventions = data.get('interventions', [])
    infrastructure = data.get('infrastructure', {})
    
    # Apply infrastructure changes
    if infrastructure:
        for change in infrastructure.get('segment_changes', []):
            seg_id = change.get('segment_id')
            new_lanes = change.get('lanes')
            if seg_id and new_lanes:
                network.update_segment_lanes(seg_id, new_lanes)
        
        for change in infrastructure.get('signal_changes', []):
            int_id = change.get('intersection_id')
            green_delta = change.get('green_time_delta')
            if int_id and green_delta:
                network.update_signal_timing(int_id, green_delta)
        
        for seg_id in infrastructure.get('segment_closures', []):
            network.close_segment(seg_id)
    
    # Apply interventions
    if interventions:
        intervention_results = intervention_engine.apply_multiple_interventions(interventions)
    
    # Run simulation
    results = simulator.run_simulation(scenario_name)
    zone_aqi = emissions_model.compute_all_zones_aqi()
    
    # Compute impact
    baseline_result = simulator.simulation_results.get('baseline', {})
    impact_analysis = {
        'total_vehicles': results['total_vehicles'],
        'avg_speed_change': 0,
        'zones_improved': 0,
    }
    
    if baseline_result:
        baseline_zones = baseline_result.get('zones', {})
        current_zones = results.get('zones', {})
        
        speed_changes = []
        for zone_id in current_zones:
            if zone_id in baseline_zones:
                baseline_speed = baseline_zones[zone_id].get('avg_speed', 0)
                current_speed = current_zones[zone_id].get('avg_speed', 0)
                if baseline_speed > 0:
                    speed_changes.append((current_speed - baseline_speed) / baseline_speed * 100)
        
        if speed_changes:
            impact_analysis['avg_speed_change'] = sum(speed_changes) / len(speed_changes)
            impact_analysis['zones_improved'] = sum(1 for c in speed_changes if c > 0)
    
    return jsonify({
        'scenario': scenario_name,
        'total_vehicles': results['total_vehicles'],
        'segments_count': len(results['segments']),
        'zones_aqi': zone_aqi,
        'zone_traffic': results['zones'],
        'impact_analysis': impact_analysis,
        'interventions_applied': len(interventions) + bool(infrastructure),
    }), 200


@corridor_api.route('/infrastructure', methods=['POST'])
def modify_infrastructure():
    """Dynamically modify corridor infrastructure."""
    global network
    
    if network is None:
        return jsonify({'error': 'Network not initialized'}), 500
    
    data = request.get_json()
    action = data.get('action')
    
    try:
        if action == 'add_lanes':
            seg_id = data.get('segment_id')
            new_lanes = data.get('new_lanes')
            success = network.update_segment_lanes(seg_id, new_lanes)
            return jsonify({'action': 'add_lanes', 'segment_id': seg_id, 'new_lanes': new_lanes, 'success': success}), 200
        
        elif action == 'close_segment':
            seg_id = data.get('segment_id')
            success = network.close_segment(seg_id)
            return jsonify({'action': 'close_segment', 'segment_id': seg_id, 'success': success}), 200
        
        elif action == 'reopen_segment':
            seg_id = data.get('segment_id')
            success = network.reopen_segment(seg_id)
            return jsonify({'action': 'reopen_segment', 'segment_id': seg_id, 'success': success}), 200
        
        elif action == 'update_signal':
            int_id = data.get('intersection_id')
            green_delta = data.get('green_time_delta')
            success = network.update_signal_timing(int_id, green_delta)
            return jsonify({'action': 'update_signal', 'intersection_id': int_id, 'green_time_delta': green_delta, 'success': success}), 200
        
        else:
            return jsonify({'error': f'Unknown action: {action}'}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@corridor_api.route('/topology', methods=['GET'])
def get_topology():
    """Get complete network topology."""
    global network
    
    if network is None:
        return jsonify({'error': 'Network not initialized'}), 500
    
    topology = network.get_network_topology()
    return jsonify(topology), 200


@corridor_api.route('/validate', methods=['GET'])
def validate_network():
    """Validate network connectivity and structure."""
    global network
    
    if network is None:
        return jsonify({'error': 'Network not initialized'}), 500
    
    validation_report = network.validate_network()
    return jsonify(validation_report), 200


@corridor_api.route('/segment/<segment_id>', methods=['GET'])
def get_segment_info(segment_id):
    """Get detailed information about a specific segment."""
    global network, simulator, emissions_model
    
    if network is None:
        return jsonify({'error': 'Network not initialized'}), 500
    
    segment_data = network.get_segment(segment_id)
    
    if not segment_data:
        return jsonify({'error': f'Segment {segment_id} not found'}), 404
    
    result = {'segment_id': segment_id, 'properties': segment_data}
    
    # Add simulation results if available
    if simulator:
        sim_results = simulator.get_segment_results(segment_id)
        result['current_state'] = sim_results
    
    # Add emissions if available
    if emissions_model:
        emissions = emissions_model.compute_segment_emissions(segment_id)
        result['emissions'] = emissions
    
    return jsonify(result), 200


@corridor_api.route('/zone/<zone_id>', methods=['GET'])
def get_zone_info(zone_id):
    """Get aggregated traffic data for a zone."""
    global network, simulator, emissions_model
    
    if network is None:
        return jsonify({'error': 'Network not initialized'}), 500
    
    segments_in_zone = network.get_segments_in_zone(zone_id)
    
    zone_data = {
        'zone_id': zone_id,
        'segments_count': len(segments_in_zone),
        'segments': segments_in_zone,
    }
    
    # Add simulation results
    if simulator:
        sim_results = simulator.get_zone_results(zone_id)
        zone_data.update(sim_results)
    
    # Add AQI
    if emissions_model:
        aqi_data = emissions_model.compute_zone_aqi(zone_id)
        zone_data['aqi_data'] = aqi_data
    
    return jsonify(zone_data), 200


@corridor_api.route('/interventions', methods=['GET'])
def get_active_interventions():
    """Get list of currently active interventions."""
    global intervention_engine
    
    if intervention_engine is None:
        return jsonify({'error': 'Intervention engine not initialized'}), 500
    
    active = intervention_engine.get_active_interventions()
    return jsonify({'active_interventions': active}), 200


@corridor_api.route('/interventions/reset', methods=['POST'])
def reset_interventions():
    """Reset all interventions to baseline."""
    global intervention_engine
    
    if intervention_engine is None:
        return jsonify({'error': 'Intervention engine not initialized'}), 500
    
    result = intervention_engine.reset_all_interventions()
    return jsonify(result), 200


@corridor_api.route('/export', methods=['GET'])
def export_results():
    """Export simulation results as CSV or JSON."""
    global simulator
    
    if simulator is None or not simulator.simulation_results:
        return jsonify({'error': 'No simulation results available'}), 400
    
    format_type = request.args.get('format', 'json')
    scenario = request.args.get('scenario', list(simulator.simulation_results.keys())[-1])
    
    if scenario not in simulator.simulation_results:
        return jsonify({'error': f'Scenario {scenario} not found'}), 404
    
    results = simulator.simulation_results[scenario]
    
    if format_type == 'csv':
        segments_df = pd.DataFrame(results['segments']).T
        output = StringIO()
        segments_df.to_csv(output)
        output.seek(0)
        
        return send_file(
            BytesIO(output.getvalue().encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'{scenario}_results.csv'
        )
    else:
        return jsonify(results), 200
