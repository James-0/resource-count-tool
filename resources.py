from data_fetchers.custom_fields import get_custom_fields
from data_fetchers.projects import get_projects
# from export_to.xlsx_exporter import export_to_xlsx

# Define each resource with its function, API endpoint, and keys to extract
RESOURCES = {
    "Custom Fields": {
        "fetch_function": get_custom_fields,
        "keys": ["total", "active", "inactive", "duplicates"]
    },
    "Projects": {
        "fetch_function": get_projects,
        "keys": ["total", "last_updated"]
    }
}
