import pandas as pd
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_dir, '..', 'data', 'Final_Portfolio_Dataset_v2.csv')
df = pd.read_csv(data_path)
print(len(df[df['DangerScore'] == 4]))
