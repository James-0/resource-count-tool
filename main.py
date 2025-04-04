import asyncio
from data_fetchers.fetch import JiraFetcher
from resources import RESOURCES
from export_to.xlsx_exporter import export_to_xlsx
from service import worker

async def main():
    results = []
    counts_list = []
    pending_dependencies = {}
    completed_resources = set()
    dependency_data = {}  


    for resource_name, details in RESOURCES.items():
        if "dependencies" in details:
            pending_dependencies[resource_name] = set(details["dependencies"])

    queue = asyncio.Queue()

    for resource_name, details in RESOURCES.items():
        if resource_name not in pending_dependencies:
            fetch_function = details["fetch_function"]
            keys = details.get("keys", [])
            values = details.get("values", "values")
            await queue.put((resource_name, fetch_function, keys, values))

    worker_tasks = []
    for _ in range(3):
        worker_task = asyncio.create_task(worker(queue, results, counts_list, pending_dependencies, 
                                                 completed_resources, RESOURCES, dependency_data))
        worker_tasks.append(worker_task)

    await queue.join()

    for _ in range(3):
        await queue.put(None)

    await asyncio.gather(*worker_tasks)

    # Process results
    resource_counts = {}
    for count_dict in counts_list:
        resource_counts.update(count_dict)

    final_data = {
        "Resource Counts": [
            {
                "Resource": k,
                "Count": v[0] if isinstance(v, list) else v,  # Use v[0] if list, else v directly
                "Active": v[1] if isinstance(v, list) and len(v) > 1 else None,
                "Inactive": v[2] if isinstance(v, list) and len(v) > 2 else None,
            }
            for k, v in resource_counts.items()
        ]
    }
    # resource_name_to_remove = "Projects Issue Security Scheme"
    # results = [(name, res) for name, res in results if name != resource_name_to_remove]


    final_data.update(dict(results))

    print(f"\nFinal Dependency Data: {final_data.keys()}\n")

    export_to_xlsx(final_data)

    if JiraFetcher._session:
        await JiraFetcher._session.close()


if __name__ == "__main__":
    asyncio.run(main())

