import pandas as pd

try:
    df = pd.read_excel('police_stations.xlsx')
    print("Columns:", list(df.columns))
    print("First row:", df.iloc[0].to_dict())
    print("Row count:", len(df))
except Exception as e:
    print("Error:", e)
