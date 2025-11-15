import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from src.models.corridor_network import CorridorNetwork

class TrafficSimulator:
    """
    Macroscopic traffic simulator using BPR (Bureau of Public Roads) congestion model.
    Routes OD flows through shortest paths and computes travel times/emissions.
    """
    
    def __init__(self, network: CorridorNetwork):
        """
        Initialize simulator with corridor network.
        
        Args:
            network: CorridorNetwork instance
        """
        self.network = network
        self.simulation_results = {}
        self.segment_flows = {}  # Accumulated flows on each segment
        self.segment_speeds = {}  # Speed on each segment
        self.segment_travel_times = {}
        self.od_paths = {}  # Pre-computed OD paths
        
        self._precompute_od_paths()
        self._reset_segment_state()
    
    def _precompute_od_paths(self):
        """Pre-compute shortest paths for all OD pairs."""
        od_pairs = self.network.od_matrix_df.groupby(['origin_intersection', 'destination_intersection']).first().index
        for origin, destination in od_pairs:
            path, dist = self.network.dijkstra(origin, destination)
            self.od_paths[(origin, destination)] = {
                'segments': path,
                'distance': dist,
            }
    
    def _reset_segment_state(self):
        """Reset all segment flows and speeds to zero/free-flow."""
        for seg_id, seg_data in self.network.segment_data.items():
            self.segment_flows[seg_id] = 0.0
            self.segment_speeds[seg_id] = seg_data['speed_limit_kmh']
            self.segment_travel_times[seg_id] = seg_data['length_km'] / seg_data['speed_limit_kmh']
    
    def _bpr_congestion_curve(self, flow: float, capacity: float, free_speed: float) -> float:
        """
        BPR congestion model: speed decreases as flow approaches capacity.
        
        Speed = free_speed * (1 / (1 + 0.15 * (flow/capacity)^4))
        
        Args:
            flow: Current flow (vehicles/hour)
            capacity: Segment capacity (vehicles/hour)
            free_speed: Free-flow speed (km/h)
            
        Returns:
            Current speed (km/h)
        """
        if flow <= 0:
            return free_speed
        
        # Capacity calculation: lanes * ~1200 vehicles/hour per lane
        flow_ratio = flow / max(capacity, 1.0)
        
        if flow_ratio > 1.0:
            # Over-capacity: queue formation
            speed = free_speed * 0.3  # Reduced to 30% of free speed
            # Calculate queue length (vehicles)
            excess = flow - capacity
            self.network.segment_data[list(self.segment_flows.keys())[0]]['queue_length'] = excess / 60  # vehicles
        else:
            # BPR formula
            speed = free_speed / (1.0 + 0.15 * (flow_ratio ** 4))
        
        return max(speed, 5.0)  # Minimum speed 5 km/h
    
    def _calculate_signal_delay(self, intersection_id: str, flow: float) -> float:
        """
        Calculate signal delay at intersection (minutes).
        Uses Webster's formula for delay at signalized intersections.
        """
        int_data = self.network.get_intersection(intersection_id)
        if not int_data.get('has_signal', False):
            return 0.0
        
        cycle_time = int_data.get('cycle_time_sec', 120)
        green_time = int_data.get('green_time_sec', 50)
        
        # Effective green ratio
        g_over_c = green_time / cycle_time
        
        # Assume capacity = 1800 veh/hour for intersection approach
        capacity = 1800.0 * g_over_c
        x = min(0.95, flow / capacity)  # Degree of saturation
        
        # Webster's delay formula (seconds)
        term1 = (cycle_time * (1 - g_over_c)**2) / (2 * (1 - x * g_over_c))
        term2 = (x**2) / (2 * flow / 3600 * (1 - x))
        delay_sec = term1 + term2
        
        return delay_sec / 60.0  # Convert to minutes
    
    def _calculate_segment_capacity(self, segment_id: str) -> float:
        """
        Calculate capacity of segment (vehicles per hour).
        Capacity = lanes * 1200 (standard assumption for urban roads)
        """
        seg = self.network.get_segment(segment_id)
        lanes = seg.get('lanes', 2)
        return lanes * 1200.0  # vehicles/hour per lane
    
    def _route_od_flow(self, origin: str, destination: str, vehicles_per_hour: float, vehicle_type: str = 'Car'):
        """
        Route OD flow through shortest path, accumulating on segments.
        
        Args:
            origin: Origin intersection ID
            destination: Destination intersection ID
            vehicles_per_hour: Flow magnitude
            vehicle_type: 'Car' or 'Truck'
        """
        if (origin, destination) not in self.od_paths:
            return  # No path found
        
        path_data = self.od_paths[(origin, destination)]
        segments = path_data['segments']
        
        for seg_id in segments:
            self.segment_flows[seg_id] += vehicles_per_hour
    
    def run_simulation(self, scenario_name: str = 'baseline') -> Dict:
        """
        Run traffic simulation for all OD pairs.
        
        Args:
            scenario_name: Name of scenario (for results tracking)
            
        Returns:
            Results dictionary with flow, speed, travel time per segment
        """
        # Reset state
        self._reset_segment_state()
        
        # Route all OD flows
        for _, row in self.network.od_matrix_df.iterrows():
            origin = row['origin_intersection']
            destination = row['destination_intersection']
            flow = row['vehicles_per_hour']
            vtype = row['vehicle_type']
            
            self._route_od_flow(origin, destination, flow, vtype)
        
        # Compute speeds and travel times using BPR model
        for seg_id in self.network.get_all_segments():
            seg = self.network.get_segment(seg_id)
            flow = self.segment_flows[seg_id]
            free_speed = seg['speed_limit_kmh']
            capacity = self._calculate_segment_capacity(seg_id)
            
            # Apply congestion model
            speed = self._bpr_congestion_curve(flow, capacity, free_speed)
            self.segment_speeds[seg_id] = speed
            
            # Travel time = length / speed (hours)
            length = seg['length_km']
            travel_time_hours = length / max(speed, 1.0)
            travel_time_min = travel_time_hours * 60  # Convert to minutes
            self.segment_travel_times[seg_id] = travel_time_min
            
            # Update network state
            self.network.update_segment_state(seg_id, flow, speed, flow / capacity)
        
        # Aggregate results
        self.simulation_results[scenario_name] = {
            'total_vehicles': self.network.od_matrix_df['vehicles_per_hour'].sum(),
            'segments': self._compile_segment_results(),
            'zones': self._compile_zone_results(),
            'od_travel_times': self._compile_od_travel_times(),
        }
        
        return self.simulation_results[scenario_name]
    
    def _compile_segment_results(self) -> Dict[str, Dict]:
        """Compile results for all segments."""
        results = {}
        for seg_id in self.network.get_all_segments():
            seg = self.network.get_segment(seg_id)
            results[seg_id] = {
                'flow_vph': self.segment_flows[seg_id],
                'speed_kmh': self.segment_speeds[seg_id],
                'travel_time_min': self.segment_travel_times[seg_id],
                'congestion_ratio': self.segment_flows[seg_id] / self._calculate_segment_capacity(seg_id),
                'road_name': seg['road_name'],
                'zone_id': seg['zone_id'],
            }
        return results
    
    def _compile_zone_results(self) -> Dict[str, Dict]:
        """Aggregate segment results to zone level."""
        zones = {}
        for seg_id, seg_results in self._compile_segment_results().items():
            zone_id = seg_results['zone_id']
            if zone_id not in zones:
                zones[zone_id] = {
                    'total_flow': 0,
                    'avg_speed': 0,
                    'avg_travel_time': 0,
                    'num_segments': 0,
                    'total_distance': 0,
                }
            zones[zone_id]['total_flow'] += seg_results['flow_vph']
            zones[zone_id]['avg_speed'] += seg_results['speed_kmh']
            zones[zone_id]['avg_travel_time'] += seg_results['travel_time_min']
            zones[zone_id]['num_segments'] += 1
            zones[zone_id]['total_distance'] += self.network.get_segment(seg_id)['length_km']
        
        # Compute averages
        for zone_id in zones:
            n = zones[zone_id]['num_segments']
            if n > 0:
                zones[zone_id]['avg_speed'] /= n
                zones[zone_id]['avg_travel_time'] /= n
        
        return zones
    
    def _compile_od_travel_times(self) -> List[Dict]:
        """Compile travel time for each OD pair."""
        results = []
        for (origin, dest), path_data in self.od_paths.items():
            segments = path_data['segments']
            total_time_min = sum(self.segment_travel_times.get(seg, 0) for seg in segments)
            results.append({
                'origin': origin,
                'destination': dest,
                'travel_time_min': total_time_min,
                'distance_km': path_data['distance'],
                'num_segments': len(segments),
            })
        return results
    
    def get_segment_results(self, segment_id: str) -> Dict:
        """Get detailed results for a specific segment."""
        if not self.simulation_results:
            return {}
        
        baseline = list(self.simulation_results.values())[0]
        return baseline['segments'].get(segment_id, {})
    
    def get_zone_results(self, zone_id: str) -> Dict:
        """Get aggregated results for a zone."""
        if not self.simulation_results:
            return {}
        
        baseline = list(self.simulation_results.values())[0]
        return baseline['zones'].get(zone_id, {})
    
    def reset_simulation(self):
        """Reset simulator to clean state."""
        self._reset_segment_state()
        self.simulation_results = {}
