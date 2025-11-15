#!/usr/bin/env python
"""
Complete Visualization Launcher for Delhi Corridor Simulation
Launches interactive dashboards, Plotly visualizations, and Flask API server
"""

import os
import sys
import subprocess
import webbrowser
import time
import threading
from pathlib import Path
import json

class VisualizationLauncher:
    """Orchestrate all visualization components"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.plotly_path = self.base_path / "visualization_outputs"
        self.html_dashboard = self.base_path / "visualization_dashboard.html"
        
    def print_header(self, text):
        """Print formatted header"""
        print("\n" + "="*70)
        print(f"  {text}")
        print("="*70 + "\n")
    
    def print_section(self, text):
        """Print section header"""
        print(f"\n📌 {text}")
        print("-" * 70)
    
    def print_status(self, status, message):
        """Print status message"""
        icons = {
            'success': '✓',
            'error': '✗',
            'info': '→',
            'warning': '⚠',
            'loading': '◌'
        }
        icon = icons.get(status, '•')
        print(f"{icon} {message}")
    
    def generate_plotly_visualizations(self):
        """Generate interactive Plotly charts"""
        self.print_section("GENERATING PLOTLY VISUALIZATIONS")
        
        try:
            # Check if visualization script exists
            viz_script = self.base_path / "visualize_corridor.py"
            if not viz_script.exists():
                self.print_status('error', f"Visualization script not found: {viz_script}")
                return False
            
            self.print_status('loading', "Running Plotly visualization generator...")
            
            # Run visualization script
            result = subprocess.run(
                [sys.executable, str(viz_script)],
                cwd=str(self.base_path),
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                self.print_status('success', "Plotly visualizations generated")
                # Print output
                for line in result.stdout.split('\n'):
                    if line.strip():
                        self.print_status('info', line)
                return True
            else:
                self.print_status('error', f"Visualization generation failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.print_status('error', "Visualization generation timed out")
            return False
        except Exception as e:
            self.print_status('error', f"Error: {e}")
            return False
    
    def start_flask_server(self):
        """Start Flask development server in background"""
        self.print_section("STARTING FLASK API SERVER")
        
        try:
            # Check if main app file exists
            app_file = self.base_path / "app.py"
            if not app_file.exists():
                self.print_status('warning', "app.py not found, Flask server not started")
                return None
            
            self.print_status('loading', "Starting Flask server on http://localhost:5000...")
            
            # Start Flask server in background thread
            def run_flask():
                subprocess.run(
                    [sys.executable, str(app_file)],
                    cwd=str(self.base_path)
                )
            
            flask_thread = threading.Thread(target=run_flask, daemon=True)
            flask_thread.start()
            
            # Wait for server to start
            time.sleep(3)
            
            self.print_status('success', "Flask API server started")
            self.print_status('info', "Available at: http://localhost:5000/api/corridor/")
            
            return flask_thread
            
        except Exception as e:
            self.print_status('warning', f"Could not start Flask: {e}")
            return None
    
    def open_visualizations(self):
        """Open all visualizations in browser"""
        self.print_section("OPENING VISUALIZATIONS")
        
        urls_to_open = []
        
        # Check Plotly visualizations
        if self.plotly_path.exists():
            index_file = self.plotly_path / "index.html"
            if index_file.exists():
                file_url = f"file:///{index_file.absolute()}".replace('\\', '/')
                urls_to_open.append(('Plotly Dashboard', file_url))
                self.print_status('success', f"Plotly dashboard: {file_url}")
        
        # Check HTML dashboard
        if self.html_dashboard.exists():
            file_url = f"file:///{self.html_dashboard.absolute()}".replace('\\', '/')
            urls_to_open.append(('Interactive Dashboard', file_url))
            self.print_status('success', f"Interactive dashboard: {file_url}")
        
        # Flask API
        urls_to_open.append(('Flask API', 'http://localhost:5000/api/corridor/'))
        self.print_status('info', "Flask API: http://localhost:5000/api/corridor/")
        
        # Open in browser
        self.print_status('loading', "Opening visualizations in browser...")
        for name, url in urls_to_open:
            try:
                webbrowser.open(url)
                self.print_status('success', f"Opened: {name}")
                time.sleep(1)  # Slight delay between opening
            except Exception as e:
                self.print_status('warning', f"Could not open {name}: {e}")
        
        return urls_to_open
    
    def display_help(self):
        """Display helpful information"""
        self.print_section("VISUALIZATION SYSTEM HELP")
        
        help_text = """
📊 AVAILABLE VISUALIZATIONS:

1. PLOTLY INTERACTIVE CHARTS (visualization_outputs/)
   • Overview Dashboard - Traffic flow, speed, travel time
   • Air Quality Analysis - AQI levels and PM2.5 concentration
   • Intervention Comparison - Policy impact analysis
   • Zone Heatmap - Zone-level aggregation
   • Time Series - Speed and flow relationships

2. INTERACTIVE HTML DASHBOARD (visualization_dashboard.html)
   • Real-time data from Flask API
   • Multiple tabs: Overview, Traffic, AQI, Interventions, Data
   • Export to CSV/JSON
   • Responsive design

3. FLASK REST API (http://localhost:5000/api/corridor/)
   
   Endpoints:
   ├─ GET  /api/corridor/baseline - Baseline results
   ├─ POST /api/corridor/run - Run scenario with interventions
   ├─ GET  /api/corridor/stats - Network statistics
   ├─ GET  /api/corridor/visualization/zone-summary - Zone data
   ├─ GET  /api/corridor/visualization/segment-details - Segment data
   ├─ GET  /api/corridor/visualization/comparison - Scenario comparison
   ├─ GET  /api/corridor/visualization/export-csv - Download as CSV
   └─ GET  /api/corridor/visualization/export-json - Download as JSON

📂 DATA FORMATS:

   CSV Files:
   • data/corridor_segments.csv - 30 segments
   • data/intersections.csv - 40 intersections
   • data/od_matrix.csv - 129 OD pairs
   
   Output Files:
   • outputs/baseline_results.csv
   • outputs/intervention_*.csv (1-4)

🚀 QUICK START:

   1. Run this launcher: python launch_visualizations.py
   2. Visualizations open automatically
   3. Explore different tabs and charts
   4. Export data for further analysis

📌 CUSTOMIZATION:

   Plotly Visualizations:
   • Edit: visualize_corridor.py
   • Regenerate: python visualize_corridor.py
   
   Interactive Dashboard:
   • Edit: visualization_dashboard.html
   • Customize charts and layouts
   
   Flask API:
   • Edit: backend/corridor_api.py
   • Add new endpoints as needed

💡 TIPS:

   • Use browser's Developer Tools (F12) to inspect data
   • Export data from dashboard for use in other tools
   • Modify CSV data files to test scenarios
   • Flask API is ready for frontend integration

📞 SUPPORT:

   • Check logs for errors
   • Ensure all dependencies installed: pip install -r requirements.txt
   • Verify CSV files exist in data/ directory
   • Check Flask server is running on port 5000
        """
        print(help_text)
    
    def display_summary(self):
        """Display summary of what was launched"""
        self.print_header("VISUALIZATION SYSTEM LAUNCHED SUCCESSFULLY!")
        
        print("\n🎯 WHAT'S RUNNING:\n")
        
        if self.plotly_path.exists() and (self.plotly_path / "index.html").exists():
            print("  ✓ Plotly Interactive Visualizations")
            print("    Location: visualization_outputs/")
            print("    Charts: Overview, AQI, Interventions, Zones, Time Series")
        
        if self.html_dashboard.exists():
            print("  ✓ Interactive HTML Dashboard")
            print("    Features: Multiple tabs, data export, real-time updates")
        
        print("  ✓ Flask API Server (localhost:5000)")
        print("    Endpoints: 10+ REST API endpoints")
        
        print("\n📊 DATA PREVIEW:\n")
        self._display_data_preview()
        
        print("\n🔗 QUICK LINKS:\n")
        print("  • Plotly Dashboard: visualization_outputs/index.html")
        print("  • Interactive Dashboard: visualization_dashboard.html")
        print("  • Flask API: http://localhost:5000/api/corridor/stats")
        print("  • Demo Script: python demo_corridor.py")
        
        print("\n💾 EXPORT OPTIONS:\n")
        print("  • CSV Export: Via dashboard or /api/corridor/visualization/export-csv")
        print("  • JSON Export: Via dashboard or /api/corridor/visualization/export-json")
        print("  • Python: pd.read_csv('outputs/baseline_results.csv')")
        
        print("\n" + "="*70 + "\n")
    
    def _display_data_preview(self):
        """Display preview of simulation data"""
        try:
            if (Path("outputs") / "baseline_results.csv").exists():
                import pandas as pd
                df = pd.read_csv(Path("outputs") / "baseline_results.csv")
                print(f"  • Baseline Results: {len(df)} segments")
                if 'flow_rate' in df.columns:
                    print(f"    - Total Flow: {df['flow_rate'].sum():,.0f} vph")
                    print(f"    - Avg Speed: {df['speed'].mean():.1f} km/h")
        except:
            pass
    
    def launch(self):
        """Main launch sequence"""
        self.print_header("🌍 DELHI CORRIDOR SIMULATION - VISUALIZATION SYSTEM")
        
        print("Initializing visualization system...\n")
        
        # Step 1: Generate Plotly visualizations
        plotly_success = self.generate_plotly_visualizations()
        
        # Step 2: Start Flask server
        flask_thread = self.start_flask_server()
        
        # Step 3: Open visualizations
        time.sleep(2)  # Wait for server to stabilize
        urls = self.open_visualizations()
        
        # Step 4: Display summary and help
        self.display_summary()
        self.display_help()
        
        print("\n✨ All visualization systems are ready!")
        print("→ Check your browser windows for the dashboards")
        print("→ Press Ctrl+C to stop the server\n")
        
        # Keep running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n→ Shutting down visualization system...")
            print("✓ Done!")
            sys.exit(0)

def main():
    """Entry point"""
    launcher = VisualizationLauncher()
    launcher.launch()

if __name__ == "__main__":
    main()
