import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Visualize results as heatmaps and graphs
def plot_heatmap(df, value_col, title):
    # Dynamically determine grid size for up to 10 zones
    n = len(df)
    ncols = int(np.ceil(np.sqrt(n)))
    nrows = int(np.ceil(n / ncols))
    grid = np.full((nrows, ncols), np.nan)
    for i, row in df.iterrows():
        idx = int(i // ncols)
        jdx = int(i % ncols)
        grid[idx, jdx] = row[value_col]
    plt.figure(figsize=(6, 3))
    sns.heatmap(grid, annot=True, cmap='coolwarm', cbar=True)
    plt.title(title)
    plt.show()

def plot_comparison(baseline, intervention, value_col, title):
    plt.figure(figsize=(8, 4))
    plt.plot(baseline['zone_id'], baseline[value_col], label='Baseline', marker='o')
    plt.plot(intervention['zone_id'], intervention[value_col], label='Intervention', marker='o')
    plt.xlabel('Zone ID')
    plt.ylabel(value_col)
    plt.title(title)
    plt.legend()
    plt.show()

if __name__ == '__main__':
    baseline = pd.read_csv('outputs/baseline_results.csv')
    intervention = pd.read_csv('outputs/intervention_1_results.csv')
    plot_heatmap(baseline, 'aqi', 'Baseline AQI Heatmap')
    plot_heatmap(intervention, 'aqi', 'Intervention AQI Heatmap')
    plot_comparison(baseline, intervention, 'energy', 'Energy Use: Baseline vs. Intervention')
    plot_comparison(baseline, intervention, 'heat_island', 'Heat Island: Baseline vs. Intervention')
