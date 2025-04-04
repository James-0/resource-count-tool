from datetime import datetime
import asyncio
import re

def is_timestamp(timestamp) -> bool:
    datetime_format = "%Y-%m-%dT%H:%M:%S.%f%z"
    try:
        datetime.strptime(timestamp, datetime_format)
        return True
    except ValueError:
        return False

def extract_date(timestamp):
    dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f%z")
    return dt.date().isoformat()

async def get_value(data, key_path):
    await asyncio.sleep(0)
    results = []
    for item in data:
        value = item
        if isinstance(key_path, list):
            for key in key_path:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    value = None
                    break
        # elif is_timestamp(data):
        #     if is_timestamp(data):
        #         print(is_timestamp(data))
        #         extract_date(data)
        #     try:
        #         datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f%z") #2024-03-16T16:24:57.178+0000
        #         value = extract_date(value)
        #     except ValueError:
        #         pass 
        else:
            if '.' in key_path:
                keys = key_path.split(".")
                for key in keys:
                    if isinstance(value, dict) and key in value:
                        value = value[key]
                    else:
                        value = None
                        break
            else:
                value = item.get(key_path) if isinstance(item, dict) else None
        if isinstance(value, str) and is_timestamp(value):
            value = extract_date(value) 
        results.append(value)
    return results

async def extract_values(json_response, keys_list):
    tasks = [get_value(json_response, key) for key in keys_list]
    results = await asyncio.gather(*tasks)
    result_dict = {}
    
    for key, result in zip(keys_list, results):
        updated_key = key.split('.')[1].capitalize() if '.' in key else key
        result_dict[updated_key] = result

    return result_dict

def is_all_none(lst, lst2):
    return all(item is None for item in lst or lst2)

async def streamline_data(resource_list):
    return [obj for obj in resource_list if "issueSecuritySchemeId" in obj]
     