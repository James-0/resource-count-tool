import asyncio
import pprint
from data_fetchers.fetch import JiraFetcher
import process_data


from utils import categorize_workflow_scheme, mark_duplicates, process_issue_security_scheme, process_issue_types, process_notification_schemes, process_permission_scheme, process_priority_schemes, process_screen_schemes, process_screens, process_workflow, categorise_projects, process_issue_statuses
async def wait_for_dependencies(resource_name, pending, completed):
    while not pending[resource_name].issubset(completed):
        print(f"⏳ Waiting for dependencies of {resource_name}")
        await asyncio.sleep(0.1)

def get_dependency_name(resources, name):
    return resources[name].get("dependencies", [])

def get_dependency_data(resources, name, dependency_data):
    keys = get_dependency_name(resources, name)
    if len(keys) == 1:
        return dependency_data.get(keys[0], [])
    elif len(keys) > 1:
        return {key: dependency_data[key] for key in keys if key in dependency_data}


async def fetch_and_process_resource(name, fetch_fn, RESOURCES, keys, values, dep_data):
    result, count = await fetch_resource(name, fetch_fn, values)

    if name == "Issue Security Schemes":
        result = await process_data.streamline_data(result)


    if not RESOURCES[name].get("unique", False):
        result = await process_data.extract_values(result, keys)

    if name == "Projects":
        result, count = await categorise_projects(name, result, count)

    if name == "Issue Statuses":
        result = await process_issue_statuses(result)

    if RESOURCES[name].get("should_additional_processes") or dep_data:
        should_temp = RESOURCES[name].get("should_temp", False)
        result, count = await additional_process(name, result, count, dep_data, should_temp, keys)

        if result == "Unknown task":
            return {}, {}
    return result, count

def store_dependencies(resource_name, result, keys, RESOURCES, dependency_data, freed_resources):
    print(f"Storing {resource_name} as dependency data")
    store_key = RESOURCES.get(resource_name, {}).get("store_key")
    store_value = result.get(store_key) if store_key else result.get(keys[0], "")
    dependency_data[resource_name] = store_value
    # ii = dependency_data[resource_name][:3] if isinstance(dependency_data, list) else dependency_data.keys()
    print(f"Stored {resource_name} as dependency data for: {dependency_data[resource_name][:3]}")
    # print(f"Result after storing dependencies: {result.keys() if resource_name == 'Workflows' else None}")
    result.pop(store_key, None)

    return result

async def schedule_dependents(queue, current_resource, pending_dependencies, completed_resources, RESOURCES):
    to_remove = []
    for res, deps in pending_dependencies.items():
        deps.discard(current_resource)
        if not deps and res not in completed_resources:
            to_remove.append(res)

    for res in to_remove:
        if res in pending_dependencies:
            del pending_dependencies[res]

        fetch_function = RESOURCES[res]["fetch_function"]
        keys = RESOURCES[res].get("keys", [])
        values = RESOURCES[res].get("values", "values")
        await queue.put((res, fetch_function, keys, values))

async def additional_process(resource_name, data, count, dep_data, should_temp, keys):
    print(f"Further Processing: {resource_name}")
    match resource_name:
        case "Issue Types":
            updated_data, updated_count = await process_issue_types(resource_name, data, count, dep_data)
            return updated_data, updated_count
        case "Workflow Schemes":
            updated_data, updated_count = await categorize_workflow_scheme(resource_name, data, count)
            return updated_data, updated_count
        case "Custom Fields":
            updated_data, updated_count = await mark_duplicates(resource_name, data, count)
            return updated_data, updated_count
        case "Notification Schemes":
            updated_data, updated_count = await process_notification_schemes(JiraFetcher.get_active_notification_scheme, resource_name, data, count, dep_data, should_temp) 
            return updated_data, updated_count
        case "Permission Schemes":
            updated_data, updated_count = await process_permission_scheme(resource_name, data, count, dep_data)
            return updated_data, updated_count
        case "Issue Security Schemes":
            updated_data, updated_count = await process_issue_security_scheme(JiraFetcher.get_issue_security_scheme, resource_name, data, keys)
            return updated_data, updated_count
        case "Issue Type Schemes":
            updated_data, updated_count = await process_notification_schemes(JiraFetcher.get_project_issue_types_scheme, resource_name, data, count, dep_data, should_temp)
            return updated_data, updated_count
        case "Workflows":
            updated_data, updated_count = await process_workflow(JiraFetcher.process_active_inactive_workflows, resource_name, data, count, dep_data)
            return updated_data, updated_count
        case "Screen Schemes":
            updated_data, updated_count = await process_screen_schemes(JiraFetcher.get_issue_type_screen_scheme, resource_name, data, count, dep_data)
            return updated_data, updated_count
        case "Field Configuration Schemes":
            updated_data, updated_count = await process_notification_schemes(JiraFetcher.get_active_field_config_screen, resource_name, data, count, dep_data, should_temp)
            return updated_data, updated_count
        case "Issue Type Screen Schemes":
            updated_data, updated_count = await process_notification_schemes(JiraFetcher.get_active_issue_type_screen_scheme, resource_name, data, count, dep_data, should_temp)
            return updated_data, updated_count
        case "Screens":
            updated_data, updated_count = await process_screens(JiraFetcher.get_active_screens, resource_name, data, count, dep_data)
            return updated_data, updated_count
        case "Priority Schemes":
            updated_data, updated_count = await process_priority_schemes(JiraFetcher.get_projects_by_priority_scheme, resource_name, data, count)
            return updated_data, updated_count
        
        # case "Custom Fields":
        #     updated_data, updated_count = await mark_duplicates(resource_name, data, count)
        #     return updated_data, updated_count
        case _:
            return "Unknown task", count
    print(f"Updated processed data for: {resource_name}, data keys: {updated_data.keys()}, count: {updated_count}")  
    return updated_data, updated_count

async def fetch_resource(resource_name, fetch_function, values):
    start_at = 0
    max_results = 50
    resource = []
    count = {}

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
    
    total = 0
    return resource, count

async def worker(queue, results, counts_list, pending_dependencies, completed_resources, RESOURCES, dependency_data):
    freed_resources = pending_dependencies.copy()

    while True:
        item = await queue.get()
        if item is None:
            queue.task_done()
            break

        resource_name, fetch_function, keys, values = item

        # 🔄 Wait for dependencies if needed
        if resource_name in pending_dependencies:
            await wait_for_dependencies(resource_name, pending_dependencies, completed_resources)

        # print(f"Pending Dependencies: {pending_dependencies}")
        print(f"\n🚀 Now Processing... {resource_name}")

        # 🔗 Check if it depends on another resource
        is_calling_dependent = resource_name in freed_resources
    # Check if current resource is a dependency in any of the freed_resources values

        is_dependency = (resource_name in deps for deps in dependency_data.values())

        # dep_string = get_dependency_name(RESOURCES, resource_name)
        # dep_data = dependency_data.get(dep_string, []) if is_calling_dependent else []
        dep_data = get_dependency_data(RESOURCES, resource_name, dependency_data) if is_calling_dependent else []
        

        try:
            result, count = await fetch_and_process_resource(
                resource_name, fetch_function, RESOURCES, keys, values, dep_data
            )

            # 📦 Store dependency data if needed
            result = store_dependencies(resource_name, result, keys, RESOURCES, dependency_data, freed_resources) if is_dependency else None

            if is_calling_dependent:
                # print(f"Popping {resource_name} from {freed_resources.keys()}")
                freed_resources.pop(resource_name)

            # 📊 Save final results
            if not RESOURCES[resource_name].get("skip_append_flag", False):
                counts_list.append(count)
                results.append((resource_name, result))
                # print(f"Stored {resource_name} data")

            completed_resources.add(resource_name)

            # 🧩 Unlock dependent resources
            await schedule_dependents(queue, resource_name, pending_dependencies, completed_resources, RESOURCES)

            print(f"✅ Done: {resource_name}")

        finally:
            queue.task_done()
