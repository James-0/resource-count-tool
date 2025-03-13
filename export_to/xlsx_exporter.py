import pandas as pd

def export_to_xlsx(data, filename="jira_report.xlsx"):
    with pd.ExcelWriter(filename) as writer:
        for key, value in data.items():
            df = pd.DataFrame(value.items(), columns=["Metric", "Count"])
            df.to_excel(writer, sheet_name=key, index=False)
    print(f"Exported to {filename}")
