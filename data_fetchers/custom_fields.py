from utils import fetch_paginated_data

async def get_custom_fields(keys=None):
    endpoint = "/rest/api/3/field"
    fields = await fetch_paginated_data(endpoint)

    data = {
        "total": len(fields),
        "active": len([f for f in fields if not f.get("deprecated")]),
        "inactive": len([f for f in fields if f.get("deprecated")]),
        "duplicates": list(set(f["name"] for f in fields if [x["name"] for x in fields].count(f["name"]) > 1))
    }
    
    return {k: data[k] for k in keys} if keys else data
