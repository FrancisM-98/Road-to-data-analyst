import pandas as pd
df = pd.read_csv('Final_Portfolio_Dataset_v2.csv')
print(len(df[df['DangerScore'] == 4]))
