# Block 1: Import necessary libraries
# We use kagglehub to easily download and load datasets from Kaggle.
import kagglehub
from kagglehub import KaggleDatasetAdapter
import pandas as pd

# Block 2: Define and Load the Dataset
# We specify the dataset handle and the file path.
# kagglehub.load_dataset handles the downloading and caching of the file.
print("Loading dataset...")
df = kagglehub.load_dataset(
  KaggleDatasetAdapter.PANDAS,
  "shrutimechlearn/churn-modelling",
  "Churn_Modelling.csv",
)

# Block 3: Initial Data Inspection
# Viewing the first few rows helps us understand the structure of the data.
print("\n--- First 5 records ---")
print(df.head())

# Block 4: Data Quality - General Info
# df.info() shows us the column names, data types, and non-null counts.
# This helps identify missing values and incorrect data types (e.g., numbers stored as strings).
print("\n--- Dataset Information (Types & Nulls) ---")
df.info()

# Block 5: Data Quality - Null Value Check
# Explicitly counting null values in each column to see if any data is missing.
print("\n--- Null Values Check ---")
null_counts = df.isnull().sum()
if null_counts.sum() == 0:
    print("✓ No null values found in the dataset.")
else:
    print("! Null values found:")
    print(null_counts[null_counts > 0])

# Block 6: Data Quality - Duplicates
# Checking if there are any identical rows in the dataset.
duplicates = df.duplicated().sum()
print(f"\n--- Duplicates Check ---")
print(f"Number of duplicate rows: {duplicates}")

# Block 7: Data Quality - Statistical Summary
# df.describe() gives basics statistics (mean, min, max) for numerical columns.
# This helps spot misplaced fields or outliers (e.g. a negative age).
print("\n--- Statistical Summary ---")
print(df.describe())


# Block 8: Feature Engineering - Brackets
# Adding brackets for Balance and EstimatedSalary as per analysis.

def get_balance_bracket(balance):
    if balance == 0:
        return 'Zero'
    elif balance <= 90000:
        return 'Low'
    elif balance <= 130000:
        return 'Middle'
    else:
        return 'High'

def get_salary_bracket(salary):
    if salary <= 50000:
        return 'Low'
    elif salary <= 100000:
        return 'Medium'
    elif salary <= 150000:
        return 'High'
    else:
        return 'Very High'

def get_credit_score_range(score):
    if score < 400: return "350-400"
    elif score < 450: return "400-450"
    elif score < 500: return "450-500"
    elif score < 550: return "500-550"
    elif score < 600: return "550-600"
    elif score < 650: return "600-650"
    elif score < 700: return "650-700"
    elif score < 750: return "700-750"
    elif score < 800: return "750-800"
    else: return "800-850"

def get_credit_score_quality(score):
    if score < 580: return "Bad"
    elif score < 670: return "Fair"
    elif score < 740: return "Good"
    else: return "Excellent"

# Calculate 25th Percentile Thresholds per Country
# (Removed as we are switching to Age Sentinel)

def calculate_danger_score(row):
    score = 0
    # Factor 1: The German Anomaly
    if row['Geography'] == 'Germany':
        score += 1
    # Factor 2: Product Instability
    # 2 products is the loyalty sweet spot. ANY other count = higher churn risk.
    if row['NumOfProducts'] != 2:
        score += 1
    # Factor 3: Inactivity
    if row['IsActiveMember'] == 0:
        score += 1
    # Factor 4: Age Sentinel (Older customers churn more)
    # Based on T-test findings, Age is a strong driver.
    if row['Age'] >= 45:
        score += 1
        
    return score

print("\n--- Adding Brackets & Danger Score ---")
df['BalanceBr'] = df['Balance'].apply(get_balance_bracket)
df['EstimatedSalaryBr'] = df['EstimatedSalary'].apply(get_salary_bracket)
df['CreditScoreRange'] = df['CreditScore'].apply(get_credit_score_range)
df['CreditScoreQuality'] = df['CreditScore'].apply(get_credit_score_quality)
df['DangerScore'] = df.apply(calculate_danger_score, axis=1)

print("Brackets added successfully.")
print("\n--- BalanceBr Distribution ---")
print(df['BalanceBr'].value_counts())
print("\n--- EstimatedSalaryBr Distribution ---")
print(df['EstimatedSalaryBr'].value_counts())
print("\n--- CreditScoreRange Distribution ---")
print(df['CreditScoreRange'].value_counts().sort_index())
print("\n--- CreditScoreQuality Distribution ---")
print(df['CreditScoreQuality'].value_counts())
print("\n--- DangerScore Distribution ---")
print(df['DangerScore'].value_counts().sort_index())

# Block 9: Example Manipulation
# Sorting the data by 'Exited' status as previously done.
print("\n--- First 5 rows sorted by Exited (with new columns) ---")
df.sort_values(by="Exited", inplace=True)
print(df[['CustomerId', 'Balance', 'BalanceBr', 'EstimatedSalary', 'EstimatedSalaryBr', 'Exited']].head())

# Block 10: Save to CSV
import os
# Saving the dataset with new features
script_dir = os.path.dirname(os.path.abspath(__file__))
output_file = os.path.join(script_dir, '..', 'data', "Final_Portfolio_Dataset.csv")
df.to_csv(output_file, index=False)
print(f"\nSaved modified dataset to {output_file}")

# Block 11: Analysis - Exits by Salary Bracket
# Calculating the number and percentage of exits for each salary bracket.
print("\n--- Exits by EstimatedSalaryBr ---")
exits_by_salary = df.groupby('EstimatedSalaryBr')['Exited'].agg(['sum', 'count', 'mean'])
exits_by_salary.columns = ['Exited (Count)', 'Total Consumers', 'Exit Rate']
print(exits_by_salary)

with open("salary_exit_analysis.txt", "w") as f:
    f.write(str(exits_by_salary))
print("Saved exit analysis to salary_exit_analysis.txt")