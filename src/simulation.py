import pandas as pd
import numpy as np

# Load data
def load_data():
    zones = pd.read_csv('data/city_zones.csv')
    weather = pd.read_csv('data/weather.csv')
    traffic = pd.read_csv('data/traffic.csv')
    return zones, weather, traffic

# Energy demand model (simple linear)
def compute_energy_demand(zone, temp):
    # Example: cooling demand increases with temp, building age, and population
    base = zone['energy_use']
    temp_factor = 1 + 0.03 * (temp - 35)
    age_factor = 1 + 0.01 * (zone['avg_building_age'] - 30)
    pop_factor = 1 + 0.00005 * (zone['population'] - 15000)
    return base * temp_factor * age_factor * pop_factor

# AQI model
def compute_aqi(zone, traffic_flow, weather):
    # AQI increases with traffic, industry, and temp; decreases with green cover
    base = zone['aqi']
    traffic_factor = 1 + 0.0002 * (traffic_flow - 1000)
    industry_factor = 1 + 0.2 * (zone['industrial_activity'] - 0.7)
    temp_factor = 1 + 0.01 * (weather['temperature'] - 35)
    green_factor = 1 - 0.5 * (zone['green_cover'] - 0.15)
    return base * traffic_factor * industry_factor * temp_factor * green_factor

# Heat island effect model
def compute_heat_island(zone):
    # Temp rise increases with population density, decreases with green cover
    density = zone['population'] / 2.0  # Assume area=2 sq km for all
    return 0.5 + 0.00005 * (density - 8000) - 2 * (zone['green_cover'] - 0.15)

# Apply intervention
def apply_intervention(zone, intervention):
    # intervention: dict with keys like 'green_cover', 'traffic_flow', 'avg_building_age'
    for k, v in intervention.items():
        if k in zone:
            zone[k] = v
    return zone

if __name__ == '__main__':
    zones, weather, traffic = load_data()
    day = 1
    temp = weather.loc[weather['day'] == day, 'temperature'].values[0]
    results = []
    for i, zone in zones.iterrows():
        tflow = traffic[(traffic['zone_id'] == zone['zone_id']) & (traffic['day'] == day)]['traffic_flow'].values[0]
        energy = compute_energy_demand(zone, temp)
        aqi = compute_aqi(zone, tflow, {'temperature': temp})
        heat = compute_heat_island(zone)
        results.append({'zone_id': zone['zone_id'], 'energy': energy, 'aqi': aqi, 'heat_island': heat})
    df = pd.DataFrame(results)
    print(df)
    df.to_csv('outputs/baseline_results.csv', index=False)
