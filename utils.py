import asyncio
from data_fetchers.fetch import JiraFetcher
from itertools import islice

import process_data

async def fetch_resource(resource_name, fetch_function, values):
    
    start_at = 0
    max_results = 50
    resource = []

    while True:  
        response = await fetch_function(start_at) 

        if isinstance(response, list):
            resource.extend(response)
            count = {resource_name : len(response)}
            break   

        elif isinstance(response, dict):  
            resource_list = response.get(values if values else "values", [])
            count = {resource_name : response.get('total')}
            if not resource_list:  
                break  

            resource.extend(resource_list)  
            is_last = response.get("isLast", True)  
            start_at += max_results  

            if is_last:  
                break
        else:  
            break
    
    start_at = 0
    return resource, count

async def categorize_workflow_scheme(resource_name, data, counts):
    if not data:
        return data, counts

    active_workflows, inactive_workflows = set(), set()

    async def process_id(id):
        is_active = await JiraFetcher.process_active_inactive_workflow_scheme(id)
        (active_workflows if is_active else inactive_workflows).add(id)
        return "yes" if is_active else "no"

    data["Active"] = await asyncio.gather(*[process_id(id) for id in data.get("id", [])])

    counts[resource_name] = [
        counts[resource_name],
        data["Active"].count("yes"),
        data["Active"].count("no")
    ]
    return data, counts
async def mark_duplicates(resource_name, data_dict, count):
    if data_dict is None:
        return data_dict, count
    
    seen = set()

    custom_indices = [i for i, is_custom in enumerate(data_dict.get("custom", [])) if is_custom]

    filtered_data = {key: [data_dict[key][i] for i in custom_indices] for key in data_dict if key != "custom"}

    filtered_data["duplicates"] = ["yes" if name in seen else (seen.add(name) or "no") for name in filtered_data["name"]]

    return filtered_data, count

async def process_notification_schemes(func, resource_name, data, counts, dep_data, should_temp):
    if not dep_data:
        return data, counts

    active_permission = set()

    async def process_id(id):
        result = await func(id)
        if result and result.get("id") in data.get("id", []):
            active_permission.add(result["id"])

    await asyncio.gather(*[process_id(id) for id in dep_data])

    data["Active"] = ["yes" if id in active_permission else "no" for id in data.get("id", [])]
    if should_temp:
        data["ids_list"] = active_permission

    counts[resource_name] = [
        counts[resource_name],
        data["Active"].count("yes"),
        data["Active"].count("no")
    ]
    return data, counts

async def process_permission_scheme(resource_name, data, counts, dep_data):
    if dep_data is not None:
        active_permission = set()  
        active = []

        async def process_id(id):
            result = await JiraFetcher.get_permission_schemes_by_project(id)
            if result is None:
                return
            notification_id = result.get("id")
            if notification_id in data.get('id'):
                active_permission.add(notification_id)

        await asyncio.gather(*[process_id(id) for id in dep_data])

        for id in data.get("id", []):
            if id in active_permission:
                active.append("yes")
            else:
                active.append("no")

        data["Active"] = active

        yes_count = active.count("yes")
        no_count = active.count("no")

        counts[resource_name] = [counts[resource_name]] + [yes_count, no_count]

        return data, counts
    else:
        # print(f"Projects resource not found. Skipping processing for {resource_name}")
        return data, counts

async def process_issue_types(resource_name, data, counts, dep_data):
    issueType_ids = data.get('id', [])
    if dep_data is not None:
        active = []
        matching_issue_types = set()
        async def process_id(id):
            result = await JiraFetcher.get_project_issue_types(id)
            if result is None:
                return
            matching_issue_types.update(set(result.get('id', [])).intersection(set(issueType_ids)))

        await asyncio.gather(*[process_id(id) for id in dep_data])
        data["Active"] = ["yes" if id in matching_issue_types else "no" for id in issueType_ids]
        counts[resource_name] = [counts[resource_name]] + [
            data["Active"].count("yes"),
            data["Active"].count("no")
        ]
        # print(f"Updated processed data for: {resource_name}, data keys: {data.keys()}, count: {counts}")

    return data, counts


async def process_issue_security_scheme(func, resource_name, data, keys):
    if not data:
        return data, None
    
    dep_data_set = set(map(int, [item["issueSecuritySchemeId"] for item in data if "issueSecuritySchemeId" in item]))
    result, counts = await fetch_resource(resource_name, func, values=None)
    data = await process_data.extract_values(result, keys)
    result_list = ["Yes" if num in dep_data_set else "No" for num in data.get('id', [])]
    counts[resource_name] = [counts[resource_name], result_list.count("Yes"), result_list.count("No")]
    data["Active"] = result_list
    
    return data, counts

async def process_workflow(func, resource_name, data, counts, dep_data):
    if dep_data is not None:
        workflow_names = data.get('name', [])
        workflow_transitions = data.get('transitions', [])
        active_workflow = set()
        active = []
        screen_present = []
        screen_ids = []

        async def process_id(id):
            result = await func(id)
            if result is None:
                return
            default_workflow = result.get("defaultWorkflow", '')
            issue_type_mappings = result.get("issueTypeMappings", {})

            if default_workflow and default_workflow in workflow_names:
                active_workflow.add(default_workflow)
            active_workflow.update({value for value in issue_type_mappings.values() if value in workflow_names})

        await asyncio.gather(*[process_id(id) for id in dep_data])

        # Flatten transitions once, outside the loop
        flat_transitions = [t for sublist in workflow_transitions for t in sublist]

        # Collect screen IDs (as integers)
        screen_ids = [
            int(t["transitionScreen"]["parameters"]["screenId"])
            for t in flat_transitions
            if "transitionScreen" in t and "parameters" in t["transitionScreen"]
        ]

        for name, transitions in zip(workflow_names, workflow_transitions):
            active.append("yes" if name in active_workflow else "no")
            screen_present.append("yes" if any(t.get("transitionScreen") for t in transitions) else "no")

        yes_count = active.count("yes")
        no_count = active.count("no")

        data.pop("transitions", None)
        data["Active?"] = active
        data["Screen Present?"] = screen_present
        data["Screen IDs in workflow"] = screen_ids
        counts[resource_name] = [counts[resource_name]] + [yes_count, no_count]

        return data, counts

def get_screen_schemes_with_its(data):
    return [screen_scheme["name"] for screen_scheme in data if "issueTypeScreenSchemes" in screen_scheme]

async def process_screen_schemes(func, resource_name, data, counts, dep_data):
    if dep_data is None:
        return data, counts
    resource = []
    resource, _ = await fetch_resource(resource_name, func, values=None)
    print(f"fetched screen scheme, result is in {type(resource)}")

    resource_dict = {r.get("issueTypeScreenSchemeId"): r for r in resource}
    matching_screen_scheme_ids = [
        resource_dict[issue_id].get("screenSchemeId")
        for issue_id in dep_data if issue_id in resource_dict
    ]
    active_set = set(matching_screen_scheme_ids)
    print(f"Active set: {list(islice(active_set, 3))}")
    
    data["Active"] = ["yes" if str(id) in active_set else "no" for id in data.get("id", [])]
    
    counts[resource_name] = [counts[resource_name]] + [
        data["Active"].count("yes"),
        data["Active"].count("no")
    ]
    
    # getting active screen values for use in additional processing of screens
    screen_values = set()
    for id_val, screen in zip(data.get("id", []), data.get("screens", [])):
        if str(id_val) in active_set and isinstance(screen, dict):
            screen_values.update(screen.values())

    data.pop("screens", None)
    # data["active_screens"] = screen_values
    # print(f"Extracted screen values: {list(islice(screen_values, 5))}")
    
    print(f"Updated processed data for: {resource_name}, data keys: {data.keys()}, count: {counts}")
    return data, counts

async def process_screens(func, resource_name, data, counts, dep_dict):
    if dep_dict is None:
        return data, counts
        
    active_screen = set()
    print(f"Processing screens for {resource_name}, dep_dict: {dep_dict.keys()}")
    dep_data = dep_dict.get("Screen Schemes", [])
    dep_screen = dep_dict.get("Workflows", [])

    async def process_id(id):
        result = await func(id)
        defs = result[0].get('screens', []).get("default")
        if result and defs in data.get("id", []):
            active_screen.add(defs)

    await asyncio.gather(*[process_id(id) for id in dep_data])

    print(f"active before updating: {len(active_screen)}")
    print(f"dep_screen: {len(dep_screen)}")

    active_screen.update(int(s) for s in dep_screen)

    print(f"active after updating: {len(active_screen)}")

    data["Active"] = ["yes" if id in active_screen else "no" for id in data.get("id", [])]
    counts[resource_name] = [counts[resource_name]] + [
        data["Active"].count("yes"),
        data["Active"].count("no")
    ]
    print(f"Updated processed data for: {resource_name}, data keys: {data.keys()}, count: {counts}")
    return data, counts

async def process_priority_schemes(func, resource_name, data, counts):
    if not data:
        return data, counts
    async def process_id(id):
        result = await func(id)
        return "yes" if result and result.get("total", 0) > 0 and result.get("values") else "no"

    data["Active"] = await asyncio.gather(*[process_id(id) for id in data.get('id', [])])

    counts[resource_name] = [counts[resource_name]] + [
        data["Active"].count("yes"),
        data["Active"].count("no")
    ]
    # print(f"Updated processed data for: {resource_name}, data keys: {data.keys()}, count: {counts}")
    return data, counts

async def categorise_projects(name, data, counts):
    if not data:
        return data, counts
    archived = data.get("archived", [])
    
    print(f"Processing projects for {name}, archived: {archived[:5]}")

    counts[name] = [counts[name]] + [
        archived.count(" ") or archived.count(""),
        archived.count(True),
    ]

    return data, counts

async def process_issue_statuses(data):
    if not data:
        return data
    
    workflow_usages = data.get("workflowUsages", [])
    
    workflow_counts = [len(group) for group in workflow_usages]
    data["workflowUsages"] = workflow_counts
    return data