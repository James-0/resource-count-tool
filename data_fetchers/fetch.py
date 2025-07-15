import random
import aiohttp
import asyncio
from config import JIRA_BASE_URL, HEADERS
from process_data import extract_values

class JiraFetcher:

    _session = None 
    SEMAPHORE = asyncio.Semaphore(5)

    @classmethod
    async def close_session(cls):
        if cls._session and not cls._session.closed:
            await cls._session.close()

    @classmethod
    async def get_session(cls):
        if cls._session is None:
            cls._session = aiohttp.ClientSession(headers=HEADERS)
        return cls._session

    @classmethod
    async def fetch_data(cls, url, params=None):
        session = await cls.get_session()
        url = f"{JIRA_BASE_URL}{url}"

        for attempt in range(5):
            async with cls.SEMAPHORE:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 429:
                        retry_after = int(response.headers.get("Retry-After", random.uniform(2, 5)))
                        print(f"Rate limited. Retrying in {retry_after} seconds...")
                        await asyncio.sleep(retry_after)
                    else:
                        text = await response.text()
                        raise aiohttp.ClientResponseError(
                            request_info=response.request_info,
                            history=response.history,
                            status=response.status,
                            message=text,
                            headers=response.headers
                        )
        return {}


    @staticmethod
    async def get_dict(url):
        return await JiraFetcher.fetch_data(url)
    
    @staticmethod
    async def get_list(url):
        return await JiraFetcher.fetch_data(url)




    @staticmethod
    async def get_projects(next):
        url = f"/rest/api/3/project/search"
        # start_at = 0
        max_results = 50
        params = {
                "startAt": next,
                "maxResults": max_results,
                "status": "live, archived",
                "expand": "insight",
            }
        extract = {'values': 'values'}
        return await JiraFetcher.fetch_data(url, params)
    
    @staticmethod
    async def get_workflows(next):
        url = f"/rest/api/3/workflows/search"
        params = {
                "expand": "values.transitions",
                "startAt" : next,
                "maxResults": 50
            }
        # extract = {'values': 'values'}
        return await JiraFetcher.fetch_data(url, params=params)

    @staticmethod
    async def get_workflow_schemes(next):
        url = f"/rest/api/3/workflowscheme"
        params = {"maxResults": 50, "startAt": next}
        extract = {'values': 'values'}
        # print("this workflow schems are called")
        workflow_schemes=  await JiraFetcher.fetch_data(url, params)
        return workflow_schemes
    
    @staticmethod
    async def get_custom_fields(start_at = None):
        url = f"/rest/api/3/field"
        return await JiraFetcher.get_list(url)
        
    @staticmethod
    async def get_users(next=None):
        url = f"/rest/api/3/users/search"
        # params = {"maxResults": 50}
        return await JiraFetcher.get_list(url)

    @staticmethod
    async def get_issues():
        url = f"/rest/api/3/search"
        params = {"jql": "ORDER BY created DESC", "maxResults": 50}
        extract = {'values': 'values'}
        return await JiraFetcher.fetch_data(url, params=params)

    @staticmethod
    async def get_groups(next):
        url = f"/rest/api/3/group/bulk"
        params = {"maxResults": 50, "startAt" : next}
        extract = {'values': 'values'}
        return await JiraFetcher.fetch_data(url, params=params)
    
    @staticmethod
    async def get_dashboards(params=None):
        url = f"/rest/api/3/dashboard"
        params = {"values": "dashboards"}
        return await JiraFetcher.get_dict(url)

    @staticmethod
    async def get_field_configurations(next):
        url = f"/rest/api/3/fieldconfiguration"
        params = {"maxResults": 50, "startAt": next}
        extract = {'values': 'values'}
        return await JiraFetcher.fetch_data(url, params=params)
    
    @staticmethod
    async def get_field_configuration_schemes(next):
        url = f"/rest/api/3/fieldconfigurationscheme"
        params = {"maxResults": 50, "startAt": next}
        extract = {'values': 'values'}
        return await JiraFetcher.fetch_data(url, params=params)
    
    @staticmethod
    async def categorise_field_configuration_scheme(id):
        url = f"/rest/api/3/fieldconfigurationscheme/project?projectId={id}"
        result = await JiraFetcher.fetch_data(url)
        return result.get('values', [])
    
    @staticmethod
    async def get_issue_link_types(params):
        url = f"/rest/api/3/issueLinkType"
        params = {"values" : "issueLinkTypes"}
        result = await JiraFetcher.get_dict(url)
        return result.get("issueLinkTypes")
    @staticmethod
    async def get_issue_priorities(params=None):
        url = f"/rest/api/3/priority"
        return await JiraFetcher.get_list(url)
    @staticmethod
    async def get_priority_schemes(next):
        url = f"/rest/api/3/priorityscheme"
        params = {"maxResults": 50, "startAt": next}
        return await JiraFetcher.fetch_data(url, params)
    
    @staticmethod
    async def get_projects_by_priority_scheme(id):
        url = f"/rest/api/3/priorityscheme/{id}/projects"
        return await JiraFetcher.fetch_data(url)
    @staticmethod
    async def get_issue_resolutions(params=None):
        url = f"/rest/api/3/resolution"
        return await JiraFetcher.get_list(url)
    
    @staticmethod
    async def get_issue_types(params=None):
        url = f"/rest/api/3/issuetype"
        return await JiraFetcher.get_list(url)
    
    # @staticmethod
    # async def get_issue_types(params=None):
    #     url = f"/rest/api/3/project/search"
    #     # start_at = 0
    #     max_results = 50
    #     params = {
    #             "startAt": next,
    #             "maxResults": max_results,
    #             "expand": "issueTypes",
    #         }
    #     extract = {'values': 'values'}
    #     return await JiraFetcher.fetch_data(url, params)
    
    @staticmethod
    async def get_project_issue_types(projectId):
        url = f"/rest/api/3/issuetype/project?projectId={projectId}"
        try:
            issue_types = await JiraFetcher.get_list(url)
            if not isinstance(issue_types, list):
                raise ValueError(f"Unexpected response format for project {projectId}: {issue_types}")
        except aiohttp.client_exceptions.ClientResponseError as e:
            if e.code == 404:
                print(f"Issue type for project '{projectId}' not found. Skipping...")
                return None
            else:
                raise e

        return {"id": [issue["id"] for issue in issue_types if "id" in issue]}  # ✅ Extract IDs correctly

    @staticmethod
    async def get_issue_type_schemes(next):
        url = f"/rest/api/3/issuetypescheme"
        params = {"maxResults": 50, "startAt": next}
        return await JiraFetcher.fetch_data(url, params)
    
    @staticmethod
    async def get_issue_type_screen_schemes(next):
        url = f"/rest/api/3/issuetypescreenscheme"
        params = {"maxResults": 50, "startAt": next}
        return await JiraFetcher.fetch_data(url, params)
    @staticmethod
    async def get_values(url, str):
        try:
            result = await JiraFetcher.fetch_data(url)
            
            if result.get("values"):
                first_value = result["values"][0]
                
                if str in first_value and "id" in first_value[str]:
                    scheme_id = first_value[str]["id"]
                    return {"id": scheme_id}
                else:
                    return {"error": f"No '{str}' key or 'id' found in response skipping..."}
            
            return {"error": f"No values found in response"}

        except aiohttp.client_exceptions.ClientResponseError as e:
            if e.code == 404:
                print(f"Skipping....")
                return None
            else:
                raise e
    async def get_project_issue_types_scheme(projectId):
        url = f"/rest/api/3/issuetypescheme/project?projectId={projectId}"
        result = await JiraFetcher.get_values(url, "issueTypeScheme")
        return result


    @staticmethod
    async def get_issue_fields(next=None):
        url = f"/rest/api/3/issuetypescheme/project"
        params = {"maxResults": 50, "startAt": next}
        extract = {'values': 'fields'}
        return await JiraFetcher.fetch_data(url, params=params), extract
    @staticmethod
    async def get_screens(next):
        url = f"/rest/api/3/screens"
        params = {"maxResults": 50, "startAt": next}
        extract = {'values': 'values'}
        return await JiraFetcher.fetch_data(url, params=params)
    
    @staticmethod
    async def get_active_screens(screen_scheme_id):
        url = f"/rest/api/3/screenscheme?id={screen_scheme_id}"
        result = await JiraFetcher.get_dict(url)
        return result.get("values", [])
    
    @staticmethod
    async def get_screen_schemes(next):
        url = f"/rest/api/3/screenscheme"
        params = {"maxResults": 50, "startAt": next}
        return await JiraFetcher.fetch_data(url, params)
    @staticmethod
    async def get_permissions(params=None):
        url = f"/rest/api/3/permissions"
        params = {"values": "permissions"}
        result = await JiraFetcher.get_dict(url)
        return result.get("permissions"), params
    @staticmethod
    async def get_project_roles(next=None):
        url = f"/rest/api/3/role"
        return await JiraFetcher.get_list(url)
    
    @staticmethod
    async def get_permission_schemes(next=None):
        url = f"/rest/api/3/permissionscheme"
        result = await JiraFetcher.get_dict(url)
        return result.get("permissionSchemes")
    
    @staticmethod
    async def get_assigned_permission_scheme(projectKeyOrId):
        url = f"/rest/api/3/project/{projectKeyOrId}/permissionscheme"
        try:
            result = await JiraFetcher.get_dict(url)
            return result.get("permissionScheme")
        except aiohttp.client_exceptions.ClientResponseError as e:
            if e.code == 404 or e.code == 403:
                print(f"Permission scheme for project '{projectKeyOrId}' not found. Skipping...")
                return None
            else:
                raise e
    
    @staticmethod
    async def process_active_inactive_workflow_scheme(id):
        url = f"/rest/api/3/workflowscheme/{id}/projectUsages"
        result = await JiraFetcher.get_dict(url)
        return bool(result.get("projects", {}).get("values"))
    
    @staticmethod
    async def process_active_inactive_workflows(id):
        url = f"/rest/api/3/workflowscheme/{id}"
        try:
            result = await JiraFetcher.fetch_data(url)
            return result
        except aiohttp.client_exceptions.ClientResponseError as e:
            if e.code == 404:
                print(f"Worlkflow scheme for project '{id}' not found. Skipping...")
                return None
            else:
                raise e
    
    @staticmethod
    async def get_permission_schemes_by_project(projectKeyOrId):
        try:
            url = f"/rest/api/3/project/{projectKeyOrId}/permissionscheme"
            return await JiraFetcher.get_dict(url)
        except aiohttp.client_exceptions.ClientResponseError as e:
            if e.code == 404 or e.code == 403:
                print(f"Permission scheme for project '{projectKeyOrId}' not found. Skipping...")
                return None
            else:
                raise e        
    

    @staticmethod
    async def get_notification_schemes(next=None):
        url = f"/rest/api/3/notificationscheme"
        params = {"maxResults": 50, "startAt": next}
        return await JiraFetcher.fetch_data(url, params)

    @staticmethod
    async def get_active_notification_scheme(projectKeyOrId):
        url = f"/rest/api/3/project/{projectKeyOrId}/notificationscheme"
        try:
            result = await JiraFetcher.fetch_data(url)
            return result
        except aiohttp.client_exceptions.ClientResponseError as e:
            if e.code == 404 or e.code == 403:
                print(f"Notification scheme for project '{projectKeyOrId}' not found. Skipping...")
                return None
            else:
                raise e
    @staticmethod
    async def get_issue_security_scheme(next):
        url = f"/rest/api/3/issuesecurityschemes"
        result = await JiraFetcher.get_list(url)
        return result.get('issueSecuritySchemes')
    
    @staticmethod
    async def get_project_security_scheme(next):
        url = f"/rest/api/3/issuesecurityschemes/project"
        params = {"maxResults": 50, "startAt": next}
        return await JiraFetcher.fetch_data(url, params)
    
    @staticmethod
    async def get_active_field_config_screen(id):
        url = f"/rest/api/3/fieldconfigurationscheme/project?projectId={id}"
        result = await JiraFetcher.get_values(url, "fieldConfigurationScheme")
        return result
    @staticmethod
    async def get_active_issue_type_screen_scheme(id):
        url = f"/rest/api/3/issuetypescreenscheme/project?projectId={id}"
        result = await JiraFetcher.get_values(url, "issueTypeScreenScheme")
        return result
    @staticmethod
    async def get_issue_type_screen_scheme(next):
        url = f"/rest/api/3/issuetypescreenscheme/mapping"
        params = {"maxResults": 50, "startAt": next}
        result = await JiraFetcher.fetch_data(url, params)
        return result
    
    @staticmethod
    async def get_issue_statuses(next):
        url = f"/rest/api/3/statuses/search?expand=workflowUsages"
        params = {"maxResults": 50, "startAt": next}
        result = await JiraFetcher.fetch_data(url, params)
        return result