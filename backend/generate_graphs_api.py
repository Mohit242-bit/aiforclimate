"""
Flask endpoint to generate graphs and return them as base64
"""
import subprocess
import json
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.graph_generator import generate_graphs

def generate_emergency_graphs(baseline_zones, emergency_zones):
    """Generate graphs and return as base64 encoded images"""
    try:
        graphs = generate_graphs(baseline_zones, emergency_zones)
        return {
            'status': 'success',
            'graphs': graphs
        }
    except Exception as e:
        print(f"[Error] Graph generation failed: {e}")
        return {
            'status': 'error',
            'error': str(e),
            'graphs': {}
        }

if __name__ == '__main__':
    # Test
    baseline = [
        {'name': 'Zone 1', 'aqi': 328},
        {'name': 'Zone 2', 'aqi': 315},
        {'name': 'Zone 3', 'aqi': 342},
        {'name': 'Zone 4', 'aqi': 305},
        {'name': 'Zone 5', 'aqi': 320}
    ]
    
    emergency = [
        {'name': 'Zone 1', 'aqi': 265},
        {'name': 'Zone 2', 'aqi': 270},
        {'name': 'Zone 3', 'aqi': 285},
        {'name': 'Zone 4', 'aqi': 245},
        {'name': 'Zone 5', 'aqi': 260}
    ]
    
    result = generate_emergency_graphs(baseline, emergency)
    print(json.dumps({'status': result['status'], 'graph_count': len(result['graphs'])}))
