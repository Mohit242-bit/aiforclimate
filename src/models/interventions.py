from typing import Dict, List, Tuple
from src.models.corridor_network import CorridorNetwork
from src.models.traffic_simulator import TrafficSimulator

class InterventionEngine:
    """
    Policy intervention system for traffic simulation.
    Supports lane modifications, signal tuning, closures, and bans.
    """
    
    def __init__(self, network: CorridorNetwork, simulator: TrafficSimulator):
        """
        Initialize intervention engine.
        
        Args:
            network: CorridorNetwork instance
            simulator: TrafficSimulator instance
        """
        self.network = network
        self.simulator = simulator
        self.active_interventions = {}  # Track applied interventions
        self.baseline_state = self._capture_state()
    
    def _capture_state(self) -> Dict:
        """Capture current network state for rollback."""
        state = {}
        for seg_id, seg_data in self.network.segment_data.items():
            state[seg_id] = {
                'lanes': seg_data['lanes'],
                'speed_limit_kmh': seg_data['speed_limit_kmh'],
            }
        return state
    
    def _restore_state(self, state: Dict):
        """Restore network to previous state."""
        for seg_id, seg_state in state.items():
            self.network.segment_data[seg_id]['lanes'] = seg_state['lanes']
            self.network.segment_data[seg_id]['speed_limit_kmh'] = seg_state['speed_limit_kmh']
    
    def add_lanes(self, segment_ids: List[str], num_lanes: int = 1) -> Dict:
        """
        Add lanes to specified segments.
        
        Args:
            segment_ids: List of segment IDs to modify
            num_lanes: Number of lanes to add
            
        Returns:
            Result with affected segments and impact
        """
        intervention_id = f"add_lanes_{len(self.active_interventions)}"
        self.active_interventions[intervention_id] = {
            'type': 'add_lanes',
            'segments': segment_ids,
            'num_lanes': num_lanes,
            'previous_lanes': {},
        }
        
        for seg_id in segment_ids:
            if seg_id in self.network.segment_data:
                seg = self.network.segment_data[seg_id]
                self.active_interventions[intervention_id]['previous_lanes'][seg_id] = seg['lanes']
                seg['lanes'] += num_lanes
        
        return {
            'intervention_id': intervention_id,
            'type': 'add_lanes',
            'segments_affected': len(segment_ids),
            'change': f"+{num_lanes} lanes",
        }
    
    def modify_signal_timing(self, intersection_ids: List[str], 
                            new_cycle_time: int = None, 
                            new_green_time: int = None) -> Dict:
        """
        Modify signal timings at intersections.
        
        Args:
            intersection_ids: List of intersection IDs
            new_cycle_time: New cycle time in seconds
            new_green_time: New green time in seconds
            
        Returns:
            Result with modified intersections
        """
        intervention_id = f"signal_modify_{len(self.active_interventions)}"
        self.active_interventions[intervention_id] = {
            'type': 'signal_timing',
            'intersections': intersection_ids,
            'previous_timings': {},
        }
        
        for int_id in intersection_ids:
            if int_id in self.network.intersection_data:
                intersection = self.network.intersection_data[int_id]
                self.active_interventions[intervention_id]['previous_timings'][int_id] = {
                    'cycle_time': intersection['cycle_time_sec'],
                    'green_time': intersection['green_time_sec'],
                }
                
                if new_cycle_time is not None:
                    intersection['cycle_time_sec'] = new_cycle_time
                if new_green_time is not None:
                    intersection['green_time_sec'] = new_green_time
        
        return {
            'intervention_id': intervention_id,
            'type': 'signal_timing',
            'intersections_affected': len(intersection_ids),
            'new_cycle_time': new_cycle_time,
            'new_green_time': new_green_time,
        }
    
    def close_segment(self, segment_ids: List[str]) -> Dict:
        """
        Close segments (e.g., for construction or restrictions).
        Routes traffic around closed segments.
        
        Args:
            segment_ids: List of segment IDs to close
            
        Returns:
            Result with closed segments
        """
        intervention_id = f"close_segment_{len(self.active_interventions)}"
        self.active_interventions[intervention_id] = {
            'type': 'segment_closure',
            'segments': segment_ids,
        }
        
        # Mark segments with zero lanes to effectively close them
        for seg_id in segment_ids:
            if seg_id in self.network.segment_data:
                self.network.segment_data[seg_id]['lanes'] = 0
        
        return {
            'intervention_id': intervention_id,
            'type': 'segment_closure',
            'segments_closed': len(segment_ids),
        }
    
    def truck_ban(self, segment_ids: List[str], time_window: Tuple[int, int] = None) -> Dict:
        """
        Ban trucks on specified segments.
        
        Args:
            segment_ids: List of segment IDs
            time_window: Tuple of (start_hour, end_hour), e.g., (6, 12)
            
        Returns:
            Result with ban details
        """
        intervention_id = f"truck_ban_{len(self.active_interventions)}"
        self.active_interventions[intervention_id] = {
            'type': 'truck_ban',
            'segments': segment_ids,
            'time_window': time_window,
        }
        
        # In actual simulation, OD matrix would be filtered
        # For now, just track the intervention
        
        return {
            'intervention_id': intervention_id,
            'type': 'truck_ban',
            'segments_affected': len(segment_ids),
            'time_window': time_window or '24h',
        }
    
    def reroute_traffic(self, from_segment: str, to_segments: List[str], 
                       percentage: float = 100.0) -> Dict:
        """
        Reroute percentage of traffic from one segment to alternatives.
        
        Args:
            from_segment: Segment to reroute traffic from
            to_segments: Alternative segments to reroute to
            percentage: Percentage of traffic to reroute (0-100)
            
        Returns:
            Result with rerouting plan
        """
        intervention_id = f"reroute_{len(self.active_interventions)}"
        self.active_interventions[intervention_id] = {
            'type': 'traffic_reroute',
            'from_segment': from_segment,
            'to_segments': to_segments,
            'percentage': percentage,
        }
        
        return {
            'intervention_id': intervention_id,
            'type': 'traffic_reroute',
            'from_segment': from_segment,
            'to_segments': len(to_segments),
            'percentage': percentage,
        }
    
    def apply_multiple_interventions(self, interventions: List[Dict]) -> Dict:
        """
        Apply multiple interventions sequentially.
        
        Args:
            interventions: List of intervention dictionaries
            
        Returns:
            Results of all applied interventions
        """
        results = []
        
        for interv in interventions:
            interv_type = interv.get('type')
            
            if interv_type == 'add_lanes':
                result = self.add_lanes(
                    interv['segment_ids'],
                    interv.get('num_lanes', 1)
                )
            elif interv_type == 'signal_timing':
                result = self.modify_signal_timing(
                    interv['intersection_ids'],
                    interv.get('cycle_time'),
                    interv.get('green_time')
                )
            elif interv_type == 'segment_closure':
                result = self.close_segment(interv['segment_ids'])
            elif interv_type == 'truck_ban':
                result = self.truck_ban(
                    interv['segment_ids'],
                    interv.get('time_window')
                )
            elif interv_type == 'reroute':
                result = self.reroute_traffic(
                    interv['from_segment'],
                    interv['to_segments'],
                    interv.get('percentage', 100)
                )
            else:
                result = {'error': f'Unknown intervention type: {interv_type}'}
            
            results.append(result)
        
        return {'interventions_applied': results}
    
    def get_active_interventions(self) -> Dict:
        """Get list of currently active interventions."""
        return self.active_interventions
    
    def rollback_intervention(self, intervention_id: str) -> Dict:
        """
        Rollback a specific intervention.
        
        Args:
            intervention_id: ID of intervention to rollback
            
        Returns:
            Result of rollback
        """
        if intervention_id not in self.active_interventions:
            return {'error': f'Intervention {intervention_id} not found'}
        
        intervention = self.active_interventions[intervention_id]
        
        if intervention['type'] == 'add_lanes':
            for seg_id, prev_lanes in intervention['previous_lanes'].items():
                self.network.segment_data[seg_id]['lanes'] = prev_lanes
        
        elif intervention['type'] == 'signal_timing':
            for int_id, prev_timings in intervention['previous_timings'].items():
                self.network.intersection_data[int_id].update(prev_timings)
        
        del self.active_interventions[intervention_id]
        
        return {
            'intervention_id': intervention_id,
            'status': 'rolled_back',
        }
    
    def reset_all_interventions(self) -> Dict:
        """Reset network to baseline state (no interventions)."""
        intervention_ids = list(self.active_interventions.keys())
        
        for intervention_id in intervention_ids:
            self.rollback_intervention(intervention_id)
        
        return {
            'interventions_reset': len(intervention_ids),
            'status': 'baseline_restored',
        }
    
    def estimate_impact(self, intervention_id: str) -> Dict:
        """
        Estimate impact of an intervention by running simulation.
        
        Args:
            intervention_id: ID of intervention to test
            
        Returns:
            Impact analysis
        """
        # Run baseline
        baseline_result = self.simulator.run_simulation('baseline')
        
        # Run with intervention (already applied)
        intervention_result = self.simulator.run_simulation(f'intervention_{intervention_id}')
        
        baseline_flow = baseline_result['total_vehicles']
        intervention_flow = intervention_result['total_vehicles']
        
        return {
            'intervention_id': intervention_id,
            'baseline_total_flow': baseline_flow,
            'intervention_total_flow': intervention_flow,
            'flow_change_percent': ((intervention_flow - baseline_flow) / baseline_flow * 100) if baseline_flow > 0 else 0,
        }
