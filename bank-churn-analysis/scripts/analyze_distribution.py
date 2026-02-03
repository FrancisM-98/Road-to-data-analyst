import kagglehub
from kagglehub import KaggleDatasetAdapter
import pandas as pd

# Load dataset
path = kagglehub.load_dataset(
  KaggleDatasetAdapter.PANDAS,
  "shrutimechlearn/churn-modelling",
  "Churn_Modelling.csv",
)

# It seems kagglehub.load_dataset returns the dataframe directly if using PANDAS adapter? 
# The original script did: df = kagglehub.load_dataset(...)
df = path


with open("analysis_results.txt", "w") as f:
    f.write("--- Balance and EstimatedSalary Stats ---\n")
    f.write(str(df[['Balance', 'EstimatedSalary']].describe()))
    f.write("\n\n--- Balance Percentiles (including zeros) ---\n")
    f.write(str(df['Balance'].quantile([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])))
    
    f.write("\n\n--- Zero Balance Percentage ---\n")
    zero_balance_pct = (df['Balance'] == 0).mean() * 100
    f.write(f"Percentage of users with 0 Balance: {zero_balance_pct:.2f}%\n")

    f.write("\n\n--- EstimatedSalary Percentiles ---\n")
    f.write(str(df['EstimatedSalary'].quantile([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])))
print("Analysis complete. Check analysis_results.txt")
