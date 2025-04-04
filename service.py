import asyncio
import pprint
from data_fetchers.fetch import JiraFetcher
import process_data
from utils import categorize_workflow_scheme, mark_duplicates, process_issue_security_scheme, process_issue_types, process_notification_schemes, process_permission_scheme, process_priority_schemes, process_screen_schemes, process_screens, process_workflow 

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
    

    # if resource_name == "Issue Security Schemes":
    #     print(f"length of result is {len(resource)}")

    start_at = 0
    
    total = 0
    return resource, count

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
            updated_data, updated_count = await process_screens(resource_name, data, count, dep_data)
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

async def worker(queue, results, counts_list, pending_dependencies, completed_resources, RESOURCES, dependency_data):
    freed_resources = pending_dependencies.copy() 
    print(f"Initial Freed Resources: {freed_resources}")

    while True:
        item = await queue.get()
        if item is None: 
            queue.task_done()
            break

        resource_name, fetch_function, keys, values = item

        if resource_name in pending_dependencies:
            while not pending_dependencies[resource_name].issubset(completed_resources):
                print(f"⏳ Waiting for dependencies to be resolved for {resource_name}")
                await asyncio.sleep(0.1)

        print(f"\n🚀 Processing resource: {resource_name}")
        print(f"📌 Current dependency data: {dependency_data.keys()}")


        is_calling_dependent = resource_name in freed_resources
        dep_data = []
        dep_string = None
        
        if is_calling_dependent:
            dep_string = next(iter(RESOURCES[resource_name]["dependencies"]), None)
            dep_data = dependency_data.get(dep_string, [])
            print(f"🔗 Using {dep_string}")

        try:
            result, count = await fetch_resource(resource_name, fetch_function, values)

            if resource_name == "Issue Security Schemes":
                result = await process_data.streamline_data(result)
                
            if not RESOURCES[resource_name].get('unique', False):
                result = await process_data.extract_values(result, keys)


            if is_calling_dependent or RESOURCES[resource_name].get('should_additional_processes'):
                should_temp = RESOURCES[resource_name].get("should_temp", False)
                result, count = await additional_process(resource_name, result, count, dep_data, should_temp, keys)
                if result == "Unknown task":
                    # print(f"�� No additional processing available for {resource_name}")
                    return
                

            store = []
            store_key = RESOURCES.get(resource_name, {}).get("store_key")
            # print(f"🔑 Store key for {resource_name}: {store_key}")
            store_value = result.get(store_key) if store_key else None

            if store_key and store_key in result or result.get(store_key) is not None:
                del result[store_key]
                # print(f"�� Now removed {store_key} for {resource_name}, now result is: {result.keys()}")

            if any(resource_name in value for value in pending_dependencies.values()):
                store = store_value if store_value is not None else result.get(keys[0], [])
                dependency_data[resource_name] = store
                # print(f"📌 Updated dependency data for {resource_name}")

            if is_calling_dependent:
                    freed_resources.pop(resource_name)
        
            append_data = not RESOURCES[resource_name].get("skip_append_flag", False)
            counts_list.append(count) if append_data else None
            results.append((resource_name, result)) if append_data else None
            # print(f"✔️ Appended {resource_name} to counts_list and results" if append_data else f"⛔ Skipped appending data for {resource_name} : {result}")



            completed_resources.add(resource_name)

            to_remove = []
            for dep_resource, deps in pending_dependencies.items():
                deps.discard(resource_name)
                if dep_resource not in completed_resources and not deps:
                    to_remove.append(dep_resource)

            for dep_resource in to_remove:
                if dep_resource in pending_dependencies:
                    del pending_dependencies[dep_resource]
                fetch_function = RESOURCES[dep_resource]["fetch_function"]
                keys = RESOURCES[dep_resource].get("keys", [])
                values = RESOURCES[dep_resource].get("values", "values")
                await queue.put((dep_resource, fetch_function, keys, values))

            print(f"✅ Finished processing: {resource_name}")

        finally:
            queue.task_done()
