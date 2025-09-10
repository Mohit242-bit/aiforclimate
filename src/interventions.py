import pandas as pd
import numpy as np
from simulation import load_data, compute_energy_demand, compute_aqi, compute_heat_island, apply_intervention

# Example interventions
def intervention_examples():
    # Each intervention is a dict: {zone_id: {attribute: new_value, ...}}
    return [
        {3: {'green_cover': 0.20}},  # Add green cover in zone 3
        {2: {'traffic_flow': 1000}},  # Reduce traffic in zone 2
        {5: {'avg_building_age': 20}},  # Retrofit buildings in zone 5
        {1: {'green_cover': 0.18, 'traffic_flow': 900}},  # Combo intervention
    ]

def run_interventions(day=1):
    zones, weather, traffic = load_data()
    temp = weather.loc[weather['day'] == day, 'temperature'].values[0]
    interventions = intervention_examples()
    all_results = []
    for intervention in interventions:
        zones_copy = zones.copy()
        for zone_id, changes in intervention.items():
            idx = zones_copy[zones_copy['zone_id'] == zone_id].index[0]
            for k, v in changes.items():
                if k == 'traffic_flow':
                    # Update traffic file for this zone/day
                    traffic.loc[(traffic['zone_id'] == zone_id) & (traffic['day'] == day), 'traffic_flow'] = v
                else:
                    zones_copy.at[idx, k] = v
        results = []
        for i, zone in zones_copy.iterrows():
            tflow = traffic[(traffic['zone_id'] == zone['zone_id']) & (traffic['day'] == day)]['traffic_flow'].values[0]
            energy = compute_energy_demand(zone, temp)
            aqi = compute_aqi(zone, tflow, {'temperature': temp})
            heat = compute_heat_island(zone)
            results.append({'zone_id': zone['zone_id'], 'energy': energy, 'aqi': aqi, 'heat_island': heat})
        df = pd.DataFrame(results)
        all_results.append(df)
    return all_results

if __name__ == '__main__':
    results = run_interventions()
    for i, df in enumerate(results):
        print(f'Intervention {i+1}')
        print(df)
        df.to_csv(f'outputs/intervention_{i+1}_results.csv', index=False)
