import asyncio
from resources import RESOURCES
from export_to.xlsx_exporter import export_to_xlsx

async def main():
    tasks = []
    for resource_name, resource_info in RESOURCES.items():
        fetch_function = resource_info["fetch_function"]
        keys = resource_info.get("keys", [])
        tasks.append(fetch_function(keys))

    results = await asyncio.gather(*tasks)

    # Structure results using the resource names
    data = {name: result for name, result in zip(RESOURCES.keys(), results)}

    export_to_xlsx(data)

if __name__ == "__main__":
    asyncio.run(main())
