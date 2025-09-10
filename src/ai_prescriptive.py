import pandas as pd
import numpy as np
from .simulation import load_data, compute_energy_demand, compute_aqi, compute_heat_island, apply_intervention
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split

# Generate random interventions
def generate_random_interventions(zones, n=100):
    interventions = []
    for _ in range(n):
        intervention = {}
        for _, zone in zones.iterrows():
            changes = {}
            if np.random.rand() < 0.5:
                changes['green_cover'] = np.clip(zone['green_cover'] + np.random.uniform(-0.05, 0.10), 0.05, 0.30)
            if np.random.rand() < 0.5:
                changes['traffic_flow'] = int(np.clip(zone['traffic_flow'] * np.random.uniform(0.8, 1.1), 800, 2000))
            if np.random.rand() < 0.5:
                changes['avg_building_age'] = int(np.clip(zone['avg_building_age'] + np.random.randint(-10, 5), 15, 50))
            if changes:
                intervention[zone['zone_id']] = changes
        interventions.append(intervention)
    return interventions

def simulate_interventions(interventions, day=1):
    zones, weather, traffic = load_data()
    temp = weather.loc[weather['day'] == day, 'temperature'].values[0]
    X, y_energy, y_aqi, y_heat = [], [], [], []
    for intervention in interventions:
        zones_copy = zones.copy()
        traffic_copy = traffic.copy()
        for zone_id, changes in intervention.items():
            idx = zones_copy[zones_copy['zone_id'] == zone_id].index[0]
            for k, v in changes.items():
                if k == 'traffic_flow':
                    traffic_copy.loc[(traffic_copy['zone_id'] == zone_id) & (traffic_copy['day'] == day), 'traffic_flow'] = v
                else:
                    zones_copy.at[idx, k] = v
        for i, zone in zones_copy.iterrows():
            tflow = traffic_copy[(traffic_copy['zone_id'] == zone['zone_id']) & (traffic_copy['day'] == day)]['traffic_flow'].values[0]
            energy = compute_energy_demand(zone, temp)
            aqi = compute_aqi(zone, tflow, {'temperature': temp})
            heat = compute_heat_island(zone)
            X.append([
                zone['zone_id'], zone['population'], tflow, zone['avg_building_age'],
                zone['green_cover'], zone['industrial_activity']
            ])
            y_energy.append(energy)
            y_aqi.append(aqi)
            y_heat.append(heat)
    return np.array(X), np.array(y_energy), np.array(y_aqi), np.array(y_heat)

def train_surrogate(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = GradientBoostingRegressor()
    model.fit(X_train, y_train)
    print(f"Surrogate R^2: {model.score(X_test, y_test):.2f}")
    return model

if __name__ == '__main__':
    zones, _, _ = load_data()
    interventions = generate_random_interventions(zones, n=100)
    X, y_energy, y_aqi, y_heat = simulate_interventions(interventions)
    print('Training surrogate for AQI...')
    surrogate_aqi = train_surrogate(X, y_aqi)
    print('Training surrogate for energy...')
    surrogate_energy = train_surrogate(X, y_energy)
    print('Training surrogate for heat island...')
    surrogate_heat = train_surrogate(X, y_heat)
