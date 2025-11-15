"""
Flask API endpoints for corridor-based traffic simulation.
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
    """
    Get baseline traffic and emissions results.
    
    Returns:
        Baseline simulation results including flows, speeds, AQI per zone
    """
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
    Run traffic simulation with optional interventions.
    
    Request JSON:
    {
        "scenario_name": "truck_ban_test",
        "interventions": [
            {
                "type": "truck_ban",
                "segment_ids": ["SEG001", "SEG002"],
                "time_window": [6, 12]
            },
            {
                "type": "add_lanes",
                "segment_ids": ["SEG009", "SEG010"],
                "num_lanes": 2
            },
            {
                "type": "signal_timing",
                "intersection_ids": ["INT001", "INT002"],
                "green_time": 70
            },
            {
                "type": "segment_closure",
                "segment_ids": ["SEG015"]
            }
        ],
        "infrastructure": {
            "segment_changes": [
                {"segment_id": "SEG001", "lanes": 4}
            ],
            "signal_changes": [
                {"intersection_id": "INT005", "green_time_delta": 15}
            ],
            "segment_closures": ["SEG008"]
        }
    }
    
    Returns:
        Simulation results and impact analysis
    """
    global simulator, intervention_engine, emissions_model, network
    
    if simulator is None:
        return jsonify({'error': 'Simulator not initialized'}), 500
    
    data = request.get_json()
    scenario_name = data.get('scenario_name', 'custom')
    interventions = data.get('interventions', [])
    infrastructure = data.get('infrastructure', {})
    
    # Apply infrastructure changes if provided
    if infrastructure:
        # Apply segment changes (lane modifications)
        for change in infrastructure.get('segment_changes', []):
            seg_id = change.get('segment_id')
            new_lanes = change.get('lanes')
            if seg_id and new_lanes:
                network.update_segment_lanes(seg_id, new_lanes)
        
        # Apply signal changes
        for change in infrastructure.get('signal_changes', []):
            int_id = change.get('intersection_id')
            green_delta = change.get('green_time_delta')
            if int_id and green_delta:
                network.update_signal_timing(int_id, green_delta)
        
        # Apply segment closures
        for seg_id in infrastructure.get('segment_closures', []):
            network.close_segment(seg_id)
        
        # Apply reroutes (if provided)
        for reroute in infrastructure.get('reroutes', []):
            # Reroute logic would be applied here
            pass
    
    # Apply interventions using intervention engine
    if interventions:
        intervention_results = intervention_engine.apply_multiple_interventions(interventions)
    
    # Run simulation
    results = simulator.run_simulation(scenario_name)
    zone_aqi = emissions_model.compute_all_zones_aqi()
    
    # Compute impact comparison
    baseline_result = simulator.simulation_results.get('baseline', {})
    impact_analysis = {
        'total_vehicles': results['total_vehicles'],
        'avg_speed_change': 0,
        'congestion_change': 0,
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
    """
    Dynamically modify corridor infrastructure.
    
    Request JSON:
    {
        "action": "add_lanes" | "close_segment" | "update_signal" | "reopen_segment",
        "segment_id": "SEG001",  # for segment operations
        "intersection_id": "INT001",  # for signal operations
        "new_lanes": 4,
        "green_time_delta": 15
    }
    
    Returns:
        Infrastructure modification result
    """
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
            return jsonify({
                'action': 'add_lanes',
                'segment_id': seg_id,
                'new_lanes': new_lanes,
                'success': success
            }), 200
        
        elif action == 'close_segment':
            seg_id = data.get('segment_id')
            success = network.close_segment(seg_id)
            return jsonify({
                'action': 'close_segment',
                'segment_id': seg_id,
                'success': success
            }), 200
        
        elif action == 'reopen_segment':
            seg_id = data.get('segment_id')
            success = network.reopen_segment(seg_id)
            return jsonify({
                'action': 'reopen_segment',
                'segment_id': seg_id,
                'success': success
            }), 200
        
        elif action == 'update_signal':
            int_id = data.get('intersection_id')
            green_delta = data.get('green_time_delta')
            success = network.update_signal_timing(int_id, green_delta)
            return jsonify({
                'action': 'update_signal',
                'intersection_id': int_id,
                'green_time_delta': green_delta,
                'success': success
            }), 200
        
        else:
            return jsonify({'error': f'Unknown action: {action}'}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@corridor_api.route('/topology', methods=['GET'])
def get_topology():
    """
    Get complete network topology.
    
    Returns:
        Network structure including segments, intersections, zones
    """
    global network
    
    if network is None:
        return jsonify({'error': 'Network not initialized'}), 500
    
    topology = network.get_network_topology()
    
    return jsonify(topology), 200


@corridor_api.route('/validate', methods=['GET'])
def validate_network():
    """
    Validate network connectivity and structure.
    
    Returns:
        Validation report with issues (if any)
    """
    global network
    
    if network is None:
        return jsonify({'error': 'Network not initialized'}), 500
    
    validation_report = network.validate_network()
    
    return jsonify(validation_report), 200


@corridor_api.route('/segment/<segment_id>', methods=['GET'])
def get_segment_details(segment_id):
    """
    Get detailed information about a specific segment.
    
    Args:
        segment_id: Segment ID (e.g., SEG001)
    
    Returns:
        Segment data including current traffic state
    """
    global network, simulator
    
    if network is None:
        return jsonify({'error': 'Network not initialized'}), 500
    
    segment_data = network.get_segment(segment_id)
    
    if not segment_data:
        return jsonify({'error': f'Segment {segment_id} not found'}), 404
    
    # Add simulation results if available
    if simulator:
        sim_results = simulator.get_segment_results(segment_id)
        segment_data.update(sim_results)
    
    return jsonify(segment_data), 200


@corridor_api.route('/zone/<zone_id>', methods=['GET'])
def get_zone_details(zone_id):
    """
    Get aggregated traffic data for a zone.
    
    Args:
        zone_id: Zone ID (e.g., Z01)
    
    Returns:
        Zone-level aggregated traffic metrics
    """
    global network, simulator, emissions_model
    
    if network is None:
        return jsonify({'error': 'Network not initialized'}), 500
    
    segments_in_zone = network.get_segments_in_zone(zone_id)
    
    zone_data = {
        'zone_id': zone_id,
        'segments_count': len(segments_in_zone),
        'segments': segments_in_zone,
    }
    
    # Add simulation results if available
    if simulator:
        sim_results = simulator.get_zone_results(zone_id)
        zone_data.update(sim_results)
    
    # Add AQI if emissions model available
    if emissions_model:
        aqi = emissions_model.compute_zone_aqi(zone_id)
        zone_data['aqi'] = aqi
    
    return jsonify(zone_data), 200


@corridor_api.route('/interventions', methods=['GET'])
def get_active_interventions():
    """
    Get list of currently active interventions.
    
    Returns:
        Active interventions
    """
    global intervention_engine
    
    if intervention_engine is None:
        return jsonify({'error': 'Intervention engine not initialized'}), 500
    
    active = intervention_engine.get_active_interventions()
    
    return jsonify({'active_interventions': active}), 200


@corridor_api.route('/interventions/reset', methods=['POST'])
def reset_interventions():
    """
    Reset all interventions to baseline.
    
    Returns:
        Reset result
    """
    global intervention_engine
    
    if intervention_engine is None:
        return jsonify({'error': 'Intervention engine not initialized'}), 500
    
    result = intervention_engine.reset_all_interventions()
    
    return jsonify(result), 200


@corridor_api.route('/export', methods=['GET'])
def export_results():
    """
    Export simulation results as CSV.
    
    Query params:
        format: 'csv' or 'json'
        scenario: scenario name (default: last run)
    
    Returns:
        File download
    """
    global simulator
    
    if simulator is None or not simulator.simulation_results:
        return jsonify({'error': 'No simulation results available'}), 400
    
    format_type = request.args.get('format', 'json')
    scenario = request.args.get('scenario', list(simulator.simulation_results.keys())[-1])
    
    if scenario not in simulator.simulation_results:
        return jsonify({'error': f'Scenario {scenario} not found'}), 404
    
    results = simulator.simulation_results[scenario]
    
    if format_type == 'csv':
        # Convert to CSV
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
        # Return JSON
        return jsonify(results), 200
    
@corridor_api.route('/stats', methods=['GET'])
def get_network_stats():
    """
    Get basic network statistics.
    
    Returns:
        Network overview statistics
    """
    global network, simulator, emissions_model
    
    if network is None:
        return jsonify({'error': 'Network not initialized'}), 500
    
    # Run baseline if not already done
    if not simulator.simulation_results:
        simulator.run_simulation('baseline')
    
    baseline = list(simulator.simulation_results.values())[0]
    all_zones_aqi = emissions_model.compute_all_zones_aqi()
    
    return jsonify({
        'total_segments': len(network.get_all_segments()),
        'total_intersections': len(network.get_all_intersections()),
        'total_od_pairs': len(network.od_matrix_df),
        'total_vehicles_per_hour': baseline['total_vehicles'],
        'average_zone_aqi': np.mean([z['total_aqi'] for z in all_zones_aqi]),
        'zones_count': len(all_zones_aqi),
    }), 200


# ============================================================================
# VISUALIZATION ENDPOINTS
# ============================================================================

@corridor_api.route('/visualization/zone-summary', methods=['GET'])
def get_zone_summary():
    """
    Get zone-level aggregated summary for visualization.
    
    Returns:
        Zone-level traffic and AQI data
    """
    global simulator, emissions_model
    
    if simulator is None:
        return jsonify({'error': 'Simulator not initialized'}), 500
    
    # Get all zones AQI
    all_zones_aqi = emissions_model.compute_all_zones_aqi()
    baseline = list(simulator.simulation_results.values())[0] if simulator.simulation_results else {}
    zone_traffic = baseline.get('zones', {})
    
    zone_data = []
    for zone_id, aqi_info in enumerate(all_zones_aqi):
        zone_key = f'zone_{zone_id}'
        traffic_info = zone_traffic.get(zone_key, {})
        
        zone_data.append({
            'zone_id': zone_id,
            'total_traffic': traffic_info.get('total_traffic', 0),
            'avg_speed': traffic_info.get('avg_speed', 0),
            'avg_travel_time': traffic_info.get('avg_travel_time', 0),
            'aqi': aqi_info.get('total_aqi', 0),
            'pm25': aqi_info.get('pm25_concentration', 0),
            'health_impact': aqi_info.get('health_impact_score', 0),
        })
    
    return jsonify(zone_data), 200


@corridor_api.route('/visualization/segment-details', methods=['GET'])
def get_visualization_segment_details():
    """
    Get detailed segment-level data for visualization.
    
    Query params:
        segment_id (optional): Get specific segment
    
    Returns:
        Segment-level results
    """
    global network, simulator
    
    if simulator is None:
        return jsonify({'error': 'Simulator not initialized'}), 500
    
    segment_id = request.args.get('segment_id')
    baseline = list(simulator.simulation_results.values())[0] if simulator.simulation_results else {}
    segments = baseline.get('segments', {})
    
    if segment_id:
        if segment_id in segments:
            return jsonify(segments[segment_id]), 200
        return jsonify({'error': f'Segment {segment_id} not found'}), 404
    
    # Return all segments
    segment_list = []
    for seg_id, seg_data in segments.items():
        segment_list.append({
            'segment_id': seg_id,
            **seg_data
        })
    
    return jsonify(segment_list), 200


@corridor_api.route('/visualization/export-csv', methods=['GET'])
def export_csv():
    """
    Export results as CSV file.
    
    Query params:
        type: 'baseline' or 'zone-summary'
    
    Returns:
        CSV file download
    """
    global simulator, emissions_model
    
    if simulator is None:
        return jsonify({'error': 'Simulator not initialized'}), 500
    
    export_type = request.args.get('type', 'baseline')
    baseline = list(simulator.simulation_results.values())[0] if simulator.simulation_results else {}
    
    if export_type == 'zone-summary':
        all_zones_aqi = emissions_model.compute_all_zones_aqi()
        zone_traffic = baseline.get('zones', {})
        
        rows = []
        for zone_id, aqi_info in enumerate(all_zones_aqi):
            zone_key = f'zone_{zone_id}'
            traffic_info = zone_traffic.get(zone_key, {})
            rows.append({
                'Zone': zone_id,
                'Traffic (vph)': traffic_info.get('total_traffic', 0),
                'Avg Speed (km/h)': traffic_info.get('avg_speed', 0),
                'Avg Travel Time (min)': traffic_info.get('avg_travel_time', 0),
                'AQI': aqi_info.get('total_aqi', 0),
                'PM2.5 (µg/m³)': aqi_info.get('pm25_concentration', 0),
                'Health Impact': aqi_info.get('health_impact_score', 0),
            })
        
        df = pd.DataFrame(rows)
    else:  # segment details
        segments = baseline.get('segments', {})
        rows = []
        for seg_id, seg_data in segments.items():
            rows.append({'Segment': seg_id, **seg_data})
        df = pd.DataFrame(rows)
    
    # Create CSV in memory
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    
    return csv_buffer.getvalue(), 200, {'Content-Type': 'text/csv', 'Content-Disposition': 'attachment;filename=corridor_data.csv'}


@corridor_api.route('/visualization/export-json', methods=['GET'])
def export_json():
    """
    Export results as JSON file.
    
    Returns:
        JSON file download
    """
    global simulator, emissions_model
    
    if simulator is None:
        return jsonify({'error': 'Simulator not initialized'}), 500
    
    all_zones_aqi = emissions_model.compute_all_zones_aqi()
    baseline = list(simulator.simulation_results.values())[0] if simulator.simulation_results else {}
    
    export_data = {
        'baseline': baseline,
        'zones_aqi': all_zones_aqi,
        'export_timestamp': pd.Timestamp.now().isoformat(),
    }
    
    return jsonify(export_data), 200


@corridor_api.route('/visualization/comparison', methods=['GET'])
def get_comparison():
    """
    Get comparison between all scenarios/interventions.
    
    Returns:
        Comparison metrics across scenarios
    """
    global simulator
    
    if simulator is None:
        return jsonify({'error': 'Simulator not initialized'}), 500
    
    comparisons = []
    for scenario_name, results in simulator.simulation_results.items():
        comparisons.append({
            'scenario': scenario_name,
            'total_traffic': results.get('total_vehicles', 0),
            'avg_speed': results.get('avg_speed', 0),
            'avg_travel_time': results.get('avg_travel_time', 0),
        })
    
    return jsonify(comparisons), 200
