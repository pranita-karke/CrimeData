import pandas as pd
import sys

file_path = 'nepal_gbv_complete_dataset.xlsx'
output_file = 'data_columns.txt'

try:
    with open(output_file, 'w', encoding='utf-8') as f:
        xl = pd.ExcelFile(file_path)
        f.write(f"ALL_SHEETS: {xl.sheet_names}\n")
        
        for sheet in xl.sheet_names:
            df = xl.parse(sheet)
            f.write(f"SHEET_NAME: {sheet}\n")
            f.write(f"{list(df.columns)}\n")
            # Convert sample to string and replace problematic characters if any, though utf-8 handles most
            f.write(f"Sample:\n{df.head(1).to_string()}\n")
    print("Done")
except Exception as e:
    print(f"Error: {e}")
