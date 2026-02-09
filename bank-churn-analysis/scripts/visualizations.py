import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Set aesthetic style
sns.set_theme(style="whitegrid")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.bbox'] = 'tight'

# Load Data
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, '..', 'data', 'Final_Portfolio_Dataset.csv')
    df = pd.read_csv(data_path)
    print("Dataset loaded.")
except FileNotFoundError:
    print("Dataset not found at " + data_path)
    exit()

import os

# Create output folder if it doesn't exist
output_folder = os.path.join(script_dir, '..', 'visualizations')
os.makedirs(output_folder, exist_ok=True)

def save_plot(filename):
    filepath = os.path.join(output_folder, filename)
    plt.savefig(filepath)
    print(f"Saved {filepath}")
    plt.close()

# 1. Correlation Heatmap
print("Generating Correlation Heatmap...")
plt.figure(figsize=(12, 10))
# Select only numerical columns for correlation
numeric_df = df.select_dtypes(include=['float64', 'int64'])
corr = numeric_df.corr()
mask = corr.where(abs(corr) > 0.1, 0) # Highlight significant correlations if needed, or just plot all
sns.heatmap(corr, annot=True, fmt=".2f", cmap='coolwarm', vmin=-1, vmax=1, linewidths=0.5)
plt.title('Correlation Matrix (Numerical Features)', fontsize=16)
save_plot('1_correlation_heatmap.png')

# 2. Key Categorical Drivers (Bar Charts of Churn Rate)
categorical_drivers = ['Geography', 'Gender', 'NumOfProducts', 'IsActiveMember', 'CreditScoreQuality']

for cat in categorical_drivers:
    print(f"Generating Churn Rate by {cat}...")
    plt.figure(figsize=(10, 6))
    
    # Calculate churn rate by category
    churn_rate = df.groupby(cat)['Exited'].mean().reset_index()
    
    # Plot
    sns.barplot(x=cat, y='Exited', data=churn_rate, palette='viridis')
    plt.axhline(df['Exited'].mean(), color='r', linestyle='--', label='Overall Churn Rate')
    plt.ylabel('Churn Rate')
    plt.title(f'Churn Rate by {cat}', fontsize=14)
    plt.legend()
    # Add labels
    for index, row in churn_rate.iterrows():
        plt.text(index, row.Exited, f'{row.Exited:.2%}', color='black', ha="center", va="bottom")
    
    save_plot(f'2_churn_by_{cat}.png')

# 3. Churn by Balance Bracket
print("Generating Churn by Balance Bracket...")
plt.figure(figsize=(10, 6))
order = ['Zero', 'Low', 'Middle', 'High']
sns.barplot(x='BalanceBr', y='Exited', data=df, order=order, palette='magma', errorbar=None)
plt.title('Churn Rate by Balance Bracket', fontsize=14)
plt.ylabel('Churn Rate')
save_plot('3_churn_by_balance_bracket.png')

print("Visualizations generation complete.")
