# 🤖 AI/ML ENGINEER - Detailed Task Guide

## 👤 **Team Member 1: AI/ML Engineer**
**Focus**: Advanced Climate AI Models, Machine Learning, Data Science

---

## 📋 **WEEK 1 TASKS (Priority 1)**

### **Task 1.1: Data Collection & Preparation**

#### **🔍 Data Sources to Collect:**

**Real Climate Data:**
```python
# 1. Delhi Air Quality Data (2019-2024)
sources = {
    'CPCB_AQI_DATA': 'https://app.cpcbccr.com/ccr_docs/FINAL-REPORT_AQI_APR2024.pdf',
    'SAFAR_DATA': 'https://safar.tropmet.res.in/',
    'IQAir_API': 'https://api.airvisual.com/v2/city?city=Delhi&state=Delhi&country=India'
}

# 2. Weather Data (2019-2024)  
weather_sources = {
    'IMD_DATA': 'https://mausam.imd.gov.in/delhi/',
    'OpenWeather': 'https://api.openweathermap.org/data/2.5/weather?q=Delhi',
    'WorldWeatherOnline': 'Historical weather data'
}

# 3. Traffic & Transportation Data
traffic_sources = {
    'Delhi_Traffic_Police': 'Traffic density data',
    'Google_Mobility': 'COVID mobility reports',
    'Uber_Movement': 'https://movement.uber.com/explore/delhi/'
}

# 4. Energy Consumption Data
energy_sources = {
    'Delhi_Electricity_Board': 'Zone-wise consumption',
    'Ministry_of_Power': 'https://powermin.gov.in/en/content/power-sector-glance-all-india',
    'CEA_DATA': 'Central Electricity Authority reports'
}

# 5. Satellite Data
satellite_sources = {
    'NASA_FIRMS': 'https://firms.modaps.eosdis.nasa.gov/', # Fire data
    'Sentinel_5P': 'https://scihub.copernicus.eu/', # NO2, CO data
    'MODIS': 'Aerosol Optical Depth data'
}
```

#### **📁 Create Training Datasets:**

Create these files with the data collection script:

```python
# File: scripts/collect_training_data.py

import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
import json

def create_synthetic_training_data():
    """Create synthetic training data based on real patterns"""
    
    # Generate 5 years of daily data (1825 days)
    dates = pd.date_range('2019-01-01', '2024-01-01', freq='D')
    
    training_data = []
    
    for date in dates:
        # Seasonal patterns
        month = date.month
        day_of_year = date.timetuple().tm_yday
        
        # Stubble burning season (Oct-Nov)
        stubble_factor = 2.5 if month in [10, 11] else 1.0
        
        # Winter pollution (Dec-Feb)  
        winter_factor = 1.8 if month in [12, 1, 2] else 1.0
        
        # Festival effects (Diwali impact)
        festival_factor = 3.0 if (month == 10 and date.day > 20) or (month == 11 and date.day < 10) else 1.0
        
        for zone_id in range(1, 6):  # 5 Delhi zones
            
            # Base AQI with seasonal variation
            base_aqi = 120 + 50 * np.sin(2 * np.pi * day_of_year / 365) # Seasonal cycle
            aqi = base_aqi * stubble_factor * winter_factor * festival_factor
            aqi += np.random.normal(0, 20)  # Daily variation
            
            # Traffic patterns  
            weekend_factor = 0.7 if date.weekday() >= 5 else 1.0
            traffic_flow = (1000 + zone_id * 200) * weekend_factor + np.random.normal(0, 100)
            
            # Weather simulation
            temp_base = 25 + 10 * np.sin(2 * np.pi * day_of_year / 365)  # Seasonal temp
            if month in [4, 5, 6]:  # Summer heat
                temp_base += 15
            temperature = temp_base + np.random.normal(0, 3)
            
            humidity = 60 + 20 * np.sin(2 * np.pi * (day_of_year + 100) / 365) + np.random.normal(0, 10)
            wind_speed = 5 + 3 * np.random.exponential(1)
            
            # Energy consumption (inversely related to temp in summer for AC)
            if temperature > 30:
                energy_base = 1000 + (temperature - 30) * 50  # AC load
            else:
                energy_base = 1000 + (20 - temperature) * 30  # Heating load
            
            energy_use = energy_base + zone_id * 100 + np.random.normal(0, 50)
            
            # Industrial activity (lower on weekends)
            industrial_activity = (0.7 + zone_id * 0.05) * weekend_factor
            
            # Green cover (varies by zone)
            green_cover = 0.10 + zone_id * 0.02 + np.random.normal(0, 0.01)
            green_cover = max(0.05, min(0.30, green_cover))
            
            # Building age (affects energy efficiency)
            avg_building_age = 25 + zone_id * 5 + np.random.normal(0, 5)
            
            training_data.append({
                'date': date,
                'zone_id': zone_id,
                'aqi': max(0, aqi),
                'temperature': temperature,
                'humidity': max(0, min(100, humidity)),
                'wind_speed': max(0, wind_speed),
                'traffic_flow': max(0, traffic_flow),
                'energy_use': max(0, energy_use),
                'industrial_activity': max(0, min(1, industrial_activity)),
                'green_cover': green_cover,
                'avg_building_age': max(10, avg_building_age),
                'population': 15000 + zone_id * 2000,
                'stubble_fires_punjab': np.random.poisson(3000) if month in [10, 11] else np.random.poisson(100),
                'festival_day': 1 if festival_factor > 1 else 0
            })
    
    df = pd.DataFrame(training_data)
    df.to_csv('data/climate_training_data.csv', index=False)
    print(f"✅ Created training data: {len(df)} records")
    
    return df

if __name__ == "__main__":
    create_synthetic_training_data()
```

### **Task 1.2: Build Advanced ML Models**

#### **🧠 Model 1: AQI Prediction Model (LSTM + Features)**

```python
# File: src/models/aqi_predictor.py

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import warnings
warnings.filterwarnings('ignore')

class AQIPredictorAdvanced:
    """Advanced AQI prediction using ensemble of models"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_names = [
            'temperature', 'humidity', 'wind_speed', 'traffic_flow',
            'energy_use', 'industrial_activity', 'green_cover', 
            'avg_building_age', 'stubble_fires_punjab', 'festival_day',
            'month', 'day_of_week', 'season'
        ]
        
    def prepare_features(self, df):
        """Engineer features for better prediction"""
        
        # Time-based features
        df['month'] = pd.to_datetime(df['date']).dt.month
        df['day_of_week'] = pd.to_datetime(df['date']).dt.dayofweek
        df['season'] = df['month'].apply(lambda x: 
            0 if x in [12, 1, 2] else  # Winter
            1 if x in [3, 4, 5] else   # Spring  
            2 if x in [6, 7, 8] else   # Summer
            3)                         # Autumn
        
        # Interaction features
        df['temp_humidity'] = df['temperature'] * df['humidity'] / 100
        df['traffic_industrial'] = df['traffic_flow'] * df['industrial_activity']
        df['green_building_age'] = df['green_cover'] * df['avg_building_age']
        df['pollution_load'] = df['traffic_flow'] + df['energy_use'] * 0.5
        
        # Lag features (previous day impact)
        df = df.sort_values(['zone_id', 'date'])
        df['aqi_lag1'] = df.groupby('zone_id')['aqi'].shift(1)
        df['temp_lag1'] = df.groupby('zone_id')['temperature'].shift(1)
        
        return df.dropna()
    
    def train_ensemble(self, df):
        """Train ensemble of models for AQI prediction"""
        
        # Prepare data
        df = self.prepare_features(df)
        
        X = df[self.feature_names + ['temp_humidity', 'traffic_industrial', 
                                   'green_building_age', 'pollution_load', 
                                   'aqi_lag1', 'temp_lag1']]
        y = df['aqi']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=df['zone_id']
        )
        
        # Scale features
        self.scalers['standard'] = StandardScaler()
        X_train_scaled = self.scalers['standard'].fit_transform(X_train)
        X_test_scaled = self.scalers['standard'].transform(X_test)
        
        # Model 1: Gradient Boosting (Best for tabular data)
        print("🔧 Training Gradient Boosting Model...")
        gb_params = {
            'n_estimators': [100, 200, 300],
            'learning_rate': [0.05, 0.1, 0.15],
            'max_depth': [5, 7, 9]
        }
        
        gb_grid = GridSearchCV(
            GradientBoostingRegressor(random_state=42),
            gb_params, cv=3, scoring='neg_mean_absolute_error', n_jobs=-1
        )
        gb_grid.fit(X_train, y_train)
        self.models['gradient_boosting'] = gb_grid.best_estimator_
        
        # Model 2: Random Forest (Good for feature importance)
        print("🔧 Training Random Forest Model...")
        rf = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)
        rf.fit(X_train, y_train)
        self.models['random_forest'] = rf
        
        # Model 3: Neural Network (Captures complex patterns)
        print("🔧 Training Neural Network Model...")
        nn = MLPRegressor(
            hidden_layer_sizes=(128, 64, 32),
            activation='relu', solver='adam',
            learning_rate_init=0.001, max_iter=500,
            random_state=42
        )
        nn.fit(X_train_scaled, y_train)
        self.models['neural_network'] = nn
        
        # Evaluate models
        print("\n📊 Model Performance:")
        for name, model in self.models.items():
            if name == 'neural_network':
                pred = model.predict(X_test_scaled)
            else:
                pred = model.predict(X_test)
            
            mae = mean_absolute_error(y_test, pred)
            r2 = r2_score(y_test, pred)
            print(f"{name:20}: MAE = {mae:.2f}, R² = {r2:.3f}")
        
        # Feature importance (from Random Forest)
        feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': self.models['random_forest'].feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\n🔝 Top 10 Most Important Features:")
        print(feature_importance.head(10).to_string(index=False))
        
        return self.models
    
    def predict_ensemble(self, X):
        """Make predictions using ensemble of models"""
        
        X_scaled = self.scalers['standard'].transform(X)
        
        # Get predictions from all models
        pred_gb = self.models['gradient_boosting'].predict(X)
        pred_rf = self.models['random_forest'].predict(X)
        pred_nn = self.models['neural_network'].predict(X_scaled)
        
        # Weighted ensemble (GB gets highest weight as it usually performs best)
        ensemble_pred = 0.5 * pred_gb + 0.3 * pred_rf + 0.2 * pred_nn
        
        return ensemble_pred
    
    def save_models(self):
        """Save trained models"""
        for name, model in self.models.items():
            joblib.dump(model, f'models/aqi_{name}_model.pkl')
        
        for name, scaler in self.scalers.items():
            joblib.dump(scaler, f'models/aqi_{name}_scaler.pkl')
        
        print("✅ Models saved successfully")

# Usage
if __name__ == "__main__":
    # Load training data
    df = pd.read_csv('data/climate_training_data.csv')
    
    # Train models
    predictor = AQIPredictorAdvanced()
    predictor.train_ensemble(df)
    predictor.save_models()
```

#### **🔋 Model 2: Carbon Emission Predictor**

```python
# File: src/models/carbon_predictor.py

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

class CarbonEmissionPredictor:
    """Predict carbon emissions based on city activities"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        
        # Emission factors (kg CO2 equivalent)
        self.emission_factors = {
            'traffic': 0.21,      # kg CO2 per km per vehicle
            'electricity': 0.82,  # kg CO2 per kWh (India grid)
            'industry': 2.1,      # kg CO2 per kWh industrial
            'buildings_gas': 2.3, # kg CO2 per m³ natural gas
            'waste': 0.5          # kg CO2 per kg waste
        }
    
    def calculate_emissions(self, df):
        """Calculate actual carbon emissions for training"""
        
        emissions = []
        
        for _, row in df.iterrows():
            # Traffic emissions (vehicles * km * emission factor)
            traffic_co2 = row['traffic_flow'] * 10 * self.emission_factors['traffic']
            
            # Electricity emissions  
            elec_co2 = row['energy_use'] * self.emission_factors['electricity']
            
            # Industrial emissions
            industrial_co2 = row['energy_use'] * row['industrial_activity'] * self.emission_factors['industry']
            
            # Building heating/cooling (estimated gas usage)
            if row['temperature'] > 30:  # AC usage
                gas_usage = (row['temperature'] - 30) * row['energy_use'] * 0.1
            elif row['temperature'] < 15:  # Heating
                gas_usage = (15 - row['temperature']) * row['energy_use'] * 0.05
            else:
                gas_usage = 0
                
            building_co2 = gas_usage * self.emission_factors['buildings_gas']
            
            # Waste emissions (population-based)
            waste_co2 = row['population'] * 0.8 * self.emission_factors['waste']  # 0.8kg waste per person per day
            
            total_co2 = traffic_co2 + elec_co2 + industrial_co2 + building_co2 + waste_co2
            
            emissions.append({
                'zone_id': row['zone_id'],
                'date': row['date'],
                'total_co2_tons': total_co2 / 1000,  # Convert to tons
                'traffic_co2': traffic_co2 / 1000,
                'electricity_co2': elec_co2 / 1000,
                'industrial_co2': industrial_co2 / 1000,
                'building_co2': building_co2 / 1000,
                'waste_co2': waste_co2 / 1000
            })
        
        return pd.DataFrame(emissions)
    
    def prepare_training_data(self, climate_df):
        """Prepare training data with features and targets"""
        
        # Calculate actual emissions
        emissions_df = self.calculate_emissions(climate_df)
        
        # Merge with climate data
        df = climate_df.merge(emissions_df, on=['zone_id', 'date'])
        
        # Feature engineering
        df['energy_intensity'] = df['energy_use'] / df['population']
        df['traffic_per_capita'] = df['traffic_flow'] / df['population'] * 1000
        df['industrial_energy'] = df['energy_use'] * df['industrial_activity']
        df['green_ratio'] = df['green_cover'] / (df['avg_building_age'] / 50)
        
        return df
    
    def train_model(self, df):
        """Train carbon emission prediction model"""
        
        features = [
            'traffic_flow', 'energy_use', 'industrial_activity', 'population',
            'temperature', 'avg_building_age', 'green_cover',
            'energy_intensity', 'traffic_per_capita', 'industrial_energy', 'green_ratio'
        ]
        
        X = df[features]
        y = df['total_co2_tons']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model = GradientBoostingRegressor(
            n_estimators=200,
            learning_rate=0.1,
            max_depth=6,
            random_state=42
        )
        
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_pred = self.model.predict(X_train_scaled)
        test_pred = self.model.predict(X_test_scaled)
        
        train_mae = mean_absolute_error(y_train, train_pred)
        test_mae = mean_absolute_error(y_test, test_pred)
        test_r2 = r2_score(y_test, test_pred)
        
        print(f"🎯 Carbon Emission Model Performance:")
        print(f"   Training MAE: {train_mae:.2f} tons CO2")
        print(f"   Test MAE: {test_mae:.2f} tons CO2")
        print(f"   Test R²: {test_r2:.3f}")
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': features,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print(f"\n🔝 Most Important Features for Carbon Prediction:")
        print(feature_importance.head(5).to_string(index=False))
        
        return self.model
    
    def predict_intervention_impact(self, baseline_data, intervention_type, zone_id, parameters):
        """Predict carbon reduction from interventions"""
        
        # Create intervention scenario
        intervention_data = baseline_data.copy()
        
        if intervention_type == 'ev_adoption':
            # Reduce traffic emissions by EV adoption rate
            reduction_factor = 1 - parameters.get('ev_percentage', 0.3)
            intervention_data.loc[intervention_data['zone_id'] == zone_id, 'traffic_flow'] *= reduction_factor
            
        elif intervention_type == 'renewable_energy':
            # Reduce electricity emissions
            renewable_percentage = parameters.get('renewable_percentage', 0.5)
            current_energy = intervention_data.loc[intervention_data['zone_id'] == zone_id, 'energy_use'].iloc[0]
            clean_energy = current_energy * renewable_percentage
            intervention_data.loc[intervention_data['zone_id'] == zone_id, 'energy_use'] = current_energy - clean_energy
            
        elif intervention_type == 'green_buildings':
            # Improve building efficiency
            efficiency_improvement = parameters.get('efficiency_improvement', 0.2)
            intervention_data.loc[intervention_data['zone_id'] == zone_id, 'energy_use'] *= (1 - efficiency_improvement)
            intervention_data.loc[intervention_data['zone_id'] == zone_id, 'avg_building_age'] *= 0.7  # Modernization
        
        elif intervention_type == 'urban_forest':
            # Increase green cover
            green_increase = parameters.get('green_increase', 0.1)
            current_green = intervention_data.loc[intervention_data['zone_id'] == zone_id, 'green_cover'].iloc[0]
            intervention_data.loc[intervention_data['zone_id'] == zone_id, 'green_cover'] = min(0.5, current_green + green_increase)
        
        # Predict emissions for both scenarios
        baseline_features = self._extract_features(baseline_data)
        intervention_features = self._extract_features(intervention_data)
        
        baseline_emissions = self.model.predict(self.scaler.transform(baseline_features))
        intervention_emissions = self.model.predict(self.scaler.transform(intervention_features))
        
        reduction = baseline_emissions[0] - intervention_emissions[0]
        reduction_percentage = (reduction / baseline_emissions[0]) * 100
        
        return {
            'baseline_co2_tons': baseline_emissions[0],
            'intervention_co2_tons': intervention_emissions[0], 
            'reduction_tons': reduction,
            'reduction_percentage': reduction_percentage,
            'annual_reduction_tons': reduction * 365,
            'carbon_credits_value_inr': reduction * 365 * 2000  # ₹2000 per ton
        }
    
    def _extract_features(self, df):
        """Extract features for prediction"""
        features = [
            'traffic_flow', 'energy_use', 'industrial_activity', 'population',
            'temperature', 'avg_building_age', 'green_cover'
        ]
        
        # Add engineered features
        df['energy_intensity'] = df['energy_use'] / df['population']
        df['traffic_per_capita'] = df['traffic_flow'] / df['population'] * 1000
        df['industrial_energy'] = df['energy_use'] * df['industrial_activity']
        df['green_ratio'] = df['green_cover'] / (df['avg_building_age'] / 50)
        
        features.extend(['energy_intensity', 'traffic_per_capita', 'industrial_energy', 'green_ratio'])
        
        return df[features]
    
    def save_model(self):
        """Save the trained model"""
        joblib.dump(self.model, 'models/carbon_emission_model.pkl')
        joblib.dump(self.scaler, 'models/carbon_scaler.pkl')
        print("✅ Carbon emission model saved")

# Usage
if __name__ == "__main__":
    # Load climate data
    df = pd.read_csv('data/climate_training_data.csv')
    
    # Train carbon model
    carbon_predictor = CarbonEmissionPredictor()
    training_data = carbon_predictor.prepare_training_data(df)
    carbon_predictor.train_model(training_data)
    carbon_predictor.save_model()
```

#### **🌿 Model 3: Renewable Energy Optimizer**

```python
# File: src/models/renewable_optimizer.py

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from sklearn.ensemble import RandomForestRegressor
import joblib

class RenewableEnergyOptimizer:
    """Optimize renewable energy placement using AI"""
    
    def __init__(self):
        self.solar_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.wind_model = RandomForestRegressor(n_estimators=100, random_state=42)
        
        # Solar/Wind potential factors by zone (based on Delhi geography)
        self.zone_potential = {
            1: {'solar': 0.8, 'wind': 0.3, 'land_availability': 0.2},  # Connaught Place (urban core)
            2: {'solar': 0.75, 'wind': 0.4, 'land_availability': 0.3}, # Karol Bagh
            3: {'solar': 0.9, 'wind': 0.6, 'land_availability': 0.7},  # Dwarka (planned city)
            4: {'solar': 0.85, 'wind': 0.5, 'land_availability': 0.6}, # Rohini
            5: {'solar': 0.7, 'wind': 0.3, 'land_availability': 0.4}   # Saket
        }
    
    def generate_renewable_training_data(self, climate_df):
        """Generate training data for renewable energy potential"""
        
        renewable_data = []
        
        for _, row in climate_df.iterrows():
            zone_id = int(row['zone_id'])
            potential = self.zone_potential[zone_id]
            
            # Solar generation potential (kWh per MW installed)
            # Factors: solar irradiance (temperature proxy), cloud cover (humidity proxy), season
            month = pd.to_datetime(row['date']).month
            
            # Solar irradiance varies with season and weather
            seasonal_solar = 1.0 + 0.3 * np.sin(2 * np.pi * (month - 3) / 12)  # Peak in summer
            weather_solar = max(0.3, 1.0 - row['humidity'] / 200)  # Clouds reduce solar
            temp_efficiency = max(0.7, 1.0 - max(0, row['temperature'] - 25) / 100)  # High temp reduces efficiency
            
            solar_generation = (potential['solar'] * seasonal_solar * weather_solar * 
                              temp_efficiency * 1200 + np.random.normal(0, 100))  # Base: 1200 kWh/MW/day
            
            # Wind generation potential  
            wind_seasonal = 1.0 + 0.2 * np.cos(2 * np.pi * (month - 1) / 12)  # Peak in winter
            wind_speed_factor = min(3.0, row['wind_speed'] / 5.0)  # Wind speed impact
            
            wind_generation = (potential['wind'] * wind_seasonal * wind_speed_factor * 
                             800 + np.random.normal(0, 80))  # Base: 800 kWh/MW/day
            
            # Installation cost factors
            solar_cost = 45000000 * (1 + (1 - potential['land_availability']) * 0.5)  # ₹4.5 crores/MW base
            wind_cost = 60000000 * (1 + (1 - potential['land_availability']) * 0.3)   # ₹6 crores/MW base
            
            renewable_data.append({
                'zone_id': zone_id,
                'date': row['date'],
                'temperature': row['temperature'],
                'humidity': row['humidity'],
                'wind_speed': row['wind_speed'],
                'month': month,
                'solar_potential_kwh_per_mw': max(0, solar_generation),
                'wind_potential_kwh_per_mw': max(0, wind_generation),
                'solar_cost_per_mw': solar_cost,
                'wind_cost_per_mw': wind_cost,
                'land_availability': potential['land_availability'],
                'energy_demand': row['energy_use']
            })
        
        return pd.DataFrame(renewable_data)
    
    def train_renewable_models(self, renewable_df):
        """Train models to predict renewable energy generation"""
        
        features = ['temperature', 'humidity', 'wind_speed', 'month', 'land_availability']
        
        # Solar model
        X_solar = renewable_df[features]
        y_solar = renewable_df['solar_potential_kwh_per_mw']
        
        self.solar_model.fit(X_solar, y_solar)
        solar_score = self.solar_model.score(X_solar, y_solar)
        
        # Wind model
        X_wind = renewable_df[features]
        y_wind = renewable_df['wind_potential_kwh_per_mw']
        
        self.wind_model.fit(X_wind, y_wind)
        wind_score = self.wind_model.score(X_wind, y_wind)
        
        print(f"🌞 Solar Model R² Score: {solar_score:.3f}")
        print(f"💨 Wind Model R² Score: {wind_score:.3f}")
        
        return self.solar_model, self.wind_model
    
    def optimize_renewable_mix(self, zone_data, budget_crores=100):
        """Optimize renewable energy mix for maximum ROI"""
        
        def objective(x):
            """Objective function to maximize renewable generation per rupee invested"""
            solar_mw, wind_mw, battery_mwh = x
            
            if solar_mw < 0 or wind_mw < 0 or battery_mwh < 0:
                return 1e10  # Penalty for negative values
            
            zone_id = zone_data['zone_id']
            potential = self.zone_potential[zone_id]
            
            # Predict generation
            features = np.array([[
                zone_data['temperature'],
                zone_data['humidity'], 
                zone_data['wind_speed'],
                zone_data['month'],
                potential['land_availability']
            ]])
            
            solar_gen = self.solar_model.predict(features)[0] * solar_mw * 365  # Annual kWh
            wind_gen = self.wind_model.predict(features)[0] * wind_mw * 365    # Annual kWh
            
            total_generation = solar_gen + wind_gen
            
            # Calculate costs
            solar_cost = solar_mw * 45  # ₹45 lakhs per MW
            wind_cost = wind_mw * 60    # ₹60 lakhs per MW  
            battery_cost = battery_mwh * 20  # ₹20 lakhs per MWh
            
            total_cost = solar_cost + wind_cost + battery_cost
            
            if total_cost > budget_crores * 10:  # Convert crores to lakhs
                return 1e10  # Budget constraint
            
            # Maximize generation per rupee (minimize negative ROI)
            roi = total_generation / (total_cost * 100000)  # kWh per rupee
            
            # Add battery adequacy constraint (storage should be 20-30% of generation capacity)
            generation_capacity_mw = solar_mw + wind_mw
            if generation_capacity_mw > 0:
                storage_ratio = battery_mwh / generation_capacity_mw
                if storage_ratio < 0.2 or storage_ratio > 0.4:
                    roi *= 0.5  # Penalty for inadequate storage
            
            return -roi  # Minimize negative ROI
        
        # Constraints
        constraints = [
            {'type': 'ineq', 'fun': lambda x: budget_crores * 10 - (x[0] * 45 + x[1] * 60 + x[2] * 20)},  # Budget
            {'type': 'ineq', 'fun': lambda x: x[2] - 0.2 * (x[0] + x[1])},  # Min storage
            {'type': 'ineq', 'fun': lambda x: 0.4 * (x[0] + x[1]) - x[2]}   # Max storage
        ]
        
        # Bounds (MW/MWh limits based on land availability)
        max_solar = zone_data.get('max_solar_mw', 50)
        max_wind = zone_data.get('max_wind_mw', 30) 
        max_battery = zone_data.get('max_battery_mwh', 50)
        
        bounds = [
            (0, max_solar),   # Solar MW
            (0, max_wind),    # Wind MW
            (0, max_battery)  # Battery MWh
        ]
        
        # Initial guess
        x0 = [budget_crores * 0.4 / 45, budget_crores * 0.3 / 60, budget_crores * 0.2 / 20]
        
        # Optimize
        result = minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=constraints)
        
        if result.success:
            solar_mw, wind_mw, battery_mwh = result.x
            
            # Calculate final metrics
            features = np.array([[
                zone_data['temperature'],
                zone_data['humidity'],
                zone_data['wind_speed'], 
                zone_data['month'],
                self.zone_potential[zone_data['zone_id']]['land_availability']
            ]])
            
            annual_solar = self.solar_model.predict(features)[0] * solar_mw * 365
            annual_wind = self.wind_model.predict(features)[0] * wind_mw * 365
            total_annual_generation = annual_solar + annual_wind
            
            investment = solar_mw * 45 + wind_mw * 60 + battery_mwh * 20  # Lakhs
            annual_savings = total_annual_generation * 6 / 100000  # ₹6/kWh savings, convert to lakhs
            payback_years = investment / annual_savings if annual_savings > 0 else 999
            
            co2_reduction = total_annual_generation * 0.82 / 1000  # 0.82 kg CO2/kWh, convert to tons
            
            return {
                'optimal_solar_mw': round(solar_mw, 2),
                'optimal_wind_mw': round(wind_mw, 2),
                'optimal_battery_mwh': round(battery_mwh, 2),
                'total_investment_lakhs': round(investment, 2),
                'total_investment_crores': round(investment / 10, 2),
                'annual_generation_mwh': round(total_annual_generation / 1000, 2),
                'annual_savings_lakhs': round(annual_savings, 2),
                'payback_years': round(payback_years, 1),
                'co2_reduction_tons_annual': round(co2_reduction, 2),
                'carbon_credits_value_lakhs': round(co2_reduction * 2000 / 100000, 2),
                'roi_percentage': round((annual_savings / investment) * 100, 1) if investment > 0 else 0
            }
        else:
            return {'error': 'Optimization failed', 'message': result.message}
    
    def save_models(self):
        """Save renewable energy models"""
        joblib.dump(self.solar_model, 'models/solar_generation_model.pkl')
        joblib.dump(self.wind_model, 'models/wind_generation_model.pkl')
        print("✅ Renewable energy models saved")

# Usage
if __name__ == "__main__":
    # Load climate data
    climate_df = pd.read_csv('data/climate_training_data.csv')
    
    # Initialize optimizer
    optimizer = RenewableEnergyOptimizer()
    
    # Generate training data
    renewable_df = optimizer.generate_renewable_training_data(climate_df)
    renewable_df.to_csv('data/renewable_training_data.csv', index=False)
    
    # Train models
    optimizer.train_renewable_models(renewable_df)
    
    # Test optimization
    sample_zone = {
        'zone_id': 3,
        'temperature': 35,
        'humidity': 60,
        'wind_speed': 8,
        'month': 5,
        'max_solar_mw': 100,
        'max_wind_mw': 50,
        'max_battery_mwh': 75
    }
    
    result = optimizer.optimize_renewable_mix(sample_zone, budget_crores=50)
    print("\n🔋 Optimization Result:")
    for key, value in result.items():
        print(f"   {key}: {value}")
    
    optimizer.save_models()
```

### **Task 1.3: Create Model Training Scripts**

```python
# File: scripts/train_all_models.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.collect_training_data import create_synthetic_training_data
from src.models.aqi_predictor import AQIPredictorAdvanced
from src.models.carbon_predictor import CarbonEmissionPredictor
from src.models.renewable_optimizer import RenewableEnergyOptimizer
import pandas as pd

def main():
    """Train all AI models for hackathon"""
    
    print("🚀 Starting AI Model Training Pipeline")
    print("=" * 50)
    
    # Create directories
    os.makedirs('data', exist_ok=True)
    os.makedirs('models', exist_ok=True)
    
    # Step 1: Generate training data
    print("\n📊 Step 1: Generating Training Data...")
    climate_df = create_synthetic_training_data()
    
    # Step 2: Train AQI Prediction Model
    print("\n🌬️ Step 2: Training AQI Prediction Models...")
    aqi_predictor = AQIPredictorAdvanced()
    aqi_predictor.train_ensemble(climate_df)
    aqi_predictor.save_models()
    
    # Step 3: Train Carbon Emission Model
    print("\n⚡ Step 3: Training Carbon Emission Model...")
    carbon_predictor = CarbonEmissionPredictor()
    carbon_training_data = carbon_predictor.prepare_training_data(climate_df)
    carbon_predictor.train_model(carbon_training_data)
    carbon_predictor.save_model()
    
    # Step 4: Train Renewable Energy Optimizer
    print("\n🌱 Step 4: Training Renewable Energy Models...")
    renewable_optimizer = RenewableEnergyOptimizer()
    renewable_df = renewable_optimizer.generate_renewable_training_data(climate_df)
    renewable_df.to_csv('data/renewable_training_data.csv', index=False)
    renewable_optimizer.train_renewable_models(renewable_df)
    renewable_optimizer.save_models()
    
    print("\n🎉 All Models Trained Successfully!")
    print("=" * 50)
    print("📁 Saved Files:")
    print("   - data/climate_training_data.csv")
    print("   - data/renewable_training_data.csv")
    print("   - models/aqi_*_model.pkl")
    print("   - models/carbon_emission_model.pkl")
    print("   - models/solar_generation_model.pkl")
    print("   - models/wind_generation_model.pkl")
    
    print("\n🎯 Next Steps:")
    print("   1. Test models with: python scripts/test_models.py")
    print("   2. Integrate with API: python backend/climate_api.py")
    print("   3. Start frontend: npm run dev")

if __name__ == "__main__":
    main()
```

---

## 📋 **WEEK 2 TASKS (Priority 2)**

### **Task 2.1: Model Validation & Testing**

```python
# File: scripts/test_models.py
# Create comprehensive model testing script

def test_all_models():
    """Test all trained models with sample data"""
    # Test AQI prediction accuracy
    # Test carbon emission calculations  
    # Test renewable energy optimization
    # Generate performance reports
    pass
```

### **Task 2.2: Advanced Features**
- Add time-series forecasting (LSTM for 24-hour AQI prediction)
- Implement reinforcement learning for policy optimization
- Add computer vision for satellite image analysis

### **Task 2.3: Model Integration**
- Create unified prediction API
- Add model versioning and A/B testing
- Implement real-time model updates

---

## ✅ **DELIVERABLES FOR AI/ML ENGINEER**

### **Week 1:**
- [ ] Synthetic training data (5 years, 5 zones)
- [ ] AQI Prediction Model (95%+ accuracy)
- [ ] Carbon Emission Predictor 
- [ ] Renewable Energy Optimizer
- [ ] Model training pipeline

### **Week 2:**
- [ ] Model validation results
- [ ] Advanced LSTM forecasting
- [ ] Policy optimization RL agent
- [ ] Performance benchmarks

### **Week 3:**
- [ ] Real-time prediction API
- [ ] Model monitoring dashboard
- [ ] A/B testing framework
- [ ] Documentation

### **Week 4:**
- [ ] Demo scenario models
- [ ] Performance optimization
- [ ] Error handling
- [ ] Final testing

---

## 🎯 **SUCCESS METRICS**

- **AQI Prediction**: >95% accuracy on test set
- **Carbon Model**: <5% error on emission calculations  
- **Renewable Optimizer**: >15% ROI predictions
- **Response Time**: <100ms for all predictions
- **Demo Impact**: Quantifiable results for judges

## 🔗 **DEPENDENCIES** 

- Data Engineer: Provides real-time data feeds
- Frontend Developer: Integrates AI predictions into UI
- All Members: Demo scenario coordination

---

**Remember**: Focus on **quantifiable results** that judges can verify. Every model should produce **specific numbers** (lives saved, CO2 reduced, ROI percentage) that create compelling demo moments! 🎯