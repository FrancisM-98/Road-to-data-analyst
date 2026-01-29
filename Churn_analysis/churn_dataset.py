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

# Block 8: Example Manipulation
# Sorting the data by 'Exited' status as previously done.
print("\n--- First 5 rows sorted by Exited ---")
df.sort_values(by="Exited", inplace=True)
print(df.head())