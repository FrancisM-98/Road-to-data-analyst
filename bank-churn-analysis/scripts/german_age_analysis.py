import pandas as pd
from scipy.stats import ttest_ind

# Load data
import os
script_dir = os.path.dirname(os.path.abspath(__file__))

try:
    data_path = os.path.join(script_dir, '..', 'data', 'Final_Portfolio_Dataset_v2.csv')
    df = pd.read_csv(data_path)
except FileNotFoundError:
    try:
        data_path = os.path.join(script_dir, '..', 'data', 'Churn_Modelling.csv')
        df = pd.read_csv(data_path)
    except:
        print("Data not found.")
        exit()

# Split groups
germans = df[df['Geography'] == 'Germany']['Age']
non_germans = df[df['Geography'] != 'Germany']['Age']

# Calculate Means
mean_german = germans.mean()
mean_non_german = non_germans.mean()

# Perform T-Test (Welch's t-test for unequal variances, just to be safe)
t_stat, p_val = ttest_ind(germans, non_germans, equal_var=False)

print(f"--- Age Analysis: Germany vs Rest of World ---")
print(f"Mean Age (Germany):    {mean_german:.2f}")
print(f"Mean Age (Non-German): {mean_non_german:.2f}")
print(f"Difference:            {mean_german - mean_non_german:.2f} years")
print(f"P-Value:               {p_val:.4e}")

if p_val < 0.05:
    print(">> RESULT: Statistically Significant Difference (Reject H0)")
    if mean_german > mean_non_german:
        print(">> Insight: Germans are indeed significantly OLDER on average.")
    else:
        print(">> Insight: Germans are significantly YOUNGER on average.")
else:
    print(">> RESULT: No Significant Age Difference. The 'German Anomaly' is NOT driven by Age.")
