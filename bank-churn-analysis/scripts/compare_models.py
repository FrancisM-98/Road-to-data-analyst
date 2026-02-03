import pandas as pd

# Load dataset (using the one with brackets as base)
import os
script_dir = os.path.dirname(os.path.abspath(__file__))

try:
    data_path = os.path.join(script_dir, '..', 'data', 'Churn_Modelling_With_Brackets.csv')
    df = pd.read_csv(data_path)
except FileNotFoundError:
    # Fallback if that doesn't exist (though it should)
    try:
        data_path = os.path.join(script_dir, '..', 'data', 'Churn_Modelling.csv')
        df = pd.read_csv(data_path) 
    except:
        print("Reference datasets not found.")
        exit()

# --- Reconstruct "Relative Low Balance" Logic ---

# 1. Calculate Country Thresholds (Bottom 25%)
balance_thresholds = df.groupby('Geography')['Balance'].quantile(0.25).to_dict()
print("Country Thresholds (P25):", balance_thresholds)

def is_relative_low_balance(row):
    country_threshold = balance_thresholds.get(row['Geography'], 0)
    return row['Balance'] <= country_threshold

# 2. Filter for Danger Score 4 Criteria
# Factor 1: Germany
# Factor 2: NumOfProducts == 1
# Factor 3: IsActiveMember == 0
# Factor 4: Relative Low Balance
criteria_mask = (
    (df['Geography'] == 'Germany') &
    (df['NumOfProducts'] == 1) &
    (df['IsActiveMember'] == 0) &
    (df.apply(is_relative_low_balance, axis=1)) 
)

target_group = df[criteria_mask]

# 3. Calculate Metrics
count = len(target_group)
churn_rate = target_group['Exited'].mean() * 100 if count > 0 else 0

print(f"\n--- Previous Model (Relative Low Balance) Analysis ---")
print(f"Target Group Count: {count}")
print(f"Churn Rate:         {churn_rate:.2f}%")
