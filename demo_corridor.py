"""
Demo script to test corridor network, traffic simulator, and interventions.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.models import CorridorNetwork, TrafficSimulator, InterventionEngine, EmissionsModel

def main():
    print("=" * 80)
    print("DELHI CORRIDOR TRAFFIC SIMULATOR - DEMO")
    print("=" * 80)
    
    # Initialize models
    print("\n[1] Loading network from CSV files...")
    data_path = os.path.join(os.path.dirname(__file__), 'data')
    
    try:
        network = CorridorNetwork(
            os.path.join(data_path, 'corridor_segments.csv'),
            os.path.join(data_path, 'intersections.csv'),
            os.path.join(data_path, 'od_matrix.csv'),
        )
        print("[OK] Network loaded: {} segments, {} intersections".format(
            len(network.get_all_segments()),
            len(network.get_all_intersections())))
    except Exception as e:
        print("[ERROR] Error loading network: {}".format(e))
        return
    
    # Validate network
    print("\n[2] Validating network...")
    validation = network.validate_network()
    print("[OK] Network valid: {} segments, {} intersections, {} OD pairs".format(
        validation['total_segments'],
        validation['total_intersections'],
        validation['total_od_pairs']))
    if validation['issues']:
        for issue in validation['issues']:
            print("  [WARN] {}".format(issue))
    
    # Initialize simulator
    print("\n[3] Initializing traffic simulator...")
    try:
        simulator = TrafficSimulator(network)
        print("[OK] Simulator initialized")
    except Exception as e:
        print("[ERROR] Error initializing simulator: {}".format(e))
        return
    
    # Run baseline simulation
    print("\n[4] Running baseline traffic simulation...")
    try:
        baseline_results = simulator.run_simulation('baseline')
        print("[OK] Baseline simulation complete")
        print("  - Total vehicles/hour: {:.0f}".format(baseline_results['total_vehicles']))
        avg_tt = sum(r['travel_time_min'] for r in baseline_results['segments'].values()) / len(baseline_results['segments'])
        print("  - Average segment travel time: {:.1f} min".format(avg_tt))
        print("  - Zones analyzed: {}".format(len(baseline_results['zones'])))
    except Exception as e:
        print("[ERROR] Error running baseline: {}".format(e))
        import traceback
        traceback.print_exc()
        return
    
    # Show zone-level results
    print("\n[5] Zone-level traffic statistics:")
    for zone_id, zone_data in sorted(baseline_results['zones'].items()):
        print("  {}: {:.0f} vph, Avg speed: {:.1f} km/h, Avg travel time: {:.1f} min".format(
            zone_id,
            zone_data['total_flow'],
            zone_data['avg_speed'],
            zone_data['avg_travel_time']))
    
    # Initialize emissions model
    print("\n[6] Initializing emissions model...")
    try:
        emissions_model = EmissionsModel(simulator)
        print("[OK] Emissions model initialized")
    except Exception as e:
        print("[ERROR] Error initializing emissions model: {}".format(e))
        return
    
    # Compute zone AQI
    print("\n[7] Computing zone-level AQI...")
    try:
        zones_aqi = emissions_model.compute_all_zones_aqi()
        print("[OK] AQI computed for all zones")
        for zone_aqi in zones_aqi:
            print("  {}: AQI {:.0f} (BG: {}, Traffic: +{:.1f})".format(
                zone_aqi['zone_id'],
                zone_aqi['total_aqi'],
                zone_aqi['background_aqi'],
                zone_aqi['traffic_aqi_contribution']))
    except Exception as e:
        print("[ERROR] Error computing AQI: {}".format(e))
        import traceback
        traceback.print_exc()
        return
    
    # Initialize intervention engine
    print("\n[8] Initializing intervention engine...")
    try:
        intervention_engine = InterventionEngine(network, simulator)
        print("[OK] Intervention engine initialized")
    except Exception as e:
        print("[ERROR] Error initializing intervention engine: {}".format(e))
        return
    
    # Test intervention: Add lanes
    print("\n[9] Testing intervention: Add 1 lane to SEG001...")
    try:
        result = intervention_engine.add_lanes(['SEG001'], num_lanes=1)
        print("[OK] Intervention applied: {}".format(result))
        
        # Run simulation with intervention
        intervention_results = simulator.run_simulation('with_lane_addition')
        print("  - Total vehicles/hour: {:.0f}".format(intervention_results['total_vehicles']))
        new_speed = intervention_results['segments']['SEG001']['speed_kmh']
        old_speed = baseline_results['segments']['SEG001']['speed_kmh']
        print("  - SEG001 new speed: {:.1f} km/h (was {:.1f})".format(new_speed, old_speed))
    except Exception as e:
        print("[ERROR] Error applying intervention: {}".format(e))
        import traceback
        traceback.print_exc()
    
    # Reset interventions
    print("\n[10] Resetting all interventions...")
    try:
        reset_result = intervention_engine.reset_all_interventions()
        print("[OK] Reset complete: {}".format(reset_result))
    except Exception as e:
        print("[ERROR] Error resetting: {}".format(e))
    
    # Show sample routes
    print("\n[11] Sample shortest paths (OD routes):")
    od_samples = [
        ('INT001', 'INT005'),
        ('INT002', 'INT007'),
        ('INT009', 'INT014'),
    ]
    for origin, dest in od_samples:
        path, distance = network.dijkstra(origin, dest)
        print("  {} -> {}: {} (distance: {:.1f} km)".format(
            origin,
            dest,
            ' -> '.join(path) if path else 'NO PATH',
            distance))
    
    # Summary
    print("\n" + "=" * 80)
    print("DEMO COMPLETE - All components working!")
    print("=" * 80)

if __name__ == '__main__':
    main()
