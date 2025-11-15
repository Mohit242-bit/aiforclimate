"""
Generate professional matplotlib/seaborn visualizations for Emergency Protocol results
"""
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import base64
from io import BytesIO

# Set style
sns.set_theme(style="darkgrid", palette="husl")
plt.rcParams['figure.facecolor'] = '#1a1a2e'
plt.rcParams['axes.facecolor'] = '#16213e'
plt.rcParams['text.color'] = 'white'
plt.rcParams['axes.labelcolor'] = 'white'
plt.rcParams['xtick.color'] = 'white'
plt.rcParams['ytick.color'] = 'white'

def generate_graphs(baseline_zones, emergency_zones):
    """Generate all graphs and return as base64 encoded images"""
    
    graphs = {}
    
    # Extract data
    zone_names = [z.get('name', f"Zone {i+1}") for i, z in enumerate(baseline_zones)]
    baseline_aqi = [z.get('aqi', 0) for z in baseline_zones]
    emergency_aqi = [z.get('aqi', 0) for z in emergency_zones]
    aqi_reduction = [b - e for b, e in zip(baseline_aqi, emergency_aqi)]
    
    # 1. AQI Comparison - Side by side bars
    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(zone_names))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, baseline_aqi, width, label='Baseline', color='#ef4444', alpha=0.8)
    bars2 = ax.bar(x + width/2, emergency_aqi, width, label='Emergency Response', color='#10b981', alpha=0.8)
    
    ax.set_xlabel('Zones', fontsize=12, fontweight='bold')
    ax.set_ylabel('AQI Level', fontsize=12, fontweight='bold')
    ax.set_title('🚨 Baseline vs Emergency Protocol AQI Comparison', fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(zone_names, rotation=45, ha='right')
    ax.legend(fontsize=11)
    ax.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom', fontsize=9, fontweight='bold', color='white')
    
    fig.tight_layout()
    graphs['aqi_comparison'] = fig_to_base64(fig)
    plt.close(fig)
    
    # 2. AQI Reduction Impact
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = ['#10b981' if x > 40 else '#f59e0b' if x > 20 else '#ef4444' for x in aqi_reduction]
    bars = ax.barh(zone_names, aqi_reduction, color=colors, alpha=0.8)
    
    ax.set_xlabel('AQI Reduction Points', fontsize=12, fontweight='bold')
    ax.set_title('📊 AQI Reduction Impact per Zone', fontsize=14, fontweight='bold', pad=20)
    ax.grid(axis='x', alpha=0.3)
    
    # Add value labels
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax.text(width, bar.get_y() + bar.get_height()/2.,
               f'{width:.0f}',
               ha='left', va='center', fontsize=11, fontweight='bold', color='white')
    
    fig.tight_layout()
    graphs['aqi_reduction'] = fig_to_base64(fig)
    plt.close(fig)
    
    # 3. Percentage Reduction
    fig, ax = plt.subplots(figsize=(12, 6))
    pct_reduction = [(b - e) / b * 100 if b > 0 else 0 for b, e in zip(baseline_aqi, emergency_aqi)]
    colors_pct = ['#10b981' if x > 15 else '#f59e0b' for x in pct_reduction]
    bars = ax.bar(zone_names, pct_reduction, color=colors_pct, alpha=0.8)
    
    ax.set_ylabel('Reduction (%)', fontsize=12, fontweight='bold')
    ax.set_title('📈 Percentage AQI Reduction', fontsize=14, fontweight='bold', pad=20)
    ax.set_xticklabels(zone_names, rotation=45, ha='right')
    ax.grid(axis='y', alpha=0.3)
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'{height:.1f}%',
               ha='center', va='bottom', fontsize=10, fontweight='bold', color='white')
    
    fig.tight_layout()
    graphs['percentage_reduction'] = fig_to_base64(fig)
    plt.close(fig)
    
    # 4. Before/After Line Chart
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(zone_names, baseline_aqi, marker='o', linewidth=3, markersize=10,
           label='Baseline', color='#ef4444', linestyle='--', alpha=0.8)
    ax.plot(zone_names, emergency_aqi, marker='s', linewidth=3, markersize=10,
           label='Emergency Response', color='#10b981', alpha=0.8)
    
    ax.set_ylabel('AQI Level', fontsize=12, fontweight='bold')
    ax.set_title('📉 AQI Trend: Before & After', fontsize=14, fontweight='bold', pad=20)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_xticklabels(zone_names, rotation=45, ha='right')
    
    fig.tight_layout()
    graphs['trend_chart'] = fig_to_base64(fig)
    plt.close(fig)
    
    return graphs

def fig_to_base64(fig):
    """Convert matplotlib figure to base64 encoded string"""
    buffer = BytesIO()
    fig.savefig(buffer, format='png', bbox_inches='tight', facecolor='#1a1a2e', edgecolor='#667eea')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode()
    buffer.close()
    return f"data:image/png;base64,{image_base64}"

# Export for use in React
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
    
    graphs = generate_graphs(baseline, emergency)
    print(f"Generated {len(graphs)} graphs")
    for name, data in graphs.items():
        print(f"{name}: {len(data)} bytes")
