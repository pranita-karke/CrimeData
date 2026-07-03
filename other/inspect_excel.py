import pandas as pd

try:
    print("Reading Excel...")
    xl = pd.ExcelFile('nepal_gbv_complete_dataset.xlsx')
    print(f"Sheet names: {xl.sheet_names}")
    
    if 'Complete_Data' in xl.sheet_names:
        df = xl.parse('Complete_Data')
        print("\nColumns:", df.columns.tolist())
        print("\nUnique Years found in 'Year' column:")
        print(df['Year'].unique())
        print("\nFirst 5 rows:")
        print(df.head())
    else:
        print("Sheet 'Complete_Data' not found!")
        
except Exception as e:
    print(f"Error: {e}")
