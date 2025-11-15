import numpy as np
import pandas as pd
from typing import Dict, List
from src.models.traffic_simulator import TrafficSimulator

class EmissionsModel:
    """
    Compute vehicle emissions and zone-level AQI impact from traffic.
    """
    
    # Emission factors (grams per vehicle-km)
    # These represent exhaust + re-suspension emissions for urban Indian vehicles
    EMISSION_FACTORS = {
        'Car': {'PM25': 0.5, 'NOx': 0.8, 'CO': 2.5, 'CO2': 180},  # 0.5g/km PM2.5 (includes re-suspension)
        'Truck': {'PM25': 2.5, 'NOx': 5.0, 'CO': 8.0, 'CO2': 950},  # 2.5g/km for trucks
    }
    
    # Zone background AQI (baseline before traffic contribution)
    ZONE_BACKGROUND_AQI = {
        'Z01': 250, 'Z02': 280, 'Z03': 265, 'Z04': 245,
        'Z05': 275, 'Z06': 290, 'Z07': 260, 'Z08': 270,
    }
    
    def __init__(self, simulator: TrafficSimulator):
        """
        Initialize emissions model.
        
        Args:
            simulator: TrafficSimulator instance with baseline results
        """
        self.simulator = simulator
        self.network = simulator.network
    
    def compute_segment_emissions(self, segment_id: str) -> Dict:
        """
        Compute emissions for a segment based on current flow.
        
        Args:
            segment_id: Segment ID
            
        Returns:
            Dictionary with emissions by pollutant
        """
        seg_results = self.simulator.get_segment_results(segment_id)
        if not seg_results:
            return {}
        
        seg = self.network.get_segment(segment_id)
        flow = seg_results['flow_vph']
        length = seg['length_km']
        
        # Assume 70% cars, 30% trucks in flow
        car_flow = flow * 0.7
        truck_flow = flow * 0.3
        
        # Daily emissions (vehicles per day = flow * 24 hours)
        daily_vehicles = {
            'Car': car_flow * 24,
            'Truck': truck_flow * 24,
        }
        
        emissions = {
            'PM25': 0, 'NOx': 0, 'CO': 0, 'CO2': 0,
            'segment_id': segment_id,
            'length_km': length,
            'daily_vehicles': flow * 24,
        }
        
        for vtype, daily_count in daily_vehicles.items():
            vehicle_km = daily_count * length
            for pollutant, factor in self.EMISSION_FACTORS[vtype].items():
                emissions[pollutant] += vehicle_km * factor  # grams
        
        return emissions
    
    def compute_zone_emissions(self, zone_id: str) -> Dict:
        """
        Aggregate emissions for all segments in a zone.
        
        Args:
            zone_id: Zone ID
            
        Returns:
            Total emissions in zone
        """
        segments = self.network.get_segments_in_zone(zone_id)
        
        zone_emissions = {
            'zone_id': zone_id,
            'PM25': 0, 'NOx': 0, 'CO': 0, 'CO2': 0,
            'total_vehicles': 0,
            'num_segments': len(segments),
        }
        
        for seg_id in segments:
            seg_emissions = self.compute_segment_emissions(seg_id)
            if seg_emissions:
                for pollutant in ['PM25', 'NOx', 'CO', 'CO2']:
                    zone_emissions[pollutant] += seg_emissions[pollutant]
                zone_emissions['total_vehicles'] += seg_emissions['daily_vehicles']
        
        return zone_emissions
    
    def estimate_aqi_from_emissions(self, pm25_grams_per_day: float, 
                                    zone_area_sqkm: float = 5.0) -> float:
        """
        Estimate AQI contribution from PM2.5 emissions.
        Simplified: Gaussian plume dispersion model.
        
        Args:
            pm25_grams_per_day: Daily PM2.5 emissions in grams
            zone_area_sqkm: Zone area in square km
            
        Returns:
            Estimated AQI contribution (0-500 scale)
        """
        # Convert grams to mg
        emissions_mg = pm25_grams_per_day * 1000
        
        # Zone area in m²
        zone_area_m2 = zone_area_sqkm * 1e6
        
        # Concentration (µg/m³) assuming uniform distribution
        # Dispersion efficiency factor: with wind, ~60% of emissions affect the zone
        concentration_ug_m3 = (emissions_mg / zone_area_m2) * 1e6 * 0.6
        
        # AQI for PM2.5: 
        # 0-50 AQI: 0-30 µg/m³
        # 51-100 AQI: 31-60 µg/m³
        # 101-200 AQI: 61-90 µg/m³
        # 201-300 AQI: 91-120 µg/m³
        # 301-500 AQI: 121+ µg/m³
        
        if concentration_ug_m3 <= 30:
            aqi = (concentration_ug_m3 / 30) * 50
        elif concentration_ug_m3 <= 60:
            aqi = 50 + ((concentration_ug_m3 - 30) / 30) * 50
        elif concentration_ug_m3 <= 90:
            aqi = 100 + ((concentration_ug_m3 - 60) / 30) * 100
        elif concentration_ug_m3 <= 120:
            aqi = 200 + ((concentration_ug_m3 - 90) / 30) * 100
        else:
            aqi = 300 + min(((concentration_ug_m3 - 120) / 120) * 200, 200)
        
        return min(aqi, 500)  # Cap at 500
    
    def compute_zone_aqi(self, zone_id: str) -> Dict:
        """
        Compute zone-level AQI including traffic and background.
        
        Args:
            zone_id: Zone ID
            
        Returns:
            Zone AQI breakdown
        """
        zone_emissions = self.compute_zone_emissions(zone_id)
        
        # AQI contribution from traffic (in grams/day, normalized)
        traffic_aqi = self.estimate_aqi_from_emissions(zone_emissions['PM25'] / 1000)
        
        # Total AQI = background + weighted traffic contribution
        background_aqi = self.ZONE_BACKGROUND_AQI.get(zone_id, 250)
        
        # Traffic AQI contribution is damped (scale down traffic contribution)
        # This prevents saturation at 500 while still showing traffic impact
        total_aqi = background_aqi + traffic_aqi * 0.15  # Scale down traffic impact
        total_aqi = min(total_aqi, 500)  # Cap at 500
        
        return {
            'zone_id': zone_id,
            'background_aqi': background_aqi,
            'traffic_aqi_contribution': traffic_aqi * 0.15,  # Show scaled contribution
            'total_aqi': total_aqi,
            'pm25_grams': zone_emissions['PM25'],
            'nox_grams': zone_emissions['NOx'],
            'co_grams': zone_emissions['CO'],
            'co2_grams': zone_emissions['CO2'],
            'total_daily_vehicles': zone_emissions['total_vehicles'],
        }
    
    def compute_all_zones_aqi(self) -> List[Dict]:
        """
        Compute AQI for all zones.
        
        Returns:
            List of zone AQI dictionaries
        """
        all_zones = set()
        for seg_id, seg_data in self.network.segment_data.items():
            all_zones.add(seg_data['zone_id'])
        
        zone_aqi_list = []
        for zone_id in sorted(all_zones):
            zone_aqi = self.compute_zone_aqi(zone_id)
            zone_aqi_list.append(zone_aqi)
        
        return zone_aqi_list
    
    def compute_health_impact(self, zone_id: str, population: int = 100000) -> Dict:
        """
        Estimate health impact from AQI in a zone.
        
        Args:
            zone_id: Zone ID
            population: Population in zone
            
        Returns:
            Health impact estimates
        """
        zone_aqi = self.compute_zone_aqi(zone_id)
        aqi = zone_aqi['total_aqi']
        
        # Health impacts based on AQI levels
        if aqi <= 50:
            category = 'Good'
            health_risk = 'None'
        elif aqi <= 100:
            category = 'Satisfactory'
            health_risk = 'Low'
        elif aqi <= 200:
            category = 'Moderately Polluted'
            health_risk = 'Moderate'
        elif aqi <= 300:
            category = 'Poor'
            health_risk = 'High'
        elif aqi <= 400:
            category = 'Very Poor'
            health_risk = 'Very High'
        else:
            category = 'Severe'
            health_risk = 'Critical'
        
        # Rough estimate: % population affected (simplified)
        if aqi > 200:
            affected_population_pct = (aqi - 200) / 300 * 100  # Up to 100% at AQI 500
        else:
            affected_population_pct = 0
        
        affected_population = int(population * affected_population_pct / 100)
        
        return {
            'zone_id': zone_id,
            'aqi': aqi,
            'category': category,
            'health_risk': health_risk,
            'population': population,
            'affected_population': affected_population,
            'respiratory_symptoms_pct': (aqi / 500) * 100,  # Rough estimate
        }
    
    def compare_scenarios(self, baseline_name: str, intervention_name: str) -> Dict:
        """
        Compare emissions between two scenarios.
        
        Args:
            baseline_name: Name of baseline scenario
            intervention_name: Name of intervention scenario
            
        Returns:
            Comparison results
        """
        if intervention_name not in self.simulator.simulation_results:
            return {'error': 'Intervention scenario not found'}
        
        baseline_zones = self.compute_all_zones_aqi()
        
        # Switch to intervention results (this is simplified; in practice would need separate computation)
        intervention_zones = self.compute_all_zones_aqi()
        
        comparison = {
            'baseline_scenario': baseline_name,
            'intervention_scenario': intervention_name,
            'zone_comparisons': [],
        }
        
        for bz, iz in zip(baseline_zones, intervention_zones):
            comparison['zone_comparisons'].append({
                'zone_id': bz['zone_id'],
                'baseline_aqi': bz['total_aqi'],
                'intervention_aqi': iz['total_aqi'],
                'aqi_change': iz['total_aqi'] - bz['total_aqi'],
                'aqi_change_pct': ((iz['total_aqi'] - bz['total_aqi']) / bz['total_aqi'] * 100) if bz['total_aqi'] > 0 else 0,
            })
        
        return comparison
