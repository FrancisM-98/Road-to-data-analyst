import pandas as pd

try:
    df = pd.read_csv('Churn_Modelling_With_Danger_Score.csv')
except FileNotFoundError:
    print("Dataset not found.")
    exit()

p10_threshold = df[df['Balance'] > 0]['Balance'].quantile(0.10)
print(f"Mathematical P10 Threshold: ${p10_threshold:,.2f}")
