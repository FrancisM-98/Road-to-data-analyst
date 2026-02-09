import pandas as pd
from scipy.stats import chi2_contingency, ttest_ind

# Load data
import os
script_dir = os.path.dirname(os.path.abspath(__file__))

try:
    data_path = os.path.join(script_dir, '..', 'data', 'Final_Portfolio_Dataset.csv')
    df = pd.read_csv(data_path)
    print("Dataset loaded successfully.")
except FileNotFoundError:
    print("Error: Dataset not found. Please ensure 'Final_Portfolio_Dataset.csv' exists.")
    exit()

def report_chi2(feature, target='Exited'):
    """Performs Chi-Square test of independence between a categorical feature and the target."""
    print(f"\n--- Chi-Square Test: {feature} vs {target} ---")
    try:
        contingency_table = pd.crosstab(df[feature], df[target])
        chi2, p, dof, expected = chi2_contingency(contingency_table)
        print(f"P-value: {p:.4e}")
        if p < 0.05:
            print(">> RESULT: Statistically Significant Relationship (Reject H0)")
        else:
            print(">> RESULT: No Significant Relationship (Fail to reject H0)")
    except Exception as e:
        print(f"Could not perform test: {e}")

def report_ttest(feature, target='Exited'):
    """Performs independent T-test to compare means of a numerical feature for churned vs retained customers."""
    print(f"\n--- T-Test: {feature} by {target} ---")
    try:
        group_churned = df[df[target] == 1][feature]
        group_retained = df[df[target] == 0][feature]
        t_stat, p = ttest_ind(group_churned, group_retained, equal_var=False) # Welch's t-test
        print(f"P-value: {p:.4e}")
        print(f"Mean (Churned): {group_churned.mean():.2f}")
        print(f"Mean (Retained): {group_retained.mean():.2f}")
        if p < 0.05:
            print(f">> RESULT: Statistically Significant Difference in Means (Reject H0)")
        else:
            print(">> RESULT: No Significant Difference (Fail to reject H0)")
    except Exception as e:
        print(f"Could not perform test: {e}")

print("\nrunning statistical verification...")

# Categorical Features to Test
categorical_features = [
    'Geography', 
    'Gender', 
    'HasCrCard', 
    'IsActiveMember', 
    'NumOfProducts', 
    'CreditScoreQuality',
    'BalanceBr', 
    'EstimatedSalaryBr'
]

# Numerical Features to Test
numerical_features = [
    'CreditScore', 
    'Age', 
    'Tenure', 
    'Balance', 
    'EstimatedSalary'
]

print("\n>>> PART 1: Categorical Features (Chi-Square Test) <<<")
for cat in categorical_features:
    report_chi2(cat)

print("\n>>> PART 2: Numerical Features (T-Test) <<<")
for num in numerical_features:
    report_ttest(num)

print("\nStatistical Analysis Complete.")
