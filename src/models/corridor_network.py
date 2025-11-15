import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import heapq
from math import radians, cos, sin, asin, sqrt

class CorridorNetwork:
    """
    Graph-based corridor network for Delhi traffic simulation.
    Supports Dijkstra routing and OD-based traffic assignment.
    """
    
    def __init__(self, segments_csv: str, intersections_csv: str, od_matrix_csv: str):
        """
        Initialize network from CSV files.
        
        Args:
            segments_csv: Path to corridor_segments.csv
            intersections_csv: Path to intersections.csv
            od_matrix_csv: Path to od_matrix.csv
        """
        self.segments_df = pd.read_csv(segments_csv)
        self.intersections_df = pd.read_csv(intersections_csv)
        self.od_matrix_df = pd.read_csv(od_matrix_csv)
        
        # Build graph structure
        self.graph = {}  # Dict[str, List[str]] - adjacency list
        self.segment_data = {}  # Dict[str, Dict] - segment properties
        self.intersection_data = {}  # Dict[str, Dict] - intersection properties
        self.precomputed_paths = {}  # Cache for shortest paths
        
        self._build_graph()
        self._build_intersection_data()
        
    def _build_graph(self):
        """Build adjacency list and segment data from CSV."""
        for _, row in self.segments_df.iterrows():
            seg_id = row['segment_id']
            from_int = row['from_intersection']
            to_int = row['to_intersection']
            
            # Store segment data
            self.segment_data[seg_id] = {
                'from': from_int,
                'to': to_int,
                'length_km': row['length_km'],
                'lanes': row['lanes'],
                'speed_limit_kmh': row['speed_limit_kmh'],
                'is_one_way': row['is_one_way'],
                'zone_id': row['zone_id'],
                'road_type': row['road_type'],
                'road_name': row['road_name'],
                'current_flow': 0,  # vehicles/hour
                'current_speed': row['speed_limit_kmh'],  # km/h (will be updated by simulator)
                'queue_length': 0,  # vehicles
            }
            
            # Build adjacency list (directed)
            if from_int not in self.graph:
                self.graph[from_int] = []
            self.graph[from_int].append((to_int, seg_id))
            
    def _build_intersection_data(self):
        """Build intersection metadata."""
        for _, row in self.intersections_df.iterrows():
            int_id = row['intersection_id']
            self.intersection_data[int_id] = {
                'lat': row['latitude'],
                'lon': row['longitude'],
                'has_signal': row['has_signal'],
                'cycle_time_sec': row['cycle_time_sec'],
                'green_time_sec': row['green_time_sec'],
                'road_name': row['road_name'],
                'zone_id': row['zone_id'],
            }
    
    def _haversine_distance(self, lat1, lon1, lat2, lon2) -> float:
        """Calculate distance between two lat/lon points in km."""
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371  # Earth radius in km
        return c * r
    
    def dijkstra(self, origin: str, destination: str) -> Tuple[List[str], float]:
        """
        Find shortest path from origin to destination using Dijkstra.
        
        Args:
            origin: Origin intersection ID
            destination: Destination intersection ID
            
        Returns:
            (path_segment_ids, total_distance_km)
        """
        cache_key = (origin, destination)
        if cache_key in self.precomputed_paths:
            return self.precomputed_paths[cache_key]
        
        # Dijkstra's algorithm on segment graph
        distances = {origin: 0}
        parent = {origin: None}
        parent_segment = {origin: None}
        pq = [(0, origin)]
        
        while pq:
            curr_dist, curr_node = heapq.heappop(pq)
            
            if curr_dist > distances.get(curr_node, float('inf')):
                continue
            
            if curr_node == destination:
                # Reconstruct path
                path_segments = []
                node = destination
                while parent[node] is not None:
                    path_segments.append(parent_segment[node])
                    node = parent[node]
                path_segments.reverse()
                total_dist = distances[destination]
                
                self.precomputed_paths[cache_key] = (path_segments, total_dist)
                return (path_segments, total_dist)
            
            # Explore neighbors
            if curr_node in self.graph:
                for next_node, seg_id in self.graph[curr_node]:
                    seg_length = self.segment_data[seg_id]['length_km']
                    new_dist = curr_dist + seg_length
                    
                    if new_dist < distances.get(next_node, float('inf')):
                        distances[next_node] = new_dist
                        parent[next_node] = curr_node
                        parent_segment[next_node] = seg_id
                        heapq.heappush(pq, (new_dist, next_node))
        
        # No path found
        return ([], float('inf'))
    
    def get_segment(self, segment_id: str) -> Dict:
        """Get segment data."""
        return self.segment_data.get(segment_id, {})
    
    def get_intersection(self, intersection_id: str) -> Dict:
        """Get intersection data."""
        return self.intersection_data.get(intersection_id, {})
    
    def get_segments_in_zone(self, zone_id: str) -> List[str]:
        """Get all segments in a zone."""
        return [seg_id for seg_id, data in self.segment_data.items() 
                if data['zone_id'] == zone_id]
    
    def update_segment_lanes(self, segment_id: str, new_lanes: int):
        """
        Dynamically update number of lanes on a segment.
        Simulates lane addition intervention.
        """
        if segment_id in self.segment_data:
            old_lanes = self.segment_data[segment_id]['lanes']
            self.segment_data[segment_id]['lanes'] = new_lanes
            print(f"[INFRA] Updated {segment_id} lanes: {old_lanes} → {new_lanes}")
            # Clear path cache as capacity changed
            self.precomputed_paths.clear()
            return True
        return False
    
    def close_segment(self, segment_id: str):
        """
        Close a segment (simulate road closure).
        Removes from graph, forces rerouting.
        """
        if segment_id not in self.segment_data:
            return False
        
        seg = self.segment_data[segment_id]
        from_int = seg['from']
        to_int = seg['to']
        
        # Mark as closed
        self.segment_data[segment_id]['closed'] = True
        
        # Remove from adjacency list
        if from_int in self.graph:
            self.graph[from_int] = [(n, s) for n, s in self.graph[from_int] if s != segment_id]
        
        print(f"[INFRA] Closed segment {segment_id}: {from_int} → {to_int}")
        self.precomputed_paths.clear()
        return True
    
    def reopen_segment(self, segment_id: str):
        """Reopen a previously closed segment."""
        if segment_id not in self.segment_data:
            return False
        
        seg = self.segment_data[segment_id]
        if not seg.get('closed', False):
            return False
        
        seg['closed'] = False
        from_int = seg['from']
        to_int = seg['to']
        
        # Re-add to graph
        if from_int not in self.graph:
            self.graph[from_int] = []
        self.graph[from_int].append((to_int, segment_id))
        
        print(f"[INFRA] Reopened segment {segment_id}")
        self.precomputed_paths.clear()
        return True
    
    def update_signal_timing(self, intersection_id: str, green_time_delta: int):
        """
        Update signal green time at intersection.
        Simulates signal tuning intervention.
        
        Args:
            intersection_id: Intersection to modify
            green_time_delta: Change in green time (seconds, can be negative)
        """
        if intersection_id in self.intersection_data:
            int_data = self.intersection_data[intersection_id]
            old_green = int_data['green_time_sec']
            new_green = max(15, min(90, old_green + green_time_delta))  # Clamp 15-90s
            int_data['green_time_sec'] = new_green
            print(f"[INFRA] Updated {intersection_id} green time: {old_green}s → {new_green}s")
            return True
        return False
    
    def get_network_topology(self) -> Dict:
        """
        Get complete network topology.
        Useful for validation and visualization.
        """
        return {
            'segments': len(self.segment_data),
            'intersections': len(self.intersection_data),
            'zones': len(set(s['zone_id'] for s in self.segment_data.values())),
            'total_length_km': sum(s['length_km'] for s in self.segment_data.values()),
            'total_lanes': sum(s['lanes'] for s in self.segment_data.values()),
            'signalized_intersections': sum(1 for i in self.intersection_data.values() if i['has_signal']),
            'segments_by_zone': {
                zone: len([s for s in self.segment_data.values() if s['zone_id'] == zone])
                for zone in set(s['zone_id'] for s in self.segment_data.values())
            }
        }
    
    def validate_network(self) -> Dict:
        """
        Validate network connectivity and structure.
        Returns validation report.
        """
        issues = []
        
        # Check for isolated intersections
        connected_ints = set(self.graph.keys())
        all_ints = set(self.intersection_data.keys())
        isolated = all_ints - connected_ints
        if isolated:
            issues.append(f"Isolated intersections: {isolated}")
        
        # Check for segments with invalid intersections
        for seg_id, seg in self.segment_data.items():
            if seg['from'] not in all_ints:
                issues.append(f"{seg_id}: from_intersection {seg['from']} not found")
            if seg['to'] not in all_ints:
                issues.append(f"{seg_id}: to_intersection {seg['to']} not found")
        
        # Check for unreachable intersections
        reachable = set()
        if self.graph:
            start = next(iter(self.graph.keys()))
            visited = {start}
            queue = [start]
            while queue:
                node = queue.pop(0)
                reachable.add(node)
                if node in self.graph:
                    for neighbor, _ in self.graph[node]:
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)
        
        unreachable = all_ints - reachable
        if unreachable:
            issues.append(f"Unreachable intersections: {unreachable}")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'topology': self.get_network_topology()
        }
    
    def get_all_segments(self) -> List[str]:
        """Get list of all segment IDs."""
        return list(self.segment_data.keys())
    
    def update_segment_state(self, segment_id: str, flow: float, speed: float, congestion_ratio: float):
        """Update segment state from simulator."""
        if segment_id in self.segment_data:
            self.segment_data[segment_id]['current_flow'] = flow
            self.segment_data[segment_id]['current_speed'] = speed
            self.segment_data[segment_id]['congestion_ratio'] = congestion_ratio
        return [seg_id for seg_id, data in self.segment_data.items() 
                if data['zone_id'] == zone_id]
    
    def get_intersections_in_zone(self, zone_id: str) -> List[str]:
        """Get all intersections in a zone."""
        return [int_id for int_id, data in self.intersection_data.items() 
                if data['zone_id'] == zone_id]
    
    def update_segment_state(self, segment_id: str, flow: float, speed: float, queue: float):
        """Update dynamic segment state (flow, speed, queue)."""
        if segment_id in self.segment_data:
            self.segment_data[segment_id]['current_flow'] = flow
            self.segment_data[segment_id]['current_speed'] = speed
            self.segment_data[segment_id]['queue_length'] = queue
    
    def get_all_segments(self) -> List[str]:
        """Get list of all segment IDs."""
        return list(self.segment_data.keys())
    
    def get_all_intersections(self) -> List[str]:
        """Get list of all intersection IDs."""
        return list(self.intersection_data.keys())
    
    def validate_network(self) -> Dict[str, any]:
        """Validate network connectivity and data integrity."""
        issues = []
        
        # Check for disconnected nodes
        all_nodes = set(self.graph.keys())
        for node in self.intersection_data.keys():
            if node not in all_nodes and node not in [seg['from'] for seg in self.segment_data.values()]:
                issues.append(f"Intersection {node} has no outgoing segments")
        
        # Check for orphan segments
        for seg_id, seg_data in self.segment_data.items():
            from_node = seg_data['from']
            to_node = seg_data['to']
            if from_node not in self.intersection_data:
                issues.append(f"Segment {seg_id} from invalid intersection {from_node}")
            if to_node not in self.intersection_data:
                issues.append(f"Segment {seg_id} to invalid intersection {to_node}")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'total_segments': len(self.segment_data),
            'total_intersections': len(self.intersection_data),
            'total_od_pairs': len(self.od_matrix_df),
        }
