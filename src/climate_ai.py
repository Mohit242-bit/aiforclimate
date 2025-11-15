"""
Delhi Digital Twin - Climate AI Module
Advanced climate modeling and carbon tracking for hackathon
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from typing import Dict, List, Tuple
import datetime

class ClimateAI:
    """Advanced climate modeling and carbon tracking"""
    
    def __init__(self):
        self.carbon_factors = {
            'traffic': 0.21,  # kg CO2 per km per vehicle
            'industry': 2.3,  # kg CO2 per kWh industrial
            'buildings': 0.85,  # kg CO2 per kWh residential
            'waste': 0.5      # kg CO2 per kg waste
        }
        self.renewable_potential = {
            1: {'solar': 0.8, 'wind': 0.3},  # Connaught Place
            2: {'solar': 0.7, 'wind': 0.4},  # Karol Bagh  
            3: {'solar': 0.9, 'wind': 0.6},  # Dwarka
            4: {'solar': 0.8, 'wind': 0.5},  # Rohini
            5: {'solar': 0.7, 'wind': 0.3}   # Saket
        }
        
    def calculate_carbon_emissions(self, zone_data: Dict) -> Dict:
        """Calculate real-time carbon emissions per zone"""
        emissions = {}
        
        for zone_id, data in zone_data.items():
            # Traffic emissions
            traffic_co2 = data['traffic_flow'] * 10 * self.carbon_factors['traffic']  # 10km avg journey
            
            # Building emissions  
            building_co2 = data['energy_use'] * self.carbon_factors['buildings']
            
            # Industrial emissions
            industrial_co2 = data.get('industrial_activity', 0.5) * 1000 * self.carbon_factors['industry']
            
            total_co2 = traffic_co2 + building_co2 + industrial_co2
            
            emissions[zone_id] = {
                'total_co2_tons': total_co2 / 1000,  # Convert to tons
                'traffic_co2': traffic_co2 / 1000,
                'building_co2': building_co2 / 1000,
                'industrial_co2': industrial_co2 / 1000,
                'per_capita_co2': (total_co2 / 1000) / (data.get('population', 15000) / 1000)
            }
            
        return emissions
    
    def predict_net_zero_pathway(self, zone_id: int, current_emissions: float) -> Dict:
        """Predict pathway to net-zero emissions"""
        
        # Intervention scenarios
        scenarios = {
            'aggressive': {
                'ev_adoption': 0.8,
                'renewable_energy': 0.9,
                'green_buildings': 0.7,
                'timeline_years': 10
            },
            'moderate': {
                'ev_adoption': 0.5,
                'renewable_energy': 0.6,
                'green_buildings': 0.4,
                'timeline_years': 15
            },
            'conservative': {
                'ev_adoption': 0.3,
                'renewable_energy': 0.4,
                'green_buildings': 0.2,
                'timeline_years': 20
            }
        }
        
        pathways = {}
        for scenario_name, scenario in scenarios.items():
            # Calculate emission reductions
            traffic_reduction = current_emissions * 0.4 * scenario['ev_adoption']
            energy_reduction = current_emissions * 0.35 * scenario['renewable_energy'] 
            building_reduction = current_emissions * 0.25 * scenario['green_buildings']
            
            total_reduction = traffic_reduction + energy_reduction + building_reduction
            remaining_emissions = max(0, current_emissions - total_reduction)
            
            pathways[scenario_name] = {
                'target_year': 2024 + scenario['timeline_years'],
                'emission_reduction_percent': (total_reduction / current_emissions) * 100,
                'remaining_emissions': remaining_emissions,
                'carbon_offset_needed': max(0, remaining_emissions),
                'investment_required_crores': total_reduction * 50  # ₹50 crores per ton reduction
            }
            
        return pathways
    
    def optimize_renewable_energy(self, zone_data: Dict) -> Dict:
        """AI-optimized renewable energy placement"""
        
        recommendations = {}
        
        for zone_id, data in zone_data.items():
            solar_potential = self.renewable_potential[zone_id]['solar']
            wind_potential = self.renewable_potential[zone_id]['wind']
            
            # Calculate optimal renewable mix
            energy_demand = data['energy_use']
            
            # Solar capacity (MW)
            optimal_solar = energy_demand * 0.6 * solar_potential
            
            # Wind capacity (MW)  
            optimal_wind = energy_demand * 0.4 * wind_potential
            
            # Battery storage (MWh)
            battery_capacity = (optimal_solar + optimal_wind) * 0.25
            
            # Economic analysis
            solar_cost = optimal_solar * 4.5  # ₹4.5 crores per MW
            wind_cost = optimal_wind * 6.0   # ₹6 crores per MW
            battery_cost = battery_capacity * 2.0  # ₹2 crores per MWh
            
            total_investment = solar_cost + wind_cost + battery_cost
            annual_savings = energy_demand * 0.06 * 8760  # ₹6/kWh savings
            payback_years = total_investment / (annual_savings / 10000000)  # Convert to crores
            
            recommendations[zone_id] = {
                'solar_mw': optimal_solar,
                'wind_mw': optimal_wind,
                'battery_mwh': battery_capacity,
                'investment_crores': total_investment,
                'annual_savings_crores': annual_savings / 10000000,
                'payback_years': payback_years,
                'co2_reduction_tons_year': (optimal_solar + optimal_wind) * 8760 * 0.85 / 1000  # 0.85 kg CO2/kWh
            }
            
        return recommendations
    
    def predict_climate_risks(self, weather_data: Dict) -> Dict:
        """Predict extreme weather and climate risks"""
        
        current_temp = weather_data.get('temperature', 35)
        humidity = weather_data.get('humidity', 60)
        
        # Simple risk assessment (would use complex ML models in production)
        risks = {
            'heatwave_risk': min(100, max(0, (current_temp - 40) * 10)),
            'flood_risk': min(100, max(0, (humidity - 80) * 5)),
            'air_quality_risk': min(100, max(0, (current_temp - 35) * 3 + (humidity - 50) * 2)),
            'drought_risk': min(100, max(0, (45 - current_temp) * 2 + (50 - humidity) * 1.5))
        }
        
        # Generate alerts
        alerts = []
        if risks['heatwave_risk'] > 70:
            alerts.append("🔥 EXTREME HEAT WARNING: Implement cooling centers")
        if risks['flood_risk'] > 60:
            alerts.append("🌊 FLOOD RISK: Activate drainage systems") 
        if risks['air_quality_risk'] > 80:
            alerts.append("💨 AIR QUALITY CRISIS: Emergency protocols needed")
            
        return {
            'risk_scores': risks,
            'alerts': alerts,
            'overall_climate_risk': sum(risks.values()) / len(risks)
        }
    
    def calculate_green_infrastructure_roi(self, intervention_type: str, zone_id: int) -> Dict:
        """Calculate ROI for green infrastructure investments"""
        
        interventions = {
            'urban_forest': {
                'cost_per_hectare': 0.5,  # ₹50 lakhs per hectare
                'co2_sequestration_tons_year': 22,  # tons CO2 per hectare per year
                'cooling_effect_celsius': 2.5,
                'air_quality_improvement': 15,  # % AQI improvement
                'biodiversity_score': 85
            },
            'green_roofs': {
                'cost_per_hectare': 1.2,  # ₹1.2 crores per hectare
                'co2_sequestration_tons_year': 8,
                'cooling_effect_celsius': 1.8,
                'air_quality_improvement': 8,
                'biodiversity_score': 45
            },
            'vertical_gardens': {
                'cost_per_hectare': 0.8,  # ₹80 lakhs per hectare
                'co2_sequestration_tons_year': 12,
                'cooling_effect_celsius': 1.2,
                'air_quality_improvement': 10,
                'biodiversity_score': 55
            }
        }
        
        if intervention_type not in interventions:
            return {}
            
        intervention = interventions[intervention_type]
        
        # Economic benefits
        carbon_credit_value = intervention['co2_sequestration_tons_year'] * 2000  # ₹2000 per ton CO2
        cooling_savings = intervention['cooling_effect_celsius'] * 100000  # ₹1 lakh per degree cooling
        health_benefits = intervention['air_quality_improvement'] * 50000  # ₹50k per % AQI improvement
        
        annual_benefits = carbon_credit_value + cooling_savings + health_benefits
        payback_years = intervention['cost_per_hectare'] * 10000000 / annual_benefits  # Convert crores to rupees
        
        return {
            'investment_crores': intervention['cost_per_hectare'],
            'annual_benefits_lakhs': annual_benefits / 100000,
            'payback_years': payback_years,
            'co2_sequestration': intervention['co2_sequestration_tons_year'],
            'cooling_effect': intervention['cooling_effect_celsius'],
            'air_quality_improvement': intervention['air_quality_improvement'],
            'biodiversity_score': intervention['biodiversity_score'],
            'roi_percentage': (annual_benefits / (intervention['cost_per_hectare'] * 10000000)) * 100
        }

# Usage example
if __name__ == "__main__":
    climate_ai = ClimateAI()
    
    # Sample zone data
    sample_zones = {
        1: {'traffic_flow': 1200, 'energy_use': 1500, 'population': 15000, 'industrial_activity': 0.8},
        2: {'traffic_flow': 1400, 'energy_use': 1600, 'population': 18000, 'industrial_activity': 0.6}
    }
    
    # Calculate emissions
    emissions = climate_ai.calculate_carbon_emissions(sample_zones)
    print("Carbon Emissions:", emissions)
    
    # Net-zero pathways
    pathways = climate_ai.predict_net_zero_pathway(1, emissions[1]['total_co2_tons'])
    print("Net-Zero Pathways:", pathways)
    
    # Renewable energy optimization
    renewable_recs = climate_ai.optimize_renewable_energy(sample_zones)
    print("Renewable Energy Recommendations:", renewable_recs)