import pandas as pd
import os

try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, '..', 'data', 'Final_Portfolio_Dataset_v2.csv')
    df = pd.read_csv(data_path)
except FileNotFoundError:
    print("Dataset not found.")
    exit()

p10_threshold = df[df['Balance'] > 0]['Balance'].quantile(0.10)
print(f"Mathematical P10 Threshold: ${p10_threshold:,.2f}")
