"""
Enhanced Climate API for AI for Climate Hackathon
Real-time climate data integration and advanced analytics
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.climate_ai import ClimateAI

app = Flask(__name__)
CORS(app)

# Initialize Climate AI
climate_ai = ClimateAI()

# Mock real-time data sources (in production, these would be live APIs)
class ClimateDataSources:
    """Simulate real-time climate data sources"""
    
    def __init__(self):
        self.api_keys = {
            'openweather': 'your_openweather_api_key',
            'aqicn': 'your_aqicn_api_key',
            'carbon_api': 'your_carbon_api_key'
        }
    
    def get_weather_data(self, city="Delhi"):
        """Get real-time weather data (simulated)"""
        # In production: requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.api_keys['openweather']}")
        return {
            'temperature': 38.5 + np.random.normal(0, 2),
            'humidity': 65 + np.random.normal(0, 10),
            'wind_speed': 8 + np.random.normal(0, 3),
            'wind_direction': 315,  # Northwest (brings stubble smoke)
            'pressure': 1013 + np.random.normal(0, 5),
            'uv_index': 8.5,
            'visibility': 3.2  # Reduced due to pollution
        }
    
    def get_satellite_fire_data(self):
        """Get satellite data for stubble burning (simulated NASA FIRMS)"""
        # In production: NASA FIRMS API or ISRO satellite data
        return {
            'active_fires_punjab': np.random.poisson(2800),  # Peak season
            'active_fires_haryana': np.random.poisson(1200),
            'fire_radiative_power': np.random.exponential(50),
            'smoke_direction': 'southeast',  # Towards Delhi
            'estimated_smoke_arrival_hours': 6
        }
    
    def get_carbon_pricing(self):
        """Get current carbon pricing data"""
        return {
            'carbon_credit_price_per_ton': 2000 + np.random.normal(0, 200),  # INR
            'eu_ets_price': 85 + np.random.normal(0, 5),  # EUR per ton
            'voluntary_carbon_price': 1800 + np.random.normal(0, 150)  # INR
        }
    
    def get_renewable_energy_prices(self):
        """Get current renewable energy pricing"""
        return {
            'solar_pv_cost_per_mw': 4.2,  # Crores INR per MW
            'wind_turbine_cost_per_mw': 6.1,  # Crores INR per MW
            'battery_storage_cost_per_mwh': 2.8,  # Crores INR per MWh
            'grid_electricity_price': 6.5  # INR per kWh
        }

# Initialize data sources
data_sources = ClimateDataSources()

@app.route('/api/climate/realtime', methods=['GET'])
def get_realtime_climate_data():
    """Get comprehensive real-time climate data"""
    
    # Get live weather data
    weather = data_sources.get_weather_data()
    
    # Get satellite fire data
    fires = data_sources.get_satellite_fire_data()
    
    # Load zone data
    zones_df = pd.read_csv('data/city_zones.csv')
    zones_dict = {}
    for _, zone in zones_df.iterrows():
        zones_dict[int(zone['zone_id'])] = zone.to_dict()
    
    # Calculate carbon emissions
    carbon_emissions = climate_ai.calculate_carbon_emissions(zones_dict)
    
    # Predict climate risks
    climate_risks = climate_ai.predict_climate_risks(weather)
    
    # Calculate renewable energy potential
    renewable_recs = climate_ai.optimize_renewable_energy(zones_dict)
    
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'weather': weather,
        'satellite_fires': fires,
        'carbon_emissions': carbon_emissions,
        'climate_risks': climate_risks,
        'renewable_energy': renewable_recs,
        'zones': zones_dict
    })

@app.route('/api/climate/carbon-tracking', methods=['GET'])
def get_carbon_tracking():
    """Get detailed carbon emission tracking"""
    
    # Load zone data
    zones_df = pd.read_csv('data/city_zones.csv')
    zones_dict = {}
    for _, zone in zones_df.iterrows():
        zones_dict[int(zone['zone_id'])] = zone.to_dict()
    
    # Calculate emissions
    emissions = climate_ai.calculate_carbon_emissions(zones_dict)
    
    # Calculate total city emissions
    total_emissions = sum(zone['total_co2_tons'] for zone in emissions.values())
    
    # Per capita emissions
    total_population = sum(zone['population'] for zone in zones_dict.values())
    per_capita_city = total_emissions / (total_population / 1000)  # Per 1000 people
    
    # Breakdown by source
    total_traffic = sum(zone['traffic_co2'] for zone in emissions.values())
    total_buildings = sum(zone['building_co2'] for zone in emissions.values())
    total_industry = sum(zone['industrial_co2'] for zone in emissions.values())
    
    # Carbon pricing
    pricing = data_sources.get_carbon_pricing()
    
    # Economic impact of emissions
    economic_impact = {
        'carbon_tax_potential': total_emissions * pricing['carbon_credit_price_per_ton'],
        'health_cost_annual': total_emissions * 150000,  # ₹1.5 lakh health cost per ton CO2
        'climate_damage_cost': total_emissions * 200000  # ₹2 lakh climate damage per ton CO2
    }
    
    return jsonify({
        'total_emissions_tons': total_emissions,
        'per_capita_emissions': per_capita_city,
        'emissions_breakdown': {
            'traffic_percent': (total_traffic / total_emissions) * 100,
            'buildings_percent': (total_buildings / total_emissions) * 100,
            'industry_percent': (total_industry / total_emissions) * 100
        },
        'zone_emissions': emissions,
        'carbon_pricing': pricing,
        'economic_impact': economic_impact,
        'comparison': {
            'delhi_target_2030': 50,  # Target reduction %
            'paris_agreement_target': 45,  # Global target
            'current_trajectory': 'increasing'
        }
    })

@app.route('/api/climate/net-zero-scenarios', methods=['POST'])
def generate_net_zero_scenarios():
    """Generate net-zero pathways for different scenarios"""
    
    data = request.json
    zone_id = data.get('zone_id', 1)
    
    # Get current emissions
    zones_df = pd.read_csv('data/city_zones.csv')
    zones_dict = {}
    for _, zone in zones_df.iterrows():
        zones_dict[int(zone['zone_id'])] = zone.to_dict()
    
    emissions = climate_ai.calculate_carbon_emissions(zones_dict)
    current_emissions = emissions[zone_id]['total_co2_tons']
    
    # Generate pathways
    pathways = climate_ai.predict_net_zero_pathway(zone_id, current_emissions)
    
    # Add financial analysis
    pricing = data_sources.get_carbon_pricing()
    renewable_costs = data_sources.get_renewable_energy_prices()
    
    for pathway_name, pathway in pathways.items():
        # Calculate carbon credits earned
        pathway['carbon_credits_earned_annually'] = (
            current_emissions * pathway['emission_reduction_percent'] / 100
        ) * pricing['carbon_credit_price_per_ton']
        
        # Calculate renewable energy investment breakdown
        pathway['investment_breakdown'] = {
            'solar_investment': pathway['investment_required_crores'] * 0.4,
            'wind_investment': pathway['investment_required_crores'] * 0.3,
            'efficiency_investment': pathway['investment_required_crores'] * 0.2,
            'storage_investment': pathway['investment_required_crores'] * 0.1
        }
        
        # Calculate job creation
        pathway['jobs_created'] = int(pathway['investment_required_crores'] * 15)  # 15 jobs per crore
        
        # Health benefits
        pathway['health_benefits_annual'] = (
            current_emissions * pathway['emission_reduction_percent'] / 100
        ) * 150000  # INR per ton CO2 health benefit
    
    return jsonify({
        'zone_id': zone_id,
        'current_emissions': current_emissions,
        'pathways': pathways,
        'recommended_pathway': 'moderate',  # AI recommendation
        'urgency_score': 85,  # Out of 100
        'feasibility_analysis': {
            'technical_feasibility': 90,
            'economic_feasibility': 75,
            'social_acceptance': 70,
            'policy_support_needed': 85
        }
    })

@app.route('/api/climate/green-finance', methods=['GET'])
def get_green_finance_opportunities():
    """Get green finance and investment opportunities"""
    
    # Load zone data
    zones_df = pd.read_csv('data/city_zones.csv')
    renewable_costs = data_sources.get_renewable_energy_prices()
    
    opportunities = []
    
    for _, zone in zones_df.iterrows():
        zone_id = int(zone['zone_id'])
        
        # Solar rooftop potential
        solar_roi = climate_ai.calculate_green_infrastructure_roi('urban_forest', zone_id)
        
        opportunities.append({
            'zone_id': zone_id,
            'zone_name': f'Zone {zone_id}',
            'investment_opportunities': [
                {
                    'type': 'Solar Rooftop Program',
                    'investment_required': renewable_costs['solar_pv_cost_per_mw'] * 10,  # 10 MW program
                    'annual_returns': 15,  # % returns
                    'carbon_credits_tons': 85,  # Annual CO2 reduction
                    'payback_years': 6.5,
                    'risk_rating': 'Low'
                },
                {
                    'type': 'Urban Forest Development',
                    'investment_required': solar_roi.get('investment_crores', 0.5),
                    'annual_returns': solar_roi.get('roi_percentage', 12),
                    'carbon_credits_tons': solar_roi.get('co2_sequestration', 22),
                    'payback_years': solar_roi.get('payback_years', 8),
                    'risk_rating': 'Medium'
                },
                {
                    'type': 'Green Building Retrofit',
                    'investment_required': 2.5,  # Crores
                    'annual_returns': 18,
                    'carbon_credits_tons': 45,
                    'payback_years': 5.5,
                    'risk_rating': 'Low'
                }
            ],
            'total_green_investment_potential': 25.5,  # Crores
            'estimated_job_creation': 382,
            'expected_carbon_reduction_annually': 152  # Tons
        })
    
    return jsonify({
        'opportunities': opportunities,
        'market_overview': {
            'total_market_size_crores': 1275,
            'government_incentives_available': True,
            'carbon_credit_market_active': True,
            'international_funding_available': True,
            'estimated_roi_range': '12-18%'
        },
        'funding_sources': [
            {'name': 'Green Climate Fund', 'max_funding_crores': 100},
            {'name': 'SIDBI Green Finance', 'max_funding_crores': 50},
            {'name': 'World Bank Climate Finance', 'max_funding_crores': 200},
            {'name': 'Private ESG Funds', 'max_funding_crores': 300}
        ]
    })

@app.route('/api/climate/crisis-response', methods=['POST'])
def generate_crisis_response():
    """Generate AI-powered climate crisis response"""
    
    data = request.json
    crisis_type = data.get('crisis_type', 'extreme_pollution')
    severity = data.get('severity', 'high')
    
    # Get current conditions
    weather = data_sources.get_weather_data()
    fires = data_sources.get_satellite_fire_data()
    
    # Climate risk assessment
    risks = climate_ai.predict_climate_risks(weather)
    
    # Generate crisis-specific response
    if crisis_type == 'extreme_pollution':
        response = {
            'crisis_type': 'Air Quality Emergency',
            'severity_level': 'CRITICAL' if risks['air_quality_risk'] > 80 else 'HIGH',
            'immediate_actions': [
                '🚛 Emergency truck ban on all major roads (next 6 hours)',
                '🏫 Close all schools and outdoor activities',
                '🏗️ Halt all construction and demolition work',
                '🚇 Make public transport free for 24 hours',
                '💧 Deploy water sprinklers on 100 key roads',
                '📢 Issue health advisory to 2 crore residents'
            ],
            'ai_optimized_interventions': [
                {
                    'intervention': 'Dynamic Traffic Routing',
                    'description': 'AI reroutes 70% traffic to less polluted zones',
                    'expected_impact': '35% AQI reduction in hotspots',
                    'implementation_time': '30 minutes'
                },
                {
                    'intervention': 'Smart Grid Load Balancing',
                    'description': 'Shift industrial load to renewable energy',
                    'expected_impact': '15% emission reduction',
                    'implementation_time': '2 hours'
                },
                {
                    'intervention': 'Precision Weather Modification',
                    'description': 'Cloud seeding in upwind areas',
                    'expected_impact': '20% particulate washout',
                    'implementation_time': '4 hours'
                }
            ],
            'predicted_outcomes': {
                'aqi_improvement': '120 points reduction in 8 hours',
                'lives_protected': 45000,
                'economic_cost': '₹12 crores for 24-hour intervention',
                'health_cost_avoided': '₹45 crores'
            },
            'monitoring_metrics': [
                'Real-time AQI from 50 sensors',
                'Traffic density via satellite',
                'Hospital admissions tracking',
                'Satellite pollution imaging'
            ]
        }
    
    elif crisis_type == 'extreme_heat':
        response = {
            'crisis_type': 'Heat Wave Emergency',
            'severity_level': 'EXTREME' if weather['temperature'] > 45 else 'HIGH',
            'immediate_actions': [
                '❄️ Open 500 cooling centers across the city',
                '🚰 Deploy mobile water tankers',
                '⚡ Ensure power backup for hospitals',
                '🌳 Activate misting systems in parks',
                '📱 Send heat safety SMS to all residents'
            ],
            'ai_optimized_interventions': [
                {
                    'intervention': 'Smart Grid Cooling Optimization',
                    'description': 'AI predicts and pre-cools buildings efficiently',
                    'expected_impact': '30% energy savings with better comfort',
                    'implementation_time': '1 hour'
                }
            ]
        }
    
    return jsonify(response)

@app.route('/api/climate/sustainability-score', methods=['GET'])
def get_sustainability_score():
    """Calculate overall city sustainability score"""
    
    # Get current data
    zones_df = pd.read_csv('data/city_zones.csv')
    zones_dict = {}
    for _, zone in zones_df.iterrows():
        zones_dict[int(zone['zone_id'])] = zone.to_dict()
    
    emissions = climate_ai.calculate_carbon_emissions(zones_dict)
    weather = data_sources.get_weather_data()
    risks = climate_ai.predict_climate_risks(weather)
    
    # Calculate scores (0-100)
    scores = {
        'carbon_efficiency': max(0, 100 - sum(zone['total_co2_tons'] for zone in emissions.values()) / 10),
        'renewable_energy': 25,  # Current renewable % (to be improved)
        'air_quality': max(0, 100 - 220 / 5),  # Based on average AQI
        'green_infrastructure': sum(zone.get('green_cover', 0.15) for zone in zones_dict.values()) / len(zones_dict) * 500,
        'climate_resilience': 100 - risks['overall_climate_risk'],
        'waste_management': 65,  # Mock score
        'water_efficiency': 70,  # Mock score
        'sustainable_mobility': 35  # Current EV adoption etc.
    }
    
    overall_score = sum(scores.values()) / len(scores)
    
    # Benchmarking
    benchmark = {
        'singapore': 85,
        'amsterdam': 82,
        'copenhagen': 88,
        'mumbai': 45,
        'bangalore': 52
    }
    
    # Recommendations for improvement
    recommendations = []
    if scores['renewable_energy'] < 50:
        recommendations.append('Accelerate solar rooftop adoption to reach 50% renewable energy by 2030')
    if scores['sustainable_mobility'] < 40:
        recommendations.append('Expand metro network and EV charging infrastructure')
    if scores['green_infrastructure'] < 60:
        recommendations.append('Increase urban forest cover to 25% of city area')
    
    return jsonify({
        'overall_score': round(overall_score, 1),
        'category_scores': {k: round(v, 1) for k, v in scores.items()},
        'global_ranking': '156 out of 200 cities',
        'benchmark_comparison': benchmark,
        'improvement_recommendations': recommendations,
        'target_score_2030': 75,
        'carbon_neutral_target': 2050,
        'progress_indicators': {
            'trending': 'improving',
            'monthly_change': '+2.3 points',
            'yearly_change': '+8.7 points'
        }
    })

if __name__ == '__main__':
    print("Starting Enhanced Climate API for Hackathon...")
    app.run(debug=True, port=5001)  # Different port to avoid conflicts