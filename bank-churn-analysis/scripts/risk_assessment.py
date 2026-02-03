import pandas as pd
import os

# Load the dataset
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, '..', 'data', 'Final_Portfolio_Dataset_v2.csv')
    df = pd.read_csv(data_path)
except FileNotFoundError:
    print(f"Dataset not found at {data_path}")
    exit()

# Filter for Danger Score 4
danger_4_segment = df[df['DangerScore'] == 4]
customer_count = len(danger_4_segment)
total_risk_balance = danger_4_segment['Balance'].sum()

print(f"--- Danger Score 4 Analysis ---")
print(f"Customer Count: {customer_count}")
print(f"Total Balance at Risk: ${total_risk_balance:,.2f}")

print("\n--- Danger Score Distribution ---")
print(df['DangerScore'].value_counts().sort_index())

print("\n--- Investigation: Germany vs Zero Balance ---")
germany_zero_balance = df[(df['Geography'] == 'Germany') & (df['Balance'] == 0)]
print(f"Number of German customers with 0 Balance: {len(germany_zero_balance)}")
if len(germany_zero_balance) == 0:
    print(">> Insight: It is impossible to reach Score 4 because 'Germany' customers never have 0 Balance.")
    print(">> The 'Premium Leak' factor (Balance=0) conflicts with the 'German Anomaly' factor.")
