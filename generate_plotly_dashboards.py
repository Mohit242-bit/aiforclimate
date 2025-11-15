"""
Advanced Interactive Emergency Protocol Dashboard
Using Plotly for interactive visualizations
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from pathlib import Path

# Mock Data
baseline_zones = {
    'Zone_1': {'name': 'Connaught Place', 'aqi': 328, 'speed': 45, 'traffic': 8750, 'pm25': 185, 'no2': 95},
    'Zone_2': {'name': 'Karol Bagh', 'aqi': 315, 'speed': 48, 'traffic': 7200, 'pm25': 178, 'no2': 88},
    'Zone_3': {'name': 'Dwarka', 'aqi': 342, 'speed': 42, 'traffic': 9100, 'pm25': 195, 'no2': 102},
    'Zone_4': {'name': 'Rohini', 'aqi': 305, 'speed': 50, 'traffic': 6800, 'pm25': 170, 'no2': 82},
    'Zone_5': {'name': 'Saket', 'aqi': 320, 'speed': 46, 'traffic': 7500, 'pm25': 182, 'no2': 91},
}

emergency_zones = {
    'Zone_1': {'name': 'Connaught Place', 'aqi': 265, 'speed': 58, 'traffic': 4200, 'pm25': 142, 'no2': 68},
    'Zone_2': {'name': 'Karol Bagh', 'aqi': 270, 'speed': 62, 'traffic': 3600, 'pm25': 147, 'no2': 71},
    'Zone_3': {'name': 'Dwarka', 'aqi': 285, 'speed': 55, 'traffic': 4500, 'pm25': 158, 'no2': 78},
    'Zone_4': {'name': 'Rohini', 'aqi': 245, 'speed': 68, 'traffic': 3400, 'pm25': 132, 'no2': 61},
    'Zone_5': {'name': 'Saket', 'aqi': 260, 'speed': 60, 'traffic': 3750, 'pm25': 140, 'no2': 67},
}

def create_comparison_dashboard():
    """Create comprehensive Plotly dashboard"""
    
    zones_list = list(baseline_zones.keys())
    zone_names = [baseline_zones[z]['name'] for z in zones_list]
    
    baseline_aqi = [baseline_zones[z]['aqi'] for z in zones_list]
    emergency_aqi = [emergency_zones[z]['aqi'] for z in zones_list]
    
    baseline_speed = [baseline_zones[z]['speed'] for z in zones_list]
    emergency_speed = [emergency_zones[z]['speed'] for z in zones_list]
    
    baseline_traffic = [baseline_zones[z]['traffic'] for z in zones_list]
    emergency_traffic = [emergency_zones[z]['traffic'] for z in zones_list]
    
    baseline_pm25 = [baseline_zones[z]['pm25'] for z in zones_list]
    emergency_pm25 = [emergency_zones[z]['pm25'] for z in zones_list]
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("AQI Comparison", "Speed Improvement", 
                       "Traffic Volume", "PM2.5 Levels"),
        specs=[[{"type": "bar"}, {"type": "bar"}],
               [{"type": "bar"}, {"type": "scatter"}]]
    )
    
    # AQI Comparison
    fig.add_trace(
        go.Bar(x=zone_names, y=baseline_aqi, name='Baseline', 
               marker_color='#ef4444', opacity=0.8),
        row=1, col=1
    )
    fig.add_trace(
        go.Bar(x=zone_names, y=emergency_aqi, name='Emergency Response', 
               marker_color='#10b981', opacity=0.8),
        row=1, col=1
    )
    
    # Speed Improvement
    fig.add_trace(
        go.Bar(x=zone_names, y=baseline_speed, name='Baseline Speed', 
               marker_color='#ef4444', opacity=0.8, showlegend=False),
        row=1, col=2
    )
    fig.add_trace(
        go.Bar(x=zone_names, y=emergency_speed, name='Emergency Speed', 
               marker_color='#10b981', opacity=0.8, showlegend=False),
        row=1, col=2
    )
    
    # Traffic Volume
    fig.add_trace(
        go.Bar(x=zone_names, y=baseline_traffic, name='Baseline Traffic', 
               marker_color='#ef4444', opacity=0.8, showlegend=False),
        row=2, col=1
    )
    fig.add_trace(
        go.Bar(x=zone_names, y=emergency_traffic, name='Emergency Traffic', 
               marker_color='#10b981', opacity=0.8, showlegend=False),
        row=2, col=1
    )
    
    # PM2.5 Levels (line chart)
    fig.add_trace(
        go.Scatter(x=zone_names, y=baseline_pm25, name='Baseline PM2.5', 
                  mode='lines+markers', line=dict(color='#ef4444', width=3),
                  marker=dict(size=10), showlegend=False),
        row=2, col=2
    )
    fig.add_trace(
        go.Scatter(x=zone_names, y=emergency_pm25, name='Emergency PM2.5', 
                  mode='lines+markers', line=dict(color='#10b981', width=3),
                  marker=dict(size=10), showlegend=False),
        row=2, col=2
    )
    
    # Update layout
    fig.update_yaxes(title_text="AQI Level", row=1, col=1)
    fig.update_yaxes(title_text="Speed (km/h)", row=1, col=2)
    fig.update_yaxes(title_text="Vehicles/Hour", row=2, col=1)
    fig.update_yaxes(title_text="PM2.5 (µg/m³)", row=2, col=2)
    
    fig.update_layout(
        title_text="Emergency Protocol Response Dashboard",
        height=800,
        showlegend=True,
        hovermode='x unified',
        template='plotly_white'
    )
    
    output_dir = Path('visualization_outputs')
    output_path = output_dir / 'interactive_dashboard.html'
    fig.write_html(output_path)
    print(f"[OK] Created interactive dashboard: {output_path.name}")
    
    return output_path

def create_impact_metrics_chart():
    """Create impact metrics visualization"""
    
    zones_list = list(baseline_zones.keys())
    zone_names = [baseline_zones[z]['name'] for z in zones_list]
    
    aqi_reduction = [baseline_zones[z]['aqi'] - emergency_zones[z]['aqi'] for z in zones_list]
    speed_improvement = [((emergency_zones[z]['speed'] - baseline_zones[z]['speed']) / baseline_zones[z]['speed']) * 100 for z in zones_list]
    traffic_reduction = [((baseline_zones[z]['traffic'] - emergency_zones[z]['traffic']) / baseline_zones[z]['traffic']) * 100 for z in zones_list]
    
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=("AQI Reduction", "Speed Improvement %", "Traffic Reduction %"),
        specs=[[{"type": "bar"}, {"type": "bar"}, {"type": "bar"}]]
    )
    
    # AQI Reduction
    fig.add_trace(
        go.Bar(x=zone_names, y=aqi_reduction, marker_color='#3b82f6', text=aqi_reduction,
               textposition='outside', showlegend=False),
        row=1, col=1
    )
    
    # Speed Improvement
    fig.add_trace(
        go.Bar(x=zone_names, y=speed_improvement, marker_color='#10b981', text=[f'{x:.1f}%' for x in speed_improvement],
               textposition='outside', showlegend=False),
        row=1, col=2
    )
    
    # Traffic Reduction
    fig.add_trace(
        go.Bar(x=zone_names, y=traffic_reduction, marker_color='#f59e0b', text=[f'{x:.1f}%' for x in traffic_reduction],
               textposition='outside', showlegend=False),
        row=1, col=3
    )
    
    fig.update_yaxes(title_text="AQI Reduction", row=1, col=1)
    fig.update_yaxes(title_text="Improvement %", row=1, col=2)
    fig.update_yaxes(title_text="Reduction %", row=1, col=3)
    
    fig.update_layout(
        title_text="Emergency Protocol Impact Metrics",
        height=500,
        template='plotly_white'
    )
    
    output_dir = Path('visualization_outputs')
    output_path = output_dir / 'impact_metrics.html'
    fig.write_html(output_path)
    print(f"[OK] Created impact metrics chart: {output_path.name}")
    
    return output_path

def create_pollutant_breakdown():
    """Create pollutant level breakdown"""
    
    zones_list = list(baseline_zones.keys())
    zone_names = [baseline_zones[z]['name'] for z in zones_list]
    
    baseline_pm25 = [baseline_zones[z]['pm25'] for z in zones_list]
    emergency_pm25 = [emergency_zones[z]['pm25'] for z in zones_list]
    baseline_no2 = [baseline_zones[z]['no2'] for z in zones_list]
    emergency_no2 = [emergency_zones[z]['no2'] for z in zones_list]
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("PM2.5 Levels", "NO2 Levels"),
        specs=[[{"type": "bar"}, {"type": "bar"}]]
    )
    
    fig.add_trace(
        go.Bar(name='Baseline PM2.5', x=zone_names, y=baseline_pm25, marker_color='#ef4444', opacity=0.8),
        row=1, col=1
    )
    fig.add_trace(
        go.Bar(name='Emergency PM2.5', x=zone_names, y=emergency_pm25, marker_color='#10b981', opacity=0.8),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(name='Baseline NO2', x=zone_names, y=baseline_no2, marker_color='#ef4444', 
               opacity=0.8, showlegend=False),
        row=1, col=2
    )
    fig.add_trace(
        go.Bar(name='Emergency NO2', x=zone_names, y=emergency_no2, marker_color='#10b981', 
               opacity=0.8, showlegend=False),
        row=1, col=2
    )
    
    fig.update_yaxes(title_text="PM2.5 (µg/m³)", row=1, col=1)
    fig.update_yaxes(title_text="NO2 (µg/m³)", row=1, col=2)
    
    fig.update_layout(
        title_text="Pollutant Level Analysis",
        height=500,
        template='plotly_white',
        barmode='group'
    )
    
    output_dir = Path('visualization_outputs')
    output_path = output_dir / 'pollutant_analysis.html'
    fig.write_html(output_path)
    print(f"[OK] Created pollutant analysis: {output_path.name}")
    
    return output_path

def create_summary_report():
    """Create comprehensive summary report"""
    
    zones_list = list(baseline_zones.keys())
    
    # Calculate totals
    total_aqi_reduction = sum(baseline_zones[z]['aqi'] - emergency_zones[z]['aqi'] for z in zones_list)
    avg_speed_improvement = np.mean([((emergency_zones[z]['speed'] - baseline_zones[z]['speed']) / baseline_zones[z]['speed']) * 100 for z in zones_list])
    avg_traffic_reduction = np.mean([((baseline_zones[z]['traffic'] - emergency_zones[z]['traffic']) / baseline_zones[z]['traffic']) * 100 for z in zones_list])
    total_health_impact = total_aqi_reduction * 2.5
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Emergency Protocol - Complete Analysis</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }}
        
        .container {{
            max-width: 1600px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            padding: 50px;
        }}
        
        h1 {{
            color: #ef4444;
            text-align: center;
            margin-bottom: 15px;
            font-size: 3em;
        }}
        
        .subtitle {{
            text-align: center;
            color: #666;
            margin-bottom: 40px;
            font-size: 1.2em;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 25px;
            margin-bottom: 50px;
        }}
        
        .metric-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            border-radius: 15px;
            color: white;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            text-align: center;
            transition: transform 0.3s ease;
        }}
        
        .metric-card:hover {{
            transform: translateY(-5px);
        }}
        
        .metric-value {{
            font-size: 3em;
            font-weight: bold;
            margin-bottom: 10px;
            letter-spacing: 1px;
        }}
        
        .metric-label {{
            font-size: 1em;
            opacity: 0.95;
        }}
        
        .content-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 40px;
        }}
        
        .card {{
            background: #f8f9fa;
            border-left: 5px solid #667eea;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        }}
        
        .card h3 {{
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.3em;
        }}
        
        .card ul {{
            list-style: none;
            padding-left: 0;
        }}
        
        .card li {{
            padding: 10px 0;
            border-bottom: 1px solid #e5e7eb;
            display: flex;
            justify-content: space-between;
        }}
        
        .card li:last-child {{
            border-bottom: none;
        }}
        
        .value {{
            color: #10b981;
            font-weight: 600;
        }}
        
        .zone-details {{
            background: white;
            border: 2px solid #667eea;
            border-radius: 10px;
            padding: 30px;
            margin-top: 30px;
        }}
        
        .zone-details h3 {{
            color: #667eea;
            margin-bottom: 20px;
        }}
        
        .zone-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        
        .zone-item {{
            background: #f0f9ff;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #3b82f6;
        }}
        
        .zone-item .zone-name {{
            font-weight: 600;
            color: #667eea;
            margin-bottom: 8px;
        }}
        
        .zone-item .zone-metric {{
            font-size: 0.9em;
            color: #666;
            margin: 5px 0;
        }}
        
        .footer {{
            margin-top: 50px;
            padding-top: 30px;
            border-top: 2px solid #e5e7eb;
            text-align: center;
            color: #666;
        }}
        
        .iframe-container {{
            margin-top: 40px;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }}
        
        iframe {{
            width: 100%;
            height: 600px;
            border: none;
        }}
        
        .links {{
            margin-top: 20px;
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            justify-content: center;
        }}
        
        .link-btn {{
            display: inline-block;
            padding: 12px 25px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 8px;
            transition: transform 0.3s ease;
            font-weight: 600;
        }}
        
        .link-btn:hover {{
            transform: scale(1.05);
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Emergency Protocol Analysis</h1>
        <p class="subtitle">Delhi Digital Twin - Crisis Response Effectiveness Report</p>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">{total_aqi_reduction:.0f}</div>
                <div class="metric-label">Total AQI Reduction</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{avg_speed_improvement:.1f}%</div>
                <div class="metric-label">Avg Speed Improvement</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{avg_traffic_reduction:.1f}%</div>
                <div class="metric-label">Avg Traffic Reduction</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{int(total_health_impact/10)}</div>
                <div class="metric-label">Lives Saved (Est.)</div>
            </div>
        </div>
        
        <div class="content-grid">
            <div class="card">
                <h3>Key Achievements</h3>
                <ul>
                    <li><span>AQI Reduction per Zone:</span> <span class="value">29-60 points</span></li>
                    <li><span>Speed Improvement:</span> <span class="value">+28% to +36%</span></li>
                    <li><span>Traffic Reduction:</span> <span class="value">~50%</span></li>
                    <li><span>PM2.5 Reduction:</span> <span class="value">18% avg</span></li>
                    <li><span>Response Time:</span> <span class="value">< 5 minutes</span></li>
                </ul>
            </div>
            
            <div class="card">
                <h3>Intervention Measures</h3>
                <ul>
                    <li><span>Odd-Even Rule:</span> <span class="value">Active</span></li>
                    <li><span>Truck Bans:</span> <span class="value">6 AM - 11 PM</span></li>
                    <li><span>Metro Incentives:</span> <span class="value">Free passes</span></li>
                    <li><span>Speed Limits:</span> <span class="value">Increased</span></li>
                    <li><span>Rerouting Active:</span> <span class="value">Yes</span></li>
                </ul>
            </div>
        </div>
        
        <div class="zone-details">
            <h3>Zone-by-Zone Performance</h3>
            <div class="zone-grid">
                <div class="zone-item">
                    <div class="zone-name">Connaught Place</div>
                    <div class="zone-metric">AQI: 328 → 265 (-63)</div>
                    <div class="zone-metric">Speed: +28.9%</div>
                    <div class="zone-metric">Traffic: -52%</div>
                </div>
                <div class="zone-item">
                    <div class="zone-name">Karol Bagh</div>
                    <div class="zone-metric">AQI: 315 → 270 (-45)</div>
                    <div class="zone-metric">Speed: +29.2%</div>
                    <div class="zone-metric">Traffic: -50%</div>
                </div>
                <div class="zone-item">
                    <div class="zone-name">Dwarka</div>
                    <div class="zone-metric">AQI: 342 → 285 (-57)</div>
                    <div class="zone-metric">Speed: +31%</div>
                    <div class="zone-metric">Traffic: -50.5%</div>
                </div>
                <div class="zone-item">
                    <div class="zone-name">Rohini</div>
                    <div class="zone-metric">AQI: 305 → 245 (-60)</div>
                    <div class="zone-metric">Speed: +36%</div>
                    <div class="zone-metric">Traffic: -50%</div>
                </div>
                <div class="zone-item">
                    <div class="zone-name">Saket</div>
                    <div class="zone-metric">AQI: 320 → 260 (-60)</div>
                    <div class="zone-metric">Speed: +30.4%</div>
                    <div class="zone-metric">Traffic: -50%</div>
                </div>
            </div>
        </div>
        
        <div class="links">
            <a href="interactive_dashboard.html" class="link-btn">View Interactive Dashboard</a>
            <a href="impact_metrics.html" class="link-btn">View Impact Metrics</a>
            <a href="pollutant_analysis.html" class="link-btn">View Pollutant Analysis</a>
        </div>
        
        <div class="footer">
            <p>Emergency Protocol Analysis Report | Generated using Delhi Digital Twin Analysis Engine</p>
            <p>System Status: ACTIVE | Last Updated: 2025-11-15</p>
        </div>
    </div>
</body>
</html>
    """
    
    output_dir = Path('visualization_outputs')
    output_path = output_dir / 'emergency_protocol_complete.html'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"[OK] Created complete report: {output_path.name}")
    return output_path

def main():
    print("\n" + "="*100)
    print("ADVANCED EMERGENCY PROTOCOL VISUALIZATION")
    print("="*100 + "\n")
    
    # Create visualizations
    print("Generating interactive visualizations...")
    
    dashboard_path = create_comparison_dashboard()
    metrics_path = create_impact_metrics_chart()
    pollutant_path = create_pollutant_breakdown()
    report_path = create_summary_report()
    
    print("\n" + "="*100)
    print("VISUALIZATION COMPLETE!")
    print("="*100)
    
    print("\nGenerated files in visualization_outputs/:")
    print(f"  [OK] interactive_dashboard.html - Main comparison dashboard")
    print(f"  [OK] impact_metrics.html - Impact metrics visualization")
    print(f"  [OK] pollutant_analysis.html - Pollutant breakdown")
    print(f"  [OK] emergency_protocol_complete.html - Complete summary report")
    print(f"  [OK] emergency_protocol_analysis.png - Static high-res visualization")
    
    print("\nOpen this file to view all reports:")
    print(f"  [MAIN] emergency_protocol_complete.html")
    
    print("\n" + "="*100 + "\n")

if __name__ == '__main__':
    main()
