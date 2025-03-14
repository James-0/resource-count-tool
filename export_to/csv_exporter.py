import csv

def export_to_csv(data, filename="jira_report.csv"):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        for key, value in data.items():
            if isinstance(value, dict):
                # Convert the dictionary to rows
                print(f"Exporting {key} as Dictionary...")
                headers = value.keys()
                rows = zip(*value.values())
                writer.writerow([key])  # Write the sheet name as a header
                writer.writerow(headers)  # Write the headers
                writer.writerows(rows)  # Write the rows
            elif isinstance(value, list):
                # Handle lists separately
                print(f"Exporting {key} as List...")
                writer.writerow([key])  # Write the sheet name as a header
                writer.writerow([key])  # Write the header
                for item in value:
                    writer.writerow([item])  # Write each item in the list
            elif isinstance(value, int):
                # Handle the "total" value separately
                print(f"Exporting {key} as Integer...")
                writer.writerow([key])  # Write the sheet name as a header
                writer.writerow(["Metric", "Count"])  # Write the headers
                writer.writerow([key, value])  # Write the value
            else:
                print(f"Skipping {key} with unsupported type {type(value)}")
    print(f"Exported to {filename}")