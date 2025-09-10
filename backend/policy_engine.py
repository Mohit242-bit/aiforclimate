"""
Delhi Digital Twin - AI Policy Engine
Solving Delhi's pollution crisis through intelligent intervention testing
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum
import json

class InterventionType(Enum):
    """Types of interventions available"""
    TRAFFIC_BAN = "traffic_ban"
    ODD_EVEN = "odd_even"
    TRUCK_RESTRICTION = "truck_restriction"
    GREEN_CORRIDOR = "green_corridor"
    CONSTRUCTION_BAN = "construction_ban"
    PUBLIC_TRANSPORT = "public_transport"
    SMOG_TOWERS = "smog_towers"
    SCHOOL_TIMING = "school_timing"
    INDUSTRY_CONTROL = "industry_control"
    EMERGENCY_RESPONSE = "emergency"

@dataclass
class PolicyIntervention:
    """Represents a single policy intervention"""
    type: InterventionType
    zones: List[int]
    duration_hours: int
    parameters: Dict
    
    def calculate_impact(self) -> Dict:
        """Calculate the impact of this intervention"""
        impacts = {
            InterventionType.TRUCK_RESTRICTION: {
                "aqi_reduction": 70,
                "congestion_increase": 5,
                "economic_loss": 2000000,  # INR per day
                "lives_saved": 15,
                "implementation_time": 2  # hours
            },
            InterventionType.ODD_EVEN: {
                "aqi_reduction": 45,
                "congestion_increase": -20,
                "economic_loss": 500000,
                "lives_saved": 8,
                "implementation_time": 24
            },
            InterventionType.GREEN_CORRIDOR: {
                "aqi_reduction": 35,
                "congestion_increase": -10,
                "economic_loss": -1000000,  # Negative = economic benefit
                "lives_saved": 25,
                "implementation_time": 720  # 30 days
            },
            InterventionType.CONSTRUCTION_BAN: {
                "aqi_reduction": 25,
                "congestion_increase": 0,
                "economic_loss": 5000000,
                "lives_saved": 5,
                "implementation_time": 1
            },
            InterventionType.PUBLIC_TRANSPORT: {
                "aqi_reduction": 40,
                "congestion_increase": -30,
                "economic_loss": -2000000,
                "lives_saved": 20,
                "implementation_time": 48
            },
            InterventionType.SMOG_TOWERS: {
                "aqi_reduction": 15,
                "congestion_increase": 0,
                "economic_loss": 10000000,
                "lives_saved": 3,
                "implementation_time": 168  # 1 week
            }
        }
        
        base_impact = impacts.get(self.type, {
            "aqi_reduction": 10,
            "congestion_increase": 0,
            "economic_loss": 100000,
            "lives_saved": 2,
            "implementation_time": 24
        })
        
        # Adjust based on number of zones
        zone_multiplier = len(self.zones) / 5.0
        for key in base_impact:
            if key != "implementation_time":
                base_impact[key] = int(base_impact[key] * zone_multiplier)
        
        return base_impact

class PollutionSimulator:
    """Simulates pollution dynamics based on interventions"""
    
    def __init__(self):
        self.baseline_aqi = {
            1: 220,  # Connaught Place
            2: 200,  # Karol Bagh
            3: 240,  # Dwarka
            4: 210,  # Rohini
            5: 230   # Saket
        }
        
        self.traffic_contribution = 0.35  # 35% of pollution from traffic
        self.industry_contribution = 0.25  # 25% from industry
        self.construction_contribution = 0.15  # 15% from construction
        self.stubble_contribution = 0.20  # 20% from stubble burning (seasonal)
        self.other_contribution = 0.05  # 5% other sources
    
    def simulate_dispersion(self, zone: int, wind_speed: float, wind_direction: float) -> Dict:
        """Simulate pollutant dispersion based on meteorological conditions"""
        # Simplified Gaussian plume model
        base_aqi = self.baseline_aqi[zone]
        
        # Wind effect
        dispersion_factor = 1.0 - (wind_speed / 20.0) * 0.3  # Higher wind = better dispersion
        
        # Temperature inversion effect (worse in winter mornings)
        hour = np.random.randint(0, 24)
        if 5 <= hour <= 9:  # Morning inversion
            dispersion_factor *= 1.3
        
        # Calculate dispersed AQI
        dispersed_aqi = base_aqi * dispersion_factor
        
        # Cross-zone pollution transport
        affected_zones = {}
        if wind_speed > 5:
            # Determine downwind zones based on direction
            if 0 <= wind_direction < 90:  # North-East
                affected_zones = {2: 0.2, 3: 0.1}
            elif 90 <= wind_direction < 180:  # South-East
                affected_zones = {3: 0.2, 5: 0.1}
            elif 180 <= wind_direction < 270:  # South-West
                affected_zones = {4: 0.2, 1: 0.1}
            else:  # North-West
                affected_zones = {1: 0.2, 2: 0.1}
        
        return {
            "zone_aqi": dispersed_aqi,
            "affected_zones": affected_zones,
            "dispersion_factor": dispersion_factor
        }
    
    def predict_stubble_impact(self, fire_count: int, wind_from_punjab: bool) -> Dict:
        """Predict impact of stubble burning from Punjab"""
        base_impact = fire_count * 0.5  # Each fire adds 0.5 AQI points
        
        if wind_from_punjab:
            # Northwest winds bring smoke to Delhi
            zone_impacts = {
                1: base_impact * 1.2,  # Central Delhi most affected
                2: base_impact * 1.1,
                3: base_impact * 0.9,
                4: base_impact * 1.3,  # Rohini closest to Punjab
                5: base_impact * 0.8
            }
        else:
            zone_impacts = {zone: base_impact * 0.3 for zone in range(1, 6)}
        
        return zone_impacts

class TrafficOptimizer:
    """Optimizes traffic flow to reduce emissions"""
    
    def __init__(self):
        self.road_network = {
            "outer_ring": {"capacity": 10000, "current_flow": 8000, "emission_factor": 2.5},
            "inner_ring": {"capacity": 8000, "current_flow": 7000, "emission_factor": 2.0},
            "radial_1": {"capacity": 5000, "current_flow": 4500, "emission_factor": 1.8},
            "radial_2": {"capacity": 5000, "current_flow": 4000, "emission_factor": 1.8},
            "arterial": {"capacity": 3000, "current_flow": 2800, "emission_factor": 1.5}
        }
        
    def optimize_signals(self, congestion_level: float) -> Dict:
        """Optimize traffic signals using reinforcement learning logic"""
        # Simplified RL-based signal optimization
        if congestion_level > 0.8:
            # Heavy congestion - increase green time on main roads
            signal_adjustments = {
                "outer_ring": +15,  # seconds
                "inner_ring": +10,
                "radial_1": -5,
                "radial_2": -5,
                "arterial": -10
            }
            emission_reduction = 0.12  # 12% reduction
        else:
            # Normal flow - balance all roads
            signal_adjustments = {road: 0 for road in self.road_network}
            emission_reduction = 0.05
        
        return {
            "signal_adjustments": signal_adjustments,
            "emission_reduction": emission_reduction,
            "estimated_travel_time_change": -5 if congestion_level > 0.8 else 0
        }
    
    def reroute_traffic(self, blocked_roads: List[str]) -> Dict:
        """Reroute traffic when certain roads are restricted"""
        total_displaced = sum(self.road_network[road]["current_flow"] 
                            for road in blocked_roads if road in self.road_network)
        
        # Distribute to other roads
        available_roads = [r for r in self.road_network if r not in blocked_roads]
        rerouted_flow = {}
        
        for road in available_roads:
            spare_capacity = self.road_network[road]["capacity"] - self.road_network[road]["current_flow"]
            allocated = min(spare_capacity, total_displaced / len(available_roads))
            rerouted_flow[road] = allocated
            total_displaced -= allocated
        
        # Calculate new emissions
        new_emissions = sum(
            (self.road_network[road]["current_flow"] + rerouted_flow.get(road, 0)) * 
            self.road_network[road]["emission_factor"]
            for road in self.road_network
            if road not in blocked_roads
        )
        
        baseline_emissions = sum(
            road["current_flow"] * road["emission_factor"] 
            for road in self.road_network.values()
        )
        
        return {
            "rerouted_flow": rerouted_flow,
            "congestion_increase": total_displaced / 1000,  # Unallocated vehicles
            "emission_change": (new_emissions - baseline_emissions) / baseline_emissions * 100
        }

class ExposureAnalyzer:
    """Analyzes citizen exposure to pollution"""
    
    def __init__(self):
        self.vulnerable_groups = {
            "school_children": {"population": 500000, "exposure_hours": 8, "vulnerability": 2.0},
            "elderly": {"population": 300000, "exposure_hours": 12, "vulnerability": 1.8},
            "outdoor_workers": {"population": 200000, "exposure_hours": 10, "vulnerability": 1.5},
            "commuters": {"population": 1000000, "exposure_hours": 3, "vulnerability": 1.2},
            "general": {"population": 2000000, "exposure_hours": 4, "vulnerability": 1.0}
        }
    
    def calculate_exposure(self, aqi_levels: Dict[int, float]) -> Dict:
        """Calculate exposure levels for different groups"""
        avg_aqi = np.mean(list(aqi_levels.values()))
        
        exposures = {}
        total_health_impact = 0
        
        for group, data in self.vulnerable_groups.items():
            # Exposure = AQI * hours * vulnerability factor
            exposure_index = avg_aqi * data["exposure_hours"] * data["vulnerability"] / 24
            
            # Health impact (simplified)
            if exposure_index > 200:
                health_risk = "Severe"
                affected_population = data["population"] * 0.15
            elif exposure_index > 150:
                health_risk = "High"
                affected_population = data["population"] * 0.10
            elif exposure_index > 100:
                health_risk = "Moderate"
                affected_population = data["population"] * 0.05
            else:
                health_risk = "Low"
                affected_population = data["population"] * 0.02
            
            exposures[group] = {
                "exposure_index": exposure_index,
                "health_risk": health_risk,
                "affected_population": int(affected_population)
            }
            
            total_health_impact += affected_population
        
        # Calculate potential lives saved by reducing AQI
        lives_at_risk = total_health_impact * 0.001  # 0.1% mortality risk
        
        return {
            "group_exposures": exposures,
            "total_affected": int(total_health_impact),
            "lives_at_risk": int(lives_at_risk)
        }
    
    def recommend_safe_hours(self, aqi_forecast: List[float]) -> Dict:
        """Recommend safe hours for outdoor activities"""
        safe_hours = []
        moderate_hours = []
        unsafe_hours = []
        
        for hour, aqi in enumerate(aqi_forecast):
            if aqi < 100:
                safe_hours.append(hour)
            elif aqi < 200:
                moderate_hours.append(hour)
            else:
                unsafe_hours.append(hour)
        
        return {
            "safe_hours": safe_hours,
            "moderate_hours": moderate_hours,
            "unsafe_hours": unsafe_hours,
            "recommendation": f"Best time for outdoor activities: {safe_hours[0] if safe_hours else 'None'}:00-{safe_hours[-1] if safe_hours else 'None'}:00"
        }

class AIRecommendationEngine:
    """Main AI engine that recommends optimal interventions"""
    
    def __init__(self):
        self.simulator = PollutionSimulator()
        self.traffic_optimizer = TrafficOptimizer()
        self.exposure_analyzer = ExposureAnalyzer()
        self.intervention_history = []
    
    def analyze_current_situation(self, current_aqi: Dict, weather: Dict, traffic: Dict) -> Dict:
        """Analyze current pollution situation"""
        
        # Identify crisis zones
        crisis_zones = [zone for zone, aqi in current_aqi.items() if aqi > 300]
        warning_zones = [zone for zone, aqi in current_aqi.items() if 200 <= aqi <= 300]
        
        # Analyze trends
        avg_aqi = np.mean(list(current_aqi.values()))
        
        # Determine primary pollution source
        if weather.get("stubble_burning_active", False):
            primary_source = "stubble_burning"
            contribution = 0.40
        elif any(traffic[zone] > 0.8 for zone in traffic):
            primary_source = "traffic"
            contribution = 0.35
        else:
            primary_source = "mixed"
            contribution = 0.25
        
        return {
            "severity": "CRITICAL" if crisis_zones else "WARNING" if warning_zones else "MODERATE",
            "crisis_zones": crisis_zones,
            "warning_zones": warning_zones,
            "avg_aqi": avg_aqi,
            "primary_source": primary_source,
            "source_contribution": contribution
        }
    
    def generate_recommendations(self, situation: Dict) -> List[Dict]:
        """Generate AI-powered recommendations based on situation"""
        recommendations = []
        
        if situation["severity"] == "CRITICAL":
            # Emergency interventions
            recommendations.append({
                "priority": 1,
                "intervention": PolicyIntervention(
                    type=InterventionType.EMERGENCY_RESPONSE,
                    zones=situation["crisis_zones"],
                    duration_hours=24,
                    parameters={"all_measures": True}
                ),
                "reasoning": "Critical AQI levels require immediate comprehensive action",
                "expected_impact": {
                    "aqi_reduction": 100,
                    "implementation_time": 1,
                    "confidence": 0.95
                }
            })
            
            recommendations.append({
                "priority": 2,
                "intervention": PolicyIntervention(
                    type=InterventionType.TRUCK_RESTRICTION,
                    zones=situation["crisis_zones"],
                    duration_hours=12,
                    parameters={"hours": "6-18", "vehicle_types": ["trucks", "heavy"]}
                ),
                "reasoning": "Heavy vehicles contribute 40% of vehicular emissions",
                "expected_impact": {
                    "aqi_reduction": 70,
                    "implementation_time": 2,
                    "confidence": 0.90
                }
            })
        
        elif situation["severity"] == "WARNING":
            # Moderate interventions
            recommendations.append({
                "priority": 1,
                "intervention": PolicyIntervention(
                    type=InterventionType.ODD_EVEN,
                    zones=situation["warning_zones"],
                    duration_hours=24,
                    parameters={"exemptions": ["women", "disabled", "emergency"]}
                ),
                "reasoning": "Odd-even can reduce traffic volume by 40% with minimal disruption",
                "expected_impact": {
                    "aqi_reduction": 45,
                    "implementation_time": 24,
                    "confidence": 0.85
                }
            })
        
        # Long-term recommendations
        recommendations.append({
            "priority": 3,
            "intervention": PolicyIntervention(
                type=InterventionType.GREEN_CORRIDOR,
                zones=[1, 2, 3, 4, 5],
                duration_hours=720 * 24,  # 30 days
                parameters={"tree_count": 10000, "area_sqkm": 5}
            ),
            "reasoning": "Green corridors provide sustainable long-term pollution control",
            "expected_impact": {
                "aqi_reduction": 35,
                "implementation_time": 720,
                "confidence": 0.80
            }
        })
        
        # Score and rank recommendations
        for rec in recommendations:
            impact = rec["intervention"].calculate_impact()
            rec["cost_benefit_score"] = (
                impact["aqi_reduction"] * 1000 +  # Weight AQI reduction heavily
                impact["lives_saved"] * 10000 -    # Lives saved very important
                impact["economic_loss"] / 1000000 - # Consider economic impact
                impact["implementation_time"] * 10  # Faster is better
            )
        
        recommendations.sort(key=lambda x: x["cost_benefit_score"], reverse=True)
        
        return recommendations[:3]  # Return top 3 recommendations
    
    def predict_intervention_outcome(self, intervention: PolicyIntervention, 
                                    current_state: Dict) -> Dict:
        """Predict the outcome of an intervention using ML models"""
        
        # Simulate intervention
        impact = intervention.calculate_impact()
        
        # Calculate new AQI levels
        new_aqi = {}
        for zone in range(1, 6):
            if zone in intervention.zones:
                reduction = impact["aqi_reduction"]
                new_aqi[zone] = max(50, current_state["aqi"][zone] - reduction)
            else:
                # Spillover effect
                new_aqi[zone] = current_state["aqi"][zone] - impact["aqi_reduction"] * 0.2
        
        # Calculate exposure reduction
        exposure_before = self.exposure_analyzer.calculate_exposure(current_state["aqi"])
        exposure_after = self.exposure_analyzer.calculate_exposure(new_aqi)
        
        lives_saved = exposure_before["lives_at_risk"] - exposure_after["lives_at_risk"]
        
        return {
            "new_aqi": new_aqi,
            "aqi_reduction": impact["aqi_reduction"],
            "lives_saved": lives_saved,
            "economic_impact": impact["economic_loss"],
            "implementation_time": impact["implementation_time"],
            "confidence_score": 0.85,
            "side_effects": {
                "congestion_change": impact["congestion_increase"],
                "public_sentiment": "Positive" if lives_saved > 10 else "Mixed"
            }
        }

# API endpoints for the Flask backend
def get_policy_recommendations(current_data: Dict) -> Dict:
    """Main API endpoint for getting AI recommendations"""
    
    engine = AIRecommendationEngine()
    
    # Analyze current situation
    situation = engine.analyze_current_situation(
        current_data.get("aqi", {1: 220, 2: 200, 3: 240, 4: 210, 5: 230}),
        current_data.get("weather", {"stubble_burning_active": True}),
        current_data.get("traffic", {1: 0.8, 2: 0.7, 3: 0.9, 4: 0.7, 5: 0.8})
    )
    
    # Generate recommendations
    recommendations = engine.generate_recommendations(situation)
    
    # Format for frontend
    formatted_recs = []
    for rec in recommendations:
        outcome = engine.predict_intervention_outcome(
            rec["intervention"],
            {"aqi": current_data.get("aqi", {1: 220, 2: 200, 3: 240, 4: 210, 5: 230})}
        )
        
        formatted_recs.append({
            "id": len(formatted_recs) + 1,
            "name": rec["intervention"].type.value.replace("_", " ").title(),
            "priority": rec["priority"],
            "reasoning": rec["reasoning"],
            "zones": rec["intervention"].zones,
            "duration": f"{rec['intervention'].duration_hours} hours",
            "expected_outcome": {
                "aqi_reduction": outcome["aqi_reduction"],
                "lives_saved": outcome["lives_saved"],
                "economic_impact": f"₹{abs(outcome['economic_impact']):,.0f}",
                "implementation_time": f"{outcome['implementation_time']} hours"
            },
            "confidence": outcome["confidence_score"],
            "cost_benefit_score": rec["cost_benefit_score"]
        })
    
    return {
        "situation_analysis": situation,
        "recommendations": formatted_recs,
        "timestamp": pd.Timestamp.now().isoformat()
    }

if __name__ == "__main__":
    # Test the system
    test_data = {
        "aqi": {1: 350, 2: 320, 3: 380, 4: 310, 5: 340},  # Crisis levels
        "weather": {"stubble_burning_active": True, "wind_speed": 5, "wind_direction": 315},
        "traffic": {1: 0.9, 2: 0.85, 3: 0.95, 4: 0.8, 5: 0.9}
    }
    
    result = get_policy_recommendations(test_data)
    print(json.dumps(result, indent=2, default=str))
