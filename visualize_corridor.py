"""
Enhanced Visualization Script for Delhi Corridor Simulation
Generates interactive Plotly visualizations and opens them in browser
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
import os
from pathlib import Path
import webbrowser

# Data directories
DATA_DIR = Path("data")
OUTPUTS_DIR = Path("outputs")

class CorridorVisualizer:
    """Generate interactive visualizations for corridor simulation results"""
    
    def __init__(self):
        self.baseline_data = None
        self.interventions_data = {}
        self.zones = {}
        self.segments = {}
        self.load_data()
    
    def load_data(self):
        """Load simulation data from CSV files"""
        try:
            # Load baseline results
            if (OUTPUTS_DIR / "baseline_results.csv").exists():
                self.baseline_data = pd.read_csv(OUTPUTS_DIR / "baseline_results.csv")
                print("[OK] Loaded baseline results")
            
            # Load intervention results
            for i in range(1, 5):
                file = OUTPUTS_DIR / f"intervention_{i}_results.csv"
                if file.exists():
                    self.interventions_data[i] = pd.read_csv(file)
                    print(f"[OK] Loaded intervention {i} results")
            
            # Load corridor segments for zone mapping
            if (DATA_DIR / "corridor_segments.csv").exists():
                segments_df = pd.read_csv(DATA_DIR / "corridor_segments.csv")
                self.zones = segments_df.groupby('zone_id').size().to_dict()
                print(f"[OK] Loaded zone data: {len(self.zones)} zones")
                
        except Exception as e:
            print(f"[ERROR] Error loading data: {e}")
    
    def create_aqi_overview(self):
        """Create AQI overview dashboard"""
        if self.baseline_data is None or self.baseline_data.empty:
            print("[SKIP] No baseline data for AQI overview")
            return None
        
        data = self.baseline_data.copy()
        
        fig = go.Figure()
        
        # AQI levels by zone
        fig.add_trace(go.Bar(
            x=data['zone_id'],
            y=data['aqi'],
            name='AQI',
            marker=dict(
                color=data['aqi'],
                colorscale='RdYlGn_r',
                showscale=True,
                colorbar=dict(title="AQI Level")
            ),
            text=data['aqi'].round(0),
            textposition='auto',
        ))
        
        fig.update_layout(
            title='<b>Air Quality Index by Zone (Baseline)</b>',
            xaxis_title='Zone ID',
            yaxis_title='AQI Level',
            height=500,
            hovermode='x unified',
            template='plotly_white'
        )
        
        return fig
    
    def create_energy_analysis(self):
        """Create energy consumption analysis"""
        if self.baseline_data is None or self.baseline_data.empty:
            return None
        
        data = self.baseline_data.copy()
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Energy by Zone', 'AQI vs Energy Correlation')
        )
        
        # Energy by zone
        fig.add_trace(
            go.Bar(x=data['zone_id'], y=data['energy'], name='Energy',
                   marker_color='#667eea'),
            row=1, col=1
        )
        
        # AQI vs Energy scatter
        fig.add_trace(
            go.Scatter(x=data['energy'], y=data['aqi'],
                      mode='markers', name='Zones',
                      marker=dict(size=10, color='#764ba2')),
            row=1, col=2
        )
        
        fig.update_yaxes(title_text='Energy (MWh)', row=1, col=1)
        fig.update_yaxes(title_text='AQI', row=1, col=2)
        fig.update_xaxes(title_text='Zone ID', row=1, col=1)
        fig.update_xaxes(title_text='Energy (MWh)', row=1, col=2)
        
        fig.update_layout(
            title_text='<b>Energy and AQI Analysis</b>',
            height=500,
            showlegend=True,
            template='plotly_white'
        )
        
        return fig
    
    def create_heat_island_analysis(self):
        """Create urban heat island analysis"""
        if self.baseline_data is None or self.baseline_data.empty:
            return None
        
        data = self.baseline_data.copy()
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=data['zone_id'],
            y=data['heat_island'],
            mode='lines+markers',
            name='Heat Island Effect',
            line=dict(color='#dc3545', width=3),
            marker=dict(size=10)
        ))
        
        fig.update_layout(
            title='<b>Urban Heat Island Effect by Zone</b>',
            xaxis_title='Zone ID',
            yaxis_title='Heat Island Index',
            height=500,
            hovermode='x unified',
            template='plotly_white'
        )
        
        return fig
    
    def create_intervention_comparison(self):
        """Compare baseline vs all interventions"""
        interventions_list = ['Baseline']
        aqi_values = [self.baseline_data['aqi'].mean()] if self.baseline_data is not None else [0]
        energy_values = [self.baseline_data['energy'].mean()] if self.baseline_data is not None else [0]
        
        intervention_names = {
            1: 'Truck Ban',
            2: 'Lane Addition',
            3: 'Signal Tuning',
            4: 'Dynamic Rerouting'
        }
        
        for i, data in self.interventions_data.items():
            if not data.empty:
                interventions_list.append(intervention_names.get(i, f'Intervention {i}'))
                aqi_values.append(data['aqi'].mean())
                energy_values.append(data['energy'].mean())
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Average AQI', 'Total Energy Consumption')
        )
        
        fig.add_trace(
            go.Bar(x=interventions_list, y=aqi_values, name='Avg AQI',
                   marker_color='#dc3545'),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Bar(x=interventions_list, y=energy_values, name='Energy',
                   marker_color='#ffc107'),
            row=1, col=2
        )
        
        fig.update_yaxes(title_text='AQI', row=1, col=1)
        fig.update_yaxes(title_text='Energy (MWh)', row=1, col=2)
        
        fig.update_layout(
            title_text='<b>Intervention Impact Comparison</b>',
            height=500,
            showlegend=False,
            template='plotly_white'
        )
        
        return fig
    
    def create_zone_heatmap(self):
        """Create zone-level metrics heatmap"""
        if self.baseline_data is None or self.baseline_data.empty:
            return None
        
        data = self.baseline_data.copy().set_index('zone_id')
        
        # Normalize data for heatmap
        normalized = data.copy()
        for col in normalized.columns:
            normalized[col] = (normalized[col] - normalized[col].min()) / (normalized[col].max() - normalized[col].min())
        
        fig = go.Figure(data=go.Heatmap(
            z=normalized.values.T,
            x=normalized.index,
            y=normalized.columns,
            colorscale='Viridis',
            text=data.values.T,
            texttemplate='%{text:.1f}',
            hovertemplate='%{y}<br>Zone %{x}<br>Value: %{text:.2f}<extra></extra>'
        ))
        
        fig.update_layout(
            title='<b>Zone-Level Metrics Heatmap (Normalized)</b>',
            xaxis_title='Zone ID',
            yaxis_title='Metric',
            height=400,
            template='plotly_white'
        )
        
        return fig
    
    def create_zone_comparison(self):
        """Create zone comparison chart"""
        if self.baseline_data is None or self.baseline_data.empty:
            return None
        
        data = self.baseline_data.copy()
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('AQI and Energy by Zone', 'Heat Island Effect by Zone'),
            specs=[[{'secondary_y': True}], [{}]]
        )
        
        # Row 1: AQI and Energy
        fig.add_trace(
            go.Bar(x=data['zone_id'], y=data['aqi'], name='AQI', marker_color='#dc3545'),
            row=1, col=1, secondary_y=False
        )
        
        fig.add_trace(
            go.Scatter(x=data['zone_id'], y=data['energy'], name='Energy',
                      line=dict(color='#ffc107', width=2), mode='lines+markers'),
            row=1, col=1, secondary_y=True
        )
        
        # Row 2: Heat Island
        fig.add_trace(
            go.Bar(x=data['zone_id'], y=data['heat_island'], name='Heat Island',
                   marker_color='#ff6b6b'),
            row=2, col=1
        )
        
        fig.update_yaxes(title_text='AQI', row=1, col=1, secondary_y=False)
        fig.update_yaxes(title_text='Energy (MWh)', row=1, col=1, secondary_y=True)
        fig.update_yaxes(title_text='Heat Island Index', row=2, col=1)
        fig.update_xaxes(title_text='Zone ID', row=2, col=1)
        
        fig.update_layout(
            title_text='<b>Comprehensive Zone Analysis</b>',
            height=700,
            showlegend=True,
            template='plotly_white',
            hovermode='x unified'
        )
        
        return fig
    
    def generate_all_visualizations(self):
        """Generate and save all visualizations"""
        print('\n' + '='*60)
        print('GENERATING INTERACTIVE VISUALIZATIONS')
        print('='*60 + '\n')
        
        viz_dir = Path('visualization_outputs')
        viz_dir.mkdir(exist_ok=True)
        
        visualizations = [
            ('aqi_overview', self.create_aqi_overview, '[AQI Overview]'),
            ('energy_analysis', self.create_energy_analysis, '[Energy Analysis]'),
            ('heat_island', self.create_heat_island_analysis, '[Heat Island Effect]'),
            ('intervention_comparison', self.create_intervention_comparison, '[Intervention Comparison]'),
            ('zone_heatmap', self.create_zone_heatmap, '[Zone Heatmap]'),
            ('zone_comparison', self.create_zone_comparison, '[Zone Comprehensive]'),
        ]
        
        for filename, func, title in visualizations:
            try:
                fig = func()
                if fig is not None:
                    output_path = viz_dir / f'{filename}.html'
                    fig.write_html(str(output_path))
                    print(f'[OK] {title}: {output_path.name}')
                else:
                    print(f'[SKIP] {title}: No data')
            except Exception as e:
                print(f'[ERROR] {title}: {str(e)[:50]}')
        
        # Create master dashboard
        self.create_master_dashboard(viz_dir)
    
    def create_master_dashboard(self, viz_dir):
        """Create HTML master dashboard linking all visualizations"""
        html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Delhi Corridor Visualization Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
            padding: 40px;
        }
        h1 {
            color: #667eea;
            text-align: center;
            margin-bottom: 10px;
            font-size: 2.5em;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 40px;
            font-size: 1.1em;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            color: white;
            text-decoration: none;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
        }
        .card h2 {
            font-size: 1.5em;
            margin-bottom: 10px;
        }
        .card p {
            opacity: 0.9;
            font-size: 0.95em;
        }
        .info {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            margin-top: 30px;
            color: #333;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        .stat {
            background: white;
            padding: 15px;
            border-radius: 6px;
            border: 1px solid #e9ecef;
        }
        .stat-label {
            color: #667eea;
            font-weight: 600;
            margin-bottom: 5px;
        }
        .stat-value {
            font-size: 1.4em;
            color: #333;
            font-weight: 700;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Delhi Corridor Digital Twin</h1>
        <p class="subtitle">Interactive Traffic Simulation Visualizations</p>
        
        <div class="grid">
            <a href="aqi_overview.html" class="card">
                <h2>AQI</h2>
                <h2>Air Quality Overview</h2>
                <p>Air Quality Index levels across zones</p>
            </a>
            
            <a href="energy_analysis.html" class="card">
                <h2>Energy</h2>
                <h2>Energy Analysis</h2>
                <p>Energy consumption patterns</p>
            </a>
            
            <a href="heat_island.html" class="card">
                <h2>Heat</h2>
                <h2>Heat Island Effect</h2>
                <p>Urban heat island distribution</p>
            </a>
            
            <a href="intervention_comparison.html" class="card">
                <h2>Compare</h2>
                <h2>Interventions</h2>
                <p>Policy impact analysis</p>
            </a>
            
            <a href="zone_heatmap.html" class="card">
                <h2>Heatmap</h2>
                <h2>Zone Metrics</h2>
                <p>Zone-level aggregation</p>
            </a>
            
            <a href="zone_comparison.html" class="card">
                <h2>Zones</h2>
                <h2>Zone Analysis</h2>
                <p>Comprehensive zone metrics</p>
            </a>
        </div>
        
        <div class="info">
            <h3>Simulation Summary</h3>
            <p>Interactive visualizations of corridor-level traffic and environmental metrics for Delhi.</p>
            <div class="stats">
                <div class="stat">
                    <div class="stat-label">Total Zones</div>
                    <div class="stat-value">8</div>
                </div>
                <div class="stat">
                    <div class="stat-label">Segments</div>
                    <div class="stat-value">30</div>
                </div>
                <div class="stat">
                    <div class="stat-label">Intersections</div>
                    <div class="stat-value">40</div>
                </div>
                <div class="stat">
                    <div class="stat-label">Scenarios</div>
                    <div class="stat-value">5</div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
        
        dashboard_path = viz_dir / 'index.html'
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f'[OK] Master dashboard: index.html')
        
        return dashboard_path

def main():
    """Main execution"""
    visualizer = CorridorVisualizer()
    visualizer.generate_all_visualizations()
    
    print('\n' + '='*60)
    print('VISUALIZATION GENERATION COMPLETE!')
    print('='*60)
    print('\nGenerated files in: visualization_outputs/')
    print('\nTo view visualizations:')
    print('  1. Open visualization_outputs/index.html in your browser')
    print('  2. Or navigate to individual visualization files')
    
    # Try to open in browser
    master_dashboard = Path('visualization_outputs/index.html')
    if master_dashboard.exists():
        print(f'\n[Opening] {master_dashboard.absolute()}')
        try:
            webbrowser.open(f'file:///{master_dashboard.absolute()}')
        except Exception as e:
            print(f'[INFO] Could not auto-open: {e}')

if __name__ == '__main__':
    main()

    
    def create_overview_dashboard(self):
        """Create overview dashboard with key metrics"""
        if self.baseline_data is None or self.baseline_data.empty:
            print("✗ No baseline data available")
            return
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=("Traffic Flow Distribution", "Average Speed by Segment",
                           "Travel Time Distribution", "Congestion Index"),
            specs=[[{'type': 'bar'}, {'type': 'bar'}],
                   [{'type': 'histogram'}, {'type': 'scatter'}]]
        )
        
        data = self.baseline_data
        
        # Traffic flow
        fig.add_trace(
            go.Bar(x=data['segment_id'], y=data['flow_rate'], 
                   name='Flow Rate', marker_color='#667eea'),
            row=1, col=1
        )
        
        # Speed
        fig.add_trace(
            go.Bar(x=data['segment_id'], y=data['speed'], 
                   name='Speed', marker_color='#28a745'),
            row=1, col=2
        )
        
        # Travel time distribution
        fig.add_trace(
            go.Histogram(x=data['travel_time'], nbinsx=20, 
                        name='Travel Time', marker_color='#ffc107'),
            row=2, col=1
        )
        
        # Congestion index
        fig.add_trace(
            go.Scatter(x=data['segment_id'], y=data['speed'], 
                      mode='lines+markers', name='Speed Curve', 
                      line=dict(color='#dc3545', width=2)),
            row=2, col=2
        )
        
        fig.update_yaxes(title_text="Flow (vph)", row=1, col=1)
        fig.update_yaxes(title_text="Speed (km/h)", row=1, col=2)
        fig.update_yaxes(title_text="Frequency", row=2, col=1)
        fig.update_yaxes(title_text="Speed (km/h)", row=2, col=2)
        
        fig.update_xaxes(title_text="Segment", row=2, col=1)
        fig.update_xaxes(title_text="Segment", row=2, col=2)
        
        fig.update_layout(
            title_text="<b>Delhi Corridor: Baseline Traffic Overview</b>",
            height=800,
            showlegend=True,
            hovermode='x unified'
        )
        
        return fig
    
    def create_aqi_visualization(self):
        """Create AQI and emissions visualization"""
        if self.baseline_data is None or self.baseline_data.empty:
            return None
        
        data = self.baseline_data
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=("AQI by Segment", "PM2.5 Concentration"),
        )
        
        # AQI levels with color coding
        colors = ['green' if aqi < 100 else 'yellow' if aqi < 200 else 'orange' if aqi < 300 else 'red' 
                 for aqi in data.get('aqi', [])]
        
        fig.add_trace(
            go.Bar(x=data['segment_id'], y=data.get('aqi', []), 
                   name='AQI', marker_color=colors),
            row=1, col=1
        )
        
        # PM2.5
        fig.add_trace(
            go.Scatter(x=data['segment_id'], y=data.get('pm25', []), 
                      mode='lines+markers', name='PM2.5', 
                      line=dict(color='#dc3545', width=2),
                      marker=dict(size=8)),
            row=1, col=2
        )
        
        fig.update_yaxes(title_text="AQI", row=1, col=1)
        fig.update_yaxes(title_text="PM2.5 (µg/m³)", row=1, col=2)
        fig.update_xaxes(title_text="Segment", row=1, col=1)
        fig.update_xaxes(title_text="Segment", row=1, col=2)
        
        fig.update_layout(
            title_text="<b>Air Quality Analysis</b>",
            height=500,
            hovermode='x unified'
        )
        
        return fig
    
    def create_intervention_comparison(self):
        """Compare baseline vs all interventions"""
        if not self.baseline_data or not self.baseline_data.empty:
            baseline_avg_speed = self.baseline_data['speed'].mean() if 'speed' in self.baseline_data else 0
            baseline_avg_aqi = self.baseline_data.get('aqi', [0]).mean() if 'aqi' in self.baseline_data.columns else 0
        else:
            baseline_avg_speed = 0
            baseline_avg_aqi = 0
        
        interventions_list = ["Baseline"]
        speeds = [baseline_avg_speed]
        aqis = [baseline_avg_aqi]
        
        intervention_names = {
            1: "Truck Ban",
            2: "Lane Addition",
            3: "Signal Tuning",
            4: "Dynamic Rerouting"
        }
        
        for i, data in self.interventions_data.items():
            if not data.empty:
                interventions_list.append(intervention_names.get(i, f"Intervention {i}"))
                speeds.append(data['speed'].mean() if 'speed' in data else 0)
                aqis.append(data.get('aqi', [0]).mean() if 'aqi' in data.columns else 0)
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=("Average Speed Improvement", "AQI Reduction"),
        )
        
        fig.add_trace(
            go.Bar(x=interventions_list, y=speeds, name='Avg Speed', 
                   marker_color='#28a745'),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Bar(x=interventions_list, y=aqis, name='Avg AQI', 
                   marker_color='#dc3545'),
            row=1, col=2
        )
        
        fig.update_yaxes(title_text="Speed (km/h)", row=1, col=1)
        fig.update_yaxes(title_text="AQI", row=1, col=2)
        
        fig.update_layout(
            title_text="<b>Intervention Impact Analysis</b>",
            height=500,
            showlegend=True,
            hovermode='x'
        )
        
        return fig
    
    def create_zone_heatmap(self):
        """Create zone-level aggregation heatmap"""
        if self.baseline_data is None or self.baseline_data.empty:
            return None
        
        data = self.baseline_data
        
        if 'zone_id' not in data.columns:
            return None
        
        zone_summary = data.groupby('zone_id').agg({
            'flow_rate': 'sum',
            'speed': 'mean',
            'travel_time': 'mean',
        }).reset_index()
        
        if 'aqi' in data.columns:
            aqi_by_zone = data.groupby('zone_id')['aqi'].mean()
            zone_summary['aqi'] = zone_summary['zone_id'].map(aqi_by_zone)
        
        fig = go.Figure(data=go.Heatmap(
            z=zone_summary[['flow_rate', 'speed']].values.T,
            x=zone_summary['zone_id'],
            y=['Flow Rate (vph)', 'Speed (km/h)'],
            colorscale='Viridis'
        ))
        
        fig.update_layout(
            title_text="<b>Zone-Level Traffic Summary</b>",
            height=400,
            xaxis_title="Zone ID",
            yaxis_title="Metric"
        )
        
        return fig
    
    def create_time_series(self):
        """Create time series analysis (if time data available)"""
        if self.baseline_data is None or self.baseline_data.empty:
            return None
        
        data = self.baseline_data.head(30)  # Show first 30 segments as proxy for time
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=data['segment_id'],
            y=data['speed'],
            mode='lines',
            name='Speed',
            line=dict(color='#667eea', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=data['segment_id'],
            y=data['flow_rate'],
            mode='lines',
            name='Flow',
            yaxis='y2',
            line=dict(color='#28a745', width=2)
        ))
        
        fig.update_layout(
            title_text="<b>Speed and Flow Relationship</b>",
            xaxis=dict(title="Segment"),
            yaxis=dict(title="Speed (km/h)"),
            yaxis2=dict(title="Flow (vph)", overlaying='y', side='right'),
            height=500,
            hovermode='x unified'
        )
        
        return fig
    
    def generate_all_visualizations(self):
        """Generate and save all visualizations"""
        print("\n" + "="*60)
        print("GENERATING INTERACTIVE VISUALIZATIONS")
        print("="*60 + "\n")
        
        viz_dir = Path("visualization_outputs")
        viz_dir.mkdir(exist_ok=True)
        
        visualizations = [
            ("overview_dashboard", self.create_overview_dashboard, "📊 Overview Dashboard"),
            ("aqi_analysis", self.create_aqi_visualization, "💨 Air Quality Analysis"),
            ("intervention_comparison", self.create_intervention_comparison, "🎯 Intervention Comparison"),
            ("zone_heatmap", self.create_zone_heatmap, "🗺️ Zone Heatmap"),
            ("time_series", self.create_time_series, "📈 Time Series Analysis"),
        ]
        
        for filename, func, title in visualizations:
            try:
                fig = func()
                if fig is not None:
                    output_path = viz_dir / f"{filename}.html"
                    fig.write_html(str(output_path))
                    print(f"✓ {title}: {output_path}")
                else:
                    print(f"⊘ {title}: Skipped (no data)")
            except Exception as e:
                print(f"✗ {title}: {e}")
        
        # Create master dashboard
        self.create_master_dashboard(viz_dir)
    
    def create_master_dashboard(self, viz_dir):
        """Create HTML master dashboard linking all visualizations"""
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Delhi Corridor Visualization Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
            padding: 40px;
        }
        h1 {
            color: #667eea;
            text-align: center;
            margin-bottom: 10px;
            font-size: 2.5em;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 40px;
            font-size: 1.1em;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            color: white;
            text-decoration: none;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
        }
        .card h2 {
            font-size: 1.5em;
            margin-bottom: 10px;
        }
        .card p {
            opacity: 0.9;
            font-size: 0.95em;
        }
        .info {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            margin-top: 30px;
            color: #333;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        .stat {
            background: white;
            padding: 15px;
            border-radius: 6px;
            border: 1px solid #e9ecef;
        }
        .stat-label {
            color: #667eea;
            font-weight: 600;
            margin-bottom: 5px;
        }
        .stat-value {
            font-size: 1.4em;
            color: #333;
            font-weight: 700;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌍 Delhi Corridor Digital Twin</h1>
        <p class="subtitle">Interactive Traffic Simulation & Air Quality Visualization</p>
        
        <div class="grid">
            <a href="overview_dashboard.html" class="card">
                <h2>📊</h2>
                <h2>Overview Dashboard</h2>
                <p>Traffic flow, speed, and travel time analysis</p>
            </a>
            
            <a href="aqi_analysis.html" class="card">
                <h2>💨</h2>
                <h2>Air Quality</h2>
                <p>AQI levels and PM2.5 concentration</p>
            </a>
            
            <a href="intervention_comparison.html" class="card">
                <h2>🎯</h2>
                <h2>Interventions</h2>
                <p>Compare policy impacts</p>
            </a>
            
            <a href="zone_heatmap.html" class="card">
                <h2>🗺️</h2>
                <h2>Zone Analysis</h2>
                <p>Zone-level aggregation heatmap</p>
            </a>
            
            <a href="time_series.html" class="card">
                <h2>📈</h2>
                <h2>Time Series</h2>
                <p>Speed and flow relationships</p>
            </a>
        </div>
        
        <div class="info">
            <h3>📍 Simulation Summary</h3>
            <p>This interactive dashboard visualizes the corridor-level traffic and air quality simulation for Delhi.</p>
            <div class="stats">
                <div class="stat">
                    <div class="stat-label">Total Segments</div>
                    <div class="stat-value">30</div>
                </div>
                <div class="stat">
                    <div class="stat-label">Intersections</div>
                    <div class="stat-value">40</div>
                </div>
                <div class="stat">
                    <div class="stat-label">OD Pairs</div>
                    <div class="stat-value">129</div>
                </div>
                <div class="stat">
                    <div class="stat-label">Zones</div>
                    <div class="stat-value">8</div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
        """
        
        dashboard_path = viz_dir / "index.html"
        with open(dashboard_path, 'w') as f:
            f.write(html_content)
        print(f"\n✓ Master dashboard created: {dashboard_path}")
        
        return dashboard_path

def main():
    """Main execution"""
    visualizer = CorridorVisualizer()
    visualizer.generate_all_visualizations()
    
    print("\n" + "="*60)
    print("VISUALIZATION GENERATION COMPLETE!")
    print("="*60)
    print("\nGenerated files in: visualization_outputs/")
    print("\nTo view visualizations:")
    print("  1. Open visualization_outputs/index.html in your browser")
    print("  2. Or navigate to individual visualization files")
    
    # Try to open in browser
    master_dashboard = Path("visualization_outputs/index.html")
    if master_dashboard.exists():
        print(f"\n→ Opening dashboard: {master_dashboard.absolute()}")
        try:
            webbrowser.open(f'file://{master_dashboard.absolute()}')
        except Exception as e:
            print(f"Could not auto-open browser: {e}")

if __name__ == "__main__":
    main()
