import pandas as pd
from datetime import datetime
import os

os.makedirs("reports", exist_ok=True)

def export_to_xlsx(data):
    # Create a filename using the current date and time
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"reports/jira_report_{current_time}.xlsx"
    
    with pd.ExcelWriter(filename) as writer:
        for sheet_name, sheet_data in data.items():
            if isinstance(sheet_data, dict):
                df = pd.DataFrame(sheet_data)
            elif isinstance(sheet_data, list):
                if all(isinstance(item, dict) for item in sheet_data):
                    df = pd.DataFrame(sheet_data)
                elif all(isinstance(item, list) for item in sheet_data):
                    df = pd.DataFrame(sheet_data)
                else:
                    df = pd.DataFrame({sheet_name: sheet_data})
            else:
                print(f"Skipping {sheet_name} with unsupported data type {type(sheet_data)}")
                continue
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    print(f"Exported to {filename}")
