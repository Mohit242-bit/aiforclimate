import os
import subprocess

# Run the full workflow: baseline, interventions, AI, visualization
def run_all():
    print('Running baseline simulation...')
    subprocess.run(['python', 'src/simulation.py'])
    print('Running interventions...')
    subprocess.run(['python', 'src/interventions.py'])
    print('Running AI prescriptive engine...')
    subprocess.run(['python', 'src/ai_prescriptive.py'])
    print('Generating visualizations...')
    subprocess.run(['python', 'src/visualization.py'])

if __name__ == '__main__':
    run_all()
