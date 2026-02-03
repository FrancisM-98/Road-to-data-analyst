import pandas as pd

import os
# Load the v2 dataset
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, '..', 'data', 'Final_Portfolio_Dataset_v2.csv')
    df = pd.read_csv(data_path)
    print("Dataset v2 loaded.")
except FileNotFoundError:
    print(f"Dataset not found at {data_path}")
    exit()

# Filter for Danger Score 4
score_4 = df[df['DangerScore'] == 4]

count = len(score_4)
churn_rate = score_4['Exited'].mean() * 100 if count > 0 else 0

print(f"\n--- Validation Results (Age Sentinel Model) ---")
print(f"Danger Score 4 Customer Count: {count}")
print(f"Danger Score 4 Churn Rate:     {churn_rate:.2f}%")

if count > 0:
    print("\nSample records:")
    print(score_4[['Geography', 'NumOfProducts', 'IsActiveMember', 'Age', 'Exited']].head())
