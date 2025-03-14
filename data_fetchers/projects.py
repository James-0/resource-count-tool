from utils import fetch_paginated_data
async def get_projects(keys=None):
    endpoint = "/rest/api/3/project/search"
    projects = await fetch_paginated_data(endpoint)

    data = {
        "total": len(projects)
        # "last_updated": max(p["updated"] for p in projects)
    }

    return {k: data[k] for k in keys} if keys else data
