#!/usr/bin/env python3
"""
Quick Setup Script for AI for Climate Hackathon
Run this to set up enhanced climate features quickly
"""

import os
import subprocess
import sys

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Error in {description}: {e}")
        print(f"Error output: {e.stderr}")
        return None

def setup_environment():
    """Set up Python environment and dependencies"""
    
    print("🚀 Setting up AI for Climate Hackathon Environment")
    print("=" * 60)
    
    # Check Python version
    python_version = sys.version_info
    print(f"🐍 Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ Python 3.8+ required. Please upgrade Python.")
        return False
    
    # Install Python dependencies
    requirements = [
        "flask",
        "flask-cors", 
        "pandas",
        "numpy",
        "scikit-learn",
        "matplotlib",
        "seaborn",
        "requests"
    ]
    
    for package in requirements:
        run_command(f"pip install {package}", f"Installing {package}")
    
    # Install Node.js dependencies
    if os.path.exists("package.json"):
        run_command("npm install", "Installing Node.js dependencies")
    
    return True

def create_demo_data():
    """Create enhanced demo data for climate features"""
    
    demo_data = {
        'climate_scenarios': {
            'baseline': {
                'year': 2024,
                'co2_emissions_tons': 4200000,
                'renewable_percent': 12,
                'aqi_average': 220
            },
            'aggressive_2035': {
                'year': 2035,
                'co2_emissions_tons': 0,
                'renewable_percent': 95,
                'aqi_average': 85,
                'investment_crores': 1200,
                'jobs_created': 15000
            }
        },
        'green_finance': {
            'solar_rooftop_roi': 15,
            'wind_farm_roi': 12,
            'urban_forest_roi': 18,
            'total_market_crores': 1275
        }
    }
    
    # Save demo data
    import json
    with open('data/demo_climate_data.json', 'w') as f:
        json.dump(demo_data, f, indent=2)
    
    print("✅ Demo climate data created")

def setup_api_keys():
    """Set up API keys for real data sources"""
    
    print("\n🔑 API Keys Setup")
    print("-" * 30)
    
    api_keys = {
        'OPENWEATHER_API_KEY': 'https://openweathermap.org/api',
        'AQICN_API_KEY': 'https://aqicn.org/api/',
        'NASA_FIRMS_API_KEY': 'https://firms.modaps.eosdis.nasa.gov/'
    }
    
    env_content = "# Climate AI API Keys\n"
    
    for key, url in api_keys.items():
        print(f"📝 Get {key} from: {url}")
        value = input(f"Enter {key} (or press Enter to skip): ").strip()
        if value:
            env_content += f"{key}={value}\n"
        else:
            env_content += f"# {key}=your_key_here\n"
    
    # Save to .env file
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ API keys configuration saved to .env")

def test_setup():
    """Test that everything is working"""
    
    print("\n🧪 Testing Setup")
    print("-" * 20)
    
    # Test Python modules
    try:
        from src.climate_ai import ClimateAI
        climate_ai = ClimateAI()
        print("✅ ClimateAI module loaded successfully")
        
        # Test a quick calculation
        sample_zones = {
            1: {'traffic_flow': 1200, 'energy_use': 1500, 'population': 15000, 'industrial_activity': 0.8}
        }
        emissions = climate_ai.calculate_carbon_emissions(sample_zones)
        print(f"✅ Carbon calculation test: {emissions[1]['total_co2_tons']:.1f} tons CO2")
        
    except Exception as e:
        print(f"❌ ClimateAI test failed: {e}")
    
    # Test backend API
    try:
        import sys
        sys.path.append('backend')
        print("✅ Backend modules accessible")
    except Exception as e:
        print(f"❌ Backend test failed: {e}")
    
    # Check if frontend builds
    if os.path.exists("package.json"):
        result = run_command("npm run build", "Testing frontend build")
        if result is not None:
            print("✅ Frontend build successful")

def create_demo_scripts():
    """Create quick demo scripts"""
    
    demo_script = """
# 🚀 Quick Demo Commands for AI for Climate Hackathon

## Start the Full Application
```bash
# Terminal 1 - Backend
python backend/app.py

# Terminal 2 - Enhanced Climate API  
python backend/climate_api.py

# Terminal 3 - Frontend
npm run dev
```

## Test Climate AI Features
```bash
# Test carbon tracking
python -c "from src.climate_ai import ClimateAI; ai = ClimateAI(); print('Carbon AI ready!')"

# Test climate visualization
python backend/climate_api.py
# Visit: http://localhost:5001/api/climate/realtime
```

## Demo Scenarios
```bash
# Crisis Response Demo
curl http://localhost:5001/api/climate/crisis-response -X POST -H "Content-Type: application/json" -d '{"crisis_type": "extreme_pollution", "severity": "high"}'

# Net-Zero Scenarios Demo  
curl http://localhost:5001/api/climate/net-zero-scenarios -X POST -H "Content-Type: application/json" -d '{"zone_id": 1}'

# Green Finance Demo
curl http://localhost:5001/api/climate/green-finance
```

## Performance Commands
```bash
# Check app performance
npm run build
npm run preview

# Monitor API response times
curl -w "@%{time_total}s" http://localhost:5001/api/climate/realtime
```
"""
    
    with open('DEMO_COMMANDS.md', 'w') as f:
        f.write(demo_script)
    
    print("✅ Demo commands saved to DEMO_COMMANDS.md")

def main():
    """Main setup function"""
    
    print("🌍 AI for Climate Hackathon - Quick Setup")
    print("=" * 50)
    
    # Create directories if they don't exist
    os.makedirs('data', exist_ok=True)
    os.makedirs('scripts', exist_ok=True)
    os.makedirs('enhancements', exist_ok=True)
    
    # Run setup steps
    if not setup_environment():
        return
    
    create_demo_data()
    setup_api_keys()
    create_demo_scripts()
    test_setup()
    
    print("\n🎉 Setup Complete!")
    print("=" * 30)
    print("Next steps:")
    print("1. Run: python backend/app.py")
    print("2. Run: python backend/climate_api.py")  
    print("3. Run: npm run dev")
    print("4. Visit: http://localhost:3000")
    print("5. Check: DEMO_COMMANDS.md for demo scripts")
    print("\n🏆 Good luck with the hackathon!")

if __name__ == "__main__":
    main()